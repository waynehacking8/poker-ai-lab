"""The fast evaluator is checked against an independent, deliberately slow oracle."""

from __future__ import annotations

import itertools
import random
from collections import Counter

import pytest

from nlhe.cards import card_from_str as c
from nlhe.evaluator import category, evaluate


def oracle5(cards):
    """Rank of exactly five cards as a comparable tuple (written from the rules)."""
    ranks = sorted((x >> 2 for x in cards), reverse=True)
    suits = {x & 3 for x in cards}
    counts = Counter(ranks)
    groups = sorted(counts.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    shape = tuple(n for _, n in groups)
    ordered = [r for r, _ in groups]
    flush = len(suits) == 1
    uniq = sorted(set(ranks), reverse=True)
    straight_high = None
    if len(uniq) == 5:
        if uniq[0] - uniq[4] == 4:
            straight_high = uniq[0]
        elif uniq == [12, 3, 2, 1, 0]:
            straight_high = 3
    if flush and straight_high is not None:
        return (8, straight_high)
    if shape == (4, 1):
        return (7, *ordered)
    if shape == (3, 2):
        return (6, *ordered)
    if flush:
        return (5, *ranks)
    if straight_high is not None:
        return (4, straight_high)
    if shape == (3, 1, 1):
        return (3, *ordered)
    if shape == (2, 2, 1):
        return (2, *ordered)
    if shape == (2, 1, 1, 1):
        return (1, *ordered)
    return (0, *ranks)


def oracle7(cards):
    return max(oracle5(h) for h in itertools.combinations(cards, 5))


def test_known_hands():
    def ev(s):
        return evaluate([c(x) for x in s.split()])

    royal = ev("Ah Kh Qh Jh Th 2c 3d")
    wheel_flush = ev("Ah 2h 3h 4h 5h 9c 9d")
    quads = ev("9c 9d 9h 9s Ah 2c 3d")
    boat = ev("9c 9d 9h Ks Kh 2c 3d")
    flush = ev("Ah 3h 5h 9h Jh 2c 3d")
    wheel = ev("Ah 2c 3d 4s 5h 9c Kd")
    assert category(royal) == 8 and category(wheel_flush) == 8
    assert royal > wheel_flush > quads > boat > flush > wheel
    assert category(wheel) == 4
    # the wheel is the lowest straight, a six-high straight beats it
    assert ev("2c 3d 4s 5h 6h 9c Kd") > wheel
    # kicker decides, and a board-played hand ties
    assert ev("Ah Ad Kc 7s 4h 3c 2d") > ev("Ah Ad Qc 7s 4h 3c 2d")
    assert ev("Ah Kh Qh Jh Th 2c 2d") == ev("Ah Kh Qh Jh Th 3c 3d")
    # two trips make a full house, the higher trips lead
    assert ev("Ah Ad Ac Kh Kd Kc 2s") > ev("Ah Ad Ac Qh Qd Qc 2s")


def test_random_7card_matches_oracle():
    rng = random.Random(7)
    for _ in range(4000):
        a = rng.sample(range(52), 7)
        b = rng.sample(range(52), 7)
        fa, fb = evaluate(a), evaluate(b)
        oa, ob = oracle7(a), oracle7(b)
        assert (fa > fb) == (oa > ob) and (fa == fb) == (oa == ob), (a, b)
        assert category(fa) == oa[0]


def test_board_biased_hands_match_oracle():
    """Random hands almost never hit straights and flushes: bias the deals."""
    rng = random.Random(11)
    for _ in range(3000):
        suit = rng.randrange(4)
        base = rng.randrange(0, 8)
        pool = [r * 4 + suit for r in range(base, base + 6)]
        hand = rng.sample(pool, 4) + rng.sample(range(52), 3)
        if len(set(hand)) < 7:
            continue
        other = rng.sample(range(52), 7)
        fa, fb = evaluate(hand), evaluate(other)
        oa, ob = oracle7(hand), oracle7(other)
        assert category(fa) == oa[0]
        assert (fa > fb) == (oa > ob) and (fa == fb) == (oa == ob)


@pytest.mark.slow
def test_all_five_card_hands_category_counts():
    expected = {8: 40, 7: 624, 6: 3744, 5: 5108, 4: 10200, 3: 54912, 2: 123552,
                1: 1098240, 0: 1302540}
    got = Counter(category(evaluate(h)) for h in itertools.combinations(range(52), 5))
    assert dict(got) == expected
