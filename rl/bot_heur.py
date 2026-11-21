"""League entry for heur4 checkpoint 300 (rl/models/h4_it000300.npz), trained with the heuristic bot in the pool."""

from __future__ import annotations

from pathlib import Path

from rl.bot import RLBot

MODEL = str(Path(__file__).resolve().parent / "models" / "h4_it000300.npz")


class Heur4Bot(RLBot):
    def __init__(self, seed=None):
        super().__init__(seed=seed, model=MODEL)
