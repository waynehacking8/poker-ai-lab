"""Strip a training checkpoint to the policy weights the runtime needs.

    python -m rl.export ckpt/adapt/latest.npz rl/models/best.npz
"""

import sys

import numpy as np

z = np.load(sys.argv[1])
keep = {k: z[k].astype(np.float32) for k in z.files if k[0] == "p" or k == "keep"}
np.savez(sys.argv[2], **keep)
print(sys.argv[2], {k: v.shape for k, v in keep.items()})
