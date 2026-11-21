"""Measure the bot's decide() latency over real simulated matches.

    taskset -c 0 python scripts/holdem_latency.py --matches 40

Reports wall and CPU milliseconds per decision (p50, p99, max), overall and per street.
Run it pinned to one core; the hosted container has 0.5 vCPU, so scale the numbers up
(about 2x for the core share, more if the host core is slower than this one).
"""

from __future__ import annotations

import argparse
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import holdem  # noqa: E402,F401
from bot import HoldemBot  # noqa: E402
from holdem.engine import play_match  # noqa: E402
from holdem.opponents import make_baseline  # noqa: E402

OPPONENTS = ("lag", "station_raiser", "reference", "nit", "maniac", "station", "random")


class Timed:
    def __init__(self, bot, rows):
        self.bot, self.rows = bot, rows

    def decide(self, state):
        w0, c0 = time.perf_counter(), time.process_time()
        act = self.bot.decide(state)
        self.rows.append((state.phase, (time.perf_counter() - w0) * 1e3,
                          (time.process_time() - c0) * 1e3))
        return act

    def __getattr__(self, name):
        return getattr(self.bot, name)


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matches", type=int, default=40)
    args = ap.parse_args()
    rows: list = []
    for k in range(args.matches):
        opp = OPPONENTS[k % len(OPPONENTS)]
        hero = Timed(HoldemBot(seed=k), rows)
        other = make_baseline(opp, k)
        bots = [hero, other] if k % 2 == 0 else [other, hero]
        play_match(bots, k)
    print(f"decisions: {len(rows)}")
    for label, sel in [("all", rows)] + [(p, [r for r in rows if r[0] == p])
                                         for p in ("preflop", "flop", "turn", "river")]:
        if not sel:
            continue
        wall = [r[1] for r in sel]
        cpu = [r[2] for r in sel]
        print(f"{label:8s} n={len(sel):6d}  wall ms p50={statistics.median(wall):6.1f} "
              f"p99={pct(wall, .99):6.1f} max={max(wall):6.1f}   "
              f"cpu ms p50={statistics.median(cpu):6.1f} p99={pct(cpu, .99):6.1f} max={max(cpu):6.1f}")


if __name__ == "__main__":
    main()
