"""Sanity check of the state mapping: blueprint vs a baseline with FLAT 50/100 blinds.

With the season schedule the stacks shrink to 5-30 bb within a few dozen hands, far
below the blueprint's 100 bb. With flat blinds every hand starts at the depth the
blueprint was trained for, so a wrong state mapping would show up as a poor result
against simple baselines.

    BP_DATA=... python -m bpopp.flat_check --opp station --matches 60 --workers 3
"""

from __future__ import annotations

import argparse
import json
import statistics
from multiprocessing import Pool

import bpopp  # noqa: F401
from holdem.arena import wilson
from holdem.engine import MatchConfig, play_match
from holdem.opponents import make_baseline


def one(job):
    from bpopp.opponent import make_bp100

    opp, seed, seat, hands = job
    bots = [None, None]
    bots[seat] = make_bp100()
    bots[1 - seat] = make_baseline(opp, seed * 13 + seat)
    cfg = MatchConfig(max_hands=hands, schedule=((10**9, 100),), final_bb=100)
    r = play_match(bots, seed, cfg)
    return seat, r.hands, r.winner, r.stacks, r.capped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opp", required=True)
    ap.add_argument("--matches", type=int, default=60)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--max-hands", type=int, default=300)
    a = ap.parse_args()
    jobs = [(a.opp, 700 + k, s, a.max_hands) for k in range(a.matches // 2) for s in (0, 1)]
    with Pool(a.workers) as p:
        rows = p.map(one, jobs, chunksize=1)
    wins = sum(1 for s, h, w, st, c in rows if w == s)
    capped = sum(c for *_, c in rows)
    # at the hand cap the winner is whoever holds more chips (capped matches are counted)
    lo, hi = wilson(wins, len(rows))
    print(json.dumps({"opp": a.opp, "matches": len(rows), "bp_wins": wins, "win_rate": wins / len(rows),
                      "capped": capped, "ci95": [round(lo, 3), round(hi, 3)],
                      "mean_hands": round(statistics.mean(h for _, h, *_ in rows), 1)}))


if __name__ == "__main__":
    main()
