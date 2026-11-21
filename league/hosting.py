"""Engine-side proxy for a candidate bot running in its own process (``bot_host.py``)."""

from __future__ import annotations

import os
import pickle
import select
import struct
import subprocess
import sys
import time
from types import SimpleNamespace

HOST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_host.py")


class HostError(Exception):
    pass


class RemoteBot:
    """Looks like an engine bot; every call is forwarded to the child process."""

    def __init__(self, root, module, cls, decision_timeout=10.0, hook_timeout=60.0):
        self.cmd = [sys.executable, "-I", HOST, str(root), module, cls]
        self.decision_timeout = decision_timeout
        self.hook_timeout = hook_timeout
        self.proc = None
        self.reset_stats()

    # -- process management ------------------------------------------------
    def _spawn(self):
        self.proc = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL)

    def close(self):
        if self.proc and self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait()
        self.proc = None

    def _recv(self, n, deadline):
        buf = b""
        fd = self.proc.stdout.fileno()
        while len(buf) < n:
            left = deadline - time.monotonic()
            if left <= 0 or not select.select([fd], [], [], left)[0]:
                raise HostError("timeout")
            chunk = os.read(fd, n - len(buf))
            if not chunk:
                raise HostError("host exited")
            buf += chunk
        return buf

    def _call(self, op, arg, timeout):
        if self.proc is None or self.proc.poll() is not None:
            raise HostError("host not running")
        data = pickle.dumps((op, arg), protocol=4)
        try:
            self.proc.stdin.write(struct.pack(">I", len(data)) + data)
            self.proc.stdin.flush()
            deadline = time.monotonic() + timeout
            (n,) = struct.unpack(">I", self._recv(4, deadline))
            status, value = pickle.loads(self._recv(n, deadline))
        except (HostError, BrokenPipeError, OSError):
            self.close()  # a hung or dead host is dropped; the next match respawns it
            raise HostError(f"{op} failed")
        if status != "ok":
            raise HostError(value)
        return value

    # -- per match ---------------------------------------------------------
    def reset_stats(self):
        self.errors = 0
        self.ms = []

    def new_match(self, seed):
        self.reset_stats()
        if self.proc is None or self.proc.poll() is not None:
            self._spawn()
        self._call("new", seed, self.hook_timeout)

    # -- engine bot interface ----------------------------------------------
    def decide(self, state):
        t0 = time.monotonic()
        try:
            kind, amount = self._call("decide", state, self.decision_timeout)
        except HostError:
            self.errors += 1
            raise
        finally:
            self.ms.append((time.monotonic() - t0) * 1000)
        return SimpleNamespace(action=kind, amount=amount)

    def _hook(self, name, msg):
        try:
            self._call(name, msg, self.hook_timeout)
        except HostError:
            self.errors += 1

    def on_match_start(self, msg):
        self._hook("on_match_start", msg)

    def on_round_start(self, msg):
        self._hook("on_round_start", msg)

    def on_round_result(self, msg):
        self._hook("on_round_result", msg)
