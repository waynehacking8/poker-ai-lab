"""Debug: random-deal CFR variant to isolate whether the enumeration is buggy."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import random
import numpy as np

from cfr.algorithms.vanilla_cfr import CFRState, _cfr_recurse, policy_table
from cfr.evaluate.exploitability import exploitability
from cfr.games import kuhn


def train_random(iterations: int) -> CFRState:
    state = CFRState(num_actions=2)
    deals = kuhn.all_deals()
    rng = random.Random(0)
    for it in range(iterations):
        cards = rng.choice(deals)
        _cfr_recurse(kuhn, state, "", cards, np.ones(2))
        if (it + 1) % max(1, iterations // 10) == 0:
            policy = policy_table(state)
            expl = exploitability(kuhn, policy)
            print(f"iter {it + 1:>6} | exploitability = {expl:.5f}")
    return state


if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    state = train_random(iters)
    policy = policy_table(state)
    print("\nFinal strategy:")
    for k in sorted(policy):
        p = policy[k]
        print(f"  {k:>10}  pass={p[0]:.3f}  bet={p[1]:.3f}")
