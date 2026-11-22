"""League entry for fb2 checkpoint 900 (rl/models/fb2_it000900.npz): fb1-900 trained 900 more iterations
with a larger field bot share and A5, A2 weighted up (tools/rl_fb2.sh)."""

from __future__ import annotations

from pathlib import Path

from rl.bot import RLBot

MODEL = str(Path(__file__).resolve().parent / "models" / "fb2_it000900.npz")


class Fb2b900Bot(RLBot):
    def __init__(self, seed=None):
        super().__init__(seed=seed, model=MODEL)
