"""The shipped RLBot and every specialist play legal full matches through the strict SDK engine."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("chipzen")
import rl  # noqa: F401,E402
from holdem.engine import MatchConfig, play_match  # noqa: E402
from holdem.opponents import make_baseline  # noqa: E402
from rl import specialists  # noqa: E402
from rl.bot import RLBot  # noqa: E402

BEST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rl", "models", "best.npz")


def test_best_model_plays_legal_matches():
    wins = 0
    for seed in range(1, 7):
        for opp in ("maniac", "lag", "random"):
            bots = [RLBot(seed=seed, model=BEST), make_baseline(opp, seed)]
            res = play_match(bots, seed, MatchConfig(), strict=True)  # strict: illegal action raises
            wins += res.winner == 0
    assert wins >= 10  # sanity, not a statistic


@pytest.mark.parametrize("name", specialists.NAMES)
def test_specialists_are_legal(name):
    if name not in specialists.available():
        pytest.skip("specialist weights missing")
    for seed in (1, 2):
        bots = [specialists.make(name, seed), make_baseline("lag", seed)]
        play_match(bots, seed, MatchConfig(), strict=True)


def _record_hands(n_matches=3):
    """Real engine hands as (round_start message, result) pairs, seen by seat 0."""
    from chipzen import Action, Bot

    class Rec(Bot):
        def __init__(self):
            super().__init__()
            self.starts, self.results = [], []

        def on_round_start(self, message):
            self.starts.append(message)

        def on_round_result(self, message):
            self.results.append(message["result"])

        def decide(self, state):
            valid = state.valid_actions
            return Action.check() if "check" in valid else Action.call()

    out = []
    for seed in range(1, n_matches + 1):
        rec = Rec()
        play_match([rec, make_baseline("lag", seed)], seed, MatchConfig())
        out += list(zip(rec.starts, rec.results))
    return out


def test_tracker_dealer_follows_the_server():
    from rl.features import Tracker

    hands = _record_hands()
    assert len(hands) > 20
    for flip in (0, 1):
        by_msg, by_hist, by_parity, forced = Tracker(), Tracker(), Tracker(), Tracker()
        for t in (by_msg, by_hist, by_parity, forced):
            t.me = 0
        for start, res in hands:
            true_d = start["state"]["dealer_seat"]
            d = true_d ^ flip  # flip=1 simulates a server whose first dealer differs from ours
            msg = {"state": {**start["state"], "dealer_seat": d}}
            by_msg.round_start(msg)
            by_msg.round_result(res)
            by_hist.round_result(res)      # no round_start: dealer from the small blind poster
            by_parity.update(res["action_history"], (res["hand_number"] - 1) % 2)
            forced.update(res["action_history"], d)
        assert by_msg.st == forced.st                    # the announced dealer is used
        assert by_hist.st == by_parity.st                # fallback agrees with the engine's own parity
