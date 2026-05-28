"""Smoke test: CFR+ on Kuhn Poker.

Expected behaviour:
    - Exploitability decreases monotonically (RM+ removes vanilla CFR's
      sign-flipping warm-up).
    - Game value for Player 1 approaches -1/18.
    - Each "iteration" performs two passes (one per traverser), so
      compute per iter is double vanilla / MCCFR.

Run from project root:
    python -m scripts.smoke_test_cfr_plus 5000
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cfr.algorithms import cfr_plus
from cfr.algorithms._state import policy_table
from cfr.evaluate.exploitability import exploitability
from cfr.games import kuhn


def main(iterations: int = 5_000) -> None:
    print(f"Training CFR+ on Kuhn for {iterations} iters "
          f"(= {iterations * 2} tree traversals)...")
    state = cfr_plus.train(kuhn, iterations=iterations, verbose=True)

    policy = policy_table(state)
    expl = exploitability(kuhn, policy)
    print(f"\nFinal exploitability: {expl:.6f}  (should approach 0)")

    print("\nLearned average strategy (action probs: pass, bet):")
    for info_set in sorted(policy.keys()):
        probs = policy[info_set]
        print(f"  {info_set:>10}  pass={probs[0]:.3f}  bet={probs[1]:.3f}")


if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 5_000
    main(iters)
