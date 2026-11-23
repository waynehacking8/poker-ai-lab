"""X2s search under the opponent model: range update, EV arithmetic, the blend, search=False unchanged."""

from __future__ import annotations

import hashlib
import json

import numpy as np
import pytest

pytest.importorskip("chipzen")
import rl  # noqa: F401,E402
from chipzen.models import Card, GameState  # noqa: E402

from holdem.engine import MatchConfig, play_match  # noqa: E402
from holdem.opponents import make_baseline  # noqa: E402
from rl.bot import RLBot  # noqa: E402
from rl.features import action_table  # noqa: E402
from rl.search import (MARGIN, MIN_OBS, PREFLOP_STRENGTH, Search, call_ev, raise_ev,  # noqa: E402
                       update_range)

P = np.array([0.2, 0.3, 0.3, 0.1, 0.1])  # fold, call, raise up to the pot, above the pot, all-in


def test_range_update_direction():
    mean = {}
    for name, cls in (("fold", 0), ("call", 1), ("raise", 2), ("allin", 4)):
        w = np.ones(len(PREFLOP_STRENGTH))
        update_range(w, P, cls, PREFLOP_STRENGTH, [])
        mean[name] = float((w * PREFLOP_STRENGTH).sum() / w.sum())
    assert mean["fold"] < mean["call"] < mean["raise"] < mean["allin"]
    assert mean["fold"] < PREFLOP_STRENGTH.mean() < mean["raise"]


def test_range_band_weights():
    w = np.ones(len(PREFLOP_STRENGTH))
    update_range(w, P, 4, PREFLOP_STRENGTH, [])
    assert set(np.round(w, 6)) == {1.0, 0.1}
    assert abs((w == 1.0).mean() - 0.1) < 0.02  # the all-in band is the top 10% of the combos


def test_ev_arithmetic():
    pot, c, r, q = 1000.0, 300.0, 900.0, 0.37
    assert raise_ev(pot, c, r, 0.0, q) == pytest.approx(q * (pot + 2 * r - c) - r)
    # at q = 0.5 a minimum raise that is always called gains nothing over calling
    for pot, c, r in ((1000, 300, 600), (400, 0, 100), (7000, 2500, 5000)):
        assert raise_ev(pot, c, r, 0.0, 0.5) == pytest.approx(call_ev(pot, c, 0.5))
    # a bet into a range that always folds earns the pot
    assert raise_ev(1000, 0, 700, 1.0, 0.2) == 1000


class Stub:
    """An opponent model that always predicts the same five class probabilities."""

    def __init__(self, p, named=None):
        self.p, self.i = np.array(p, float), named

    def start_match(self, name):
        pass

    def predict(self, state):
        return self.p

    def observe(self, state, cls):
        pass


def flop_state():
    """Seat 1 (big blind) to act first on the flop: blinds 50/100, small blind called, big blind checked."""
    hist = [{"seat": 0, "action": "post_small_blind", "amount": 50, "phase": "preflop"},
            {"seat": 1, "action": "post_big_blind", "amount": 100, "phase": "preflop"},
            {"seat": 0, "action": "call", "amount": 50, "phase": "preflop"},
            {"seat": 1, "action": "check", "amount": 0, "phase": "preflop"}]
    return GameState(
        hand_number=1, phase="flop", hole_cards=[Card.from_str("Ah"), Card.from_str("Ad")],
        board=[Card.from_str(x) for x in ("2c", "7d", "9s")], pot=200, your_stack=9900,
        opponent_stacks=[9900], your_seat=1, dealer_seat=0, to_call=0, min_raise=100, max_raise=9900,
        valid_actions=["check", "raise"], action_history=hist, round_id="h1", request_id="")


def test_bet_into_a_range_that_always_folds_earns_the_pot():
    s = Search(Stub([1, 0, 0, 0, 0]), seed=1)
    s.start_match(None, 1, 10000)
    state = flop_state()
    mask, amt = action_table(state, 0)
    from nlhe.cards import cards_from
    hole, board = cards_from(state.hole_cards), cards_from(state.board)
    s._sync(state.action_history, hole, board)
    evs = s.evs(state, mask, amt, hole, board)
    assert {a for a in evs if a >= 2} == {2, 3, 4, 5}
    assert all(evs[a] == 200 for a in range(2, 6))
    assert 0 not in evs and evs[1] > 100  # checking aces on a dry flop is worth more than half the pot


def decide_with(search, evs, policy_a, pot=1000):
    state = flop_state()
    state.pot = pot
    search.evs = lambda *a: evs
    mask, amt = action_table(state, 0)
    return search.decide(state, policy_a, mask, amt)


def test_blend_needs_evidence():
    big = {1: 0.0, 2: 10 * 1000.0}
    s = Search(Stub([1, 0, 0, 0, 0]), seed=1)
    s.start_match(None, 1, 10000)
    assert decide_with(s, big, 1) == 1  # no profile, no opponent actions yet
    s.n_obs = MIN_OBS - 1
    assert decide_with(s, big, 1) == 1
    s.n_obs = MIN_OBS
    assert decide_with(s, big, 1) == 2
    s2 = Search(Stub([1, 0, 0, 0, 0], named=3), seed=1)
    s2.start_match("x", 1, 10000)
    assert decide_with(s2, big, 1) == 2  # a named profile is evidence


def test_blend_margin():
    s = Search(Stub([1, 0, 0, 0, 0], named=3), seed=1)
    s.start_match("x", 1, 10000)
    assert decide_with(s, {1: 100.0, 2: 100.0 + MARGIN * 1000}, 1) == 1  # exactly the margin: policy plays
    assert decide_with(s, {1: 100.0, 2: 100.0 + MARGIN * 1000 + 1}, 1) == 2
    assert decide_with(s, {1: 100.0, 2: 90.0}, 2) == 2  # the policy's own choice is the argmax: no override


def test_search_runs_and_logs_in_a_real_match(tmp_path, monkeypatch):
    log = tmp_path / "log.jsonl"
    monkeypatch.setenv("RL_SEARCH_LOG", str(log))
    play_match([RLBot(seed=3, search=True), make_baseline("tight_sticky", 3)], 3, MatchConfig())
    rows = [json.loads(x) for x in log.read_text().splitlines()]
    assert rows and {"policy", "search", "ev", "override"} <= set(rows[0])


def test_no_log_without_env_var(tmp_path, monkeypatch):
    monkeypatch.delenv("RL_SEARCH_LOG", raising=False)
    monkeypatch.chdir(tmp_path)
    play_match([RLBot(seed=3, search=True), make_baseline("tight_sticky", 3)], 3, MatchConfig())
    assert list(tmp_path.iterdir()) == []


def test_search_off_plays_as_before():
    """Digest of 200 seeded matches (100 against tight_sticky, 100 against jam, which exercises the all-in
    answer), taken from rl/bot.py at c348a59 (before search)."""
    rows = []
    for seed in range(1, 201):
        opp = "tight_sticky" if seed <= 100 else "jam"
        r = play_match([RLBot(seed=seed), make_baseline(opp, seed)], seed, MatchConfig())
        rows.append([r.hands, r.stacks])
    assert hashlib.sha256(json.dumps(rows).encode()).hexdigest() == (
        "09cd1df780dca7c1362bf34cdf876f501aac5ccffe333511ec11582e0eb79c51")
