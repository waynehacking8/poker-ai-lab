"""Run rl.eval_arena with the all-in answer instrumented: every True from should_call or
should_fold_first is appended to $ALLIN_COUNT_LOG as one JSON line (pid, kind, hand, hole).
Workers fork from this process, so the patch carries into them. Usage:
    ALLIN_COUNT_LOG=path python tools/allin_count.py <rl.eval_arena args>
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())

import rl.allin as allin  # noqa: E402

LOG = os.environ["ALLIN_COUNT_LOG"]


def wrap(name):
    orig = getattr(allin.AllInAnswer, name)

    def f(self, state):
        r = orig(self, state)
        if r:
            with open(LOG, "a") as fh:
                fh.write(json.dumps({"pid": os.getpid(), "kind": name, "hand": state.hand_number,
                                     "hole": [str(c) for c in state.hole_cards], "freq": round(self.freq(), 3)}) + "\n")
        return r
    setattr(allin.AllInAnswer, name, f)


wrap("should_call")
wrap("should_fold_first")

import rl.eval_arena as ea  # noqa: E402

sys.argv = ["rl.eval_arena"] + sys.argv[1:]
ea.main()
