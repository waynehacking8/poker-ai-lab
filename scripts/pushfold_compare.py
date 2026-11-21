"""Compare the shipped CFR+ push/fold table with published HU Nash numbers.

Reference (PokerStrategy HU Nash charts, no antes): SB shove 74.1 / 56.6 / 45.7 / 40.9 %
and BB call 68.6 / 38.5 / 28.4 / 21.7 % at 5 / 10 / 15 / 20 BB.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "chipzen_bot"))

from nlhe import preflop as pf  # noqa: E402

REF = {5: (74.1, 68.6), 10: (56.6, 38.5), 15: (45.7, 28.4), 20: (40.9, 21.7)}


def main():
    d = json.load(open(os.path.join(ROOT, "chipzen_bot", "nlhe", "data", "pushfold.json")))
    print("stack  SB shove (ours / ref)   BB call (ours / ref)   exploitability bb/hand")
    for s, (rp, rc) in REF.items():
        i = d["stacks"].index(float(s))
        ours_p = 100 * pf.mean_weight(pf.nash_push(s))
        ours_c = 100 * pf.mean_weight(pf.nash_call(s))
        print(f"{s:4d}   {ours_p:5.1f} / {rp:5.1f}          {ours_c:5.1f} / {rc:5.1f}"
              f"          {d['exploitability'][i]:.5f}")


if __name__ == "__main__":
    main()
