"""CFR+ — Tammelin 2014.

CFR+ differs from vanilla CFR in three details:

1. **Regret-matching+ (RM+).** After each update, regrets are floored
   at zero rather than allowed to accumulate as negatives. Vanilla CFR
   spends a long warm-up bringing once-deeply-negative regrets back
   above zero before they influence the current strategy; RM+ removes
   that wasted work entirely.

2. **Linear iteration weighting.** ``strategy_sum`` is updated with
   weight ``t`` (the iteration index) rather than the unit weight of
   vanilla CFR. Later iterations dominate the time-average, so the
   running policy stabilizes well before the iteration budget is spent.

3. **Alternating updates.** Each iteration performs two passes — first
   with P0 as traverser, then with P1 — and only the traverser's
   regrets / strategy_sum change in each pass. The second pass therefore
   responds to P0's *just-updated* strategy, which pairs naturally with
   RM+ to give each player a strictly monotone update path.

Together these give CFR+ markedly faster convergence than vanilla CFR
on Kuhn — typically reaching the same exploitability in roughly an
order of magnitude fewer iterations.

The recursion itself (current-player-perspective utility, sign-flipping
in recursive calls) is identical to vanilla CFR. Chance is sampled per
iteration to stay consistent with the rest of the package; Tammelin's
original presentation used full chance enumeration, which is feasible
on Kuhn but harder to extend to Leduc.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np

from cfr.algorithms._state import CFRState


def _terminal_util_current(game, history: str, cards: Tuple[int, int]) -> float:
    """Adapter: convert P1-perspective utility to current-player perspective."""
    util_p1 = game.terminal_utility(history, cards)
    current = len(history) % 2
    return util_p1 if current == 0 else -util_p1


def _cfr_plus(
    game,
    state: CFRState,
    history: str,
    cards: Tuple[int, int],
    reach_p0: float,
    reach_p1: float,
    traverser: int,
    iteration: int,
) -> float:
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
            util[i] = -_cfr_plus(
                game, state, next_history, cards,
                reach_p0 * strategy[i], reach_p1, traverser, iteration,
            )
        else:
            util[i] = -_cfr_plus(
                game, state, next_history, cards,
                reach_p0, reach_p1 * strategy[i], traverser, iteration,
            )
        node_util += strategy[i] * util[i]

    # Alternating updates: only the traverser writes this iteration.
    if player == traverser:
        cf_reach = reach_p1 if player == 0 else reach_p0
        own_reach = reach_p0 if player == 0 else reach_p1
        state._ensure(info_set)
        # RM+: floor regrets at 0 after the update.
        state.regret_sum[info_set] = np.maximum(
            state.regret_sum[info_set] + cf_reach * (util - node_util), 0.0
        )
        # Linear iteration weighting in strategy averaging.
        state.strategy_sum[info_set] += iteration * own_reach * strategy

    return node_util


def train(
    game,
    iterations: int,
    verbose: bool = False,
    seed: int | None = 0,
) -> CFRState:
    """Run CFR+ with alternating traversers and chance sampling.

    Each iteration consists of two passes — one with each player as the
    traverser. The 1-indexed iteration counter is shared by both passes,
    matching the standard CFR+ convention (Tammelin 2014).
    """
    state = CFRState(num_actions=len(game.ACTIONS))
    deals = game.all_deals()
    rng = np.random.default_rng(seed)
    deal_indices = np.arange(len(deals))

    for it in range(iterations):
        cards = deals[int(rng.choice(deal_indices))]
        for traverser in (0, 1):
            _cfr_plus(game, state, "", cards, 1.0, 1.0, traverser, iteration=it + 1)
        if verbose and (it + 1) % max(1, iterations // 10) == 0:
            print(f"iter {it + 1:>6} | info sets touched = {len(state.regret_sum)}")
    return state
