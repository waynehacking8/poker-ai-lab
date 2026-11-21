/* Lean heads-up NLHE match engine for RL training.
 *
 * Mirrors holdem/engine.py (season blind schedule, short all-in rules, uncalled
 * chips returned, odd chip to the big blind), the seven baselines of
 * holdem/opponents.py, and the feature vector of rl/features.py.
 * Build: gcc -O2 -shared -fPIC -o libfastenv.so fastenv.c -lm
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define D_OBS 54
#define NACT 6
#define MAXH 48
#define NST 11

typedef struct { signed char seat, kind, phase; int amt; } Ev;
/* kinds: 0 post_sb 1 post_bb 2 fold 3 check 4 call 5 raise */

typedef struct {
    uint64_t rs;
    int ctrl[2], hero, max_hands, start_stack;
    int stacks[2], hand_no, done, winner;
    int dealer, sb, bb, bbpost;
    int hole[2][2], fboard[5];
    int stack[2], bet[2], contrib[2], pot, folded[2];
    int phase, in_round, level, last_raise, pend[2], npend, acted[2], can_raise[2];
    Ev hist[MAXH]; int nh;
    int actor, to_call, min_raise, max_raise, can_rs;
    double stats[2][NST];
    double hs[2][4]; int hs_ok[2][4];
    int bk[2][4], bk_ok[2][4];
    int *inj; int inj_n;          /* injected decks, 52 ints per hand */
    double *urand; int urand_n, urand_i;  /* injected uniform stream */
    double phi;
    int last_payout[2];
} Env;

typedef struct { int n; Env *e; } Pool;

static int STRAIGHT[8192], TOP5[8192];
static double VSR[169], PCT[169];
static int tables_ready = 0;

static const int SCHED_END[5] = {20, 40, 60, 80, 100};
static const int SCHED_BB[5] = {100, 150, 200, 300, 400};

static int RULES_V2 = 1;  /* 1: Chipzen server rules (short big blind, 800/1000 levels) */
void fe_set_rules(int v2) { RULES_V2 = v2; }

static int bb_for(int hand) {
    for (int i = 0; i < 5; i++) if (hand <= SCHED_END[i]) return SCHED_BB[i];
    if (!RULES_V2) return 600;
    return hand <= 120 ? 600 : hand <= 140 ? 800 : 1000;
}

static void init_tables(void) {
    if (tables_ready) return;
    for (int mask = 0; mask < 8192; mask++) {
        STRAIGHT[mask] = -1; TOP5[mask] = 0;
        for (int high = 12; high >= 4; high--) {
            int window = 0x1f << (high - 4);
            if ((mask & window) == window) { STRAIGHT[mask] = high; break; }
        }
        if (STRAIGHT[mask] < 0 && (mask & 0x100F) == 0x100F) STRAIGHT[mask] = 3;
        if (__builtin_popcount(mask) >= 5) {
            int v = 0, k = 0;
            for (int r = 12; r >= 0 && k < 5; r--) if (mask >> r & 1) { v = (v << 4) | r; k++; }
            TOP5[mask] = v;
        }
    }
    tables_ready = 1;
}

/* ---- evaluator: identical value to chipzen_bot/nlhe/evaluator.py ---- */
static int evaluate(const int *cards, int n) {
    int cnt[13] = {0}, sm[4] = {0}, sc[4] = {0};
    for (int i = 0; i < n; i++) {
        int r = cards[i] >> 2, s = cards[i] & 3;
        cnt[r]++; sm[s] |= 1 << r; sc[s]++;
    }
    int fm = 0;
    for (int s = 0; s < 4; s++) if (sc[s] >= 5) { fm = sm[s]; break; }
    if (fm) { int sf = STRAIGHT[fm]; if (sf >= 0) return (8 << 20) | (sf << 16); }
    int quad = -1, trips[3], nt = 0, pairs[3], np = 0, singles[7], ns = 0, rm = 0;
    for (int r = 12; r >= 0; r--) {
        int c = cnt[r];
        if (c) {
            rm |= 1 << r;
            if (c == 1) singles[ns++] = r;
            else if (c == 2) pairs[np++] = r;
            else if (c == 3) trips[nt++] = r;
            else quad = r;
        }
    }
    if (quad >= 0) {
        int rest = -1;
        for (int r = 12; r >= 0; r--) if (cnt[r] && r != quad) { rest = r; break; }
        return (7 << 20) | (quad << 16) | (rest << 12);
    }
    if (nt && (nt > 1 || np)) {
        int pair = nt > 1 ? trips[1] : -1;
        if (np && pairs[0] > pair) pair = pairs[0];
        return (6 << 20) | (trips[0] << 16) | (pair << 12);
    }
    if (fm) return (5 << 20) | TOP5[fm];
    int st = STRAIGHT[rm];
    if (st >= 0) return (4 << 20) | (st << 16);
    int v, k;
    if (nt) {
        v = trips[0]; k = 1;
        for (int i = 0; i < ns && k < 3; i++, k++) v = (v << 4) | singles[i];
        return (3 << 20) | (v << (4 * (5 - k)));
    }
    if (np >= 2) {
        int kick = ns ? singles[0] : -1;
        if (np == 3 && pairs[2] > kick) kick = pairs[2];
        if (kick < 0) kick = 0;
        v = (pairs[0] << 8) | (pairs[1] << 4) | kick;
        return (2 << 20) | (v << 8);
    }
    if (np) {
        v = pairs[0]; k = 1;
        for (int i = 0; i < ns && k < 4; i++, k++) v = (v << 4) | singles[i];
        return (1 << 20) | (v << (4 * (5 - k)));
    }
    v = 0; k = 0;
    for (int i = 0; i < ns && k < 5; i++, k++) v = (v << 4) | singles[i];
    return v << (4 * (5 - k));
}

