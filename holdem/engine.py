"""Heads-up No-Limit Hold'em engine that drives bots through the real SDK objects.

Bots see exactly what they see on Chipzen: a ``chipzen.models.GameState`` built
from the live protocol's fields, plus the ``on_round_start`` / ``on_round_result``
hook messages.  Rules follow the platform's protocol notes:

  * the button posts the small blind and acts first preflop; the big blind acts
    first on every later street,
  * ``min_raise`` / ``max_raise`` are raise-to totals, ``min_raise`` can exceed
    ``max_raise`` (then only the shove is legal), there is no ``all_in`` action,
  * a short all-in raise does not reopen the betting for a seat that already acted,
  * the uncalled part of a bet is returned, odd chips go to the big blind,
  * a big blind that is all in for no more than the small blind's post is never
    answered: the hand runs out and the small blind gets the excess back.

The match format mirrors the real season fixtures: 10,000 chip stacks, blinds
50/100 rising every 20 hands (100, 150, 200, 300, 400, 600 big blind), played
until one player is bust.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from chipzen.models import Card, GameState

from nlhe.cards import card_str
from nlhe.evaluator import category_name, evaluate

# Observed levels (NLHE replays reach hand 117): big blind 100 for hands 1-20, 150 to 40,
# 200 to 60, 300 to 80, 400 to 100, 600 from hand 101.  The levels past 600 are
# INFERRED from the same platform's OFC replays (800 from hand 121, 1000 from hand 141,
# last observed hand 146); nothing past hand 146 has been observed.  Held at 1000 after that.
SCHEDULE = ((20, 100), (40, 150), (60, 200), (80, 300), (100, 400), (120, 600), (140, 800))
FINAL_BB = 1000


def blinds_for_hand(hand_number: int, schedule=SCHEDULE, final_bb: int = FINAL_BB):
    """(small blind, big blind) for a 1-indexed hand under the season schedule."""
    for last_hand, bb in schedule:
        if hand_number <= last_hand:
            return bb // 2, bb
    return final_bb // 2, final_bb


@dataclass
class MatchConfig:
    starting_stack: int = 10000
    max_hands: int = 1000
    schedule: tuple = SCHEDULE
    final_bb: int = FINAL_BB


@dataclass
class MatchResult:
    winner: int | None  # seat index, None for a tie at the hand cap
    hands: int
    stacks: list[int]
    capped: bool = False
    log: list = field(default_factory=list)


class IllegalAction(Exception):
    pass


def _cards(ints):
    return [Card.from_str(card_str(c)) for c in ints]


class Hand:
    """One hand of heads-up play."""

    def __init__(self, bots, stacks, dealer, hand_number, sb, bb, deck, strict=True):
        self.bots = bots
        self.stack = list(stacks)
        self.dealer = dealer
        self.hand_number = hand_number
        self.sb, self.bb = sb, bb
        self.hole = [deck[0:2], deck[2:4]]
        self.full_board = deck[4:9]
        self.board: list[int] = []
        self.history: list[dict] = []
        self.contrib = [0, 0]  # whole hand
        self.bet = [0, 0]  # this street
        self.folded = [False, False]
        self.strict = strict
        self.start_stacks = list(stacks)
        self.pot = 0

    # -- helpers ---------------------------------------------------------
    def _post(self, seat, amount, action, phase="preflop"):
        paid = min(amount, self.stack[seat])
        self.stack[seat] -= paid
        self.bet[seat] += paid
        self.contrib[seat] += paid
        self.pot += paid
        self.history.append({"seat": seat, "action": action, "amount": paid,
                             "phase": phase, "is_timeout": False})

    def _state(self, seat, phase, to_call, min_raise, max_raise, valid):
        return GameState(
            hand_number=self.hand_number, phase=phase,
            hole_cards=_cards(self.hole[seat]), board=_cards(self.board),
            pot=self.pot, your_stack=self.stack[seat],
            opponent_stacks=[self.stack[1 - seat]], your_seat=seat,
            dealer_seat=self.dealer, to_call=to_call, min_raise=min_raise,
            max_raise=max_raise, valid_actions=list(valid),
            action_history=[dict(e) for e in self.history],
            round_id=f"h{self.hand_number}", request_id="",
        )

    # -- betting ---------------------------------------------------------
    def _betting_round(self, phase, first):
        # the bet to match preflop is the larger post: a short all-in big blind does not
        # raise it above the small blind's post (the server never prompts the small blind then)
        level = max(self.bet) if phase == "preflop" else 0
        last_raise = self.bb
        pending = [s for s in (first, 1 - first) if self.stack[s] > 0]
        acted: set[int] = set()
        can_raise = [True, True]
        while pending:
            seat = pending.pop(0)
            other = 1 - seat
            if self.folded[other]:
                return
            to_call = max(level - self.bet[seat], 0)
            opp_can_act = self.stack[other] > 0
            if to_call == 0 and not opp_can_act:
                continue  # nobody left to bet against
            valid = []
            if to_call > 0:
                valid.append("fold")
                valid.append("call")
            else:
                valid.append("check")
            max_raise = self.bet[seat] + self.stack[seat]
            min_raise = level + last_raise
            if opp_can_act and self.stack[seat] > to_call and can_raise[seat]:
                valid.append("raise")
            state = self._state(seat, phase, to_call, min_raise, max_raise, valid)
            action = self._ask(seat, state)
            kind, amount = action.action, action.amount
            if kind not in valid:
                if self.strict:
                    raise IllegalAction(f"seat {seat} sent {kind} not in {valid}")
                kind = "check" if "check" in valid else "fold"
            if kind == "fold":
                self.folded[seat] = True
                self.history.append({"seat": seat, "action": "fold", "amount": 0,
                                     "phase": phase, "is_timeout": False})
                return
            acted.add(seat)
            if kind == "check":
                self.history.append({"seat": seat, "action": "check", "amount": 0,
                                     "phase": phase, "is_timeout": False})
            elif kind == "call":
                paid = min(to_call, self.stack[seat])
                self._pay(seat, paid)
                self.history.append({"seat": seat, "action": "call", "amount": paid,
                                     "phase": phase, "is_timeout": False})
            else:  # raise
                lo = min(min_raise, max_raise)
                if not lo <= amount <= max_raise:
                    if self.strict:
                        raise IllegalAction(
                            f"seat {seat} raise {amount} outside [{lo}, {max_raise}]")
                    amount = max(lo, min(max_raise, amount))
                self._pay(seat, amount - self.bet[seat])
                self.history.append({"seat": seat, "action": "raise", "amount": amount,
                                     "phase": phase, "is_timeout": False})
                increment = amount - level
                if increment >= last_raise:
                    last_raise = increment
                    can_raise = [True, True]
                elif other in acted:
                    can_raise[other] = False  # short all-in does not reopen
                level = amount
                pending = [other] if self.stack[other] > 0 else []
                continue
            # after a call/check the remaining pending seats stay; a call that
            # matches the level closes action for this seat only

    def _pay(self, seat, chips):
        self.stack[seat] -= chips
        self.bet[seat] += chips
        self.contrib[seat] += chips
        self.pot += chips

    def _ask(self, seat, state):
        try:
            return self.bots[seat].decide(state)
        except Exception:
            if self.strict:
                raise
            from chipzen import Action
            return Action.fold() if state.to_call > 0 else Action.check()

    # -- the hand --------------------------------------------------------
    def play(self):
        d, n = self.dealer, 1 - self.dealer
        self._post(d, self.sb, "post_small_blind")
        self._post(n, self.bb, "post_big_blind")
        msg = {"type": "round_start", "state": {
            "hand_number": self.hand_number, "dealer_seat": d, "pot": self.pot,
            "stacks": list(self.start_stacks),
            "post_blind_stacks": list(self.stack)}}
        for s in (0, 1):
            m = {**msg, "state": {**msg["state"],
                                  "your_hole_cards": [card_str(c) for c in self.hole[s]]}}
            hook = getattr(self.bots[s], "on_round_start", None)
            if hook:
                hook(m)
        phases = [("preflop", 0), ("flop", 3), ("turn", 4), ("river", 5)]
        for phase, ncards in phases:
            if phase != "preflop":
                self.board = list(self.full_board[:ncards])
                self.bet = [0, 0]
            first = d if phase == "preflop" else n
            if self.stack[0] > 0 or self.stack[1] > 0:
                self._betting_round(phase, first)
            if any(self.folded):
                break
        self.board = list(self.full_board) if not any(self.folded) else self.board
        return self._settle()

    def _settle(self):
        c = self.contrib
        showdown = []
        payouts = [0, 0]
        if any(self.folded):
            winner = 1 if self.folded[0] else 0
            payouts[winner] = self.pot
            winners = [winner]
        else:
            # return the uncalled excess to the bigger contributor
            big = 0 if c[0] > c[1] else 1
            excess = abs(c[0] - c[1])
            contested = self.pot - excess
            payouts[big] += excess
            scores = [evaluate(self.hole[s] + self.full_board) for s in (0, 1)]
            for s in (0, 1):
                showdown.append({"seat": s, "hole_cards": [card_str(x) for x in self.hole[s]],
                                 "hand_rank": category_name(scores[s]), "best_hand": []})
            if scores[0] > scores[1]:
                winners = [0]
            elif scores[1] > scores[0]:
                winners = [1]
            else:
                winners = [0, 1]
            if len(winners) == 1:
                payouts[winners[0]] += contested
            else:
                half = contested // 2
                payouts[0] += half
                payouts[1] += half
                if contested % 2:
                    payouts[1 - self.dealer] += 1  # odd chip to the big blind
        for s in (0, 1):
            self.stack[s] += payouts[s]
        result = {
            "hand_number": self.hand_number, "winner_seats": winners, "pot": self.pot,
            "payouts": [{"seat": s, "amount": payouts[s]} for s in (0, 1) if payouts[s]],
            "showdown": showdown, "action_history": [dict(e) for e in self.history],
            "stacks": list(self.stack),
        }
        for s in (0, 1):
            hook = getattr(self.bots[s], "on_round_result", None)
            if hook:
                hook({"type": "round_result", "result": result})
        return result


def play_match(bots, seed: int, config: MatchConfig | None = None, strict: bool = True,
               on_hand=None):
    """Play one match between ``bots[0]`` and ``bots[1]`` until a bust or the hand cap."""
    cfg = config or MatchConfig()
    stacks = [cfg.starting_stack, cfg.starting_stack]
    for s, b in enumerate(bots):
        hook = getattr(b, "on_match_start", None)
        if hook:
            hook({"type": "match_start", "your_seat": s,
                  "seats": [{"seat": i, "is_self": i == s} for i in (0, 1)],
                  "game_config": {"starting_stack": cfg.starting_stack, "num_players": 2,
                                  "small_blind": 50, "big_blind": 100, "ante": 0}})
    hands = 0
    while min(stacks) > 0 and hands < cfg.max_hands:
        hands += 1
        sb, bb = blinds_for_hand(hands, cfg.schedule, cfg.final_bb)
        rng = random.Random(seed * 1_000_003 + hands)
        deck = list(range(52))
        rng.shuffle(deck)
        dealer = (hands - 1) % 2
        hand = Hand(bots, stacks, dealer, hands, sb, bb, deck, strict)
        result = hand.play()
        if on_hand:
            on_hand(hand, result)
        stacks = list(hand.stack)
    capped = min(stacks) > 0
    if stacks[0] == stacks[1]:
        winner = None
    else:
        winner = 0 if stacks[0] > stacks[1] else 1
    return MatchResult(winner=winner, hands=hands, stacks=stacks, capped=capped)
