"""The Hold'em bot: legality on arbitrary states, multiway safety, stats and a smoke match."""

from __future__ import annotations

import dataclasses
import random

import pytest

pytest.importorskip("chipzen")

from chipzen.models import Card, GameState  # noqa: E402

from bot import HoldemBot  # noqa: E402
from holdem.engine import MatchConfig, play_match  # noqa: E402
from holdem.opponents import BASELINES, make_baseline  # noqa: E402
from nlhe.history import parse_history  # noqa: E402
from nlhe.model import OpponentModel  # noqa: E402


def cards(*s):
    return [Card.from_str(x) for x in s]


def hist(*entries):
    return [{"seat": s, "action": a, "amount": n, "phase": p, "is_timeout": False}
            for s, a, n, p in entries]


def check_legal(bot, state):
    act = bot.decide(state)
    assert act.action in state.valid_actions, (act, state.valid_actions)
    assert act.action != "all_in"
    if act.action == "raise":
        lo = min(state.min_raise, state.max_raise)
        assert lo <= act.amount <= state.max_raise
    return act


def test_never_illegal_against_every_baseline():
    """The engine runs in strict mode: any illegal action raises."""
    for name in BASELINES:
        for seed in range(2):
            bots = [HoldemBot(seed), make_baseline(name, seed)]
            if seed:
                bots.reverse()
            res = play_match(bots, seed, MatchConfig(max_hands=80))
            assert sum(res.stacks) == 20000


def test_min_raise_above_max_raise_returns_shove_or_call():
    state = GameState(
        hand_number=3, phase="flop", hole_cards=cards("Ah", "Ad"), board=cards("2c", "7d", "9h"),
        pot=1500, your_stack=300, opponent_stacks=[5000], your_seat=0, dealer_seat=0,
        to_call=100, min_raise=900, max_raise=300, valid_actions=["fold", "call", "raise"],
        action_history=hist((0, "post_small_blind", 50, "preflop"),
                            (1, "post_big_blind", 100, "preflop"),
                            (0, "call", 50, "preflop"), (1, "check", 0, "preflop"),
                            (1, "raise", 100, "flop")),
    )
    act = check_legal(HoldemBot(1), state)
    assert act.action in ("raise", "call")
    if act.action == "raise":
        assert act.amount == 300


def test_multiway_state_does_not_crash():
    """Four opponent stacks (a 5 seat table): aggregate, never index opponent_stacks[0]."""
    h = hist((1, "post_small_blind", 50, "preflop"), (2, "post_big_blind", 100, "preflop"),
             (3, "fold", 0, "preflop"), (4, "call", 100, "preflop"), (0, "raise", 300, "preflop"),
             (1, "fold", 0, "preflop"), (2, "call", 200, "preflop"), (4, "call", 200, "preflop"))
    state = GameState(
        hand_number=9, phase="preflop", hole_cards=cards("Ks", "Kd"), board=[], pot=950,
        your_stack=9700, opponent_stacks=[9950, 9700, 0, 9700], your_seat=0, dealer_seat=0,
        to_call=0, min_raise=400, max_raise=9700, valid_actions=["check", "raise"],
        action_history=h,
    )
    check_legal(HoldemBot(2), state)
    flop = dataclasses.replace(state, phase="flop", board=cards("2c", "7d", "Kh"),
                               action_history=h + hist((2, "check", 0, "flop")))
    check_legal(HoldemBot(2), flop)


def test_random_states_always_legal():
    rng = random.Random(4)
    ranks, suits = "23456789TJQKA", "hdcs"
    deck = [r + s for r in ranks for s in suits]
    bot = HoldemBot(5)
    for _ in range(150):
        n_board = rng.choice([0, 3, 4, 5])
        picks = rng.sample(deck, 2 + n_board)
        phase = {0: "preflop", 3: "flop", 4: "turn", 5: "river"}[n_board]
        stack = rng.choice([300, 1500, 9000])
        pot = rng.choice([150, 600, 3000])
        to_call = rng.choice([0, 0, 100, 400, stack])
        h = hist((0, "post_small_blind", 50, "preflop"), (1, "post_big_blind", 100, "preflop"))
        valid = ["check", "raise"] if to_call == 0 else ["fold", "call", "raise"]
        if to_call >= stack:
            valid = ["fold", "call"]
        state = GameState(
            hand_number=1, phase=phase, hole_cards=cards(*picks[:2]), board=cards(*picks[2:]),
            pot=pot, your_stack=stack, opponent_stacks=[rng.choice([300, 9000])], your_seat=0,
            dealer_seat=rng.choice([0, 1]), to_call=to_call, min_raise=max(200, to_call * 2),
            max_raise=stack, valid_actions=valid, action_history=h,
        )
        check_legal(bot, state)


def test_preflop_folds_count_towards_fold_to_bet():
    """A bot that folds every big blind to our raise must read as a folder."""
    model = OpponentModel()
    for _ in range(12):
        result = {"action_history": hist(
            (0, "post_small_blind", 50, "preflop"), (1, "post_big_blind", 100, "preflop"),
            (0, "raise", 250, "preflop"), (1, "fold", 0, "preflop")), "showdown": []}
        model.observe_hand(result, my_seat=0)
    s = model.get(1)
    assert s.fold_to_bet_all.rate() > 0.65
    assert s.pre_fold_to_raise.rate() > 0.6
    assert s.hands == 12


def test_parse_history_amounts():
    h = hist((0, "post_small_blind", 50, "preflop"), (1, "post_big_blind", 100, "preflop"),
             (0, "raise", 300, "preflop"), (1, "call", 200, "preflop"),
             (1, "raise", 400, "flop"), (0, "call", 400, "flop"))
    info = parse_history(h)
    assert info.pot == 1400
    assert info.contrib == {0: 700, 1: 700}
    assert info.big_blind == 100 and info.preflop_raises == 1
    assert info.events[0].raises_before == 0 and info.events[1].facing


def test_shoves_premium_and_folds_trash_short_stacked():
    """At 8 bb the small blind shoves AA and does not shove 72o against the Nash call range."""
    def state(c1, c2):
        h = hist((0, "post_small_blind", 400, "preflop"), (1, "post_big_blind", 800, "preflop"))
        return GameState(
            hand_number=1, phase="preflop", hole_cards=cards(c1, c2), board=[], pot=1200,
            your_stack=6000, opponent_stacks=[6400], your_seat=0, dealer_seat=0,
            to_call=400, min_raise=1600, max_raise=6400, valid_actions=["fold", "call", "raise"],
            action_history=h)
    bot = HoldemBot(3)
    assert bot.decide(state("Ah", "Ad")).action == "raise"
    assert bot.decide(state("7h", "2d")).action in ("fold", "call")  # never a shove; may complete


@pytest.mark.slow
def test_beats_calling_station_most_of_the_time():
    wins = 0
    for seed in range(20):
        bots = [HoldemBot(seed), make_baseline("station", seed)]
        if seed % 2:
            bots.reverse()
        res = play_match(bots, seed)
        hero = 1 if seed % 2 else 0
        wins += res.winner == hero
    assert wins >= 15