int fe_evaluate(const int *cards, int n) { init_tables(); return evaluate(cards, n); }

/* ---- rng ---- */
static uint64_t splitmix(uint64_t *s) {
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}
static double urnd(Env *e) {
    if (e->urand && e->urand_i < e->urand_n) return e->urand[e->urand_i++];
    return (splitmix(&e->rs) >> 11) * (1.0 / 9007199254740992.0);
}
static int rint_below(Env *e, int n) { return (int)(urnd(e) * n); }

/* ---- helpers ---- */
static int hand_class(int c1, int c2) {
    int r1 = c1 >> 2, r2 = c2 >> 2;
    if (r1 < r2) { int t = r1; r1 = r2; r2 = t; }
    if (r1 == r2 || (c1 & 3) == (c2 & 3)) return r1 * 13 + r2;
    return r2 * 13 + r1;
}

static void log_ev(Env *e, int seat, int kind, int amt, int phase) {
    if (e->nh < MAXH) { Ev *v = &e->hist[e->nh++]; v->seat = seat; v->kind = kind; v->amt = amt; v->phase = phase; }
}

static int nboard_for(int phase) { return phase == 0 ? 0 : phase + 2; }

/* ---- stats from a finished hand (mirrors rl/features.py:update_stats) ---- */
static void update_stats(Env *e) {
    int bet[2] = {0, 0}, level = 0, cur = 0, vol = 0, raised_pre = 0;
    for (int i = 0; i < e->nh; i++) {
        Ev *v = &e->hist[i];
        if (v->phase != cur) { cur = v->phase; bet[0] = bet[1] = 0; level = 0; }
        if (v->kind <= 1) { bet[(int)v->seat] += v->amt; if (bet[(int)v->seat] > level) level = bet[(int)v->seat]; continue; }
        int s = v->seat, o = 1 - s;
        double *st = e->stats[o];
        int facing = level > bet[s];
        if (cur == 0) {
            if (!vol && s == e->dealer) { st[0] += 1; if (v->kind == 5) st[1] += 1; }
            vol = 1;
            if (raised_pre && facing) {
                st[2] += 1;
                if (v->kind == 2) st[3] += 1;
                if (v->kind == 5) st[4] += 1;
            }
        } else if (facing) {
            st[5] += 1;
            if (v->kind == 2) st[6] += 1;
            if (v->kind == 5) st[7] += 1;
        } else {
            st[8] += 1;
            if (v->kind == 5) st[9] += 1;
        }
        if (v->kind == 4) bet[s] += v->amt;
        if (v->kind == 5) { bet[s] = v->amt; level = v->amt; if (cur == 0) raised_pre = 1; }
    }
    e->stats[0][10] += 1; e->stats[1][10] += 1;
}

/* ---- hand lifecycle ---- */
static void post(Env *e, int seat, int amount, int kind) {
    int paid = amount < e->stack[seat] ? amount : e->stack[seat];
    e->stack[seat] -= paid; e->bet[seat] += paid; e->contrib[seat] += paid; e->pot += paid;
    log_ev(e, seat, kind, paid, 0);
}

static void start_hand(Env *e) {
    e->hand_no++;
    e->bb = bb_for(e->hand_no); e->sb = e->bb / 2;
    e->dealer = (e->hand_no - 1) % 2;
    int deck[52];
    if (e->inj && e->hand_no <= e->inj_n) memcpy(deck, e->inj + (e->hand_no - 1) * 52, sizeof(deck));
    else {
        for (int i = 0; i < 52; i++) deck[i] = i;
        for (int i = 51; i > 0; i--) { int j = rint_below(e, i + 1); int t = deck[i]; deck[i] = deck[j]; deck[j] = t; }
    }
    e->hole[0][0] = deck[0]; e->hole[0][1] = deck[1]; e->hole[1][0] = deck[2]; e->hole[1][1] = deck[3];
    for (int i = 0; i < 5; i++) e->fboard[i] = deck[4 + i];
    for (int s = 0; s < 2; s++) { e->stack[s] = e->stacks[s]; e->bet[s] = 0; e->contrib[s] = 0; e->folded[s] = 0; }
    e->pot = 0; e->nh = 0; memset(e->hs_ok, 0, sizeof(e->hs_ok)); memset(e->bk_ok, 0, sizeof(e->bk_ok));
    post(e, e->dealer, e->sb, 0);
    int d = e->dealer, n = 1 - d;
    int before = e->stack[n];
    post(e, n, e->bb, 1);
    e->bbpost = before - e->stack[n];
    e->phase = 0; e->in_round = 0;
}

static void begin_street(Env *e) {
    if (e->phase > 0) { e->bet[0] = e->bet[1] = 0; }
    int first = e->phase == 0 ? e->dealer : 1 - e->dealer;
    e->level = e->phase == 0 ? (RULES_V2 ? (e->bet[0] > e->bet[1] ? e->bet[0] : e->bet[1]) : e->bb) : 0;
    e->last_raise = e->bb;
    e->npend = 0;
    int order[2] = {first, 1 - first};
    for (int i = 0; i < 2; i++) if (e->stack[order[i]] > 0) e->pend[e->npend++] = order[i];
    e->acted[0] = e->acted[1] = 0; e->can_raise[0] = e->can_raise[1] = 1;
    e->in_round = 1;
}

