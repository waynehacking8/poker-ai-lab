"""Engine rules: chip conservation, legal actions, showdown, short all-ins, schedule."""

from __future__ import annotations

import random

import pytest

pytest.importorskip("chipzen")

from chipzen import Action  # noqa: E402

from holdem.engine import Hand, IllegalAction, MatchConfig, blinds_for_hand, play_match  # noqa: E402
from holdem.opponents import (  # noqa: E402
    BASELINES, EXTREMES, Maniac, RandomLegal, make_baseline,
)
from nlhe.cards import card_from_str as c  # noqa: E402


class Script:
    """Plays a fixed list of actions and records every state it was shown."""

    def __init__(self, *actions):
        self.actions = list(actions)
        self.states = []

    def decide(self, state):
        self.states.append(state)
        return self.actions.pop(0)


def deck_of(hole0, hole1, board):
    cards = [c(x) for x in (hole0 + hole1 + board)]
    rest = [x for x in range(52) if x not in cards]
    return cards + rest


def play_hand(bots, stacks, deck, dealer=0, sb=50, bb=100):
    h = Hand(bots, stacks, dealer, 1, sb, bb, deck)
    return h, h.play()


def test_blind_schedule():
    assert blinds_for_hand(1) == (50, 100)
    assert blinds_for_hand(20) == (50, 100)
    assert blinds_for_hand(21) == (75, 150)
    assert blinds_for_hand(61) == (150, 300)
    assert blinds_for_hand(101) == (300, 600)
    assert blinds_for_hand(120) == (300, 600)
    # past 600 the levels are inferred from OFC replays (nothing past hand 146 observed)
    assert blinds_for_hand(121) == (400, 800)
    assert blinds_for_hand(140) == (400, 800)
    assert blinds_for_hand(141) == (500, 1000)
    assert blinds_for_hand(900) == (500, 1000)


def test_showdown_winner_and_conservation():
    deck = deck_of(["Ah", "Ad"], ["Kc", "Ks"], ["2c", "7d", "9h", "Jd", "3s"])
    a = Script(Action.call(), Action.check(), Action.check(), Action.check())
    b = Script(Action.check(), Action.check(), Action.check(), Action.check())
    h, res = play_hand([a, b], [10000, 10000], deck)
    assert res["winner_seats"] == [0]
    assert h.stack == [10100, 9900]
    assert sum(h.stack) == 20000
    assert res["showdown"][0]["hand_rank"] == "Pair"


def test_first_to_act_and_state_fields():
    deck = deck_of(["Ah", "Ad"], ["Kc", "Ks"], ["2c", "7d", "9h", "Jd", "3s"])
    a = Script(Action.raise_to(300), Action.check(), Action.check(), Action.check())
    b = Script(Action.call(), Action.check(), Action.check(), Action.check())
    play_hand([a, b], [10000, 10000], deck, dealer=0)
    first = a.states[0]  # button / small blind acts first preflop
    assert first.phase == "preflop" and first.to_call == 50
    assert first.valid_actions == ["fold", "call", "raise"]
    assert first.min_raise == 200 and first.max_raise == 10000
    assert first.pot == 150
    assert first.opponent_stacks == [9900]
    flop_bb = b.states[1]  # big blind acts first on the flop
    assert flop_bb.phase == "flop" and flop_bb.to_call == 0
    assert flop_bb.valid_actions == ["check", "raise"]
    assert len(flop_bb.board) == 3


def test_fold_pays_pot():
    deck = deck_of(["2h", "3d"], ["Kc", "Ks"], ["2c", "7d", "9h", "Jd", "3s"])
    a = Script(Action.fold())
    b = Script()
    h, res = play_hand([a, b], [10000, 10000], deck)
    assert h.stack == [9950, 10050]
    assert res["showdown"] == []


def test_uncalled_bet_returned_and_short_call():
    # seat 1 has only 500: seat 0 shoves 10000, seat 1 calls for less, excess comes back
    deck = deck_of(["Ah", "Ad"], ["Kc", "Ks"], ["2c", "7d", "9h", "Jd", "3s"])
    a = Script(Action.raise_to(10000))
    b = Script(Action.call())
    h, res = play_hand([a, b], [10000, 500], deck)
    assert h.stack == [10500, 0]
    assert sum(h.stack) == 10500


