"""CFR+ — Tammelin 2014.

CFR+ differs from vanilla CFR in three details:

1. **Regret-matching+ (RM+).** After each iteration, cumulative
   regrets are floored at zero rather than allowed to remain negative.
   Vanilla CFR spends a long warm-up bringing once-deeply-negative
   regrets back above zero before they influence the current strategy;
   RM+ removes that wasted work entirely. The floor is applied **as a
   post-traversal step**, not inline during traversal — flooring
   inline corrupts the regret accumulator when an info set is visited
   multiple times per iteration (e.g., once per chance outcome under
   full enumeration). See OpenSpiel's note: "This must be done at the
   level of the information set, and thus cannot be done during the
   tree traversal (which is done on histories)."

2. **Linear iteration weighting.** ``strategy_sum`` is updated with
   weight ``t`` (the iteration index) rather than the unit weight of
   vanilla CFR. Later iterations dominate the time-average, so the
   running policy stabilizes well before the iteration budget is spent.

3. **Alternating updates.** Each iteration performs two passes — first
   with P0 as traverser, then with P1 — and only the traverser's
   regrets / strategy_sum change in each pass. The second pass therefore
   responds to P0's *just-updated* strategy.

**Strategy snapshot.** Canonical CFR+ keeps the policy frozen for the
duration of one player's full traversal. We take a `snapshot` of the
regret-matched strategies once per traversal and pass it into the
recursion — without this, regrets updated mid-traversal would change
the strategies read downstream, breaking the per-iteration semantics.

The recursion's sign convention (current-player-perspective utility,
per-call negate-only-if-player-changes) is identical to vanilla CFR.

Two training entry points are provided:

  ``train``              chance-sampling (one deal per iteration).
  ``train_enumeration``  full chance enumeration (Tammelin 2014
                         original setup, deterministic, no RNG).
"""

from __future__ import annotations

from typing import Dict

import numpy as np

from cfr.algorithms._state import CFRState


def _terminal_util_current(game, history: str, cards) -> float:
    """Convert game.terminal_utility (P1-perspective) to current-player perspective.

    Uses ``game.current_player(history)`` so the conversion stays correct
    even when the game's history representation does not equate one
    character with one player turn (e.g., Leduc's ``'/'`` separator).
    """
    util_p1 = game.terminal_utility(history, cards)
    current = game.current_player(history)
    return util_p1 if current == 0 else -util_p1


def _snapshot_strategy(
    state: CFRState, info_set: str, num_actions: int,
) -> np.ndarray:
    """Regret-matched strategy from the current ``regret_sum`` (RM+ form)."""
    state._ensure(info_set, num_actions)
    regrets = state.regret_sum[info_set]
    positive = np.maximum(regrets, 0.0)
    total = positive.sum()
    if total > 0.0:
        return positive / total
    return np.full(num_actions, 1.0 / num_actions)


def _apply_rm_plus_floor(state: CFRState) -> None:
    """RM+ floor — clip every cumulative regret at zero.

    Called after one player's full traversal completes (not inline).
    """
    for info_set, regrets in state.regret_sum.items():
        np.maximum(regrets, 0.0, out=regrets)


def _cfr_plus(
    game,
    state: CFRState,
    history: str,
    cards: tuple,
    reach_p0: float,
    reach_p1: float,
    traverser: int,
    iteration: int,
    strategy_cache: Dict[str, np.ndarray],
) -> float:
    """Recursive CFR+ traversal under a frozen strategy snapshot.

    Strategies are looked up from ``strategy_cache`` (filled lazily as
    new info sets are encountered). Regrets are accumulated plainly —
    the RM+ floor is applied once at the end of the full traversal by
    ``_apply_rm_plus_floor``.
    """
    if game.is_terminal(history):
        return _terminal_util_current(game, history, cards)

    player = game.current_player(history)
    info_set = game.info_set_key(player, cards, history)
    actions = game.legal_actions(history)
    num_actions = len(actions)

    strategy = strategy_cache.get(info_set)
    if strategy is None:
        strategy = _snapshot_strategy(state, info_set, num_actions)
        strategy_cache[info_set] = strategy

    util = np.zeros(num_actions)
    node_util = 0.0

    for i, action in enumerate(actions):
        next_history = game.next_history(history, action)
        if player == 0:
            child = _cfr_plus(
                game, state, next_history, cards,
                reach_p0 * strategy[i], reach_p1, traverser, iteration, strategy_cache,
            )
        else:
            child = _cfr_plus(
                game, state, next_history, cards,
                reach_p0, reach_p1 * strategy[i], traverser, iteration, strategy_cache,
            )
        sign = 1.0 if game.current_player(next_history) == player else -1.0
        util[i] = sign * child
        node_util += strategy[i] * util[i]

    if player == traverser:
        cf_reach = reach_p1 if player == 0 else reach_p0
        own_reach = reach_p0 if player == 0 else reach_p1
        state.regret_sum[info_set] += cf_reach * (util - node_util)
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
    traverser, each preceded by a fresh strategy snapshot and followed
    by an RM+ floor. The 1-indexed iteration counter is shared by both
    passes, matching the standard CFR+ convention (Tammelin 2014).
    """
    state = CFRState()
    deals = game.all_deals()
    rng = np.random.default_rng(seed)
    deal_indices = np.arange(len(deals))

    for it in range(iterations):
        cards = deals[int(rng.choice(deal_indices))]
        for traverser in (0, 1):
            strategy_cache: Dict[str, np.ndarray] = {}
            _cfr_plus(
                game, state, "", cards, 1.0, 1.0,
                traverser, iteration=it + 1, strategy_cache=strategy_cache,
            )
            _apply_rm_plus_floor(state)
        if verbose and (it + 1) % max(1, iterations // 10) == 0:
            print(f"iter {it + 1:>6} | info sets touched = {len(state.regret_sum)}")
    return state


def train_enumeration(
    game,
    iterations: int,
    verbose: bool = False,
) -> CFRState:
    """CFR+ with full chance enumeration — Tammelin 2014 original.

    Each iteration enumerates every chance outcome (deal) under both
    traversers, weighting the regret / strategy updates by ``1 / |deals|``.
    No RNG is used.

    Strategy is **frozen** within each player's full traversal (snapshot
    taken once before the traversal begins). Regrets accumulate plainly
    during the traversal; the RM+ floor is applied once after the
    traversal completes.

    Per-iteration cost is ``2 × |deals| × tree_size``, but the
    canonical algorithm pattern means each iteration is much more
    informative than the chance-sampling variant — Tammelin reports
    order-of-magnitude faster convergence over vanilla CFR on Leduc.
    """
    state = CFRState()
    deals = game.all_deals()
    chance_prob = 1.0 / len(deals)

    for it in range(iterations):
        for traverser in (0, 1):
            strategy_cache: Dict[str, np.ndarray] = {}
            for cards in deals:
                _cfr_plus(
                    game, state, "", cards,
                    chance_prob, chance_prob,
                    traverser, iteration=it + 1, strategy_cache=strategy_cache,
                )
            _apply_rm_plus_floor(state)
        if verbose and (it + 1) % max(1, iterations // 10) == 0:
            print(f"iter {it + 1:>6} | info sets touched = {len(state.regret_sum)}")
    return state
