"""The four field-style rule bots: legal play, determinism, and a stronger hand never folds more."""

from __future__ import annotations

import pytest

pytest.importorskip("chipzen")

from chipzen.models import Card, GameState  # noqa: E402

from holdem.engine import MatchConfig, play_match  # noqa: E402
from holdem.opponents import (  # noqa: E402
    BASELINES, EXTREMES, STYLES, RandomLegal, make_baseline, postflop_strength, preflop_pct,
)

NAMES = sorted(STYLES)


def cards(*s):
    return [Card.from_str(x) for x in s]


def hist(*entries):
    return [{"seat": s, "action": a, "amount": n, "phase": p, "is_timeout": False}
            for s, a, n, p in entries]


def test_styles_are_separate_from_the_league():
    assert not set(STYLES) & (set(BASELINES) | set(EXTREMES))
    for name in NAMES:
        assert make_baseline(name, 1).name == name


@pytest.mark.parametrize("name", NAMES)
def test_legal_over_hundreds_of_hands(name):
    """The engine runs in strict mode: any illegal action raises."""
    hands = 0
    for seed in range(80):
        bots = [make_baseline(name, seed), RandomLegal(seed)]
        if seed % 2:
            bots.reverse()
        res = play_match(bots, seed, MatchConfig(max_hands=150))
        assert sum(res.stacks) == 20000
        hands += res.hands
    assert hands >= 200


@pytest.mark.parametrize("name", NAMES)
def test_deterministic_for_a_fixed_seed(name):
    def run(seed):
        res = play_match([make_baseline(name, seed), RandomLegal(5)], 9, MatchConfig(max_hands=120))
        return res.hands, res.stacks
    assert run(4) == run(4)


def post_state(hole, bet=300):
    """Flop, we are first to act and face a bet of `bet` into a pot of 600."""
    return GameState(
        hand_number=3, phase="flop", hole_cards=cards(*hole), board=cards("2c", "7d", "9h"),
        pot=600 + bet, your_stack=9000, opponent_stacks=[8500], your_seat=0, dealer_seat=0,
        to_call=bet, min_raise=2 * bet, max_raise=9000, valid_actions=["fold", "call", "raise"],
        action_history=hist((0, "post_small_blind", 50, "preflop"), (1, "post_big_blind", 100, "preflop"),
                            (0, "call", 50, "preflop"), (1, "check", 0, "preflop"),
                            (1, "raise", bet, "flop")),
    )


def pre_state(hole, raised):
    hh = [(0, "post_small_blind", 50, "preflop"), (1, "post_big_blind", 100, "preflop")]
    if raised:
        hh.append((1, "raise", 300, "preflop"))
        return GameState(
            hand_number=3, phase="preflop", hole_cards=cards(*hole), board=[], pot=350,
            your_stack=9950, opponent_stacks=[9700], your_seat=0, dealer_seat=0, to_call=250,
            min_raise=500, max_raise=9950, valid_actions=["fold", "call", "raise"],
            action_history=hist(*hh))
    return GameState(
        hand_number=3, phase="preflop", hole_cards=cards(*hole), board=[], pot=150,
        your_stack=9950, opponent_stacks=[9900], your_seat=0, dealer_seat=0, to_call=50,
        min_raise=200, max_raise=9950, valid_actions=["fold", "call", "raise"], action_history=hist(*hh))


def fold_count(name, state, n=400):
    """Same seeds for every hand, so each decision sees the same draw: fold sets are nested."""
    return sum(make_baseline(name, k).decide(state).action == "fold" for k in range(n))


def test_postflop_ladder_is_what_the_test_assumes():
    ladder = [("Ks", "4d"), ("4d", "2h"), ("9s", "4d"), ("Kd", "Ks"), ("9s", "9d")]
    state = post_state(ladder[0])
    levels = []
    for hole in ladder:
        state = post_state(hole)
        level, draw = postflop_strength(state)
        assert not draw
        levels.append(level)
    assert levels == [0, 1, 2, 3, 4]


@pytest.mark.parametrize("name", NAMES)
def test_stronger_postflop_hand_never_folds_more(name):
    ladder = [("Ks", "4d"), ("4d", "2h"), ("9s", "4d"), ("Kd", "Ks"), ("9s", "9d")]
    folds = [fold_count(name, post_state(h)) for h in ladder]
    assert folds == sorted(folds, reverse=True), folds


@pytest.mark.parametrize("raised", [False, True])
@pytest.mark.parametrize("name", NAMES)
def test_stronger_preflop_hand_never_folds_more(name, raised):
    ladder = [("7c", "2d"), ("9c", "3d"), ("Th", "6d"), ("Jh", "9d"), ("Kh", "Qs"), ("As", "Ad")]
    pcts = [preflop_pct(pre_state(h, raised)) for h in ladder]
    assert pcts == sorted(pcts)
    folds = [fold_count(name, pre_state(h, raised)) for h in ladder]
    assert folds == sorted(folds, reverse=True), folds


def test_the_station_styles_never_fold_to_a_raise_or_after_the_flop():
    for name in ("raise_station", "never_fold_pre"):
        assert all(fold_count(name, pre_state(h, True)) == 0 for h in [("7c", "2d"), ("As", "Ad")])
    assert fold_count("raise_station", post_state(("Ks", "4d"))) == 0
