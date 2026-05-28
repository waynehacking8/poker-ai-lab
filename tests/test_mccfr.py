"""Convergence tests for MCCFR (External Sampling) on Kuhn Poker.

External Sampling has higher per-iteration variance than vanilla CFR
because chance and the opponent's actions are sampled rather than
enumerated. We compensate by running more iterations and loosening
the exploitability / game-value thresholds.
"""

from __future__ import annotations

import numpy as np
import pytest

from cfr.algorithms import mccfr
from cfr.algorithms._state import policy_table
from cfr.evaluate.exploitability import exploitability, expected_game_value
from cfr.games import kuhn

KUHN_GAME_VALUE = -1.0 / 18.0
EXPECTED_INFO_SETS = {
    "J:", "Q:", "K:",
    "J:pb", "Q:pb", "K:pb",
    "J:p", "Q:p", "K:p",
    "J:b", "Q:b", "K:b",
}


@pytest.fixture(scope="module")
def trained_state():
    return mccfr.train(kuhn, iterations=50_000, seed=42)


def test_visits_every_info_set(trained_state):
    assert set(trained_state.strategy_sum.keys()) == EXPECTED_INFO_SETS


def test_policy_is_a_distribution(trained_state):
    policy = policy_table(trained_state)
    for probs in policy.values():
        assert float(probs.sum()) == pytest.approx(1.0, abs=1e-9)
        assert (probs >= 0).all()


def test_converges_below_threshold(trained_state):
    policy = policy_table(trained_state)
    assert exploitability(kuhn, policy) < 0.05


def test_game_value_near_analytical(trained_state):
    policy = policy_table(trained_state)
    value = expected_game_value(kuhn, policy, policy)
    assert value == pytest.approx(KUHN_GAME_VALUE, abs=0.025)


def test_seed_determinism():
    a = mccfr.train(kuhn, iterations=500, seed=123)
    b = mccfr.train(kuhn, iterations=500, seed=123)
    assert a.regret_sum.keys() == b.regret_sum.keys()
    for key in a.regret_sum:
        np.testing.assert_allclose(a.regret_sum[key], b.regret_sum[key])


def test_dominant_pure_actions(trained_state):
    policy = policy_table(trained_state)
    assert policy["J:b"][0] > 0.9
    assert policy["J:pb"][0] > 0.9
    assert policy["K:b"][1] > 0.9
    assert policy["K:pb"][1] > 0.9
    assert policy["K:p"][1] > 0.9
    assert policy["Q:"][0] > 0.9
