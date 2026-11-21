"""Chipzen candidate: the RL policy as a ``Bot`` subclass (league importable).

    from rl.bot import RLBot   # needs the repo root and chipzen_bot/ on sys.path
"""

from __future__ import annotations

import rl  # noqa: F401  (puts chipzen_bot on sys.path)
from chipzen import Action, Bot

from rl.features import Tracker, build
from rl.runtime import DEFAULT_MODEL, Policy


class RLBot(Bot):
    def __init__(self, seed=None, model=DEFAULT_MODEL, temperature=1.0):
        super().__init__()
        self.policy = Policy(model, temperature, seed)
        self.tracker = Tracker()

    def on_match_start(self, match_info):
        me = match_info.get("your_seat")
        if me is None:
            for seat in match_info.get("seats", ()) or ():
                if seat.get("is_self"):
                    me = seat["seat"]
        self.tracker = Tracker()
        self.tracker.me = int(me or 0)

    def on_round_result(self, message):
        r = message.get("result", {}) or {}
        hist = r.get("action_history")
        if hist:
            self.tracker.update(hist, (int(r.get("hand_number", 1)) - 1) % 2)

    def decide(self, state):
        try:
            self.tracker.me = state.your_seat
            f, mask, amt = build(state, self.tracker)
            a = self.policy.act(f, mask)
            if a == 0:
                return Action.fold()
            if a == 1:
                return Action.call() if state.to_call > 0 else Action.check()
            return Action.raise_to(int(amt[a]))
        except Exception:
            valid = list(state.valid_actions or ())
            if "check" in valid:
                return Action.check()
            return Action.fold() if "fold" in valid else Action.call()
