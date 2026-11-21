"""Child process that hosts one candidate bot behind a pipe.

Candidates from different branches share module names (``nlhe``, ``bot``), so each one
lives in its own interpreter and the league talks to it through length-prefixed pickles.
Usage (started by ``league.hosting``): ``python bot_host.py <root> <module> <class>``.
Only the standard library and the chipzen SDK are imported before the candidate's root
is put on ``sys.path``.
"""

import importlib
import inspect
import os
import pickle
import struct
import sys


def _read(fd):
    head = b""
    while len(head) < 4:
        chunk = os.read(fd, 4 - len(head))
        if not chunk:
            return None
        head += chunk
    (n,) = struct.unpack(">I", head)
    buf = b""
    while len(buf) < n:
        chunk = os.read(fd, n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return pickle.loads(buf)


def _write(fd, obj):
    data = pickle.dumps(obj, protocol=4)
    os.write(fd, struct.pack(">I", len(data)) + data)


def main():
    root, module, cls_name = sys.argv[1:4]
    out_fd = os.dup(1)
    os.dup2(2, 1)  # candidate prints go to stderr, never into the protocol stream
    sys.path.insert(0, os.path.abspath(root))
    os.chdir(os.path.abspath(root))
    cls = getattr(importlib.import_module(module), cls_name)
    bot = None
    while True:
        msg = _read(0)
        if msg is None:
            return
        op, arg = msg
        try:
            if op == "new":
                params = inspect.signature(cls).parameters
                bot = cls(seed=arg) if "seed" in params else cls()
                _write(out_fd, ("ok", None))
            elif op == "decide":
                a = bot.decide(arg)
                _write(out_fd, ("ok", (a.action, a.amount)))
            else:  # hook
                fn = getattr(bot, op, None)
                if fn:
                    fn(arg)
                _write(out_fd, ("ok", None))
        except Exception as exc:  # report, keep serving
            _write(out_fd, ("err", repr(exc)))


if __name__ == "__main__":
    main()
