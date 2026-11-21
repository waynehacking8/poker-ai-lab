"""Render ``out/validation.json`` (from ``league.validate``) as the clone validation tables.

    python -m league.validation_md out/validation.json reports/league/clone_validation.md
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path


def fmt(p, n):
    return "-" if p is None or p != p else f"{p:.3f} (n={n})"


def render(data: dict, model_meta: dict | None = None) -> str:
    table = data["table"]
    L = ["# Clone validation on held-out replays", "",
         f"Held-out: {data['n_test_matches']} matches, {data['n_test_hands']} hands (stable hash "
         "split of match ids; clustering, EM fit and size tables use the other matches only).  "
         f"Tolerance: {data['tolerance']}; open size passes within max(0.5 bb, 15%).  "
         "Each clone plays the field mix in the real format and its statistics are measured on "
         "its own simulated hands; real values come from the held-out hands of the bots in that "
         "archetype (or the single bot).", ""]
    rl, sl = data["real_len"], data["sim_len"]
    L += ["## Match length", "",
          f"Real held-out matches: mean {statistics.mean(rl):.1f} hands, median "
          f"{statistics.median(rl)}, n={len(rl)}.  Field clones vs field clones (simulated): mean "
          f"{statistics.mean(sl):.1f}, median {statistics.median(sl)}, n={len(sl)}.", ""]
    stats = [x[0] for x in next(iter(table.values()))]
    for name, rows in table.items():
        if name.startswith("bot:"):
            continue
        ok = [r for r in rows if r[5] is not None]
        L += [f"## {name}", "", f"{sum(bool(r[5]) for r in ok)} of {len(ok)} statistics within tolerance.", "",
              "| statistic | real | clone | within tolerance |", "|---|---|---|---|"]
        for k, pr, nr, ps, ns, okk in rows:
            L.append(f"| {k} | {fmt(pr, nr)} | {fmt(ps, ns)} | "
                     f"{'n/a' if okk is None else 'yes' if okk else 'NO'} |")
        L.append("")
    bots = {n: r for n, r in table.items() if n.startswith("bot:")}
    L += ["## Per-bot clones", "",
          "Cells are real / clone; `*` marks a miss of the tolerance, `.` an unmeasurable cell "
          "(too few held-out decisions).  The bots have only about 100 to 200 held-out hands, "
          "so most misses here are real-side noise, which the 2 SE rule already widens.", "",
          "| statistic | " + " | ".join(n[4:] for n in bots) + " |",
          "|---|" + "---|" * len(bots)]
    for i, k in enumerate(stats):
        cells = []
        for rows in bots.values():
            _, pr, nr, ps, ns, okk = rows[i]
            if okk is None:
                cells.append(".")
            else:
                cells.append(f"{pr:.2f} / {ps:.2f}{'' if okk else ' *'}")
        L.append(f"| {k} | " + " | ".join(cells) + " |")
    passes = {n: (sum(bool(r[5]) for r in rows if r[5] is not None),
                  sum(1 for r in rows if r[5] is not None)) for n, rows in bots.items()}
    L += ["", "Within tolerance per bot: " + ", ".join(
        f"{n[4:]} {a}/{b}" for n, (a, b) in passes.items()), ""]
    em = [sum(bool(r[5]) for r in rows if r[5] is not None) for n, rows in table.items()
          if not n.startswith("bot:") and "[naive]" not in n]
    nv = [sum(bool(r[5]) for r in rows if r[5] is not None) for n, rows in table.items()
          if "[naive]" in n]
    L += ["## Censoring effect", "",
          f"Statistics within tolerance (of 15) per archetype with the EM de-censored fit: {em}; "
          f"with a naive fit that only learns from hands whose cards were shown: {nv}.  The naive "
          "clones almost never fold, since a folded hand never reaches a showdown, which is the "
          "overstatement the censoring note warns about.", "", WEAKNESSES]
    return "\n".join(L)


WEAKNESSES = """## Weaknesses of the clones

* Memoryless and non-adaptive: a clone samples from fixed frequencies and never reacts to the
  opponent, so a candidate's opponent model has nothing to learn beyond those frequencies. Real
  bots that adapt, or leak patterns across hands, are not represented.
* Strength is an 8 bucket percentile (all-in equity percentile preflop, board-relative percentile
  with a rough draw bonus postflop) and the context is coarse (street, position, facing class, four
  stack bands). Board texture, blockers, bet history beyond the facing class and exact pot odds are
  invisible, so clones are blunter than the bots they imitate, especially in raised pots.
* Cluster membership of low-data bots comes from shrunk statistics, so an archetype mixes bots with
  different habits. The station archetype is the clearest case: the held-out real rate of folding
  to a button open and to bets is far above what the two high-volume stations it was fitted on do.
* The per-bot clones use only 150 to 1,400 hand-seats each, shrunk toward their archetype
  (pseudo-count 12); frequencies that are exactly 0 or 1 for a real bot (never folds the big blind)
  come out at 0.2 to 0.3. A lighter shrink (pseudo-count 3, `--k-bot 3`) raised the in-tolerance
  counts of the weaker clones by two to three statistics in a spot check, so treat per-bot results
  as a sensitivity check, not as a stand-in for that bot.
* Held-out sets are small (61 matches, 1,930 hands), so per-bot and rare-spot comparisons are noisy.
  The archetype count was chosen by silhouette on the training set, and the field weights come from
  how often each archetype appears among rated participants (a participant count, not hands).
* The field was observed between bots that mostly play each other; effects of a stronger opponent
  (for example a candidate that exploits) are extrapolation.
* Match length: the simulated field plays slightly longer matches than the real held-out set (about
  34 against 32 hands on average, medians 28 and 29).
"""


if __name__ == "__main__":
    data = json.loads(Path(sys.argv[1]).read_text())
    text = render(data)
    Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    Path(sys.argv[2]).write_text(text)
    print(text[:3000])
