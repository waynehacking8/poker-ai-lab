"""League entry for fb1 checkpoint 900 (rl/models/fb1_it000900.npz): h4-300 trained 900 more iterations
with real Chipzen field bots in the SDK workers (tools/rl_fb.sh)."""

from __future__ import annotations

from pathlib import Path

from rl.bot import RLBot

MODEL = str(Path(__file__).resolve().parent / "models" / "fb1_it000900.npz")


class Fb1b900Bot(RLBot):
    def __init__(self, seed=None):
        super().__init__(seed=seed, model=MODEL)
