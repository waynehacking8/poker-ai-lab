"""Convergence curves for vanilla CFR / MCCFR / CFR+ on Leduc Hold'em.

Iteration budgets are tuned per algorithm — Leduc is large enough that
the per-iteration cost differences become visible. CFR+ uses 1/3 of the
vanilla budget because each iteration performs two tree traversals.

Run from project root:
    python -m scripts.plot_convergence_leduc
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
from cfr.games import leduc

LEDUC_P1_NASH_VALUE = -0.0856


def _checkpoints(total: int, num_points: int = 12) -> List[int]:
    start = max(500, total // num_points)
    return sorted(set(int(x) for x in np.logspace(np.log10(start), np.log10(total), num_points)))


def _trace(stepper, game, total: int, seed: int, *, two_pass: bool = False) -> List[Tuple[int, float]]:
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
        expl = exploitability(game, policy_table(state))
        trace.append((target, expl))
        print(f"  ... {target:>7} iter | expl = {expl:.4f}")
    return trace


def main(out_path: Path) -> None:
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
        print(f"\n=== {name} ({n} iter) ===")
        t0 = time.time()
        trace = _trace(fn, leduc, n, seed=42)
        dt = time.time() - t0
        xs, ys = zip(*trace)
        ax.loglog(xs, ys, marker="o", markersize=3, label=f"{name} ({dt:.0f}s)")

    ax.axhline(0.10, color="grey", linestyle="--", linewidth=0.8, label="expl = 0.10")
    ax.set_xlabel("iterations")
    ax.set_ylabel("exploitability")
    ax.set_title("CFR family convergence on Leduc Hold'em (seed=42)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    print(f"\nFigure saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/convergence_leduc.png"))
    args = parser.parse_args()
    main(args.out)
