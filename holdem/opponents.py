"""Baseline opponents for the local arena.

Each one is a plain object with ``decide(state)`` (and no hooks), so it plays
through the same ``GameState`` / ``Action`` objects as the real bot.
"""

from __future__ import annotations

import random

from chipzen import Action

from nlhe import preflop as pf
from nlhe.cards import cards_from, hand_class
from nlhe.evaluator import category, evaluate
from nlhe.ranges import draw_bonus


def preflop_pct(state) -> float:
    a, b = cards_from(state.hole_cards)
    return pf.PCT[hand_class(a, b)]


def postflop_strength(state) -> tuple[int, bool]:
    """(0 nothing, 1 weak pair, 2 top pair, 3 overpair or two pair, 4 trips or better, draw?)."""
    hole = cards_from(state.hole_cards)
    board = cards_from(state.board)
    score = evaluate(hole + board)
    cat = category(score)
    top = max(c >> 2 for c in board)
    pair_hole = (hole[0] >> 2) == (hole[1] >> 2)
    if cat >= 3:
        level = 4
    elif cat == 2:
        level = 3
    elif cat == 1:
        hr = [c >> 2 for c in hole]
        if pair_hole and hr[0] > top:
            level = 3
        elif max(hr) == top and top in hr:
            level = 2
        else:
            level = 1
    else:
        level = 0
    draw = len(board) < 5 and draw_bonus(hole, board) >= 0.1
    return level, draw


def raise_to(state, target):
    if "raise" not in state.valid_actions:
        return call_or_check(state)
    lo = min(state.min_raise, state.max_raise)
    return Action.raise_to(int(max(lo, min(state.max_raise, target))))


def call_or_check(state):
    return Action.call() if "call" in state.valid_actions else Action.check()


def check_or_fold(state):
    return Action.check() if "check" in state.valid_actions else Action.fold()


def my_street_bet(state) -> int:
    """Chips we already have in on the current street (from the history)."""
    total = 0
    for e in state.action_history:
        if e["seat"] == state.your_seat and e["phase"] == state.phase:
            if e["action"] == "raise":
                total = e["amount"]
            else:
                total += e["amount"] if e["action"] in ("call", "post_small_blind",
                                                        "post_big_blind") else 0
    return total


class CallingStation:
    """Never folds, never raises."""

    name = "station"

    def decide(self, state):
        return call_or_check(state)


class Maniac:
    """Raises or shoves almost every time."""

    name = "maniac"

    def __init__(self, seed=0):
        self.rng = random.Random(seed)

    def decide(self, state):
        r = self.rng.random()
        if "raise" in state.valid_actions and r < 0.75:
            if r < 0.25:
                return Action.raise_to(state.max_raise)
            size = my_street_bet(state) + state.to_call + 0.8 * (state.pot + state.to_call)
            return raise_to(state, max(size, state.min_raise))
        return call_or_check(state)


class Nit:
    """Tight and passive: premium hands only, folds to any bet without a strong hand."""

    name = "nit"

    def decide(self, state):
        if state.phase == "preflop":
            p = preflop_pct(state)
            if p >= 0.97 and "raise" in state.valid_actions:
                return raise_to(state, 3 * state.min_raise)
            if p >= 0.86 or state.to_call == 0:
                return call_or_check(state)
            if state.to_call <= state.pot // 3 and p >= 0.75:
                return call_or_check(state)
            return check_or_fold(state)
        level, _ = postflop_strength(state)
        if level >= 3:
            if state.to_call == 0 and "raise" in state.valid_actions:
                return raise_to(state, my_street_bet(state) + 0.5 * state.pot)
            return call_or_check(state)
        if level == 2 and state.to_call <= state.pot // 2:
            return call_or_check(state)
        return check_or_fold(state)


