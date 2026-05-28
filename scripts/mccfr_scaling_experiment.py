"""Experiment: at what deck size does MCCFR start beating enum CFR+?

For each N in a sweep, run both algorithms with a fixed **wall-time
budget** on N-card Kuhn and record the exploitability reached. The
crossover N — where MCCFR's final expl beats enum CFR+'s final expl —
is where sampling stops being a liability and starts being a feature.

Theory:
  - Per-enum-iter cost grows as N(N-1) × tree_size  (quadratic in N)
  - Per-MCCFR-iter cost is independent of N         (one path)
  - At small N, enum's per-iter cost is so cheap that its O(1/T)
    convergence (CFR+ super-√T) dominates. At large N, enum becomes
    expensive per iteration and MCCFR's cheap-but-noisy iters add up
    faster.

Outputs:
  reports/mccfr-scaling.json   raw measurements
  reports/mccfr-scaling.png    plot of final expl vs N for both algos
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from cfr.algorithms._state import CFRState, policy_table
from cfr.algorithms.cfr_plus import _apply_rm_plus_floor, _cfr_plus
from cfr.algorithms.mccfr import _external_sampling
from cfr.evaluate.exploitability import exploitability
from cfr.games import big_kuhn


def _run_enum_cfr_plus(game, wall_budget: float) -> Dict:
    state = CFRState()
    deals = game.all_deals()
    iter_count = 0
    t0 = time.time()
    while time.time() - t0 < wall_budget:
        for traverser in (0, 1):
            cache: dict = {}
            for cards in deals:
                _cfr_plus(
                    game, state, "", cards, 1.0, 1.0,
                    traverser, iteration=iter_count + 1, strategy_cache=cache,
                )
            _apply_rm_plus_floor(state)
        iter_count += 1
    dt = time.time() - t0
    expl = exploitability(game, policy_table(state))
    return {"iters": iter_count, "wall": dt, "expl": expl}


def _run_mccfr(game, wall_budget: float, seed: int = 42) -> Dict:
    state = CFRState()
    deals = game.all_deals()
    rng = np.random.default_rng(seed)
    deal_idx = np.arange(len(deals))
    iter_count = 0
    t0 = time.time()
    while time.time() - t0 < wall_budget:
        # Do batches of 1000 MCCFR iters between time checks so the
        # time-check overhead doesn't dominate the inner loop.
        for _ in range(1000):
            cards = deals[int(rng.choice(deal_idx))]
            _external_sampling(game, state, "", cards, iter_count % 2, rng)
            iter_count += 1
        if time.time() - t0 >= wall_budget:
            break
    dt = time.time() - t0
    expl = exploitability(game, policy_table(state))
    return {"iters": iter_count, "wall": dt, "expl": expl}


def main(ns_to_test: List[int], wall_budget: float, out_dir: Path) -> None:
    results = []
    for n in ns_to_test:
        game = big_kuhn.make_game(n)
        deals_count = len(game.all_deals())
        print(f"\n=== N = {n} cards ({deals_count} deals) — {wall_budget:.0f}s budget each ===")

        enum_result = _run_enum_cfr_plus(game, wall_budget)
        print(f"  Enum CFR+ : {enum_result['iters']:>8} iter | wall {enum_result['wall']:5.1f}s "
              f"| expl {enum_result['expl']:.6f}")

        mc_result = _run_mccfr(game, wall_budget)
        print(f"  MCCFR ES  : {mc_result['iters']:>8} iter | wall {mc_result['wall']:5.1f}s "
              f"| expl {mc_result['expl']:.6f}")

        winner = "MCCFR" if mc_result["expl"] < enum_result["expl"] else "Enum CFR+"
        ratio = enum_result["expl"] / max(mc_result["expl"], 1e-12)
        print(f"  Winner    : {winner}  (enum/MCCFR expl ratio = {ratio:.2f})")

        results.append({
            "N": n,
            "deals": deals_count,
            "enum_cfr_plus": enum_result,
            "mccfr_es": mc_result,
            "winner": winner,
            "enum_to_mccfr_expl_ratio": ratio,
        })

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "mccfr-scaling.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nRaw results saved: {out_dir / 'mccfr-scaling.json'}")

    # Plot.
    ns = [r["N"] for r in results]
    enum_expls = [r["enum_cfr_plus"]["expl"] for r in results]
    mc_expls = [r["mccfr_es"]["expl"] for r in results]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.loglog(ns, enum_expls, marker="o", markersize=6, linewidth=2,
              label="Enum CFR+ (per-iter cost grows as N²)")
    ax.loglog(ns, mc_expls, marker="^", markersize=6, linewidth=2,
              label="MCCFR External Sampling (per-iter cost constant)")
    ax.set_xlabel("N (deck size)")
    ax.set_ylabel(f"final exploitability after {wall_budget:.0f} s wall time")
    ax.set_title(
        "MCCFR crossover on N-card Kuhn\n"
        "Lower is better. Where the MCCFR line dips below the enum line, "
        "MCCFR wins."
    )
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out_path = out_dir / "mccfr-scaling.png"
    fig.savefig(out_path, dpi=120)
    print(f"Plot saved:        {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ns", type=int, nargs="+",
                        default=[3, 13, 30, 60, 120, 200],
                        help="Deck sizes to sweep")
    parser.add_argument("--budget", type=float, default=20.0,
                        help="Wall-time budget per algorithm per N (seconds)")
    parser.add_argument("--out-dir", type=Path, default=Path("reports"))
    args = parser.parse_args()
    main(args.ns, args.budget, args.out_dir)
