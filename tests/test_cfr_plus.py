"""Convergence tests for CFR+ on Kuhn Poker.

CFR+ should converge markedly faster than vanilla CFR — Tammelin 2014
reports near-zero exploitability on Kuhn in ~100 iterations of full
enumeration. With chance sampling we use a modest 5000 iterations and
expect tight exploitability.
"""

from __future__ import annotations

import numpy as np
import pytest

from cfr.algorithms import cfr_plus, vanilla_cfr
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
    # Each iter performs two tree traversals (one per traverser); 8000
    # iters = 16000 traversals, comfortably below the threshold under
    # chance sampling.
    return cfr_plus.train(kuhn, iterations=8_000, seed=42)


def test_visits_every_info_set(trained_state):
    assert set(trained_state.strategy_sum.keys()) == EXPECTED_INFO_SETS


def test_policy_is_a_distribution(trained_state):
    policy = policy_table(trained_state)
    for probs in policy.values():
        assert float(probs.sum()) == pytest.approx(1.0, abs=1e-9)
        assert (probs >= 0).all()


def test_regrets_are_non_negative(trained_state):
    """RM+ floor: no stored regret should be negative."""
    for regrets in trained_state.regret_sum.values():
        assert (regrets >= 0).all()


def test_converges_below_threshold(trained_state):
    policy = policy_table(trained_state)
    assert exploitability(kuhn, policy) < 0.02


def test_game_value_near_analytical(trained_state):
    policy = policy_table(trained_state)
    value = expected_game_value(kuhn, policy, policy)
    assert value == pytest.approx(KUHN_GAME_VALUE, abs=0.015)


def test_seed_determinism():
    a = cfr_plus.train(kuhn, iterations=500, seed=123)
    b = cfr_plus.train(kuhn, iterations=500, seed=123)
    assert a.regret_sum.keys() == b.regret_sum.keys()
    for key in a.regret_sum:
        np.testing.assert_allclose(a.regret_sum[key], b.regret_sum[key])


def test_dominant_pure_actions(trained_state):
    policy = policy_table(trained_state)
    assert policy["J:b"][0] > 0.95
    assert policy["J:pb"][0] > 0.95
    assert policy["K:b"][1] > 0.95
    assert policy["K:pb"][1] > 0.95
    assert policy["K:p"][1] > 0.95
    assert policy["Q:"][0] > 0.95


def test_converges_faster_than_vanilla():
    """At equal iteration count, CFR+ should be no worse than vanilla CFR."""
    iters = 2_000
    cfr_plus_policy = policy_table(cfr_plus.train(kuhn, iterations=iters, seed=11))
    vanilla_policy = policy_table(vanilla_cfr.train(kuhn, iterations=iters, seed=11))
    cfr_plus_expl = exploitability(kuhn, cfr_plus_policy)
    vanilla_expl = exploitability(kuhn, vanilla_policy)
    assert cfr_plus_expl <= vanilla_expl
