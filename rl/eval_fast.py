"""Fast evaluation in the C engine: seat-swapped matches per opponent with Wilson CIs.

    python -m rl.eval_fast --model ckpt/run1/latest.npz --matches 400 [--clones data/clones.npz]
"""

from __future__ import annotations

import argparse
import json

import numpy as np

import rl  # noqa: F401
from rl import fastenv
from rl.fastenv import BASELINE_IDS, EXT, Pool
from rl.train import np_forward, sample
from holdem.arena import wilson


def run_matches(params, opp_ctrl, matches, seed=1, temperature=1.0, envs=128, opp_params=None):
    """Play ``matches`` matches (half per seat, same deals in each seat pair); returns a result dict."""
    rng = np.random.default_rng(seed)
    E = min(envs, matches)
    pool = Pool(E)
    jobs = [(seed * 100003 + k // 2, k % 2) for k in range(matches)]  # (deal seed, hero seat)
    nxt = 0
    res = []
    slot = [None] * E

    def start(i):
        nonlocal nxt
        if nxt >= len(jobs):
            slot[i] = None
            return
        sd, hero = jobs[nxt]
        nxt += 1
        ctrl = [EXT, EXT]
        ctrl[1 - hero] = opp_ctrl if opp_params is None else EXT + 1
        pool.reset(i, sd, ctrl[0], ctrl[1], hero)
        slot[i] = hero

    for i in range(E):
        start(i)
    pols = [None, params, opp_params]
    while any(s is not None for s in slot):
        act = [i for i in range(E) if slot[i] is not None]
        idx = np.array(act, dtype=np.int32)
        obs, mask, meta, _ = pool.obs(idx)
        acts = np.zeros(len(idx), dtype=np.int32)
        for sl in np.unique(meta[:, 1]):
            rows = np.nonzero(meta[:, 1] == sl)[0]
            p = params if sl == EXT else opp_params
            lg, _ = np_forward(p, obs[rows], value=False)
            a, _ = sample(lg, mask[rows], rng, greedy=temperature <= 0) if sl == EXT and temperature <= 0 \
                else sample(lg / (temperature if sl == EXT else 1.0), mask[rows], rng)
            acts[rows] = a
        pool.step(idx, acts)
        info = pool.info(idx)
        for j, i in enumerate(act):
            if info[j, 0] > 0:
                res.append((int(info[j, 3] == 1.0), int(info[j, 2])))
                start(i)
    wins = sum(w for w, _ in res)
    lo, hi = wilson(wins, len(res))
    won_h = [h for w, h in res if w]
    return {"matches": len(res), "wins": wins, "win_rate": round(wins / len(res), 3),
            "ci95": [round(lo, 3), round(hi, 3)],
            "hands_per_win": round(float(np.mean(won_h)), 1) if won_h else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--matches", type=int, default=400)
    ap.add_argument("--clones", default=None)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--only", default=None, help="comma separated opponent names")
    args = ap.parse_args()
    z = np.load(args.model)
    params = {k: z[k] for k in z.files}
    opps = {k: v for k, v in BASELINE_IDS.items()}
    if args.clones:
        from rl import clones
        for k, spec in enumerate(clones.load(args.clones)):
            opps[spec] = 200 + k
    if args.only:
        opps = {k: opps[k] for k in args.only.split(",")}
    for name, cid in opps.items():
        out = run_matches(params, cid, args.matches, args.seed, args.temperature)
        out["opponent"] = name
        print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
