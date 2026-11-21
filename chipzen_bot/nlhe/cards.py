"""Card helpers.

A card is an int ``rank * 4 + suit`` with rank 0..12 (deuce..ace) and suit 0..3
(h, d, c, s).  Ints keep the hot loops (equity simulation) free of object
allocation; the SDK ``Card`` objects are converted once per decision.
"""

from __future__ import annotations

RANKS = "23456789TJQKA"
SUITS = "hdcs"
RANK_INDEX = {r: i for i, r in enumerate(RANKS)}
SUIT_INDEX = {s: i for i, s in enumerate(SUITS)}
DECK = tuple(range(52))


def card_from_str(s: str) -> int:
    """'Ah' -> int.  Accepts any case for the suit and rank."""
    return RANK_INDEX[s[0].upper()] * 4 + SUIT_INDEX[s[1].lower()]


def card_from_obj(c) -> int:
    """Convert an SDK ``Card`` (has ``.rank`` and ``.suit``) or a string."""
    if isinstance(c, str):
        return card_from_str(c)
    return RANK_INDEX[c.rank] * 4 + SUIT_INDEX[c.suit]


def card_str(c: int) -> str:
    return RANKS[c >> 2] + SUITS[c & 3]


def cards_from(seq) -> list[int]:
    return [card_from_obj(c) for c in seq]


def hand_class(c1: int, c2: int) -> int:
    """Index 0..168 of the starting-hand class of two cards.

    Layout: pairs on the diagonal, suited above it, offsuit below it, in a
    13 x 13 grid ``row = high rank, col = low rank`` flattened as ``row*13+col``
    when suited or paired, ``col*13+row`` when offsuit.
    """
    r1, r2 = c1 >> 2, c2 >> 2
    if r1 < r2:
        r1, r2 = r2, r1
    if r1 == r2 or (c1 & 3) == (c2 & 3):
        return r1 * 13 + r2
    return r2 * 13 + r1


def class_name(idx: int) -> str:
    """Human readable name such as 'AKs', 'T9o', 'QQ'."""
    a, b = divmod(idx, 13)
    if a == b:
        return RANKS[a] * 2
    if a > b:
        return RANKS[a] + RANKS[b] + "s"
    return RANKS[b] + RANKS[a] + "o"


def class_combos(idx: int) -> list[tuple[int, int]]:
    """All concrete two-card combos of a hand class."""
    a, b = divmod(idx, 13)
    out = []
    if a == b:
        for s1 in range(4):
            for s2 in range(s1 + 1, 4):
                out.append((a * 4 + s1, a * 4 + s2))
    elif a > b:
        for s in range(4):
            out.append((a * 4 + s, b * 4 + s))
    else:
        hi, lo = b, a
        for s1 in range(4):
            for s2 in range(4):
                if s1 != s2:
                    out.append((hi * 4 + s1, lo * 4 + s2))
    return out


CLASS_COMBOS = [class_combos(i) for i in range(169)]
CLASS_SIZE = [len(c) for c in CLASS_COMBOS]
