"""Vendored from Shaurya-S0603/PokerBots (ashwing_sdk) @ dc87080d1030ebf6df900eab2d8938acaf830878, patched for the offline arena (see PROVENANCE.md)."""

COMPETITION_PROFILE = {
  "call_cushion": 0.045,
  "value_edge": 0.19,
  "position_bonus": 0.14,
  "pot_fraction": 0.72,
  "river_call_margin": 0.015,
  "shallow_open_bonus": 0.03
}

RIVER_GATE = {
  "min_evidence": 3,
  "min_call_rate": 0.67,
  "smaller_bucket_discount": 0.8
}

BLIND_RAISE_BB = {
  "25": [
    0,
    0,
    3
  ],
  "100": [
    0,
    4,
    4
  ]
}
