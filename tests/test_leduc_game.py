"""Tests for the Leduc Hold'em game module — purely about the tree, not CFR.

Pot accounting, legal actions per state, round transitions, fold vs.
showdown payoffs, and the zero-sum invariant. None of these depend on
which algorithm uses the game later; they freeze the contract that
``vanilla_cfr.train(leduc, ...)`` will rely on.
"""

from __future__ import annotations

import pytest

from cfr.games import leduc


# ---------------------------------------------------------------------------
# Combinatorial properties of the game tree.
# ---------------------------------------------------------------------------


def test_120_ordered_deals():
    assert len(leduc.all_deals()) == 6 * 5 * 4
    assert len(set(leduc.all_deals())) == 6 * 5 * 4  # all distinct
    # Every triple has 3 distinct cards.
    for hp0, hp1, com in leduc.all_deals():
        assert len({hp0, hp1, com}) == 3


def test_legal_actions_per_state():
    # Round opening: either player can check or bet.
    assert leduc.legal_actions("") == ("c", "r")
    assert leduc.legal_actions("c") == ("c", "r")  # P2 facing a check
    # Bet pending below cap: fold/call/raise.
    assert leduc.legal_actions("r") == ("f", "c", "r")
    assert leduc.legal_actions("rr") == ("f", "c", "r")
    assert leduc.legal_actions("cr") == ("f", "c", "r")
    assert leduc.legal_actions("crr") == ("f", "c", "r")
    # At cap (1 opening bet + 2 raises): fold or call only.
    assert leduc.legal_actions("rrr") == ("f", "c")
    assert leduc.legal_actions("crrr") == ("f", "c")
    # Round 2 inherits the same rules.
    assert leduc.legal_actions("cc/") == ("c", "r")
    assert leduc.legal_actions("cc/rrr") == ("f", "c")


def test_round_one_auto_transition():
    # Round-1-closing call/check appends '/' so callers stay round-agnostic.
    for h in ["", "c", "r", "cr", "rr", "crr", "rrr", "crrr"]:
        for a in leduc.legal_actions(h):
            nxt = leduc.next_history(h, a)
            # If the round-1 sequence now ends in a non-fold close, '/' must be appended.
            if "/" not in nxt and not nxt.endswith("f"):
                # Either still in round 1, or terminal-by-fold. Either way not '/'.
                assert not nxt.endswith("c") or not (len(nxt) > 1 and nxt[-2] in ("c", "r"))


def test_terminal_detection():
    terminals_expected_round1 = ["rf", "rrf", "rrrf", "crf", "crrf", "crrrf"]
    for h in terminals_expected_round1:
        assert leduc.is_terminal(h), h
    # 'cc' is NOT a terminal — it transitions to round 2 via 'cc/'.
    assert not leduc.is_terminal("cc")
    assert not leduc.is_terminal("cc/")
    # Round-2 closings are terminal.
    for h in ["cc/cc", "cc/rc", "cc/rf", "cc/rrc", "cc/rrf", "cc/rrrc", "cc/rrrf"]:
        assert leduc.is_terminal(h), h


def test_current_player_alternates_within_each_round():
    # Round 1.
    assert leduc.current_player("") == 0
    assert leduc.current_player("c") == 1
    assert leduc.current_player("cr") == 0
    assert leduc.current_player("rr") == 0
    # Round 2 resets — P1 acts first postflop.
    assert leduc.current_player("cc/") == 0
    assert leduc.current_player("cc/c") == 1
    assert leduc.current_player("cc/cr") == 0


# ---------------------------------------------------------------------------
# Pot accounting and terminal utility — zero-sum, contributions correct.
# ---------------------------------------------------------------------------


def test_both_check_throughout_pays_only_antes():
    # cc/cc: both players checked both rounds, antes only at risk.
    # Pick a deal where P0 wins on high card.
    cards = (4, 0, 2)  # K, J, Q — P0 wins (K > J, neither pairs Q)
    assert leduc.terminal_utility("cc/cc", cards) == 1.0
    # Reverse: P1 has the K.
    cards = (0, 4, 2)
    assert leduc.terminal_utility("cc/cc", cards) == -1.0


def test_fold_in_round_one_loses_ante():
    # P1 bets, P2 folds → P1 wins P2's 1-chip ante.
    cards = (0, 2, 4)  # ranks don't matter on a fold
    assert leduc.terminal_utility("rf", cards) == 1.0
    # P1 checks, P2 bets, P1 folds → P1 loses 1.
    assert leduc.terminal_utility("crf", cards) == -1.0


