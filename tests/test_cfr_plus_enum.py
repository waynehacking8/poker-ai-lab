"""Full-enumeration CFR+ — Tammelin 2014 original setup.

Tests both Kuhn and Leduc. Per-iteration cost is higher than the
chance-sampling variant (every deal is enumerated each iteration), but
the algorithm is **deterministic** — no RNG anywhere in the path — and
convergence per iteration is much faster.

Calibration sweep (seed irrelevant, deterministic):

  Kuhn:
       50 iter |  0.01 s | expl 0.043
      200 iter |  0.03 s | expl 0.021
     1000 iter |  0.15 s | expl 0.010

  Leduc:
       50 iter |   5.0 s | expl 0.33 | val -0.080
      200 iter |  20   s | expl 0.21 | val -0.074
     1000 iter | 103   s | expl 0.14 | val -0.076

Kuhn test pinned at 200 iter / expl < 0.05.
Leduc test pinned at 200 iter / expl < 0.30 (marked slow).
"""

from __future__ import annotations

import pytest

from cfr.algorithms import cfr_plus
from cfr.algorithms._state import policy_table
from cfr.evaluate.exploitability import exploitability, expected_game_value
from cfr.games import kuhn, leduc

KUHN_GAME_VALUE = -1.0 / 18.0
LEDUC_P1_NASH_VALUE = -0.0856


# ---------------------------------------------------------------------------
# Kuhn
# ---------------------------------------------------------------------------


def test_kuhn_enum_visits_every_info_set():
    state = cfr_plus.train_enumeration(kuhn, iterations=100)
    assert len(state.strategy_sum) == 12


def test_kuhn_enum_regrets_non_negative():
    state = cfr_plus.train_enumeration(kuhn, iterations=100)
    for regrets in state.regret_sum.values():
        assert (regrets >= 0).all()


def test_kuhn_enum_converges():
    state = cfr_plus.train_enumeration(kuhn, iterations=200)
    policy = policy_table(state)
    assert exploitability(kuhn, policy) < 0.05


def test_kuhn_enum_is_deterministic():
    """No RNG — two runs at the same iteration count are bit-identical."""
    a = cfr_plus.train_enumeration(kuhn, iterations=200)
    b = cfr_plus.train_enumeration(kuhn, iterations=200)
    assert a.regret_sum.keys() == b.regret_sum.keys()
    for key in a.regret_sum:
        # Equality, not approx — no RNG means no float drift between runs.
        assert (a.regret_sum[key] == b.regret_sum[key]).all()


def test_kuhn_enum_game_value_near_analytical():
    state = cfr_plus.train_enumeration(kuhn, iterations=200)
    policy = policy_table(state)
    value = expected_game_value(kuhn, policy, policy)
    assert value == pytest.approx(KUHN_GAME_VALUE, abs=0.02)


# ---------------------------------------------------------------------------
# Leduc — marked slow because each iteration is ~100ms.
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_leduc_enum_converges():
    state = cfr_plus.train_enumeration(leduc, iterations=200)
    policy = policy_table(state)
    assert len(state.strategy_sum) == 528
    assert exploitability(leduc, policy) < 0.30


@pytest.mark.slow
def test_leduc_enum_game_value_near_published_nash():
    state = cfr_plus.train_enumeration(leduc, iterations=200)
    policy = policy_table(state)
    value = expected_game_value(leduc, policy, policy)
    assert value == pytest.approx(LEDUC_P1_NASH_VALUE, abs=0.025)
