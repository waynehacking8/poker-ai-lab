"""Tests for the Phase 2 pairwise feature extractor.

These tests will fail until the collusion modules are implemented;
they exist now to encode the contract from
``docs/specifications-phase2.md`` section 4.
"""

from __future__ import annotations

import pandas as pd
import pytest


def test_compute_pairwise_features_schema() -> None:
    from collusion.features.pairwise import compute_pairwise_features

    log = pd.DataFrame(
        {
            "hand_id": [0, 0, 0, 0],
            "player_id": [0, 1, 2, 3],
            "seat": [0, 1, 2, 3],
            "info_set": ["J:", "Q:", "K:", "J:p"],
            "action": ["p", "b", "p", "p"],
            "own_card": [0, 1, 2, 0],
            "is_colluder": [False, False, False, False],
            "partner_id": [None, None, None, None],
        }
    )
    features = compute_pairwise_features(log, num_players=4)
    expected_cols = {
        "co_table_freq",
        "mutual_fold_rate_i_vs_j",
        "mutual_fold_rate_j_vs_i",
        "simultaneous_fold_rate",
        "chip_flow_i_to_j",
        "decision_time_corr",
    }
    assert expected_cols.issubset(set(features.columns))
    # Pair index should contain unordered pairs with i < j.
    assert all(i < j for i, j in features.index)


@pytest.mark.slow
def test_lgbm_auc_threshold() -> None:
    """End-to-end smoke: simulator -> features -> LightGBM AUC >= 0.85.

    The §6 spec setting (4-player, single session) yields only 6
    labelled pairs — too few to train a classifier on. We instead stack
    many independent 4-player sessions, each with its own colluder
    assignment, to grow the labelled-pair pool. Players from different
    sessions are namespaced apart so pairs never collide.
    """
    pytest.importorskip("lightgbm")
    from collusion.simulator.game_runner import run_many_sessions
    from collusion.features.pairwise import compute_pairwise_features_multi
    from collusion.models.lgbm_classifier import train_lgbm

    from cfr.algorithms import vanilla_cfr
    from cfr.games import kuhn

    state = vanilla_cfr.train(kuhn, iterations=20_000, seed=0)
    policy = vanilla_cfr.policy_table(state)

    log = run_many_sessions(
        num_sessions=40,
        num_players=4,
        num_hands=2_000,
        colluder_fraction=0.25,
        policy=policy,
        seed=0,
    )
    features = compute_pairwise_features_multi(log, num_players=4)
    labels = _derive_labels(log, num_players=4 * 40)
    # Align label index with the feature index — only pairs present in
    # features carry meaningful labels.
    labels = labels.reindex(features.index, fill_value=False)
    result = train_lgbm(features, labels, test_size=0.3, seed=0)
    assert result["auc_test"] >= 0.85


def _derive_labels(log: pd.DataFrame, num_players: int) -> pd.Series:
    """Helper: build pair-level ground-truth labels from the simulator log."""
    from itertools import combinations
    partner_of = (
        log.dropna(subset=["partner_id"])
        .drop_duplicates(subset=["player_id"])
        .set_index("player_id")["partner_id"]
        .astype(int)
        .to_dict()
    )
    pairs = list(combinations(range(num_players), 2))
    labels = pd.Series(
        [partner_of.get(i) == j for (i, j) in pairs],
        index=pd.MultiIndex.from_tuples(pairs, names=["i", "j"]),
    )
    return labels
