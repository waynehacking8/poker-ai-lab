"""Is slow adaptation what keeps the bot under 80%? An oracle-prior probe.

Phase 1 plays the normal bot against an opponent and sums, over all matches,
the raw counts its opponent model collects (hits and opportunities per stat,
showdown hand percentiles). Phase 2 replays the arena with a bot whose model
starts every match already holding those true rates with near-infinite
weight, so from hand 1 it knows the opponent's frequencies exactly.

If the oracle bot clears 80% where the normal bot does not, slow learning of
frequencies is the bottleneck. If it does not, frequency modeling is not
enough and the gap is in how the bot uses what it knows (for example, what an
opponent's raise says about its hand), which a frequency model cannot carry.

    python scripts/adapt_probe.py --opp lag,station_raiser,maniac --measure 200 --matches 400
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import fields
from multiprocessing import Pool
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1]),
                str(Path(__file__).resolve().parents[1] / "chipzen_bot")]

from bot import HoldemBot  # noqa: E402
from holdem.arena import run_arena  # noqa: E402
from holdem.engine import MatchConfig, play_match  # noqa: E402
from holdem.opponents import make_baseline  # noqa: E402
from nlhe.model import Counter2, Stats  # noqa: E402

COUNTERS = [f.name for f in fields(Stats) if f.name not in ("hands", "showdown_pcts")]
ORACLE: dict = {}


def measure_one(job):
    opp_name, pair_seed, hero_seat = job
    hero = HoldemBot(seed=pair_seed * 7 + hero_seat)
    bots = [None, None]
    bots[hero_seat] = hero
    bots[1 - hero_seat] = make_baseline(opp_name, pair_seed * 13 + hero_seat)
    play_match(bots, pair_seed, MatchConfig())
    st = hero.brain.model.get(1 - hero_seat)
    return ({c: (getattr(st, c).hit, getattr(st, c).opp) for c in COUNTERS},
            st.hands, list(st.showdown_pcts))


def measure(opp: str, matches: int, workers: int) -> dict:
    jobs = [(opp, 900000 + k, s) for k in range(matches // 2) for s in (0, 1)]
    with Pool(workers) as pool:
        rows = pool.map(measure_one, jobs, chunksize=2)
    tot = defaultdict(lambda: [0, 0])
    pcts, hands = [], 0
    for counts, h, sd in rows:
        hands += h
        pcts.extend(sd)
        for c, (hit, n) in counts.items():
            tot[c][0] += hit
            tot[c][1] += n
    return {"rates": {c: (hit / n if n else None, n) for c, (hit, n) in tot.items()},
            "hands": hands, "showdown_pcts": pcts[:300]}


def oracle_stats() -> Stats:
    s = Stats()
    for c, (rate, n) in ORACLE["rates"].items():
        if rate is None:
            continue
        cnt: Counter2 = getattr(s, c)
        cnt.prior, cnt.k = rate, 1e6
        cnt.opp = 12  # past the 12-observation gates (is_station); the rate stays the prior
        cnt.hit = round(rate * 12)
    s.hands = 12
    s.showdown_pcts = list(ORACLE["showdown_pcts"])
    return s


def oracle_hero(seed):
    hero = HoldemBot(seed=seed)
    hero.brain.model.stats = defaultdict(oracle_stats)
    return hero


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--opp", default="lag,station_raiser,maniac")
    ap.add_argument("--measure", type=int, default=200)
    ap.add_argument("--matches", type=int, default=400)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    for opp in a.opp.split(","):
        ORACLE.clear()
        ORACLE.update(measure(opp, a.measure, a.workers))
        base = run_arena(opp, a.matches, a.seed, a.workers)
        orc = run_arena(opp, a.matches, a.seed, a.workers, hero_factory=oracle_hero)
        print(json.dumps({"opponent": opp,
                          "normal": [base["win_rate"], base["ci95"]],
                          "oracle_prior": [orc["win_rate"], orc["ci95"]],
                          "true_rates": {c: round(r, 3) for c, (r, n) in ORACLE["rates"].items()
                                         if r is not None}}), flush=True)


if __name__ == "__main__":
    main()
