"""Tabular CFR state shared by vanilla CFR, MCCFR, and CFR+.

The three algorithms all maintain per-information-set ``regret_sum`` and
``strategy_sum`` vectors and derive the current strategy via regret
matching. They differ only in how those sums are *updated* (vanilla:
opponent-reach-weighted; MCCFR: sampled; CFR+: floored at 0 with linear
strategy averaging) — not in their layout.

Keeping this single ``CFRState`` lets the algorithms share the same
``policy_table`` extraction and the same exploitability oracle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

import numpy as np


@dataclass
class CFRState:
    """Tabular regret and strategy storage, keyed by information set."""

    regret_sum: Dict[str, np.ndarray] = field(default_factory=dict)
    strategy_sum: Dict[str, np.ndarray] = field(default_factory=dict)
    num_actions: int = 2

    def _ensure(self, info_set: str) -> None:
        if info_set not in self.regret_sum:
            self.regret_sum[info_set] = np.zeros(self.num_actions)
            self.strategy_sum[info_set] = np.zeros(self.num_actions)

    def current_strategy(self, info_set: str) -> np.ndarray:
        """Regret-matching: proportions of positive regrets; uniform if all <= 0."""
        self._ensure(info_set)
        regrets = self.regret_sum[info_set]
        positive = np.maximum(regrets, 0.0)
        total = positive.sum()
        if total > 0.0:
            return positive / total
        return np.full(self.num_actions, 1.0 / self.num_actions)

    def average_strategy(self, info_set: str) -> np.ndarray:
        """Time-averaged strategy — this is what converges to Nash."""
        if info_set not in self.strategy_sum:
            return np.full(self.num_actions, 1.0 / self.num_actions)
        total = self.strategy_sum[info_set].sum()
        if total > 0.0:
            return self.strategy_sum[info_set] / total
        return np.full(self.num_actions, 1.0 / self.num_actions)


def policy_table(state: CFRState) -> Dict[str, np.ndarray]:
    """Return the average (Nash-approximating) policy at every visited info set."""
    return {k: state.average_strategy(k) for k in state.strategy_sum}
