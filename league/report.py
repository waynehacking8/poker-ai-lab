"""Leaderboard from ``results.jsonl``.

Primary rank: match-win rate against the field population, i.e. the archetype win rates
weighted by how often each archetype appears in rated matches, with a 95% bootstrap CI
that resamples duplicate pairs inside each archetype.  Tie-break: mean hands per win.

    python -m league.report --out out/league --md reports/league/leaderboard.md
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from .clone import load_model


def wilson(wins: float, n: int, z: float = 1.96):
    if n == 0:
        return 0.0, 1.0
    p = wins / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def pair_scores(rows):
    """{(opp, pair): mean a_win over the two seatings}."""
    acc = defaultdict(list)
    for r in rows:
        acc[(r["opp"], r["pair"])].append(r["a_win"])
    return {k: sum(v) / len(v) for k, v in acc.items()}


def stratified(rows, weights, reps=2000, seed=0):
    """(estimate, lo, hi, n_pairs) with archetype weights; bootstrap over pairs."""
    strata = defaultdict(list)
    for (opp, _), s in pair_scores(rows).items():
        strata[int(opp.split(":")[1])].append(s)
    ks = [k for k in sorted(strata) if strata[k]]
    if not ks:
        return None
    w = np.array([weights[k] for k in ks])
    w = w / w.sum()
    arrs = [np.array(strata[k]) for k in ks]
    est = float(sum(wi * a.mean() for wi, a in zip(w, arrs)))
    rng = np.random.default_rng(seed)
    boots = np.zeros(reps)
    for wi, a in zip(w, arrs):
        boots += wi * a[rng.integers(0, len(a), (reps, len(a)))].mean(1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return est, float(lo), float(hi), sum(len(a) for a in arrs)


def pooled(rows):
    """(rate, lo, hi, n_matches) with a Wilson interval on matches."""
    n = len(rows)
    w = sum(r["a_win"] for r in rows)
    lo, hi = wilson(w, n)
    return (w / n if n else float("nan")), lo, hi, n


def pct(x):
    return "-" if x is None or x != x else f"{100 * x:.1f}"


def ci(t):
    return "-" if t is None else f"{pct(t[0])} [{pct(t[1])}, {pct(t[2])}]"


def num(x, fmt="{:.1f}"):
    return "-" if x is None else fmt.format(x)


GATE = 0.80
GATE_MIN_MATCHES = 400


def gate(rows, meta):
    """Per-opponent gate: {label: (rate, lo, hi, n, passed)}; pass = rate >= 80% over >= 400 matches."""
    out = {}
    labels = [(f"base:{n}", f"baseline {n}") for n in sorted({r["opp"][5:] for r in rows
                                                              if r["opp"].startswith("base:")})]
    labels += [(f"arch:{k}", f"archetype {meta['arch_names'][k]}") for k in range(meta["k"])]
    labels += [(f"bot:{b}", f"bot clone {b}") for b in meta["bots"]]
    for key, label in labels:
        rs = [r for r in rows if r["opp"] == key]
        if not rs:
            continue
        rate, lo, hi, n = pooled(rs)
        out[label] = (rate, lo, hi, n, rate >= GATE and n >= GATE_MIN_MATCHES)
    return out


def build(results_path, model_path):
    meta = load_model(model_path).meta
    rows = [json.loads(x) for x in Path(results_path).read_text().splitlines() if x.strip()]
    by_a = defaultdict(list)
    for r in rows:
        by_a[r["a"]].append(r)
    weights = meta["weights_rated"]
    board = []
    for a, rs in by_a.items():
        field = [r for r in rs if r["opp"].startswith("arch:")]
        botc = [r for r in rs if r["opp"].startswith("bot:")]
        base = [r for r in rs if r["opp"].startswith("base:")]
        wins = [r["hands"] for r in field if r["a_win"] == 1.0]
        tms = [r["a_ms_mean"] for r in rs if r.get("a_ms_mean") is not None]
        board.append({
            "entrant": a, "field": stratified(field, weights),
            "hands_per_win": (sum(wins) / len(wins)) if wins else None,
            "botclone": pooled(botc) if botc else None,
            "baseline": pooled(base) if base else None,
            "field_matches": len(field), "matches": len(rs),
            "errors": sum(r.get("a_err", 0) for r in rs),
            "ms_mean": (sum(tms) / len(tms)) if tms else None,
            "ms_max": max((r.get("a_ms_max", 0) for r in rs), default=0),
            "by_arch": {k: pooled([r for r in field if r["opp"] == f"arch:{k}"])
                        for k in range(meta["k"]) if any(r["opp"] == f"arch:{k}" for r in field)},
            "gate": gate(rs, meta),
            "by_bot": {b: pooled([r for r in botc if r["opp"] == f"bot:{b}"])
                       for b in meta["bots"] if any(r["opp"] == f"bot:{b}" for r in botc)},
        })
    board.sort(key=lambda b: (-(b["field"][0] if b["field"] else -1),
                              b["hands_per_win"] if b["hands_per_win"] else 1e9))
    names = [b["entrant"] for b in board]
    cell = defaultdict(list)
    for r in rows:
        if r["a"] in names and r["opp"] in names:
            cell[(r["a"], r["opp"])].append(r["a_win"])
            cell[(r["opp"], r["a"])].append(1 - r["a_win"])
    matrix = {k: (sum(v) / len(v), len(v)) for k, v in cell.items()}
    return meta, board, matrix, names


def markdown(meta, board, matrix, names, title="League leaderboard"):
    L = [f"# {title}", ""]
    L.append("Rank is the match-win rate against the field population (archetype win rates "
             "weighted by archetype share in rated matches), 95% bootstrap CI over duplicate "
             "pairs; ties broken by mean hands per won match (fewer is better).  Win rate is "
             "percent of matches, a tied hand cap counts half.")
    L.append("")
    L.append("| # | entrant | gate | field win % [95% CI] | hands/win "
             "| bot-clone win % [95% CI] | baseline win % [95% CI] | field matches "
             "| decide ms mean/max | errors |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for i, b in enumerate(board, 1):
        bc = ci(b["botclone"][:3]) if b["botclone"] else "-"
        bs = ci(b["baseline"][:3]) if b["baseline"] else "-"
        g = b["gate"]
        npt = sum(v[4] for v in g.values())
        if any(v[3] < GATE_MIN_MATCHES for v in g.values()):
            gp = f"n/a (under {GATE_MIN_MATCHES} matches) {npt}/{len(g)}"
        else:
            gp = ("PASS " if npt == len(g) else "FAIL ") + f"{npt}/{len(g)}"
        L.append(f"| {i} | {b['entrant']} | {gp} | {ci(b['field'])} | "
                 f"{num(b['hands_per_win'])} | "
                 f"{bc} | {bs} | {b['field_matches']} | "
                 f"{num(b['ms_mean'])}/{b['ms_max']:.0f} | {b['errors']} |")
    L += ["", f"## Gate: at least {100 * GATE:.0f}% over at least {GATE_MIN_MATCHES} matches, per opponent",
          "",
          "An entrant passes an opponent when its win rate against that opponent alone is at least "
          f"{100 * GATE:.0f}% over at least {GATE_MIN_MATCHES} matches ({GATE_MIN_MATCHES // 2} "
          "duplicate pairs); it passes the gate only if it passes every baseline, every archetype "
          "clone and every per-bot clone. The 95% Wilson lower bound over matches is shown next "
          "to the point estimate. Baseline entrants play fewer matches, so their rows read n/a. "
          "An entrant never plays itself.", ""]
    for b in board:
        L += [f"### {b['entrant']}", "",
              "| opponent | win % | 95% lower bound | matches | result |",
              "|---|---|---|---|---|"]
        for label, (rate, lo, hi, n, ok) in b["gate"].items():
            res = "PASS" if ok else ("n/a" if n < GATE_MIN_MATCHES else "FAIL")
            L.append(f"| {label} | {pct(rate)} | {pct(lo)} | {n} | {res} |")
        L.append("")
    L += ["## Field population", "",
          "Archetype shares (rated participants): " + ", ".join(
              f"{n} {100 * w:.0f}%" for n, w in zip(meta["arch_names"], meta["weights_rated"])), ""]
    L.append("| entrant | " + " | ".join(meta["arch_names"]) + " |")
    L.append("|---|" + "---|" * meta["k"])
    for b in board:
        cells = []
        for k in range(meta["k"]):
            t = b["by_arch"].get(k)
            cells.append("-" if t is None else f"{pct(t[0])} (n={t[3]})")
        L.append(f"| {b['entrant']} | " + " | ".join(cells) + " |")
    L += ["", "## Per-bot clones (win %, matches)", ""]
    L.append("| entrant | " + " | ".join(meta["bots"]) + " |")
    L.append("|---|" + "---|" * len(meta["bots"]))
    for b in board:
        cells = []
        for x in meta["bots"]:
            t = b["by_bot"].get(x)
            cells.append("-" if t is None else f"{pct(t[0])} ({t[3]})")
        L.append(f"| {b['entrant']} | " + " | ".join(cells) + " |")
    L += ["", "## Head-to-head matrix (row's win % against column, matches)", ""]
    L.append("| row \\ col | " + " | ".join(names) + " |")
    L.append("|---|" + "---|" * len(names))
    for x in names:
        cells = []
        for y in names:
            if x == y:
                cells.append(".")
            elif (x, y) in matrix:
                cells.append(f"{pct(matrix[(x, y)][0])} ({matrix[(x, y)][1]})")
            else:
                cells.append("-")
        L.append(f"| {x} | " + " | ".join(cells) + " |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/league")
    ap.add_argument("--model", default=str(Path(__file__).parent / "data" / "clones.npz"))
    ap.add_argument("--md", default=None)
    ap.add_argument("--title", default="League leaderboard")
    args = ap.parse_args(argv)
    meta, board, matrix, names = build(Path(args.out) / "results.jsonl", args.model)
    text = markdown(meta, board, matrix, names, args.title)
    if args.md:
        Path(args.md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.md).write_text(text)
    print(text)


if __name__ == "__main__":
    main()
