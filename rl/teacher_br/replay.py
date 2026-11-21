"""Rebuild the betting-round bookkeeping (level, last raise, reopen flags) from a GameState.

State vector S (shared with dp.py / search.py): 0 sU, 1 sO, 2 bU, 3 bO, 4 level, 5 last_raise,
6 canraise U, 7 canraise O, 8 acted U, 9 acted O, 10 first, 11 raise seen preflop.
Seat 0 is us, seat 1 the opponent.
"""

from __future__ import annotations

import numpy as np

from . import dp

PHASES = ("preflop", "flop", "turn", "river")


def _new_street(S, bb):
    S[2] = S[3] = 0
    S[4] = 0
    S[5] = bb
    S[6] = S[7] = 1
    S[8] = S[9] = 0
    S[10] = 1


def replay_full(state, bb):
    """Return (S, sU0, street, events); events are (S before the action, seat, kind, amount,
    street) for every non-blind action in the hand, seat 0 = us."""
    me = state.your_seat
    street = PHASES.index(state.phase)
    contrib = [0, 0]
    bet = [0, 0]
    cur = "preflop"
    for e in state.action_history:
        a = 0 if e["seat"] == me else 1
        if e["phase"] != cur:
            cur = e["phase"]
            bet = [0, 0]
        if e["action"] in ("post_small_blind", "post_big_blind", "call"):
            contrib[a] += e["amount"]
            bet[a] += e["amount"]
        elif e["action"] == "raise":
            contrib[a] += e["amount"] - bet[a]
            bet[a] = e["amount"]
    sU0 = state.your_stack + contrib[0]
    S = np.array([sU0, 2 * 10000 - sU0, 0, 0, 0, bb, 1, 1, 0, 0, 1, 0], dtype=np.int64)
    events = []
    cur = "preflop"
    for e in state.action_history:
        a = 0 if e["seat"] == me else 1
        kind = e["action"]
        if kind in ("post_small_blind", "post_big_blind"):
            S[a] -= e["amount"]
            S[2 + a] += e["amount"]
            S[4] = max(S[2], S[3])
            continue
        if e["phase"] != cur:
            cur = e["phase"]
            _new_street(S, bb)
        events.append((S.copy(), a, kind, e["amount"], PHASES.index(e["phase"])))
        raised = S[11]
        if kind == "call":
            S = dp.after_call(S, a, e["amount"])
        elif kind == "raise":
            S = dp.after_raise(S, a, e["amount"])
            if cur == "preflop":
                raised = 1
        elif kind == "check":
            S[8 + a] = 1
        S[10] = 0
        S[11] = raised
    if street > 0 and (not state.action_history or state.action_history[-1]["phase"] != state.phase):
        _new_street(S, bb)
    return S, sU0, street, events


def replay(state, bb):
    S, sU0, street, _ = replay_full(state, bb)
    return S, sU0, street
