"""Unit tests for the Phase 2 simulator components.

These pin the contracts from ``docs/specifications-phase2.md`` §§1-3:
agent determinism, the colluding pair's behavioural deltas, and the
shape and content of the simulator log frame.
"""

from __future__ import annotations

import numpy as np
import pytest

from cfr.algorithms import vanilla_cfr
from cfr.games import kuhn
from collusion.simulator.colluding_pair import ColludingPair
from collusion.simulator.game_runner import run_session
from collusion.simulator.honest_player import HonestPlayer


@pytest.fixture(scope="module")
def kuhn_policy():
    state = vanilla_cfr.train(kuhn, iterations=10_000, seed=0)
    return vanilla_cfr.policy_table(state)


# ---------------------------------------------------------------------------
# HonestPlayer
# ---------------------------------------------------------------------------


def test_honest_player_is_deterministic_given_seed(kuhn_policy):
    a = HonestPlayer(kuhn_policy, np.random.default_rng(7))
    b = HonestPlayer(kuhn_policy, np.random.default_rng(7))
    actions_a = [a.act("Q:", ("p", "b")) for _ in range(20)]
    actions_b = [b.act("Q:", ("p", "b")) for _ in range(20)]
    assert actions_a == actions_b


def test_honest_player_matches_policy_distribution(kuhn_policy):
    """Sampled action frequency converges to the underlying policy probs."""
    rng = np.random.default_rng(0)
    agent = HonestPlayer(kuhn_policy, rng)
    info_set = "Q:p"
    expected = kuhn_policy[info_set]
    samples = [agent.act(info_set, ("p", "b")) for _ in range(10_000)]
    empirical_b = samples.count("b") / len(samples)
    assert empirical_b == pytest.approx(expected[1], abs=0.02)


def test_honest_player_unknown_info_set_is_uniform():
    """Missing info sets fall back to a uniform distribution."""
    rng = np.random.default_rng(0)
    agent = HonestPlayer({}, rng)
    samples = [agent.act("never:seen", ("p", "b")) for _ in range(2_000)]
    rate_b = samples.count("b") / len(samples)
    assert rate_b == pytest.approx(0.5, abs=0.05)


# ---------------------------------------------------------------------------
# ColludingPair
# ---------------------------------------------------------------------------


def test_colluder_behaves_honestly_when_partner_absent(kuhn_policy):
    """No partner at the table -> indistinguishable from HonestPlayer."""
    rng_c = np.random.default_rng(42)
    rng_h = np.random.default_rng(42)
    colluder = ColludingPair(
        own_id=0, partner_id=1, policy=kuhn_policy, rng=rng_c,
    )
    honest = HonestPlayer(kuhn_policy, rng_h)
    actions_c = [colluder.act(own_card=1, partner_card=None,
                              info_set="Q:b", legal_actions=("p", "b")) for _ in range(200)]
    actions_h = [honest.act("Q:b", ("p", "b")) for _ in range(200)]
    assert actions_c == actions_h


def test_colluder_soft_folds_more_than_honest(kuhn_policy):
    """With a weaker hand and partner across the table, fold rate rises."""
    rng_c = np.random.default_rng(0)
    colluder = ColludingPair(
        own_id=0, partner_id=1, policy=kuhn_policy,
        soft_fold_prob=0.95, chip_dump_prob=0.0, rng=rng_c,
    )
    # Q:b normally folds with prob ~0.67; with weaker-than-partner soft-fold
    # at 0.95 the colluder's fold rate must be clearly higher.
    rate = sum(
        colluder.act(own_card=1, partner_card=2,
                     info_set="Q:b", legal_actions=("p", "b")) == "p"
        for _ in range(2_000)
    ) / 2_000
    assert rate >= 0.85


def test_colluder_no_bluff_when_weakest(kuhn_policy):
    """At the root with J and partner across, never open with a bet."""
    rng_c = np.random.default_rng(0)
    colluder = ColludingPair(
        own_id=0, partner_id=1, policy=kuhn_policy, rng=rng_c,
    )
    actions = [
        colluder.act(own_card=0, partner_card=2,
                     info_set="J:", legal_actions=("p", "b"))
        for _ in range(500)
    ]
    assert "b" not in actions


# ---------------------------------------------------------------------------
# run_session
# ---------------------------------------------------------------------------


def test_run_session_schema(kuhn_policy):
    log = run_session(num_players=4, num_hands=200, colluder_fraction=0.25,
                      policy=kuhn_policy, seed=0)
    required = {
        "hand_id", "player_id", "seat", "info_set", "action", "own_card",
        "is_colluder", "partner_id",
    }
    assert required.issubset(log.columns)
    # Row count: 2-3 decisions per hand, total ~400-600.
    assert 2 * 200 <= len(log) <= 3 * 200
    # Determinism.
    log_b = run_session(num_players=4, num_hands=200, colluder_fraction=0.25,
                        policy=kuhn_policy, seed=0)
    assert log.equals(log_b)


def test_run_session_colluder_fraction_approximates_setting(kuhn_policy):
    log = run_session(num_players=4, num_hands=1_000, colluder_fraction=0.25,
                      policy=kuhn_policy, seed=0)
    # Per the runner, frac=0.25 with N=4 -> 1 disjoint pair (2 colluders out
    # of 4 players). Half of decision rows should therefore be colluders.
    assert log["is_colluder"].mean() == pytest.approx(0.5, abs=0.15)
