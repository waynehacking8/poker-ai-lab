"""Vanilla CFR with full chance enumeration — canonical Zinkevich 2007 form.

Tests pin the canonical convergence numbers used by the Phase 1 report.
Each iteration enumerates every chance outcome (deal); per-iteration
cost is ``|deals| × tree_size`` but the algorithm is deterministic
(no RNG anywhere) and is the reference baseline that CFR+ enumeration
should beat by an order of magnitude on Leduc.

Calibration sweep (seed irrelevant, deterministic):

  Kuhn:
       50 iter |  0.005 s | expl 0.054
      200 iter |  0.018 s | expl 0.024
     1000 iter |  0.092 s | expl 0.013
     5000 iter |  0.45  s | expl 0.0047

  Leduc:
       50 iter |   2.7 s | expl 0.221 | val -0.089
      200 iter |  11   s | expl 0.073 | val -0.083
      500 iter |  28   s | expl 0.057 | val -0.080
     1000 iter |  56   s | expl 0.033 | val -0.079

Kuhn test pinned at 1000 iter / expl < 0.02.
Leduc test pinned at 200 iter / expl < 0.10 (marked slow).
"""

from __future__ import annotations

import pytest

from cfr.algorithms import vanilla_cfr
from cfr.algorithms._state import policy_table
from cfr.evaluate.exploitability import exploitability, expected_game_value
from cfr.games import kuhn, leduc

KUHN_GAME_VALUE = -1.0 / 18.0
LEDUC_P1_NASH_VALUE = -0.0856


# ---------------------------------------------------------------------------
# Kuhn — fast tests
# ---------------------------------------------------------------------------


def test_kuhn_enum_visits_every_info_set():
    state = vanilla_cfr.train_enumeration(kuhn, iterations=100)
    assert len(state.strategy_sum) == 12


def test_kuhn_enum_converges():
    state = vanilla_cfr.train_enumeration(kuhn, iterations=1000)
    policy = policy_table(state)
    assert exploitability(kuhn, policy) < 0.02


def test_kuhn_enum_is_deterministic():
    """No RNG — two runs at the same iteration count are bit-identical."""
    a = vanilla_cfr.train_enumeration(kuhn, iterations=200)
    b = vanilla_cfr.train_enumeration(kuhn, iterations=200)
    assert a.regret_sum.keys() == b.regret_sum.keys()
    for key in a.regret_sum:
        assert (a.regret_sum[key] == b.regret_sum[key]).all()


def test_kuhn_enum_game_value_near_analytical():
    state = vanilla_cfr.train_enumeration(kuhn, iterations=1000)
    policy = policy_table(state)
    value = expected_game_value(kuhn, policy, policy)
    assert value == pytest.approx(KUHN_GAME_VALUE, abs=0.005)


# ---------------------------------------------------------------------------
# Leduc — marked slow because each iteration is ~50 ms.
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_leduc_enum_converges():
    state = vanilla_cfr.train_enumeration(leduc, iterations=200)
    policy = policy_table(state)
    assert len(state.strategy_sum) == 528
    assert exploitability(leduc, policy) < 0.10


@pytest.mark.slow
def test_leduc_enum_game_value_near_published_nash():
    state = vanilla_cfr.train_enumeration(leduc, iterations=200)
    policy = policy_table(state)
    value = expected_game_value(leduc, policy, policy)
    assert value == pytest.approx(LEDUC_P1_NASH_VALUE, abs=0.01)


# ---------------------------------------------------------------------------
# Canonical algorithm ordering: CFR+ enum < vanilla enum < MCCFR ES on
# small games. This freezes the literature-consistent ordering so future
# changes that break it are flagged immediately.
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_cfr_plus_enum_beats_vanilla_enum_on_leduc():
    """Tammelin 2014: CFR+ accelerates over vanilla CFR. On Leduc at 200
    iter, CFR+ should reach < half the vanilla expl."""
    from cfr.algorithms import cfr_plus

    vanilla_state = vanilla_cfr.train_enumeration(leduc, iterations=200)
    plus_state = cfr_plus.train_enumeration(leduc, iterations=200)
    vanilla_expl = exploitability(leduc, policy_table(vanilla_state))
    plus_expl = exploitability(leduc, policy_table(plus_state))
    assert plus_expl < vanilla_expl / 2.0, (
        f"CFR+ expl={plus_expl:.4f} should be << vanilla expl={vanilla_expl:.4f}"
    )
