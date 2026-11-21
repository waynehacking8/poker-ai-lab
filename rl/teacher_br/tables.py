"""Equity buckets and bucket transition matrices from sampled trajectories.

Street 0 (preflop) buckets are the 169 starting-hand classes with their exact all-in equity
against a random hand.  Streets 1..3 (flop, turn, river) use ``k`` equal-width buckets of
equity e = win + tie/2 against a random hand with the board run out.  Equity is a martingale
along the board, so a bucket's mean equity equals the mean equity of what it turns into.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "chipzen_bot"))
from nlhe import preflop as pf  # noqa: E402

KMAX = 169


def build(traj_path: str, k: int):
    d = np.load(traj_path)
    cls, eq, size = d["cls"], d["eq"], d["size"]
    per = int(d["per_class"])
    wt = size[cls] / per  # sample weight ~ class combos
    wt = wt / wt.sum()
    n = len(cls)
    # per-street equity e and bucket index
    e = np.stack([eq[:, 0] + eq[:, 1] / 2, eq[:, 2] + eq[:, 3] / 2, eq[:, 4] + eq[:, 5] / 2])
    wn = np.stack([eq[:, 0], eq[:, 2], eq[:, 4]])
    tn = np.stack([eq[:, 1], eq[:, 3], eq[:, 5]])
    bidx = np.minimum((e * k).astype(int), k - 1)
    Ks = np.array([169, k, k, k])
    EQW = np.zeros((4, KMAX))
    EQT = np.zeros((4, KMAX))
    for c in range(169):
        EQW[0, c] = pf.VS_RANDOM[c]
    for s in range(3):
        for b in range(k):
            m = bidx[s] == b
            ww = wt[m].sum()
            if ww > 0:
                EQW[s + 1, b] = (wt[m] * wn[s][m]).sum() / ww
                EQT[s + 1, b] = (wt[m] * tn[s][m]).sum() / ww
            else:
                EQW[s + 1, b] = (b + 0.5) / k
    TR = np.zeros((3, KMAX, KMAX))
    for c in range(169):
        m = cls == c
        if m.any():
            for b in range(k):
                TR[0, c, b] = (bidx[0][m] == b).mean()
        else:
            TR[0, c, :k] = 1.0 / k
    for s in range(2):
        for b in range(k):
            m = bidx[s] == b
            ww = wt[m].sum()
            if ww > 0:
                for b2 in range(k):
                    TR[s + 1, b, b2] = wt[m & (bidx[s + 1] == b2)].sum() / ww
            else:
                TR[s + 1, b, b] = 1.0
    # class prior for the preflop value
    prior = np.zeros(KMAX)
    prior[:169] = size / size.sum()
    return dict(Ks=Ks, EQW=EQW, EQT=EQT, TR=TR, prior=prior, k=k, n=n)


if __name__ == "__main__":
    t = build(sys.argv[1], int(sys.argv[2]))
    np.savez(sys.argv[3], **t)
    print("saved", t["k"], t["n"])
