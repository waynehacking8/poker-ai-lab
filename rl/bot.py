"""Chipzen candidate: the RL policy as a ``Bot`` subclass (league importable).

    from rl.bot import RLBot   # needs the repo root and chipzen_bot/ on sys.path
"""

from __future__ import annotations

import os

import rl  # noqa: F401  (puts chipzen_bot on sys.path)
from chipzen import Action, Bot

from rl.allin import DEFAULT_TABLE, AllInAnswer
from rl.features import Tracker, build
from rl.runtime import DEFAULT_MODEL, Policy


class RLBot(Bot):
    def __init__(self, seed=None, model=DEFAULT_MODEL, temperature=1.0, allin=DEFAULT_TABLE):
        super().__init__()
        self.policy = Policy(model, temperature, seed)
        self.tracker = Tracker()
        # RL_ALLIN=off turns the all-in answer off for A/B runs
        self.allin = AllInAnswer(allin) if allin and os.environ.get("RL_ALLIN") != "off" else None

    def on_match_start(self, match_info):
        me = match_info.get("your_seat")
        if me is None:
            for seat in match_info.get("seats", ()) or ():
                if seat.get("is_self"):
                    me = seat["seat"]
        self.tracker = Tracker()
        self.tracker.me = int(me or 0)
        if self.allin:
            stack = (match_info.get("game_config") or {}).get("starting_stack") or self.allin.total // 2
            self.allin.reset(self.tracker.me, stack)

    def on_round_result(self, message):
        self.tracker.round_result(message.get("result", {}) or {})
        if self.allin:
            try:
                self.allin.round_result(message.get("result", {}) or {})
            except Exception:
                pass

    def on_round_start(self, message):
        self.tracker.round_start(message)

    def decide(self, state):
        try:
            self.tracker.me = state.your_seat
            f, mask, amt = build(state, self.tracker)
            a = self.policy.act(f, mask)
            if a == 0:
                if self.allin and self.allin.should_call(state):
                    return Action.call()
                return Action.fold()
            if self.allin and self.allin.should_fold_first(state):
                return Action.fold()
            if a == 1:
                return Action.call() if state.to_call > 0 else Action.check()
            return Action.raise_to(int(amt[a]))
        except Exception:
            valid = list(state.valid_actions or ())
            if "check" in valid:
                return Action.check()
            return Action.fold() if "fold" in valid else Action.call()
