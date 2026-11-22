"""Run many matches of the Hold'em bot against a baseline and report win rates.

Matches are played in duplicate pairs: the same seed deals the same cards, and
the bots swap seats in the second match of each pair, so card luck cancels.

    python -m holdem.arena --opp station --matches 200 --seed 1 --workers 10
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from multiprocessing import Pool

from .engine import MatchConfig, play_match
from .opponents import BASELINES, make_baseline


def wilson(wins: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    p = wins / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return centre - half, centre + half


def _make_hero(seed):
    from bot import HoldemBot

    return HoldemBot(seed=seed)


def run_one(job):
    opp_name, pair_seed, hero_seat, hero_factory = job
    hero = (hero_factory or _make_hero)(pair_seed * 7 + hero_seat)
    opp = make_baseline(opp_name, pair_seed * 13 + hero_seat) if isinstance(opp_name, str) else opp_name()
    if hasattr(opp, "set_seed"):
        opp.set_seed(pair_seed * 13 + hero_seat)
    bots = [None, None]
    bots[hero_seat] = hero
    bots[1 - hero_seat] = opp
    res = play_match(bots, pair_seed, MatchConfig())
    return {"seed": pair_seed, "hero_seat": hero_seat, "hands": res.hands,
            "won": res.winner == hero_seat, "tie": res.winner is None,
            "capped": res.capped, "stacks": res.stacks}


def run_arena(opp: str, matches: int, seed: int = 1, workers: int = 8, hero_factory=None, rows_out=None):
    """Aggregate result of ``matches`` matches; per-match rows are appended to ``rows_out`` when given."""
    jobs = []
    for k in range(matches // 2):
        for seat in (0, 1):
            jobs.append((opp, seed * 100000 + k, seat, hero_factory))
    t0 = time.time()
    if workers <= 1:
        rows = [run_one(j) for j in jobs]
    else:
        with Pool(workers) as pool:
            rows = pool.map(run_one, jobs, chunksize=2)
    if rows_out is not None:
        rows_out.extend(rows)
    n = len(rows)
    wins = sum(r["won"] for r in rows)
    lo, hi = wilson(wins, n)
    won_hands = [r["hands"] for r in rows if r["won"]]
    return {
        "opponent": opp, "matches": n, "wins": wins, "win_rate": wins / n,
        "ci95": [round(lo, 3), round(hi, 3)],
        "mean_hands_all": round(statistics.mean(r["hands"] for r in rows), 1),
        "mean_hands_per_win": round(statistics.mean(won_hands), 1) if won_hands else None,
        "ties_or_caps": sum(r["capped"] for r in rows), "seed": seed,
        "seconds": round(time.time() - t0, 1),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--opp", default="all", help="baseline name or 'all'")
    ap.add_argument("--matches", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args(argv)
    names = list(BASELINES) if args.opp == "all" else [args.opp]
    for name in names:
        out = run_arena(name, args.matches, args.seed, args.workers)
        print(json.dumps(out), flush=True)


if __name__ == "__main__":
    sys.exit(main())
