"""N-card Kuhn poker — same rules, configurable deck size, for scale experiments.

Standard Kuhn (recovered at ``num_cards = 3``) is the smallest poker
game and is tractable under every algorithm in the package. As the
deck grows:

  - Chance branching = ``N × (N - 1)`` deals (quadratic in N).
  - Information sets ≈ ``2 × 6 × N`` (linear in N — own card × betting
    history × player).
  - Per-iteration cost of **full enumeration** scales as ``N²`` because
    every deal must be traversed.
  - Per-iteration cost of **MCCFR (External Sampling)** is independent
    of N (one sampled deal, one path).

Convergence per iteration in iter-count is similar across N for both
families (the strategy space only grows linearly), so the wall-time
crossover where MCCFR starts winning is purely driven by the per-iter
cost ratio. This module lets us measure that crossover empirically
rather than argue about it from intuition.

Rules (same as Kuhn 1950):
  - Two players, each ante 1 chip.
  - Each player gets one hole card from a deck of ``num_cards`` cards
    numbered ``0..num_cards-1`` (higher rank wins).
  - Single round of betting, actions ``p`` (pass / check / fold) and
    ``b`` (bet / call).
  - Terminal histories ``pp``, ``pbp``, ``pbb``, ``bp``, ``bb``.
  - Payoffs identical to Kuhn at ``num_cards = 3``; same showdown rule
    (higher rank wins, no ties because cards are distinct).
"""

from __future__ import annotations

from itertools import permutations
from types import SimpleNamespace
from typing import List, Tuple

NUM_PLAYERS = 2
ACTIONS = ("p", "b")


def _is_terminal(history: str) -> bool:
    return history in {"pp", "pbp", "pbb", "bp", "bb"}


def _current_player(history: str) -> int:
    return len(history) % 2


def _legal_actions(history: str) -> Tuple[str, ...]:
    return ACTIONS


def _terminal_utility(history: str, cards: Tuple[int, int]) -> float:
    card_p1, card_p2 = cards
    p1_wins = card_p1 > card_p2
    if history == "pp":
        return 1.0 if p1_wins else -1.0
    if history == "pbp":
        return -1.0
    if history == "pbb":
        return 2.0 if p1_wins else -2.0
    if history == "bp":
        return 1.0
    if history == "bb":
        return 2.0 if p1_wins else -2.0
    raise ValueError(f"Not a terminal history: {history!r}")


def _info_set_key(player: int, cards: Tuple[int, int], history: str) -> str:
    return f"{cards[player]}:{history}"


def _next_history(history: str, action: str) -> str:
    return history + action


def make_game(num_cards: int) -> SimpleNamespace:
    """Return a Kuhn-poker game module for the given deck size.

    The returned object exposes the same protocol as ``cfr.games.kuhn``:
    ``ACTIONS``, ``all_deals()``, ``is_terminal``, ``current_player``,
    ``legal_actions``, ``next_history``, ``terminal_utility``, and
    ``info_set_key``.
    """
    if num_cards < 3:
        raise ValueError(f"num_cards must be >= 3, got {num_cards}")

    cards = tuple(range(num_cards))

    def all_deals() -> List[Tuple[int, int]]:
        return list(permutations(cards, 2))

    return SimpleNamespace(
        ACTIONS=ACTIONS,
        all_deals=all_deals,
        is_terminal=_is_terminal,
        current_player=_current_player,
        legal_actions=_legal_actions,
        next_history=_next_history,
        terminal_utility=_terminal_utility,
        info_set_key=_info_set_key,
    )
