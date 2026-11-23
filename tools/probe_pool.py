"""Pooled exploitability probe (roadmap E3, S2b): wins, matches and Wilson 95% interval over the named
logs/exploit_probe/NAME.json files. The probes must have distinct eval seeds, or their matches would replay
the same deals; it exits 1 otherwise.

    python tools/probe_pool.py NAME [NAME ...]        e.g. s2_it001800_f2 s2_it001800_f3 s2_it001800_f4
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from holdem.arena import wilson  # noqa: E402

wins = matches = 0
seeds = []
for name in sys.argv[1:]:
    d = json.load(open(f"logs/exploit_probe/{name}.json"))
    e = d["eval"]
    print(f"{name}  train seed {d['train_seed']}  eval seed {d['eval_seed']}  {e['wins']}/{e['matches']}")
    wins, matches = wins + e["wins"], matches + e["matches"]
    seeds.append(d["eval_seed"])
if not seeds or len(set(seeds)) != len(seeds):
    sys.exit(f"eval seeds {seeds} are missing or repeat")
lo, hi = wilson(wins, matches)
print(json.dumps({"names": sys.argv[1:], "wins": wins, "matches": matches, "win_rate": round(wins / matches, 4),
                  "ci95": [round(lo, 3), round(hi, 3)]}))
