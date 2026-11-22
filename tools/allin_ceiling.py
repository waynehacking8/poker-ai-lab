"""Ceiling check: fb2-900 plus the all-in answer when the shove range (any two) is known from hand 1.

    python tools/allin_ceiling.py oracle jam     # known range from hand 1 (65.5% against jam, seed 3)
    python tools/allin_ceiling.py fast jam       # the online estimate with PRIOR_N 1
"""
import functools, json, sys
sys.path.insert(0, ".")
import rl  # noqa
import rl.allin as A
from holdem.arena import run_arena
from rl.eval_arena import make_hero

mode = sys.argv[1]
if mode == "oracle":
    A.AllInAnswer.width = lambda self: 1.0
    A.PRIOR_W, A.PRIOR_N = 1.0, 1e9
elif mode == "fast":
    A.PRIOR_N = 1.0
hero = functools.partial(make_hero, "rl/models/fb2_it000900.npz", 1.0)
for opp in sys.argv[2].split(","):
    r = run_arena(opp, 400, seed=3, workers=8, hero_factory=hero)
    print(mode, opp, f"{100*r['win_rate']:.1f}%", r["ci95"], "hands", r["mean_hands_all"])
