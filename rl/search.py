"""Search under the opponent model (roadmap X2s): the smallest end-to-end loop.

At each of our decisions, a one-street chip EV per legal action of the policy's action table, against a
range of opponent hole cards that X1 (rl/oppmodel.py) updates after every opponent action. The argmax plays
only when X1 has evidence and the EV beats the policy's own choice by more than MARGIN of the pot.

    search = Search(OppModel.load(OPPMODEL), seed)
    search.start_match(opponent_name, my_seat, starting_stack)
    a = search.decide(state, policy_action, mask, amt)   # every decision; returns an action index 0..5
    search.finish_hand(result)                            # on every round_result

The one-line JSON log of each search decision goes to the file named by the env var RL_SEARCH_LOG.
"""

from __future__ import annotations

import copy
import itertools
import json
import os
import random

import numpy as np

from nlhe.cards import card_str, cards_from, hand_class
from nlhe.evaluator import evaluate
from nlhe.preflop import PCT
from rl.oppmodel import FOLD, NCLS, STREETS, HandTracker, classify

OPPMODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "oppmodel.npz")
LOG_ENV = "RL_SEARCH_LOG"
OUTSIDE = 0.1  # weight of a combo outside the band an action falls in (bluffs and model error)
RUNOUTS = 200
MARGIN = 0.05  # of the pot
MIN_OBS = 10  # opponent actions in this match when the opponent has no named profile
K = 2 * np.log(0.912 / 0.088)  # edge curvature: v4's league field win rate, 91.2% (E1), as gambler's ruin

COMBO_LIST = list(itertools.combinations(range(52), 2))
COMBOS = np.array(COMBO_LIST)
PREFLOP_STRENGTH = np.array([PCT[hand_class(a, b)] for a, b in COMBO_LIST])
BOARD_LEN = {"preflop": 0, "flop": 3, "turn": 4, "river": 5}


# ---------------------------------------------------------------- range

def strength(board):
    """Strength of every combo on this board: preflop percentile, postflop evaluator score (-1 for a combo
    that shares a card with the board: it cannot occur, and five of a rank crashes the evaluator)."""
    if not board:
        return PREFLOP_STRENGTH
    return np.array([-1 if a in board or b in board else evaluate([a, b] + board) for a, b in COMBO_LIST])


def ranked(w, s, dead):
    """The live combos from weakest to strongest, and each one's quantile in the range's weight."""
    live = np.flatnonzero(~np.isin(COMBOS, dead).any(axis=1))
    order = live[np.argsort(s[live], kind="stable")]
    c = np.cumsum(w[order])
    return order, (c - w[order] / 2) / c[-1]


def update_range(w, p, cls, s, dead):
    """After an opponent action of class `cls` with X1 probabilities `p`: the band of the range that action
    falls in (classes from the bottom: fold, call, raise up to the pot, above the pot, all-in) keeps its
    weight, every other combo is multiplied by OUTSIDE."""
    order, u = ranked(w, s, dead)
    lo = p[:cls].sum()
    hi = 2.0 if cls == NCLS - 1 else lo + p[cls]
    w[order[(u < lo) | (u >= hi)]] *= OUTSIDE


# ---------------------------------------------------------------- EV

def equity(rnd, hole, board, ids, wts):
    """Our win share (ties half) over RUNOUTS runouts against hands drawn from combos `ids` by weight."""
    deck = [c for c in range(52) if c not in hole and c not in board]
    won = 0.0
    for k in rnd.choices(ids, wts, k=RUNOUTS):
        a, b = COMBO_LIST[k]
        run = board + rnd.sample([c for c in deck if c != a and c != b], 5 - len(board))
        mine, theirs = evaluate(hole + run), evaluate([a, b] + run)
        won += 1.0 if mine > theirs else 0.5 if mine == theirs else 0.0
    return won / RUNOUTS


def win_prob(x, T):
    """Match-win probability holding x of the T chips in play, for a player with an edge: gambler's ruin
    with curvature K (K -> 0 is the chip share x / T). Chip EV ignores the edge and takes coin flips that
    a stronger player should decline (14.16: with the true opponent model, chip EV lost 59% and 81% where
    the policy won 96% and 95%; this utility won 100% and 98%)."""
    return np.expm1(-K * x / T) / np.expm1(-K)


def in_chips(u, rem, T):
    """A match-win probability u, relative to folding now with `rem` chips behind, in chips at that stack."""
    return (u - win_prob(rem, T)) / (K / T * np.exp(-K * rem / T) / -np.expm1(-K))


def call_ev(pot, c, q, rem, T):
    """Check or call for `c` (0 when nothing is to call), equity q."""
    return in_chips(q * win_prob(rem + pot, T) + (1 - q) * win_prob(rem - c, T), rem, T)


def raise_ev(pot, c, r, f, q, rem, T):
    """Bet or raise putting in `r` chips (r > c) when `c` is to call: the opponent folds with probability f
    (we win the pot), otherwise calls and we win with equity q (against the part of the range that calls)."""
    won, lost = win_prob(rem + pot + r - c, T), win_prob(rem - r, T)
    return in_chips(f * win_prob(rem + pot, T) + (1 - f) * (q * won + (1 - q) * lost), rem, T)


# ---------------------------------------------------------------- the search

