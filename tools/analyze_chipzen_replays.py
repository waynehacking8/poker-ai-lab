"""Summarize Chipzen heads-up NLHE replays: match format and field tendencies.

Input: a directory of JSON files, each {"match": <GET /api/matches/{id}>,
"replay": <GET /api/matches/{id}/replay>}. The replays are fetched from the
Chipzen site by hand (see tools/README.md); this script only reads them.

Usage:
    python tools/analyze_chipzen_replays.py .cache/chipzen-replays
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

PREFLOP_AGGR = {"raise", "all_in", "bet"}


def load(directory: Path) -> list[dict]:
    out = []
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("match", {}).get("game_type") != "poker":
            continue
        out.append(data)
    return out


def main(directory: str) -> None:
    matches = load(Path(directory))
    lengths, blind_steps, end_kinds = [], Counter(), Counter()
    match_types = Counter()
    per_bot = defaultdict(Counter)
    record = defaultdict(lambda: [0, 0])
    first_level_change = []

    for data in matches:
        match, replay = data["match"], data["replay"]
        match_types[(match.get("match_type"), match.get("rated"))] += 1
        hands = replay["hands"]
        lengths.append(len(hands))
        for res in replay["metadata"].get("final_result", []):
            record[res["name"]][0 if res["net_chips"] > 0 else 1] += 1

        prev_bb = None
        for hand in hands:
            bb = hand["blinds"]["big_blind"]
            if prev_bb is not None and bb != prev_bb:
                blind_steps[(hand["hand_number"], prev_bb, bb)] += 1
                if prev_bb == hands[0]["blinds"]["big_blind"]:
                    first_level_change.append(hand["hand_number"])
            prev_bb = bb

            streets = hand["streets"]
            pre = streets[0]["actions"] if streets else []
            names = {a["seat"]: a["player"] for a in pre}
            sb_seat = next((a["seat"] for a in pre if a["action_type"] == "post_small_blind"), None)
            stacks = {s["seat"]: s["starting_stack"] for s in hand["starting_stacks"]}
            eff_bb = min(stacks.values()) / bb if bb else 0

            # Per-bot preflop stats on the player's first voluntary decision.
            seen = set()
            raised_before = False
            for a in pre:
                kind = a["action_type"]
                if kind.startswith("post_"):
                    continue
                name = a["player"]
                if a["seat"] not in seen:
                    seen.add(a["seat"])
                    pos = "sb" if a["seat"] == sb_seat else "bb"
                    c = per_bot[name]
                    c[f"{pos}_decisions"] += 1
                    if kind in ("call", "raise", "all_in"):
                        c[f"{pos}_vpip"] += 1
                    if kind in PREFLOP_AGGR:
                        c[f"{pos}_pfr"] += 1
                    if kind == "all_in" or (kind == "raise" and a["amount"] >= 0.9 * stacks[a["seat"]]):
                        c[f"{pos}_shove"] += 1
                    if raised_before:
                        c["faced_raise"] += 1
                        if kind == "fold":
                            c["fold_to_raise"] += 1
                if kind in PREFLOP_AGGR:
                    raised_before = True

            last = hand["streets"][-1]["street"] if hand["streets"] else "preflop"
            if hand is hands[-1]:
                showdown = bool(hand.get("showdown"))
                end_kinds[(last, "showdown" if showdown else "fold", round(eff_bb) // 10 * 10)] += 1
            for seat, name in names.items():
                per_bot[name]["hands"] += 1
                if hand.get("showdown"):
                    per_bot[name]["showdowns"] += 1
            per_bot["_all"]["ended_" + last] += 1

    print(f"matches: {len(matches)}  types: {dict(match_types)}")
    if lengths:
        q = statistics.quantiles(lengths, n=4) if len(lengths) > 1 else [lengths[0]] * 3
        print(f"hands per match: mean {statistics.mean(lengths):.1f} median {statistics.median(lengths)}"
              f" q1 {q[0]} q3 {q[2]} max {max(lengths)}")
    print("blind steps (hand, old bb, new bb):", sorted(blind_steps.items())[:12])
    print("first blind change at hand:", Counter(first_level_change))
    print("final hand (street, how, eff stack bb bucket):", end_kinds.most_common(12))
    print("streets where hands ended:", {k: v for k, v in per_bot["_all"].items()})
    print()
    print(f"{'bot':24} {'W-L':>6} {'hands':>5} {'SBvpip':>6} {'SBpfr':>6} {'SBshv':>6}"
          f" {'BBvpip':>6} {'BBpfr':>6} {'f2r':>5} {'sd%':>5}")
    ranked = sorted(record, key=lambda n: (-record[n][0], record[n][1]))
    for name in ranked:
        c = per_bot[name]

        def pct(num, den):
            return f"{100 * c[num] / c[den]:.0f}" if c[den] else "-"

        print(f"{name[:24]:24} {record[name][0]:>2}-{record[name][1]:<3} {c['hands']:>5}"
              f" {pct('sb_vpip', 'sb_decisions'):>6} {pct('sb_pfr', 'sb_decisions'):>6}"
              f" {pct('sb_shove', 'sb_decisions'):>6} {pct('bb_vpip', 'bb_decisions'):>6}"
              f" {pct('bb_pfr', 'bb_decisions'):>6} {pct('fold_to_raise', 'faced_raise'):>5}"
              f" {pct('showdowns', 'hands'):>5}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".cache/chipzen-replays")
