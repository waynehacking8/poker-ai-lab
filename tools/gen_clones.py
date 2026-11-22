"""Generate perturbed clone opponents for training (domain randomization over the clone family).

    python tools/gen_clones.py data/clones.npz data/clones_gen.npz [N] [SEED]

Keeps the 6 fitted archetypes as arch:0..5 and appends N generated ones (rl/clonegen.py) as arch:6.. .
The per-bot clones are copied unchanged, so they stay a held-out family without --bot-clones.
"""

import json
import sys

import numpy as np

import rl  # noqa: F401
from rl import clonegen


def main():
    src, dst = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 48
    rng = np.random.default_rng(int(sys.argv[4]) if len(sys.argv) > 4 else 7)
    d = np.load(src, allow_pickle=False)
    meta = json.loads(str(d["meta"]))
    arch = d["arch_theta"].astype(np.float64)
    out = [clonegen.sample(arch, meta["arch_sizes"], rng) for _ in range(n)]
    clonegen.write(dst, src, [o[0] for o in out], [o[1] for o in out], [o[2] for o in out])
    print(f"{dst}: {len(arch)} fitted + {n} generated archetypes, {len(d['bot_theta'])} held-out bot clones")


if __name__ == "__main__":
    main()
