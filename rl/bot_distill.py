"""League entry for the distilled policy (rl/models/distill1.npz) under its own class name."""

from __future__ import annotations

from pathlib import Path

from rl.bot import RLBot

MODEL = str(Path(__file__).resolve().parent / "models" / "distill1.npz")


class Distill1Bot(RLBot):
    def __init__(self, seed=None):
        super().__init__(seed=seed, model=MODEL)
