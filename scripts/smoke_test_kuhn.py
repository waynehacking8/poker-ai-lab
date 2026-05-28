"""Smoke test: vanilla CFR on Kuhn Poker.

Expected behaviour:
    - Exploitability → 0 as iterations grow.
    - Game value for Player 1 ≈ -1/18 ≈ -0.0556.
    - At equilibrium, P1 J bets with α ∈ [0, 1/3], P1 K bets with 3α.

Run from project root:
    python -m scripts.smoke_test_kuhn
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cfr.algorithms import vanilla_cfr
from cfr.evaluate.exploitability import exploitability
from cfr.games import kuhn


def main(iterations: int = 5000) -> None:
    print(f"Training vanilla CFR on Kuhn Poker for {iterations} iters...")
    state = vanilla_cfr.train(kuhn, iterations=iterations, verbose=True)

    policy = vanilla_cfr.policy_table(state)
    expl = exploitability(kuhn, policy)
    print(f"\nFinal exploitability: {expl:.6f}  (should approach 0)")

    print("\nLearned average strategy (action probs: pass, bet):")
    for info_set in sorted(policy.keys()):
        probs = policy[info_set]
        print(f"  {info_set:>10}  pass={probs[0]:.3f}  bet={probs[1]:.3f}")


if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    main(iters)
