"""Opponent range tracking and Monte Carlo equity.

An opponent's range is a weight for each of the 1326 hole-card combos.  It starts
uniform and is multiplied, action by action, by how likely that combo is to take
that action given what we know about the opponent (observed frequencies with a
prior).  Preflop actions weight combos by starting-hand class; postflop actions
weight them by their strength on the board at the time, including draws.
"""

from __future__ import annotations

import time
from bisect import bisect_left, bisect_right
from itertools import accumulate

from . import preflop as pf
from .cards import hand_class
from .evaluator import _STRAIGHT, evaluate

COMBOS = [(a, b) for a in range(52) for b in range(a + 1, 52)]
COMBO_CLASS = [hand_class(a, b) for a, b in COMBOS]


def _clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


# --------------------------------------------------------------------------
# Board-dependent strength tables
# --------------------------------------------------------------------------


def draw_bonus(hole, board) -> float:
    """Rough value of draws (flush and straight) as a percentile bonus."""
    suits = [0, 0, 0, 0]
    for c in board:
        suits[c & 3] += 1
    bonus = 0.0
    for c in hole:
        s = c & 3
        if suits[s] >= 2 and suits[s] + sum(1 for h in hole if (h & 3) == s) >= 4:
            bonus += 0.14
            break
    bmask = 0
    for c in board:
        bmask |= 1 << (c >> 2)
    hmask = bmask
    for c in hole:
        hmask |= 1 << (c >> 2)
    if _STRAIGHT[hmask] < 0:
        outs = 0
        for r in range(13):
            if hmask >> r & 1:
                continue
            if _STRAIGHT[hmask | (1 << r)] >= 0 and _STRAIGHT[bmask | (1 << r)] < 0:
                outs += 1
        bonus += 0.11 if outs >= 2 else 0.05 if outs == 1 else 0.0
    return bonus


class StreetTable:
    """Strength of every combo on one particular board."""

    def __init__(self, board):
        self.board = tuple(board)
        used = set(board)
        n = len(COMBOS)
        self.score = [None] * n
        scores = []
        for i, (a, b) in enumerate(COMBOS):
            if a in used or b in used:
                continue
            s = evaluate([a, b, *board])
            self.score[i] = s
            scores.append(s)
        scores.sort()
        total = len(scores)
        self.pct = [0.0] * n
        river = len(board) >= 5
        for i, s in enumerate(self.score):
            if s is None:
                continue
            lo = bisect_left(scores, s)
            hi = bisect_right(scores, s)
            p = (lo + 0.5 * (hi - lo)) / total
            if not river and p < 0.85:
                p = min(0.95, p + draw_bonus(COMBOS[i], board))
            self.pct[i] = p


# --------------------------------------------------------------------------
# Action likelihoods
# --------------------------------------------------------------------------


def pre_event_weights(ev, stats, eff_bb: float) -> list[float]:
    """169 class weights for 'a hand that takes this preflop action'."""
    if ev.kind == "raise":
        if ev.allin:
            if ev.raises_before == 0:
                prior = pf.nash_push(eff_bb) if eff_bb <= 25 else pf.top_range(0.25)
            else:
                prior = pf.top_range(0.12)
            obs = pf.top_range(_clamp(stats.shove_rate.rate() * 3, 0.03, 0.9))
            mix = stats.shove_rate.opp / (stats.shove_rate.opp + 20.0)
            return pf.blend(prior, obs, mix)
        if ev.raises_before == 0:
            return pf.top_range(_clamp(stats.open_raise.rate(), 0.15, 0.95))
        if ev.raises_before == 1:
            return pf.top_range(_clamp(max(stats.three_bet.rate() * 1.2, stats.aggression_floor()), 0.04, 0.6))
        return pf.top_range(max(0.07, stats.aggression_floor(0.7)))
    if ev.kind == "call":
        if ev.raises_before == 0:  # limp
            return pf.band_range(0.0, 1.0 - _clamp(stats.open_raise.rate(), 0.15, 0.95) + 0.05)
        hi = 1.0 - _clamp(stats.three_bet.rate() * 1.2, 0.04, 0.45)
        width = _clamp(stats.vpip.rate() - stats.pfr.rate() + 0.2, 0.15, 0.7)
        return pf.band_range(max(0.0, hi - width), hi)
    if ev.kind == "check":
        return pf.band_range(0.0, 0.8)
    return [1.0] * 169


def post_event_weight(pct, ev, stats) -> float:
    """Likelihood of a combo with strength percentile ``pct`` taking this action."""
    kind = ev.kind
    if kind == "raise":
        size = ev.amount / max(ev.pot_before, 1)
        base = max(stats.raise_vs_bet.rate() * 1.4 if ev.facing else stats.bet.rate(),
                   stats.aggression_floor())
        width = _clamp(base * (1.0 - 0.2 * min(size, 1.5)), 0.06, 0.9)
        if ev.allin:
            width = min(width, 0.3)
        bluff = 0.05 + (0.25 * stats.river_bet_bluff.rate() if ev.street == "river" else 0.08)
        d = (1.0 - width) - pct
        return 1.0 if d <= 0 else max(bluff, 1.0 - d / 0.12)
    if kind == "call":
        size = ev.to_call / max(ev.pot_before, 1)
        raise_w = _clamp(stats.raise_vs_bet.rate(), 0.03, 0.4)
        call_w = _clamp(1.0 - stats.fold_to_bet.rate() - raise_w, 0.15, 0.9)
        call_w *= 1.0 - 0.3 * min(size, 1.0)
        hi = 1.0 - raise_w * 0.7
        lo = hi - call_w
        if pct > hi:
            return 0.5
        if pct >= lo:
            return 1.0
        return max(0.04, 1.0 - (lo - pct) / 0.1)
    if kind == "check":
        return max(0.1, 1.0 - stats.bet.rate() * pct)
    return 1.0


