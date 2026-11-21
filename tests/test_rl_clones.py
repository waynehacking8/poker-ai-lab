"""C replay clones behave like league.clone.CloneBot (synthetic tables, injected randomness)."""

from __future__ import annotations

import json
import os
import random
import sys

import numpy as np
import pytest

pytest.importorskip("chipzen")
import rl  # noqa: F401,E402

_LP = os.environ.get("LEAGUE_PKG")
if _LP:
    sys.path.insert(0, _LP)
league = pytest.importorskip("league.clone")

from holdem.engine import MatchConfig, play_match  # noqa: E402
from rl import clones, fastenv  # noqa: E402
from tests.test_rl_env import KIND, Scripted, Stub, check_state, decks_for  # noqa: E402


pytestmark = pytest.mark.usefixtures("rl_legacy")


def synth(path, rng):
    def sizes():
        return {f"{s}:{f}": [float(x) for x in rng.uniform(0.3, 2.0, rng.integers(0, 30))]
                for s in (0, 1) for f in range(10)}
    arch = rng.dirichlet(np.ones(5) * 0.7, size=(2, 4, 2, 10, 4, 8))
    bot = rng.dirichlet(np.ones(5) * 0.7, size=(2, 4, 2, 10, 4, 8))
    meta = {"bots": ["x", "y"], "bot_archetype": {"x": 0, "y": 1},
            "arch_sizes": [sizes(), sizes()], "bot_sizes": [sizes(), sizes()], "all_sizes": sizes()}
    np.savez(path, arch_theta=arch, bot_theta=bot, arch_naive=arch, meta=json.dumps(meta))


class CStub(Stub):
    def choices(self, pop, weights):
        tot = sum(weights)
        x = self.random() * tot
        cum = 0.0
        for i, w in zip(pop, weights):
            cum += w
            if cum > x:
                return [i]
        return [pop[-1]]

    def uniform(self, a, b):
        return a + (b - a) * self.random()


@pytest.mark.parametrize("spec_i", range(4))
def test_clone_matches_python(tmp_path, spec_i):
    rng = np.random.default_rng(3)
    p = tmp_path / "c.npz"
    synth(p, rng)
    specs = clones.load(str(p))
    pool = fastenv.Pool(1)
    model = league.CloneModel(str(p))
    for seed in range(1, 31):
        stream = np.random.default_rng(seed).random(4000)
        bot = league.CloneBot(specs[spec_i], model=model)
        bot.rng = CStub(stream)
        seat_b = seed % 2
        log = []
        hero = Scripted(seed, log)
        bots = [None, None]
        bots[seat_b] = bot
        bots[1 - seat_b] = hero
        res = play_match(bots, seed, MatchConfig())
        pool.inject(0, decks=decks_for(seed), urand=stream)
        ctrl = [fastenv.EXT, fastenv.EXT]
        ctrl[seat_b] = 200 + spec_i
        pool.reset(0, seed, ctrl[0], ctrl[1], 0)
        for seat, kind, amount, st, f, mask, amt in log:
            assert pool.state(0)["done"] == 0
            check_state(pool, st, seat, mask, amt, f)
            assert pool.apply_raw(0, KIND[kind], amount) == 0
        s = pool.state(0)
        assert s["done"] == 1
        assert [s["stacks0"], s["stacks1"]] == res.stacks, (spec_i, seed)
