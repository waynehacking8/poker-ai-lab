"""Vendored from Shaurya-S0603/PokerBots (ashwing_sdk) @ dc87080d1030ebf6df900eab2d8938acaf830878, patched for the offline arena (see PROVENANCE.md)."""

"""Hold'em policy with a precomputed heads-up response to limps."""

from bisect import bisect_right
from .data import BLIND_RAISE_BB

from .adaptive_policy import ashwing_adaptive
from .betting_line import preflop_strength


TITLE = "Ashwing Search"
DEPTHS = (25, 100)

def depth_bucket(view, cuts):
  depth = min(view.stack + view.current_bet, view.effective_raise_total) / view.big_blind
  if depth < 15 or depth > 125:
    return None
  return min(DEPTHS, key=lambda anchor: abs(depth - anchor)), bisect_right(cuts, preflop_strength(view.hole))


def limp_bucket(view):
  if (view.board or view.opponents != 1 or len(view.stacks) != 2 or view.late_position
      or view.table_bet != view.big_blind or not view.legal["check"] or len(view.betting_line) != 1):
    return None
  limp = view.betting_line[0]
  if not limp.opponent or limp.street != "preflop" or limp.action != "call":
    return None
  return depth_bucket(view, (.54, .66))

def blind_blueprint():
  return BLIND_RAISE_BB


def ashwing_search(view, rng, *, history=None, diagnostics=None):
  bucket = limp_bucket(view)
  if bucket is not None:
    depth, strength = bucket
    target = blind_blueprint()[str(depth)][strength] * view.big_blind
    maximum = min(view.effective_raise_total, view.legal["max_raise_total"])
    if view.legal["raise"] and view.legal["min_raise_total"] <= target <= maximum:
      if diagnostics is not None:
        diagnostics.update(method=TITLE, depth_bb=depth, strength_bucket=strength)
      return "raise", target
  return ashwing_adaptive(view, rng, history=history, diagnostics=diagnostics)
