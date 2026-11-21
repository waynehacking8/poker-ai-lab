"""Chipzen entry point for the poker-ai-lab Hold'em bot.

The strategy lives in the ``nlhe`` package next to this file; this module is the
thin SDK adapter (hooks, safe fallback) and the ``main()`` the Dockerfile runs.
The platform injects CHIPZEN_WS_URL and CHIPZEN_TOKEN (or CHIPZEN_TICKET) at launch.
"""

from __future__ import annotations

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chipzen import Action, Bot, GameState  # noqa: E402
from chipzen.client import run_bot  # noqa: E402

from nlhe.strategy import Brain  # noqa: E402


class HoldemBot(Bot):
    """Stack-depth aware NLHE bot with an online opponent model."""

    def __init__(self, seed=None) -> None:
        super().__init__()
        self.brain = Brain(seed)

    # lifecycle hooks -------------------------------------------------
    def on_match_start(self, match_info: dict) -> None:
        for seat in match_info.get("seats", ()) or ():
            if seat.get("is_self"):
                self.brain.my_seat = int(seat["seat"])
        if match_info.get("your_seat") is not None:
            self.brain.my_seat = int(match_info["your_seat"])

    def on_round_start(self, message: dict) -> None:
        state = message.get("state", {}) or {}
        self.brain.set_start_stacks(state.get("stacks"))

    def on_round_result(self, message: dict) -> None:
        self.brain.observe_result(message.get("result", {}) or {})

    # decision --------------------------------------------------------
    def decide(self, state: GameState) -> Action:
        try:
            return self.brain.decide(state)
        except Exception as exc:  # never forfeit a hand to a crash
            print(f"decide failed: {exc!r}", file=sys.stderr)
            return _safe_action(state)


def _safe_action(state: GameState) -> Action:
    valid = list(state.valid_actions or ())
    if "check" in valid:
        return Action.check()
    if "call" in valid and state.to_call <= max(state.pot // 6, 1):
        return Action.call()
    if "fold" in valid:
        return Action.fold()
    return Action.check()


def main() -> None:
    url = os.environ.get("CHIPZEN_WS_URL") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not url:
        print("error: CHIPZEN_WS_URL not set and no URL passed on the command line",
              file=sys.stderr)
        sys.exit(1)
    asyncio.run(
        run_bot(
            url,
            HoldemBot(),
            token=os.environ.get("CHIPZEN_TOKEN"),
            ticket=os.environ.get("CHIPZEN_TICKET"),
        )
    )


if __name__ == "__main__":
    main()
