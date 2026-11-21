"""Every real Chipzen NLHE hand in .cache/chipzen-replays must replay exactly through the engine."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("chipzen")

ROOT = Path(__file__).resolve().parent.parent
REPLAYS = ROOT / ".cache" / "chipzen-replays"

if not REPLAYS.is_dir() or not any(REPLAYS.glob("*.json")):
    pytest.skip("no replays in .cache/chipzen-replays", allow_module_level=True)

sys.path.insert(0, str(ROOT / "tools"))
import replay_conformance  # noqa: E402


@pytest.mark.slow
def test_all_real_hands_replay_through_the_engine():
    res, bad = replay_conformance.run(REPLAYS)
    assert res["ok"] > 1000, dict(res)
    assert not bad, f"{len(bad)} hands differ, first: {bad[:5]}"
