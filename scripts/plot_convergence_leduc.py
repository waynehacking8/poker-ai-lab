"""Convergence curves for the three canonical CFR family algorithms on Leduc.

Plots vanilla CFR, CFR+, and MCCFR (External Sampling) in their
**canonical forms**:

  - Vanilla CFR and CFR+ use full chance enumeration (the form
    presented in Zinkevich 2007 / Tammelin 2014 and the default in
    OpenSpiel's CFRSolver / CFRPlusSolver classes).
  - MCCFR is by definition a sampling method (Lanctot 2009).

This yields the literature-consistent algorithm ordering on small
games like Leduc:  CFR+ enum < vanilla enum < MCCFR.

The chance-sampling variants of vanilla CFR and CFR+ are also provided
in the package (`vanilla_cfr.train`, `cfr_plus.train`) but they are
practical alternatives for memory-constrained settings, not canonical
algorithms — they are not plotted here to keep the comparison clean.

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
from cfr.algorithms.cfr_plus import _apply_rm_plus_floor, _cfr_plus
from cfr.algorithms.mccfr import _external_sampling
from cfr.algorithms.vanilla_cfr import _cfr
from cfr.evaluate.exploitability import exploitability
from cfr.games import leduc

LEDUC_P1_NASH_VALUE = -0.0856


def _log_checkpoints(start: int, total: int, num_points: int) -> List[int]:
    return sorted(
        set(int(x) for x in np.logspace(np.log10(start), np.log10(total), num_points))
    )


def _trace_vanilla_enum(total: int) -> List[Tuple[int, float]]:
    state = CFRState()
    deals = leduc.all_deals()
    chance_prob = 1.0 / len(deals)
    points = _log_checkpoints(50, total, 8)
    trace: List[Tuple[int, float]] = []
    target = 0
    for next_target in points:
        for _ in range(next_target - target):
            for cards in deals:
                _cfr(leduc, state, "", cards, chance_prob, chance_prob)
        target = next_target
        trace.append((target, exploitability(leduc, policy_table(state))))
    return trace


def _trace_cfr_plus_enum(total: int) -> List[Tuple[int, float]]:
    state = CFRState()
    deals = leduc.all_deals()
    points = _log_checkpoints(50, total, 8)
    trace: List[Tuple[int, float]] = []
    target = 0
    for next_target in points:
        for it in range(target, next_target):
            for traverser in (0, 1):
                strategy_cache: dict = {}
                for cards in deals:
                    _cfr_plus(
                        leduc, state, "", cards, 1.0, 1.0,
                        traverser, iteration=it + 1, strategy_cache=strategy_cache,
                    )
                _apply_rm_plus_floor(state)
        target = next_target
        trace.append((target, exploitability(leduc, policy_table(state))))
    return trace


def _trace_mccfr(total: int, seed: int) -> List[Tuple[int, float]]:
    state = CFRState()
    deals = leduc.all_deals()
    rng = np.random.default_rng(seed)
    deal_idx = np.arange(len(deals))
    points = _log_checkpoints(max(1000, total // 100), total, 8)
    trace: List[Tuple[int, float]] = []
    target = 0
    for next_target in points:
        for it in range(target, next_target):
            cards = deals[int(rng.choice(deal_idx))]
            _external_sampling(leduc, state, "", cards, it % 2, rng)
        target = next_target
        trace.append((target, exploitability(leduc, policy_table(state))))
    return trace


def main(out_path: Path, mccfr_seeds) -> None:
    fig, ax = plt.subplots(figsize=(8, 5.5))

    t0 = time.time()
    vanilla_trace = _trace_vanilla_enum(total=1000)
    print(f"vanilla enum  | wall {time.time() - t0:5.1f}s | final expl {vanilla_trace[-1][1]:.4f}")
    xs_v, ys_v = zip(*vanilla_trace)
    ax.loglog(xs_v, ys_v, marker="o", markersize=4,
              label=f"Vanilla CFR (full enum)  final expl={ys_v[-1]:.4f}")

    t0 = time.time()
    plus_trace = _trace_cfr_plus_enum(total=1000)
    print(f"CFR+ enum     | wall {time.time() - t0:5.1f}s | final expl {plus_trace[-1][1]:.4f}")
    xs_p, ys_p = zip(*plus_trace)
    ax.loglog(xs_p, ys_p, marker="s", markersize=4,
              label=f"CFR+ (full enum)  final expl={ys_p[-1]:.4f}")

    # MCCFR multi-seed band.
    print(f"MCCFR ES (mean of {len(mccfr_seeds)} seeds):")
    mccfr_runs = []
    for s in mccfr_seeds:
        t0 = time.time()
        tr = _trace_mccfr(total=200_000, seed=s)
        print(f"  seed {s} | wall {time.time() - t0:5.1f}s | final expl {tr[-1][1]:.4f}")
        mccfr_runs.append(tr)
    xs_m = np.array([pt[0] for pt in mccfr_runs[0]])
    ys_m = np.array([[pt[1] for pt in run] for run in mccfr_runs])
    mean = ys_m.mean(axis=0)
    std = ys_m.std(axis=0)
    ax.loglog(xs_m, mean, marker="^", markersize=4,
              label=f"MCCFR (External Sampling)  final expl≈{mean[-1]:.3f}")
    ax.fill_between(xs_m, np.maximum(mean - std, 1e-6), mean + std, alpha=0.2)

    ax.set_xlabel("iterations  (1 iter = 1 full pass for enum, 1 deal sample for MCCFR)")
    ax.set_ylabel("exploitability (chips per game)")
    ax.set_title(
        "Leduc Hold'em — canonical CFR family convergence\n"
        "CFR+ enum < vanilla CFR enum < MCCFR (per literature, small game)"
    )
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    print(f"\nFigure saved: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("results/convergence_leduc.png"))
    parser.add_argument("--mccfr-seeds", type=int, nargs="+", default=[42, 43, 44])
    args = parser.parse_args()
    main(args.out, tuple(args.mccfr_seeds))
