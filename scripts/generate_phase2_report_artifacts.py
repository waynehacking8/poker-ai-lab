"""Produce the artifacts cited by reports/phase2-collusion-detection.md.

Runs the end-to-end Phase 2 pipeline once with the same seeds used by
``tests/test_collusion_features.py::test_lgbm_auc_threshold``, captures
the LightGBM diagnostics, and saves a ROC curve to
``reports/phase2-roc.png``. Also prints a JSON-shaped summary that the
report copy-pastes verbatim.

Run from project root:
    python -m scripts.generate_phase2_report_artifacts
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cfr.algorithms import vanilla_cfr
from cfr.games import kuhn
from collusion.features.pairwise import compute_pairwise_features_multi
from collusion.models.lgbm_classifier import train_lgbm
from collusion.simulator.game_runner import run_many_sessions


def _derive_labels(log: pd.DataFrame, num_players_total: int) -> pd.Series:
    partner_of = (
        log.dropna(subset=["partner_id"])
        .drop_duplicates(subset=["player_id"])
        .set_index("player_id")["partner_id"]
        .astype(int)
        .to_dict()
    )
    pairs = list(combinations(range(num_players_total), 2))
    return pd.Series(
        [partner_of.get(i) == j for (i, j) in pairs],
        index=pd.MultiIndex.from_tuples(pairs, names=["i", "j"]),
    )


def main() -> None:
    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    state = vanilla_cfr.train(kuhn, iterations=20_000, seed=0)
    policy = vanilla_cfr.policy_table(state)

    num_sessions = 40
    num_players = 4
    num_hands = 2_000

    log = run_many_sessions(
        num_sessions=num_sessions,
        num_players=num_players,
        num_hands=num_hands,
        colluder_fraction=0.25,
        policy=policy,
        seed=0,
    )
    features = compute_pairwise_features_multi(log, num_players=num_players)
    labels = _derive_labels(log, num_players_total=num_players * num_sessions)
    labels = labels.reindex(features.index, fill_value=False)
    result = train_lgbm(features, labels, test_size=0.3, seed=0)

    fpr, tpr, _ = result["roc_curve"]
    auc = result["auc_test"]
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, label=f"LightGBM (AUC = {auc:.3f})")
    ax.plot([0, 1], [0, 1], color="grey", linestyle="--", linewidth=0.8,
            label="random")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title("Phase 2 — pair-level collusion detector ROC")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out_dir / "phase2-roc.png", dpi=120)

    summary = {
        "num_sessions": num_sessions,
        "num_players_per_session": num_players,
        "num_hands_per_session": num_hands,
        "colluder_fraction": 0.25,
        "log_rows": int(len(log)),
        "n_pairs_total": int(len(features)),
        "n_train": int(result["n_train"]),
        "n_test": int(result["n_test"]),
        "auc_test": float(auc),
        "precision_at_recall_50": float(result["precision_at_recall_50"]),
        "positive_rate_test": float(
            (labels.reindex(features.index, fill_value=False)).mean()
        ),
        "feature_importances_gain": [
            {"feature": k, "gain": float(v)}
            for k, v in result["feature_importances"]
        ],
    }
    summary_path = out_dir / "phase2-metrics.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")

    print(json.dumps(summary, indent=2))
    print(f"\nROC saved: {out_dir / 'phase2-roc.png'}")
    print(f"Metrics saved: {summary_path}")


if __name__ == "__main__":
    main()