class RandomLegal:
    """Uniformly random legal action; raise amounts uniform in the legal range."""

    name = "random"

    def __init__(self, seed=0):
        self.rng = random.Random(seed)

    def decide(self, state):
        kind = self.rng.choice(state.valid_actions)
        if kind == "raise":
            lo = min(state.min_raise, state.max_raise)
            return Action.raise_to(self.rng.randint(lo, state.max_raise))
        return Action(kind)


class ReferenceBot:
    """The SDK reference bot's strategy (examples/reference-bot/bot.py), history-driven.

    Position-blind rank buckets preflop, made-hand class postflop, folds to
    pressure, never bluffs.
    """

    name = "reference"

    @staticmethod
    def _bucket(state) -> str:
        a, b = state.hole_cards
        ranks = "23456789TJQKA"
        ri = {r: i for i, r in enumerate(ranks)}
        hi, lo = sorted((a.rank, b.rank), key=lambda r: ri[r], reverse=True)
        suited = a.suit == b.suit
        if a.rank == b.rank:
            return "premium" if a.rank in "JQKA" else "strong" if a.rank in "9T" else "medium"
        if {hi, lo} == {"A", "K"}:
            return "premium"
        if hi == "A" and lo in "QJT":
            return "strong" if suited else "medium"
        if hi == "K" and lo in "QJ":
            return "strong" if suited else "medium"
        if hi in "QJ" and lo in "T9":
            return "strong" if suited else "medium"
        if hi == "A":
            return "medium"
        return "weak"

    @staticmethod
    def _bounded(state, target):
        if state.min_raise == 0 or state.max_raise == 0:
            return None
        return min(state.max_raise, max(state.min_raise, target))  # server clamps the same way

    def decide(self, state):
        valid = state.valid_actions
        opp_raises = sum(
            1 for e in state.action_history
            if e["seat"] != state.your_seat and e["action"] in ("raise", "all_in")
        )
        if state.phase == "preflop":
            return self._pre(state, valid)
        return self._post(state, valid, opp_raises)

    def _pre(self, state, valid):
        bucket = self._bucket(state)
        if bucket == "premium":
            t = self._bounded(state, state.min_raise * 3)
            if t is not None and "raise" in valid:
                return Action.raise_to(t)
            return Action.call() if "call" in valid else check_or_fold(state)
        if bucket == "strong":
            if state.to_call == 0 and "raise" in valid:
                t = self._bounded(state, state.min_raise * 2)
                if t is not None:
                    return Action.raise_to(t)
            if "call" in valid and state.to_call <= state.your_stack // 10:
                return Action.call()
            return check_or_fold(state)
        if bucket == "medium":
            if "check" in valid:
                return Action.check()
            if "call" in valid and state.to_call <= state.your_stack // 30:
                return Action.call()
            return Action.fold()
        return check_or_fold(state)

    def _post(self, state, valid, opp_raises):
        from collections import Counter

        ranks = [c >> 2 for c in cards_from(state.hole_cards) + cards_from(state.board)]
        counts = sorted(Counter(ranks).values(), reverse=True)
        klass = 3 if counts[0] >= 3 else 2 if counts[:2] == [2, 2] else 1 if counts[0] == 2 else 0
        if klass >= 2:
            if "raise" in valid and opp_raises == 0:
                t = self._bounded(state, int(state.pot * 0.66))
                if t is not None:
                    return Action.raise_to(t)
            return Action.call() if "call" in valid else check_or_fold(state)
        if klass == 1:
            if "check" in valid:
                return Action.check()
            if "call" in valid and state.to_call <= state.pot // 3:
                return Action.call()
            return Action.fold()
        return check_or_fold(state)


