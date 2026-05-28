"""Regression tests pinning the Phase 1 CFR convergence properties.

These tests run a (relatively short) CFR training to confirm the
implementation has not regressed. Slow tests should be marked and
runnable with `pytest -m slow`.
"""

from __future__ import annotations

import pytest

from cfr.algorithms import vanilla_cfr
from cfr.evaluate.exploitability import exploitability
from cfr.games import kuhn


def test_kuhn_strategy_has_all_info_sets() -> None:
    """After training, the policy must cover all 12 Kuhn info sets."""
    state = vanilla_cfr.train(kuhn, iterations=2000, seed=0)
    policy = vanilla_cfr.policy_table(state)
    expected = {
        "J:", "Q:", "K:",
        "J:p", "Q:p", "K:p",
        "J:b", "Q:b", "K:b",
        "J:pb", "Q:pb", "K:pb",
    }
    assert set(policy.keys()) == expected


def test_kuhn_qualitative_strategies() -> None:
    """Strategies at high-confidence info sets should match Nash."""
    state = vanilla_cfr.train(kuhn, iterations=50_000, seed=0)
    policy = vanilla_cfr.policy_table(state)

    # K (best card) always bets when checked to.
    assert policy["K:p"][1] > 0.95
    # K always calls when bet into.
    assert policy["K:b"][1] > 0.95
    # J:b always folds (worst card facing bet).
    assert policy["J:b"][0] > 0.95
    # Q at root always checks.
    assert policy["Q:"][0] > 0.95


@pytest.mark.slow
def test_kuhn_exploitability_converges() -> None:
    """200k iterations should drive exploitability below 0.01."""
    state = vanilla_cfr.train(kuhn, iterations=200_000, seed=0)
    policy = vanilla_cfr.policy_table(state)
    assert exploitability(kuhn, policy) < 0.01
