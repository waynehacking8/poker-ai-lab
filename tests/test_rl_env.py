"""Equivalence of the C engine with holdem/engine.py: evaluator, rules, baselines, features."""

from __future__ import annotations

import random

import numpy as np
import pytest

pytest.importorskip("chipzen")

import rl  # noqa: F401,E402
from chipzen import Action  # noqa: E402

from holdem.engine import MatchConfig, play_match  # noqa: E402
from holdem.opponents import make_baseline  # noqa: E402
from nlhe.evaluator import evaluate as py_eval  # noqa: E402
from rl import fastenv  # noqa: E402
from rl.features import Tracker, build  # noqa: E402

KIND = {"fold": 0, "check": 1, "call": 2, "raise": 3}


def test_evaluator_matches_python():
    rng = random.Random(5)
    for _ in range(30000):
        n = rng.choice((5, 6, 7))
        cards = rng.sample(range(52), n)
        assert fastenv.evaluate(cards) == py_eval(cards), cards


class Stub:
    """Random-source stand-in so Python baselines and the C engine see the same stream."""

    def __init__(self, stream):
        self.s = stream
        self.i = 0

    def random(self):
        v = self.s[self.i]
        self.i += 1
        return v

    def choice(self, seq):
        return seq[int(self.random() * len(seq))]

    def randint(self, a, b):
        return a + int(self.random() * (b - a + 1))


class Scripted:
    """Random-legal actor that logs every decision and the Python features it saw."""

    def __init__(self, seed, log):
        self.rng = random.Random(seed)
        self.log = log
        self.tr = Tracker()
        self.seat = 0

    def on_match_start(self, m):
        self.seat = m["your_seat"]
        self.tr.me = self.seat

    def on_round_result(self, msg):
        r = msg["result"]
        self.tr.update(r["action_history"], (r["hand_number"] - 1) % 2)

    def decide(self, state):
        f, mask, amt = build(state, self.tr)
        r = self.rng.random()
        valid = state.valid_actions
        if "raise" in valid and r < 0.4:
            lo = min(state.min_raise, state.max_raise)
            pick = self.rng.choice(["min", "max", "pot", "rand", "rand"])
            if pick == "min":
                a = lo
            elif pick == "max":
                a = state.max_raise
            elif pick == "pot":
                a = min(state.max_raise, max(lo, state.pot))
            else:
                a = self.rng.randint(lo, state.max_raise)
            act = Action.raise_to(a)
        elif state.to_call > 0:
            act = Action.fold() if r < 0.62 else Action.call()
        else:
            act = Action.check()
        self.log.append((state.your_seat, act.action, getattr(act, "amount", 0) or 0, state, f, mask, amt))
        return act


def decks_for(seed, n=400):
    out = []
    for h in range(1, n + 1):
        d = list(range(52))
        random.Random(seed * 1_000_003 + h).shuffle(d)
        out.append(d)
    return np.array(out, dtype=np.int32)


def check_state(pool, st, seat, mask, amt, f):
    s = pool.state(0)
    assert s["to_call"] == st.to_call and s["min_raise"] == st.min_raise
    assert s["max_raise"] == st.max_raise and s["stack0" if seat == 0 else "stack1"] == st.your_stack
    assert s["pot"] == st.pot
    obs, m, meta, a = pool.obs([0])
    assert meta[0, 0] == seat
    assert m[0].tolist() == [bool(x) for x in mask]
    assert a[0].tolist() == amt
    assert np.allclose(obs[0], np.array(f, dtype=np.float32), atol=2e-5), (
        [(i, obs[0][i], f[i]) for i in range(len(f)) if abs(obs[0][i] - f[i]) > 2e-5])


@pytest.mark.parametrize("seed", range(12))
def test_random_actors_full_match(seed):
    """Both seats external: every decision, feature vector and the final stacks must agree."""
    log = []
    bots = [Scripted(seed * 2, log), Scripted(seed * 2 + 1, log)]
    res = play_match(bots, seed + 1, MatchConfig())
    pool = fastenv.Pool(1)
    pool.inject(0, decks=decks_for(seed + 1))
    pool.reset(0, 1, fastenv.EXT, fastenv.EXT + 1, 0)
    for seat, kind, amount, st, f, mask, amt in log:
        check_state(pool, st, seat, mask, amt, f)
        assert pool.apply_raw(0, KIND[kind], amount) == 0
    s = pool.state(0)
    assert s["done"] == 1
    assert [s["stacks0"], s["stacks1"]] == res.stacks
    assert s["hand_no"] == res.hands


@pytest.mark.parametrize("name", list(fastenv.BASELINE_IDS))
def test_baselines_match_sdk(name):
    """The C baseline picks the same actions as the Python one over many full matches."""
    bid = fastenv.BASELINE_IDS[name]
    pool = fastenv.Pool(1)
    for seed in range(1, 41):
        seat_b = seed % 2
        log = []
        stream = np.random.default_rng(seed).random(4000)
        opp = make_baseline(name, seed)
        if hasattr(opp, "rng"):
            opp.rng = Stub(stream)
        hero = Scripted(seed, log)
        bots = [None, None]
        bots[1 - seat_b] = hero
        bots[seat_b] = opp
        res = play_match(bots, seed, MatchConfig())
        pool.inject(0, decks=decks_for(seed), urand=stream)
        ctrl = [fastenv.EXT, fastenv.EXT]
        ctrl[seat_b] = bid
        pool.reset(0, seed, ctrl[0], ctrl[1], 0)
        for seat, kind, amount, st, f, mask, amt in log:
            s = pool.state(0)
            assert s["done"] == 0, (name, seed)
            check_state(pool, st, seat, mask, amt, f)
            assert pool.apply_raw(0, KIND[kind], amount) == 0
        s = pool.state(0)
        assert s["done"] == 1, (name, seed)
        assert [s["stacks0"], s["stacks1"]] == res.stacks, (name, seed)
        assert s["hand_no"] == res.hands
