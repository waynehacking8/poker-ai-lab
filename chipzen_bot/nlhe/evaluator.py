"""Fast pure-Python 5/6/7-card hand evaluator.

``evaluate(cards)`` returns an int; a larger int is a stronger hand and equal
ints tie.  The value is ``category << 20 | kickers`` where the kickers are five
4-bit rank nibbles.  Categories: 0 high card, 1 pair, 2 two pair, 3 trips,
4 straight, 5 flush, 6 full house, 7 quads, 8 straight flush.

The approach is a single pass over rank counts plus two 8192-entry lookup
tables (straight detection and the top five ranks of a flush mask), which is
about as fast as pure Python gets without a giant perfect-hash table.
"""

from __future__ import annotations

CATEGORY_NAMES = (
    "High Card", "Pair", "Two Pair", "Three of a Kind", "Straight",
    "Flush", "Full House", "Four of a Kind", "Straight Flush",
)


def _build_tables():
    straight = [-1] * 8192
    top5 = [0] * 8192
    for mask in range(8192):
        for high in range(12, 3, -1):
            window = 0b11111 << (high - 4)
            if mask & window == window:
                straight[mask] = high
                break
        else:
            if mask & 0b1000000001111 == 0b1000000001111:  # A-2-3-4-5
                straight[mask] = 3
        if bin(mask).count("1") >= 5:
            ranks = [r for r in range(12, -1, -1) if mask >> r & 1][:5]
            v = 0
            for r in ranks:
                v = (v << 4) | r
            top5[mask] = v
    return straight, top5


_STRAIGHT, _TOP5 = _build_tables()


def _pack(ranks):
    v = 0
    for r in ranks:
        v = (v << 4) | r
    # left-align to five nibbles so shorter kicker lists compare correctly
    return v << (4 * (5 - len(ranks)))


def evaluate(cards) -> int:
    """Strength of the best 5-card hand among 5..7 cards (ints, see cards.py)."""
    cnt = [0] * 13
    sm = [0, 0, 0, 0]
    sc = [0, 0, 0, 0]
    for c in cards:
        r = c >> 2
        s = c & 3
        cnt[r] += 1
        sm[s] |= 1 << r
        sc[s] += 1
    flush_mask = 0
    for s in range(4):
        if sc[s] >= 5:
            flush_mask = sm[s]
            break
    if flush_mask:
        sf = _STRAIGHT[flush_mask]
        if sf >= 0:
            return (8 << 20) | (sf << 16)
    quad = -1
    trips = []
    pairs = []
    singles = []
    rank_mask = 0
    for r in range(12, -1, -1):
        c = cnt[r]
        if c:
            rank_mask |= 1 << r
            if c == 1:
                singles.append(r)
            elif c == 2:
                pairs.append(r)
            elif c == 3:
                trips.append(r)
            else:
                quad = r
    if quad >= 0:
        rest = [r for r in range(12, -1, -1) if cnt[r] and r != quad]
        return (7 << 20) | (quad << 16) | (rest[0] << 12)
    if trips and (len(trips) > 1 or pairs):
        pair = trips[1] if len(trips) > 1 else -1
        if pairs and pairs[0] > pair:
            pair = pairs[0]
        return (6 << 20) | (trips[0] << 16) | (pair << 12)
    if flush_mask:
        return (5 << 20) | _TOP5[flush_mask]
    st = _STRAIGHT[rank_mask]
    if st >= 0:
        return (4 << 20) | (st << 16)
    if trips:
        return (3 << 20) | _pack([trips[0]] + singles[:2])
    if len(pairs) >= 2:
        kick = singles[0] if singles else -1
        if len(pairs) == 3 and pairs[2] > kick:
            kick = pairs[2]
        return (2 << 20) | _pack([pairs[0], pairs[1], kick])
    if pairs:
        return (1 << 20) | _pack([pairs[0]] + singles[:3])
    return _pack(singles[:5])


def category(score: int) -> int:
    return score >> 20


def category_name(score: int) -> str:
    return CATEGORY_NAMES[score >> 20]
