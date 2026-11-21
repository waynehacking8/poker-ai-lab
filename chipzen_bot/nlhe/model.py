"""Light online opponent model.

Every rate is a Beta-style estimate that starts at a prior (what the Chipzen
field looks like) and only moves as real observations accumulate: with ``k``
pseudo-observations of prior, 15 samples pull a rate about halfway.  Preflop
folds count towards fold-to-bet, which matters against bots that simply fold.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from .cards import card_from_str, hand_class
from .history import parse_history
from .preflop import PCT

PRIOR_K = 16.0


class Counter2:
    """Hits out of opportunities with a prior."""

    __slots__ = ("hit", "opp", "prior", "k")

    def __init__(self, prior: float, k: float = PRIOR_K):
        self.hit = 0
        self.opp = 0
        self.prior = prior
        self.k = k

    def add(self, hit: bool):
        self.opp += 1
        self.hit += 1 if hit else 0

    def rate(self, k: float | None = None) -> float:
        k = self.k if k is None else k
        return (self.hit + self.prior * k) / (self.opp + k)


@dataclass
class Stats:
    hands: int = 0
    vpip: Counter2 = field(default_factory=lambda: Counter2(0.70))
    pfr: Counter2 = field(default_factory=lambda: Counter2(0.55))
    open_raise: Counter2 = field(default_factory=lambda: Counter2(0.70))  # SB first in
    pre_fold_to_raise: Counter2 = field(default_factory=lambda: Counter2(0.40))
    three_bet: Counter2 = field(default_factory=lambda: Counter2(0.10))
    fold_to_3bet: Counter2 = field(default_factory=lambda: Counter2(0.55))
    fold_to_4bet: Counter2 = field(default_factory=lambda: Counter2(0.35))
    shove_rate: Counter2 = field(default_factory=lambda: Counter2(0.06))
    call_shove: Counter2 = field(default_factory=lambda: Counter2(0.40))
    bet: Counter2 = field(default_factory=lambda: Counter2(0.60, 8.0))  # bets when checked to
    fold_to_bet: Counter2 = field(default_factory=lambda: Counter2(0.38, 8.0))  # post flop only
    fold_to_bet_all: Counter2 = field(default_factory=lambda: Counter2(0.40))  # incl. preflop
    fold_to_raise_post: Counter2 = field(default_factory=lambda: Counter2(0.45, 8.0))
    raise_vs_bet: Counter2 = field(default_factory=lambda: Counter2(0.12))
    raise_any: Counter2 = field(default_factory=lambda: Counter2(0.30, 8.0))  # raises per decision
    river_bet_bluff: Counter2 = field(default_factory=lambda: Counter2(0.30))
    showdown_pcts: list = field(default_factory=list)

    def is_station(self) -> bool:
        """Calls too much: rarely folds to bets once enough is seen."""
        return self.fold_to_bet_all.opp >= 12 and self.fold_to_bet_all.rate() < 0.22

    def aggression_floor(self, scale: float = 1.0) -> float:
        """Range width implied by raising a lot in general (0 for a normal opponent)."""
        return max(0.0, (self.raise_any.rate() - 0.30) * scale)

    def is_maniac(self) -> bool:
        return self.hands >= 12 and self.bet.rate() > 0.7 and self.pfr.rate() > 0.7


class OpponentModel:
    def __init__(self):
        self.stats: dict[int, Stats] = defaultdict(Stats)
        self.start_stacks: dict[int, int] = {}

    def get(self, seat: int) -> Stats:
        return self.stats[seat]

    def observe_hand(self, result: dict, my_seat: int, start_stacks=None) -> None:
        """Fold one finished hand (the ``round_result.result`` payload) into the stats."""
        history = result.get("action_history") or []
        info = parse_history(history, start_stacks)
        last_raise_allin = False
        for ev in info.events:
            if ev.seat == my_seat:
                if ev.kind == "raise":
                    last_raise_allin = ev.allin
                continue
            s = self.stats[ev.seat]
            pre = ev.street == "preflop"
            s.raise_any.add(ev.kind == "raise")
            if pre:
                if ev.first_action and ev.raises_before == 0:
                    s.open_raise.add(ev.kind == "raise")
                if ev.facing and ev.raises_before == 1:
                    s.pre_fold_to_raise.add(ev.kind == "fold")
                    s.three_bet.add(ev.kind == "raise")
                if ev.facing and ev.raises_before == 2:
                    s.fold_to_3bet.add(ev.kind == "fold")
                if ev.facing and ev.raises_before >= 3:
                    s.fold_to_4bet.add(ev.kind == "fold")
                if ev.first_action:
                    s.shove_rate.add(ev.kind == "raise" and ev.allin)
                if ev.facing and last_raise_allin:
                    s.call_shove.add(ev.kind == "call")
            elif ev.facing:
                if ev.raises_before >= 2:  # a bet and a raise: facing pressure
                    s.fold_to_raise_post.add(ev.kind == "fold")
                else:
                    s.fold_to_bet.add(ev.kind == "fold")
                    s.raise_vs_bet.add(ev.kind == "raise")
            else:
                s.bet.add(ev.kind == "raise")
            if ev.facing:
                s.fold_to_bet_all.add(ev.kind == "fold")
            if ev.kind == "raise":
                last_raise_allin = ev.allin
        for seat in info.seats:
            if seat == my_seat:
                continue
            s = self.stats[seat]
            s.hands += 1
            acts = [e for e in info.events if e.seat == seat and e.street == "preflop"]
            s.vpip.add(any(e.kind in ("call", "raise") for e in acts))
            s.pfr.add(any(e.kind == "raise" for e in acts))
        for sd in result.get("showdown") or []:
            seat = sd.get("seat")
            if seat == my_seat or not sd.get("hole_cards"):
                continue
            try:
                a, b = (card_from_str(c) for c in sd["hole_cards"])
            except (KeyError, ValueError):
                continue
            pct = PCT[hand_class(a, b)]
            st = self.stats[seat]
            st.showdown_pcts.append(pct)
            river_bet = any(
                e.seat == seat and e.street == "river" and e.kind == "raise"
                and not e.facing for e in info.events
            )
            if river_bet:
                st.river_bet_bluff.add(pct < 0.35)