static int pop_decision(Env *e) {
    while (e->npend > 0) {
        int seat = e->pend[0];
        e->pend[0] = e->pend[1]; e->npend--;
        int other = 1 - seat;
        if (e->folded[other]) { e->npend = 0; return 0; }
        int to_call = e->level - e->bet[seat]; if (to_call < 0) to_call = 0;
        int opp_can = e->stack[other] > 0;
        if (to_call == 0 && !opp_can) continue;
        e->actor = seat; e->to_call = to_call;
        e->max_raise = e->bet[seat] + e->stack[seat];
        e->min_raise = e->level + e->last_raise;
        e->can_rs = opp_can && e->stack[seat] > to_call && e->can_raise[seat];
        return 1;
    }
    return 0;
}

static void pay(Env *e, int seat, int chips) {
    e->stack[seat] -= chips; e->bet[seat] += chips; e->contrib[seat] += chips; e->pot += chips;
}

/* kind: 0 fold 1 check 2 call 3 raise. returns 0 ok, nonzero illegal */
static int apply(Env *e, int kind, int amount) {
    int seat = e->actor, other = 1 - seat;
    if (kind == 0 && e->to_call == 0) return 1;
    if (kind == 1 && e->to_call > 0) return 2;
    if (kind == 2 && e->to_call == 0) return 3;
    if (kind == 3 && !e->can_rs) return 4;
    if (kind == 0) {
        e->folded[seat] = 1; log_ev(e, seat, 2, 0, e->phase); e->npend = 0; e->in_round = 0; return 0;
    }
    e->acted[seat] = 1;
    if (kind == 1) { log_ev(e, seat, 3, 0, e->phase); return 0; }
    if (kind == 2) {
        int paid = e->to_call < e->stack[seat] ? e->to_call : e->stack[seat];
        pay(e, seat, paid); log_ev(e, seat, 4, paid, e->phase); return 0;
    }
    int lo = e->min_raise < e->max_raise ? e->min_raise : e->max_raise;
    if (amount < lo || amount > e->max_raise) return 5;
    pay(e, seat, amount - e->bet[seat]);
    log_ev(e, seat, 5, amount, e->phase);
    int inc = amount - e->level;
    if (inc >= e->last_raise) { e->last_raise = inc; e->can_raise[0] = e->can_raise[1] = 1; }
    else if (e->acted[other]) e->can_raise[other] = 0;
    e->level = amount;
    e->npend = 0;
    if (e->stack[other] > 0) { e->pend[0] = other; e->npend = 1; }
    return 0;
}

static void settle(Env *e) {
    int payouts[2] = {0, 0};
    if (e->folded[0] || e->folded[1]) {
        int w = e->folded[0] ? 1 : 0; payouts[w] = e->pot;
    } else {
        int big = e->contrib[0] > e->contrib[1] ? 0 : 1;
        int excess = abs(e->contrib[0] - e->contrib[1]);
        int contested = e->pot - excess;
        payouts[big] += excess;
        int c7[7], sc[2];
        for (int s = 0; s < 2; s++) {
            c7[0] = e->hole[s][0]; c7[1] = e->hole[s][1];
            for (int i = 0; i < 5; i++) c7[2 + i] = e->fboard[i];
            sc[s] = evaluate(c7, 7);
        }
        if (sc[0] > sc[1]) payouts[0] += contested;
        else if (sc[1] > sc[0]) payouts[1] += contested;
        else {
            int half = contested / 2;
            payouts[0] += half; payouts[1] += half;
            if (contested % 2) payouts[1 - e->dealer] += 1;
        }
    }
    for (int s = 0; s < 2; s++) { e->stack[s] += payouts[s]; e->stacks[s] = e->stack[s]; e->last_payout[s] = payouts[s]; }
    update_stats(e);
    if (e->stacks[0] <= 0 || e->stacks[1] <= 0 || e->hand_no >= e->max_hands) {
        e->done = 1;
        e->winner = e->stacks[0] == e->stacks[1] ? -1 : (e->stacks[0] > e->stacks[1] ? 0 : 1);
        e->phi = e->winner < 0 ? 0.5 : (e->winner == e->hero ? 1.0 : 0.0);
    } else {
        e->phi = (double)e->stacks[e->hero] / (2.0 * e->start_stack);
        start_hand(e);
    }
}

/* ---- baselines (mirror holdem/opponents.py) ---- */
static int cat_of(const int *hole, const int *board, int nb) {
    int c[7]; c[0] = hole[0]; c[1] = hole[1];
    for (int i = 0; i < nb; i++) c[2 + i] = board[i];
    return evaluate(c, 2 + nb) >> 20;
}

/* flush draw flag and straight outs, mirrors ranges.draw_bonus */
static void draw_info(const int *hole, const int *board, int nb, int *flush_draw, int *outs) {
    int suits[4] = {0}; *flush_draw = 0; *outs = 0;
    for (int i = 0; i < nb; i++) suits[board[i] & 3]++;
    for (int i = 0; i < 2; i++) {
        int s = hole[i] & 3, hs = 0;
        for (int j = 0; j < 2; j++) if ((hole[j] & 3) == s) hs++;
        if (suits[s] >= 2 && suits[s] + hs >= 4) { *flush_draw = 1; break; }
    }
    int bmask = 0, hmask;
    for (int i = 0; i < nb; i++) bmask |= 1 << (board[i] >> 2);
    hmask = bmask;
    for (int i = 0; i < 2; i++) hmask |= 1 << (hole[i] >> 2);
    if (STRAIGHT[hmask] < 0) {
        for (int r = 0; r < 13; r++) {
            if (hmask >> r & 1) continue;
            if (STRAIGHT[hmask | (1 << r)] >= 0 && STRAIGHT[bmask | (1 << r)] < 0) (*outs)++;
        }
    }
}

