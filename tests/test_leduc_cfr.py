"""Vanilla CFR convergence on Leduc Hold'em.

Verifies that, with the same algorithm we run on Kuhn:

  * Every reachable information set is visited.
  * Exploitability (via the two-pass best-response oracle) drops below a
    loose threshold.
  * The implied game value to Player 1 is close to the published Nash
    value of approximately -0.0856 chips (Lanctot 2013, OpenSpiel reference).

Leduc is enough bigger than Kuhn that we use 30k iterations rather than
Kuhn's 20k, and we accept a noisier exploitability threshold (0.15 vs.
0.02). Both numbers come from a calibration sweep (1k → 0.74,
5k → 0.35, 20k → 0.14, 30k → 0.10, 50k → 0.07) — 0.15 sits comfortably
above the 30k empirical value but well below the no-learning baseline.
"""

from __future__ import annotations

import pytest

from cfr.algorithms import vanilla_cfr
from cfr.algorithms._state import policy_table
from cfr.evaluate.exploitability import exploitability, expected_game_value
from cfr.games import leduc


# Published Nash game value for P1 in Leduc (Lanctot 2013, p. 19).
LEDUC_P1_NASH_VALUE = -0.0856


@pytest.fixture(scope="module")
def trained_state():
    return vanilla_cfr.train(leduc, iterations=30_000, seed=42)


def test_visits_every_info_set(trained_state):
    # 264 P0 info sets + 264 P1 info sets = 528 visited.
    assert len(trained_state.strategy_sum) == 528


def test_policy_is_a_distribution(trained_state):
    policy = policy_table(trained_state)
    for probs in policy.values():
        assert float(probs.sum()) == pytest.approx(1.0, abs=1e-9)
        assert (probs >= 0).all()


def test_converges_below_threshold(trained_state):
    policy = policy_table(trained_state)
    assert exploitability(leduc, policy) < 0.15


def test_game_value_near_published_nash(trained_state):
    policy = policy_table(trained_state)
    value = expected_game_value(leduc, policy, policy)
    # Wider abs tolerance than Kuhn — Leduc has a larger sampling envelope.
    assert value == pytest.approx(LEDUC_P1_NASH_VALUE, abs=0.02)