def test_min_raise_above_max_raise_only_shove():
    deck = deck_of(["Ah", "Ad"], ["Kc", "Ks"], ["2c", "7d", "9h", "Jd", "3s"])
    # seat 0 raises to 1000; seat 1 has 1100 total so min re-raise (1900) > max_raise
    bot0 = Script(Action.raise_to(1000), Action.call())
    bot1 = Script(Action.raise_to(1100))
    h, res = play_hand([bot0, bot1], [10000, 1100], deck)
    st = bot1.states[0]
    assert st.min_raise > st.max_raise == 1100
    assert "raise" in st.valid_actions


def test_short_allin_does_not_reopen():
    deck = deck_of(["2h", "3d"], ["Kc", "Ks"], ["2c", "7d", "9h", "Jd", "3s"])
    # seat 0 raises to 400; seat 1 shoves for 500 total (increment 100 < 300): a short raise
    a = Script(Action.raise_to(400), Action.call())
    b = Script(Action.raise_to(500))
    play_hand([a, b], [10000, 500], deck)
    reply = a.states[1]
    assert reply.to_call == 100
    assert "raise" not in reply.valid_actions


def test_illegal_action_rejected():
    deck = deck_of(["Ah", "Ad"], ["Kc", "Ks"], ["2c", "7d", "9h", "Jd", "3s"])
    a = Script(Action.check())  # facing the small blind completion: check is illegal
    with pytest.raises(IllegalAction):
        play_hand([a, Script()], [10000, 10000], deck)


@pytest.mark.parametrize("name", sorted(BASELINES) + sorted(EXTREMES))
def test_baselines_play_legal_matches_and_conserve_chips(name):
    for seed in range(3):
        bots = [make_baseline(name, seed), RandomLegal(seed)]
        res = play_match(bots, seed, MatchConfig(max_hands=60))
        assert sum(res.stacks) == 20000


def test_match_ends_on_bust_and_is_deterministic():
    r1 = play_match([Maniac(1), Maniac(2)], 5)
    r2 = play_match([Maniac(1), Maniac(2)], 5)
    assert (r1.hands, r1.stacks) == (r2.hands, r2.stacks)
    assert 0 in r1.stacks and r1.winner is not None


def test_random_bots_random_seeds_conserve_chips():
    rng = random.Random(3)
    for _ in range(40):
        s = rng.randrange(10**6)
        res = play_match([RandomLegal(s), RandomLegal(s + 1)], s, MatchConfig(max_hands=80))
        assert sum(res.stacks) == 20000


class FoldIfPossible:
    def __init__(self):
        self.states = []

    def decide(self, state):
        self.states.append(state)
        return Action.fold() if "fold" in state.valid_actions else Action.check()


def test_small_blind_not_prompted_when_big_blind_all_in_for_no_more_than_the_small_blind():
    """Real server (match 53990391 hand 9): BB all in for 20 under a 50 small blind, no prompt."""
    deck = deck_of(["Ah", "Ad"], ["7c", "2d"], ["Ks", "9h", "4c", "Jd", "3s"])
    bots = [FoldIfPossible(), FoldIfPossible()]
    h = Hand(bots, [10000, 20], 0, 9, 50, 100, deck)
    result = h.play()
    assert bots[0].states == [] and bots[1].states == []  # nobody is asked
    assert result["showdown"]  # straight to showdown
    assert h.stack == [10020, 0]  # seat 0 wins the 40 contested and its 30 comes back
    assert sum(h.stack) == 10020
    # the same spot with seat 0 losing: it still gets the 30 back
    deck = deck_of(["7c", "2d"], ["Ah", "Ad"], ["Ks", "9h", "4c", "Jd", "3s"])
    h = Hand([FoldIfPossible(), FoldIfPossible()], [10000, 20], 0, 9, 50, 100, deck)
    h.play()
    assert h.stack == [9980, 40]


def test_small_blind_prompted_when_short_big_blind_post_exceeds_the_small_blind():
    """Real server (554b8185 hand 13): BB posts 93 under a 100 big blind, SB owes 43."""
    bots = [FoldIfPossible(), FoldIfPossible()]
    h = Hand(bots, [10000, 93], 0, 13, 50, 100, list(range(52)))
    h.play()
    assert len(bots[0].states) == 1
    st = bots[0].states[0]
    assert st.valid_actions == ["fold", "call"] and st.to_call == 43
