"""Real-format evaluation of the deployable runtime through holdem/arena.py (SDK engine).

    python -m rl.eval_arena --model rl/models/best.npz --matches 400 --opp all --workers 4
    python -m rl.eval_arena --model ... --opp chipzen     # head-to-head vs the current bot
    python -m rl.eval_arena --model ... --opp model:rl/models/h4_it000300.npz   # vs another policy
    python -m rl.eval_arena --model ... --opp policy:rl/models/fb2_it000900.npz  # vs the bare policy (v3 as deployed)
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


def make_bare_policy(model, temperature, seed):
    """The policy without the all-in answer (rl/allin.py), as poker-ai-lab-v3 and older were deployed."""
    from rl.bot import RLBot
    return RLBot(seed=seed, model=model, temperature=temperature, allin=None)


def make_policy_opp(model, temperature, bare):
    """A policy opponent that holdem/arena.py seeds per match through set_seed, so runs repeat."""
    import numpy as np
    bot = (make_bare_policy if bare else make_hero)(model, temperature, None)
    bot.set_seed = lambda s: setattr(bot.policy, "rng", np.random.default_rng(s))
    return bot


def make_chipzen():
    from bot import HoldemBot
    return HoldemBot(seed=None)


def make_chipzen_hero(seed):
    from bot import HoldemBot
    return HoldemBot(seed=seed)


def make_bp100(seed=None):
    from bpopp.opponent import make_bp100 as factory
    return factory()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=None, help="hero policy (required unless --hero chipzen or bp100)")
    ap.add_argument("--matches", type=int, default=400)
    ap.add_argument("--opp", default="all",
                    help="baseline, chipzen, model:<npz>, policy:<npz> (no all-in answer), ext:<field bot>, comma separated")
    ap.add_argument("--hero", default="rl", choices=("rl", "chipzen", "bp100"),
                    help="chipzen: the heuristic HoldemBot plays hero; bp100: the isolated blueprint (smoke test)")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--legacy-rules", action="store_true", help="match the pre-fix SDK engine (600 cap, old short blind)")
    ap.add_argument("--rows", default=None, help="write every match as a JSON line, sorted by (opponent, seed, hero_seat)")
    args = ap.parse_args()
    if args.hero == "rl" and not args.model:
        ap.error("--model is required with --hero rl")
    if args.legacy_rules:
        from rl.features import set_rules
        set_rules(False)
    if args.hero == "chipzen":
        hero = make_chipzen_hero
    elif args.hero == "bp100":
        hero = make_bp100
    else:
        hero = functools.partial(make_hero, os.path.abspath(args.model), args.temperature)
    names = list(BASELINES) + ["chipzen"] if args.opp == "all" else args.opp.split(",")
    all_rows = []
    for name in names:
        if name.startswith("ext:"):
            from rl.field_bots import build
            opp = functools.partial(build, name)
        elif name.startswith("model:"):
            opp = functools.partial(make_policy_opp, os.path.abspath(name[6:]), 1.0, False)
        elif name.startswith("policy:"):
            opp = functools.partial(make_policy_opp, os.path.abspath(name[7:]), 1.0, True)
        else:
            opp = make_chipzen if name == "chipzen" else make_bp100 if name == "bp100" else name
        rows = []
        out = run_arena(opp, args.matches, args.seed, args.workers, hero_factory=hero, rows_out=rows)
        out["opponent"] = name
        print(json.dumps(out), flush=True)
        all_rows += [{"opponent": name, "seed": r["seed"], "hero_seat": r["hero_seat"], "hands": r["hands"],
                      "won": r["won"], "stacks": list(r["stacks"])} for r in rows]
    if args.rows:
        all_rows.sort(key=lambda r: (r["opponent"], r["seed"], r["hero_seat"]))
        with open(args.rows, "w") as f:
            for r in all_rows:
                f.write(json.dumps(r, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
