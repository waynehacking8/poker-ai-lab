"""Leduc Hold'em — the canonical small benchmark for CFR research.

Rules (Southey et al. 2005, "Bayes' Bluff: Opponent Modelling in Poker"):

  - 6-card deck: two suits of {J, Q, K}. Suit is irrelevant to payoffs.
  - Each player antes 1 chip; pot starts at 2.
  - Each player gets 1 hole card. After round 1 betting, one community
    card is dealt. Round 2 betting follows. Then showdown.
  - Bet/raise size is fixed at 2 chips in round 1 and 4 chips in round 2.
  - At most 2 raises per round (so the per-round action sequences are
    capped at 3 escalations: bet → raise → raise).
  - Showdown: a player who has *paired* their hole card with the
    community card beats a non-paired opponent. Otherwise the higher
    hole card wins. Genuine ties (same hole rank, neither paired) split
    the pot.

Cards are indexed 0..5; ``rank(c) = c // 2`` maps to {J=0, Q=1, K=2}.

History encoding:

  - Action symbols: ``'f'`` (fold), ``'c'`` (check / call), ``'r'`` (bet /
    raise — the kind depends on whether a bet is pending).
  - ``'/'`` separates the two betting rounds. Round 2 begins immediately
    after round 1 ends without a fold; ``next_history`` appends ``'/'``
    automatically so callers don't have to track round boundaries.
  - Example histories: ``""`` (start of round 1), ``"crc/"`` (round 1
    closed by call after a check-bet, round 2 about to start),
    ``"rrf"`` (terminal fold).
"""

from __future__ import annotations

from typing import List, Tuple

RANKS = (0, 1, 2)
RANK_NAMES = {0: "J", 1: "Q", 2: "K"}
NUM_CARDS = 6  # 2 copies of each rank
NUM_PLAYERS = 2
ACTIONS = ("f", "c", "r")
BET_SIZE = {1: 2, 2: 4}  # round-index -> bet/raise amount
MAX_RAISES_PER_ROUND = 2
ANTE = 1


def rank(card: int) -> int:
    return card // 2


def _current_round_str(history: str) -> str:
    """The action sequence of the *active* (not-yet-completed) round."""
    if "/" in history:
        return history.split("/", 1)[1]
    return history


def _round_index(history: str) -> int:
    """1 if we're in the first betting round, 2 if in the second."""
    return 2 if "/" in history else 1


def _round_complete(round_actions: str) -> bool:
    """Has this single round of betting finished?"""
    if not round_actions:
        return False
    last = round_actions[-1]
    if last == "f":
        return True
    if last == "c":
        # A lone 'c' is just a check with the opponent still to respond.
        # 'cc' = both checked; '*rc' = call after a bet/raise.
        if len(round_actions) == 1:
            return False
        return round_actions[-2] in ("c", "r")
    return False  # last == 'r' — opponent still to act


def is_terminal(history: str) -> bool:
    """Terminal iff someone has folded, or round 2 has been resolved."""
    if not history:
        return False
    if history.endswith("f"):
        return True
    if "/" in history:
        return _round_complete(history.split("/", 1)[1])
    return False


def current_player(history: str) -> int:
    """Whose turn it is (0 or 1). P1 acts first in each round."""
    return len(_current_round_str(history)) % 2


def legal_actions(history: str) -> Tuple[str, ...]:
    """Legal actions at ``history`` — varies with bet state and the raise cap."""
    round_actions = _current_round_str(history)
    bet_pending = bool(round_actions) and round_actions[-1] == "r"
    if not bet_pending:
        # No bet to respond to: check or open a bet.
        return ("c", "r")
    # A bet is pending. Folding and calling are always legal.
    raises = round_actions.count("r")
    if raises >= 1 + MAX_RAISES_PER_ROUND:
        # Cap: no more re-raises.
        return ("f", "c")
    return ("f", "c", "r")


def next_history(history: str, action: str) -> str:
    """Append ``action`` and auto-transition to round 2 when round 1 closes."""
    new = history + action
    if "/" in new:
        return new
    # Still in round 1 — check whether the action just closed it.
    if _round_complete(new) and not new.endswith("f"):
        new += "/"
    return new


def _round_contribution(round_actions: str, player: int, bet_size: int) -> int:
    """Chips ``player`` added in this round (excluding antes)."""
    p_chips = [0, 0]
    current_bet = 0
    for i, action in enumerate(round_actions):
        actor = i % 2
        if action == "f":
            break
        if action == "c":
            p_chips[actor] = current_bet
        elif action == "r":
            current_bet += bet_size
            p_chips[actor] = current_bet
    return p_chips[player]


def _contribution(history: str, player: int) -> int:
    """Total chips ``player`` has put into the pot, antes included."""
    total = ANTE
    if "/" in history:
        r1, r2 = history.split("/", 1)
    else:
        r1, r2 = history, ""
    total += _round_contribution(r1, player, BET_SIZE[1])
    total += _round_contribution(r2, player, BET_SIZE[2])
    return total


def _folder(history: str) -> int:
    """Which player folded — only valid if ``history`` ends with 'f'."""
    # The folder is whoever acted last; that's len(current_round) - 1 mod 2.
    round_actions = _current_round_str(history)
    return (len(round_actions) - 1) % 2


def _showdown_winner(hole_p0: int, hole_p1: int, community: int) -> int:
    """0 if P0 wins, 1 if P1 wins, -1 if split."""
    r0, r1, rc = rank(hole_p0), rank(hole_p1), rank(community)
    p0_pair, p1_pair = r0 == rc, r1 == rc
    # Strictly: only one player can pair with the community since each rank
    # has two physical cards and the community already used one of its rank.
    if p0_pair and not p1_pair:
        return 0
    if p1_pair and not p0_pair:
        return 1
    # Neither pairs — compare hole ranks.
    if r0 > r1:
        return 0
    if r1 > r0:
        return 1
    return -1  # tie (same hole rank, neither pairs)


def terminal_utility(history: str, cards: Tuple[int, int, int]) -> float:
    """P1's payoff at a terminal history.

    Args:
        history: terminal action sequence.
        cards: (hole_p0, hole_p1, community), each a card index in 0..5.
    """
    hole_p0, hole_p1, community = cards
    contrib_p0 = _contribution(history, 0)
    contrib_p1 = _contribution(history, 1)

    if history.endswith("f"):
        folder = _folder(history)
        # Folder loses what they put in; the other wins that amount.
        return -float(contrib_p0) if folder == 0 else float(contrib_p1)

    winner = _showdown_winner(hole_p0, hole_p1, community)
    if winner == 0:
        return float(contrib_p1)
    if winner == 1:
        return -float(contrib_p0)
    return 0.0  # split


def info_set_key(player: int, cards: Tuple[int, int, int], history: str) -> str:
    """Information set visible to ``player``.

    Preflop: own hole rank + betting history.
    Postflop: own hole rank + community rank + full betting history.
    """
    own = RANK_NAMES[rank(cards[player])]
    if "/" not in history:
        return f"{own}|{history}"
    community = RANK_NAMES[rank(cards[2])]
    return f"{own}|{community}|{history}"


def all_deals() -> List[Tuple[int, int, int]]:
    """All 6 * 5 * 4 = 120 ordered (hole_p0, hole_p1, community) deals."""
    deals: List[Tuple[int, int, int]] = []
    for hp0 in range(NUM_CARDS):
        for hp1 in range(NUM_CARDS):
            if hp1 == hp0:
                continue
            for com in range(NUM_CARDS):
                if com == hp0 or com == hp1:
                    continue
                deals.append((hp0, hp1, com))
    return deals
