"""RL track: lean C match engine, features, PPO training and a numpy-only runtime.

Importing this package puts ``chipzen_bot`` on ``sys.path`` (for ``nlhe``).
"""

import os
import sys

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "chipzen_bot"), _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
