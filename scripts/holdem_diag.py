"""Where do the chips go? Bucket per-hand results by position, preflop line and last street.

    python scripts/holdem_diag.py DEPTH_BB OPPONENT HANDS
"""

import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holdem import cash  # noqa: E402


def main():
    depth, opp, n = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
    cash.TRACE = []
    cash._chunk((opp, depth, 5, n))
    agg = collections.defaultdict(lambda: [0, 0.0])
    for btn, hist, res in cash.TRACE:
        pre = [e for e in hist if e["phase"] == "preflop" and not e["action"].startswith("post")]
        key = ("BTN" if btn else "BB", " ".join(e["action"][:2] for e in pre)[:24], hist[-1]["phase"])
        agg[key][0] += 1
        agg[key][1] += res
    show = sys.argv[4] if len(sys.argv) > 4 else None  # e.g. "BB|ra ca|turn" prints examples
    if show:
        pos, line, street = show.split("|")
        shown = 0
        for btn, hist, res in cash.TRACE:
            pre = [e for e in hist if e["phase"] == "preflop" and not e["action"].startswith("post")]
            key = ("BTN" if btn else "BB", " ".join(e["action"][:2] for e in pre)[:24], hist[-1]["phase"])
            if key == (pos, line, street) and shown < 12:
                shown += 1
                print(round(res, 1), [("H" if e["seat"] == (0 if btn else 1) else "O") + ":" + e["phase"][:2]
                                      + ":" + e["action"][:2] + str(e["amount"]) for e in hist
                                      if not e["action"].startswith("post")])
    for k, v in sorted(agg.items(), key=lambda kv: kv[1][1]):
        if v[0] >= 20:
            print(k, v[0], round(v[1] / v[0], 2), round(v[1], 0))


if __name__ == "__main__":
    main()
