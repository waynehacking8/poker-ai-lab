"""Per-hand chip flow of one RL policy against one opponent: where matches are won and lost.

Plays duplicate pairs like holdem/arena.py (same seeds, seats swapped) and logs every hand from the
hero's side: blind, effective stack in big blinds, chip delta, how the hand ended and, for all-in
showdowns, the hero's equity when the money went in (exact after the flop, 4000 sampled boards
preflop). Actual minus expected chips on all-in hands is card luck; the rest comes from decisions.

    python tools/chipflow.py --model rl/models/fb2_it000900.npz --opp bp100 --matches 400 --seed 3 \
        --workers 2 --out logs/bp_diag/fb2_900_bp100.jsonl
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import sys
from collections import defaultdict
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rl  # noqa: E402,F401  (puts chipzen_bot on sys.path)
from holdem.engine import MatchConfig, play_match  # noqa: E402
from holdem.opponents import make_baseline  # noqa: E402
from nlhe.cards import card_from_str, cards_from  # noqa: E402
from nlhe.evaluator import evaluate  # noqa: E402
from rl.eval_arena import make_bp100, make_hero  # noqa: E402
from rl.features import bb_for  # noqa: E402


def equity(h, o, board, rng, samples=4000):
    used = set(h) | set(o) | set(board)
    deck = [c for c in range(52) if c not in used]
    need = 5 - len(board)
    runs = (itertools.combinations(deck, need) if need <= 2
            else (rng.sample(deck, need) for _ in range(samples)))
    w = n = 0
    for ext in runs:
        b = board + list(ext)
        a, c = evaluate(h + b), evaluate(o + b)
        w += 1.0 if a > c else 0.5 if a == c else 0.0
        n += 1
    return w / n


class Logged:
    """Wraps the hero bot; remembers the board at its last decision and logs each finished hand."""

    def __init__(self, bot, seat, rows, rng):
        self.bot, self.seat, self.rows, self.rng = bot, seat, rows, rng
        self.prev = [MatchConfig().starting_stack] * 2
        self.board = []

    def __getattr__(self, k):
        return getattr(self.bot, k)

    def on_round_start(self, message):
        self.board = []
        self.bot.on_round_start(message)

    def decide(self, state):
        self.board = cards_from(state.board)
        return self.bot.decide(state)

    def on_round_result(self, message):
        self.bot.on_round_result(message)
        r = message["result"]
        me, op = self.seat, 1 - self.seat
        before, after = self.prev, list(r["stacks"])
        self.prev = after
        pay = [0, 0]
        for p in r["payouts"]:
            pay[p["seat"]] = p["amount"]
        inv = [before[s] - after[s] + pay[s] for s in (0, 1)]
        hist = r["action_history"]
        bb = bb_for(r["hand_number"])
        row = {"hand": r["hand_number"], "bb": bb, "eff_bb": min(before) / bb, "delta": after[me] - before[me]}
        folds = [e for e in hist if e["action"] == "fold"]
        if folds:
            f = folds[0]
            row["end"] = ("hero" if f["seat"] == me else "opp") + "_folds_" + ("pre" if f["phase"] == "preflop" else "post")
        else:
            allin = min(inv) >= min(before)
            row["end"] = "allin" if allin else "showdown"
            if allin:
                hole = {s["seat"]: [card_from_str(c) for c in s["hole_cards"]] for s in r["showdown"]}
                eq = equity(hole[me], hole[op], self.board, self.rng)
                contested = 2 * min(inv)
                row["eq"] = round(eq, 4)
                row["street"] = ("preflop", "x", "x", "flop", "turn", "river")[len(self.board)]
                row["ev_delta"] = round(eq * contested + max(0, inv[me] - inv[op]) - inv[me], 1)
        pre = [e for e in hist if e["phase"] == "preflop" and e["action"] not in ("post_small_blind", "post_big_blind")]
        for who, s in (("hero", me), ("opp", op)):
            first = next((e["action"] for e in pre if e["seat"] == s), None)
            row[who + "_pre"] = first
        self.rows.append(row)


def run_one(job):
    model, opp_name, pair_seed, seat = job
    rows = []
    hero = Logged(make_hero(model, 1.0, pair_seed * 7 + seat), seat, rows, random.Random(pair_seed * 31 + seat))
    if opp_name == "bp100":
        opp = make_bp100()
    elif opp_name.startswith("ext:"):
        from rl.field_bots import build
        opp = build(opp_name)
    else:
        opp = make_baseline(opp_name, pair_seed * 13 + seat)
    bots = [None, None]
    bots[seat], bots[1 - seat] = hero, opp
    res = play_match(bots, pair_seed, MatchConfig())
    for x in rows:
        x["match"] = f"{pair_seed}:{seat}"
    return {"match": f"{pair_seed}:{seat}", "won": res.winner == seat, "hands": res.hands, "rows": rows}


def summarize(matches):
    rows = [x for m in matches for x in m["rows"]]
    won = sum(m["won"] for m in matches)
    print(f"matches {len(matches)}  won {won} ({100 * won / len(matches):.1f}%)  hands {len(rows)}")
    print("\nchips by effective stack at hand start (bb per hand, total in big blinds):")
    for lo, hi in ((60, 1e9), (30, 60), (15, 30), (0, 15)):
        xs = [x for x in rows if lo <= x["eff_bb"] < hi]
        if xs:
            tot = sum(x["delta"] / x["bb"] for x in xs)
            print(f"  {lo:>3}+ bb  hands {len(xs):5d}  {tot / len(xs):+6.2f} bb/hand  total {tot:+8.0f} bb")
    print("\nhow hands end (count, chips total):")
    by = defaultdict(list)
    for x in rows:
        by[x["end"]].append(x["delta"])
    for k in sorted(by):
        print(f"  {k:18s} {len(by[k]):5d}  {sum(by[k]):+10.0f}")
    ai = [x for x in rows if x["end"] == "allin"]
    if ai:
        act, ev = sum(x["delta"] for x in ai), sum(x["ev_delta"] for x in ai)
        print(f"\nall-in showdowns {len(ai)}: actual {act:+.0f}, expected {ev:+.0f}, luck {act - ev:+.0f} chips")
        for st in ("preflop", "flop", "turn", "river"):
            s = [x for x in ai if x["street"] == st]
            if s:
                print(f"  {st:7s} {len(s):4d}  mean equity {sum(x['eq'] for x in s) / len(s):.3f}  "
                      f"expected {sum(x['ev_delta'] for x in s):+8.0f}  actual {sum(x['delta'] for x in s):+8.0f}")
    lost = [m for m in matches if not m["won"]]
    last = [m["rows"][-1] for m in lost if m["rows"]]
    fav = [x for x in last if x["end"] == "allin" and x["eq"] >= 0.5]
    dog = [x for x in last if x["end"] == "allin" and x["eq"] < 0.5]
    print(f"\nlost matches {len(lost)}: final hand all-in as favourite {len(fav)}, as underdog {len(dog)}, "
          f"other {len(last) - len(fav) - len(dog)}")
    print("\npreflop first action (share of hands where the player acted):")
    for who in ("hero", "opp"):
        acts = [x[who + "_pre"] for x in rows if x[who + "_pre"]]
        c = defaultdict(int)
        for a in acts:
            c[a] += 1
        print(f"  {who:4s} " + "  ".join(f"{k} {100 * v / len(acts):.1f}%" for k, v in sorted(c.items())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--opp", required=True, help="bp100, ext:<field bot> or a baseline name")
    ap.add_argument("--matches", type=int, default=400)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    model = os.path.abspath(args.model)
    jobs = [(model, args.opp, args.seed * 100000 + k, seat) for k in range(args.matches // 2) for seat in (0, 1)]
    with Pool(args.workers) as pool:
        matches = pool.map(run_one, jobs, chunksize=2)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        for m in matches:
            f.write(json.dumps(m) + "\n")
    summarize(matches)


if __name__ == "__main__":
    main()
