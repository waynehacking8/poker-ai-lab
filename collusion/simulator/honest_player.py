"""Honest player — wraps a CFR-trained average policy as a callable agent.

The agent is deterministic given a fixed ``rng``: ``act`` samples from
the policy at the queried information set. Missing info sets fall back
to a uniform distribution over the legal actions, matching the
convention used by ``cfr.evaluate.exploitability``.
"""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np


class HonestPlayer:
    """Stochastic agent that samples from a fixed average-strategy table."""

    def __init__(self, policy: Dict[str, np.ndarray], rng: np.random.Generator):
        self.policy = policy
        self.rng = rng

    def act(self, info_set: str, legal_actions: Tuple[str, ...]) -> str:
        num_actions = len(legal_actions)
        probs = self.policy.get(info_set)
        if probs is None or len(probs) != num_actions:
            probs = np.full(num_actions, 1.0 / num_actions)
        idx = int(self.rng.choice(num_actions, p=probs))
        return legal_actions[idx]
