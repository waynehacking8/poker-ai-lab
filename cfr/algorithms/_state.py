"""Tabular CFR state shared by vanilla CFR, MCCFR, and CFR+.

The three algorithms all maintain per-information-set ``regret_sum`` and
``strategy_sum`` vectors and derive the current strategy via regret
matching. They differ only in how those sums are *updated* (vanilla:
opponent-reach-weighted; MCCFR: sampled; CFR+: floored at 0 with linear
strategy averaging) — not in their layout.

Storage is **sized per information set** rather than globally, so the
same state object can serve games with variable legal-action counts
(e.g., Leduc Hold'em: 2 actions when no bet is pending, 3 when raising
is legal, 2 again at the cap). Callers pass ``num_actions`` on every
operation; ``policy_table`` recovers the size from the stored arrays.
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

    def _ensure(self, info_set: str, num_actions: int) -> None:
        if info_set not in self.regret_sum:
            self.regret_sum[info_set] = np.zeros(num_actions)
            self.strategy_sum[info_set] = np.zeros(num_actions)

    def current_strategy(self, info_set: str, num_actions: int) -> np.ndarray:
        """Regret-matching: proportions of positive regrets; uniform if all <= 0."""
        self._ensure(info_set, num_actions)
        regrets = self.regret_sum[info_set]
        positive = np.maximum(regrets, 0.0)
        total = positive.sum()
        if total > 0.0:
            return positive / total
        return np.full(num_actions, 1.0 / num_actions)

    def average_strategy(self, info_set: str) -> np.ndarray:
        """Time-averaged strategy — this is what converges to Nash.

        Size is recovered from the stored ``strategy_sum`` vector, so the
        caller does not need to remember ``num_actions``.
        """
        if info_set not in self.strategy_sum:
            raise KeyError(f"info set never visited: {info_set!r}")
        sums = self.strategy_sum[info_set]
        total = sums.sum()
        if total > 0.0:
            return sums / total
        return np.full(len(sums), 1.0 / len(sums))


def policy_table(state: CFRState) -> Dict[str, np.ndarray]:
    """Return the average (Nash-approximating) policy at every visited info set."""
    return {k: state.average_strategy(k) for k in state.strategy_sum}
