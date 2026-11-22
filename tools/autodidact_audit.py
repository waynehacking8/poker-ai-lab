"""Tally which branch of the vendored autodidact engine decided each action (a swallowed error shows as fallback_error_path)."""

import collections
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rl  # noqa: E402,F401
from holdem.engine import MatchConfig, play_match  # noqa: E402
from holdem.opponents import make_baseline  # noqa: E402
from rl.field_bots.autodidact import AutodidactBot  # noqa: E402
from rl.field_bots.vendor.autodidact import chipzen_adapter as A  # noqa: E402

tally = collections.Counter()


class Audit(AutodidactBot):
    def decide(self, state):
        action, dec = A.decide_chipzen(state, self.game_config, self.match_id)
        tally[(dec.get("_debug") or {}).get("decided_by")] += 1
        return action


for opp in ("random", "lag", "station"):
    for seat in (0, 1):
        bots = [None, None]
        bots[seat], bots[1 - seat] = Audit(eq_trials=200, ranged_trials=150), make_baseline(opp, 5)
        play_match(bots, 77 + seat, MatchConfig(), strict=False)
for k, v in tally.most_common():
    print(v, k)
