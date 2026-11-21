"""Reference feature extractor (pure Python) for the RL policy.

This is the specification that rl/fastenv.c mirrors; tests/test_rl_env.py checks
the two agree decision by decision.  It is also what the deployed bot runs, so
it only needs the SDK ``GameState`` and ``nlhe`` helpers.

Observation: D_OBS floats.  Actions: 0 fold, 1 check/call, 2/3/4 raise 0.5/1/2
pot, 5 all-in, with a legality mask and the engine amount of each raise.
"""

from __future__ import annotations

import math

from nlhe import preflop as pf
from nlhe.cards import cards_from, hand_class
from nlhe.evaluator import category, evaluate

D_OBS = 54
NACT = 6
NST = 11
FRACS = (0.5, 1.0, 2.0)
PHASES = ("preflop", "flop", "turn", "river")
_SCHED = ((20, 100), (40, 150), (60, 200), (80, 300), (100, 400))

_STRAIGHT = [-1] * 8192
for _m in range(8192):
    for _h in range(12, 3, -1):
        _w = 0b11111 << (_h - 4)
        if _m & _w == _w:
            _STRAIGHT[_m] = _h
            break
    else:
        if _m & 0b1000000001111 == 0b1000000001111:
            _STRAIGHT[_m] = 3


RULES_V2 = True  # Chipzen server rules; tests flip it to compare with the legacy engine


def set_rules(v2: bool):
    global RULES_V2
    RULES_V2 = v2
    from rl import fastenv
    fastenv.set_rules(v2)


def bb_for(hand_no: int) -> int:
    for last, bb in _SCHED:
        if hand_no <= last:
            return bb
    if not RULES_V2:
        return 600
    return 600 if hand_no <= 120 else 800 if hand_no <= 140 else 1000


def draw_info(hole, board):
    """(flush draw flag, straight outs) exactly as ranges.draw_bonus counts them."""
    suits = [0] * 4
    for c in board:
        suits[c & 3] += 1
    fd = 0
    for c in hole:
        s = c & 3
        if suits[s] >= 2 and suits[s] + sum(1 for h in hole if (h & 3) == s) >= 4:
            fd = 1
            break
    bmask = 0
    for c in board:
        bmask |= 1 << (c >> 2)
    hmask = bmask
    for c in hole:
        hmask |= 1 << (c >> 2)
    outs = 0
    if _STRAIGHT[hmask] < 0:
        for r in range(13):
            if hmask >> r & 1:
                continue
            if _STRAIGHT[hmask | (1 << r)] >= 0 and _STRAIGHT[bmask | (1 << r)] < 0:
                outs += 1
    return fd, outs


def hand_strength(hole, board) -> float:
    """Win share against a uniformly random hand on the current board (ties half)."""
    used = set(hole) | set(board)
    rem = [c for c in range(52) if c not in used]
    ms = evaluate(list(hole) + list(board))
    w = 0.0
    n = 0
    for i in range(len(rem)):
        for j in range(i + 1, len(rem)):
            os_ = evaluate([rem[i], rem[j]] + list(board))
            w += 1.0 if ms > os_ else 0.5 if ms == os_ else 0.0
            n += 1
    return w / n


def level_of(hole, board) -> int:
    cat = category(evaluate(list(hole) + list(board)))
    top = max(c >> 2 for c in board)
    h0, h1 = hole[0] >> 2, hole[1] >> 2
    if cat >= 3:
        return 4
    if cat == 2:
        return 3
    if cat == 1:
        if h0 == h1 and h0 > top:
            return 3
        if max(h0, h1) == top:
            return 2
        return 1
    return 0


class Tracker:
    """Opponent statistics for one match, from finished hands."""

    def __init__(self):
        self.st = [0.0] * NST

    def update(self, history, dealer):
        """history: engine action_history of the finished hand (blinds included)."""
        st = self.st
        me = self.me
        bet = [0, 0]
        level = 0
        cur = "preflop"
        vol = False
        raised_pre = False
        for ev in history:
            if ev["phase"] != cur:
                cur = ev["phase"]
                bet = [0, 0]
                level = 0
            k = ev["action"]
            s = ev["seat"]
            if k in ("post_small_blind", "post_big_blind"):
                bet[s] += ev["amount"]
                level = max(level, bet[s])
                continue
            if s == me:
                # our own actions are not the opponent's statistics
                if k == "call":
                    bet[s] += ev["amount"]
                elif k in ("raise", "all_in"):
                    bet[s] = ev["amount"]
                    level = ev["amount"]
                    if cur == "preflop":
                        raised_pre = True
                if cur == "preflop":
                    vol = True
                continue
            facing = level > bet[s]
            is_raise = k in ("raise", "all_in")
            if cur == "preflop":
                if not vol and s == dealer:
                    st[0] += 1
                    if is_raise:
                        st[1] += 1
                vol = True
                if raised_pre and facing:
                    st[2] += 1
                    if k == "fold":
                        st[3] += 1
                    if is_raise:
                        st[4] += 1
            elif facing:
                st[5] += 1
                if k == "fold":
                    st[6] += 1
                if is_raise:
                    st[7] += 1
            else:
                st[8] += 1
                if is_raise:
                    st[9] += 1
            if k == "call":
                bet[s] += ev["amount"]
            if is_raise:
                bet[s] = ev["amount"]
                level = ev["amount"]
                if cur == "preflop":
                    raised_pre = True
        st[10] += 1

    me = 0


