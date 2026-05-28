"""Vanilla Counterfactual Regret Minimization (Zinkevich et al., 2007).

Reference implementation operating on Kuhn-like extensive-form games via the
small game module API:

    is_terminal(history) -> bool
    current_player(history) -> int          # 0 or 1
    legal_actions(history) -> tuple[str]
    terminal_utility(history, cards) -> float  # from P1's perspective
    info_set_key(card, history) -> str
    all_deals() -> list[tuple[int, int]]

Recursive CFR with full game-tree traversal. Chance is handled by enumerating
all deals at the root and averaging — exact, no sampling.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np


@dataclass
class CFRState:
    """Tabular regret and strategy storage, keyed by information set."""

    regret_sum: Dict[str, np.ndarray] = field(default_factory=dict)
    strategy_sum: Dict[str, np.ndarray] = field(default_factory=dict)
    num_actions: int = 2

    def get_regrets(self, info_set: str) -> np.ndarray:
        if info_set not in self.regret_sum:
            self.regret_sum[info_set] = np.zeros(self.num_actions)
            self.strategy_sum[info_set] = np.zeros(self.num_actions)
        return self.regret_sum[info_set]

    def current_strategy(self, info_set: str) -> np.ndarray:
        """Regret-matching: positive-regret proportions; uniform if all <= 0."""
        regrets = self.get_regrets(info_set)
        positive = np.maximum(regrets, 0.0)
        total = positive.sum()
        if total > 0.0:
            return positive / total
        return np.ones(self.num_actions) / self.num_actions

    def average_strategy(self, info_set: str) -> np.ndarray:
        """Time-averaged strategy — this is what converges to Nash."""
        total = self.strategy_sum.get(info_set, np.zeros(self.num_actions)).sum()
        if total > 0.0:
            return self.strategy_sum[info_set] / total
        return np.ones(self.num_actions) / self.num_actions


def _cfr_recurse(
    game,
    state: CFRState,
    history: str,
    cards: Tuple[int, int],
    reach_probs: np.ndarray,
) -> float:
    """Recursive CFR traversal returning utility for the player to act.

    reach_probs[i] = probability that player i reached this node under current
    strategies (excluding chance, which is enumerated externally).
    """
    if game.is_terminal(history):
        # Convert P1-perspective utility into "player-to-act" utility when needed.
        # We return P1's utility; sign-flip handled by the caller for P2 nodes.
        return game.terminal_utility(history, cards)

    player = game.current_player(history)
    card = cards[player]
    info_set = game.info_set_key(card, history)
    actions = game.legal_actions(history)

    strategy = state.current_strategy(info_set)
    util_per_action = np.zeros(len(actions))
    node_util = 0.0

    for i, action in enumerate(actions):
        new_history = history + action
        new_reach = reach_probs.copy()
        new_reach[player] *= strategy[i]
        # Returned utility is always from P1's perspective.
        util_per_action[i] = _cfr_recurse(game, state, new_history, cards, new_reach)
        # When computing this player's expected payoff, flip sign for P2.
        signed_util = util_per_action[i] if player == 0 else -util_per_action[i]
        node_util += strategy[i] * signed_util

    # Regret update — counterfactual reach excludes the acting player's reach.
    cf_reach = reach_probs[1 - player]
    own_reach = reach_probs[player]
    regrets = state.get_regrets(info_set)
    for i in range(len(actions)):
        signed_util_i = util_per_action[i] if player == 0 else -util_per_action[i]
        regrets[i] += cf_reach * (signed_util_i - node_util)
    state.strategy_sum[info_set] += own_reach * strategy

    # Return P1-perspective utility so the caller doesn't need to flip again.
    return node_util if player == 0 else -node_util


def train(game, iterations: int, verbose: bool = False) -> CFRState:
    """Run vanilla CFR for the given number of iterations.

    Chance (the deal) is enumerated exactly: each iteration sums over all
    (card_p1, card_p2) deals weighted by uniform probability.
    """
    state = CFRState(num_actions=len(game.ACTIONS))
    deals = game.all_deals()
    p_deal = 1.0 / len(deals)

    for it in range(iterations):
        util = 0.0
        for cards in deals:
            util += p_deal * _cfr_recurse(game, state, "", cards, np.ones(2))
        if verbose and (it + 1) % max(1, iterations // 10) == 0:
            print(f"iter {it + 1:>6} | mean P1 util ≈ {util:+.4f}")
    return state


def policy_table(state: CFRState) -> Dict[str, np.ndarray]:
    """Return the average (Nash-approximating) policy at every visited info set."""
    return {k: state.average_strategy(k) for k in state.strategy_sum}
