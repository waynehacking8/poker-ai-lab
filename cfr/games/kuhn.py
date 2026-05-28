"""Kuhn Poker — minimal poker game for CFR validation.

Rules:
    - 3 cards: J (rank 0), Q (rank 1), K (rank 2)
    - Each player antes 1 chip; pot starts at 2.
    - Each player gets 1 hole card.
    - Action sequence: P1 acts, then P2, possibly P1 again.
    - Actions: 'p' = pass / check / fold-after-bet; 'b' = bet / call
    - Terminal histories: pp, pbp, pbb, bp, bb

Utilities are computed from Player 1's perspective.
"""

from __future__ import annotations

from itertools import permutations
from typing import List, Tuple

CARDS = (0, 1, 2)  # J, Q, K
CARD_NAMES = {0: "J", 1: "Q", 2: "K"}
NUM_PLAYERS = 2
ACTIONS = ("p", "b")  # pass / bet


def is_terminal(history: str) -> bool:
    """Return True if the betting sequence has reached a terminal node."""
    return history in {"pp", "pbp", "pbb", "bp", "bb"}


def current_player(history: str) -> int:
    """Return whose turn it is at the given non-terminal history (0-indexed)."""
    # Player 1 (index 0) acts on '' and 'pb'; Player 2 (index 1) acts on 'p' and 'b'.
    return len(history) % 2


def legal_actions(history: str) -> Tuple[str, ...]:
    """All Kuhn states have two legal actions until terminal."""
    return ACTIONS


def terminal_utility(history: str, cards: Tuple[int, int]) -> float:
    """Return Player 1's payoff at a terminal node.

    Args:
        history: terminal action sequence.
        cards: (card_p1, card_p2) hole cards.
    """
    card_p1, card_p2 = cards
    p1_wins_showdown = card_p1 > card_p2

    if history == "pp":
        # Both pass → showdown, antes only (1 chip stake).
        return 1.0 if p1_wins_showdown else -1.0
    if history == "pbp":
        # P1 checked, P2 bet, P1 folded → P1 loses ante.
        return -1.0
    if history == "pbb":
        # P1 checked, P2 bet, P1 called → showdown with 2 chips at risk.
        return 2.0 if p1_wins_showdown else -2.0
    if history == "bp":
        # P1 bet, P2 folded → P1 wins P2's ante.
        return 1.0
    if history == "bb":
        # P1 bet, P2 called → showdown with 2 chips at risk.
        return 2.0 if p1_wins_showdown else -2.0
    raise ValueError(f"Not a terminal history: {history!r}")


def info_set_key(card: int, history: str) -> str:
    """Build the information-set key visible to the acting player."""
    return f"{CARD_NAMES[card]}:{history}"


def all_deals() -> List[Tuple[int, int]]:
    """Enumerate every legal (card_p1, card_p2) deal — 3 * 2 = 6 deals."""
    return list(permutations(CARDS, 2))