static void strength(Env *e, int seat, int *level, int *draw) {
    int nb = nboard_for(e->phase);
    const int *hole = e->hole[seat];
    int cat = cat_of(hole, e->fboard, nb);
    int top = 0;
    for (int i = 0; i < nb; i++) if ((e->fboard[i] >> 2) > top) top = e->fboard[i] >> 2;
    int h0 = hole[0] >> 2, h1 = hole[1] >> 2;
    int pair_hole = h0 == h1, lv;
    if (cat >= 3) lv = 4;
    else if (cat == 2) lv = 3;
    else if (cat == 1) {
        int mx = h0 > h1 ? h0 : h1;
        if (pair_hole && h0 > top) lv = 3;
        else if (mx == top) lv = 2;
        else lv = 1;
    } else lv = 0;
    *level = lv;
    int fd, outs; draw_info(hole, e->fboard, nb, &fd, &outs);
    *draw = nb < 5 && (fd || outs >= 2);
}

typedef struct { int kind, amt; } Act;
static Act A_fold(void) { Act a = {0, 0}; return a; }
static Act A_check(void) { Act a = {1, 0}; return a; }
static Act A_call(void) { Act a = {2, 0}; return a; }
static Act A_callchk(Env *e) { return e->to_call > 0 ? A_call() : A_check(); }
static Act A_chkfold(Env *e) { return e->to_call == 0 ? A_check() : A_fold(); }
static Act A_raise_to(Env *e, double target) {
    if (!e->can_rs) return A_callchk(e);
    int lo = e->min_raise < e->max_raise ? e->min_raise : e->max_raise;
    double t = target > e->max_raise ? e->max_raise : target;
    if (t < lo) t = lo;
    Act a = {3, (int)t}; return a;
}
static Act A_bounded(Env *e, int target) {
    int t = target < e->min_raise ? e->min_raise : target;
    if (t > e->max_raise) t = e->max_raise;
    Act a = {3, t}; return a;
}

