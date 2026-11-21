"""Referee harness: opponent field cloned from Chipzen replays and a candidate league."""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT, os.path.join(_ROOT, "chipzen_bot")):
    if _p not in sys.path:
        sys.path.append(_p)
