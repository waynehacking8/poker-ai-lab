"""Smoke test: Vanilla CFR on Leduc Hold'em.

Expected behaviour:
    - 528 information sets visited (264 per player).
    - Exploitability decreases as iterations grow.
    - Game value for Player 1 approaches the published Nash value
      of approximately -0.0856 chips (Lanctot 2013).
    - The published value reflects P1's first-actor disadvantage in
      the fixed-bet structure.

Run from project root:
    python -m scripts.smoke_test_leduc 50000
"""

from __future__ import annotations

import sys
import time

from cfr.algorithms import vanilla_cfr
from cfr.algorithms._state import policy_table
from cfr.evaluate.exploitability import exploitability, expected_game_value
from cfr.games import leduc


def main(iterations: int) -> None:
    t0 = time.time()
    state = vanilla_cfr.train(leduc, iterations=iterations, verbose=True, seed=42)
    train_time = time.time() - t0

    policy = policy_table(state)
    t0 = time.time()
    expl = exploitability(leduc, policy)
    expl_time = time.time() - t0

    game_value = expected_game_value(leduc, policy, policy)

    print()
    print(f"=== Leduc CFR — {iterations} iterations ===")
    print(f"info sets visited : {len(state.strategy_sum)} (expected 528)")
    print(f"training time     : {train_time:.1f}s")
    print(f"exploitability    : {expl:.4f} (computed in {expl_time:.2f}s)")
    print(f"game value P1     : {game_value:+.4f}  (Nash ≈ -0.0856)")


if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 20_000
    main(iters)