def replay(history, phase):
    """Per-street bets, hand contributions and raise counts at a decision."""
    bet = [0, 0]
    contrib = [0, 0]
    cur = "preflop"
    raises = []  # (seat, phase)
    for ev in history:
        if ev["phase"] != cur:
            cur = ev["phase"]
            bet = [0, 0]
        k = ev["action"]
        s = ev["seat"]
        if k in ("post_small_blind", "post_big_blind", "call"):
            bet[s] += ev["amount"]
            contrib[s] += ev["amount"]
        elif k in ("raise", "all_in"):
            contrib[s] += ev["amount"] - bet[s]
            bet[s] = ev["amount"]
            raises.append((s, ev["phase"]))
    if cur != phase:
        bet = [0, 0]
    return bet, contrib, raises


def action_table(state, bet_me):
    """(mask, amounts) of the six discrete actions."""
    tc = state.to_call
    mask = [0] * NACT
    amt = [0] * NACT
    mask[0] = 1 if tc > 0 else 0
    mask[1] = 1
    if "raise" not in state.valid_actions:
        return mask, amt
    lo = min(state.min_raise, state.max_raise)
    prev = -1
    for k, fr in enumerate(FRACS):
        t = bet_me + tc + fr * (state.pot + tc)
        t = min(t, state.max_raise)
        t = max(t, lo)
        a = int(t)
        amt[2 + k] = a
        if a < state.max_raise and a != prev:
            mask[2 + k] = 1
            prev = a
    mask[5] = 1
    amt[5] = state.max_raise
    return mask, amt


def build(state, tracker):
    """Observation vector, mask and raise amounts for the acting seat."""
    me = state.your_seat
    hole = cards_from(state.hole_cards)
    board = cards_from(state.board)
    nb = len(board)
    phase = state.phase
    si = PHASES.index(phase)
    f = [0.0] * D_OBS
    cls = hand_class(hole[0], hole[1])
    r1, r2 = sorted((hole[0] >> 2, hole[1] >> 2), reverse=True)
    f[0] = (pf.VS_RANDOM[cls] - 0.5) * 2
    f[1] = pf.PCT[cls]
    f[2] = 1.0 if r1 == r2 else 0.0
    f[3] = 1.0 if (hole[0] & 3) == (hole[1] & 3) else 0.0
    f[4] = r1 / 12.0
    f[5] = r2 / 12.0
    f[6 + si] = 1.0
    if nb == 0:
        f[10] = pf.VS_RANDOM[cls]
    else:
        f[10] = hand_strength(hole, board)
        cat = category(evaluate(hole + board))
        f[11 + min(cat, 7)] = 1.0
        if nb < 5:
            fd, outs = draw_info(hole, board)
            f[19] = float(fd)
            f[20] = 1.0 if outs >= 2 else 0.0
            f[21] = 1.0 if outs == 1 else 0.0
        top = max(c >> 2 for c in board)
        over = sum(1 for c in hole if (c >> 2) > top)
        ranks = [c >> 2 for c in board]
        suits = [c & 3 for c in board]
        f[22] = over / 2.0
        f[23] = 1.0 if len(set(ranks)) < len(ranks) else 0.0
        f[24] = 1.0 if max(suits.count(s) for s in range(4)) >= 3 else 0.0
        f[25] = top / 12.0
        f[26] = level_of(hole, board) / 4.0
    f[27] = 1.0 if state.dealer_seat == me else 0.0
    bet, contrib, raises = replay(state.action_history, phase)
    bb = bb_for(state.hand_number)
    pot = float(state.pot)
    tc = float(state.to_call)
    my = float(state.your_stack)
    opp = float(state.opponent_stacks[0])
    eff = min(my, opp)
    f[28] = tc / (pot + tc) if pot + tc > 0 else 0.0
    f[29] = min(tc / pot, 3.0) / 3.0
    f[30] = math.log2(pot / bb) / 6.0
    f[31] = math.log2(my / bb + 1) / 6.0
    f[32] = math.log2(opp / bb + 1) / 6.0
    f[33] = math.log2(eff / bb + 1) / 6.0
    f[34] = math.log2(1 + eff / pot) / 4.0
    f[35] = min(tc / my, 1.0) if my > 0 else 1.0
    f[36] = (my + contrib[me]) / (my + opp + pot)
    f[37] = math.log2(bb / 100.0) / 3.0
    h = state.hand_number
    hl = ((h - 1) // 20 + 1) * 20 - h if h <= (140 if RULES_V2 else 100) else 0
    f[38] = hl / 20.0
    f[39] = min(h, 200) / 100.0
    f[40] = 1.0 if h > 100 else 0.0
    rh = len(raises)
    ors = sum(1 for s, p in raises if s != me and p == phase)
    mrs = sum(1 for s, p in raises if s == me and p == phase)
    orp = any(s != me and p == "preflop" for s, p in raises)
    f[41] = min(rh, 4) / 4.0
    f[42] = min(ors, 3) / 3.0
    f[43] = min(mrs, 3) / 3.0
    f[44] = 1.0 if orp else 0.0
    f[45] = 1.0 if raises and raises[-1][0] != me else 0.0
    st = tracker.st
    f[46] = (st[1] + 1) / (st[0] + 2)
    f[47] = (st[3] + 1) / (st[2] + 2)
    f[48] = (st[4] + 1) / (st[2] + 4)
    f[49] = (st[6] + 1) / (st[5] + 2)
    f[50] = (st[7] + 1) / (st[5] + 4)
    f[51] = (st[9] + 1) / (st[8] + 2)
    f[52] = min(st[10], 40.0) / 40.0
    f[53] = 1.0 if "raise" in state.valid_actions else 0.0
    mask, amt = action_table(state, bet[me])
    return f, mask, amt
