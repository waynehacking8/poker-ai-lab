"""Monte Carlo CFR — External Sampling (Lanctot et al., 2009).

External Sampling reduces the per-iteration cost of vanilla CFR by
**sampling chance and the opponent's actions** while exhaustively
traversing the **acting player's actions** at every one of their
information sets.

Per iteration one player is designated the *traverser*:

  * The traverser fully expands all of their actions at each of their
    own info sets, computing an action-value vector ``v[a]``.
  * The opponent samples a single action from their current strategy.
  * Chance samples a single deal.

The traverser's regrets are updated by the standard counterfactual
formula ``v[a] - sum_a sigma(a) v[a]``. Because chance and the
opponent are sampled exactly proportionally to their reach
probabilities, the estimator is unbiased; External Sampling does **not**
require importance-sampling correction (in contrast to Outcome
Sampling, the other MCCFR variant).

Strategy averaging uses the "unweighted" visit-based rule (Lanctot
2009, §4.2): at each visit to a traverser info set, the current
strategy is added to ``strategy_sum``. Over many iterations the
sample reach probability cancels out, so the normalized average
converges to the same time-average policy as vanilla CFR.

Traversers alternate (P0 on even iterations, P1 on odd) so both
players' info sets accumulate updates. The recursion always returns
utility from the *traverser's* perspective, so no sign flipping is
needed in the recursive calls.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

from cfr.algorithms._state import CFRState


def _terminal_util_for(game, history: str, cards: Tuple[int, int], traverser: int) -> float:
    """Terminal payoff from the traverser's perspective."""
    util_p1 = game.terminal_utility(history, cards)
    return util_p1 if traverser == 0 else -util_p1


def _external_sampling(
    game,
    state: CFRState,
    history: str,
    cards: Tuple[int, int],
    traverser: int,
    rng: np.random.Generator,
) -> float:
    """Recursive External Sampling — returns sampled utility for the traverser."""
    if game.is_terminal(history):
        return _terminal_util_for(game, history, cards, traverser)

    player = game.current_player(history)
    info_set = game.info_set_key(cards[player], history)
    actions = game.legal_actions(history)
    strategy = state.current_strategy(info_set)

    if player == traverser:
        num_actions = len(actions)
        utils = np.zeros(num_actions)
        for i, action in enumerate(actions):
            utils[i] = _external_sampling(
                game, state, history + action, cards, traverser, rng
            )
        node_util = float(np.dot(strategy, utils))
        state._ensure(info_set)
        state.regret_sum[info_set] += utils - node_util
        state.strategy_sum[info_set] += strategy
        return node_util

    # Opponent: sample one action proportional to current strategy.
    idx = int(rng.choice(len(actions), p=strategy))
    return _external_sampling(
        game, state, history + actions[idx], cards, traverser, rng
    )


def train(
    game,
    iterations: int,
    verbose: bool = False,
    seed: int | None = 0,
) -> CFRState:
    """Run External-Sampling MCCFR for the given number of iterations.

    Iterations alternate between traversers (P0 on even iterations,
    P1 on odd). Chance (the deal) is sampled uniformly each iteration.
    """
    state = CFRState(num_actions=len(game.ACTIONS))
    deals = game.all_deals()
    rng = np.random.default_rng(seed)
    deal_indices = np.arange(len(deals))

    for it in range(iterations):
        traverser = it % 2
        cards = deals[int(rng.choice(deal_indices))]
        _external_sampling(game, state, "", cards, traverser, rng)
        if verbose and (it + 1) % max(1, iterations // 10) == 0:
            visited = len(state.regret_sum)
            print(f"iter {it + 1:>6} | info sets touched = {visited}")
    return state
