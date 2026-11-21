"""Local Chipzen-protocol server for one full heads-up match against a built-in opponent.

Runs holdem.engine on the server side and speaks the SDK wire protocol (authenticate, hello,
match_start, round_start, turn_request, round_result, match_end) to a bot container that
connects to ws://HOST:PORT/ws/match/<id>/bot. Seat 0 is the container, seat 1 the opponent.
Needs the repo root on PYTHONPATH (holdem, nlhe, rl) plus chipzen-bot and websockets.

    python deploy/localmatch.py --opp lag --seed 7 --port 8765 --out result.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "chipzen_bot")]

import websockets  # noqa: E402
from chipzen import Action  # noqa: E402

from holdem.engine import MatchConfig, play_match  # noqa: E402
from holdem.opponents import make_baseline  # noqa: E402

MID = "m_local_1"


class Remote:
    """Engine-side seat 0 that forwards every decision to the connected container."""

    def __init__(self, ws, loop):
        self.ws, self.loop = ws, loop
        self.seq = 2
        self.inbox = asyncio.Queue()
        self.lat = []  # round-trip ms per decision
        self.bad = []  # protocol problems

    def _frame(self, msg):
        self.seq += 1
        return json.dumps({"match_id": MID, "seq": self.seq,
                           "server_ts": "2026-11-22T00:00:00Z", **msg})

    async def send_async(self, msg):  # from the event loop thread
        await self.ws.send(self._frame(msg))

    def send(self, msg):  # from the engine thread
        asyncio.run_coroutine_threadsafe(self.ws.send(self._frame(msg)), self.loop).result(30)

    def on_match_start(self, m):
        pass  # sent by the handler before the engine starts

    def on_round_start(self, m):
        st = m["state"]
        self.send({"type": "round_start", "round_id": f"r_{st['hand_number']}",
                   "round_number": st["hand_number"], "state": {
                       "hand_number": st["hand_number"], "dealer_seat": st["dealer_seat"],
                       "your_hole_cards": st["your_hole_cards"], "stacks": st["stacks"],
                       "deck_commitment": ""}})

    def on_round_result(self, m):
        r = m["result"]
        self.send({"type": "round_result", "round_id": f"r_{r['hand_number']}",
                   "round_number": r["hand_number"], "result": r})

    def decide(self, s):
        rid = f"req_{time.monotonic_ns()}"
        self.send({"type": "turn_request", "seat": 0, "request_id": rid, "timeout_ms": 5000,
                   "valid_actions": list(s.valid_actions), "state": {
                       "hand_number": s.hand_number, "phase": s.phase,
                       "board": [str(c) for c in s.board],
                       "your_hole_cards": [str(c) for c in s.hole_cards], "pot": s.pot,
                       "your_stack": s.your_stack, "opponent_stacks": s.opponent_stacks,
                       "to_call": s.to_call, "min_raise": s.min_raise,
                       "max_raise": s.max_raise, "action_history": s.action_history}})
        t0 = time.perf_counter()
        while True:
            msg = asyncio.run_coroutine_threadsafe(self.inbox.get(), self.loop).result(30)
            if msg.get("type") == "turn_action" and msg.get("request_id") == rid:
                break
        self.lat.append((time.perf_counter() - t0) * 1000)
        a = msg["action"]
        if a not in s.valid_actions:
            self.bad.append(f"hand {s.hand_number}: {a} not in {s.valid_actions}")
        if a == "raise":
            amt = int(msg["params"]["amount"])
            if not (s.min_raise <= amt <= s.max_raise) and amt != s.max_raise:
                self.bad.append(f"hand {s.hand_number}: raise {amt} outside "
                                f"[{s.min_raise},{s.max_raise}]")
            return Action.raise_to(amt)
        return Action(action=a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opp", default="lag")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--out", default="result.json")
    args = ap.parse_args()
    done = threading.Event()

    async def handler(ws):
        loop = asyncio.get_running_loop()
        print("CONNECTED", flush=True)
        await ws.recv()  # authenticate
        await ws.send(json.dumps({"type": "hello", "match_id": MID, "seq": 1,
                                  "supported_versions": ["1.0"], "selected_version": "1.0",
                                  "game_type": "nlhe_hu", "capabilities": []}))
        await ws.recv()  # client hello
        remote = Remote(ws, loop)
        await remote.send_async({"type": "match_start", "seats": [
            {"seat": 0, "participant_id": "p0", "display_name": "bot", "is_self": True},
            {"seat": 1, "participant_id": "p1", "display_name": "opp", "is_self": False}],
            "game_config": {"variant": "nlhe", "starting_stack": 10000, "small_blind": 50,
                            "big_blind": 100, "ante": 0, "total_hands": 0},
            "turn_timeout_ms": 5000})

        async def reader():
            async for raw in ws:
                await remote.inbox.put(json.loads(raw))

        rd = asyncio.create_task(reader())
        res = await asyncio.to_thread(
            play_match, [remote, make_baseline(args.opp, args.seed)], args.seed, MatchConfig())
        await remote.send_async({"type": "match_end", "reason": "complete", "results": [
            {"seat": s, "participant_id": f"p{s}", "rank": 1 + (res.winner != s),
             "score": res.stacks[s]} for s in (0, 1)]})
        lat = sorted(remote.lat)
        out = {"opp": args.opp, "seed": args.seed, "hands": res.hands, "winner": res.winner,
               "stacks": res.stacks, "decisions": len(lat),
               "mean_ms": round(sum(lat) / len(lat), 2),
               "p99_ms": round(lat[int(len(lat) * .99)], 2), "max_ms": round(lat[-1], 2),
               "protocol_problems": remote.bad[:20], "protocol_problem_count": len(remote.bad)}
        json.dump(out, open(args.out, "w"))
        print(json.dumps(out), flush=True)
        await asyncio.sleep(1)
        await ws.close()
        rd.cancel()
        done.set()

    async def serve():
        async with websockets.serve(handler, "0.0.0.0", args.port):
            while not done.is_set():
                await asyncio.sleep(0.2)

    asyncio.run(serve())


if __name__ == "__main__":
    main()
