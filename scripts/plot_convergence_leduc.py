"""Convergence curves for vanilla CFR / MCCFR / CFR+ on Leduc Hold'em.

Iteration budgets are tuned per algorithm — Leduc is large enough that
the per-iteration cost differences become visible. CFR+ uses 1/3 of the
vanilla budget because each iteration performs two tree traversals.
Each algorithm is run under multiple seeds; the chart shows the mean
exploitability and a ±1-std band.

Run from project root:
    python -m scripts.plot_convergence_leduc
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Callable, List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from cfr.algorithms._state import CFRState, policy_table
from cfr.algorithms.cfr_plus import _cfr_plus
from cfr.algorithms.mccfr import _external_sampling
from cfr.algorithms.vanilla_cfr import _cfr
from cfr.evaluate.exploitability import exploitability
from cfr.games import leduc

LEDUC_P1_NASH_VALUE = -0.0856
DEFAULT_SEEDS = (42, 43, 44)  # 3 seeds — Leduc runs are minutes per algo per seed


def _checkpoints(total: int, num_points: int = 12) -> List[int]:
    start = max(500, total // num_points)
    return sorted(set(int(x) for x in np.logspace(np.log10(start), np.log10(total), num_points)))


def _trace(
    stepper: Callable, game, total: int, seed: int,
) -> List[Tuple[int, float]]:
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
            stepper(state, cards, it, rng)
        target = next_target
        trace.append((target, exploitability(game, policy_table(state))))
    return trace


def _trace_many(stepper, game, total: int, seeds):
    runs = [_trace(stepper, game, total, seed) for seed in seeds]
    xs = np.array([pt[0] for pt in runs[0]])
    ys = np.array([[pt[1] for pt in run] for run in runs])
    return xs, ys.mean(axis=0), ys.std(axis=0)


def main(out_path: Path, seeds) -> None:
    def vanilla_step(state, cards, it, rng):
        _cfr(leduc, state, "", cards, 1.0, 1.0)

    def mccfr_step(state, cards, it, rng):
        _external_sampling(leduc, state, "", cards, it % 2, rng)

    def cfr_plus_step(state, cards, it, rng):
        for traverser in (0, 1):
            _cfr_plus(leduc, state, "", cards, 1.0, 1.0, traverser, iteration=it + 1)

    runs = [
        ("Vanilla CFR", vanilla_step, 50_000),
        ("MCCFR (External Sampling)", mccfr_step, 200_000),
        ("CFR+", cfr_plus_step, 20_000),
    ]
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, fn, n in runs:
        print(f"\n=== {name} ({n} iter × {len(seeds)} seeds) ===")
        t0 = time.time()
        xs, mean, std = _trace_many(fn, leduc, n, seeds)
        dt = time.time() - t0
        ax.loglog(xs, mean, marker="o", markersize=3, label=f"{name} ({dt:.0f}s)")
        ax.fill_between(xs, np.maximum(mean - std, 1e-6), mean + std, alpha=0.2)
        print(f"  final expl mean = {mean[-1]:.4f} ± {std[-1]:.4f}"
              f" @ {xs[-1]} iters | wall {dt:.1f}s")

    ax.axhline(0.10, color="grey", linestyle="--", linewidth=0.8, label="expl = 0.10")
    ax.set_xlabel("iterations")
    ax.set_ylabel("exploitability (mean ± 1 std over %d seeds)" % len(seeds))
    ax.set_title("CFR family convergence on Leduc Hold'em")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    print(f"\nFigure saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/convergence_leduc.png"))
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=list(DEFAULT_SEEDS),
        help="Seeds to average over (default: 42-44; 3 seeds keep Leduc run under ~10 min).",
    )
    args = parser.parse_args()
    main(args.out, tuple(args.seeds))
