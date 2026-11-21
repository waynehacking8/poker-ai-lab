"""Playable field clones: bots that act from the fitted action tables.

``CloneBot("arch:2", seed)`` plays like archetype 2, ``CloneBot("bot:Kimiko", seed)`` like
one real bot.  It is a plain engine bot (``decide(state)``), memoryless and
non-adaptive: it reads strength bucket and context, samples an action, then a size.
"""

from __future__ import annotations

import json
import random
from functools import lru_cache
from pathlib import Path

import numpy as np
from chipzen import Action

from holdem.opponents import my_street_bet
from nlhe.cards import cards_from

from .context import ALLIN, CALL, CHECK, FOLD, RAISE, ctx_of_state
from .strength import bucket_for

DEFAULT_MODEL = Path(__file__).parent / "data" / "clones.npz"
MIN_SIZE_SAMPLES = 8
DEFAULT_SIZE = 0.75


class CloneModel:
    def __init__(self, path=DEFAULT_MODEL):
        d = np.load(path, allow_pickle=False)
        self.arch = d["arch_theta"].astype(np.float64)
        self.bot = d["bot_theta"].astype(np.float64)
        self.naive = d["arch_naive"].astype(np.float64)
        self.meta = json.loads(str(d["meta"]))
        self.bot_index = {n: i for i, n in enumerate(self.meta["bots"])}

    def source(self, spec: str):
        """(theta table, size lists) for 'arch:<i>' or 'bot:<name>'."""
        kind, _, key = spec.partition(":")
        if kind == "arch":
            i = int(key)
            return self.arch[i], [self.meta["arch_sizes"][i], self.meta["all_sizes"]]
        i = self.bot_index[key]
        arch = self.meta["bot_archetype"][key]
        return self.bot[i], [self.meta["bot_sizes"][i], self.meta["arch_sizes"][arch],
                             self.meta["all_sizes"]]


@lru_cache(maxsize=2)
def load_model(path=DEFAULT_MODEL) -> CloneModel:
    return CloneModel(path)


class CloneBot:
    def __init__(self, spec: str, seed: int = 0, model: CloneModel | None = None):
        self.spec = spec
        self.rng = random.Random(seed)
        self.theta, self.sizes = (model or load_model()).source(spec)

    def _size(self, street: int, fcl: int) -> float:
        key = f"{0 if street == 0 else 1}:{fcl}"
        for table in self.sizes:
            v = table.get(key)
            if v and len(v) >= MIN_SIZE_SAMPLES:
                return max(self.rng.choice(v) * self.rng.uniform(0.93, 1.07), 0.05)
        return DEFAULT_SIZE

    def decide(self, state):
        ctx, _, _ = ctx_of_state(state)
        hole, board = cards_from(state.hole_cards), cards_from(state.board)
        p = np.array(self.theta[ctx][bucket_for(hole, board)], dtype=np.float64)
        valid = state.valid_actions
        if "fold" not in valid:
            p[FOLD] = 0
        if "call" not in valid:
            p[CALL] = 0
        if "check" not in valid:
            p[CHECK] = 0
        if "raise" not in valid:
            p[RAISE] = p[ALLIN] = 0
        elif state.min_raise > state.max_raise:
            p[ALLIN] += p[RAISE]
            p[RAISE] = 0
        if p.sum() <= 0:
            return Action.check() if "check" in valid else Action.call() if "call" in valid \
                else Action.fold()
        code = self.rng.choices(range(5), weights=p / p.sum())[0]
        if code == FOLD:
            return Action.fold()
        if code == CHECK:
            return Action.check()
        if code == CALL:
            return Action.call()
        if code == ALLIN:
            return Action.raise_to(int(state.max_raise))
        frac = self._size(ctx[0], ctx[2])
        target = my_street_bet(state) + state.to_call + frac * (state.pot + state.to_call)
        lo = min(state.min_raise, state.max_raise)
        target = max(lo, min(state.max_raise, int(round(target))))
        if target >= 0.8 * state.max_raise:
            target = state.max_raise
        return Action.raise_to(int(target))
