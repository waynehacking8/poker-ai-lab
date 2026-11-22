"""Arena opponent that plays the third-party poker-solver blueprint (100 bb, MIT).

The blueprint runs only inside a Docker container on the box (see
docs/blueprint_opponent.md); this class talks JSON lines to it over
``docker run -i``. One container per arena worker process, started on first use
and reused for every match that process plays (loading the blueprint takes about
a minute).

Environment:
  BP_IMAGE   image tag (default bpopp:v010)
  BP_DATA    host path of the extracted blueprint tar, mounted read only
  BP_RUN     run directory name under data/runs
  BP_AT      checkpoint iteration (default 65000)
  BP_THRESHOLD  policy threshold (default 0.35, the live seat's deep value)
  BP_LOG     directory for per decision jsonl logs (optional)
  BP_CPUS    cpus per container (default 2)
"""

from __future__ import annotations

import atexit
import json
import os
import subprocess
import time
import uuid

from chipzen import Action

_RUN = "run-pcs-production_opens-to12k-d100-145201-6584"


def docker_cmd(name: str) -> list[str]:
    image = os.environ.get("BP_IMAGE", "bpopp:v010")
    data = os.environ["BP_DATA"]
    return [
        "docker", "run", "-i", "--rm", "--name", name,
        "--network", "none",
        "--read-only", "--tmpfs", "/tmp:rw,exec,size=2g",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "--pids-limit", "256", "--memory", os.environ.get("BP_MEM", "10g"),
        "--cpus", os.environ.get("BP_CPUS", "2"),
        "--user", "10001:10001",
        "-v", f"{data}/data:/work/data:ro",
        "-e", f"BP_RUN={os.environ.get('BP_RUN', _RUN)}",
        "-e", f"BP_AT={os.environ.get('BP_AT', '65000')}",
        "-e", f"BP_THRESHOLD={os.environ.get('BP_THRESHOLD', '0.35')}",
        "-e", "OMP_NUM_THREADS=1", "-e", "NUMBA_NUM_THREADS=1",
        image,
    ]


class _Container:
    def __init__(self):
        self.name = f"bpopp-{os.getpid()}-{uuid.uuid4().hex[:6]}"
        log_dir = os.environ.get("BP_LOG")
        self.log = None
        self.err = subprocess.DEVNULL
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            self.log = open(os.path.join(log_dir, f"bp_{os.getpid()}.jsonl"), "a", buffering=1)
            self.err = open(os.path.join(log_dir, f"bp_{os.getpid()}.err"), "a")
        self.proc = subprocess.Popen(
            docker_cmd(self.name), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=self.err, text=True, bufsize=1)
        ready = self._read()
        if not ready.get("ready"):
            raise RuntimeError(f"blueprint container did not start: {ready}")
        self.ready = ready
        atexit.register(self.close)

    def _read(self):
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("blueprint container closed its stdout")
        return json.loads(line)

    def call(self, msg):
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()
        return self._read()

    def close(self):
        try:
            if self.proc.poll() is None:
                self.proc.stdin.close()
                self.proc.wait(timeout=10)
        except Exception:
            try:
                subprocess.run(["docker", "kill", self.name], capture_output=True, timeout=20)
            except Exception:
                pass


_CONTAINER: _Container | None = None
_PID = None


def container() -> _Container:
    global _CONTAINER, _PID
    if _CONTAINER is None or _PID != os.getpid():
        _CONTAINER, _PID = _Container(), os.getpid()
    return _CONTAINER


def wire_state(state) -> dict:
    """SDK GameState into the wire dict the blueprint seat parses."""
    return {
        "hand_number": state.hand_number, "phase": state.phase,
        "board": [str(c) for c in state.board],
        "your_hole_cards": [str(c) for c in state.hole_cards],
        "pot": state.pot, "your_stack": state.your_stack,
        "opponent_stacks": list(state.opponent_stacks),
        "to_call": state.to_call, "min_raise": state.min_raise, "max_raise": state.max_raise,
        "action_history": list(state.action_history),
        "valid_actions": list(state.valid_actions or ()),
    }


class BlueprintOpponent:
    def __init__(self):
        self.box = container()
        self.seat = 0

    def on_match_start(self, match_info):
        self.seat = int(match_info["your_seat"])
        cfg = dict(match_info["game_config"])
        cfg.setdefault("variant", "nlhe")
        self.box.call({"op": "match_start", "game_config": cfg, "seat": self.seat})

    def decide(self, state):
        t0 = time.perf_counter()
        frame = self.box.call({"op": "decide", "state": wire_state(state), "seat": state.your_seat})
        rtt = (time.perf_counter() - t0) * 1000
        info = frame.pop("info", {})
        kind = frame["action"]
        clamped = False
        if kind == "raise":
            # Their _clamp_raise returns max(min_raise, min(total, max_raise)), which
            # exceeds max_raise when min_raise > max_raise (only the shove is legal).
            # The live server would reject that frame; the arena engine would raise.
            # Clamp into the legal range (the shove) and count it.
            lo = min(state.min_raise, state.max_raise)
            want = int(frame["params"]["amount"])
            amount = max(lo, min(want, state.max_raise))
            clamped = amount != want
            frame["params"]["amount"] = amount
        valid = list(state.valid_actions or ())
        repaired = None
        if kind not in valid:
            # The adapter snaps a raise that rounds to no increment in its coarse chips
            # (e.g. a short all-in below the min raise) to a CALL, so it answers as if
            # it faced a check and returns "check" where the real price is positive.
            # The live server would reject it. Repair to the nearest legal action
            # and count it.
            repaired = kind
            if kind in ("check", "raise") and "call" in valid:
                kind = "call"
            elif kind in ("call", "raise") and "check" in valid:
                kind = "check"
            else:
                kind = "fold" if "fold" in valid else valid[0]
        if self.box.log:
            self.box.log.write(json.dumps({
                "hand": state.hand_number, "phase": state.phase, "seat": state.your_seat,
                "hole": [str(c) for c in state.hole_cards], "board": [str(c) for c in state.board],
                "pot": state.pot, "stack": state.your_stack, "opp": list(state.opponent_stacks),
                "to_call": state.to_call, "min": state.min_raise, "max": state.max_raise,
                "valid": list(state.valid_actions or ()), "hist": list(state.action_history),
                "clamped": clamped, "repaired": repaired, "final": kind, "act": frame, "rtt_ms": round(rtt, 3), **info}) + "\n")
        if kind == "fold":
            return Action.fold()
        if kind == "check":
            return Action.check()
        if kind == "call":
            return Action.call()
        return Action.raise_to(int(frame["params"]["amount"]))


def make_bp100():
    return BlueprintOpponent()
