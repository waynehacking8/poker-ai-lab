"""Diagnosis of the X2s search: run rl.eval_arena with one part of the search neutralized.

    python tools/x2s_ablate.py ABL -- <rl.eval_arena arguments, including --search>

ABL is "none" or a comma-separated subset of:
  f0      the opponent never folds to our raises (tests X1's fold estimates)
  exact   overrides only where the one-street EV is exact: on the river, or among fold, all-in, and a call
          that puts us all-in (tests the one-street horizon)
  crn     1,000 runouts drawn from one seed per decision for every action (tests Monte Carlo noise and the
          maximum over noisy estimates)
  flat    the opponent range is never updated: uniform over the live combos (tests the range model)
  soft    combos outside an action's band keep weight 0.5 instead of 0.1 (tests the range's confidence)
  oracle  the true opponent model in place of X1: the exact Bayesian range and fold probability of the
          StyleBot named by --opp (holdem/opponents.py STYLES); evidence from the first decision. Tests
          the decision procedure with model error removed.

The patches are applied before the arena's worker pool forks (Linux), so every worker inherits them.
"""

from __future__ import annotations

import os
import random
import sys
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rl  # noqa: F401,E402
import rl.bot  # noqa: E402
import rl.search as S  # noqa: E402
from holdem.opponents import STYLES, postflop_strength  # noqa: E402
from nlhe.cards import card_str  # noqa: E402
from rl import eval_arena  # noqa: E402
from rl.oppmodel import STREETS  # noqa: E402


class Oracle(S.Search):
    """The X2s search with the opponent's true StyleBot rules as its model."""

    BOT = None

    def _new_hand(self):
        super()._new_hand()
        self._lv = {}

    def has_evidence(self):
        return True

    def _levels(self, board):
        """The StyleBot postflop index (made-hand level, a draw counts as at least 1) of every combo."""
        key = tuple(board)
        if key not in self._lv:
            bs = [card_str(c) for c in board]
            out = np.zeros(len(S.COMBO_LIST), int)
            for k, (a, b) in enumerate(S.COMBO_LIST):
                if a not in board and b not in board:
                    lvl, draw = postflop_strength(SimpleNamespace(hole_cards=[card_str(a), card_str(b)], board=bs))
                    out[k] = max(lvl, 1) if draw else lvl
            self._lv[key] = out
        return self._lv[key]

    def _probs(self, phase, board, to_call, raised):
        """(fold, check or call, raise) probability of every combo for the bot in this spot."""
        B = self.BOT
        if phase == "preflop":
            p = S.PREFLOP_STRENGTH
            if raised:
                cont = (p >= B.face_p).astype(float) if to_call > 0 else np.ones_like(p)
                return 1 - cont, cont, 0 * p
            r = (p >= B.open_p).astype(float)
            c = (1 - r) * ((p >= B.play_p) | (to_call == 0))
            return 1 - r - c, c, r
        i = self._levels(board)
        if to_call == 0:
            b = np.array(B.bet)[i]
            return 0 * b, 1 - b, b
        rr, cont = np.array(B.rr)[i], np.array(B.cont)[i]
        return 1 - np.maximum(rr, cont), np.maximum(0, cont - rr), rr

    def _sync(self, history, hole, board):
        """As Search._sync, with the exact Bayesian range update of the bot's rules."""
        for j in range(self.n_done, len(history)):
            ev = history[j]
            kind, seat, amt, phase = ev["action"], ev["seat"], ev["amount"], ev["phase"]
            if self.tr is None:
                bb = next(e["amount"] for e in history if e["action"] == "post_big_blind")
                self.tr = S.HandTracker(self.stacks, bb)
            if STREETS.index(phase) != self.tr.street:
                self.tr.new_street(STREETS.index(phase))
            if kind.startswith("post_"):
                self.tr.apply(seat, kind, amt)
                continue
            raised = any(e["action"] == "raise" and e["phase"] == "preflop" for e in history[:j])
            to_call = self.tr.state(seat).to_call
            if kind in ("raise", "all_in"):
                kind, amt = "raise", amt - self.tr.street_committed[seat]
            self.tr.apply(seat, kind, amt)
            if seat == self.me or not hole:
                continue
            b = board[:S.BOARD_LEN[phase]]
            pf, pc, pr = self._probs(phase, b, to_call, raised)
            like = pr if kind == "raise" else pf if kind == "fold" else pc
            self.w *= np.maximum(like, 1e-3)  # floor: a spot the rules model inexactly (short stacks)
        self.n_done = len(history)

    def evs(self, state, mask, amt, hole, board):
        pot, c, me = float(state.pot), float(state.to_call), self.me
        bet_me = self.tr.street_committed[me]
        st = self.tr.state(me)
        w = self.w * ~np.isin(S.COMBOS, hole + board).any(axis=1)
        ids = np.flatnonzero(w > 0)
        q = S.equity(self.rnd, hole, board, ids, w[ids])
        pf, _, _ = self._probs(state.phase, board, 1, True)  # the bot facing our raise
        f = float((w * pf).sum() / w.sum())
        cont = w * (1 - pf)
        sel = np.flatnonzero(cont > 0)
        q_top = S.equity(self.rnd, hole, board, sel, cont[sel]) if len(sel) else q
        evs = {0: 0.0} if mask[0] else {}
        cc = min(c, st.rem)
        evs[1] = S.call_ev(pot - (c - cc), cc, q)
        self.fold_p = {}
        for a in range(2, 6):
            if mask[a]:
                r = amt[a] - bet_me
                evs[a] = S.raise_ev(pot, c, c + min(r - c, st.rem_opp), f, q_top)
                self.fold_p[a] = round(f, 3)
        return evs


def main():
    abl = set(sys.argv[1].split(",")) - {"none"}
    unknown = abl - {"f0", "exact", "crn", "flat", "soft", "oracle"}
    if unknown or sys.argv[2] != "--":
        sys.exit(__doc__)
    cls = S.Search
    if "oracle" in abl:
        Oracle.BOT = STYLES[sys.argv[sys.argv.index("--opp") + 1]]
        cls = rl.bot.Search = Oracle
    if "f0" in abl:
        S.Search.fold_prob = lambda self, st: 0.0
    if "exact" in abl:
        evs = cls.evs

        def exact_evs(self, state, mask, amt, hole, board):
            out = evs(self, state, mask, amt, hole, board)
            if state.phase == "river":
                return out
            keep = {0, 5} | ({1} if state.to_call >= self.tr.state(self.me).rem else set())
            return {a: v for a, v in out.items() if a in keep}

        cls.evs = exact_evs
    if "crn" in abl:
        S.RUNOUTS = 1000
        equity = S.equity
        S.equity = lambda rnd, hole, board, ids, wts: equity(
            random.Random(hash((tuple(hole), tuple(board)))), hole, board, ids, wts)
    if "flat" in abl:
        S.update_range = lambda *a: None
    if "soft" in abl:
        S.OUTSIDE = 0.5
    sys.argv = [sys.argv[0]] + sys.argv[3:]
    eval_arena.main()


if __name__ == "__main__":
    main()
