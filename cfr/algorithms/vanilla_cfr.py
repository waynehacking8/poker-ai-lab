"""Vanilla Counterfactual Regret Minimization (Zinkevich et al., 2007).

This implementation follows the Neller & Lanctot (2013) tutorial convention:

  - ``cfr(history, ...)`` returns the expected utility from the perspective
    of the player whose turn it is at ``history``.
  - Each recursive call decides whether to negate by comparing
    ``current_player(history)`` with ``current_player(next_history)``.
    In strictly-alternating games (Kuhn) the players always flip; in
    Leduc the same player can act on both sides of a round boundary, so
    the comparison must be performed per call rather than assumed.
  - Terminal utilities are also expressed from the current player's
    perspective (the player who would act next if play continued).

Chance is enumerated by sampling a uniform deal each iteration (chance
sampling MCCFR semantics applied to vanilla CFR — provably correct and
empirically faster than full enumeration on Kuhn).

The small-game API used (e.g., ``cfr.games.kuhn``) must expose:

  ``ACTIONS``                              tuple of all action symbols
  ``all_deals()``                          list of card tuples (one per chance outcome)
  ``is_terminal(history)``                 bool
  ``current_player(history)``              int (0 or 1)
  ``legal_actions(history)``               tuple[str, ...] (may vary by state)
  ``next_history(history, action)``        str (game-aware; handles round
                                                 transitions in Leduc, just
                                                 concatenates in Kuhn)
  ``terminal_utility(history, cards)``     float (P1 perspective)
  ``info_set_key(player, cards, history)`` str (the game decides what is
                                                 visible to ``player``)
"""

from __future__ import annotations

import numpy as np

from cfr.algorithms._state import CFRState, policy_table  # noqa: F401  (re-export)


def _terminal_util_current(game, history: str, cards) -> float:
    """Adapter: convert game.terminal_utility (P1-perspective) to current-player perspective.

    Uses ``game.current_player(history)`` — the player who would act next
    if play continued. This must come from the game, not from
    ``len(history) % 2``, because Leduc inserts a ``'/'`` separator that
    inflates history length without consuming a player turn.
    """
    util_p1 = game.terminal_utility(history, cards)
    current = game.current_player(history)
    return util_p1 if current == 0 else -util_p1


def _cfr(
    game,
    state: CFRState,
    history: str,
    cards: tuple,
    reach_p0: float,
    reach_p1: float,
) -> float:
    """Recursive CFR — returns utility for the player to act at ``history``."""
    if game.is_terminal(history):
        return _terminal_util_current(game, history, cards)

    player = game.current_player(history)
    info_set = game.info_set_key(player, cards, history)
    actions = game.legal_actions(history)
    num_actions = len(actions)

    strategy = state.current_strategy(info_set, num_actions)
    util = np.zeros(num_actions)
    node_util = 0.0

    for i, action in enumerate(actions):
        next_history = game.next_history(history, action)
        if player == 0:
            child = _cfr(game, state, next_history, cards, reach_p0 * strategy[i], reach_p1)
        else:
            child = _cfr(game, state, next_history, cards, reach_p0, reach_p1 * strategy[i])
        # The child returns utility from current_player(next_history)'s perspective.
        # If that is *us* (e.g., across a Leduc round boundary where the same
        # player acts on both sides), keep the sign; otherwise negate.
        sign = 1.0 if game.current_player(next_history) == player else -1.0
        util[i] = sign * child
        node_util += strategy[i] * util[i]

    # Counterfactual regret: weight by opponent's reach.
    cf_reach = reach_p1 if player == 0 else reach_p0
    own_reach = reach_p0 if player == 0 else reach_p1
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
    state = CFRState()
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