static Act baseline_act(Env *e, int id) {
    int seat = e->actor, tc = e->to_call, pot = e->pot, mybet = e->bet[seat];
    int pre = e->phase == 0;
    int cls = hand_class(e->hole[seat][0], e->hole[seat][1]);
    double p = PCT[cls];
    int level = 0, draw = 0;
    if (!pre) strength(e, seat, &level, &draw);
    switch (id) {
    case 0: return A_callchk(e);
    case 1: { /* maniac */
        double r = urnd(e);
        if (e->can_rs && r < 0.75) {
            if (r < 0.25) { Act a = {3, e->max_raise}; return a; }
            double size = mybet + tc + 0.8 * (pot + tc);
            return A_raise_to(e, size > e->min_raise ? size : e->min_raise);
        }
        return A_callchk(e);
    }
    case 2: { /* nit */
        if (pre) {
            if (p >= 0.97 && e->can_rs) return A_raise_to(e, 3.0 * e->min_raise);
            if (p >= 0.86 || tc == 0) return A_callchk(e);
            if (tc <= pot / 3 && p >= 0.75) return A_callchk(e);
            return A_chkfold(e);
        }
        if (level >= 3) {
            if (tc == 0 && e->can_rs) return A_raise_to(e, mybet + 0.5 * pot);
            return A_callchk(e);
        }
        if (level == 2 && tc <= pot / 2) return A_callchk(e);
        return A_chkfold(e);
    }
    case 3: { /* random legal */
        int kinds[3], nk = 0;
        if (tc > 0) { kinds[nk++] = 0; kinds[nk++] = 2; } else kinds[nk++] = 1;
        if (e->can_rs) kinds[nk++] = 3;
        int k = kinds[rint_below(e, nk)];
        if (k == 3) {
            int lo = e->min_raise < e->max_raise ? e->min_raise : e->max_raise;
            Act a = {3, lo + rint_below(e, e->max_raise - lo + 1)}; return a;
        }
        Act a = {k, 0}; return a;
    }
    case 4: { /* reference */
        int stack = e->stack[seat];
        if (pre) {
            int a0 = e->hole[seat][0] >> 2, a1 = e->hole[seat][1] >> 2;
            int hi = a0 > a1 ? a0 : a1, lo = a0 > a1 ? a1 : a0;
            int suited = (e->hole[seat][0] & 3) == (e->hole[seat][1] & 3);
            int bucket; /* 0 weak 1 medium 2 strong 3 premium; ranks T=8 J=9 Q=10 K=11 A=12 */
            if (hi == lo) bucket = hi >= 9 ? 3 : (hi == 7 || hi == 8) ? 2 : 1;
            else if (hi == 12 && lo == 11) bucket = 3;
            else if (hi == 12 && lo >= 8 && lo <= 10) bucket = suited ? 2 : 1;
            else if (hi == 11 && (lo == 10 || lo == 9)) bucket = suited ? 2 : 1;
            else if ((hi == 10 || hi == 9) && (lo == 8 || lo == 7)) bucket = suited ? 2 : 1;
            else if (hi == 12) bucket = 1;
            else bucket = 0;
            if (bucket == 3) {
                if (e->can_rs) return A_bounded(e, e->min_raise * 3);
                return tc > 0 ? A_call() : A_chkfold(e);
            }
            if (bucket == 2) {
                if (tc == 0 && e->can_rs) return A_bounded(e, e->min_raise * 2);
                if (tc > 0 && tc <= stack / 10) return A_call();
                return A_chkfold(e);
            }
            if (bucket == 1) {
                if (tc == 0) return A_check();
                if (tc <= stack / 30) return A_call();
                return A_fold();
            }
            return A_chkfold(e);
        }
        int nb = nboard_for(e->phase), cnt[13] = {0};
        cnt[e->hole[seat][0] >> 2]++; cnt[e->hole[seat][1] >> 2]++;
        for (int i = 0; i < nb; i++) cnt[e->fboard[i] >> 2]++;
        int c1 = 0, c2 = 0;
        for (int r = 0; r < 13; r++) { int c = cnt[r]; if (c > c1) { c2 = c1; c1 = c; } else if (c > c2) c2 = c; }
        int klass = c1 >= 3 ? 3 : (c1 == 2 && c2 == 2) ? 2 : c1 == 2 ? 1 : 0;
        int opp_raises = 0;
        for (int i = 0; i < e->nh; i++) if (e->hist[i].seat != seat && e->hist[i].kind == 5) opp_raises++;
        if (klass >= 2) {
            if (e->can_rs && opp_raises == 0) return A_bounded(e, (int)(pot * 0.66));
            return tc > 0 ? A_call() : A_chkfold(e);
        }
        if (klass == 1) {
            if (tc == 0) return A_check();
            if (tc <= pot / 3) return A_call();
            return A_fold();
        }
        return A_chkfold(e);
    }
    case 5: { /* lag */
        int bb = e->bbpost > 0 ? e->bbpost : 100;
        int facing_raise = 0;
        for (int i = 0; i < e->nh; i++) if (e->hist[i].kind == 5 && e->hist[i].phase == 0) facing_raise = 1;
        if (pre) {
            if (!facing_raise) {
                if (tc > 0) return p >= 0.25 ? A_raise_to(e, 2.5 * bb) : A_chkfold(e);
                return p >= 0.7 ? A_raise_to(e, 3.5 * bb) : A_check();
            }
            if (p >= 0.92) return A_raise_to(e, 3.0 * (tc + mybet));
            if (p >= 0.45 && tc <= 0.15 * e->stack[seat]) return A_callchk(e);
            return A_chkfold(e);
        }
        int rest = pot - tc; if (rest < 1) rest = 1;
        int big = tc > 0.75 * rest;
        if (tc == 0) {
            if (e->can_rs && (level >= 2 || draw || urnd(e) < 0.65)) return A_raise_to(e, 0.5 * pot);
            return A_check();
        }
        if (level >= 3 || (level == 2 && !big))
            return level >= 4 ? A_raise_to(e, mybet + tc + 0.7 * pot) : A_callchk(e);
        if ((level >= 1 || draw) && !big) return A_callchk(e);
        return A_chkfold(e);
    }
    default: { /* 6 station raiser */
        if (pre) {
            if (p >= 0.9 && e->can_rs) return A_raise_to(e, 3.0 * e->min_raise);
            if (p >= 0.3 || tc == 0) return A_callchk(e);
            return A_chkfold(e);
        }
        if (level >= 3 && e->can_rs) return A_raise_to(e, mybet + tc + 0.75 * pot);
        if (level >= 1 || draw || tc == 0) return A_callchk(e);
        return A_chkfold(e);
    }
    }
}

/* ---- replay clones (mirror league/clone.py; tables come from Python) ---- */
#define NCL_MAX 80
#define NBK 8
#define SZ_CAP 300
static double CL_THETA[NCL_MAX][4][2][10][4][NBK][5];
static double CL_SZ[NCL_MAX][2][10][SZ_CAP];
static int CL_SZN[NCL_MAX][2][10];
static int cl_ready = 0;

void fe_set_clones(int n, const double *theta, const double *sz, const int *szn) {
    if (n > NCL_MAX) n = NCL_MAX;
    memcpy(CL_THETA, theta, sizeof(double) * (size_t)n * 4 * 2 * 10 * 4 * NBK * 5);
    memcpy(CL_SZ, sz, sizeof(double) * (size_t)n * 2 * 10 * SZ_CAP);
    memcpy(CL_SZN, szn, sizeof(int) * (size_t)n * 2 * 10);
    cl_ready = n;
}

static int bucket_of(double p) {
    static const double EDG[7] = {0.25, 0.45, 0.60, 0.72, 0.82, 0.90, 0.96};
    int b = 0;
    for (int i = 0; i < 7; i++) if (p >= EDG[i]) b++;
    return b;
}

static int clone_bucket(Env *e, int seat) {
    int ph = e->phase;
    if (ph == 0) return bucket_of(PCT[hand_class(e->hole[seat][0], e->hole[seat][1])]);
    int nb = nboard_for(ph);
    int used[52] = {0};
    int me[7], op[7];
    me[0] = e->hole[seat][0]; me[1] = e->hole[seat][1];
    for (int i = 0; i < nb; i++) { me[2 + i] = op[2 + i] = e->fboard[i]; used[e->fboard[i]] = 1; }
    int ms = evaluate(me, 2 + nb);
    long lo = 0, tie = 0, total = 0;
    for (int a = 0; a < 52; a++) {
        if (used[a]) continue;
        for (int b = a + 1; b < 52; b++) {
            if (used[b]) continue;
            op[0] = a; op[1] = b;
            int s = evaluate(op, 2 + nb);
            if (s < ms) lo++; else if (s == ms) tie++;
            total++;
        }
    }
    double p = (lo + 0.5 * tie) / total;
    if (nb < 5 && p < 0.85) {
        int fd, outs; draw_info(e->hole[seat], e->fboard, nb, &fd, &outs);
        double bonus = 0.0;
        if (fd) bonus += 0.14;
        if (outs >= 2) bonus += 0.11; else if (outs == 1) bonus += 0.05;
        p = p + bonus; if (p > 0.95) p = 0.95;
    }
    return bucket_of(p);
}

