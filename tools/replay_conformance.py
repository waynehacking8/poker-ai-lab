"""Replay real Chipzen NLHE hands through holdem/engine.py and report every difference.

For each hand the engine is driven by a script that plays the recorded actions.  A hand
passes when the engine asks the same seat on the same street for each recorded action,
offers that action as legal, accepts the raise size, posts the same blinds, ends with no
recorded action left over and reaches the recorded ``stacks_after``.  Replay ``raise``
amounts are chips added by the action, not raise-to totals.  Unknown hole cards and
undealt board cards are filled in deterministically (they do not change betting).

Matches with variant actions (anything outside post/fold/check/call/raise) are skipped.

Usage:
    python tools/replay_conformance.py [REPLAY_DIR] [--show N]
    (REPLAY_DIR defaults to .cache/chipzen-replays; exit code 1 when any hand fails)
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import holdem  # noqa: E402,F401  (puts chipzen_bot on sys.path)
from chipzen import Action  # noqa: E402
from holdem.engine import Hand, IllegalAction  # noqa: E402
from nlhe.cards import card_from_str  # noqa: E402

DEFAULT_DIR = Path(__file__).resolve().parent.parent / ".cache" / "chipzen-replays"
KNOWN = {"post_small_blind", "post_big_blind", "fold", "check", "call", "raise"}


class Mismatch(Exception):
    pass


class Script:
    def __init__(self, queue):
        self.q = queue

    def decide(self, st):
        if not self.q:
            raise Mismatch(f"engine asked seat {st.your_seat} {st.phase} but replay has no more actions")
        street, a = self.q[0]
        if a["seat"] != st.your_seat or street != st.phase:
            raise Mismatch(f"engine asks seat {st.your_seat}/{st.phase}, replay next is "
                           f"seat {a['seat']}/{street} {a['action_type']}")
        self.q.pop(0)
        t = a["action_type"]
        if t not in st.valid_actions:
            raise Mismatch(f"replay action {t} not in engine valid {st.valid_actions} "
                           f"(seat {st.your_seat} {st.phase} to_call {st.to_call})")
        if t == "raise":
            to = (st.max_raise - st.your_stack) + a["amount"]  # amount is chips added
            lo = min(st.min_raise, st.max_raise)
            if not lo <= to <= st.max_raise:
                raise Mismatch(f"replay raise-to {to} outside engine [{lo},{st.max_raise}] "
                               f"(min_raise {st.min_raise})")
            return Action.raise_to(to)
        return Action(action=t)


def check_hand(h):
    """Play one recorded hand; raise Mismatch / IllegalAction on any difference."""
    acts = [(s["street"], a) for s in h["streets"] for a in s["actions"]]
    syn = [a for _, a in acts if a["action_type"].startswith("post")]
    q = [(st, a) for st, a in acts if not a["action_type"].startswith("post")]
    stacks = {s["seat"]: s["starting_stack"] for s in h["starting_stacks"]}
    stacks = [stacks[0], stacks[1]]
    dealer = [a["seat"] for a in syn if a["action_type"] == "post_small_blind"][0]
    sb, bb = h["blinds"]["small_blind"], h["blinds"]["big_blind"]
    board = [card_from_str(c) for c in h["community_cards"]]
    holes = {}
    for sd in h.get("showdown") or []:
        holes[sd["seat"]] = [card_from_str(c) for c in sd["hole_cards"]]
    for k, v in (h.get("hole_cards") or {}).items():
        holes.setdefault(int(k), [card_from_str(c) for c in v])
    used = set(board) | {c for v in holes.values() for c in v}
    rest = [c for c in range(52) if c not in used]
    random.Random(1).shuffle(rest)
    for s in (0, 1):
        if s not in holes:
            holes[s] = [rest.pop(), rest.pop()]
    full = board + [rest.pop() for _ in range(5 - len(board))]
    deck = holes[0] + holes[1] + full
    bots = [Script(q), Script(q)]
    hand = Hand(bots, stacks, dealer, h["hand_number"], sb, bb, deck, strict=True)
    hand.play()
    posted = [(e["seat"], e["action"], e["amount"]) for e in hand.history if e["action"].startswith("post")]
    real = [(a["seat"], a["action_type"], a["amount"]) for a in syn]
    if posted != real:
        raise Mismatch(f"blinds engine {posted} vs replay {real}")
    if q:
        raise Mismatch(f"engine ended hand with {len(q)} replay actions left: {q[0][0]} {q[0][1]['action_type']}")
    sa = h["stacks_after"]
    want = [sa["0"], sa["1"]]
    if hand.stack != want:
        raise Mismatch(f"stacks engine {hand.stack} vs replay {want} (start {stacks}, blinds {sb}/{bb})")
    if sum(hand.stack) != sum(stacks):
        raise Mismatch("chips not conserved")


def run(directory):
    """Return (counts, failures); failures is a list of (match#hand, reason)."""
    res = collections.Counter()
    bad = []
    for f in sorted(glob.glob(str(Path(directory) / "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        hands = d["replay"]["hands"]
        if not hands or hands[0]["streets"][0]["actions"][0]["action_type"] != "post_small_blind":
            continue
        if any(a["action_type"] not in KNOWN for h in hands for st in h["streets"] for a in st["actions"]):
            res["skipped_variant_match"] += 1
            continue
        for h in hands:
            key = f"{Path(f).stem}#{h['hand_number']}"
            try:
                check_hand(h)
                res["ok"] += 1
            except (Mismatch, IllegalAction) as e:
                res["bad"] += 1
                bad.append((key, repr(e)[:300]))
    return res, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory", nargs="?", default=str(DEFAULT_DIR))
    ap.add_argument("--show", type=int, default=40)
    args = ap.parse_args()
    res, bad = run(args.directory)
    print(dict(res))
    for b in bad[: args.show]:
        print(b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
