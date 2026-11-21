"""Compare two clone models (for example the full fit and the uncontaminated prior).

Simulates every archetype of both models against the field mix with identical seeds and
reports the per-archetype statistic deltas, plus the held-out validation pass counts when
two ``validate`` outputs are given.  Appends a markdown section to a report.

    python -m league.compare_clones --a league/data/clones.npz --b league/data/clones_prior.npz \
        --sims 400 --workers 2 --md-append reports/league/clone_validation.md \
        --val-a out/validation.json --val-b out/validation_prior.json
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
    out = []
    for j in range(k):
        out.append(rates(merge([c for (c, _), job in zip(res, jobs) if job[2] == f"arch:{j}"])))
    return out


def section(meta, a, b, sims, val_a=None, val_b=None):
    pri = meta["prior"]
    L = ["## Uncontaminated prior (`league/data/clones_prior.npz`)", "",
         "The archetype tables refit without every match that involves one of the 10 per-bot "
         f"test bots ({', '.join(pri['excluded_bots'])}). Archetype labels, weights and the "
         "per-bot clones are copied unchanged from `clones.npz`, so ids stay comparable. "
         f"{pri['matches_kept']} of {pri['matches_total']} matches ({pri['hands_kept']} hands) "
         "remain.", "",
         "Hand-seats left per archetype: " + ", ".join(
             f"{n} {s}" for n, s in zip(meta["arch_names"], pri["seats_per_archetype"])) + ". "
         f"Every archetype table is shrunk toward the pooled table of the remaining seats with "
         f"pseudo-count {pri['k_prior']:.0f}; archetypes with under {pri['min_seats']} seats "
         "(" + ", ".join(meta["arch_names"][j] for j in pri["thin_archetypes"]) + ") are thin, "
         "and an archetype with zero seats is the pooled table, not that archetype. "
         "A1-station is Kimiko and DeepStack only, both held-out bots, so it has no clean data "
         "at all and the prior's A1 is a generic table: do not use `arch:1` of the prior as a "
         "station.", "",
         f"### How far the tables moved ({sims} simulated matches per archetype and model, same "
         "seeds, against the field mix)", "",
         "Cells are full fit, prior and the change in percentage points.", "",
         "| statistic | " + " | ".join(meta["arch_names"]) + " |",
         "|---|" + "---|" * meta["k"]]
    mean_abs = [[] for _ in range(meta["k"])]
    for key in list(RATE_STATS):
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
    if val_a and val_b:
        L += ["", "### Held-out validation (70/30 split, same held-out matches)", "",
              "Statistics within tolerance (of 15) per archetype. The base columns are the "
              "contaminated train-split fit, the prior columns the same split refit without the "
              "test bots' matches. Archetype names come from the split's own clustering.", "",
              "| archetype | contaminated fit | prior |", "|---|---|---|"]
        for na, rows_a in val_a["table"].items():
            if na.startswith("bot:") or "[naive]" in na:
                continue
            rows_b = val_b["table"].get(na)
            ok = lambda rows: sum(bool(r[5]) for r in rows if r[5] is not None)  # noqa: E731
            L.append(f"| {na} | {ok(rows_a)} | {ok(rows_b) if rows_b else '-'} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--sims", type=int, default=400)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--md-append", default=None)
    ap.add_argument("--val-a", default=None)
    ap.add_argument("--val-b", default=None)
    args = ap.parse_args(argv)
    meta = CloneModel(args.b).meta
    k, w = meta["k"], meta["weights_rated"]
    sa = sim_stats(args.a, args.sims, args.workers, k, w)
    sb = sim_stats(args.b, args.sims, args.workers, k, w)
    va = json.loads(Path(args.val_a).read_text()) if args.val_a else None
    vb = json.loads(Path(args.val_b).read_text()) if args.val_b else None
    text = section(meta, sa, sb, args.sims, va, vb)
    if args.md_append:
        with open(args.md_append, "a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n" + text)
    print(text)


if __name__ == "__main__":
    main()
