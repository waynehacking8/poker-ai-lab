"""numpy-only inference for the trained policy (no torch, no C)."""

from __future__ import annotations

import os

import numpy as np

DEFAULT_MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "best.npz")


class Policy:
    def __init__(self, path=DEFAULT_MODEL, temperature=1.0, seed=None):
        z = np.load(path)
        self.w = [(z[f"pw{i}"].astype(np.float32), z[f"pb{i}"].astype(np.float32)) for i in range(3)]
        self.temperature = temperature
        self.rng = np.random.default_rng(seed)

    def logits(self, obs):
        h = np.asarray(obs, dtype=np.float32)
        for i, (w, b) in enumerate(self.w):
            h = h @ w + b
            if i < 2:
                h = np.maximum(h, 0)
        return h

    def act(self, obs, mask):
        """Action index 0..5; temperature 0 means argmax."""
        lg = self.logits(obs).astype(np.float64)
        lg[~np.asarray(mask, dtype=bool)] = -1e9
        if self.temperature <= 0:
            return int(lg.argmax())
        lg = lg / self.temperature
        lg -= lg.max()
        p = np.exp(lg)
        p /= p.sum()
        return int(self.rng.choice(len(p), p=p))
