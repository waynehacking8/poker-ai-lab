"""Search off against on, per cell and pooled, from tools/x2s_judge.sh output.

    python tools/x2s_stats.py [logs/x2s_judge]

The difference interval is Newcombe's (hybrid Wilson score, 95%), unpaired: the ext: bots are unseeded.
"""

from __future__ import annotations

import json
import math
import os
import sys


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def newcombe(k1, n1, k2, n2):
    """95% interval of p2 - p1."""
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1)
    l2, u2 = wilson(k2, n2)
    d = p2 - p1
    return d - math.sqrt((p2 - l2) ** 2 + (u1 - p1) ** 2), d + math.sqrt((u2 - p2) ** 2 + (p1 - l1) ** 2)


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "logs/x2s_judge"
    arm = {a: {r["opponent"]: r for r in map(json.loads, open(os.path.join(d, a + ".jsonl")))} for a in ("off", "on")}
    tot = [0, 0, 0, 0]
    print(f"{'cell':20s} {'off':>6s} {'on':>6s} {'diff':>6s}  95% interval     hands per win off/on")
    for o, a in arm["off"].items():
        b = arm["on"].get(o)
        if b is None:
            print(f"{o:20s} missing in on")
            continue
        lo, hi = newcombe(a["wins"], a["matches"], b["wins"], b["matches"])
        pa, pb = a["wins"] / a["matches"], b["wins"] / b["matches"]
        print(f"{o:20s} {100 * pa:6.1f} {100 * pb:6.1f} {100 * (pb - pa):+6.1f}  [{100 * lo:+5.1f}, {100 * hi:+5.1f}]"
              f"   {a['mean_hands_per_win']}/{b['mean_hands_per_win']}")
        tot = [tot[0] + a["wins"], tot[1] + a["matches"], tot[2] + b["wins"], tot[3] + b["matches"]]
    lo, hi = newcombe(*tot)
    print(f"{'pooled':20s} {100 * tot[0] / tot[1]:6.1f} {100 * tot[2] / tot[3]:6.1f} "
          f"{100 * (tot[2] / tot[3] - tot[0] / tot[1]):+6.1f}  [{100 * lo:+5.1f}, {100 * hi:+5.1f}]")


if __name__ == "__main__":
    main()
