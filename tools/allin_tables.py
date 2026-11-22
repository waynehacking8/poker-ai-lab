"""Match-value tables for answering a preflop shove (roadmap S0, the all-in fix).

Model: in each hand the opponent shoves preflop the top w of hands (nlhe.preflop.top_range), a share q_w
of all deals; the other hands leave the stacks unchanged. We answer a shove with call or fold. Backward
induction over (hand number, our stack) gives V_w(h, s) = P(we win the match) at the start of hand h with
stack s:

    V_w(h, s) = q_w * E_c[max(call_c, fold)] + (1 - q_w) * V_w(h + 1, s)
    call_c    = e_w[c] * V_w(h + 1, s + m) + (1 - e_w[c]) * V_w(h + 1, s - m),  m = min(s, total - s)
    fold      = V_w(h + 1, s - bb(h))

with e_w[c] the equity of class c against the range. Past MAX_HANDS the value is the chip share.
Against w = 1 (shove every hand) the model is exact up to the blind sizes. It fits only near-certain
shovers: for a tight range the opponent only ever gains in the model (we fold, it never pays a blind
back), and for a random part-time shover it ignores our edge in the other hands. rl/allin.py therefore
uses the tables only when the opponent's shove frequency is at least 0.7. rl/allin.py reads the tables at play time with the opponent's estimated w.

    python tools/allin_tables.py rl/models/allin_v.npz
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rl  # noqa: E402,F401  (chipzen_bot on sys.path)
from nlhe import preflop as pf  # noqa: E402
from nlhe.cards import CLASS_SIZE  # noqa: E402
from rl.features import bb_for  # noqa: E402

TOTAL = 20000
UNIT = 50
MAX_HANDS = 200
WIDTHS = (0.5, 0.75, 0.9, 1.0)


def range_weights(w):
    return [1.0] * 169 if w >= 1.0 else pf.top_range(w)


def class_equity(w):
    wt = range_weights(w)
    return np.array([pf.equity_vs_range(c, wt) for c in range(169)]), pf.mean_weight(wt)


def solve(w):
    e, q = class_equity(w)
    p = np.array(CLASS_SIZE, dtype=float) / 1326.0
    n = TOTAL // UNIT
    s = np.arange(n + 1) * UNIT
    m = np.minimum(s, TOTAL - s)
    nxt = s / TOTAL
    out = np.zeros((MAX_HANDS + 2, n + 1), dtype=np.float32)
    out[MAX_HANDS + 1] = nxt
    for h in range(MAX_HANDS, 0, -1):
        bb = bb_for(h)
        win = nxt[(s + m) // UNIT]
        lose = nxt[(s - m) // UNIT]
        call = np.outer(e, win) + np.outer(1 - e, lose)          # (169, n + 1)
        fold = nxt[np.maximum(s - bb, 0) // UNIT]
        best = np.maximum(call, fold[None, :])
        cur = q * (p @ best) + (1 - q) * nxt
        cur[0], cur[n] = 0.0, 1.0
        out[h] = cur
        nxt = cur
    return out, e, q


def main(path):
    vs, es, qs = [], [], []
    for w in WIDTHS:
        v, e, q = solve(w)
        vs.append(v)
        es.append(e)
        qs.append(q)
        print(f"w {w:.2f}  shove share {q:.3f}  V(hand 1, even stacks) {v[1][TOTAL // 2 // UNIT]:.4f}")
    np.savez_compressed(path, v=np.array(vs, dtype=np.float32), e=np.array(es, dtype=np.float32),
                        widths=np.array(WIDTHS), unit=UNIT, total=TOTAL, max_hands=MAX_HANDS)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "rl/models/allin_v.npz")
