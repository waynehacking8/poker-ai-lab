"""MCCFR (External Sampling) convergence on Leduc Hold'em.

Per-iteration variance is higher than vanilla CFR because chance, the
opponent's actions, and (for non-traverser nodes) the traverser's hand
are all sampled rather than enumerated. The trade-off pays off on large
games where the constant factor of tree traversal dominates; on Leduc
both effects are visible — wall time per iteration is small, but more
iterations are needed for a comparable exploitability.

Threshold calibration (seed=42):

    iters      expl       wall time
       5k     1.55         0.6 s
      20k     0.87         1.7 s
      50k     0.54         4.1 s
     100k     0.51         8.3 s
     200k     0.47        16.5 s
     500k     0.28        41.8 s

We pin the test at 200k iterations / expl < 0.6 — comfortably above the
empirical value yet well below the uniform-policy baseline (~3.0 chips).
The expected-value tolerance is similarly loose because MCCFR's
last-iterate noise on Leduc is non-trivial at this iteration count.
"""

from __future__ import annotations

import pytest

from cfr.algorithms import mccfr
from cfr.algorithms._state import policy_table
from cfr.evaluate.exploitability import exploitability, expected_game_value
from cfr.games import leduc

LEDUC_P1_NASH_VALUE = -0.0856


@pytest.fixture(scope="module")
def trained_state():
    return mccfr.train(leduc, iterations=200_000, seed=42)


def test_visits_every_info_set(trained_state):
    # 264 + 264 = 528 information sets total across both players.
    assert len(trained_state.strategy_sum) == 528


def test_policy_is_a_distribution(trained_state):
    policy = policy_table(trained_state)
    for probs in policy.values():
        assert float(probs.sum()) == pytest.approx(1.0, abs=1e-9)
        assert (probs >= 0).all()


def test_converges_below_threshold(trained_state):
    policy = policy_table(trained_state)
    assert exploitability(leduc, policy) < 0.6


def test_game_value_near_published_nash(trained_state):
    policy = policy_table(trained_state)
    value = expected_game_value(leduc, policy, policy)
    assert value == pytest.approx(LEDUC_P1_NASH_VALUE, abs=0.04)