static Act clone_act(Env *e, int k) {
    int seat = e->actor, other = 1 - seat, tc = e->to_call, pot = e->pot;
    int street = e->phase, is_button = seat == e->dealer;
    int n_raises = 0;
    for (int i = 0; i < e->nh; i++) if (e->hist[i].phase == street && e->hist[i].kind == 5) n_raises++;
    int bb = e->bbpost > 0 ? e->bbpost : 100;
    double eff = (e->stack[seat] < e->stack[other] ? e->stack[seat] : e->stack[other]) / (double)bb;
    int stk = (eff > 10) + (eff > 25) + (eff > 50);
    int fcl;
    if (street == 0) fcl = n_raises == 0 ? (is_button ? 0 : 1) : (n_raises == 1 ? 2 : 3);
    else if (n_raises == 0) fcl = 4;
    else if (n_raises >= 2) fcl = 9;
    else {
        int d = pot - tc; if (d < 1) d = 1;
        double ratio = (double)tc / d;
        fcl = 5 + (ratio >= 0.4) + (ratio >= 0.8) + (ratio >= 1.6);
    }
    int bk;
    if (e->bk_ok[seat][street]) bk = e->bk[seat][street];
    else { bk = clone_bucket(e, seat); e->bk[seat][street] = bk; e->bk_ok[seat][street] = 1; }
    double p[5];
    memcpy(p, CL_THETA[k][street][is_button][fcl][stk][bk], sizeof(p));
    if (tc == 0) p[0] = 0;
    if (tc <= 0) p[2] = 0;
    if (tc > 0) p[1] = 0;
    if (!e->can_rs) { p[3] = p[4] = 0; }
    else if (e->min_raise > e->max_raise) { p[4] += p[3]; p[3] = 0; }
    double tot = p[0] + p[1] + p[2] + p[3] + p[4];
    if (tot <= 0) return tc > 0 ? A_call() : A_check();
    double x = urnd(e) * 1.0, cum = 0; int code = 4;
    for (int i = 0; i < 5; i++) { cum += p[i] / tot; if (cum > x) { code = i; break; } }
    if (code == 0) return A_fold();
    if (code == 1) return A_check();
    if (code == 2) return A_call();
    if (code == 4) { Act a = {3, e->max_raise}; return a; }
    int sk = street == 0 ? 0 : 1, n = CL_SZN[k][sk][fcl];
    double frac = 0.75;
    if (n >= 8) {
        double v = CL_SZ[k][sk][fcl][(int)(urnd(e) * n)];
        frac = v * (0.93 + (1.07 - 0.93) * urnd(e));
        if (frac < 0.05) frac = 0.05;
    }
    double target = e->bet[seat] + tc + frac * (pot + tc);
    int lo = e->min_raise < e->max_raise ? e->min_raise : e->max_raise;
    int t = (int)rint(target);
    if (t > e->max_raise) t = e->max_raise;
    if (t < lo) t = lo;
    if (t >= 0.8 * e->max_raise) t = e->max_raise;
    Act a = {3, t}; return a;
}

/* ---- main loop: runs until an external seat must act or the match ends ---- */
static void run(Env *e) {
    for (;;) {
        if (e->done) return;
        if (!e->in_round) {
            if (e->folded[0] || e->folded[1] || e->phase > 3) { settle(e); continue; }
            begin_street(e); continue;
        }
        if (!pop_decision(e)) {
            e->in_round = 0;
            if (e->folded[0] || e->folded[1]) { settle(e); continue; }
            e->phase++;
            continue;
        }
        int c = e->ctrl[e->actor];
        if (c >= 100 && c < 200) return;
        Act a = c >= 200 ? clone_act(e, c - 200) : baseline_act(e, c);
        apply(e, a.kind, a.amt);
    }
}

/* ---- features ---- */
static double hs_now(Env *e, int seat) {
    int ph = e->phase;
    if (e->hs_ok[seat][ph]) return e->hs[seat][ph];
    int nb = nboard_for(ph), used[52] = {0};
    int me[7], op[7];
    me[0] = e->hole[seat][0]; me[1] = e->hole[seat][1];
    used[me[0]] = used[me[1]] = 1;
    for (int i = 0; i < nb; i++) { me[2 + i] = op[2 + i] = e->fboard[i]; used[e->fboard[i]] = 1; }
    int ms = evaluate(me, 2 + nb);
    int rem[52], nr = 0;
    for (int c = 0; c < 52; c++) if (!used[c]) rem[nr++] = c;
    double w = 0; long n = 0;
    for (int i = 0; i < nr; i++) for (int j = i + 1; j < nr; j++) {
        op[0] = rem[i]; op[1] = rem[j];
        int os = evaluate(op, 2 + nb);
        w += ms > os ? 1.0 : (ms == os ? 0.5 : 0.0); n++;
    }
    double v = w / n;
    e->hs[seat][ph] = v; e->hs_ok[seat][ph] = 1;
    return v;
}

