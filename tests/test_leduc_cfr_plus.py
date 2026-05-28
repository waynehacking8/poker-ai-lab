"""CFR+ convergence on Leduc Hold'em.

Each iteration performs two tree traversals (one per traverser), so the
work budget at ``N`` iterations is ``2N`` traversals. Tammelin 2014's
original CFR+ formulation enumerates chance; this implementation
samples one deal per iteration for consistency with the rest of the
package, which pushes more of the convergence cost onto iteration count.

Threshold calibration (seed=42):

    iters     traversals     expl       wall time
       1k        2 000       0.71        0.9 s
       3k        6 000       0.43        2.6 s
       8k       16 000       0.23        7.0 s
      20k       40 000       0.15       18 s
      50k      100 000       0.11       45 s

We pin the test at 20k iterations / expl < 0.20.
"""

from __future__ import annotations

import numpy as np
import pytest

from cfr.algorithms import cfr_plus
from cfr.algorithms._state import policy_table
from cfr.evaluate.exploitability import exploitability, expected_game_value
from cfr.games import leduc

LEDUC_P1_NASH_VALUE = -0.0856


@pytest.fixture(scope="module")
def trained_state():
    return cfr_plus.train(leduc, iterations=20_000, seed=42)


def test_visits_every_info_set(trained_state):
    assert len(trained_state.strategy_sum) == 528


def test_policy_is_a_distribution(trained_state):
    policy = policy_table(trained_state)
    for probs in policy.values():
        assert float(probs.sum()) == pytest.approx(1.0, abs=1e-9)
        assert (probs >= 0).all()


def test_regrets_are_non_negative(trained_state):
    """RM+ floor: no stored regret may be negative on any info set."""
    for regrets in trained_state.regret_sum.values():
        assert (regrets >= 0).all()


def test_converges_below_threshold(trained_state):
    policy = policy_table(trained_state)
    assert exploitability(leduc, policy) < 0.20


def test_game_value_near_published_nash(trained_state):
    policy = policy_table(trained_state)
    value = expected_game_value(leduc, policy, policy)
    assert value == pytest.approx(LEDUC_P1_NASH_VALUE, abs=0.02)


def test_seed_determinism():
    a = cfr_plus.train(leduc, iterations=500, seed=123)
    b = cfr_plus.train(leduc, iterations=500, seed=123)
    assert a.regret_sum.keys() == b.regret_sum.keys()
    for key in a.regret_sum:
        np.testing.assert_allclose(a.regret_sum[key], b.regret_sum[key])
