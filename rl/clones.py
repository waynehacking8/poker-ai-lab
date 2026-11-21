"""Load the league's replay clones (league/data/clones.npz) into the C engine.

Clone ``k`` of the returned spec list is controller id ``200 + k``.
"""

from __future__ import annotations

import json

import numpy as np

from rl import fastenv

MIN_SIZE_SAMPLES = 8


def _resolve(tables):
    out = np.zeros((2, 10, fastenv.SZ_CAP))
    cnt = np.zeros((2, 10), dtype=np.int32)
    for street in (0, 1):
        for fcl in range(10):
            for t in tables:
                v = t.get(f"{street}:{fcl}")
                if v and len(v) >= MIN_SIZE_SAMPLES:
                    v = v[:fastenv.SZ_CAP]
                    out[street, fcl, :len(v)] = v
                    cnt[street, fcl] = len(v)
                    break
    return out, cnt


def load(path, bots=None):
    """Install the clones in the C engine; returns the list of spec strings."""
    d = np.load(path, allow_pickle=False)
    meta = json.loads(str(d["meta"]))
    arch, bot = d["arch_theta"].astype(np.float64), d["bot_theta"].astype(np.float64)
    specs, thetas, szs, cnts = [], [], [], []
    for i in range(len(arch)):
        specs.append(f"arch:{i}")
        thetas.append(arch[i])
        s, c = _resolve([meta["arch_sizes"][i], meta["all_sizes"]])
        szs.append(s); cnts.append(c)
    names = meta["bots"] if bots is None else bots
    for name in names:
        i = meta["bots"].index(name)
        specs.append(f"bot:{name}")
        thetas.append(bot[i])
        a = meta["bot_archetype"][name]
        s, c = _resolve([meta["bot_sizes"][i], meta["arch_sizes"][a], meta["all_sizes"]])
        szs.append(s); cnts.append(c)
    fastenv.set_clones(np.array(thetas), np.array(szs), np.array(cnts))
    return specs
