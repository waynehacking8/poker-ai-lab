"""League entry for heur4 checkpoint 900 (rl/models/h4_it000900.npz), same run as h4-300, 600 iterations later."""

from __future__ import annotations

from pathlib import Path

from rl.bot import RLBot

MODEL = str(Path(__file__).resolve().parent / "models" / "h4_it000900.npz")


class Heur4b900Bot(RLBot):
    def __init__(self, seed=None):
        super().__init__(seed=seed, model=MODEL)
