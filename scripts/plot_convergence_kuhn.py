"""Convergence curves for vanilla CFR / MCCFR / CFR+ on Kuhn Poker.

Drives each algorithm's per-iteration primitive directly so we can probe
exploitability at evenly-spaced checkpoints without retraining from
scratch each time. Runs each algorithm under multiple seeds and plots
the mean ± 1 std band on a log-log axis to ``results/convergence_kuhn.png``.

Run from project root:
    python -m scripts.plot_convergence_kuhn
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from cfr.algorithms._state import CFRState, policy_table
from cfr.algorithms.cfr_plus import _apply_rm_plus_floor, _cfr_plus
from cfr.algorithms.mccfr import _external_sampling
from cfr.algorithms.vanilla_cfr import _cfr
from cfr.evaluate.exploitability import exploitability
from cfr.games import kuhn

DEFAULT_SEEDS = (42, 43, 44, 45, 46)


def _checkpoints(total: int, num_points: int = 20) -> List[int]:
    return sorted(set(int(x) for x in np.logspace(2, np.log10(total), num_points)))


def _trace_vanilla(game, total: int, seed: int) -> List[Tuple[int, float]]:
    state = CFRState()
    deals = game.all_deals()
    rng = np.random.default_rng(seed)
    deal_idx = np.arange(len(deals))
    points = _checkpoints(total)
    trace: List[Tuple[int, float]] = []
    target = 0
    for next_target in points:
        for _ in range(next_target - target):
            cards = deals[int(rng.choice(deal_idx))]
            _cfr(game, state, "", cards, 1.0, 1.0)
        target = next_target
        trace.append((target, exploitability(game, policy_table(state))))
    return trace


def _trace_mccfr(game, total: int, seed: int) -> List[Tuple[int, float]]:
    state = CFRState()
    deals = game.all_deals()
    rng = np.random.default_rng(seed)
    deal_idx = np.arange(len(deals))
    points = _checkpoints(total)
    trace: List[Tuple[int, float]] = []
    target = 0
    for next_target in points:
        for it in range(target, next_target):
            cards = deals[int(rng.choice(deal_idx))]
            _external_sampling(game, state, "", cards, it % 2, rng)
        target = next_target
        trace.append((target, exploitability(game, policy_table(state))))
    return trace


def _trace_cfr_plus(game, total: int, seed: int) -> List[Tuple[int, float]]:
    state = CFRState()
    deals = game.all_deals()
    rng = np.random.default_rng(seed)
    deal_idx = np.arange(len(deals))
    points = _checkpoints(total)
    trace: List[Tuple[int, float]] = []
    target = 0
    for next_target in points:
        for it in range(target, next_target):
            cards = deals[int(rng.choice(deal_idx))]
            for traverser in (0, 1):
                strategy_cache: dict = {}
                _cfr_plus(
                    game, state, "", cards, 1.0, 1.0,
                    traverser, iteration=it + 1, strategy_cache=strategy_cache,
                )
                _apply_rm_plus_floor(state)
        target = next_target
        trace.append((target, exploitability(game, policy_table(state))))
    return trace


def _trace_many(trace_fn, game, total: int, seeds):
    """Run ``trace_fn`` under each seed; return (xs, mean, std) over checkpoints."""
    runs = [trace_fn(game, total, seed) for seed in seeds]
    xs = np.array([pt[0] for pt in runs[0]])
    ys = np.array([[pt[1] for pt in run] for run in runs])
    return xs, ys.mean(axis=0), ys.std(axis=0)


def main(iters: int, out_path: Path, seeds) -> None:
    runs = {
        "Vanilla CFR": (_trace_vanilla, iters),
        "MCCFR (External Sampling)": (_trace_mccfr, iters),
        "CFR+": (_trace_cfr_plus, iters // 4),
    }
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, (fn, n) in runs.items():
        t0 = time.time()
        xs, mean, std = _trace_many(fn, kuhn, n, seeds)
        dt = time.time() - t0
        ax.loglog(xs, mean, marker="o", markersize=3, label=f"{name} ({dt:.0f}s)")
        ax.fill_between(xs, np.maximum(mean - std, 1e-6), mean + std, alpha=0.2)
        print(f"{name:<28} | final expl mean = {mean[-1]:.4f} ± {std[-1]:.4f}"
              f" @ {xs[-1]} iters | {dt:.1f}s | {len(seeds)} seeds")

    ax.set_xlabel("iterations")
    ax.set_ylabel("exploitability (mean ± 1 std over %d seeds)" % len(seeds))
    ax.set_title("CFR family convergence on Kuhn Poker")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    print(f"\nFigure saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters", type=int, default=20_000)
    parser.add_argument("--out", type=Path, default=Path("results/convergence_kuhn.png"))
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=list(DEFAULT_SEEDS),
        help="Seeds to average over (default: 42-46).",
    )
    args = parser.parse_args()
    main(args.iters, args.out, tuple(args.seeds))
