"""Opponent model (roadmap X1): P(opponent action class | public state, name, match so far).

Runtime layer, pure Python plus numpy (no torch). Three layers:
  1. population prior: a small numpy MLP (or softmax regression) over public features;
  2. per-name profile: counts per context bucket (street by facing-bet bucket), shrunk toward the prior;
  3. in-match update: the same counts, accumulated over the opponent's actions in this match.

Action classes: 0 fold, 1 check or call, 2 bet or raise up to the pot, 3 above the pot, 4 all-in.

API:
    m = OppModel.load("rl/models/oppmodel.npz")
    m.start_match("BotName")
    p = m.predict(state)        # state: PublicState before the opponent acts, 5 probabilities
    m.observe(state, cls)       # after the opponent acted

HandTracker builds PublicState and the class of each action from replay-style events (seat, action_type,
amount), so the fit tool and a runtime caller share one definition.
"""
import json
from collections import namedtuple

import numpy as np

NCLS = 5
FOLD, CALL, RAISE_POT, RAISE_OVER, ALLIN = range(5)
STREETS = ("preflop", "flop", "turn", "river")

# street index, actor is the small blind, chips to call, pot before the action, actor's remaining stack,
# the other player's remaining stack, big blind, class of the preceding action (5 = none yet), raises so far
# on this street.
PublicState = namedtuple(
    "PublicState", "street is_sb to_call pot rem rem_opp bb last_cls n_raises")


def classify(action_type, amount, to_call, pot, rem):
    """Class of one action. `amount` is chips added by the action, `pot` is the pot before it (blinds and
    earlier streets included), `rem` the actor's stack before it.

    A raise is all-in when it puts in the whole remaining stack and goes beyond the call. Otherwise its
    size is the chips beyond the call, compared with the pot after the call (a pot-sized raise). A call or
    check, even for the whole stack, stays class 1."""
    if action_type == "fold":
        return FOLD
    if action_type in ("check", "call"):
        return CALL
    if amount <= to_call:  # a "raise" that only matches the bet
        return CALL
    if amount >= rem - 0.5:
        return ALLIN
    return RAISE_POT if (amount - to_call) <= (pot + to_call) + 0.5 else RAISE_OVER


class HandTracker:
    """Public state of one hand from its events. `stacks` maps seat to starting stack."""

    def __init__(self, stacks, bb):
        self.stack0 = dict(stacks)
        self.bb = float(bb)
        self.committed = {s: 0.0 for s in self.stack0}
        self.street_committed = dict(self.committed)
        self.street = 0
        self.sb_seat = None
        self.last_cls = 5
        self.n_raises = 0

    def new_street(self, idx):
        self.street = idx
        self.street_committed = {s: 0.0 for s in self.stack0}
        self.n_raises = 0

    def pot(self):
        return sum(self.committed.values())

    def state(self, seat):
        other = [s for s in self.stack0 if s != seat][0]
        to_call = max(self.street_committed.values()) - self.street_committed[seat]
        return PublicState(
            self.street, int(seat == self.sb_seat), to_call, self.pot(),
            self.stack0[seat] - self.committed[seat], self.stack0[other] - self.committed[other],
            self.bb, self.last_cls, self.n_raises)

    def apply(self, seat, action_type, amount):
        """Apply one event; returns the action class, or None for a blind post."""
        if action_type.startswith("post_"):
            if action_type == "post_small_blind":
                self.sb_seat = seat
            self._add(seat, amount)
            return None
        st = self.state(seat)
        cls = classify(action_type, amount, st.to_call, st.pot, st.rem)
        self._add(seat, amount)
        if cls >= RAISE_POT:
            self.n_raises += 1
        self.last_cls = cls
        return cls

    def _add(self, seat, amount):
        self.committed[seat] += amount
        self.street_committed[seat] += amount


