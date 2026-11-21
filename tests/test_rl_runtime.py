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
