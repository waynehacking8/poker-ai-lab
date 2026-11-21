"""Preflop knowledge: class-vs-class equities, class strength, Nash push/fold.

Data files (built offline by scripts/build_preflop_equity.py and
scripts/solve_pushfold.py) live in ``nlhe/data``.
"""

from __future__ import annotations

import json
import os

from .cards import CLASS_SIZE

_DATA = os.path.join(os.path.dirname(__file__), "data")


def _load(name):
    with open(os.path.join(_DATA, name), encoding="utf-8") as f:
        return json.load(f)


_eq = _load("preflop_equity.json")
EQ = [[v / 10000.0 for v in row] for row in _eq["eq"]]  # EQ[i][j]: class i vs class j
W = _eq["w"]  # compatible combo pairs

# Strength = all-in equity against a uniformly random hand, then converted to a
# combo-weighted percentile (1.0 = best hand, 0.0 = worst).
_vs_random = []
for _i in range(169):
    tot = sum(W[_i])
    _vs_random.append(sum(W[_i][j] * EQ[_i][j] for j in range(169)) / tot)
_order = sorted(range(169), key=lambda i: _vs_random[i])
PCT = [0.0] * 169
_acc = 0.0
_total = sum(CLASS_SIZE)
for _i in _order:
    PCT[_i] = (_acc + CLASS_SIZE[_i] / 2) / _total
    _acc += CLASS_SIZE[_i]
VS_RANDOM = _vs_random

_pf = _load("pushfold.json")
PF_STACKS = _pf["stacks"]


def top_range(width: float, soft: float = 0.06) -> list[float]:
    """Class weights for 'the strongest ``width`` of all hands', with soft edges."""
    cut = 1.0 - width
    out = []
    for i in range(169):
        d = cut - PCT[i]  # > 0 means below the cut
        out.append(1.0 if d <= 0 else max(0.0, 1.0 - d / soft) if soft > 0 else 0.0)
    return out


def band_range(lo: float, hi: float, soft: float = 0.06) -> list[float]:
    """Class weights for hands whose percentile lies in [lo, hi]."""
    out = []
    for i in range(169):
        p = PCT[i]
        d = max(lo - p, p - hi, 0.0)
        out.append(max(0.0, 1.0 - d / soft))
    return out


def _stack_index(stack_bb: float) -> int:
    best, bd = 0, 1e9
    for k, s in enumerate(PF_STACKS):
        d = abs(s - stack_bb)
        if d < bd:
            best, bd = k, d
    return best


def nash_push(stack_bb: float) -> list[float]:
    """Nash shove probability per class for the small blind (clamped to 2-25 BB)."""
    return [v / 100.0 for v in _pf["push"][_stack_index(stack_bb)]]


def nash_call(stack_bb: float) -> list[float]:
    """Nash call probability per class for the big blind facing a shove."""
    return [v / 100.0 for v in _pf["call"][_stack_index(stack_bb)]]


def mean_weight(weights: list[float]) -> float:
    """Fraction of all combos covered by a class weighting."""
    return sum(w * s for w, s in zip(weights, CLASS_SIZE)) / 1326.0


def equity_vs_range(cls: int, weights: list[float]) -> float:
    """All-in equity of class ``cls`` against a class-weighted range (card removal included)."""
    row, wrow = EQ[cls], W[cls]
    num = den = 0.0
    for j in range(169):
        wj = weights[j]
        if wj > 0.0:
            x = wj * wrow[j]
            num += x * row[j]
            den += x
    return num / den if den > 0 else 0.5


def blend(a: list[float], b: list[float], t: float) -> list[float]:
    """(1 - t) * a + t * b."""
    return [(1 - t) * x + t * y for x, y in zip(a, b)]
