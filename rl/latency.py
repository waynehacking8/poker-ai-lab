"""Decision latency of the deployable bot (run under taskset -c 0 for one core)."""

from __future__ import annotations

import argparse
import statistics
import time

import rl  # noqa: F401
from holdem.engine import MatchConfig, play_match
from holdem.opponents import make_baseline
from rl.bot import RLBot


class Timed(RLBot):
    times = []

    def decide(self, state):
        t = time.perf_counter()
        a = super().decide(state)
        Timed.times.append((time.perf_counter() - t) * 1000)
        return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--matches", type=int, default=40)
    args = ap.parse_args()
    for k in range(args.matches):
        bots = [Timed(seed=k, model=args.model), make_baseline("lag", k)]
        play_match(bots, k + 1, MatchConfig())
    t = sorted(Timed.times)
    print({"decisions": len(t), "mean_ms": round(statistics.mean(t), 2),
           "p95_ms": round(t[int(len(t) * 0.95)], 2), "p99_ms": round(t[int(len(t) * 0.99)], 2),
           "max_ms": round(t[-1], 2)})


if __name__ == "__main__":
    main()
