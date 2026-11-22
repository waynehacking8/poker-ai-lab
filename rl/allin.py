"""Answering a preflop all-in from solved match-value tables (roadmap S0, the all-in fix).

fb2-900 folded almost every hand that beats a random hand against a bot that shoves every hand, and lost
about half of those matches. Facing a preflop all-in, this module estimates the width w of the opponent's
shoving range and compares two match values from the tables of tools/allin_tables.py:

    call = e_w * V_w(h + 1, s0 + m) + (1 - e_w) * V_w(h + 1, s0 - m)
    fold = V_w(h + 1, s_now)

s0 is our stack at the start of the hand, m the effective stack, s_now our stack after folding, e_w the
equity of our hand class against the top w of hands. The width is the larger of two estimates: the
opponent's preflop shove frequency, shrunk toward a tight prior, and the weakest shoving hand it has shown.

The tables model an opponent that shoves every hand, so they decide only against near-certain shovers
(frequency at least MIN_FREQ, reached after three shoves in three chances). Against anyone else the tables
would undervalue our edge in the hands the opponent does not shove; there the policy decides alone (it
already beats a bot that shoves any two half the time 85%). Facing an all-in the module only turns a policy
fold into a call. Its one added fold is the small blind's first decision, where limping and folding to the
shove loses a big blind instead of a small one.
"""

from __future__ import annotations

import os

import numpy as np

from nlhe import preflop as pf
from nlhe.cards import card_from_str, cards_from, hand_class

DEFAULT_TABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "allin_v.npz")
PRIOR_W, PRIOR_N = 0.05, 1.0
MIN_FREQ = 0.7  # three shoves in three chances: 0.76
_BLINDS = ("post_small_blind", "post_big_blind")


class AllInAnswer:
    def __init__(self, path=DEFAULT_TABLE):
        z = np.load(path)
        self.v, self.e = z["v"], z["e"]
        self.widths = [float(x) for x in z["widths"]]
        self.unit, self.total, self.max_hands = int(z["unit"]), int(z["total"]), int(z["max_hands"])
        self.reset(0, self.total // 2)

    def reset(self, me, stack):
        self.me = int(me)
        self.start = [int(stack), int(stack)]
        self.chances = self.shoves = 0
        self.weakest = None  # lowest strength percentile among the shoving hands it has shown

    def round_result(self, result):
        me, opp = self.me, 1 - self.me
        left, bet, chance, shoved = list(self.start), [0, 0], False, False
        for ev in result.get("action_history") or ():
            if ev["phase"] != "preflop":
                break
            s, k, a = ev["seat"], ev["action"], int(ev.get("amount") or 0)
            if s == opp and k not in _BLINDS and left[me] > 0:
                chance = True
            if k in _BLINDS or k == "call":
                left[s] -= a
                bet[s] += a
            elif k == "raise":
                left[s] -= a - bet[s]
                bet[s] = a
            if s == opp and (k == "all_in" or (k == "raise" and left[opp] <= 0)):
                shoved = True
        self.chances += chance
        self.shoves += shoved
        if shoved:
            for sd in result.get("showdown") or ():
                if sd.get("seat") == opp and len(sd.get("hole_cards") or ()) == 2:
                    p = pf.PCT[hand_class(*[card_from_str(c) for c in sd["hole_cards"]])]
                    self.weakest = p if self.weakest is None else min(self.weakest, p)
        # the next hand starts from these end-of-hand stacks (live round_start stacks are post-blind)
        st = result.get("stacks")
        if st and len(st) == 2:
            self.start = [int(x) for x in st]

    def freq(self):
        return (self.shoves + PRIOR_W * PRIOR_N) / (self.chances + PRIOR_N)

    def width(self):
        w = self.freq()
        if self.weakest is not None:
            w = max(w, 1.0 - self.weakest)
        return min(w, 1.0)

    def _value(self, k, h, s):
        x = min(max(s / self.unit, 0.0), self.v.shape[2] - 1.0)
        i = min(int(x), self.v.shape[2] - 2)
        t = x - i
        return (1 - t) * self.v[k, h, i] + t * self.v[k, h, i + 1]

    def _bracket(self, w):
        ws = self.widths
        if w <= ws[0]:
            return [(0, 1.0)]
        for k in range(1, len(ws)):
            if w <= ws[k]:
                t = (w - ws[k - 1]) / (ws[k] - ws[k - 1])
                return [(k - 1, 1.0 - t), (k, t)]
        return [(len(ws) - 1, 1.0)]

    def _ctx(self, state):
        """(width, s0, effective stack, scale, hand class, next hand) for a table decision, or None."""
        q = self.freq()
        if q < MIN_FREQ:
            return None  # not a near-certain shover: the policy decides
        w = self.width()
        me = state.your_seat
        s0, o0 = self.start[me], self.start[1 - me]
        if s0 <= 0 or o0 <= 0:
            return None
        cls = hand_class(*cards_from(state.hole_cards))
        return w, s0, min(s0, o0), self.total / (s0 + o0), cls, min(state.hand_number + 1, self.max_hands + 1)

    def _values(self, ctx, stacks):
        """Match value of getting all in, and of carrying each listed stack into the next hand."""
        w, s0, m, scale, cls, h = ctx
        call, vals = 0.0, [0.0] * len(stacks)
        for k, t in self._bracket(w):
            e = float(self.e[k, cls])
            call += t * (e * self._value(k, h, (s0 + m) * scale) + (1 - e) * self._value(k, h, (s0 - m) * scale))
            for i, x in enumerate(stacks):
                vals[i] += t * self._value(k, h, x * scale)
        return call, vals

    def should_call(self, state):
        """True when calling a preflop all-in beats folding under the estimated shoving range."""
        if state.phase != "preflop" or state.to_call <= 0 or "call" not in (state.valid_actions or ()):
            return False
        opp_left = state.opponent_stacks[0] if state.opponent_stacks else 0
        if opp_left > 0 and state.to_call < state.your_stack:
            return False  # a raise that is not all-in stays with the policy
        ctx = self._ctx(state)
        if ctx is None:
            return False
        call, (fold,) = self._values(ctx, [state.your_stack])
        return call > fold

    def should_fold_first(self, state):
        """The small blind's first decision against a near-certain shover: True when folding the small blind
        now beats entering the pot, which the shover answers with an all-in that we then call or fold.
        Without it the policy limps, gets shoved on and folds a big blind."""
        if state.phase != "preflop" or state.to_call <= 0 or "fold" not in (state.valid_actions or ()):
            return False
        if any(ev["action"] not in _BLINDS for ev in state.action_history if ev["phase"] == "preflop"):
            return False
        ctx = self._ctx(state)
        if ctx is None:
            return False
        q, s0 = self.freq(), ctx[1]
        bb = s0 - state.your_stack + state.to_call
        call, (fold_now, fold_later, no_shove) = self._values(ctx, [state.your_stack, s0 - bb, s0])
        return fold_now > q * max(call, fold_later) + (1 - q) * no_shove
