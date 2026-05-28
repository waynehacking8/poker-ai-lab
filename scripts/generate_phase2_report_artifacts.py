"""Produce the artifacts cited by reports/phase2-collusion-detection.md.

Runs the end-to-end Phase 2 pipeline **twice** — once with the
synthetic shared-latency factor active (the "easy" setting), once
without it (closer to an adversarial colluder who deliberately
uncorrelates their input cadence). Saves a ROC curve and metrics
JSON for each, plus a combined ROC chart.

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


def _run(setting_name: str, *, shared_latency: bool) -> tuple[dict, tuple]:
    """Run one pipeline configuration and return (summary_dict, (fpr, tpr, auc))."""
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
        shared_latency=shared_latency,
    )
    features = compute_pairwise_features_multi(log, num_players=num_players)
    labels = _derive_labels(log, num_players_total=num_players * num_sessions)
    labels = labels.reindex(features.index, fill_value=False)
    result = train_lgbm(features, labels, test_size=0.3, seed=0)

    fpr, tpr, _ = result["roc_curve"]
    auc = result["auc_test"]

    summary = {
        "setting": setting_name,
        "shared_latency": shared_latency,
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
        "positive_rate_test": float(labels.mean()),
        "feature_importances_gain": [
            {"feature": k, "gain": float(v)} for k, v in result["feature_importances"]
        ],
    }
    return summary, (fpr, tpr, auc)


def main() -> None:
    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    settings = [
        ("with_shared_latency", True),
        ("without_shared_latency", False),
    ]

    rocs = []
    for name, shared in settings:
        print(f"\n=== {name} (shared_latency={shared}) ===")
        summary, roc = _run(name, shared_latency=shared)
        rocs.append((name, summary, roc))
        path = out_dir / f"phase2-metrics-{name}.json"
        path.write_text(json.dumps(summary, indent=2) + "\n")
        print(f"AUC = {summary['auc_test']:.4f}")
        print(f"P@R50 = {summary['precision_at_recall_50']:.4f}")
        print("Top features by gain:")
        for entry in summary["feature_importances_gain"][:3]:
            print(f"  {entry['feature']:30}  {entry['gain']:.4f}")
        print(f"Saved {path}")

    # Per-setting ROC plots (keep the original phase2-roc.png as the
    # default high-signal panel for backwards compatibility).
    for name, summary, (fpr, tpr, auc) in rocs:
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.plot(fpr, tpr, label=f"LightGBM (AUC = {auc:.3f})")
        ax.plot([0, 1], [0, 1], color="grey", linestyle="--", linewidth=0.8, label="random")
        ax.set_xlabel("False positive rate")
        ax.set_ylabel("True positive rate")
        ax.set_title(f"Phase 2 ROC — {name.replace('_', ' ')}")
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower right")
        fig.tight_layout()
        fig.savefig(out_dir / f"phase2-roc-{name}.png", dpi=120)
        plt.close(fig)

    # Backwards-compat alias for the original report cite.
    fpr, tpr, auc = rocs[0][2]
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, label=f"LightGBM (AUC = {auc:.3f})")
    ax.plot([0, 1], [0, 1], color="grey", linestyle="--", linewidth=0.8, label="random")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title("Phase 2 — pair-level collusion detector ROC")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out_dir / "phase2-roc.png", dpi=120)
    plt.close(fig)

    # Combined side-by-side ROC for the report's headline chart.
    fig, ax = plt.subplots(figsize=(6, 5))
    for name, summary, (fpr, tpr, auc) in rocs:
        label = name.replace("_", " ")
        ax.plot(fpr, tpr, label=f"{label}  (AUC = {auc:.3f})")
    ax.plot([0, 1], [0, 1], color="grey", linestyle="--", linewidth=0.8, label="random")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title("Phase 2 — detector ROC with vs without shared-latency signal")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out_dir / "phase2-roc-comparison.png", dpi=120)
    plt.close(fig)
    print("\nCombined ROC saved: reports/phase2-roc-comparison.png")

    # Compact summary file for the report tables.
    combined = {name: summary for name, summary, _ in rocs}
    (out_dir / "phase2-metrics.json").write_text(
        json.dumps(combined, indent=2) + "\n"
    )
    print("Combined metrics saved: reports/phase2-metrics.json")


if __name__ == "__main__":
    main()
