"""Compare the full clone fit with its uncontaminated priors.

Simulates every archetype of each model against the field mix with identical seeds and
reports the per-archetype statistic deltas, plus held-out validation pass counts from
``validate`` outputs.  Appends a markdown section to a report.

    python -m league.compare_clones --a league/data/clones.npz \
        --b league/data/clones_prior.npz --c league/data/clones_prior_strict.npz \
        --sims 400 --workers 2 --md-append reports/league/clone_validation.md \
        --val-a out/validation.json --val-b out/validation_prior.json \
        --val-c out/validation_prior_strict.json
"""

from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from .clone import CloneModel
from .stats import RATE_STATS, rates
from .validate import merge, sim_job


def sim_stats(path, sims, workers, k, weights):
    jobs = [(str(path), False, f"arch:{j}", weights, 20_000 * j + i, i % 2 == 0)
            for j in range(k) for i in range(sims)]
    with Pool(workers) as pool:
        res = pool.map(sim_job, jobs, chunksize=4)
    return [rates(merge([c for (c, _), job in zip(res, jobs) if job[2] == f"arch:{j}"]))
            for j in range(k)]


def movement_table(meta, a, b):
    L = ["| statistic | " + " | ".join(meta["arch_names"]) + " |", "|---|" + "---|" * meta["k"]]
    mean_abs = [[] for _ in range(meta["k"])]
    for key in RATE_STATS:
        cells = []
        for j in range(meta["k"]):
            pa, pb = a[j][key][0], b[j][key][0]
            if pa != pa or pb != pb:
                cells.append(".")
                continue
            mean_abs[j].append(abs(pb - pa))
            cells.append(f"{pa:.2f} / {pb:.2f} ({100 * (pb - pa):+.0f})")
        L.append(f"| {key} | " + " | ".join(cells) + " |")
    L.append("| mean abs change, pp | " + " | ".join(
        f"{100 * float(np.mean(m)):.1f}" for m in mean_abs) + " |")
    return L


def within(rows):
    return sum(bool(r[5]) for r in rows if r[5] is not None)


def section(meta_b, meta_c, sims, a, b, c, val_a, val_b, val_c):
    pb, pc = meta_b["prior"], meta_c["prior"]
    names = meta_b["arch_names"]
    pooled = [names[j] for j in meta_b["pooled_archetypes"]]
    L = ["## Uncontaminated prior", "",
         "The per-bot clones are the league's held-out test opponents, so anything trained against "
         "the archetypes must not have seen those 10 bots: " + ", ".join(pb["excluded_bots"]) +
         ". Two refits of the archetype action tables, with the same fit and shrinkage (toward "
         f"the pooled table of the remaining seats, pseudo-count {pb['k_prior']:.0f}); archetype "
         "labels, weights and per-bot clones are copied unchanged from `clones.npz`, so ids "
         "stay comparable.", "",
         "* `league/data/clones_prior.npz` (seat variant, the clean definition): only the test bots' "
         f"own seats are dropped, their opponents' seats stay. {pb['matches_kept']} matches, "
         f"{pb['hands_kept']} hands.",
         "* `league/data/clones_prior_strict.npz` (strict variant): every match involving a test bot "
         f"is dropped. {pc['matches_kept']} of {pc['matches_total']} matches, {pc['hands_kept']} "
         "hands.", "",
         "Both files carry `meta[\"pooled_archetypes\"]`. " + ", ".join(pooled) +
         " is Kimiko and DeepStack only, both test bots, so no clean data exists for it under "
         "either rule: its table is the pooled table, not a station. Do not use that `arch:` id "
         "of a prior as a station.", "",
         "Hand-seats left per archetype:", "",
         "| variant | " + " | ".join(names) + " |", "|---|" + "---|" * meta_b["k"],
         "| seat (clones_prior) | " + " | ".join(str(n) for n in pb["seats_per_archetype"]) + " |",
         "| strict (clones_prior_strict) | " + " | ".join(
             str(n) for n in pc["seats_per_archetype"]) + " |", ""]
    L += [f"### How far the tables moved ({sims} simulated matches per archetype and model, same "
          "seeds, against the field mix)", "",
          "Cells are full fit / prior and the change in percentage points. The last row is the mean "
          "absolute change over the 14 rate statistics.", "",
          "Seat variant:", ""] + movement_table(meta_b, a, b) + ["", "Strict variant:", ""] \
        + movement_table(meta_c, a, c)
    if val_a and val_b and val_c:
        L += ["", "### Held-out validation (70/30 split, same held-out matches)", "",
              "Statistics within tolerance (of 15) per archetype of the split's own clustering. "
              "Contaminated is the train-split fit; seat and strict are the same split refit "
              "without the test bots' seats or matches.", "",
              "| archetype | contaminated fit | seat prior | strict prior |", "|---|---|---|---|"]
        for na, rows_a in val_a["table"].items():
            if na.startswith("bot:") or "[naive]" in na:
                continue
            rb, rc = val_b["table"].get(na), val_c["table"].get(na)
            L.append(f"| {na} | {within(rows_a)} | {within(rb) if rb else '-'} | "
                     f"{within(rc) if rc else '-'} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="full (contaminated) fit")
    ap.add_argument("--b", required=True, help="seat prior")
    ap.add_argument("--c", required=True, help="strict prior")
    ap.add_argument("--sims", type=int, default=400)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--md-append", default=None)
    ap.add_argument("--val-a")
    ap.add_argument("--val-b")
    ap.add_argument("--val-c")
    args = ap.parse_args(argv)
    mb, mc = CloneModel(args.b).meta, CloneModel(args.c).meta
    k, w = mb["k"], mb["weights_rated"]
    sa, sb, sc = (sim_stats(p, args.sims, args.workers, k, w) for p in (args.a, args.b, args.c))
    load = lambda p: json.loads(Path(p).read_text()) if p else None  # noqa: E731
    text = section(mb, mc, args.sims, sa, sb, sc, load(args.val_a), load(args.val_b),
                   load(args.val_c))
    if args.md_append:
        with open(args.md_append, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n" + text)
    print(text)


if __name__ == "__main__":
    main()
