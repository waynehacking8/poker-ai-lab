"""LightGBM baseline for pair-level collusion detection.

The split is by **player** rather than by pair: every pair involving a
test-set player goes to the test set, every pair with both endpoints in
the train set goes to train. This avoids leakage from a player who
appears in both partitions.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_auc_score, roc_curve


def _split_by_player(
    features: pd.DataFrame,
    labels: pd.Series,
    test_size: float,
    seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Player-disjoint train/test split. Returns X_train, X_test, y_train, y_test."""
    players = sorted({p for pair in features.index for p in pair})
    rng = np.random.default_rng(seed)
    rng.shuffle(players)
    n_test = max(1, int(round(len(players) * test_size)))
    test_players = set(players[:n_test])

    test_mask = features.index.map(
        lambda pair: pair[0] in test_players or pair[1] in test_players
    )
    train_mask = ~test_mask
    return (
        features.loc[train_mask], features.loc[test_mask],
        labels.loc[train_mask], labels.loc[test_mask],
    )


def train_lgbm(
    features: pd.DataFrame,
    labels: pd.Series,
    test_size: float = 0.3,
    seed: int = 0,
) -> Dict:
    """Train a LightGBM binary classifier and return diagnostics."""
    import lightgbm as lgb

    X_train, X_test, y_train, y_test = _split_by_player(
        features, labels, test_size, seed,
    )

    train_set = lgb.Dataset(X_train, label=y_train.astype(int))
    valid_set = lgb.Dataset(X_test, label=y_test.astype(int), reference=train_set)

    params = {
        "objective": "binary",
        "metric": "auc",
        "verbosity": -1,
        "learning_rate": 0.05,
        "num_leaves": 31,
        "min_data_in_leaf": max(1, len(X_train) // 50),
        "seed": seed,
    }
    booster = lgb.train(
        params,
        train_set,
        num_boost_round=200,
        valid_sets=[valid_set],
        callbacks=[lgb.early_stopping(20, verbose=False)],
    )

    probs = booster.predict(X_test)
    if y_test.nunique() < 2:
        auc = float("nan")
    else:
        auc = float(roc_auc_score(y_test.astype(int), probs))

    # precision at recall == 0.5
    p_at_r50 = float("nan")
    if y_test.nunique() >= 2:
        prec, recall, _ = precision_recall_curve(y_test.astype(int), probs)
        at_50 = np.where(recall >= 0.5)[0]
        if len(at_50) > 0:
            p_at_r50 = float(prec[at_50.max()])

    importances = sorted(
        zip(features.columns, booster.feature_importance(importance_type="gain")),
        key=lambda kv: -kv[1],
    )

    fpr, tpr, thresholds = (np.array([]), np.array([]), np.array([]))
    if y_test.nunique() >= 2:
        fpr, tpr, thresholds = roc_curve(y_test.astype(int), probs)

    return {
        "model": booster,
        "auc_test": auc,
        "precision_at_recall_50": p_at_r50,
        "feature_importances": importances,
        "roc_curve": (fpr, tpr, thresholds),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }
