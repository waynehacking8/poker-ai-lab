"""Parse a hand's ``action_history`` into betting events.

The same parser serves two jobs: narrowing an opponent's range from what they
did in the current hand, and updating the long-run opponent model once the hand
has finished.  Amounts follow the Chipzen protocol: a ``raise`` amount is the
total bet on that street, a ``call`` amount is the chips added, blinds are the
chips posted.
"""

from __future__ import annotations

from dataclasses import dataclass, field

STREETS = ("preflop", "flop", "turn", "river")
SYNTHETIC = {"post_small_blind", "post_big_blind", "post_ante"}


@dataclass
class Event:
    seat: int
    kind: str  # fold / check / call / raise
    street: str
    amount: int  # raise-to total for raises, chips added for calls
    facing: bool  # the actor had to match a bet
    to_call: int  # chips the actor owed before acting
    pot_before: int  # pot before this action
    level_before: int  # highest street bet before this action
    raises_before: int  # raises already made on this street
    allin: bool  # the action put the actor's whole stack in (needs start stacks)
    first_action: bool  # first voluntary action of the hand for this seat
    is_timeout: bool = False


@dataclass
class HandInfo:
    events: list[Event] = field(default_factory=list)
    big_blind: int = 0
    small_blind: int = 0
    contrib: dict[int, int] = field(default_factory=dict)  # whole-hand chips per seat
    street_contrib: dict[int, int] = field(default_factory=dict)  # current street
    street_level: int = 0
    folded: set[int] = field(default_factory=set)
    seats: set[int] = field(default_factory=set)
    pot: int = 0
    street: str = "preflop"
    raises_this_street: int = 0
    preflop_raises: int = 0


def parse_history(history, start_stacks: dict[int, int] | None = None) -> HandInfo:
    info = HandInfo()
    seen_action: set[int] = set()
    street = "preflop"
    level = 0
    raises = 0
    for entry in history or ():
        seat = int(entry.get("seat", 0))
        action = entry.get("action", "")
        amount = int(entry.get("amount", 0) or 0)
        phase = entry.get("phase", street) or street
        info.seats.add(seat)
        if phase != street:
            street = phase
            info.street_contrib = {}
            level = 0
            raises = 0
        if action in SYNTHETIC:
            info.contrib[seat] = info.contrib.get(seat, 0) + amount
            info.street_contrib[seat] = info.street_contrib.get(seat, 0) + amount
            info.pot += amount
            if action == "post_small_blind":
                info.small_blind = amount
            elif action == "post_big_blind":
                info.big_blind = max(info.big_blind, amount)
            if action != "post_ante":
                level = max(level, amount)
            continue
        mine = info.street_contrib.get(seat, 0)
        owed = max(level - mine, 0)
        added = 0
        if action == "raise":
            added = max(amount - mine, 0)
        elif action == "call":
            added = amount
        total_after = info.contrib.get(seat, 0) + added
        allin = bool(
            start_stacks
            and seat in start_stacks
            and added > 0
            and total_after >= start_stacks[seat]
        )
        info.events.append(
            Event(
                seat=seat, kind=action, street=street, amount=amount,
                facing=owed > 0, to_call=owed, pot_before=info.pot,
                level_before=level, raises_before=raises, allin=allin,
                first_action=seat not in seen_action,
                is_timeout=bool(entry.get("is_timeout", False)),
            )
        )
        seen_action.add(seat)
        if action == "fold":
            info.folded.add(seat)
        elif action == "raise":
            info.contrib[seat] = total_after
            info.street_contrib[seat] = max(amount, mine)
            info.pot += added
            level = max(level, amount)
            raises += 1
            if street == "preflop":
                info.preflop_raises += 1
        elif action == "call":
            info.contrib[seat] = total_after
            info.street_contrib[seat] = mine + added
            info.pot += added
    info.street = street
    info.street_level = level
    info.raises_this_street = raises
    return info
