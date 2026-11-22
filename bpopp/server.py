"""Blueprint opponent server. Runs ONLY inside the isolated container.

Reads one JSON object per line on stdin, writes one per line on stdout.

    {"op": "match_start", "game_config": {...}, "seat": 0}   -> {"ok": true}
    {"op": "decide", "state": {...wire turn state...}}        -> {"action": ..., "params": {...}, "info": {...}}

It drives the third-party BlueprintSeat (decision path only: depth ladder, hand
replay, policy lookup, wire pricing) exactly as the live seat does with
``--no-resolver``. It never opens a socket, never imports the Chipzen SDK, the
cloud task code, or the Postgres record source (the run record comes from the
run's own manifest, ``RunTracker.load(dir, None)``).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

# Protocol channel is the real stdout; anything the library prints goes to stderr.
_OUT = os.fdopen(os.dup(1), "w", buffering=1)
sys.stdout = sys.stderr

import logging  # noqa: E402

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

RUNS = Path(os.environ.get("BP_RUNS_DIR", "/work/data/runs"))
RUN = os.environ["BP_RUN"]
AT = int(os.environ["BP_AT"]) if os.environ.get("BP_AT") else None
THRESHOLD = float(os.environ.get("BP_THRESHOLD", "0.35"))


def load_blueprint():
    from src.engine.solver.policy.threshold import apply_policy_threshold
    from src.pipeline.services.scoring._shared import build_blueprint_for
    from src.pipeline.training.run_tracker import RunTracker

    run_dir = RUNS / RUN
    metadata = RunTracker.load(run_dir, None).metadata
    solver, storage, _ = build_blueprint_for(
        run_dir, metadata, abstraction_hash=metadata.card_abstraction_hash,
        at_iteration=AT, play_only=True)
    changed, trained = apply_policy_threshold(storage, solver.tree, THRESHOLD)
    print(f"threshold {THRESHOLD}: {changed}/{trained} rows changed", file=sys.stderr)
    return solver


def send(obj):
    _OUT.write(json.dumps(obj) + "\n")


def main():
    t0 = time.perf_counter()
    from src.interfaces.chipzen.seat import BlueprintSeat

    blueprint = load_blueprint()
    game = blueprint.config.game
    send({"ready": True, "load_s": round(time.perf_counter() - t0, 1),
          "stack": game.starting_stack, "sb": game.small_blind, "bb": game.big_blind,
          "threshold": THRESHOLD})
    seat = None
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        msg = json.loads(line)
        op = msg["op"]
        if op == "match_start":
            seat = BlueprintSeat.for_match(
                blueprint, {"game_config": msg["game_config"]}, seat=int(msg["seat"]),
                use_resolver=False)
            send({"ok": True, "depth_matches": seat.scale.depth_matches,
                  "factor": seat.scale.factor})
        elif op == "decide":
            t = seat.tally
            before = (t.fallbacks, t.truncated, t.off_tree)
            started = time.perf_counter()
            frame = seat.decide_frame(msg["state"])
            ms = (time.perf_counter() - started) * 1000
            frame["info"] = {
                "ms": round(ms, 3),
                "fallback": t.fallbacks - before[0],
                "truncated": t.truncated - before[1],
                "off_tree": t.off_tree - before[2],
                "rung_bb": seat.scale.our_depth,
            }
            send(frame)
        elif op == "quit":
            break


if __name__ == "__main__":
    main()
