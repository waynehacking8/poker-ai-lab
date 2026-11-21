"""Refit the archetype action tables without the held-out bots (an uncontaminated prior).

The per-bot clones are the league's held-out test opponents.  Anything trained against the
archetypes (RL, a decision model) must not have seen those bots.  ``--mode seat`` (default)
drops only those bots' own seats and keeps their opponents' seats; ``--mode match`` is the
strict variant that drops every match involving one of them.  Archetype definitions (cluster labels, weights, member lists)
are copied from the base model unchanged, so archetype ids stay comparable; only the action
tables and size samples are refit.  The per-bot tables are copied as they are.

An archetype left with fewer than ``--min-seats`` hand-seats is shrunk toward the pooled
table of all remaining hand-seats (pseudo-count ``--k-prior`` for every archetype), and one
with none at all becomes that pooled table; ``meta["prior_seats"]`` records the counts.

    python -m league.fit_prior --base league/data/clones.npz --out league/data/clones_prior.npz
"""

from __future__ import annotations

import argparse
import json

import numpy as np

from .fit import collect_sizes, fit_table, pack_sizes, save, seat_records, split_of
from .replays import load_dir

K_PRIOR = 30.0


def fit_prior(base_path, data_dir, out_path, holdout=0.0, seed=1, k_prior=K_PRIOR, iters=8,
              min_seats=400, mode="seat"):
    d = np.load(base_path, allow_pickle=False)
    meta = json.loads(str(d["meta"]))
    held = set(meta["bots"])
    lab = meta["bot_archetype"]
    ms = load_dir(data_dir)
    test_ids = set(meta.get("test_match_ids", []))
    if holdout:
        test_ids = {m["id"] for m, _ in ms if split_of(m["id"], holdout, seed)}
    keep = [(m, hs) for m, hs in ms if m["id"] not in test_ids
            and (mode == "seat" or not any(p["name"] in held for p in m["participants"]))]
    hands = [h for _, hs in keep for h in hs]
    by_arch = {j: [] for j in range(meta["k"])}
    for name, rec in seat_records(hands):
        if name in lab and name not in held:  # the test bots' own seats never enter a table
            by_arch[lab[name]].append(rec)
    pooled_recs = [r for rs in by_arch.values() for r in rs]
    pooled, _ = fit_table(pooled_recs, iters)
    arch_theta, arch_naive, arch_sizes, seats = [], [], [], []
    for j in range(meta["k"]):
        recs = by_arch[j]
        seats.append(len(recs))
        if recs:
            _, C = fit_table(recs, iters)
            arch_theta.append((C + k_prior * pooled) / (C.sum(-1, keepdims=True) + k_prior))
            arch_naive.append(fit_table(recs, naive=True)[0])
        else:
            arch_theta.append(pooled.copy())
            arch_naive.append(pooled.copy())
        arch_sizes.append(pack_sizes(collect_sizes(recs)))
    meta["arch_sizes"] = arch_sizes
    meta["all_sizes"] = pack_sizes(collect_sizes(pooled_recs))
    meta["prior"] = {
        "base": str(base_path), "excluded_bots": sorted(held), "k_prior": k_prior,
        "min_seats": min_seats, "matches_kept": len(keep), "matches_total": len(ms),
        "hands_kept": len(hands), "seats_per_archetype": seats, "mode": mode,
        "pooled_archetypes": [j for j, n in enumerate(seats) if n == 0],
        "thin_archetypes": [j for j, n in enumerate(seats) if n < min_seats],
    }
    meta["pooled_archetypes"] = meta["prior"]["pooled_archetypes"]  # no clean data: pooled table
    meta["test_match_ids"] = sorted(test_ids)
    save(out_path, meta, np.array(arch_theta), d["bot_theta"].astype(np.float64),
         np.array(arch_naive))
    return meta["prior"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="league/data/clones.npz")
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="league/data/clones_prior.npz")
    ap.add_argument("--holdout", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--min-seats", type=int, default=400)
    ap.add_argument("--mode", choices=("seat", "match"), default="seat",
                    help="seat: drop only the test bots' own seats; match: drop their whole matches")
    args = ap.parse_args(argv)
    info = fit_prior(args.base, args.data, args.out, args.holdout, args.seed,
                     min_seats=args.min_seats, mode=args.mode)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
