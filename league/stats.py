"""Behavioural statistics from hand records (real replays or simulated hands).

One counter set serves three jobs: per-bot feature vectors for clustering, the
held-out validation table, and the engine-side check that a clone plays like its
source.  Every statistic is a (numerator, denominator) pair so rates carry a
binomial standard error.
"""

from __future__ import annotations

import math
from collections import defaultdict

from .context import (ALLIN, CALL, F_BET_L, F_BET_M, F_BET_S, F_BET_XL, F_LIMP, F_NOBET, F_OPEN,
                      F_VS_3BET, F_VS_OPEN, FOLD, RAISE, event_of_act)
from .replays import Act, HandRec

RATE_STATS = (
    "btn_open", "btn_limp", "bb_fold_vs_open", "bb_3bet", "btn_fold_vs_3bet",
    "pf_allin_short", "pf_allin_deep", "flop_bet", "turn_bet", "river_bet",
    "fold_to_bet", "post_agg", "wtsd", "fold_end",
)
SCALAR_STATS = ("open_size_bb",)
CLUSTER_STATS = (
    "btn_open", "btn_limp", "bb_fold_vs_open", "bb_3bet", "btn_fold_vs_3bet",
    "pf_allin_short", "flop_bet", "fold_to_bet", "post_agg", "wtsd",
)
AGGRESSIVE = (RAISE, ALLIN)


def new_counter():
    return defaultdict(lambda: [0, 0])


def add_hand(counter, hand: HandRec, include=None):
    """Accumulate one hand; ``include(seat)`` filters which seats count (default both)."""
    ok = [True, True] if include is None else [bool(include(s)) for s in (0, 1)]
    for a in hand.acts:
        if not ok[a.seat]:
            continue
        is_btn = a.seat == hand.button
        ctx, code, _ = event_of_act(a, is_btn)
        street, _, fcl, stk = ctx
        if street == 0:
            if fcl == F_OPEN:
                c = counter["btn_open"]
                c[1] += 1
                c[0] += code in AGGRESSIVE
                c = counter["btn_limp"]
                c[1] += 1
                c[0] += code == CALL
                if code == RAISE:
                    counter["open_size_bb"][0] += a.put / a.bb
                    counter["open_size_bb"][1] += 1
            elif fcl == F_VS_OPEN and not is_btn:
                c = counter["bb_fold_vs_open"]
                c[1] += 1
                c[0] += code == FOLD
                c = counter["bb_3bet"]
                c[1] += 1
                c[0] += code in AGGRESSIVE
            elif fcl == F_VS_3BET and is_btn:
                c = counter["btn_fold_vs_3bet"]
                c[1] += 1
                c[0] += code == FOLD
            if fcl in (F_OPEN, F_LIMP, F_VS_OPEN, F_VS_3BET):
                key = "pf_allin_short" if stk <= 1 else "pf_allin_deep"
                c = counter[key]
                c[1] += 1
                c[0] += code == ALLIN
        else:
            if fcl == F_NOBET:
                c = counter[("flop_bet", "turn_bet", "river_bet")[street - 1]]
                c[1] += 1
                c[0] += code in AGGRESSIVE
            if fcl in (F_BET_S, F_BET_M, F_BET_L, F_BET_XL):
                c = counter["fold_to_bet"]
                c[1] += 1
                c[0] += code == FOLD
            if code in AGGRESSIVE or code == CALL:
                c = counter["post_agg"]
                c[1] += 1
                c[0] += code in AGGRESSIVE
    saw_flop = hand.ended != "preflop"
    for s in (0, 1):
        if not ok[s]:
            continue
        counter["hands"][0] += 1
        if saw_flop:
            c = counter["wtsd"]
            c[1] += 1
            c[0] += hand.showdown
        c = counter["fold_end"]
        c[1] += 1
        last = next((a for a in reversed(hand.acts)), None)
        c[0] += bool(last and last.kind == "fold" and last.seat == s)


def rates(counter):
    out = {}
    for k in RATE_STATS:
        n, d = counter[k] if k in counter else (0, 0)
        out[k] = (n / d if d else float("nan"), d)
    n, d = counter["open_size_bb"] if "open_size_bb" in counter else (0, 0)
    out["open_size_bb"] = (n / d if d else float("nan"), d)
    return out


def se(p: float, n: int) -> float:
    if n <= 0 or p != p:
        return float("nan")
    return math.sqrt(max(p * (1 - p), 0.0) / n) if p <= 1 else float("nan")


def rec_from_engine(names, result, dealer, bb, stacks_start, match_id="sim") -> HandRec:
    """Rebuild a ``HandRec`` from an engine hand result (raise amounts are raise-to totals)."""
    rec = HandRec(match_id, result["hand_number"], tuple(names), dealer, bb,
                  tuple(stacks_start), {}, [])
    stack = list(stacks_start)
    put = [0, 0]
    pot = level = nraise = 0
    cur = None
    for e in result["action_history"]:
        seat, kind, amt, phase = e["seat"], e["action"], e["amount"], e["phase"]
        if phase != cur:
            put, level, nraise, cur = [0, 0], 0, 0, phase
        if kind.startswith("post_"):
            put[seat] += amt
            stack[seat] -= amt
            pot += amt
            level = max(level, put[seat])
            continue
        to_call = level - put[seat]
        act = Act(seat, kind, phase, put[seat], to_call, pot, stack[seat], nraise,
                  opp_stack=stack[1 - seat], bb=bb)
        if kind == "call":
            stack[seat] -= amt
            put[seat] += amt
            pot += amt
            act.added, act.put = amt, put[seat]
        elif kind == "raise":
            add = amt - put[seat]
            stack[seat] -= add
            pot += add
            put[seat] = level = amt
            nraise += 1
            act.added, act.put, act.raise_total = add, amt, amt
        rec.acts.append(act)
        rec.ended = phase
    rec.showdown = bool(result.get("showdown"))
    rec.winner_seats = tuple(result.get("winner_seats", ()))
    return rec
