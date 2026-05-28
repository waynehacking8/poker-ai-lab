"""Vanilla Counterfactual Regret Minimization (Zinkevich et al., 2007).

This implementation follows the Neller & Lanctot (2013) tutorial convention:

  - ``cfr(history, ...)`` returns the expected utility from the perspective
    of the player whose turn it is at ``history``.
  - Recursive calls negate the returned value because the child node's
    "current player" is the opponent of the caller's.
  - Terminal utilities are also expressed from the current player's
    perspective (the player whose turn it would be next if play continued).

Chance is enumerated by sampling a uniform deal each iteration (chance
sampling MCCFR semantics applied to vanilla CFR — provably correct and
empirically faster than full enumeration on Kuhn).

The small-game API used (e.g., ``cfr.games.kuhn``) must expose:

  ``ACTIONS``                              tuple of action symbols
  ``CARDS``                                tuple of card indices
  ``all_deals()``                          list of all (card_p1, card_p2)
  ``is_terminal(history)``                 bool
  ``current_player(history)``              int (0 or 1)
  ``legal_actions(history)``               tuple[str, ...]
  ``terminal_utility_current(history, cards)``
      Returns utility from the current player's perspective at the
      terminal node. (If only a P1-perspective utility is exposed, wrap
      it: ``util if current_player else -util``.)
  ``info_set_key(card, history)``          str
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

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


def _terminal_util_current(game, history: str, cards: Tuple[int, int]) -> float:
    """Adapter: convert game.terminal_utility (P1-perspective) to current-player perspective.

    At a terminal node, ``current_player`` is ``len(history) % 2`` — the
    player who would act next if play continued. By convention the
    function returns that player's utility.
    """
    util_p1 = game.terminal_utility(history, cards)
    current = len(history) % 2
    return util_p1 if current == 0 else -util_p1


def _cfr(
    game,
    state: CFRState,
    history: str,
    cards: Tuple[int, int],
    reach_p0: float,
    reach_p1: float,
) -> float:
    """Recursive CFR — returns utility for the player to act at ``history``."""
    if game.is_terminal(history):
        return _terminal_util_current(game, history, cards)

    player = game.current_player(history)
    info_set = game.info_set_key(cards[player], history)
    actions = game.legal_actions(history)
    num_actions = len(actions)

    strategy = state.current_strategy(info_set)
    util = np.zeros(num_actions)
    node_util = 0.0

    for i, action in enumerate(actions):
        next_history = history + action
        if player == 0:
            # Negate because the child returns the opponent's perspective.
            util[i] = -_cfr(game, state, next_history, cards, reach_p0 * strategy[i], reach_p1)
        else:
            util[i] = -_cfr(game, state, next_history, cards, reach_p0, reach_p1 * strategy[i])
        node_util += strategy[i] * util[i]

    # Counterfactual regret: weight by opponent's reach.
    cf_reach = reach_p1 if player == 0 else reach_p0
    own_reach = reach_p0 if player == 0 else reach_p1
    state._ensure(info_set)
    state.regret_sum[info_set] += cf_reach * (util - node_util)
    state.strategy_sum[info_set] += own_reach * strategy

    return node_util


def train(
    game,
    iterations: int,
    verbose: bool = False,
    seed: int | None = 0,
) -> CFRState:
    """Run vanilla CFR with chance-sampling for the given number of iterations."""
    state = CFRState(num_actions=len(game.ACTIONS))
    deals = game.all_deals()
    rng = np.random.default_rng(seed)
    deal_indices = np.arange(len(deals))

    util_running = 0.0
    for it in range(iterations):
        cards = deals[int(rng.choice(deal_indices))]
        util_running += _cfr(game, state, "", cards, 1.0, 1.0)
        if verbose and (it + 1) % max(1, iterations // 10) == 0:
            print(f"iter {it + 1:>6} | mean P1 util ≈ {util_running / (it + 1):+.4f}")
    return state


def policy_table(state: CFRState) -> Dict[str, np.ndarray]:
    """Return the average (Nash-approximating) policy at every visited info set."""
    return {k: state.average_strategy(k) for k in state.strategy_sum}
