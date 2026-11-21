"""Lower bound on the best achievable match win rate against the Maniac baseline.

The Maniac (holdem/opponents.py) ignores its cards: on every action it shoves
with probability 0.25, makes a pot-sized raise with probability 0.5, and
otherwise calls or checks. It never folds. Against such an opponent every
pot we continue in ends all-in, so a restricted best response only has to
choose, per hand class and stack, between giving up the blind and getting all
the chips in with the class's equity against a random hand.

The dynamic program below solves that restricted game exactly over
(hand number, our stack) under the season blind schedule. Restricting us to
fold-or-shove (and to giving up after a limp) can only lower our value, so
the result is a lower bound on what any strategy can reach against this
opponent. If it is under a target, the target needs a strategy that also
uses postflop play after a limp; if it is far under, the target is out of
reach for every algorithm.

Usage:
    python tools/match_ceiling.py [chipzen_bot/nlhe/data/preflop_equity.json]
"""

from __future__ import annotations

import json
import sys

import numpy as np

UNIT = 25
TOTAL = 20000
# 800 and 1000 are inferred from OFC replays (see holdem/engine.py); unobserved past hand 146.
SCHEDULE = [(20, 100), (40, 150), (60, 200), (80, 300), (100, 400), (120, 600), (140, 800)]
FINAL_BB = 1000
MAX_HANDS = 400


def big_blind(hand: int) -> int:
    for last, bb in SCHEDULE:
        if hand <= last:
            return bb
    return FINAL_BB


def class_equity_vs_random(path: str) -> tuple[np.ndarray, np.ndarray]:
    data = json.load(open(path, encoding="utf-8"))
    eq = np.array(data["eq"], dtype=float) / 10000.0
    w = np.array(data["w"], dtype=float)
    e = (eq * w).sum(axis=1) / w.sum(axis=1)
    # Class probability is proportional to its combo count: 6 pairs, 4 suited, 12 offsuit.
    combos = np.array([w[i].sum() for i in range(len(w))])
    p = combos / combos.sum()
    return e, p


def solve(e: np.ndarray, p: np.ndarray, we_are_sb_first: bool) -> float:
    n = TOTAL // UNIT
    stacks = np.arange(n + 1) * UNIT
    nxt = stacks / TOTAL  # value beyond MAX_HANDS: chip share
    for hand in range(MAX_HANDS, 0, -1):
        bb = big_blind(hand)
        sb = bb // 2
        we_sb = (hand % 2 == 1) == we_are_sb_first
        cur = np.zeros(n + 1)
        cur[n] = 1.0
        for i in range(1, n):
            s = stacks[i]
            opp = TOTAL - s
            m = min(s, opp)
            win = nxt[(s + m) // UNIT]
            lose = nxt[(s - m) // UNIT]
            allin = e * win + (1 - e) * lose  # value of getting it in, per class
            post = sb if we_sb else bb
            if s <= post:
                # Forced all-in for less than a blind.
                cur[i] = float(p @ allin)
                continue
            give_up = nxt[(s - post) // UNIT]
            if we_sb:
                v = np.maximum(allin, give_up)
            else:
                # Maniac acts first: shove 0.25, raise 0.5, limp 0.25. In every branch
                # we either get it all in or give up the big blind.
                v = np.maximum(allin, give_up)
            cur[i] = float(p @ v)
        nxt = cur
    return float(nxt[(TOTAL // 2) // UNIT])


def main(path: str) -> None:
    e, p = class_equity_vs_random(path)
    a = solve(e, p, True)
    b = solve(e, p, False)
    print(f"maniac, fold-or-shove best response: SB first {a:.4f}, BB first {b:.4f}, "
          f"seat-swapped mean {(a + b) / 2:.4f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "chipzen_bot/nlhe/data/preflop_equity.json")
