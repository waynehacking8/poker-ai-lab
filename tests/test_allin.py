"""The all-in answer (rl/allin.py): shove counting, the width gate and the call decision."""

import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rl  # noqa: E402,F401
from rl.allin import DEFAULT_TABLE, AllInAnswer  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(DEFAULT_TABLE), reason="python tools/allin_tables.py first")


def shove_hand(opp_shows=None, stacks=(10000, 10000)):
    """Seat 1 posts the small blind and shoves, seat 0 (us) folds or calls."""
    hist = [{"seat": 1, "action": "post_small_blind", "amount": 50, "phase": "preflop"},
            {"seat": 0, "action": "post_big_blind", "amount": 100, "phase": "preflop"},
            {"seat": 1, "action": "raise", "amount": 10000, "phase": "preflop"},
            {"seat": 0, "action": "fold", "amount": 0, "phase": "preflop"}]
    res = {"action_history": hist, "stacks": list(stacks), "showdown": []}
    if opp_shows:
        hist[-1] = {"seat": 0, "action": "call", "amount": 9900, "phase": "preflop"}
        res["showdown"] = [{"seat": 1, "hole_cards": opp_shows}, {"seat": 0, "hole_cards": ["As", "Ad"]}]
    return res


def facing_shove(hole, hand=5, stack=9900):
    return SimpleNamespace(phase="preflop", to_call=stack, valid_actions=["fold", "call"], opponent_stacks=[0],
                           your_stack=stack, your_seat=0, hole_cards=hole, hand_number=hand)


def test_one_shove_is_left_to_the_policy():
    a = AllInAnswer()
    a.reset(0, 10000)
    a.round_result(shove_hand(stacks=(9900, 10100)))
    assert a.shoves == 1 and a.chances == 1
    assert a.freq() < 0.7
    assert not a.should_call(facing_shove(["Ah", "Ad"]))


def test_a_spammer_gets_called_with_strong_hands_only():
    a = AllInAnswer()
    a.reset(0, 10000)
    for _ in range(6):
        a.round_result(shove_hand())
    assert a.width() > 0.6
    assert a.should_call(facing_shove(["Ah", "Ad"]))
    assert a.should_call(facing_shove(["Ah", "Kd"]))
    assert not a.should_call(facing_shove(["7h", "2d"]))


def test_a_weak_shown_shove_widens_the_range_at_once():
    a = AllInAnswer()
    a.reset(0, 10000)
    a.round_result(shove_hand(opp_shows=["7c", "2s"]))
    assert a.width() > 0.95


def test_only_all_in_decisions_are_answered():
    a = AllInAnswer()
    a.reset(0, 10000)
    for _ in range(6):
        a.round_result(shove_hand())
    raise_only = SimpleNamespace(phase="preflop", to_call=200, valid_actions=["fold", "call", "raise"],
                                 opponent_stacks=[9700], your_stack=9900, your_seat=0, hole_cards=["Ah", "Ad"],
                                 hand_number=5)
    assert not a.should_call(raise_only)
    flop = facing_shove(["Ah", "Ad"])
    flop.phase = "flop"
    assert not a.should_call(flop)


def sb_first(hole, hand=7):
    hist = [{"seat": 0, "action": "post_small_blind", "amount": 50, "phase": "preflop"},
            {"seat": 1, "action": "post_big_blind", "amount": 100, "phase": "preflop"}]
    return SimpleNamespace(phase="preflop", to_call=50, valid_actions=["fold", "call", "raise"],
                           opponent_stacks=[9900], your_stack=9950, your_seat=0, hole_cards=hole,
                           hand_number=hand, action_history=hist)


def test_small_blind_folds_trash_up_front_against_a_near_certain_shover():
    a = AllInAnswer()
    a.reset(0, 10000)
    a.round_result(shove_hand())
    a.round_result(shove_hand())
    assert not a.should_fold_first(sb_first(["7h", "2d"]))  # two shoves: frequency 0.68, not yet
    for _ in range(8):
        a.round_result(shove_hand())
    assert a.should_fold_first(sb_first(["7h", "2d"]))
    assert not a.should_fold_first(sb_first(["Ah", "Ad"]))
