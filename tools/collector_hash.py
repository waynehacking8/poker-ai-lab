"""X2a acceptance 3: hash of Collector batches on a fixed seed, to compare two trees. python tools/collector_hash.py TREE [real|empty]"""
import hashlib
import sys

import numpy as np

tree = sys.argv[1]
sys.path.insert(0, tree)
import rl  # noqa: E402,F401
from rl import train  # noqa: E402
from rl.features import NST  # noqa: E402

train.install_clones(tree + "/data/clones.npz", True)
params = train.init_params(5)
snaps = []
for s in (6, 7):
    p = train.init_params(s)
    snaps.append(p)
weights = {k: 1.0 for k in list(train.BASE_W) + list(train.CLONE_IDS)}
weights["snap:1"] = 1.0
weights["snap:2"] = 1.0
if len(sys.argv) > 2:
    from rl.features import load_priors
    col = train.Collector(24, 11, load_priors() if sys.argv[2] == "real" else {"nobody": [0.0] * NST})
else:
    col = train.Collector(24, 11)
h = hashlib.sha256()
n = 0
for it in range(3):
    batch, results = col.collect(params, snaps, weights, 3000)
    for k in sorted(batch):
        h.update(np.ascontiguousarray(batch[k]).tobytes())
        n += len(batch[k])
    h.update(repr(results).encode())
print("rows", n, "sha256", h.hexdigest())
