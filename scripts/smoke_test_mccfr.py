"""Smoke test: MCCFR External Sampling on Kuhn Poker.

Expected behaviour:
    - Exploitability decreases as iterations grow (noisier than vanilla
      due to sampled chance and opponent actions).
    - Game value for Player 1 approaches -1/18.
    - Learned average strategy is a Kuhn Nash equilibrium.

Run from project root:
    python -m scripts.smoke_test_mccfr 50000
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cfr.algorithms import mccfr
from cfr.algorithms._state import policy_table
from cfr.evaluate.exploitability import exploitability
from cfr.games import kuhn


def main(iterations: int = 50_000) -> None:
    print(f"Training External-Sampling MCCFR on Kuhn for {iterations} iters...")
    state = mccfr.train(kuhn, iterations=iterations, verbose=True)

    policy = policy_table(state)
    expl = exploitability(kuhn, policy)
    print(f"\nFinal exploitability: {expl:.6f}  (should approach 0)")

    print("\nLearned average strategy (action probs: pass, bet):")
    for info_set in sorted(policy.keys()):
        probs = policy[info_set]
        print(f"  {info_set:>10}  pass={probs[0]:.3f}  bet={probs[1]:.3f}")


if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 50_000
    main(iters)