def test_round_one_bet_size_2_round_two_bet_size_4():
    # Sequence: cc/rc — both checked round 1, then in round 2 P1 bets (4) and
    # P2 calls. Both put in 4 + ante = 5. Winner gets 5 (P1's perspective: +5
    # if P0 wins, -5 if P1 wins).
    cards = (4, 0, 2)  # P0 (=P1) wins on K
    assert leduc.terminal_utility("cc/rc", cards) == 5.0
    # rrc/cc — round 1 had bet+raise+call (so each put in 4 of round-1 chips).
    cards = (4, 0, 2)
    assert leduc.terminal_utility("rrc/cc", cards) == 5.0  # 1 ante + 4 round-1
    # rrc/rrrc — round 1 capped + round 2 capped (each put in 4 then 12).
    cards = (4, 0, 2)
    assert leduc.terminal_utility("rrc/rrrc", cards) == 17.0  # 1 + 4 + 12


def test_pair_beats_non_pair_on_showdown():
    # P0 has J, P1 has K, community is J → P0 pairs and wins.
    cards = (0, 4, 1)  # J(0), K(4), J(1)
    # Showdown via cc/cc (1 chip stake).
    assert leduc.terminal_utility("cc/cc", cards) == 1.0
    # P1 has K, P0 has J, community is K — P1 pairs and wins.
    cards = (0, 4, 5)
    assert leduc.terminal_utility("cc/cc", cards) == -1.0


def test_tie_splits_pot():
    # Both players hold a J (the only way to tie: same hole rank, neither pairs).
    cards = (0, 1, 4)  # J, J, K — neither pairs the K, tie on hole rank
    assert leduc.terminal_utility("cc/cc", cards) == 0.0
    # Same tie under a fatter pot.
    assert leduc.terminal_utility("rrc/rrrc", cards) == 0.0


def test_terminal_utility_zero_sum_under_negation():
    """Swapping the two hole cards must negate the utility (game is symmetric)."""
    histories = ["rf", "crf", "rc", "cc/cc", "cc/rc", "rrc/rrrc"]
    for hp0 in range(6):
        for hp1 in range(6):
            if hp0 == hp1:
                continue
            for com in range(6):
                if com in (hp0, hp1):
                    continue
                for h in histories:
                    direct = leduc.terminal_utility(h, (hp0, hp1, com))
                    swapped = leduc.terminal_utility(h, (hp1, hp0, com))
                    # Symmetry only holds for *symmetric* histories — folds
                    # are asymmetric. For pure-call histories the game is
                    # symmetric (same chips in, only the cards decide).
                    if h.endswith("c") and "f" not in h:
                        assert direct == pytest.approx(-swapped), (h, hp0, hp1, com)


# ---------------------------------------------------------------------------
# Info-set keys and depth invariants.
# ---------------------------------------------------------------------------


def test_info_set_count_per_player():
    """264 info sets per player — 12 preflop + 252 postflop."""
    seen_p0: set[str] = set()
    seen_p1: set[str] = set()

    def dfs(history, cards):
        if leduc.is_terminal(history):
            return
        cur = leduc.current_player(history)
        key = leduc.info_set_key(cur, cards, history)
        (seen_p0 if cur == 0 else seen_p1).add(key)
        for action in leduc.legal_actions(history):
            dfs(leduc.next_history(history, action), cards)

    for cards in leduc.all_deals():
        dfs("", cards)

    assert len(seen_p0) == 264
    assert len(seen_p1) == 264


def test_info_set_key_hides_opponent_card():
    """Two deals that differ ONLY in the opponent's hole card must produce
    the same info-set key for ``player``."""
    h = "cr"  # P0's turn in round 1
    a = leduc.info_set_key(0, (0, 2, 4), h)  # P1 has Q
    b = leduc.info_set_key(0, (0, 3, 4), h)  # P1 has the other Q
    c = leduc.info_set_key(0, (0, 4, 5), h)  # P1 has K (different rank!)
    assert a == b == c  # P0 can't see P1's card; no community yet.


def test_info_set_key_reveals_community_postflop():
    """After the round-1 separator, the community card is part of the key."""
    h = "cc/cr"  # P0 acting postflop
    a = leduc.info_set_key(0, (0, 2, 4), h)  # community = K
    b = leduc.info_set_key(0, (0, 2, 0), h)  # community = J (same rank as P0)
    assert a != b
