"""Per-hand EV diagnostic: play independent hands at a fixed stack depth.

Unlike a match (winner take all, high variance), this measures the bot's average
result in big blinds per hand against a baseline at a chosen depth, which is how
leaks by stack depth are found.

    python -m holdem.cash --opp lag --depth 100 --hands 4000 --workers 10
"""

from __future__ import annotations

import argparse
import random
import statistics
from multiprocessing import Pool

from .engine import Hand
from .opponents import make_baseline


RESET = 30
TRACE = None


def _chunk(job):
    opp_name, depth, seed, n = job
    from bot import HoldemBot

    bb = 100
    out = []
    for k in range(n):
        if k % RESET == 0:  # fresh model every few hands, like a new match
            hero = HoldemBot(seed=seed * 7 + k)
            opp = make_baseline(opp_name, seed + k)
        rng = random.Random(seed * 100003 + k)
        deck = list(range(52))
        rng.shuffle(deck)
        for hero_seat in (0, 1):
            bots = [None, None]
            bots[hero_seat] = hero
            bots[1 - hero_seat] = opp
            hero.brain.my_seat = hero_seat
            hand = Hand(bots, [depth * bb, depth * bb], k % 2, k + 1, bb // 2, bb, deck)
            hand.play()
            out.append((hand.stack[hero_seat] - depth * bb) / bb)
            if TRACE is not None:
                TRACE.append((hero_seat == hand.dealer, hand.history, out[-1]))
    return out


def run(opp, depth, hands, workers, seed=1):
    per = max(1, hands // (2 * workers))
    jobs = [(opp, depth, seed * 1000 + w, per) for w in range(workers)]
    with Pool(workers) as p:
        res = [x for r in p.map(_chunk, jobs) for x in r]
    mean = statistics.mean(res)
    se = statistics.stdev(res) / len(res) ** 0.5
    return mean, se, len(res)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--opp", required=True)
    ap.add_argument("--depth", type=int, default=100)
    ap.add_argument("--hands", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    m, se, n = run(a.opp, a.depth, a.hands, a.workers)
    print(f"{a.opp} depth={a.depth}bb hands={n}: {m:+.2f} bb/hand (se {se:.2f})")
