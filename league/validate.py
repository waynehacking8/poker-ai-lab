"""Validate the clones on held-out replays.

Fit on a train split, then compare statistics of the held-out real hands against the
same statistics of clone hands simulated in the real match format (the clone faces the
field mix, as the real bots did).  Also reports a naive (showdown-only) fit to show the
censoring bias, and match length of field vs field.

    python -m league.validate --data data --model out/clones_train.npz --sims 600 --workers 4
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import zlib
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from holdem.engine import MatchConfig, play_match

from .clone import CloneBot, CloneModel
from .replays import load_dir
from .stats import RATE_STATS, add_hand, new_counter, rates, rec_from_engine, se

TOL_ABS = 0.05
_M = {}


def _model(path, naive):
    key = (path, naive)
    if key not in _M:
        m = CloneModel(path)
        if naive:
            m.arch = m.naive
        _M[key] = m
    return _M[key]


def sim_job(job):
    path, naive, spec, weights, seed, subject_first = job
    model = _model(path, naive)
    rng = random.Random(seed)
    opp_arch = rng.choices(range(len(weights)), weights=weights)[0]
    subj = CloneBot(spec, seed * 3 + 1, model)
    opp = CloneBot(f"arch:{opp_arch}", seed * 3 + 2, model)
    seat = 0 if subject_first else 1
    bots = [None, None]
    bots[seat], bots[1 - seat] = subj, opp
    counter = new_counter()
    lens = []

    def on_hand(hand, result):
        rec = rec_from_engine(["s", "o"][::1] if seat == 0 else ["o", "s"], result,
                              hand.dealer, hand.bb, hand.start_stacks)
        add_hand(counter, rec, include=lambda s: s == seat)

    res = play_match(bots, seed, MatchConfig(), strict=False, on_hand=on_hand)
    lens.append(res.hands)
    return {k: list(v) for k, v in counter.items()}, res.hands


def merge(parts):
    out = new_counter()
    for p in parts:
        for k, (n, d) in p.items():
            out[k][0] += n
            out[k][1] += d
    return out


def real_counter(hands, names):
    c = new_counter()
    for h in hands:
        add_hand(c, h, include=lambda s: h.names[s] in names)
    return c


def row(label, real, sim):
    r, s = rates(real), rates(sim)
    out = []
    for k in list(RATE_STATS) + ["open_size_bb"]:
        pr, nr = r[k]
        ps, ns = s[k]
        if nr == 0 or ns == 0 or pr != pr or ps != ps:
            out.append((k, pr, nr, ps, ns, None))
            continue
        if k == "open_size_bb":
            ok = abs(pr - ps) <= max(0.5, 0.15 * pr)
        else:
            tol = max(TOL_ABS, 2 * math.sqrt(se(pr, nr) ** 2 + se(ps, ns) ** 2))
            ok = abs(pr - ps) <= tol
        out.append((k, pr, nr, ps, ns, bool(ok)))
    return label, out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--model", default="out/clones_train.npz")
    ap.add_argument("--sims", type=int, default=600, help="matches per archetype")
    ap.add_argument("--bot-sims", type=int, default=300)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="out/validation.json")
    args = ap.parse_args(argv)
    model = CloneModel(args.model)
    meta = model.meta
    test_ids = set(meta["test_match_ids"])
    ms = [(m, hs) for m, hs in load_dir(args.data) if m["id"] in test_ids]
    hands = [h for _, hs in ms for h in hs]
    weights = meta["weights_rated"]
    k = meta["k"]
    jobs, tags = [], []
    for j in range(k):
        for naive in (False, True):
            n = args.sims if not naive else args.sims // 2
            for i in range(n):
                jobs.append((args.model, naive, f"arch:{j}", weights, 10_000 * j + i + (5_000_000 if naive else 0), i % 2 == 0))
                tags.append(("arch", j, naive))
    for b in meta["bots"]:
        for i in range(args.bot_sims):
            jobs.append((args.model, False, f"bot:{b}", weights, 7_000_000 + zlib.crc32(b.encode()) % 100000 * 10 + i, i % 2 == 0))
            tags.append(("bot", b, False))
    # field vs field match length
    for i in range(args.sims):
        jobs.append((args.model, False, f"arch:{random.Random(i).choices(range(k), weights=weights)[0]}", weights, 9_000_000 + i, True))
        tags.append(("field", 0, False))
    with Pool(args.workers) as pool:
        res = pool.map(sim_job, jobs, chunksize=4)
    groups = defaultdict(list)
    lens = defaultdict(list)
    for t, (c, hl) in zip(tags, res):
        groups[t].append(c)
        lens[t].append(hl)
    lab = meta["bot_archetype"]
    table = {}
    for j in range(k):
        names = {n for n, a in lab.items() if a == j}
        real = real_counter(hands, names)
        for naive in (False, True):
            _, r = row(meta["arch_names"][j], real, merge(groups[("arch", j, naive)]))
            table[f"{meta['arch_names'][j]}{' [naive]' if naive else ''}"] = r
    for b in meta["bots"]:
        real = real_counter(hands, {b})
        _, r = row(b, real, merge(groups[("bot", b, False)]))
        table[f"bot:{b}"] = r
    real_len = [len(hs) for _, hs in ms]
    sim_len = lens[("field", 0, False)]
    out = {"table": table, "real_len": real_len, "sim_len": sim_len, "n_test_matches": len(ms),
           "n_test_hands": len(hands), "tolerance": f"abs {TOL_ABS} or 2 SE of the difference"}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out))
    print(f"real hands/match mean {statistics.mean(real_len):.1f} median {statistics.median(real_len)}"
          f" | sim mean {statistics.mean(sim_len):.1f} median {statistics.median(sim_len)}")
    for name, r in table.items():
        ok = [x for x in r if x[5] is not None]
        print(f"{name:32} pass {sum(x[5] for x in ok)}/{len(ok)}")


if __name__ == "__main__":
    main()