/* amounts for the 6 discrete actions; mask[i]=1 if legal */
static void action_table(Env *e, int *mask, int *amt) {
    int seat = e->actor, tc = e->to_call;
    for (int i = 0; i < NACT; i++) { mask[i] = 0; amt[i] = 0; }
    mask[0] = tc > 0; mask[1] = 1;
    if (!e->can_rs) return;
    static const double FR[3] = {0.5, 1.0, 2.0};
    int lo = e->min_raise < e->max_raise ? e->min_raise : e->max_raise;
    int prev = -1;
    for (int k = 0; k < 3; k++) {
        double t = e->bet[seat] + tc + FR[k] * (e->pot + tc);
        if (t > e->max_raise) t = e->max_raise;
        if (t < lo) t = lo;
        int a = (int)t;
        amt[2 + k] = a;
        if (a < e->max_raise && a != prev) { mask[2 + k] = 1; prev = a; }
    }
    mask[5] = 1; amt[5] = e->max_raise;
}

static void features(Env *e, int seat, float *f) {
    int other = 1 - seat;
    memset(f, 0, sizeof(float) * D_OBS);
    int nb = nboard_for(e->phase);
    const int *hole = e->hole[seat];
    int cls = hand_class(hole[0], hole[1]);
    int r1 = hole[0] >> 2, r2 = hole[1] >> 2;
    if (r1 < r2) { int t = r1; r1 = r2; r2 = t; }
    f[0] = (float)((VSR[cls] - 0.5) * 2); f[1] = (float)PCT[cls];
    f[2] = r1 == r2; f[3] = (hole[0] & 3) == (hole[1] & 3);
    f[4] = r1 / 12.0f; f[5] = r2 / 12.0f;
    f[6 + e->phase] = 1;
    if (nb == 0) f[10] = (float)VSR[cls];
    else {
        f[10] = (float)hs_now(e, seat);
        int cat = cat_of(hole, e->fboard, nb);
        f[11 + (cat > 7 ? 7 : cat)] = 1;
        if (nb < 5) {
            int fd, outs; draw_info(hole, e->fboard, nb, &fd, &outs);
            f[19] = fd; f[20] = outs >= 2; f[21] = outs == 1;
        }
        int top = 0, over = 0, bc[13] = {0}, sc[4] = {0}, paired = 0, msc = 0;
        for (int i = 0; i < nb; i++) {
            int r = e->fboard[i] >> 2; if (r > top) top = r;
            bc[r]++; sc[e->fboard[i] & 3]++;
        }
        for (int r = 0; r < 13; r++) if (bc[r] >= 2) paired = 1;
        for (int s = 0; s < 4; s++) if (sc[s] > msc) msc = sc[s];
        for (int i = 0; i < 2; i++) if ((hole[i] >> 2) > top) over++;
        f[22] = over / 2.0f; f[23] = paired; f[24] = msc >= 3; f[25] = top / 12.0f;
        int lv, dr; strength(e, seat, &lv, &dr); f[26] = lv / 4.0f;
    }
    f[27] = e->dealer == seat;
    double bb = e->bb, pot = e->pot, tc = e->to_call;
    double my = e->stack[seat], opp = e->stack[other];
    double eff = my < opp ? my : opp;
    f[28] = (float)(pot + tc > 0 ? tc / (pot + tc) : 0);
    f[29] = (float)(fmin(tc / pot, 3.0) / 3.0);
    f[30] = (float)(log2(pot / bb) / 6.0);
    f[31] = (float)(log2(my / bb + 1) / 6.0);
    f[32] = (float)(log2(opp / bb + 1) / 6.0);
    f[33] = (float)(log2(eff / bb + 1) / 6.0);
    f[34] = (float)(log2(1 + eff / pot) / 4.0);
    f[35] = (float)(my > 0 ? fmin(tc / my, 1.0) : 1.0);
    f[36] = (float)((my + e->contrib[seat]) / (my + opp + pot));
    f[37] = (float)(log2(bb / 100.0) / 3.0);
    int h = e->hand_no, hl = 0;
    if (h <= (RULES_V2 ? 140 : 100)) hl = ((h - 1) / 20 + 1) * 20 - h;
    f[38] = hl / 20.0f; f[39] = (float)(h < 200 ? h : 200) / 100.0f; f[40] = h > 100;
    int rh = 0, ors = 0, mrs = 0, orp = 0, lastopp = 0;
    for (int i = 0; i < e->nh; i++) {
        Ev *v = &e->hist[i];
        if (v->kind != 5) continue;
        rh++;
        if (v->seat != seat && v->phase == 0) orp = 1;
        if (v->phase == e->phase) { if (v->seat == seat) mrs++; else ors++; }
        lastopp = v->seat != seat;
    }
    f[41] = (rh < 4 ? rh : 4) / 4.0f; f[42] = (ors < 3 ? ors : 3) / 3.0f; f[43] = (mrs < 3 ? mrs : 3) / 3.0f;
    f[44] = orp; f[45] = lastopp;
    double *st = e->stats[seat];
    f[46] = (float)((st[1] + 1) / (st[0] + 2));
    f[47] = (float)((st[3] + 1) / (st[2] + 2));
    f[48] = (float)((st[4] + 1) / (st[2] + 4));
    f[49] = (float)((st[6] + 1) / (st[5] + 2));
    f[50] = (float)((st[7] + 1) / (st[5] + 4));
    f[51] = (float)((st[9] + 1) / (st[8] + 2));
    f[52] = (float)(fmin(st[10], 40.0) / 40.0);
    f[53] = e->can_rs;
}

