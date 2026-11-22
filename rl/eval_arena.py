"""Real-format evaluation of the deployable runtime through holdem/arena.py (SDK engine).

    python -m rl.eval_arena --model rl/models/best.npz --matches 400 --opp all --workers 4
    python -m rl.eval_arena --model ... --opp chipzen     # head-to-head vs the current bot
    python -m rl.eval_arena --model ... --opp model:rl/models/h4_it000300.npz   # vs another policy
"""

from __future__ import annotations

import argparse
import functools
import json
import os

import rl  # noqa: F401
from holdem.arena import run_arena
from holdem.opponents import BASELINES


def make_hero(model, temperature, seed):
    from rl.bot import RLBot
    return RLBot(seed=seed, model=model, temperature=temperature)


def make_chipzen():
    from bot import HoldemBot
    return HoldemBot(seed=None)


def make_chipzen_hero(seed):
    from bot import HoldemBot
    return HoldemBot(seed=seed)


def make_bp100():
    from bpopp.opponent import make_bp100 as factory
    return factory()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=None, help="hero policy (not needed with --hero chipzen)")
    ap.add_argument("--hero", default="rl", choices=["rl", "chipzen"], help="chipzen = the old heuristic bot.HoldemBot")
    ap.add_argument("--matches", type=int, default=400)
    ap.add_argument("--opp", default="all")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--legacy-rules", action="store_true", help="match the pre-fix SDK engine (600 cap, old short blind)")
    args = ap.parse_args()
    if args.legacy_rules:
        from rl.features import set_rules
        set_rules(False)
    hero = functools.partial(make_hero, os.path.abspath(args.model), args.temperature)
    names = list(BASELINES) + ["chipzen"] if args.opp == "all" else args.opp.split(",")
    for name in names:
        if name.startswith("model:"):
            opp = functools.partial(make_hero, os.path.abspath(name[6:]), 1.0, None)
        else:
            opp = make_chipzen if name == "chipzen" else make_bp100 if name == "bp100" else name
        out = run_arena(opp, args.matches, args.seed, args.workers, hero_factory=hero)
        out["opponent"] = name
        print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
