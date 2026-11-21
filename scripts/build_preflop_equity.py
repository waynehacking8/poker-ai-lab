"""Build the 169 x 169 hand-class equity matrix used by the Hold'em bot.

For every pair of starting-hand classes (AA, AKs, AKo, ...) this estimates the
all-in equity of class i against class j by Monte Carlo over concrete combos and
random boards, and counts how many card-compatible combo pairs exist (the
"card removal" weight).  The output is a small JSON file shipped with the bot:

    chipzen_bot/nlhe/data/preflop_equity.json

Usage:
    python scripts/build_preflop_equity.py --samples 4000 --workers 8

The result is deterministic for a given ``--samples`` and ``--seed``.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "chipzen_bot"))

from nlhe.cards import CLASS_COMBOS  # noqa: E402
from nlhe.evaluator import evaluate  # noqa: E402

OUT = ROOT / "chipzen_bot" / "nlhe" / "data" / "preflop_equity.json"


def pair_equity(args):
    i, j, samples, seed = args
    rng = random.Random(seed * 1_000_003 + i * 169 + j)
    pairs = [
        (a, b)
        for a in CLASS_COMBOS[i]
        for b in CLASS_COMBOS[j]
        if not set(a) & set(b)
    ]
    if i == j:
        return i, j, 0.5, len(pairs)
    score = 0.0
    for _ in range(samples):
        a, b = pairs[rng.randrange(len(pairs))]
        used = {a[0], a[1], b[0], b[1]}
        board = []
        while len(board) < 5:
            x = rng.randrange(52)
            if x not in used:
                used.add(x)
                board.append(x)
        ea = evaluate([*a, *board])
        eb = evaluate([*b, *board])
        score += 1.0 if ea > eb else 0.5 if ea == eb else 0.0
    return i, j, score / samples, len(pairs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=4000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    jobs = [(i, j, args.samples, args.seed) for i in range(169) for j in range(i, 169)]
    eq = [[0.5] * 169 for _ in range(169)]
    w = [[0] * 169 for _ in range(169)]
    t0 = time.time()
    with Pool(args.workers) as pool:
        for i, j, e, n in pool.imap_unordered(pair_equity, jobs, chunksize=64):
            eq[i][j], eq[j][i] = e, 1.0 - e
            w[i][j] = w[j][i] = n
    data = {
        "samples_per_pair": args.samples,
        "seed": args.seed,
        "eq": [[round(v * 10000) for v in row] for row in eq],
        "w": w,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
