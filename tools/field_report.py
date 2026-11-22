"""Render the field-bot results table (markdown) from the measurement and smoke outputs.

    python tools/field_report.py RESULTS_DIR SMOKE.jsonl [SMOKE2.jsonl ...] > table.md

RESULTS_DIR holds <bot>.a.json (our policy as hero) and <bot>.b.json (heuristic bot as hero), one JSON line each,
as printed by rl.eval_arena. Rates are the hero win rate; the interval is Wilson 95%.
"""

import json
import os
import sys


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.loads(f.readline())
    except (OSError, ValueError):
        return None


def cell(d):
    if not d:
        return "n/a"
    return f"{100 * d['win_rate']:.1f}% [{100 * d['ci95'][0]:.1f}, {100 * d['ci95'][1]:.1f}]"


def main(argv):
    res, smokes = argv[0], argv[1:]
    smoke = {}
    for p in smokes:
        with open(p, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                smoke[d["bot"]] = d
    print("| bot | h4-300 beats it (400 matches) | heuristic bot beats it | smoke p99 ms | smoke max ms | exceptions | illegal |")
    print("|---|---|---|---|---|---|---|")
    for bot, d in smoke.items():
        a, b = load(os.path.join(res, bot + ".a.json")), load(os.path.join(res, bot + ".b.json"))
        runs = [d[k] for k in ("random", "lag") if k in d]
        p99 = max((r["ms_p99"] for r in runs), default=d["probe"]["ms_p99"])
        mx = max((r["ms_max"] for r in runs), default=d["probe"]["ms_max"])
        exc = sum(r["exceptions"] for r in runs)
        ill = sum(r["illegal"] for r in runs)
        print(f"| ext:{bot} | {cell(a)} | {cell(b)} | {p99:.0f} | {mx:.0f} | {exc} | {ill} |")


if __name__ == "__main__":
    main(sys.argv[1:])
