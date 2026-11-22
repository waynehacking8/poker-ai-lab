"""Smoke test the ext: field bots: exceptions, illegal actions and per-decision time in the SDK engine.

    python -m tools.field_smoke --bots all --matches 50 --workers 4 > smoke.jsonl

Each bot plays `--matches` matches against `random` and `lag` (both seats, duplicate seeds). A probe of a few
matches runs first; a bot whose probe p99 is over the limit is reported as too slow and not run further.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rl  # noqa: E402,F401
from holdem.engine import MatchConfig, play_match  # noqa: E402
from holdem.opponents import make_baseline  # noqa: E402


class Probe:
    """Wraps a bot: times decide(), counts exceptions and illegal actions, forwards the hooks."""

    def __init__(self, bot):
        self.bot, self.times, self.exceptions, self.illegal, self.first_error = bot, [], 0, 0, None

    def __getattr__(self, name):
        if name.startswith("on_") and hasattr(self.bot, name):
            return getattr(self.bot, name)
        raise AttributeError(name)

    def decide(self, state):
        from chipzen import Action
        t0 = time.perf_counter()
        try:
            act = self.bot.decide(state)
        except Exception as e:  # noqa: BLE001
            self.exceptions += 1
            self.first_error = self.first_error or f"{type(e).__name__}: {e}"
            act = Action.fold() if state.to_call > 0 else Action.check()
        self.times.append(time.perf_counter() - t0)
        if act.action not in state.valid_actions:
            self.illegal += 1
        elif act.action == "raise" and not min(state.min_raise, state.max_raise) <= act.amount <= state.max_raise:
            self.illegal += 1
        return act


def one(job):
    bot_name, opp, seed, seat = job
    from rl.field_bots import build
    p = Probe(build(bot_name))
    bots = [None, None]
    bots[seat], bots[1 - seat] = p, make_baseline(opp, seed * 13 + seat)
    # strict=False so one illegal action is counted (above) and auto-corrected by the engine, not fatal
    res = play_match(bots, seed, MatchConfig(), strict=False)
    return dict(times=p.times, exc=p.exceptions, ill=p.illegal, err=p.first_error, won=res.winner == seat, hands=res.hands)


def summarize(rows):
    ts = sorted(t for r in rows for t in r["times"])
    n = len(ts)
    pct = lambda q: ts[min(n - 1, int(q * n))] * 1000 if n else 0.0  # noqa: E731
    return dict(matches=len(rows), decisions=n, exceptions=sum(r["exc"] for r in rows),
                illegal=sum(r["ill"] for r in rows), first_error=next((r["err"] for r in rows if r["err"]), None),
                ms_mean=round(sum(ts) / n * 1000, 2) if n else 0, ms_p99=round(pct(0.99), 2), ms_max=round(ts[-1] * 1000, 2) if n else 0,
                win_rate=round(sum(r["won"] for r in rows) / len(rows), 3), mean_hands=round(sum(r["hands"] for r in rows) / len(rows), 1))


def main():
    from rl.field_bots import REGISTRY
    ap = argparse.ArgumentParser()
    ap.add_argument("--bots", default="all")
    ap.add_argument("--matches", type=int, default=50)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--probe", type=int, default=4)
    ap.add_argument("--p99-limit-ms", type=float, default=1000.0)
    a = ap.parse_args()
    names = list(REGISTRY) if a.bots == "all" else a.bots.split(",")
    with Pool(a.workers) as pool:
        for name in names:
            out = {"bot": name}
            probe = summarize(pool.map(one, [(name, "random", 900 + k, k % 2) for k in range(a.probe)]))
            out["probe"] = probe
            if probe["exceptions"] or probe["ms_p99"] > a.p99_limit_ms:
                out["verdict"] = "drop: " + ("throws" if probe["exceptions"] else f"p99 {probe['ms_p99']} ms over limit")
            else:
                for opp in ("random", "lag"):
                    jobs = [(name, opp, 1000 + k, s) for k in range(a.matches // 2) for s in (0, 1)]
                    out[opp] = summarize(pool.map(one, jobs, chunksize=1))
                bad = any(out[o]["exceptions"] or out[o]["ms_p99"] > a.p99_limit_ms for o in ("random", "lag"))
                out["verdict"] = "drop" if bad else "ok"
            print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
