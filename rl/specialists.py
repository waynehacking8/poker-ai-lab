"""Per-opponent-type specialists as numpy Bot subclasses.

    from rl.specialists import make, NAMES
    bot = make("maniac", seed=1)

Each specialist is the adaptive generalist fine-tuned against one baseline or one
archetype clone (weights in rl/models/spec_<name>.npz); the portfolio track picks one online.
"""

from __future__ import annotations

import os

from rl.bot import RLBot

MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
NAMES = ["station", "maniac", "nit", "random", "reference", "lag", "station_raiser",
         "arch_0", "arch_1", "arch_2", "arch_3", "arch_4", "arch_5"]


class SpecialistBot(RLBot):
    def __init__(self, name, seed=None, temperature=1.0):
        super().__init__(seed=seed, model=os.path.join(MODELS, f"spec_{name}.npz"), temperature=temperature)
        self.specialty = name


def make(name, seed=None, temperature=1.0):
    return SpecialistBot(name, seed, temperature)


def available():
    return [n for n in NAMES if os.path.exists(os.path.join(MODELS, f"spec_{n}.npz"))]
