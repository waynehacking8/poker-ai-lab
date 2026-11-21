"""Load Chipzen heads-up NLHE replays into flat per-hand records.

Only no-limit hold'em matches are kept (the replay dump also holds Pineapple OFC
matches, which use ``place`` / ``draw`` actions and a ``variant`` block).

Conventions verified against ``stacks_after`` (see ``check_conservation``):
  * ``call.amount`` is the chips added by the call,
  * ``raise.amount`` is also the chips added by the action (raise-to = put + amount),
  * blinds are ``post_small_blind`` / ``post_big_blind``; the small blind is the button.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

NLHE_ACTIONS = {"post_small_blind", "post_big_blind", "check", "call", "raise", "fold"}


@dataclass
class Act:
    seat: int
    kind: str            # fold / check / call / raise
    street: str          # preflop / flop / turn / river
    put: int             # chips this seat has put in on this street AFTER the action
    to_call: int         # chips the seat had to call before acting
    pot: int             # pot before the action
    stack: int           # seat stack before the action (after blinds)
    n_raises: int        # raises already made on this street
    raise_total: int = 0  # for a raise: the raise-to total
    opp_stack: int = 0   # the other seat's stack before the action
    bb: int = 100
    added: int = 0       # chips this action added (call / raise); 0 for fold / check


@dataclass
class HandRec:
    match_id: str
    hand_no: int
    names: tuple         # name per seat
    button: int
    bb: int
    stacks: tuple        # starting stacks per seat
    hole: dict           # seat -> [c1, c2] when shown down, else absent
    board: list
    acts: list = field(default_factory=list)
    winner_seats: tuple = ()
    showdown: bool = False
    ended: str = "preflop"
    net: tuple = (0, 0)  # net chips per seat


def is_nlhe(data: dict) -> bool:
    m, r = data.get("match") or {}, data.get("replay") or {}
    if m.get("game_type") != "poker" or not r.get("hands"):
        return False
    for h in r["hands"]:
        if h.get("variant") is not None:
            return False
        for s in h["streets"]:
            if any(a["action_type"] not in NLHE_ACTIONS for a in s["actions"]):
                return False
    return True


def parse_hand(match_id: str, h: dict) -> HandRec | None:
    names = [None, None]
    stacks = [0, 0]
    for s in h["starting_stacks"]:
        names[s["seat"]] = s["name"]
        stacks[s["seat"]] = s["starting_stack"]
    bb = h["blinds"]["big_blind"]
    pre = h["streets"][0]["actions"] if h["streets"] else []
    button = next((a["seat"] for a in pre if a["action_type"] == "post_small_blind"), None)
    if button is None or None in names:
        return None
    sd = h.get("showdown") or []
    hole = {}
    for e in sd:
        hole[e["seat"]] = list(e["hole_cards"])[:2]
    rec = HandRec(match_id, h["hand_number"], tuple(names), button, bb, tuple(stacks), hole,
                  list(h.get("community_cards") or []))
    stack = list(stacks)
    pot = 0
    for st in h["streets"]:
        put = [0, 0]
        level = 0
        nraise = 0
        for a in st["actions"]:
            seat, kind, amt = a["seat"], a["action_type"], a["amount"]
            if kind.startswith("post_"):
                put[seat] += amt
                stack[seat] -= amt
                pot += amt
                level = max(level, put[seat])
                continue
            to_call = level - put[seat]
            rec.acts.append(Act(seat, kind, st["street"], put[seat], to_call, pot,
                                stack[seat], nraise, opp_stack=stack[1 - seat], bb=bb,
                                added=amt if kind in ("call", "raise") else 0))
            if kind == "call":
                stack[seat] -= amt
                put[seat] += amt
                pot += amt
            elif kind == "raise":
                stack[seat] -= amt
                pot += amt
                put[seat] += amt
                level = put[seat]
                nraise += 1
                rec.acts[-1].raise_total = put[seat]
                rec.acts[-1].put = put[seat]
            if kind == "call":
                rec.acts[-1].put = put[seat]
        rec.ended = st["street"]
    rec.winner_seats = tuple((h.get("result") or {}).get("winner_seats") or ())
    rec.showdown = bool(sd)
    after = h.get("stacks_after") or {}
    rec.net = tuple(int(after.get(str(s), stacks[s])) - stacks[s] for s in (0, 1))
    rec._end_stacks = stack  # for conservation check
    rec._pot = pot
    rec._payouts = h.get("payouts") or {}
    return rec


def load_dir(directory) -> list[tuple[dict, list[HandRec]]]:
    out = []
    for p in sorted(Path(directory).glob("*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        if not is_nlhe(data):
            continue
        m = data["match"]
        hands = [x for x in (parse_hand(m["id"], h) for h in data["replay"]["hands"]) if x]
        out.append((m, hands))
    return out


def check_conservation(hands) -> tuple[int, int]:
    """(consistent, total): start - paid + payout == stacks_after for every seat."""
    ok = tot = 0
    for h in hands:
        for s in (0, 1):
            tot += 1
            paid = h.stacks[s] - h._end_stacks[s]
            pay = int(h._payouts.get(str(s), 0))
            if h.net[s] == pay - paid:
                ok += 1
    return ok, tot
