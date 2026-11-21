"""Decision logic for the heads-up No-Limit Hold'em bot.

Everything here is a pure function of the ``GameState`` the SDK hands us plus the
online opponent model, so the same code runs live and in the local simulator.

Structure
  * Preflop, stack-depth aware.  Short stacks (<= 15 BB) shove or fold using an
    expected value computed against the opponent's calling range, whose prior is
    the CFR+ Nash call table.  Between 15 and 40 BB we compare jam, call and fold
    by EV against the opponent's range narrowed by what he has done.  Deeper we
    open, 3-bet for value and call by pot odds against his narrowed range.
  * Postflop: Monte Carlo equity against a range narrowed by every action he
    took this hand, then pot odds, value betting, semi-bluffs and bluffs whose
    frequency follows his observed fold-to-bet.
Every returned action is validated against ``valid_actions``.
"""

from __future__ import annotations

import math
import os
import random

from chipzen import Action

from . import preflop as pf
from .cards import CLASS_SIZE, cards_from, hand_class
from .evaluator import evaluate
from .history import parse_history
from .model import OpponentModel
from .ranges import COMBO_CLASS, RangeBuilder, mc_equity, weighted_win_fraction

SHOVE_FOLD_MAX_BB = 15.0  # at or below this effective depth: shove or fold
JAM_ZONE_MAX_BB = 40.0  # up to here: compare jam / call / fold by EV


def _clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


class MatchUtility:
    """Win-probability utility of a chip stack in a winner-take-all heads-up match.

    Chip EV is the wrong objective when the match is decided by who busts first and
    we are the stronger player: a 55% coin flip for the whole stack is +EV in chips
    but loses win probability.  Modelling the match as a random walk with drift
    ``mu`` and variance ``sigma^2`` per hand (in big blinds) gives the gambler's
    ruin win probability  U(x) = (1 - exp(-lam x)) / (1 - exp(-lam N))  with
    ``lam = 2 mu / sigma^2``: concave (risk averse) when we have an edge and
    convex when we trail.  The drift starts at a conservative prior and moves
    slowly with our observed results.
    """

    PRIOR_MU = 0.1  # big blinds per hand; sweeps showed more risk aversion loses
    PRIOR_SIGMA = 7.0
    PRIOR_HANDS = 60.0

    def __init__(self):
        self.n = 0
        self.total = 0.0
        self.total_sq = 0.0

    def add_hand(self, net_bb: float) -> None:
        self.n += 1
        self.total += net_bb
        self.total_sq += net_bb * net_bb

    def lam_per_bb(self) -> float:
        k = self.PRIOR_HANDS
        mu = (k * self.PRIOR_MU + self.total) / (k + self.n)
        mu = _clamp(mu, 0.02, 1.0)
        var = (k * self.PRIOR_SIGMA ** 2 + self.total_sq) / (k + self.n)
        var = max(var, 9.0)
        return 2.0 * mu / var

    def make(self, total_chips: float, bb: float):
        lam = self.lam_per_bb() / max(bb, 1.0)
        denom = math.expm1(-lam * total_chips)
        if abs(denom) < 1e-12:
            return lambda x: _clamp(x, 0.0, total_chips) / max(total_chips, 1.0)

        def u(x: float) -> float:
            x = _clamp(x, 0.0, total_chips)
            return math.expm1(-lam * x) / denom

        return u