class LooseAggressive:
    """Field-like: opens ~75% of buttons to 2.5x, defends ~55% of big blinds, c-bets often,
    folds to big pressure."""

    name = "lag"

    def __init__(self, seed=0):
        self.rng = random.Random(seed)

    def decide(self, state):
        valid = state.valid_actions
        bb = max((e["amount"] for e in state.action_history if e["action"] == "post_big_blind"),
                 default=100)
        facing_raise = any(e["action"] == "raise" and e["phase"] == "preflop"
                           for e in state.action_history)
        if state.phase == "preflop":
            p = preflop_pct(state)
            if not facing_raise:
                if state.to_call > 0:  # button, first in
                    return raise_to(state, 2.5 * bb) if p >= 0.25 else check_or_fold(state)
                return raise_to(state, 3.5 * bb) if p >= 0.7 else Action.check()
            if p >= 0.92:
                return raise_to(state, 3 * (state.to_call + my_street_bet(state)))
            if p >= 0.45 and state.to_call <= 0.15 * state.your_stack:
                return call_or_check(state)
            return check_or_fold(state)
        level, draw = postflop_strength(state)
        big = state.to_call > 0.75 * max(state.pot - state.to_call, 1)
        if state.to_call == 0:
            if "raise" in valid and (level >= 2 or draw or self.rng.random() < 0.65):
                return raise_to(state, 0.5 * state.pot)
            return Action.check()
        if level >= 3 or (level == 2 and not big):
            return raise_to(state, my_street_bet(state) + state.to_call + 0.7 * state.pot) \
                if level >= 4 else call_or_check(state)
        if (level >= 1 or draw) and not big:
            return call_or_check(state)
        return check_or_fold(state)


class StationRaiser:
    """Calls down light (any pair or draw), raises strong pairs and better."""

    name = "station_raiser"

    def decide(self, state):
        valid = state.valid_actions
        if state.phase == "preflop":
            p = preflop_pct(state)
            if p >= 0.9 and "raise" in valid:
                return raise_to(state, 3 * state.min_raise)
            if p >= 0.3 or state.to_call == 0:
                return call_or_check(state)
            return check_or_fold(state)
        level, draw = postflop_strength(state)
        if level >= 3 and "raise" in valid:
            return raise_to(state, my_street_bet(state) + state.to_call + 0.75 * state.pot)
        if level >= 1 or draw or state.to_call == 0:
            return call_or_check(state)
        return check_or_fold(state)


BASELINES = {
    "station": CallingStation,
    "maniac": Maniac,
    "nit": Nit,
    "random": RandomLegal,
    "reference": ReferenceBot,
    "lag": LooseAggressive,
    "station_raiser": StationRaiser,
}



class Jam:
    """Shoves whenever a raise is legal, otherwise calls. Regression bot for the all-in fix."""

    name = "jam"

    def __init__(self, seed=0):
        pass

    def decide(self, state):
        if "raise" in state.valid_actions:
            return Action.raise_to(state.max_raise)
        return call_or_check(state)


class JamHalf:
    """Shoves any two cards on half of its decisions, otherwise calls or checks."""

    name = "jam_half"

    def __init__(self, seed=0):
        self.rng = random.Random(seed)

    def decide(self, state):
        if "raise" in state.valid_actions and self.rng.random() < 0.5:
            return Action.raise_to(state.max_raise)
        return call_or_check(state)


class JamPost:
    """Calls or checks preflop, then shoves every later street."""

    name = "jam_post"

    def __init__(self, seed=0):
        pass

    def decide(self, state):
        if state.phase != "preflop" and "raise" in state.valid_actions:
            return Action.raise_to(state.max_raise)
        return call_or_check(state)


class MinRaiser:
    """Min-raises whenever it can, otherwise calls."""

    name = "minraiser"

    def __init__(self, seed=0):
        pass

    def decide(self, state):
        if "raise" in state.valid_actions:
            return raise_to(state, state.min_raise)
        return call_or_check(state)


# Extreme strategies a human can play against us online; not part of "all" or the league.
EXTREMES = {
    "jam": Jam,
    "jam_half": JamHalf,
    "jam_post": JamPost,
    "minraiser": MinRaiser,
}


def make_baseline(name: str, seed: int = 0):
    cls = BASELINES[name] if name in BASELINES else EXTREMES[name]
    try:
        return cls(seed)
    except TypeError:
        return cls()
