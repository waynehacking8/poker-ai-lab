"""Solve heads-up push/fold Nash equilibria over the 169 starting-hand classes.

Game (chips measured in big blinds, effective stack S, no antes):
  * the small blind (SB, button) either folds (-0.5) or shoves all-in;
  * the big blind (BB) facing a shove either folds (SB wins +1) or calls and
    the two hands run out.  SB's call payoff is S * (2 * equity - 1).

Both players hold one of 169 hand classes, dealt with card-removal weights, so
the game is a 169 x 169 matrix game with chance.  It is solved with CFR+ in
the same flavour as ``cfr/algorithms/cfr_plus.py``: regrets are floored at zero
after every update, the strategy comes from regret matching, and the average
strategy is weighted linearly by iteration.  The updates are vectorised with
numpy because the "tree" is just two 169-vectors.

Usage:
    python scripts/solve_pushfold.py            # writes chipzen_bot/nlhe/data/pushfold.json

Requires chipzen_bot/nlhe/data/preflop_equity.json (scripts/build_preflop_equity.py).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "chipzen_bot" / "nlhe" / "data"

STACKS = [x / 2 for x in range(4, 51)]  # 2.0 .. 25.0 BB in half-BB steps


def solve(M: np.ndarray, W: np.ndarray, S: float, iters: int = 4000):
    """CFR+ for the push/fold game.

    M[i, j]: SB equity of class i against BB class j.  W[i, j]: combo counts.
    Returns (push, call, exploitability) where push[i] is SB's shove probability
    and call[j] is BB's call probability, both averaged over iterations.
    """
    n = M.shape[0]
    J = W / W.sum()  # joint chance probability of (SB class, BB class)
    showdown = S * (2 * M - 1)  # SB payoff when the shove is called
    reg_push = np.zeros(n)
    reg_fold = np.zeros(n)
    reg_call = np.zeros(n)
    reg_bfold = np.zeros(n)
    sum_push = np.zeros(n)
    sum_call = np.zeros(n)
    wsum = 0.0
    for t in range(1, iters + 1):
        p = np.where(reg_push + reg_fold > 0, reg_push / np.maximum(reg_push + reg_fold, 1e-12), 0.5)
        c = np.where(reg_call + reg_bfold > 0, reg_call / np.maximum(reg_call + reg_bfold, 1e-12), 0.5)
        # SB: value of shoving vs folding, per SB class (reach-weighted by J)
        shove_val = (J * ((1 - c)[None, :] * 1.0 + c[None, :] * showdown)).sum(axis=1)
        fold_val = -0.5 * J.sum(axis=1)
        reg_push = np.maximum(reg_push + (shove_val - fold_val), 0.0)
        reg_fold = np.maximum(reg_fold + (fold_val - shove_val), 0.0)
        # BB: value of calling vs folding, per BB class, over SB shoves
        call_val = (J * p[:, None] * (-showdown)).sum(axis=0)
        bfold_val = (J * p[:, None] * (-1.0)).sum(axis=0)
        reg_call = np.maximum(reg_call + (call_val - bfold_val), 0.0)
        reg_bfold = np.maximum(reg_bfold + (bfold_val - call_val), 0.0)
        sum_push += t * p
        sum_call += t * c
        wsum += t
    push = sum_push / wsum
    call = sum_call / wsum
    return push, call, exploitability(M, W, S, push, call)


def exploitability(M, W, S, push, call) -> float:
    """Sum of both players' best-response gains, in big blinds per hand."""
    J = W / W.sum()
    showdown = S * (2 * M - 1)
    shove_val = (J * ((1 - call)[None, :] + call[None, :] * showdown)).sum(axis=1)
    fold_val = -0.5 * J.sum(axis=1)
    sb_br = np.maximum(shove_val, fold_val).sum()  # SB best response to call
    call_val = (J * push[:, None] * (-showdown)).sum(axis=0)
    bfold_val = (J * push[:, None] * (-1.0)).sum(axis=0)
    # BB best response to push, expressed as SB utility
    bb_br_for_sb = -np.maximum(call_val, bfold_val).sum() + 0.0
    # SB's own fold branch already counted inside sb_br; add SB's fixed-strategy
    # fold value so both terms are utilities of SB.
    sb_fold_part = (J * (1 - push)[:, None] * (-0.5)).sum()
    bb_br_for_sb += sb_fold_part
    return float(sb_br - bb_br_for_sb)


def load_matrices():
    d = json.loads((DATA / "preflop_equity.json").read_text())
    return np.array(d["eq"], dtype=float) / 10000.0, np.array(d["w"], dtype=float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=4000)
    args = ap.parse_args()
    M, W = load_matrices()
    out = {"stacks": STACKS, "push": [], "call": [], "iters": args.iters, "exploitability": []}
    t0 = time.time()
    for S in STACKS:
        push, call, expl = solve(M, W, S, args.iters)
        out["push"].append([int(round(x * 100)) for x in push])
        out["call"].append([int(round(x * 100)) for x in call])
        out["exploitability"].append(round(expl, 5))
        print(f"S={S:5.1f}  push {push @ W.sum(axis=1) / W.sum():.3f}  "
              f"call {call @ W.sum(axis=0) / W.sum():.3f}  expl {expl:.5f} bb/hand")
    (DATA / "pushfold.json").write_text(json.dumps(out, separators=(",", ":")), newline="\n")
    print(f"wrote pushfold.json in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