def extract_replay(replay):
    """Yield (hand_idx, actor_seat, actor_name, PublicState, cls) for every non-blind action of a replay."""
    for hi, h in enumerate(replay["hands"]):
        stacks = {s["seat"]: s["starting_stack"] for s in h["starting_stacks"]}
        tr = HandTracker(stacks, h["blinds"]["big_blind"])
        for si, st in enumerate(h["streets"]):
            tr.new_street(STREETS.index(st["street"]) if st["street"] in STREETS else si)
            for a in st["actions"]:
                at = a["action_type"]
                if at.startswith("post_"):
                    tr.apply(a["seat"], at, a["amount"])
                    continue
                state = tr.state(a["seat"])
                cls = tr.apply(a["seat"], at, a["amount"])
                yield hi, a["seat"], a["player"], state, cls


# ---------------------------------------------------------------- features and buckets

FEATURE_SETS = {0: "core", 1: "core+extras"}


def features(s, fs):
    pot = max(s.pot, 1.0)
    bb = max(s.bb, 1.0)
    v = np.zeros(4 + 1 + 2 + 1 + 6 + (4 if fs == 1 else 0), dtype=np.float32)
    v[s.street] = 1.0
    v[4] = s.is_sb
    v[5] = 1.0 if s.to_call > 0 else 0.0
    v[6] = np.log1p(min(s.to_call / pot, 8.0))
    v[7] = np.log1p(min(s.rem, s.rem_opp) / bb) / 5.0
    v[8 + s.last_cls] = 1.0
    if fs == 1:
        v[14] = min(s.n_raises, 4) / 4.0
        v[15] = min(s.to_call / max(s.rem, 1.0), 1.0)
        v[16] = np.log1p(pot / bb) / 6.0
        v[17] = np.log1p(max(s.rem, 0.0) / bb) / 5.0
    return v


def n_buckets(edges):
    return 4 * (len(edges) + 2)


def bucket(s, edges):
    """Context bucket: street by facing-bet bucket (0 = nothing to call, then bet over pot by edges)."""
    if s.to_call <= 0:
        fb = 0
    else:
        r = s.to_call / max(s.pot, 1.0)
        fb = 1 + sum(1 for e in edges if r > e)
    return s.street * (len(edges) + 2) + fb


def prior_probs(p, X):
    """Softmax of the prior network on a batch X (n, d). `p` holds W1, b1, W2, b2."""
    if p["W1"].shape[0] > 0:
        X = np.maximum(X @ p["W1"].T + p["b1"], 0.0)
    z = X @ p["W2"].T + p["b2"]
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


# ---------------------------------------------------------------- the model

_ARRAYS = ("W1", "b1", "W2", "b2", "edges", "names", "counts", "scalars")


def save_params(path, p):
    np.savez_compressed(path, **{k: np.asarray(p[k]) for k in _ARRAYS})


class OppModel:
    """Frozen parameters plus the in-match state of one opponent."""

    def __init__(self, p):
        self.p = p
        sc = p["scalars"]
        self.fs, self.k, self.w, self.k_im = int(sc[0]), float(sc[1]), float(sc[2]), float(sc[3])
        self.edges = [float(e) for e in p["edges"]]
        self.name_idx = {str(n): i for i, n in enumerate(p["names"])}
        self.counts = p["counts"].astype(np.float64)
        self.start_match(None)

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as z:
            return cls({k: z[k] for k in _ARRAYS})

    def start_match(self, name):
        self.i = self.name_idx.get(name) if name is not None else None
        self.m = np.zeros((n_buckets(self.edges), NCLS))

    def predict(self, state):
        p0 = prior_probs(self.p, features(state, self.fs)[None, :])[0]
        b = bucket(state, self.edges)
        m = self.m[b]
        if self.i is None:
            return (m + self.k_im * p0) / (m.sum() + self.k_im)
        n = self.counts[self.i, b]
        return (n + self.w * m + self.k * p0) / (n.sum() + self.w * m.sum() + self.k)

    def observe(self, state, cls):
        self.m[bucket(state, self.edges), cls] += 1.0


def describe(p):
    sc = p["scalars"]
    return json.dumps({"feature_set": int(sc[0]), "hidden": int(p["W1"].shape[0]), "k": float(sc[1]),
                       "w": float(sc[2]), "k_im": float(sc[3]), "edges": [float(e) for e in p["edges"]],
                       "names": int(len(p["names"]))})
