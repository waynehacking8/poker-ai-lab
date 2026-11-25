"""M3 probe: two leaks seen in v4's live loss, measured on D2a's logs (fb2-900's policy against real bot code).

1. Folding to postflop bets: fold rate by street and bet size, against the indifference line b / (P + b)
   (folding more than that lets any two cards bluff at a profit).
2. River all-ins: how often, into what pot, with what made hand, and what came of them.

Usage: python m3_leaks.py HERO DIR [DIR ...]   (each DIR holds m*.json plus true_cards.jsonl, or a live file)
"""
import collections
import glob
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import rl  # noqa: F401  (puts chipzen_bot on the path)
from nlhe.cards import cards_from
from nlhe.evaluator import category, evaluate
from rl.features import hand_strength

CAT = ["high", "pair", "two pair", "trips", "straight", "flush", "full", "quads", "straight flush"]
SIZE = [(0.0, 0.4, "<=0.4 pot"), (0.4, 0.8, "0.4-0.8"), (0.8, 1.5, "0.8-1.5"), (1.5, 99, ">1.5 pot")]


def load_true(d):
    out = {}
    p = os.path.join(d, "true_cards.jsonl")
    if os.path.exists(p):
        for line in open(p):
            r = json.loads(line)
            out[(r["match"], r["hand"])] = r["hole"]
    return out


def main(hero, dirs):
    face = collections.Counter()  # (street, size) -> [n, fold, call, raise] via keys
    ideal = collections.defaultdict(float)
    shoves = []
    types = collections.Counter()
    for d in dirs:
        true = load_true(d)
        files = sorted(glob.glob(os.path.join(d, "*.json"))) if os.path.isdir(d) else [d]
        for f in files:
            if f.endswith("summary.json"):
                continue
            rep = json.load(open(f))["replay"]
            mid = rep["metadata"]["match_id"]
            seats = {p["seat"]: p["name"] for p in rep["metadata"]["players"]}
            hs = [s for s, n in seats.items() if n == hero]
            if not hs:
                continue
            me = hs[0]
            for h in rep["hands"]:
                stack = {s["seat"]: s["starting_stack"] for s in h["starting_stacks"]}
                hole = true.get((mid, h["hand_number"]), {}).get(str(me))
                if hole is None and h.get("showdown"):
                    hole = next((e["hole_cards"] for e in h["showdown"] if e["seat"] == me), None)
                pot = 0
                for st in h["streets"]:
                    put = collections.Counter()
                    board = (h.get("community_cards") or [])[:{"preflop": 0, "flop": 3, "turn": 4, "river": 5}[st["street"]]]
                    for a in st["actions"]:
                        t, amt, s = a["action_type"], a.get("amount") or 0, a["seat"]
                        types[t] += 1
                        if s == me and st["street"] != "preflop" and not t.startswith("post"):
                            to_call = put[1 - me] - put[me]
                            if to_call > 0:
                                p_before = pot - to_call  # the pot before the opponent's bet
                                r = to_call / max(p_before, 1)
                                sz = next(lab for lo, hi, lab in SIZE if lo < r <= hi or (lo == 0 and r <= hi))
                                kind = "fold" if t == "fold" else "call" if t == "call" else "raise"
                                face[(st["street"], sz, kind)] += 1
                                face[(st["street"], sz, "n")] += 1
                                ideal[(st["street"], sz)] += to_call / (pot + 0.0)  # b / (P + b), P + b = pot now
                            left = stack[me] - put[me]
                            if st["street"] == "river" and t in ("raise", "bet", "all_in") and amt >= 0.9 * left and amt > 0:
                                after = h["stacks_after"][str(me)]
                                cat = st_ = None
                                if hole:
                                    c = cards_from(hole) + cards_from(board)
                                    cat = CAT[category(evaluate(c))] if callable(category) else None
                                    st_ = hand_strength(cards_from(hole), cards_from(board))
                                rest = st["actions"][st["actions"].index(a) + 1:]
                                resp = next((x["action_type"] for x in rest if x["seat"] != me), "none")
                                shoves.append({"match": mid, "hand": h["hand_number"], 
                                               "pot_before": pot, "amount": amt, "ratio": amt / max(pot, 1),
                                               "cat": cat, "strength": st_, "resp": resp,
                                               "net": after - stack[me]})
                        put[s] += amt
                        pot += amt
                    for s in put:
                        stack[s] -= put[s]
    print("action types:", dict(types))
    print(f"\n{hero}: facing a postflop bet (fold share vs the indifference line b/(P+b))")
    for street in ("flop", "turn", "river"):
        for _, _, sz in SIZE:
            n = face[(street, sz, "n")]
            if not n:
                continue
            print(f"  {street:5s} {sz:9s} n {n:6d}  fold {face[(street, sz, 'fold')] / n:.3f}  "
                  f"call {face[(street, sz, 'call')] / n:.3f}  raise {face[(street, sz, 'raise')] / n:.3f}  "
                  f"line {ideal[(street, sz)] / n:.3f}")
    print(f"\nriver all-ins: {len(shoves)}")
    if shoves:
        by = collections.defaultdict(list)
        for x in shoves:
            by[x["cat"]].append(x)
        for c, xs in sorted(by.items(), key=lambda kv: -len(kv[1])):
            called = [x for x in xs if x["resp"] == "call"]
            print(f"  {str(c):10s} n {len(xs):5d}  median ratio {sorted(x['ratio'] for x in xs)[len(xs) // 2]:6.1f}x pot  "
                  f"called {len(called) / len(xs):.2f}  net per shove {sum(x['net'] for x in xs) / len(xs):+8.0f}  "
                  f"net when called {sum(x['net'] for x in called) / max(len(called), 1):+8.0f}")
        weak = [x for x in shoves if x["strength"] is not None and x["strength"] < 0.6]
        print(f"  strength < 0.6 (bluffs and weak made hands): {len(weak)}, called {sum(x['resp'] == 'call' for x in weak)}, "
              f"net {sum(x['net'] for x in weak):+d}")
        json.dump(shoves, open(f"/tmp/m3_shoves_{hero}.json", "w"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
