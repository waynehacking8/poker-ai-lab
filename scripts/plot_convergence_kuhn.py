"""Convergence curves for vanilla CFR / MCCFR / CFR+ on Kuhn Poker.

Drives each algorithm's per-iteration primitive directly so we can probe
exploitability at evenly-spaced checkpoints without retraining from
scratch each time. Writes a log-log plot to ``results/convergence_kuhn.png``.

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
from cfr.algorithms.cfr_plus import _cfr_plus
from cfr.algorithms.mccfr import _external_sampling
from cfr.algorithms.vanilla_cfr import _cfr
from cfr.evaluate.exploitability import exploitability
from cfr.games import kuhn


def _checkpoints(total: int, num_points: int = 20) -> List[int]:
    """Log-spaced iteration checkpoints from ``total / num_points`` to ``total``."""
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
        expl = exploitability(game, policy_table(state))
        trace.append((target, expl))
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
        expl = exploitability(game, policy_table(state))
        trace.append((target, expl))
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
                _cfr_plus(game, state, "", cards, 1.0, 1.0, traverser, iteration=it + 1)
        target = next_target
        expl = exploitability(game, policy_table(state))
        trace.append((target, expl))
    return trace


def main(iters: int, out_path: Path) -> None:
    runs = {
        "Vanilla CFR": (_trace_vanilla, iters),
        "MCCFR (External Sampling)": (_trace_mccfr, iters),
        "CFR+": (_trace_cfr_plus, iters // 4),
    }
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, (fn, n) in runs.items():
        t0 = time.time()
        trace = fn(kuhn, n, seed=42)
        dt = time.time() - t0
        xs, ys = zip(*trace)
        ax.loglog(xs, ys, marker="o", markersize=3, label=f"{name} ({dt:.0f}s)")
        print(f"{name:<28} | final expl = {ys[-1]:.4f} @ {xs[-1]} iters | {dt:.1f}s")

    ax.set_xlabel("iterations")
    ax.set_ylabel("exploitability")
    ax.set_title("CFR family convergence on Kuhn Poker (seed=42)")
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
    args = parser.parse_args()
    main(args.iters, args.out)