/* ---- public API ---- */
void fe_set_tables(const double *vsr, const double *pct) {
    init_tables();
    memcpy(VSR, vsr, sizeof(VSR)); memcpy(PCT, pct, sizeof(PCT));
}

Pool *pool_new(int n) {
    init_tables();
    Pool *p = (Pool *)calloc(1, sizeof(Pool));
    p->n = n; p->e = (Env *)calloc(n, sizeof(Env));
    return p;
}
void pool_free(Pool *p) { free(p->e); free(p); }

void env_reset_stacks(Pool *p, int i, uint64_t seed, int ctrl0, int ctrl1, int hero, int s0, int s1, int max_hands);
void env_reset(Pool *p, int i, uint64_t seed, int ctrl0, int ctrl1, int hero, int start_stack, int max_hands) {
    env_reset_stacks(p, i, seed, ctrl0, ctrl1, hero, start_stack, start_stack, max_hands);
}
void env_reset_stacks(Pool *p, int i, uint64_t seed, int ctrl0, int ctrl1, int hero, int s0, int s1, int max_hands) {
    int start_stack = (s0 + s1) / 2;
    Env *e = &p->e[i];
    int *inj = e->inj, inj_n = e->inj_n; double *ur = e->urand; int urn = e->urand_n;
    memset(e, 0, sizeof(Env));
    e->inj = inj; e->inj_n = inj_n; e->urand = ur; e->urand_n = urn;
    e->rs = seed * 0x9E3779B97F4A7C15ULL + 12345;
    e->ctrl[0] = ctrl0; e->ctrl[1] = ctrl1; e->hero = hero;
    e->start_stack = start_stack; e->max_hands = max_hands;
    e->stacks[0] = s0; e->stacks[1] = s1; e->phi = 0.5;
    start_hand(e);
    run(e);
}

void env_set_injection(Pool *p, int i, int *decks, int ndecks, double *ur, int nur) {
    Env *e = &p->e[i]; e->inj = decks; e->inj_n = ndecks; e->urand = ur; e->urand_n = nur; e->urand_i = 0;
}

int env_apply_raw(Pool *p, int i, int kind, int amount) {
    Env *e = &p->e[i];
    int err = apply(e, kind, amount);
    if (err) return err;
    run(e);
    return 0;
}

/* discrete action 0..5 -> engine action */
void env_apply_discrete(Pool *p, int i, int a) {
    Env *e = &p->e[i];
    int mask[NACT], amt[NACT];
    action_table(e, mask, amt);
    if (!mask[a]) a = 1;  /* defensive: an illegal choice becomes check/call */
    if (a == 0) apply(e, 0, 0);
    else if (a == 1) apply(e, e->to_call > 0 ? 2 : 1, 0);
    else apply(e, 3, amt[a]);
    run(e);
}

void pool_step(Pool *p, const int *idx, const int *acts, int n) {
    for (int k = 0; k < n; k++) env_apply_discrete(p, idx[k], acts[k]);
}

/* obs rows for the acting seat of each listed env; meta: actor, ctrl */
void pool_obs(Pool *p, const int *idx, int n, float *obs, unsigned char *mask, int *meta, int *amts) {
    for (int k = 0; k < n; k++) {
        Env *e = &p->e[idx[k]];
        features(e, e->actor, obs + (size_t)k * D_OBS);
        int m[NACT], a[NACT];
        action_table(e, m, a);
        for (int j = 0; j < NACT; j++) { mask[k * NACT + j] = (unsigned char)m[j]; if (amts) amts[k * NACT + j] = a[j]; }
        meta[k * 2] = e->actor; meta[k * 2 + 1] = e->ctrl[e->actor];
    }
}

/* info rows: done winner hand_no phi actor hero stack0 stack1 */
void pool_info(Pool *p, const int *idx, int n, double *out) {
    for (int k = 0; k < n; k++) {
        Env *e = &p->e[idx[k]]; double *o = out + k * 8;
        o[0] = e->done; o[1] = e->winner; o[2] = e->hand_no; o[3] = e->phi;
        o[4] = e->actor; o[5] = e->hero; o[6] = e->stacks[0]; o[7] = e->stacks[1];
    }
}

/* state dump for tests */
void env_state(Pool *p, int i, int *out) {
    Env *e = &p->e[i]; int k = 0;
    out[k++] = e->dealer; out[k++] = e->hole[0][0]; out[k++] = e->hole[0][1]; out[k++] = e->hole[1][0]; out[k++] = e->hole[1][1];
    for (int j = 0; j < 5; j++) out[k++] = e->fboard[j];
    out[k++] = e->stack[0]; out[k++] = e->stack[1]; out[k++] = e->pot; out[k++] = e->to_call;
    out[k++] = e->min_raise; out[k++] = e->max_raise; out[k++] = e->can_rs; out[k++] = e->phase;
    out[k++] = e->stacks[0]; out[k++] = e->stacks[1]; out[k++] = e->nh; out[k++] = e->hand_no; out[k++] = e->done;
    out[k++] = e->bb;
}
int env_hist(Pool *p, int i, int *out) {
    Env *e = &p->e[i];
    for (int j = 0; j < e->nh; j++) { out[j * 4] = e->hist[j].seat; out[j * 4 + 1] = e->hist[j].kind; out[j * 4 + 2] = e->hist[j].amt; out[j * 4 + 3] = e->hist[j].phase; }
    return e->nh;
}
void env_stats(Pool *p, int i, int seat, double *out) { memcpy(out, p->e[i].stats[seat], sizeof(double) * NST); }
