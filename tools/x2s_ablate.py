"""Diagnosis of the X2s search: run rl.eval_arena with one part of the search neutralized.

    python tools/x2s_ablate.py ABL -- <rl.eval_arena arguments, including --search>

ABL is "none" or a comma-separated subset of:
  f0     the opponent never folds to our raises (tests X1's fold estimates)
  exact  overrides only where the one-street EV is exact: on the river, or among fold, all-in, and a call
         that puts us all-in (tests the one-street horizon)
  crn    1,000 runouts drawn from one seed per decision for every action (tests Monte Carlo noise and the
         maximum over noisy estimates)

The patches are applied before the arena's worker pool forks (Linux), so every worker inherits them.
"""

from __future__ import annotations

import random
import sys

import rl  # noqa: F401
import rl.search as S
from rl import eval_arena


def main():
    abl = set(sys.argv[1].split(",")) - {"none"}
    unknown = abl - {"f0", "exact", "crn"}
    if unknown or sys.argv[2] != "--":
        sys.exit(__doc__)
    if "f0" in abl:
        S.Search.fold_prob = lambda self, st: 0.0
    if "exact" in abl:
        evs = S.Search.evs

        def exact_evs(self, state, mask, amt, hole, board):
            out = evs(self, state, mask, amt, hole, board)
            if state.phase == "river":
                return out
            keep = {0, 5} | ({1} if state.to_call >= self.tr.state(self.me).rem else set())
            return {a: v for a, v in out.items() if a in keep}

        S.Search.evs = exact_evs
    if "crn" in abl:
        S.RUNOUTS = 1000
        equity = S.equity
        S.equity = lambda rnd, hole, board, ids, wts: equity(
            random.Random(hash((tuple(hole), tuple(board)))), hole, board, ids, wts)
    sys.argv = [sys.argv[0]] + sys.argv[3:]
    eval_arena.main()


if __name__ == "__main__":
    main()