class Brain:
    def __init__(self, seed: int | None = None):
        if seed is None:
            seed = int.from_bytes(os.urandom(8), "little")
        self.rng = random.Random(seed)
        self.model = OpponentModel()
        self.ranges = RangeBuilder()
        self.my_seat: int | None = None
        self.start_stacks: dict[int, int] = {}
        self.last_debug: dict = {}
        self.utility = MatchUtility()

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    def _context(self, state):
        me = state.your_seat
        self.my_seat = me
        valid = set(state.valid_actions or ())
        hole = cards_from(state.hole_cards)
        board = cards_from(state.board)
        others = [s for s in range(len(state.opponent_stacks) + 1) if s != me]
        opp_stack = dict(zip(others, state.opponent_stacks))
        info = parse_history(state.action_history)
        starts = {me: state.your_stack + info.contrib.get(me, 0)}
        for s, st in opp_stack.items():
            starts[s] = st + info.contrib.get(s, 0)
        info = parse_history(state.action_history, starts)
        live = [s for s in others if s not in info.folded and (s in info.seats or opp_stack[s] > 0)]
        bb = info.big_blind or max(state.min_raise // 2, 1)
        n_live = len(live) + 1
        seats_live = sorted([me, *live, state.dealer_seat])
        seats_live = sorted(set(seats_live))
        pos = (seats_live.index(me) - seats_live.index(state.dealer_seat)) % len(seats_live)
        opp_start = max((starts[s] for s in live), default=starts[me])
        ctx = {
            "me": me, "valid": valid, "hole": hole, "board": board, "info": info,
            "live": live, "opp_stack": opp_stack, "bb": bb, "n_live": n_live,
            "ip": pos == 0 or (len(live) == 1 and state.dealer_seat == me),
            "eff_bb": min(starts[me], opp_start) / bb,
            "my_stack": state.your_stack, "pot": state.pot, "to_call": state.to_call,
            "my_street": info.street_contrib.get(me, 0),
            "opp_behind": max((opp_stack[s] for s in live), default=0),
            "phase": state.phase, "state": state,
        }
        total = state.your_stack + sum(state.opponent_stacks) + state.pot
        ctx["u"] = self.utility.make(total, bb)
        return ctx

    # ------------------------------------------------------------------
    # Action constructors (always legal)
    # ------------------------------------------------------------------

    def _raise_to(self, ctx, target: int, state) -> Action:
        valid = ctx["valid"]
        if "raise" not in valid or state.max_raise <= 0:
            return self._call(ctx)
        lo = min(state.min_raise, state.max_raise)
        hi = state.max_raise
        target = int(round(target))
        # a bet that commits most of the stack is just a shove
        if target >= ctx["my_street"] + 0.7 * (hi - ctx["my_street"]) or target >= hi:
            target = hi
        target = max(lo, min(hi, target))
        return Action.raise_to(target)

    def _call(self, ctx) -> Action:
        valid = ctx["valid"]
        if "call" in valid:
            return Action.call()
        if "check" in valid:
            return Action.check()
        return self._fold(ctx)

    def _check_or_fold(self, ctx) -> Action:
        if "check" in ctx["valid"]:
            return Action.check()
        return self._fold(ctx)

    def _fold(self, ctx) -> Action:
        valid = ctx["valid"]
        if "fold" in valid:
            return Action.fold()
        if "check" in valid:
            return Action.check()
        return Action.call()

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def decide(self, state) -> Action:
        ctx = self._context(state)
        valid = ctx["valid"]
        if not valid:
            return Action.check()
        if len(ctx["hole"]) != 2:
            return self._check_or_fold(ctx)
        self.ranges.new_hand((state.hand_number, tuple(ctx["hole"])))
        # nothing to decide when only call/fold remain and the call is free
        if ctx["phase"] == "preflop":
            act = self._preflop(ctx, state)
        else:
            act = self._postflop(ctx, state)
        return self._validate(act, ctx, state)

    def _validate(self, act: Action, ctx, state) -> Action:
        valid = ctx["valid"]
        if act.action == "raise":
            if "raise" not in valid:
                return self._call(ctx)
            lo = min(state.min_raise, state.max_raise)
            amt = max(lo, min(state.max_raise, act.amount))
            return Action.raise_to(amt)
        if act.action in valid:
            return act
        if act.action == "fold" and "check" in valid:
            return Action.check()
        if act.action == "check" and "call" in valid and ctx["to_call"] <= 0:
            return Action.call()
        return self._check_or_fold(ctx)

    # ------------------------------------------------------------------
    # Preflop
    # ------------------------------------------------------------------

    def _opp_class_weights(self, ctx, seat) -> list[float]:
        """Class weights of the opponent's range given his preflop actions."""
        stats = self.model.get(seat)
        w = self.ranges.build(ctx["info"], ctx["board"], seat, stats, ctx["eff_bb"], ctx["hole"])
        cw = [0.0] * 169
        for i, c in enumerate(COMBO_CLASS):
            cw[c] += w[i]
        return [cw[c] / max(CLASS_SIZE[c], 1) for c in range(169)]

    @staticmethod
    def _continuing(cls_w: list[float], keep: float) -> list[float]:
        """The strongest slice of a class range holding ``keep`` of its total weight."""
        total = sum(w * s for w, s in zip(cls_w, CLASS_SIZE))
        target = keep * total
        out = [0.0] * 169
        acc = 0.0
        for c in sorted(range(169), key=lambda i: -pf.PCT[i]):
            if acc >= target:
                break
            out[c] = cls_w[c]
            acc += cls_w[c] * CLASS_SIZE[c]
        return out

    @staticmethod
    def _call_gain(ctx, e: float) -> float:
        """Utility gained by calling with win probability ``e`` (versus folding)."""
        u, S = ctx["u"], ctx["my_stack"]
        tc = min(ctx["to_call"], S)  # a short call: the excess of his bet goes back to him
        pot = ctx["pot"] - (ctx["to_call"] - tc)
        return e * u(S + pot) + (1 - e) * u(S - tc) - u(S)

    @staticmethod
    def _aggr_gain(ctx, f: float, eq_c: float, tm: float, r_re: float = 0.0,
                   eq_raised: float = 0.0) -> float:
        """Utility gained by betting ``tm`` chips (jam): he folds with probability ``f``,
        otherwise we win with probability ``eq_c`` at showdown."""
        u, S, pot, tc = ctx["u"], ctx["my_stack"], ctx["pot"], ctx["to_call"]
        called = eq_c * u(S + pot + tm - tc) + (1 - eq_c) * u(S - tm)
        if r_re <= 0.0 or tm >= S:
            return f * u(S + pot) + (1 - f) * called - u(S)
        # he raises: continue only if that beats folding (we assume a raise of about our size)
        extra = min(tm, S - tm)
        cont = eq_raised * u(S + pot + tm - tc + extra) + (1 - eq_raised) * u(S - tm - extra)
        raised = max(cont, u(S - tm))
        return f * u(S + pot) + r_re * raised + (1 - f - r_re) * called - u(S)

    def _preflop(self, ctx, state) -> Action:
        c1, c2 = ctx["hole"]
        cls = hand_class(c1, c2)
        pct = pf.PCT[cls]
        info = ctx["info"]
        bb = ctx["bb"]
        eff = ctx["eff_bb"]
        n_raises = info.preflop_raises
        to_call = ctx["to_call"]
        pot = ctx["pot"]
        my_stack = ctx["my_stack"]
        live = ctx["live"]
        seat = live[0] if live else None
        stats = self.model.get(seat) if seat is not None else None
        multiway = ctx["n_live"] > 2

        if n_raises == 0:
            if to_call > 0:  # first to act (button / small blind): open, limp-fold or shove
                return self._open(ctx, state, cls, pct, eff, stats)
            # big blind with the option after a limp
            iso = 0.55 if not multiway else 0.7
            if pct >= iso and ctx["opp_behind"] > 0:
                if eff <= 12:
                    return self._raise_to(ctx, my_stack + ctx["my_street"], state)
                return self._raise_to(ctx, 3.5 * bb, state)
            return self._check_or_fold(ctx)

        # Facing a raise
        if seat is None:
            return self._call(ctx)
        cls_w = self._opp_class_weights(ctx, seat)
        eq = pf.equity_vs_range(cls, cls_w)
        if multiway:
            eq = eq ** (ctx["n_live"] - 1) * 1.15
        all_in_call = to_call >= my_stack
        if all_in_call:
            return self._call(ctx) if self._call_gain(ctx, eq) > 0 else self._fold(ctx)
        real = 0.95 if ctx["ip"] else 0.84
        if eff < 20:
            real = min(1.0, real + 0.05)
        best, best_gain = "fold", 0.0
        g_call = self._call_gain(ctx, eq * real)
        if g_call > best_gain:
            best, best_gain = "call", g_call
        raise_ok = "raise" in ctx["valid"] and ctx["opp_behind"] > 0 and not multiway

        if raise_ok and eff <= JAM_ZONE_MAX_BB:
            counter = stats.fold_to_3bet if n_raises == 1 else stats.fold_to_4bet
            f = _clamp(counter.rate(), 0.1, 0.9)
            eq_c = pf.equity_vs_range(cls, self._continuing(cls_w, 1.0 - f))
            tm = min(my_stack, to_call + ctx["opp_behind"])
            g_jam = self._aggr_gain(ctx, f, eq_c, tm)
            if g_jam > best_gain + 1e-4:
                best, best_gain = "jam", g_jam
        elif raise_ok:
            # deep: 3-bet / 4-bet for value, plus a few suited bluffs against folders
            size = (3.0 if ctx["ip"] else 3.6) * (to_call + ctx["my_street"])
            if n_raises >= 2:
                size = 2.3 * (to_call + ctx["my_street"])
            value = eq >= 0.60 and pct >= 0.85
            f = _clamp(stats.fold_to_3bet.rate(), 0.1, 0.9)
            suited_or_ace = (c1 & 3) == (c2 & 3) or (c1 >> 2) == 12 or (c2 >> 2) == 12
            bluff = (
                n_raises == 1 and f > 0.5 and 0.3 <= pct <= 0.7 and suited_or_ace
                and self.rng.random() < 0.4
            )
            if value or bluff:
                return self._raise_to(ctx, size, state)
        if best == "jam":
            return self._raise_to(ctx, ctx["my_street"] + my_stack, state)
        if best == "call":
            return self._call(ctx)
        return self._fold(ctx)

    def _open(self, ctx, state, cls, pct, eff, stats) -> Action:
        bb = ctx["bb"]
        my_stack = ctx["my_stack"]
        sb_post = ctx["my_street"]
        multiway = ctx["n_live"] > 2
        if multiway:
            th = 0.55 if ctx["ip"] else 0.62
            return self._raise_to(ctx, 3 * bb, state) if pct >= th else self._check_or_fold(ctx)
        if eff <= SHOVE_FOLD_MAX_BB and "raise" in ctx["valid"]:
            nash = pf.nash_call(eff)
            obs = pf.top_range(_clamp(stats.call_shove.rate(), 0.05, 0.95))
            mix = stats.call_shove.opp / (stats.call_shove.opp + 20.0)
            call_w = pf.blend(nash, obs, mix)
            p_call = pf.mean_weight(call_w)
            eq = pf.equity_vs_range(cls, call_w)
            tm = min(my_stack, ctx["to_call"] + ctx["opp_behind"])
            if self._aggr_gain(ctx, 1 - p_call, eq, tm) > 1e-4:
                return self._raise_to(ctx, sb_post + my_stack, state)
            return self._fold(ctx)
        ftr = stats.pre_fold_to_raise.rate() if stats else 0.4
        tb = stats.three_bet.rate() if stats else 0.1
        th = 0.28 - (ftr - 0.4) * 0.5 + max(0.0, tb - 0.15) * 1.5
        th = _clamp(th, 0.08, 0.6)
        if eff < 25:
            th = max(th, 0.30)
        if pct >= th:
            return self._raise_to(ctx, (2.3 if eff < 30 else 2.5) * bb, state)
        return self._fold(ctx)

    # ------------------------------------------------------------------
    # Postflop
    # ------------------------------------------------------------------

    def _postflop(self, ctx, state) -> Action:
        hole, board, info = ctx["hole"], ctx["board"], ctx["info"]
        live = ctx["live"]
        pot, to_call = ctx["pot"], ctx["to_call"]
        my_stack, my_street = ctx["my_stack"], ctx["my_street"]
        if not live:
            return self._check_or_fold(ctx)
        multiway = len(live) > 1
        dead = hole + board
        ranges = []
        for s in live:
            ranges.append(
                self.ranges.build(info, board, s, self.model.get(s), ctx["eff_bb"], dead)
            )
        # focus opponent: the one who acted last aggressively, else the first
        focus = live[0]
        for ev in reversed(info.events):
            if ev.seat in live and ev.kind == "raise":
                focus = ev.seat
                break
        st = self.model.get(focus)
        tab = self.ranges.table(board)
        my_score = evaluate(hole + board)
        made = 1.0
        for r in ranges:
            made *= weighted_win_fraction(my_score, tab, r)
        river = len(board) >= 5
        if river and not multiway:
            eq = made
        else:
            eq = mc_equity(hole, board, ranges, self.rng, n=500 if not multiway else 400)
        draw = (not river) and (eq - made) > 0.10
        self.last_debug = {"eq": eq, "made": made, "draw": draw}

        if not multiway:
            eq_half = self._equity_vs_top(ctx, ranges[0], tab, river, 0.5)
            eq_q = self._equity_vs_top(ctx, ranges[0], tab, river, 0.2)
            return self._ev_decide(ctx, state, st, eq, eq_half, eq_q, river)
        allin_call = to_call >= my_stack
        if to_call > 0:
            return self._facing_bet(ctx, state, st, eq, draw, river, multiway, allin_call)
        return self._can_bet(ctx, state, st, eq, made, draw, river, multiway)

    @staticmethod
    def _top_fraction(weights, tab, frac: float):
        """The strongest ``frac`` of a range by current strength (made hand plus draws)."""
        items = [(tab.pct[i], w, i) for i, w in enumerate(weights)
                 if w > 0.0 and tab.score[i] is not None]
        items.sort(reverse=True)
        total = sum(w for _, w, _ in items)
        out = [0.0] * len(weights)
        acc = 0.0
        for _, w, i in items:
            if acc >= frac * total:
                break
            out[i] = w
            acc += w
        return out

    def _equity_vs_top(self, ctx, weights, tab, river, frac) -> float:
        top = self._top_fraction(weights, tab, frac)
        if river:
            return weighted_win_fraction(evaluate(ctx["hole"] + ctx["board"]), tab, top)
        return mc_equity(ctx["hole"], ctx["board"], [top], self.rng, n=250)

    @staticmethod
    def _fold_prob(f0: float, x: float, xref: float, observed: int) -> float:
        """Chance he folds to a bet of ``x`` pots given his fold rate ``f0`` at ``xref`` pots."""
        if f0 <= 0.0:
            return 0.0
        f = 1.0 - (1.0 - f0) ** (x / xref)
        return min(f, f0 * 1.5 + 0.05 * min(observed, 4) / 4, 0.85)

    def _ev_decide(self, ctx, state, st, eq, eq_half, eq_q, river) -> Action:
        """Pick fold / check / call / bet / raise by expected chips against his model.

        Each aggressive option is valued as  f * pot + (1 - f) * (equity when called *
        (pot + 2 * risk) - risk)  where ``f`` is his fold probability for that size
        (learned fold-to-bet, scaled by size) and the equity when called is taken
        against the stronger part of his range that does not fold.
        """
        pot, c, S = ctx["pot"], ctx["to_call"], ctx["my_stack"]
        my_street = ctx["my_street"]
        real = 1.0 if river else (0.97 if ctx["ip"] else 0.90)
        can_raise = "raise" in ctx["valid"] and ctx["opp_behind"] > 0 and state.max_raise > 0

        def eq_called(f):
            keep = 1.0 - f
            if keep >= 1.0:
                return eq
            if keep >= 0.5:
                return eq + (eq_half - eq) * (1.0 - keep) / 0.5
            return min(1.0, eq_half + (eq_half - eq) * (0.5 - keep) / 0.5 * 0.8)

        if c > 0 and c >= S:  # a call is all-in
            return self._call(ctx) if self._call_gain(ctx, eq) > 1e-4 else self._fold(ctx)
        f0 = st.fold_to_bet.rate() if c == 0 else st.fold_to_raise_post.rate()
        n_obs = st.fold_to_bet.opp if c == 0 else st.fold_to_raise_post.opp
        xref = 0.6 if c == 0 else 1.0
        u = ctx["u"]
        # chance he raises our bet (we then fold unless our equity against a raising range is good)
        r_re = _clamp(st.raise_vs_bet.rate(), 0.02, 0.45) * (1.0 if c == 0 else 0.6)
        if c > 0:
            g_call = self._call_gain(ctx, eq * real)
            g_hold = max(g_call, 0.0)
            hold = self._call(ctx) if g_call > 0 else self._fold(ctx)
        else:
            g_hold = eq * real * (u(S + pot) - u(S))
            hold = self._check_or_fold(ctx)
        best_gain, best_target = g_hold, None
        if can_raise:
            sizes = (0.33, 0.66, 1.0) if n_obs < 4 else (0.33, 0.66, 1.0, 1.6)
            level = my_street + c
            for x in sizes:
                target = level + max(x * pot, ctx["bb"]) if c == 0 else level + x * (pot + c)
                target = min(target, state.max_raise)
                if target < min(state.min_raise, state.max_raise):
                    target = min(state.min_raise, state.max_raise)
                a = target - my_street  # chips we add
                if a >= 0.7 * S:
                    target = state.max_raise
                    a = S
                x_eff = max((target - level) / max(pot, 1), 0.05)
                f = self._fold_prob(f0, x_eff, xref, n_obs)
                g = self._aggr_gain(ctx, f, min(1.0, eq_called(f + 0.5 * r_re) * real), a,
                                    r_re, eq_q * real)
                if g > best_gain + 0.002:
                    best_gain, best_target = g, target
        if best_target is not None:
            return self._raise_to(ctx, best_target, state)
        return hold

    def _size_to(self, ctx, frac: float) -> int:
        return ctx["my_street"] + max(frac * ctx["pot"], ctx["bb"])

    def _facing_bet(self, ctx, state, st, eq, draw, river, multiway, allin_call) -> Action:
        pot, to_call = ctx["pot"], ctx["to_call"]
        if allin_call:
            return self._call(ctx) if self._call_gain(ctx, eq) > 1e-4 else self._fold(ctx)
        real = 1.0 if river else (0.96 if ctx["ip"] else 0.90)
        margin = 0.02 + (0.04 if multiway else 0.0)
        can_raise = "raise" in ctx["valid"] and ctx["opp_behind"] > to_call
        strong = 0.82 + (0.06 if multiway else 0.0)
        if can_raise and eq >= strong and self.rng.random() < 0.85:
            frac = 1.0 if st.is_station() else 0.8
            level = ctx["my_street"] + to_call
            return self._raise_to(ctx, level + frac * (pot + to_call), state)
        if (
            can_raise and draw and not river and not multiway and 0.28 <= eq < 0.55
            and st.fold_to_bet.rate() * 0.9 >= 0.4 and self.rng.random() < 0.18
        ):
            level = ctx["my_street"] + to_call
            return self._raise_to(ctx, level + 0.75 * (pot + to_call), state)
        if (
            can_raise and not river and not multiway and eq < 0.35 and not draw
            and st.fold_to_raise_post.rate() >= 0.6 and st.fold_to_raise_post.opp >= 4
            and self.rng.random() < 0.35
        ):
            level = ctx["my_street"] + to_call
            return self._raise_to(ctx, level + 0.9 * (pot + to_call), state)
        if self._call_gain(ctx, eq * real - margin) > 0:
            return self._call(ctx)
        return self._fold(ctx)

    def _can_bet(self, ctx, state, st, eq, made, draw, river, multiway) -> Action:
        if "raise" not in ctx["valid"] or ctx["opp_behind"] <= 0:
            return self._check_or_fold(ctx)
        rng = self.rng
        pot = ctx["pot"]
        callish = st.fold_to_bet.rate()  # low means he pays us off
        station = st.is_station() or callish < 0.25
        hi = 0.80 + (0.06 if multiway else 0.0)
        mid = 0.62 + (0.06 if multiway else 0.0)
        if eq >= hi:
            # occasional slow-play on the flop against an aggressive opponent
            if (not river and ctx["phase"] == "flop" and st.bet.rate() > 0.6
                    and rng.random() < 0.3):
                return self._check_or_fold(ctx)
            frac = 1.0 if station else 0.75
            return self._raise_to(ctx, self._size_to(ctx, frac), state)
        if eq >= mid:
            frac = 0.75 if station else 0.55
            return self._raise_to(ctx, self._size_to(ctx, frac), state)
        if eq >= 0.52 and (station or (ctx["ip"] and rng.random() < 0.4)) and not multiway:
            return self._raise_to(ctx, self._size_to(ctx, 0.33), state)
        if multiway:
            return self._check_or_fold(ctx)
        if draw and not river and 0.28 <= eq < 0.55 and callish >= 0.3:
            p = _clamp(0.25 + 0.6 * (callish - 0.3), 0.15, 0.8)
            if rng.random() < p:
                return self._raise_to(ctx, self._size_to(ctx, 0.6), state)
        if eq < 0.30 and made < 0.30:
            frac = 0.66
            break_even = frac / (1 + frac)
            f_est = callish
            p = 0.5 if f_est > break_even + 0.05 else 0.08 if f_est > 0.3 else 0.0
            if river and p and rng.random() < p:
                return self._raise_to(ctx, self._size_to(ctx, frac), state)
            if not river and f_est > break_even + 0.1 and rng.random() < p * 0.7:
                return self._raise_to(ctx, self._size_to(ctx, frac), state)
        return self._check_or_fold(ctx)

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def observe_result(self, result: dict) -> None:
        if self.my_seat is None:
            return
        try:
            info = parse_history(result.get("action_history") or [])
            paid = sum(p.get("amount", 0) for p in result.get("payouts", [])
                       if p.get("seat") == self.my_seat)
            bb = max(info.big_blind, 1)
            self.utility.add_hand((paid - info.contrib.get(self.my_seat, 0)) / bb)
        except Exception:
            pass
        try:
            self.model.observe_hand(result, self.my_seat, self.start_stacks or None)
        except Exception:  # the model is a nicety; never let it break a match
            pass

    def set_start_stacks(self, stacks) -> None:
        self.start_stacks = {i: int(s) for i, s in enumerate(stacks or ())}
