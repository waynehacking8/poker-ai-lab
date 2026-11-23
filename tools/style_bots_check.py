"""Distance of each rule style bot (holdem/opponents.py STYLES) from its field target.

    python tools/style_map.py sim raise_station,sticky_overbettor,tight_sticky,never_fold_pre HERO.npz 60 3 2 OUT.json
    python tools/style_bots_check.py OUT.json [OUT2.json ...]

Targets are measured field vectors (.cache/style_field.json); a missing axis counts as 0.5, as in
style_map.py compare. Prints the Euclidean distance per bot and the per axis gap.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style_map import AXES  # noqa: E402

TARGETS = {
    "raise_station": dict(vpip=0.89, pfr=0.67, shove=0.00, fold_pre_raise=0.00, post_aggr=0.00,
                          post_fold_bet=0.00, bet_size=None, showdown=0.88),
    "sticky_overbettor": dict(vpip=0.61, pfr=0.53, shove=0.00, fold_pre_raise=0.59, post_aggr=0.72,
                              post_fold_bet=0.11, bet_size=0.71, showdown=0.08),
    "tight_sticky": dict(vpip=0.32, pfr=0.14, shove=0.00, fold_pre_raise=0.72, post_aggr=0.32,
                         post_fold_bet=0.29, bet_size=0.32, showdown=0.21),
    "never_fold_pre": dict(vpip=0.84, pfr=0.41, shove=0.00, fold_pre_raise=0.02, post_aggr=0.32,
                           post_fold_bet=0.21, bet_size=0.40, showdown=0.62),
}


def vec(v):
    return [v[a] if v.get(a) is not None else 0.5 for a in AXES]


if __name__ == "__main__":
    for path in sys.argv[1:]:
        res = json.load(open(path))
        print(path)
        print(f"{'bot':18} {'dist':>5} " + " ".join(f"{a[:7]:>7}" for a in AXES))
        for name, target in TARGETS.items():
            if name not in res:
                continue
            m, t = vec(res[name]), vec(target)
            d = sum((x - y) ** 2 for x, y in zip(m, t)) ** 0.5
            print(f"{name:18} {d:5.3f} " + " ".join(f"{x:7.2f}" for x in m))
            print(f"{'  target':18} {'':>5} " + " ".join(f"{x:7.2f}" for x in t))
