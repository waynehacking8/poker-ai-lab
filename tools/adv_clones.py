"""Adversarial opponent search in the generated clone family (GOAT-style, arXiv 2504.15457).

    python tools/adv_clones.py --model ckpt/RUN/latest.npz --out data/clones_adv.npz [--cands 192 --keep 32]

Samples candidates from rl/clonegen.py, plays the policy against each in the C engine, mutates the
hardest, and writes the 6 fitted archetypes plus the KEEP hardest and RAND random candidates, so
training can focus on the plausible opponents the policy loses to. Prints the win-rate spread.
"""

import argparse
import json
import os
import tempfile

import numpy as np

import rl  # noqa: F401
from rl import clonegen, clones
from rl.eval_fast import run_matches

CHUNK = 64


def score(params, base, cands, matches, seed):
    """Win rate of the policy against each candidate (theta, sizes, recipe)."""
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(0, len(cands), CHUNK):
            part = cands[i:i + CHUNK]
            path = os.path.join(tmp, "c.npz")
            clonegen.write(path, base, [c[0] for c in part], [c[1] for c in part], [c[2] for c in part])
            specs = clones.load(path, bots=[])
            first = len(specs) - len(part)
            for j in range(len(part)):
                r = run_matches(params, 200 + first + j, matches, seed + i + j)
                out.append(r["wins"] / r["matches"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--base", default="data/clones.npz")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cands", type=int, default=192)
    ap.add_argument("--mutants", type=int, default=64, help="children of the hardest, second round")
    ap.add_argument("--keep", type=int, default=32)
    ap.add_argument("--rand", type=int, default=16)
    ap.add_argument("--matches", type=int, default=100)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    z = np.load(args.model)
    params = {k: z[k] for k in z.files}
    d = np.load(args.base, allow_pickle=False)
    meta = json.loads(str(d["meta"]))
    arch = d["arch_theta"].astype(np.float64)
    rng = np.random.default_rng(args.seed)
    cands = [clonegen.sample(arch, meta["arch_sizes"], rng) for _ in range(args.cands)]
    wr = score(params, args.base, cands, args.matches, args.seed * 1000)
    order = np.argsort(wr)
    parents = [cands[i] for i in order[:max(1, args.mutants // 4)]]
    kids = [clonegen.mutate(*parents[k % len(parents)], rng) for k in range(args.mutants)]
    wr += score(params, args.base, kids, args.matches, args.seed * 1000 + 500)
    cands += kids
    wr = np.array(wr)
    order = np.argsort(wr)
    hard = list(order[:args.keep])
    rest = list(order[args.keep:])
    pick = hard + list(rng.choice(rest, min(args.rand, len(rest)), replace=False))
    recipes = [dict(cands[i][2], wr=round(float(wr[i]), 3)) for i in pick]
    clonegen.write(args.out, args.base, [cands[i][0] for i in pick], [cands[i][1] for i in pick], recipes,
                   {"model": args.model, "matches": args.matches})
    q = np.percentile(wr, [0, 5, 25, 50, 75])
    print(json.dumps({"out": args.out, "n": len(wr), "min": round(q[0], 3), "p5": round(q[1], 3),
                      "p25": round(q[2], 3), "median": round(q[3], 3), "p75": round(q[4], 3),
                      "first_round_min": round(float(min(wr[:args.cands])), 3),
                      "mutant_min": round(float(min(wr[args.cands:])), 3) if args.mutants else None,
                      "kept_hard_max": round(float(wr[hard[-1]]), 3)}))


if __name__ == "__main__":
    main()
