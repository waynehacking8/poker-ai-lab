"""Hand-strength feature shared by fitting and playing the clones.

Strength is a percentile in [0, 1] (1 = best): the combo-weighted all-in equity
percentile preflop (``nlhe.preflop.PCT``) and the board-relative percentile with a
draw bonus postflop (``nlhe.ranges.StreetTable``).  It is cut into ``NB`` buckets.
Using the bot's own strength tables keeps the clones and the bots they face on one
yardstick.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from nlhe import preflop as pf  # noqa: E402
from nlhe.cards import hand_class  # noqa: E402
from nlhe.ranges import COMBOS, StreetTable  # noqa: E402

EDGES = (0.25, 0.45, 0.60, 0.72, 0.82, 0.90, 0.96)
NB = len(EDGES) + 1
NCOMBO = len(COMBOS)
COMBO_INDEX = {c: i for i, c in enumerate(COMBOS)}


def bucket_of(p: float) -> int:
    b = 0
    for e in EDGES:
        if p >= e:
            b += 1
    return b


def combo_index(c1: int, c2: int) -> int:
    return COMBO_INDEX[(c1, c2) if c1 < c2 else (c2, c1)]


# preflop bucket per combo (static)
PRE_BUCKETS = np.array([bucket_of(pf.PCT[hand_class(a, b)]) for a, b in COMBOS], dtype=np.int8)


@lru_cache(maxsize=4096)
def board_buckets(board: tuple) -> np.ndarray:
    """Bucket of every combo on a 3, 4 or 5 card board; -1 for combos the board blocks."""
    t = StreetTable(board)
    out = np.full(NCOMBO, -1, dtype=np.int8)
    for i, s in enumerate(t.score):
        if s is not None:
            out[i] = bucket_of(t.pct[i])
    return out


def bucket_for(hole, board) -> int:
    """Bucket of a concrete holding (ints) on the given board (possibly empty)."""
    if not board:
        return int(PRE_BUCKETS[combo_index(hole[0], hole[1])])
    return int(board_buckets(tuple(sorted(board)))[combo_index(hole[0], hole[1])])
