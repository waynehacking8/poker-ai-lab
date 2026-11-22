"""Glue: the Wolf JavaScript bot (vendor/wolf) behind a JSON-lines pipe to a locked-down node container.

Needs docker and the official ``node:22-alpine`` image. The container has no network, a read-only root, the
vendor/wolf folder mounted read-only, one cpu and 256 MB. It exits by itself when this process closes its stdin.
"""

import json
import os
import subprocess

from chipzen import Action, Bot

IMAGE = "node:22-alpine"
APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "wolf")


def _card(c):
    return {"rank": c.rank, "suit": c.suit}


class WolfBot(Bot):
    def __init__(self, variant="wolf", budget_ms=100):
        super().__init__()
        self.variant, self.budget_ms = variant, budget_ms
        self.proc = None
        self.seat = 0

    def _start(self):
        cmd = ["docker", "run", "-i", "--rm", "--network", "none", "--read-only", "--cap-drop", "ALL",
               "--security-opt", "no-new-privileges", "--pids-limit", "64", "--memory", "256m", "--cpus", "1",
               "--user", "65534:65534", "-v", f"{APP}:/app:ro", "-w", "/app", IMAGE,
               "node", "shim.mjs", self.variant, str(self.budget_ms)]
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

    def _send(self, obj):
        if self.proc is None or self.proc.poll() is not None:
            self._start()
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def close(self):
        if self.proc is not None:
            try:
                self.proc.stdin.close()
                self.proc.wait(timeout=5)
            except Exception:  # noqa: BLE001
                self.proc.kill()
            self.proc = None

    __del__ = close

    def on_match_start(self, info):
        self.close()  # a fresh tracker per match, like one real process per match
        self.seat = info.get("your_seat") or 0
        self._send({"ev": "match_start", "msg": {"game_config": info.get("game_config"), "num_players": 2}})

    def on_round_start(self, message):
        self._send({"ev": "round_start", "msg": {"your_seat": self.seat, "num_players": 2}})

    def on_round_result(self, message):
        self._send({"ev": "round_result", "msg": {}})

    def decide(self, state):
        self._send({"ev": "decide", "state": {
            "holeCards": [_card(c) for c in state.hole_cards], "board": [_card(c) for c in state.board],
            "toCall": state.to_call, "pot": state.pot, "yourStack": state.your_stack,
            "opponentStacks": list(state.opponent_stacks), "yourSeat": state.your_seat,
            "dealerSeat": state.dealer_seat, "validActions": list(state.valid_actions),
            "minRaise": state.min_raise, "maxRaise": state.max_raise, "phase": state.phase,
            "handNumber": state.hand_number, "roundId": state.round_id,
            "actionHistory": state.action_history}})
        reply = json.loads(self.proc.stdout.readline())
        if reply.get("error"):
            raise RuntimeError("wolf engine error: " + reply["error"][:200])
        if reply["action"] == "raise":
            return Action.raise_to(int(reply["amount"]))
        return {"fold": Action.fold, "call": Action.call, "check": Action.check}[reply["action"]]()