class Search:
    def __init__(self, model, seed=None):
        self.model = model
        self.rnd = random.Random(seed)
        self.n_obs = 0
        self.fold_p = {}  # X1's fold probability per raise at the last search decision (for the log)
        self.start_match(None, 0, 0)

    def start_match(self, name, me, stack):
        self.model.start_match(name)
        self.me = int(me)
        self.stacks = {0: stack, 1: stack}  # hand-start stacks, from the previous round_result
        self.n_obs = 0
        self._new_hand()

    def _new_hand(self):
        self.tr = None
        self.n_done = 0
        self.w = np.ones(len(COMBO_LIST))
        self._strength = {}

    def _board_strength(self, board):
        key = tuple(board)
        if key not in self._strength:
            self._strength[key] = strength(board)
        return self._strength[key]

    def _sync(self, history, hole, board):
        """Apply the events not seen yet: X1 observes each opponent action, and (when we know our hole cards)
        the range is updated. Raise amounts in the history are raise-to totals for the street; HandTracker
        wants the chips added."""
        for ev in history[self.n_done:]:
            kind, seat, amt, phase = ev["action"], ev["seat"], ev["amount"], ev["phase"]
            if self.tr is None:
                bb = next(e["amount"] for e in history if e["action"] == "post_big_blind")
                self.tr = HandTracker(self.stacks, bb)
            if STREETS.index(phase) != self.tr.street:
                self.tr.new_street(STREETS.index(phase))
            if kind.startswith("post_"):
                self.tr.apply(seat, kind, amt)
                continue
            if kind in ("raise", "all_in"):
                kind, amt = "raise", amt - self.tr.street_committed[seat]
            before = self.tr.state(seat)
            cls = self.tr.apply(seat, kind, amt)
            if seat == self.me:
                continue
            p = self.model.predict(before)
            self.model.observe(before, cls)
            self.n_obs += 1
            if hole:
                b = board[:BOARD_LEN[phase]]
                update_range(self.w, p, cls, self._board_strength(b), hole + b)
        self.n_done = len(history)

    def finish_hand(self, result):
        """round_result: observe the actions after our last decision, and take the next hand's stacks."""
        self._sync(result.get("action_history") or [], None, None)
        st = result.get("stacks")
        if st and len(st) == 2:
            self.stacks = {0: st[0], 1: st[1]}
        self._new_hand()

    def has_evidence(self):
        return self.model.i is not None or self.n_obs >= MIN_OBS

    def fold_prob(self, st):
        """X1's probability that the opponent folds in public state `st`."""
        return float(self.model.predict(st)[FOLD])

    def evs(self, state, mask, amt, hole, board):
        """{action index: EV in chips} for each legal action."""
        pot, c, me = float(state.pot), float(state.to_call), self.me
        bet_me = self.tr.street_committed[me]
        rem, rem_opp = float(state.your_stack), float(min(state.opponent_stacks))
        T = rem + rem_opp + pot
        order, u = ranked(self.w, self._board_strength(board), hole + board)

        def eq(lo):
            sel = order[u >= lo]
            return equity(self.rnd, hole, board, sel, self.w[sel]) if len(sel) else None

        q = eq(0.0)
        evs = {}
        if mask[0]:
            evs[0] = 0.0
        cc = min(c, rem)  # a call for more than our stack gets the rest of the bet back
        evs[1] = call_ev(pot - (c - cc), cc, q, rem, T)
        self.fold_p = {}
        for a in range(2, 6):
            if not mask[a]:
                continue
            r = amt[a] - bet_me
            after = copy.deepcopy(self.tr)
            after.apply(me, "raise", r)
            f = self.fold_prob(after.state(1 - me))
            q_top = eq(f)
            r_eff = c + min(r - c, rem_opp)  # the opponent can match at most its stack
            evs[a] = raise_ev(pot, c, r_eff, f, q if q_top is None else q_top, rem, T)
            self.fold_p[a] = round(f, 3)
        return evs

    def decide(self, state, policy_a, mask, amt):
        """The action index to play: the policy's, unless the search overrides it."""
        hole, board = cards_from(state.hole_cards), cards_from(state.board)
        self.me = state.your_seat
        self._sync(state.action_history, hole, board)
        if STREETS.index(state.phase) != self.tr.street:
            self.tr.new_street(STREETS.index(state.phase))
        if not self.has_evidence():
            return policy_a
        evs = self.evs(state, mask, amt, hole, board)
        best = max(evs, key=evs.get)
        override = policy_a in evs and evs[best] - evs[policy_a] > MARGIN * state.pot
        self._log(state, hole, board, policy_a, best, evs, override)
        return best if override else policy_a

    def _log(self, state, hole, board, policy_a, best, evs, override):
        path = os.environ.get(LOG_ENV)
        if not path:
            return
        row = {"hand": state.hand_number, "phase": state.phase, "pot": state.pot, "to_call": state.to_call,
               "stack": state.your_stack, "hole": [card_str(c) for c in hole], "board": [card_str(c) for c in board],
               "policy": policy_a, "search": best,
               "ev": {str(a): round(v, 1) for a, v in evs.items()},
               "fold": {str(a): f for a, f in self.fold_p.items()}, "override": bool(override)}
        with open(path, "a") as fh:
            fh.write(json.dumps(row) + "\n")
