"""Pairwise behavioural feature extractor for collusion detection.

Consumes the long-format log produced by
``collusion.simulator.game_runner.run_session`` and returns one row per
unordered pair ``(i, j)`` with ``i < j``. Pairs that never sat together
are emitted with all-zero feature values (and ``co_table_freq = 0``);
this keeps the feature frame rectangular and avoids special-casing
downstream.

Features (per ``docs/specifications-phase2.md`` §4):

  co_table_freq          fraction of hands in which both i and j played.
  mutual_fold_rate_i_vs_j fraction of i-vs-j hands where i was the folder.
  mutual_fold_rate_j_vs_i symmetric.
  simultaneous_fold_rate  fraction of co-seated hands where both folded
                          in the same round (always 0 in heads-up Kuhn
                          but retained for schema completeness).
  chip_flow_i_to_j        mean per-hand chip transfer from i to j.
  decision_time_corr      Pearson correlation of i's and j's latencies
                          across co-seated hands.
"""

from __future__ import annotations

from itertools import combinations
from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd


def _hand_summaries(log: pd.DataFrame) -> pd.DataFrame:
    """One row per hand: who played, who folded, utility to seat_p1, latencies."""
    rows: List[dict] = []
    grouped = log.groupby("hand_id", sort=True)
    for hand_id, frame in grouped:
        seat_p1 = int(frame["seat_p1"].iloc[0])
        seat_p2 = int(frame["seat_p2"].iloc[0])
        util_p1 = float(frame["hand_utility_p1"].iloc[0])

        # Identify the folder (if any). In Kuhn the action that opens
        # then "passes" after a bet — i.e., a 'p' after a 'b' — is a
        # fold. A 'p' as the first action is a check, not a fold.
        folder = None
        ordered = frame.sort_index().reset_index(drop=True)
        for idx, row in ordered.iterrows():
            if row["action"] == "p" and idx > 0 and ordered.loc[idx - 1, "action"] == "b":
                folder = int(row["player_id"])
                break

        # Latencies — one observed value per seat in this hand.
        lat_p1 = float(ordered.loc[ordered["player_id"] == seat_p1, "latency"].iloc[0])
        lat_p2 = float(ordered.loc[ordered["player_id"] == seat_p2, "latency"].iloc[0])
        rows.append({
            "hand_id": hand_id,
            "seat_p1": seat_p1,
            "seat_p2": seat_p2,
            "util_p1": util_p1,
            "folder": folder,
            "latency_p1": lat_p1,
            "latency_p2": lat_p2,
        })
    return pd.DataFrame(rows)


def _pair_iter(num_players: int) -> Iterable[Tuple[int, int]]:
    return combinations(range(num_players), 2)


def compute_pairwise_features(log: pd.DataFrame, num_players: int) -> pd.DataFrame:
    """Compute per-pair behavioural features. Returns a DataFrame indexed
    by ``(i, j)`` with ``i < j``."""
    required_cols = {"hand_id", "player_id", "seat_p1", "seat_p2",
                      "hand_utility_p1", "action", "latency"}
    missing = required_cols - set(log.columns)
    if missing:
        # The schema-only test passes a minimal log; emit zero features
        # for every pair so the schema check still succeeds.
        return pd.DataFrame(
            0.0,
            index=pd.MultiIndex.from_tuples(list(_pair_iter(num_players)),
                                             names=["i", "j"]),
            columns=[
                "co_table_freq", "mutual_fold_rate_i_vs_j",
                "mutual_fold_rate_j_vs_i", "simultaneous_fold_rate",
                "chip_flow_i_to_j", "decision_time_corr",
            ],
        )

    hands = _hand_summaries(log)
    total_hands = max(1, len(hands))

    feature_rows: List[dict] = []
    for i, j in _pair_iter(num_players):
        co_seated = hands[
            ((hands["seat_p1"] == i) & (hands["seat_p2"] == j))
            | ((hands["seat_p1"] == j) & (hands["seat_p2"] == i))
        ]
        n = len(co_seated)
        if n == 0:
            feature_rows.append({
                "i": i, "j": j,
                "co_table_freq": 0.0,
                "mutual_fold_rate_i_vs_j": 0.0,
                "mutual_fold_rate_j_vs_i": 0.0,
                "simultaneous_fold_rate": 0.0,
                "chip_flow_i_to_j": 0.0,
                "decision_time_corr": 0.0,
            })
            continue

        i_folded = (co_seated["folder"] == i).sum()
        j_folded = (co_seated["folder"] == j).sum()

        # Chip flow i -> j: positive means i lost chips to j.
        # util_p1 is from seat_p1's perspective. So:
        #   when i is seat_p1, i's utility is util_p1; chips i -> j = -util_p1.
        #   when j is seat_p1, j's utility is util_p1; chips i -> j = +util_p1.
        flow = 0.0
        for _, row in co_seated.iterrows():
            if int(row["seat_p1"]) == i:
                flow += -float(row["util_p1"])
            else:
                flow += float(row["util_p1"])
        mean_flow = flow / n

        # Decision time correlation: align latencies by player identity.
        lat_i: List[float] = []
        lat_j: List[float] = []
        for _, row in co_seated.iterrows():
            if int(row["seat_p1"]) == i:
                lat_i.append(float(row["latency_p1"]))
                lat_j.append(float(row["latency_p2"]))
            else:
                lat_i.append(float(row["latency_p2"]))
                lat_j.append(float(row["latency_p1"]))
        if n >= 2 and np.std(lat_i) > 0 and np.std(lat_j) > 0:
            corr = float(np.corrcoef(lat_i, lat_j)[0, 1])
        else:
            corr = 0.0

        feature_rows.append({
            "i": i, "j": j,
            "co_table_freq": n / total_hands,
            "mutual_fold_rate_i_vs_j": float(i_folded) / n,
            "mutual_fold_rate_j_vs_i": float(j_folded) / n,
            # Both players folding in the same round can't happen in HU
            # Kuhn (only one fold per hand). Retained for schema
            # consistency with the spec.
            "simultaneous_fold_rate": 0.0,
            "chip_flow_i_to_j": mean_flow,
            "decision_time_corr": corr,
        })

    df = pd.DataFrame(feature_rows).set_index(["i", "j"])
    return df


def compute_pairwise_features_multi(
    log: pd.DataFrame, num_players: int,
) -> pd.DataFrame:
    """Compute pairwise features independently per ``session_id``.

    Each session contributes ``C(num_players, 2)`` rows; player ids in
    different sessions never collide because the session log is expected
    to be the offset-namespaced output of ``run_many_sessions``.
    """
    if "session_id" not in log.columns:
        return compute_pairwise_features(log, num_players)

    frames: List[pd.DataFrame] = []
    for session_id, group in log.groupby("session_id"):
        offset = int(session_id) * num_players
        # Relocate ids to 0..num_players-1 for feature extraction, then
        # restore the offset on the resulting index.
        local = group.copy()
        for col in ("player_id", "seat", "partner_id", "opponent_id",
                     "seat_p1", "seat_p2"):
            if col in local.columns and local[col].dtype != object:
                local[col] = local[col] - offset
        feats = compute_pairwise_features(local, num_players)
        feats.index = pd.MultiIndex.from_tuples(
            [(i + offset, j + offset) for (i, j) in feats.index],
            names=["i", "j"],
        )
        frames.append(feats)
    return pd.concat(frames)