# --------------------------------------------------------------------------
# Range building
# --------------------------------------------------------------------------


class RangeBuilder:
    """Rebuilds opponent ranges from the hand history at each decision."""

    def __init__(self):
        self._tables: dict[tuple, StreetTable] = {}
        self._hand_key = None

    def table(self, board) -> StreetTable:
        key = tuple(board)
        t = self._tables.get(key)
        if t is None:
            t = self._tables[key] = StreetTable(board)
        return t

    def new_hand(self, key):
        if key != self._hand_key:
            self._hand_key = key
            self._tables = {}

    def build(self, info, board, seat, stats, eff_bb, dead) -> list[float]:
        """Combo weights (length 1326) for one opponent seat, ``dead`` cards removed."""
        dead = set(dead)
        w = [0.0 if (a in dead or b in dead) else 1.0 for a, b in COMBOS]
        street_boards = {"flop": board[:3], "turn": board[:4], "river": board[:5]}
        tabs = {}
        for ev in info.events:
            if ev.seat != seat:
                continue
            if ev.street == "preflop":
                cw = pre_event_weights(ev, stats, eff_bb)
                for i, c in enumerate(COMBO_CLASS):
                    if w[i]:
                        w[i] *= cw[c]
            else:
                b = street_boards.get(ev.street)
                if not b or len(b) < 3:
                    continue
                tab = tabs.get(ev.street)
                if tab is None:
                    tab = tabs[ev.street] = self.table(b)
                for i in range(len(w)):
                    if w[i] and tab.score[i] is not None:
                        w[i] *= post_event_weight(tab.pct[i], ev, stats)
        total = sum(w)
        if total <= 0:  # the model ruled everything out: fall back to uniform
            return [0.0 if (a in dead or b in dead) else 1.0 for a, b in COMBOS]
        # keep a trickle of every live combo so a mis-modelled range cannot hit zero
        live = sum(1 for x in w if x > 0)
        floor = 0.003 * total / max(1, live)
        return [x + floor if x > 0 or (c[0] not in dead and c[1] not in dead) else 0.0
                for x, c in zip(w, COMBOS)]


# --------------------------------------------------------------------------
# Equity
# --------------------------------------------------------------------------


def weighted_win_fraction(my_score, table: StreetTable, weights) -> float:
    """Share (by weight) of an opponent range our current hand beats right now.

    On the river this is the exact equity; earlier it ignores future cards.
    """
    win = tot = 0.0
    sc = table.score
    for i, w in enumerate(weights):
        if w > 0.0:
            s = sc[i]
            if s is None:
                continue
            tot += w
            win += w if my_score > s else 0.5 * w if my_score == s else 0.0
    return win / tot if tot else 0.5


def mc_equity(hole, board, range_list, rng, n=500, budget_s=0.25) -> float:
    """Monte Carlo equity against one weighted range per live opponent."""
    dead = set(hole) | set(board)
    samplers = []
    for weights in range_list:
        combos, cum = [], []
        for i, w in enumerate(weights):
            if w > 0.0:
                a, b = COMBOS[i]
                if a not in dead and b not in dead:
                    combos.append((a, b))
                    cum.append(w)
        if not combos:
            return 0.5
        cum = list(accumulate(cum))
        samplers.append((combos, cum, cum[-1]))
    deck = [c for c in range(52) if c not in dead]
    need = 5 - len(board)
    rand = rng.random
    deadline = time.perf_counter() + budget_s
    score = 0.0
    done = 0
    for k in range(n):
        if k & 31 == 31 and time.perf_counter() > deadline:
            break
        used = set()
        hands = []
        ok = True
        for combos, cum, total in samplers:
            for _ in range(6):
                a, b = combos[min(bisect_right(cum, rand() * total), len(combos) - 1)]
                if a not in used and b not in used:
                    used.add(a)
                    used.add(b)
                    hands.append((a, b))
                    break
            else:
                ok = False
                break
        if not ok:
            continue
        runout = []
        while len(runout) < need:
            c = deck[int(rand() * len(deck))]
            if c not in used and c not in runout:
                runout.append(c)
        full = list(board) + runout
        mine = evaluate([*hole, *full])
        best = 0
        ties = 0
        for a, b in hands:
            s = evaluate([a, b, *full])
            if s > best:
                best, ties = s, 1
            elif s == best:
                ties += 1
        if mine > best:
            score += 1.0
        elif mine == best:
            score += 1.0 / (ties + 1)
        done += 1
    return score / done if done else 0.5
