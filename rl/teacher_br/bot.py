"""Best-response bots (oracle, not deployable: uses numba and exact equity enumeration).

ManiacBR plays the value-table policy from br/dp.py against the Maniac baseline.
"""

from __future__ import annotations

import os
import sys

import numpy as np
from chipzen import Action, Bot

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "chipzen_bot"))
from nlhe.cards import cards_from, hand_class  # noqa: E402

from . import dp, evalnb, replay  # noqa: E402


def street_bucket(state, k):
    hole = cards_from(state.hole_cards)
    if state.phase == "preflop":
        return hand_class(hole[0], hole[1])
    board = np.array(cards_from(state.board), dtype=np.int64)
    fn = {"flop": evalnb.flop_eq, "turn": evalnb.turn_eq, "river": evalnb.river_eq}[state.phase]
    w, t = fn(hole[0], hole[1], board, evalnb.STRAIGHT, evalnb.TOP5)
    return min(int((w + t / 2) * k), k - 1)


class ManiacBR(Bot):
    def __init__(self, seed=None, table="data/maniac_k25.npz", **_):
        super().__init__()
        d = np.load(table)
        self.grid = d["grid"]
        self.hs = [int(h) for h in d["hs"]]
        self.V = d["V"]  # [h index][role][grid]
        self.fr = d["fr"]
        self.k = int(d["k"])
        self.tab = {"EQW": d["tab_EQW"], "EQT": d["tab_EQT"], "TR": d["tab_TR"],
                    "Ks": d["tab_Ks"].astype(np.int64)}
        self.stats = {}

    def decide(self, state):
        h = state.hand_number
        bb = dp.bb_for(h)
        we_dealer = 1 if state.dealer_seat == state.your_seat else 0
        hi = min(h + 1, self.hs[-1]) - self.hs[0]
        Vn = self.V[hi][1 - we_dealer]
        S, sU0, street = replay.replay(state, bb)
        C = dp.make_ctx(sU0, we_dealer, bb, self.grid, Vn, self.tab, self.fr)
        b = street_bucket(state, self.k)
        oa = np.zeros(169, np.int64)
        ok = np.zeros(169, np.int64)
        dp.node(C, 0, street, 0, S, 0, oa, ok)
        kind, amt = int(oa[b]), int(ok[b])
        valid = state.valid_actions
        if kind == 2 and "raise" in valid:
            lo = min(state.min_raise, state.max_raise)
            return Action.raise_to(int(max(lo, min(state.max_raise, amt))))
        if kind == 0 and "fold" in valid:
            return Action.fold()
        return Action.call() if "call" in valid else Action.check()


BBS = np.array([100, 150, 200, 300, 400, 600, 800, 1000])


def share_table():
    grid = dp.default_grid(250)
    return {"grid": grid, "bbs": BBS, "V": np.tile(grid / dp.TOTAL, (len(BBS), 1))}


class SearchBR(Bot):
    """Best response to a deterministic opponent (lag, station_raiser) by sampled expectimax."""

    SAMPLES = {0: (5, 4, 4), 1: (1, 8, 6), 2: (1, 1, 12), 3: (1, 1, 1)}

    def __init__(self, seed=None, opp="lag", table=None, fr=(0.5, 1.0, 2.0), samples=None, **_):
        super().__init__()
        from . import search

        self.search = search
        self.oid = search.OPP_ID[opp]
        d = share_table() if table is None else dict(np.load(table))
        self.grid = d["grid"]
        self.bbs = [int(x) for x in d["bbs"]]
        self.V = d["V"]
        self.fr = np.asarray(fr, float)
        self.samples = samples or self.SAMPLES
        self.seed = seed or 0
        self.my_seat = 0
        self.log = []  # (hand number, our stack at hand start)
        self.decisions = []

    def on_match_start(self, info):
        if info.get("your_seat") is not None:
            self.my_seat = int(info["your_seat"])

    def on_round_start(self, message):
        st = message.get("state", {})
        self.log.append((int(st["hand_number"]), int(st["stacks"][self.my_seat])))

    def decide(self, state):
        sr = self.search
        h = state.hand_number
        bb = dp.bb_for(h)
        we_dealer = 1 if state.dealer_seat == state.your_seat else 0
        S, sU0, street, events = replay.replay_full(state, bb)
        hole = cards_from(state.hole_cards)
        board = cards_from(state.board)
        w = np.ones(sr.NC)
        w[(sr.CA == hole[0]) | (sr.CA == hole[1]) | (sr.CB == hole[0]) | (sr.CB == hole[1])] = 0.0
        codes = np.zeros(sr.NC, np.int64)
        for Sb, a, kind, amt, st in events:
            if a != 1:
                continue
            if st >= 1:
                nb = 2 + st
                sr.fill_types(np.array(board[:nb], np.int64), nb, hole[0], hole[1], sr.CA, sr.CB,
                              evalnb.STRAIGHT, evalnb.TOP5, codes)
            sr.obs_weights(self.oid, st, codes, sr.PCT, Sb, sU0, dp.TOTAL - sU0, bb,
                           1 if kind == "raise" else 0, amt, w)
        if street >= 1:
            nb = 2 + street
            sr.fill_types(np.array(board[:nb], np.int64), nb, hole[0], hole[1], sr.CA, sr.CB,
                          evalnb.STRAIGHT, evalnb.TOP5, codes)
            w[codes < 0] = 0.0
        if w.sum() <= 0:  # model mismatch: fall back to the prior range
            w = np.ones(sr.NC)
            w[(sr.CA == hole[0]) | (sr.CA == hole[1]) | (sr.CB == hole[0]) | (sr.CB == hole[1])] = 0
        li = self.bbs.index(dp.bb_for(h + 1))
        rng = np.random.default_rng(self.seed * 1000003 + h * 101 + street)
        ctx = sr.build_ctx(hole, board, street, S, sU0, bb, we_dealer, self.grid, self.V[li],
                           self.fr, self.oid, self.samples[street], rng)
        oa = np.zeros(4)
        sr.search(ctx, 0, street, 0, S, w, 0, 0, 0, 0, oa)
        kind, amt = int(oa[0]), int(oa[1])
        self.decisions.append((h, street, kind, amt, float(w.sum())))
        valid = state.valid_actions
        if kind == 2 and "raise" in valid:
            lo = min(state.min_raise, state.max_raise)
            return Action.raise_to(int(max(lo, min(state.max_raise, amt))))
        if kind == 0 and "fold" in valid:
            return Action.fold()
        return Action.call() if "call" in valid else Action.check()


def make(name: str, **kw):
    if name == "maniac":
        return ManiacBR(**kw)
    return SearchBR(opp=name, **kw)
