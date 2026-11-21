"""Chipzen server rules in the C engine: short big blind and the extended blind schedule."""

from __future__ import annotations

import numpy as np

import rl  # noqa: F401
from rl import fastenv
from rl.features import bb_for


def test_schedule_extends_to_1000():
    assert [bb_for(h) for h in (1, 20, 21, 100, 101, 120, 121, 140, 141, 400)] == \
        [100, 100, 150, 400, 600, 600, 800, 800, 1000, 1000]
    pool = fastenv.Pool(1)
    for hand, bb in ((1, 100), (21, 150), (101, 600), (121, 800), (141, 1000), (300, 1000)):
        d = np.tile(np.arange(52, dtype=np.int32), (hand, 1))
        pool.inject(0, decks=d)
        pool.reset_stacks(0, 1, fastenv.EXT, fastenv.EXT + 1, 0, 10000, 10000)
        # play hands as fold-outs until the wanted hand number is reached
        while pool.state(0)["hand_no"] < hand:
            s = pool.state(0)
            pool.apply_raw(0, 0 if s["to_call"] > 0 else 1, 0)
            if pool.state(0)["done"]:
                break
        assert pool.state(0)["bb"] == bb


def test_big_blind_all_in_at_or_below_small_blind_skips_action():
    pool = fastenv.Pool(1)
    pool.reset_stacks(0, 3, fastenv.EXT, fastenv.EXT + 1, 0, 10000, 30)  # seat 0 is the button
    s = pool.state(0)
    assert s["done"] == 1 or s["hand_no"] > 1 or s["nh"] == 0
    total = 10030
    assert s["stacks0"] + s["stacks1"] == total
    assert (s["stacks0"], s["stacks1"]) in ((10000 - 30, 60), (10030, 0), (10000, 30))


def test_short_big_blind_above_small_blind_prompts_call_difference():
    pool = fastenv.Pool(1)
    pool.reset_stacks(0, 3, fastenv.EXT, fastenv.EXT + 1, 0, 10000, 80)
    s = pool.state(0)
    assert s["hand_no"] == 1 and s["done"] == 0
    assert s["to_call"] == 30
