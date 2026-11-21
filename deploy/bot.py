"""Chipzen entry point for the RL policy bot (numpy-only, weights rl/models/weights.npz set at build time).

The platform injects CHIPZEN_WS_URL and CHIPZEN_TOKEN (or CHIPZEN_TICKET) at launch.
"""

from __future__ import annotations

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chipzen.client import run_bot  # noqa: E402

from rl.bot import RLBot  # noqa: E402

WEIGHTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rl", "models", "weights.npz")


def main() -> None:
    url = os.environ.get("CHIPZEN_WS_URL") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not url:
        print("error: CHIPZEN_WS_URL not set and no URL passed on the command line",
              file=sys.stderr)
        sys.exit(1)
    asyncio.run(
        run_bot(
            url,
            RLBot(model=WEIGHTS),
            token=os.environ.get("CHIPZEN_TOKEN"),
            ticket=os.environ.get("CHIPZEN_TICKET"),
        )
    )


if __name__ == "__main__":
    main()
