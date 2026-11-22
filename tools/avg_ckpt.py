"""Average the weights of several checkpoints of one run (stochastic weight averaging, offline).

    python tools/avg_ckpt.py OUT.npz ckpt/heur4/it000600.npz ckpt/heur4/it000900.npz ...

Only meaningful for checkpoints of the same run, which share one basin of the loss.
"""

import sys

import numpy as np

out, srcs = sys.argv[1], sys.argv[2:]
zs = [np.load(s) for s in srcs]
keys = zs[0].files
assert all(z.files == keys for z in zs), "checkpoints differ in keys"
np.savez(out, **{k: np.mean([z[k] for z in zs], axis=0).astype(zs[0][k].dtype) for k in keys})
print(f"{out}: mean of {len(srcs)} checkpoints")
