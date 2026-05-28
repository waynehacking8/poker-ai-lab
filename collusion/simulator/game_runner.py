"""Multi-player Kuhn simulator with optional colluding pairs.

Topology: heads-up Kuhn played pairwise. Each hand a random pair of
players is drawn from the ``num_players`` seats; the two acting roles
inside the hand are P1 (acts first) and P2. Hole cards come from the
six legal Kuhn deals.

Colluder assignment:
  - ``colluder_fraction`` is interpreted as the fraction of all
    ordered pairs that should be colluding. We sample disjoint pairs
    until we have ``max(1, round(colluder_fraction * num_players / 2))``
    pairs (when ``colluder_fraction > 0``).
  - The remaining players are honest.

Per-decision log rows contain the schema declared in
``docs/specifications-phase2.md`` §3 plus a ``latency`` column used by
the decision-time-correlation feature. Honest latencies are i.i.d.;
colluding partners share a hidden hand-level latency factor so their
per-hand decision latencies are correlated.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from cfr.games import kuhn

from collusion.simulator.colluding_pair import ColludingPair
from collusion.simulator.honest_player import HonestPlayer


def _assign_colluder_pairs(
    num_players: int, colluder_fraction: float, rng: np.random.Generator,
) -> List[Tuple[int, int]]:
    if colluder_fraction <= 0.0:
        return []
    target = max(1, int(round(colluder_fraction * num_players / 2)))
    target = min(target, num_players // 2)
    seats = list(range(num_players))
    rng.shuffle(seats)
    return [(seats[2 * i], seats[2 * i + 1]) for i in range(target)]


def _build_agents(
    num_players: int,
    colluder_pairs: List[Tuple[int, int]],
    policy: Dict[str, np.ndarray],
    soft_fold_prob: float,
    chip_dump_prob: float,
    rng: np.random.Generator,
):
    partner_of: Dict[int, int] = {}
    for a, b in colluder_pairs:
        partner_of[a] = b
        partner_of[b] = a
    agents = {}
    for pid in range(num_players):
        if pid in partner_of:
            agents[pid] = ColludingPair(
                own_id=pid,
                partner_id=partner_of[pid],
                policy=policy,
                soft_fold_prob=soft_fold_prob,
                chip_dump_prob=chip_dump_prob,
                rng=rng,
            )
        else:
            agents[pid] = HonestPlayer(policy, rng)
    return agents, partner_of


def _play_hand(
    hand_id: int,
    pair: Tuple[int, int],
    hole: Tuple[int, int],
    agents: Dict[int, object],
    partner_of: Dict[int, int],
    latency_p1: float,
    latency_p2: float,
) -> Tuple[List[dict], float]:
    """Play one Kuhn HU hand, return decision rows + utility to P1."""
    seat_p1, seat_p2 = pair
    rows: List[dict] = []
    history = ""

    while not kuhn.is_terminal(history):
        cur = kuhn.current_player(history)
        seat = seat_p1 if cur == 0 else seat_p2
        own_card = hole[cur]
        opp_seat = seat_p2 if cur == 0 else seat_p1
        info_set = kuhn.info_set_key(cur, hole, history)
        legal = kuhn.legal_actions(history)

        agent = agents[seat]
        if isinstance(agent, ColludingPair):
            partner_card = hole[1 - cur] if partner_of.get(seat) == opp_seat else None
            action = agent.act(own_card, partner_card, info_set, legal)
        else:
            action = agent.act(info_set, legal)

        rows.append({
            "hand_id": hand_id,
            "player_id": seat,
            "seat": seat,
            "info_set": info_set,
            "action": action,
            "own_card": own_card,
            "is_colluder": seat in partner_of,
            "partner_id": partner_of.get(seat),
            "opponent_id": opp_seat,
            "latency": latency_p1 if cur == 0 else latency_p2,
        })
        history = kuhn.next_history(history, action)

    util_p1 = kuhn.terminal_utility(history, hole)
    for row in rows:
        row["hand_utility_p1"] = util_p1
        row["seat_p1"] = seat_p1
        row["seat_p2"] = seat_p2
    return rows, util_p1


def run_session(
    num_players: int,
    num_hands: int,
    colluder_fraction: float,
    policy: Dict[str, np.ndarray],
    seed: int = 0,
    soft_fold_prob: float = 0.7,
    chip_dump_prob: float = 0.1,
) -> pd.DataFrame:
    """Simulate ``num_hands`` heads-up Kuhn hands across ``num_players``.

    Returns a long-format DataFrame with one row per (player, decision)
    event. Columns:

        hand_id, player_id, seat, info_set, action, own_card,
        is_colluder, partner_id, opponent_id, latency

    ``opponent_id`` and ``latency`` are extensions beyond the §3 spec —
    they are needed by the pairwise feature extractor (chip-flow and
    decision-time correlation, respectively) and the spec leaves both
    "synthetic latencies" and the chip-flow accounting as
    implementation choices.
    """
    if num_players < 2:
        raise ValueError(f"num_players must be >= 2, got {num_players}")
    rng = np.random.default_rng(seed)

    colluder_pairs = _assign_colluder_pairs(num_players, colluder_fraction, rng)
    agents, partner_of = _build_agents(
        num_players, colluder_pairs, policy, soft_fold_prob, chip_dump_prob, rng,
    )
    deals = kuhn.all_deals()

    all_rows: List[dict] = []
    for hand_id in range(num_hands):
        # Pick two distinct seats; order them — first chosen acts as P1.
        seats = rng.choice(num_players, size=2, replace=False)
        pair = (int(seats[0]), int(seats[1]))
        hole = deals[int(rng.choice(len(deals)))]

        # Synthetic latencies. Colluding partners share a latent base.
        if pair[0] in partner_of and partner_of[pair[0]] == pair[1]:
            base = rng.normal(1.5, 0.3)
            latency_p1 = max(0.05, base + rng.normal(0, 0.05))
            latency_p2 = max(0.05, base + rng.normal(0, 0.05))
        else:
            latency_p1 = max(0.05, rng.normal(1.5, 0.3))
            latency_p2 = max(0.05, rng.normal(1.5, 0.3))

        rows, _ = _play_hand(
            hand_id, pair, hole, agents, partner_of, latency_p1, latency_p2,
        )
        all_rows.extend(rows)

    return pd.DataFrame(all_rows)


def run_many_sessions(
    num_sessions: int,
    num_players: int,
    num_hands: int,
    colluder_fraction: float,
    policy: Dict[str, np.ndarray],
    seed: int = 0,
    soft_fold_prob: float = 0.7,
    chip_dump_prob: float = 0.1,
) -> pd.DataFrame:
    """Run several independent sessions and concatenate them.

    Each session uses a fresh ``num_players`` namespace by offsetting
    ``player_id``/``partner_id`` by ``session_idx * num_players``. The
    resulting frame is suitable for stacking many small sessions into
    one feature matrix without pair-index collisions.
    """
    frames: List[pd.DataFrame] = []
    for session_idx in range(num_sessions):
        log = run_session(
            num_players=num_players,
            num_hands=num_hands,
            colluder_fraction=colluder_fraction,
            policy=policy,
            seed=seed + session_idx,
            soft_fold_prob=soft_fold_prob,
            chip_dump_prob=chip_dump_prob,
        )
        offset = session_idx * num_players
        for col in ("player_id", "seat", "partner_id", "opponent_id", "seat_p1", "seat_p2"):
            if col in log.columns:
                if log[col].dtype == object:
                    log[col] = log[col].map(
                        lambda x: x + offset if x is not None else None,
                    )
                else:
                    log[col] = log[col] + offset
        log["session_id"] = session_idx
        log["hand_id"] = log["hand_id"] + session_idx * num_hands
        frames.append(log)
    return pd.concat(frames, ignore_index=True)
