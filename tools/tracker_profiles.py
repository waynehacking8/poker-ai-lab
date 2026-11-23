"""Per-name opponent profiles for the in-match tracker (roadmap X2a).

    python tools/tracker_profiles.py --data DIR [--out rl/models/tracker_prior.npz]

Every hand of every poker replay in DIR is converted to the action_history the live server sends, run through
rl.features.Tracker.update itself with `me` set to the other seat, and the counts are summed per player name.
Names with at least MIN_HANDS hands get a profile: the counts scaled so the hand count st[10] is H0.

Replay -> live conversion (holdem/engine.py documents the live form; tools/replay_conformance.py the replay one):
posts, fold, check and call keep their amount (chips added); a replay `raise` or `all_in` adds chips on top of the
street's bet, so its live amount is the raise-to total (street bet before + chips added); one that adds no more than
the amount to call is an all-in for less and is a call. Names: the starting_stacks name of each seat.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from rl.features import Tracker  # noqa: E402

H0 = 20.0
MIN_HANDS = 100


def load_replays(data_dir):
    """Poker replays of DIR in file name order (the other files hold different games)."""
    out = []
    for f in sorted(glob.glob(os.path.join(data_dir, "*.json"))):
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        if d["match"].get("game_type") == "poker":
            out.append(d["replay"])
    return out


def to_history(hand, stats=None, raise_to=True):
    """Live-form action_history of one replay hand. stats (a dict) counts the all-ins for less.
    raise_to=False keeps the replay's chips added (the mutation of acceptance 1: it must fail the check)."""
    hist = []
    bet = {}
    level = 0
    cur = None
    for st in hand["streets"]:
        if st["street"] != cur:
            cur = st["street"]
            bet = {0: 0, 1: 0}
            level = 0
        for a in st["actions"]:
            seat, kind, amt = a["seat"], a["action_type"], a["amount"]
            if kind in ("raise", "all_in"):
                if amt <= level - bet[seat]:
                    if stats is not None:
                        stats["allin_for_less"] = stats.get("allin_for_less", 0) + 1
                    kind = "call"
                else:
                    amt = bet[seat] + amt if raise_to else amt
                    kind = "raise"
            if kind in ("post_small_blind", "post_big_blind", "call"):
                bet[seat] += amt
            elif kind == "raise":
                bet[seat] = amt
            level = max(level, bet[seat])
            hist.append({"seat": seat, "action": kind, "amount": amt, "phase": cur, "is_timeout": False})
    return hist


def raw_counts(replays, stats=None, raise_to=True):
    """{name: NST unscaled counts}, from Tracker.update on every hand and seat."""
    counts = {}
    for r in replays:
        for h in r["hands"]:
            hist = to_history(h, stats, raise_to)
            dealer = next(e["seat"] for e in hist if e["action"] == "post_small_blind")
            names = {s["seat"]: s["name"] for s in h["starting_stacks"]}
            for seat, name in names.items():
                tr = counts.setdefault(name, Tracker())
                tr.me = 1 - seat
                tr.update(hist, dealer)
    return {n: list(t.st) for n, t in counts.items()}


def scaled(counts):
    """Profile table: names with MIN_HANDS hands or more, counts scaled to H0 hands."""
    return {n: [x * H0 / c[10] for x in c] for n, c in counts.items() if c[10] >= MIN_HANDS}


def save(table, path):
    names = sorted(table)
    np.savez_compressed(path, names=np.array(names), counts=np.array([table[n] for n in names], dtype=np.float64))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rl", "models",
                                                  "tracker_prior.npz"))
    args = ap.parse_args()
    replays = load_replays(args.data)
    stats = {}
    counts = raw_counts(replays, stats)
    table = scaled(counts)
    save(table, args.out)
    print(f"{len(replays)} poker replays, {len(counts)} names, {len(table)} with a profile (>= {MIN_HANDS} hands, "
          f"scaled to {H0:g} hands), all-ins for less read as calls: {stats.get('allin_for_less', 0)}")
    for n in sorted(counts, key=lambda n: -counts[n][10]):
        print(f"  {int(counts[n][10]):6d} hands  {'profile' if n in table else '-':7s}  {n}")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
