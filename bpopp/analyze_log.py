"""Summarise bp_*.jsonl decision logs written by bpopp.opponent (BP_LOG=dir).

    python -m bpopp.analyze_log DIR [--show N]
"""

from __future__ import annotations

import argparse
import glob
import json
import statistics
from collections import Counter


def load(path):
    rows = []
    for f in sorted(glob.glob(f"{path}/bp_*.jsonl")):
        for line in open(f):
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * p))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--show", type=int, default=0)
    a = ap.parse_args()
    rows = load(a.dir)
    n = len(rows)
    srv = [r["ms"] for r in rows]
    rtt = [r["rtt_ms"] for r in rows]
    print(f"decisions {n}")
    print(f"server ms  mean {statistics.mean(srv):.3f}  p99 {pct(srv, .99):.3f}  max {max(srv):.3f}")
    print(f"round trip mean {statistics.mean(rtt):.3f}  p99 {pct(rtt, .99):.3f}  max {max(rtt):.3f}")
    print("fallbacks", sum(r["fallback"] for r in rows), "truncated", sum(r["truncated"] for r in rows),
          "off_tree", sum(r["off_tree"] for r in rows), "clamped", sum(r["clamped"] for r in rows),
          "repaired", sum(bool(r.get("repaired")) for r in rows))
    # action mix by street
    for ph in ("preflop", "flop", "turn", "river"):
        c = Counter(r.get("final") or r["act"]["action"] for r in rows if r["phase"] == ph)
        print(ph, dict(c))
    # preflop spots at the 50/100 level (hands 1-20), our seat's first action
    def first_pre(r):
        return [e for e in r["hist"] if e["phase"] == "preflop" and not e["action"].startswith("post")]
    sb_open, bb_def = Counter(), Counter()
    for r in rows:
        if r["phase"] != "preflop" or r["hand"] > 20:
            continue
        h = first_pre(r)
        if not h and r["to_call"] > 0:
            sb_open[r.get("final") or r["act"]["action"]] += 1  # button, first to act
        elif len(h) == 1 and h[0]["action"] == "raise":
            bb_def[r.get("final") or r["act"]["action"]] += 1  # facing the first raise
    print("SB first action (hands<=20):", dict(sb_open))
    print("facing the first raise (hands<=20):", dict(bb_def))
    if a.show:
        for r in rows[: a.show]:
            print(json.dumps({k: r[k] for k in ("hand", "phase", "hole", "board", "pot", "to_call", "stack", "act")}))


if __name__ == "__main__":
    main()
