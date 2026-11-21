"""Teacher labels from ManiacBR for distillation (expert iteration with an exact teacher).

Plays matches against the maniac in the SDK engine. At every decision ManiacBR names its action; the state is
featurized exactly like the runtime (rl.features.build) and the teacher action is mapped to the nearest legal
discrete action. With probability ``beta`` the teacher acts (expert states), otherwise the student policy acts
(DAgger states), so the labels cover the states the student actually visits.

    python -m rl.teacher --model ckpt/ablA/latest.npz --out data/maniac_labels.npz --matches 600 --workers 6
"""

from __future__ import annotations

import argparse
import math
import random
from multiprocessing import Pool

import numpy as np

import rl  # noqa: F401
from chipzen import Action, Bot
from holdem.engine import MatchConfig, play_match
from holdem.opponents import make_baseline
from rl.features import Tracker, build
from rl.runtime import Policy


def teacher_label(act, state, amt, mask):
    """Map a chipzen Action to the discrete index 0..5."""
    if act.action == "fold":
        return 0
    if act.action in ("check", "call"):
        return 1
    if act.action == "all_in":
        return 5 if mask[5] else 1
    best, bd = 1, 1e9
    for a in (2, 3, 4, 5):
        if mask[a]:
            d = abs(math.log(max(amt[a], 1)) - math.log(max(act.amount, 1)))
            if d < bd:
                best, bd = a, d
    return best


class DaggerBot(Bot):
    def __init__(self, model, table, beta, seed, record):
        super().__init__()
        from rl.teacher_br.bot import ManiacBR
        self.teacher = ManiacBR(table=table)
        self.policy = Policy(model, 1.0, seed)
        self.tracker = Tracker()
        self.beta = beta
        self.rng = random.Random(seed)
        self.record = record

    def on_match_start(self, info):
        me = info.get("your_seat")
        if me is None:
            for seat in info.get("seats", ()) or ():
                if seat.get("is_self"):
                    me = seat["seat"]
        self.tracker = Tracker()
        self.tracker.me = int(me or 0)

    def on_round_result(self, message):
        self.tracker.round_result(message.get("result", {}) or {})

    def on_round_start(self, message):
        self.tracker.round_start(message)

    def decide(self, state):
        self.tracker.me = state.your_seat
        f, mask, amt = build(state, self.tracker)
        tact = self.teacher.decide(state)
        lab = teacher_label(tact, state, amt, mask)
        self.record.append((np.asarray(f, np.float32), np.asarray(mask, bool), lab))
        if self.rng.random() < self.beta:
            return tact
        a = self.policy.act(f, mask)
        if a == 0:
            return Action.fold()
        if a == 1:
            return Action.call() if state.to_call > 0 else Action.check()
        return Action.raise_to(int(amt[a]))


def job(args):
    model, table, beta, seed, seat = args
    rec = []
    hero = DaggerBot(model, table, beta, seed, rec)
    opp = make_baseline("maniac", seed * 13 + seat)
    bots = [None, None]
    bots[seat] = hero
    bots[1 - seat] = opp
    res = play_match(bots, seed, MatchConfig())
    return rec, res.winner == seat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--table", default="data/maniac_k25.npz")
    ap.add_argument("--out", required=True)
    ap.add_argument("--matches", type=int, default=600)
    ap.add_argument("--beta", type=float, default=0.5, help="share of decisions where the teacher acts")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    jobs = [(a.model, a.table, a.beta, a.seed * 100000 + k, k % 2) for k in range(a.matches)]
    with Pool(a.workers) as p:
        rows = p.map(job, jobs, chunksize=1)
    recs = [r for rs, _ in rows for r in rs]
    F = np.stack([r[0] for r in recs])
    M = np.stack([r[1] for r in recs])
    L = np.array([r[2] for r in recs], np.int64)
    np.savez_compressed(a.out, obs=F, mask=M, label=L)
    print(f"{len(L)} labels, match win rate while collecting {np.mean([w for _, w in rows]):.3f}, "
          f"label counts {np.bincount(L, minlength=6).tolist()}")


if __name__ == "__main__":
    main()
