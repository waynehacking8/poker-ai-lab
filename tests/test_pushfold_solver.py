"""CFR+ push/fold solver: exploitability and the shipped tables."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from scripts.solve_pushfold import exploitability, solve

DATA = Path(__file__).resolve().parent.parent / "chipzen_bot" / "nlhe" / "data"


def toy_game(n=13, seed=0):
    rng = np.random.default_rng(seed)
    strength = np.sort(rng.random(n))
    M = 0.5 + 0.9 * (strength[:, None] - strength[None, :]) / 2
    M = np.clip(M, 0.02, 0.98)
    return M, np.ones((n, n))


def test_solver_converges_and_perturbation_is_exploitable():
    M, W = toy_game()
    push, call, expl = solve(M, W, S=8.0, iters=3000)
    assert expl < 5e-3
    bad = np.clip(push + 0.3, 0, 1)
    assert exploitability(M, W, 8.0, bad, call) > 10 * max(expl, 1e-4)


def test_shipped_tables_look_like_nash():
    d = json.loads((DATA / "pushfold.json").read_text())
    assert max(d["exploitability"]) < 0.01  # big blinds per hand
    push = np.array(d["push"]) / 100.0
    call = np.array(d["call"]) / 100.0
    i10 = d["stacks"].index(10.0)
    aa = 12 * 13 + 12
    seven_two = 5 * 13 + 0  # 72o sits below the diagonal: row = low rank
    assert push[i10][aa] == 1.0 and call[i10][aa] == 1.0
    assert push[i10][seven_two] == 0.0
    # shorter stacks shove (and call) wider
    assert push[d["stacks"].index(4.0)].mean() > push[d["stacks"].index(15.0)].mean()
    assert call[d["stacks"].index(4.0)].mean() > call[d["stacks"].index(15.0)].mean()
