"""PPO rollouts against a pure-Python opponent in the real SDK engine (the heuristic HoldemBot).

The heuristic bot costs about 8 ms per decision, so it cannot live in the C env. A few SDK worker processes
play it continuously, always with the newest policy parameters, and stream finished matches back to the learner
in the same sample format as ``rl.train.Collector`` (obs, mask, act, lp, adv, ret; potential shaped reward on
chip share, gamma 1, GAE lambda 0.95).
"""

from __future__ import annotations

import time

import numpy as np

import rl  # noqa: F401
from chipzen import Action, Bot
from holdem.engine import MatchConfig, play_match
from rl.features import Tracker, build

LAM = 0.95


class HeroRec(Bot):
    def __init__(self, params, seed):
        super().__init__()
        from rl.train import np_forward, sample
        self._fwd, self._sample = np_forward, sample
        self.p = params
        self.rng = np.random.default_rng(seed)
        self.tracker = Tracker()
        self.me = 0
        self.o, self.m, self.a, self.lp, self.v, self.r, self.d = [], [], [], [], [], [], []
        self.phi = 0.5
        self.phi_prev = 0.5
        self.has_prev = False

    def on_match_start(self, info):
        me = info.get("your_seat")
        if me is None:
            for seat in info.get("seats", ()) or ():
                if seat.get("is_self"):
                    me = seat["seat"]
        self.me = int(me or 0)
        self.tracker = Tracker()
        self.tracker.me = self.me

    def on_round_start(self, message):
        self.tracker.round_start(message)
        st = (message.get("state", {}) or {}).get("stacks")
        if st:
            self.phi = st[self.me] / float(sum(st))

    def on_round_result(self, message):
        self.tracker.round_result(message.get("result", {}) or {})

    def decide(self, state):
        self.tracker.me = state.your_seat
        f, mask, amt = build(state, self.tracker)
        obs = np.asarray(f, np.float32)[None]
        mk = np.asarray(mask, bool)[None]
        lg, v = self._fwd(self.p, obs)
        a, lp = self._sample(lg, mk, self.rng)
        a = int(a[0])
        if self.has_prev:
            self.r[-1] += self.phi - self.phi_prev
        self.phi_prev, self.has_prev = self.phi, True
        self.o.append(obs[0]); self.m.append(mk[0]); self.a.append(a)
        self.lp.append(float(lp[0])); self.v.append(float(v[0])); self.r.append(0.0); self.d.append(0.0)
        if a == 0:
            return Action.fold()
        if a == 1:
            return Action.call() if state.to_call > 0 else Action.check()
        return Action.raise_to(int(amt[a]))

    def batch(self, won):
        if not self.o:
            return None
        self.r[-1] += (1.0 if won else 0.0) - self.phi_prev
        self.d[-1] = 1.0
        v = np.array(self.v, np.float32)
        r = np.array(self.r, np.float32)
        d = np.array(self.d, np.float32)
        n = len(r)
        nxt = np.append(v[1:], 0.0)
        delta = r + (1 - d) * nxt - v
        adv = np.zeros(n, np.float32)
        g = 0.0
        for t in range(n - 1, -1, -1):
            g = delta[t] + LAM * (1 - d[t]) * g
            adv[t] = g
        return dict(obs=np.array(self.o, np.float32), mask=np.array(self.m, bool),
                    act=np.array(self.a, np.int64), lp=np.array(self.lp, np.float32), adv=adv, ret=adv + v)


def play_one(params, seed, seat):
    from bot import HoldemBot  # chipzen_bot/bot.py, the original heuristic
    hero = HeroRec(params, seed)
    opp = HoldemBot(seed=seed * 13 + seat)
    bots = [None, None]
    bots[seat] = hero
    bots[1 - seat] = opp
    res = play_match(bots, seed, MatchConfig())
    won = res.winner == seat
    return hero.batch(won), won, res.hands


def sdk_worker_main(conn, seed):
    """Loop: take the newest parameters, play one match, send (batch, won, hands). None stops the worker."""
    params = None
    k = 0
    while True:
        while conn.poll(0 if params is not None else None):
            msg = conn.recv()
            if msg is None:
                return
            params = msg
        k += 1
        batch, won, hands = play_one(params, seed * 1000003 + k, k % 2)
        conn.send((batch, won, hands))
