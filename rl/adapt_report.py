"""Adaptation curves from eval_fast logs: python -m rl.adapt_report adaptive.jsonl nohist.jsonl"""
import json
import sys

import numpy as np


def group(name):
    return "baselines" if not (name.startswith("arch:") or name.startswith("bot:")) else \
        "archetype clones" if name.startswith("arch:") else "held-out per-bot clones"


def load(path):
    out = {}
    for line in open(path):
        d = json.loads(line)
        out.setdefault(group(d["opponent"]), []).append(d)
    return out


def mean_opt(vals):
    v = [x for x in vals if x is not None]
    return round(float(np.mean(v)), 3) if v else None


labels = ["adaptive (opponent statistics as input)", "no history (same training, statistics hidden)"]
for path, label in zip(sys.argv[1:], labels):
    data = load(path)
    print(f"\n### {label}\n")
    print("| opponent group | match win rate | bb/hand, hands 1-5 | 6-10 | 11-20 | 21-40 | 41+ | chip leader after 5 | 10 | 20 | 40 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for g, rows in data.items():
        wr = round(float(np.mean([r["win_rate"] for r in rows])), 3)
        cur = [r["bb_per_hand_by_5_hands"] for r in rows]
        b = lambda ix: mean_opt([np.mean([c[i] for i in ix if c[i] is not None] or [np.nan]) for c in cur])  # noqa: E731
        lead = [mean_opt([r["chip_leader_after"][h] for r in rows]) for h in ("5", "10", "20", "40")]
        print(f"| {g} | {wr} | {b([0])} | {b([1])} | {b([2, 3])} | {b([4, 5, 6, 7])} | {b([8, 9, 10, 11])} | "
              + " | ".join(str(x) for x in lead) + " |")
