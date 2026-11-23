"""Name-seeded tracker counts (roadmap X2a): the profile table, the C setter, the training caller, the bot."""

from __future__ import annotations

import glob
import json
import os
import random
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("chipzen")

import rl  # noqa: F401,E402
from holdem.engine import MatchConfig, play_match  # noqa: E402
from holdem.opponents import make_baseline  # noqa: E402
from rl import fastenv  # noqa: E402
from rl.features import NST, Tracker, load_priors  # noqa: E402
from rl.oppmodel import FOLD, extract_replay  # noqa: E402
from tests.test_rl_env import KIND, Scripted, Stub, check_state, decks_for  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import tracker_profiles as tp  # noqa: E402

REPLAY_DIRS = [os.environ.get("CHIPZEN_REPLAYS", ""), str(ROOT / ".cache" / "chipzen-replays"),
               os.path.expanduser("~/poker-ai-lab-x1/data")]


def replay_dir():
    for d in REPLAY_DIRS:
        if d and glob.glob(os.path.join(d, "*.json")):
            return d
    return None


# ---- acceptance 1: the profile counts against an independent reading of the replays ----

def independent_counts(replays):
    """hands (st[10]), postflop decisions facing a bet (st[5]), folds among them (st[6]), preflop first actions
    (st[11]) per name, read with rl.oppmodel.extract_replay (its own public-state bookkeeping, chips added)."""
    out = {}

    def row(name):
        return out.setdefault(name, {10: 0, 5: 0, 6: 0, 11: 0})

    for r in replays:
        for h in r["hands"]:
            for s in h["starting_stacks"]:
                row(s["name"])[10] += 1
        seen = set()
        for hi, seat, name, state, cls in extract_replay(r):
            if state.street > 0 and state.to_call > 0:
                row(name)[5] += 1
                if cls == FOLD:
                    row(name)[6] += 1
            if state.street == 0 and (hi, seat) not in seen:
                seen.add((hi, seat))
                row(name)[11] += 1
    return out


@pytest.fixture(scope="module")
def replays():
    d = replay_dir()
    if d is None:
        pytest.skip("NOT TESTED: no chipzen replays (set CHIPZEN_REPLAYS)")
    return tp.load_replays(d)


def mismatches(counts, ind):
    bad = []
    for name, c in counts.items():
        for k in (10, 5, 6, 11):
            if c[k] != ind[name][k]:
                bad.append((name, k, c[k], ind[name][k]))
    return bad


def test_profile_counts_match_extract_replay(replays):
    stats = {}
    counts = tp.raw_counts(replays, stats)
    ind = independent_counts(replays)
    assert set(counts) == set(ind)
    assert mismatches(counts, ind) == []
    print(f"profile check: {len(replays)} replays, {len(counts)} names, "
          f"{sum(int(c[10]) for c in counts.values())} name-hands, all-ins for less read as calls: "
          f"{stats.get('allin_for_less', 0)}")


def test_chips_added_raise_amounts_fail_the_check(replays):
    """The mutation of acceptance 1: raise amounts left as chips added disagree with the independent count."""
    counts = tp.raw_counts(replays, raise_to=False)
    assert mismatches(counts, independent_counts(replays)) != []


def hand(actions):
    return {"streets": [{"street": st, "actions": [{"seat": s, "action_type": k, "amount": a} for s, k, a in acts]}
                        for st, acts in actions]}


def test_conversion_rule():
    h = hand([("preflop", [(0, "post_small_blind", 50), (1, "post_big_blind", 100), (0, "raise", 250),
                           (1, "raise", 100), (0, "call", 100)]),
              ("flop", [(1, "raise", 300), (0, "raise", 200)])])
    live = [(e["seat"], e["action"], e["amount"]) for e in tp.to_history(h)]
    # seat 0 has 50 in, adds 250: raise to 300; seat 1 adds 100 with 200 to call: all-in for less, a call
    assert live == [(0, "post_small_blind", 50), (1, "post_big_blind", 100), (0, "raise", 300), (1, "call", 100),
                    (0, "call", 100), (1, "raise", 300), (0, "call", 200)]
    stats = {}
    tp.to_history(h, stats)
    assert stats["allin_for_less"] == 2


def test_table_names_and_weight(replays, tmp_path):
    counts = tp.raw_counts(replays)
    table = tp.scaled(counts)
    assert table and all(abs(v[10] - tp.H0) < 1e-9 for v in table.values())
    assert set(table) == {n for n, c in counts.items() if c[10] >= tp.MIN_HANDS}
    tp.save(table, tmp_path / "t.npz")
    back = load_priors(str(tmp_path / "t.npz"))
    assert set(back) == set(table) and all(np.allclose(back[n], table[n]) for n in table)
    print(f"profile table: {len(counts)} names, {len(table)} with a profile")


# ---- acceptance 2: C counts against the Python Tracker, both seats, seeded by Pool.set_prior ----

class Seeded(Scripted):
    """Scripted actor whose trackers start from priors. `own` seats are updated by this actor (the C engine's
    stats of a seat hold the opponent counts of the other seat's observer, so the baseline seat gets a shadow)."""

    def __init__(self, seed, log, snaps, trs, own):
        super().__init__(seed, log)
        self.snaps, self.trs, self.own = snaps, trs, own

    def on_match_start(self, m):
        super().on_match_start(m)
        self.tr = self.trs[self.seat]

    def on_round_result(self, msg):
        r = msg["result"]
        for s in self.own:
            self.trs[s].update(r["action_history"], (r["hand_number"] - 1) % 2)

    def decide(self, state):
        act = super().decide(state)
        self.snaps.append((list(self.trs[0].st), list(self.trs[1].st), state.hand_number))
        return act


def make_trackers(priors):
    trs = []
    for s in (0, 1):
        t = Tracker(priors[s])
        t.me = s
        trs.append(t)
    return trs


def draw_priors(seed):
    """Seat priors: the four combinations of (none, random) cycle with the seed."""
    rng = np.random.default_rng(seed)
    return [None if not (seed >> s) & 1 else rng.uniform(0, 12, NST) for s in (0, 1)]


def play_compare(seed, priors, baseline, tally):
    """One match: the SDK engine plays and logs; the C engine replays it with set_prior, and every decision and
    the final counts must agree for both seats."""
    log, snaps = [], []
    trs = make_trackers(priors)
    pool = fastenv.Pool(1)
    stream = np.random.default_rng(seed).random(4000)
    if baseline is None:
        bots = [Seeded(seed * 2, log, snaps, trs, (0,)), Seeded(seed * 2 + 1, log, snaps, trs, (1,))]
        ctrl = [fastenv.EXT, fastenv.EXT]
    else:
        seat_b = seed % 2
        opp = make_baseline(baseline, seed)
        if hasattr(opp, "rng"):
            opp.rng = Stub(stream)
        bots = [None, None]
        bots[1 - seat_b] = Seeded(seed, log, snaps, trs, (0, 1))
        bots[seat_b] = opp
        ctrl = [fastenv.EXT, fastenv.EXT]
        ctrl[seat_b] = fastenv.BASELINE_IDS[baseline]
    res = play_match(bots, seed + 1, MatchConfig())
    pool.inject(0, decks=decks_for(seed + 1), urand=stream if baseline else None)
    for s in (0, 1):
        pool.set_prior(0, s, priors[s])
    pool.reset(0, 1, ctrl[0], ctrl[1], 0)
    assert len(snaps) == len(log)
    for (seat, kind, amount, st, f, mask, amt), (s0, s1, hand_no) in zip(log, snaps):
        check_state(pool, st, seat, mask, amt, f)  # includes f[46..55] read from the seeded counts
        for s, py in ((0, s0), (1, s1)):
            c = pool.stats(0, s)
            assert np.allclose(c, py, atol=1e-9, rtol=0), (seed, baseline, s, hand_no, c.tolist(), py)
            tally[s]["prior" if priors[s] is not None else "none"] += 1
            tally[s]["evidence"] += hand_no > 1
        assert pool.apply_raw(0, KIND[kind], amount) == 0
    assert pool.state(0)["done"] == 1 and [pool.state(0)["stacks0"], pool.state(0)["stacks1"]] == res.stacks
    for s in (0, 1):
        assert np.allclose(pool.stats(0, s), trs[s].st, atol=1e-9, rtol=0), (seed, baseline, s)


def new_tally():
    return [dict(prior=0, none=0, evidence=0) for _ in (0, 1)]


def test_parity_both_seats():
    tally = new_tally()
    for seed in range(16):
        play_compare(seed, draw_priors(seed), None, tally)
    for k, name in enumerate(("station", "maniac", "nit", "reference")):
        for seed in range(20 * k, 20 * k + 20):
            play_compare(seed + 100, draw_priors(seed), name, tally)
    for s in (0, 1):
        print(f"parity seat {s}: with prior {tally[s]['prior']}, without {tally[s]['none']}, "
              f"with in-match evidence {tally[s]['evidence']}")
        for branch, n in tally[s].items():
            assert n >= 500, f"NOT TESTED: seat {s} {branch} branch has {n} compared decisions"


def test_prior_hand_one_inside_the_reset():
    """A nit on the dealer seat folds hand 1 inside env_reset (hero acts later): the counts are prior plus hand 1."""
    rng = np.random.default_rng(7)
    found = 0
    for seed in range(1, 60):
        pool = fastenv.Pool(1)
        pri = [rng.uniform(0, 12, NST), rng.uniform(0, 12, NST)]
        pool.inject(0, decks=decks_for(seed))
        for s in (0, 1):
            pool.set_prior(0, s, pri[s])
        pool.reset(0, seed, fastenv.BASELINE_IDS["nit"], fastenv.EXT, 1)
        if pool.state(0)["hand_no"] != 2:
            continue
        found += 1
        # seat 1 (hero) never acted, so seat 0 folded its small blind: sb, bb, fold
        hist = [{"seat": 0, "action": "post_small_blind", "amount": 50, "phase": "preflop"},
                {"seat": 1, "action": "post_big_blind", "amount": 100, "phase": "preflop"},
                {"seat": 0, "action": "fold", "amount": 0, "phase": "preflop"}]
        for s in (0, 1):
            t = Tracker(pri[s])
            t.me = s
            t.update(hist, 0)
            assert np.allclose(pool.stats(0, s), t.st, atol=1e-9, rtol=0), (seed, s)
            assert pool.stats(0, s)[10] == pri[s][10] + 1
    assert found >= 5, f"only {found} decks fold hand 1 inside the reset"
    print(f"hand 1 inside the reset: {found} decks checked")


def test_set_prior_is_used_once_and_default_is_zero():
    pool = fastenv.Pool(1)
    pool.set_prior(0, 0, np.arange(NST, dtype=float))
    pool.reset(0, 1, fastenv.EXT, fastenv.EXT, 0)
    assert pool.stats(0, 0).tolist() == list(range(NST)) and not pool.stats(0, 1).any()
    pool.reset(0, 2, fastenv.EXT, fastenv.EXT, 0)  # the next reset starts from nothing
    assert not pool.stats(0, 0).any()
    pool.set_prior(0, 1, np.ones(NST))
    pool.set_prior(0, 1, None)
    pool.reset(0, 3, fastenv.EXT, fastenv.EXT, 0)
    assert not pool.stats(0, 1).any()


# ---- acceptance 2b: the training caller ----

class FakePool:
    def __init__(self):
        self.calls = []

    def set_prior(self, i, seat, counts):
        self.calls.append(("prior", i, seat, None if counts is None else list(counts)))

    def reset(self, i, seed, c0, c1, hero):
        self.calls.append(("reset", i, hero))


def test_collector_seeds_hero_seat_for_named_bot_clones(monkeypatch):
    pytest.importorskip("torch")
    from rl import train
    monkeypatch.setitem(train.CLONE_IDS, "bot:Known", 200)
    monkeypatch.setitem(train.CLONE_IDS, "bot:Other", 201)
    monkeypatch.setitem(train.CLONE_IDS, "arch:3", 202)
    prof = [float(k) for k in range(NST)]
    weights = {"bot:Known": 1.0, "bot:Other": 1.0, "arch:3": 1.0, "station": 1.0, "snap:1": 1.0}
    seen = set()
    for flagged in (True, False):
        col = train.Collector(1, 5, {"Known": prof} if flagged else None)
        col.pool = FakePool()
        for _ in range(200):
            col.pool.calls.clear()
            col._new_match(0, weights, 1)
            key = col.opp[0]
            hero = col.pool.calls[-1][2]
            priors = {c[2]: c[3] for c in col.pool.calls if c[0] == "prior"}
            if not flagged:
                assert priors == {}, "no flag, no set_prior call"
            elif key == "bot:Known":
                assert priors == {hero: prof, 1 - hero: None}
                seen.add(key)
            else:
                assert priors == {0: None, 1: None}
                seen.add(key)
    assert seen == {"bot:Known", "bot:Other", "arch:3", "station", "snap:1"}


# ---- acceptance 4: the deployed bot and the shipped files ----

def seats(opp_name):
    return [{"seat": 0, "display_name": "Me", "is_self": True}, {"seat": 1, "display_name": opp_name, "is_self": False}]


def test_bot_seeds_from_known_name_only():
    from rl.bot import RLBot
    from rl.features import PRIOR_PATH
    assert RLBot(seed=1).priors == {}, "seeding is opt-in: the default bot plays as before"
    assert len(RLBot(seed=1, priors=PRIOR_PATH).priors) >= 40
    bot = RLBot(seed=1)
    prior = [float(k + 1) for k in range(NST)]
    bot.priors = {"Known": prior}
    bot.on_match_start({"your_seat": 0, "seats": seats("Known")})
    assert bot.tracker.st == prior and bot.tracker.me == 0
    bot.tracker.st[0] += 1
    assert bot.priors["Known"] == prior, "the table must not be mutated by a match"
    bot.on_match_start({"your_seat": 0, "seats": seats("Stranger")})
    assert bot.tracker.st == [0.0] * NST
    bot.on_match_start({"your_seat": 1, "seats": [{"seat": 0, "display_name": "Known", "is_self": False},
                                                  {"seat": 1, "display_name": "Me", "is_self": True}]})
    assert bot.tracker.st == prior and bot.tracker.me == 1
    bot.on_match_start({"your_seat": 0, "seats": [{"seat": 0, "is_self": True}, {"seat": 1, "is_self": False}]})
    assert bot.tracker.st == [0.0] * NST


def test_shipped_table_and_packaging():
    table = load_priors()
    assert len(table) >= 40 and all(len(v) == NST and abs(v[10] - 20.0) < 1e-6 for v in table.values())
    for f in ("deploy/Dockerfile", "deploy/hf_package.sh"):
        assert "tracker_prior.npz" in (ROOT / f).read_text(encoding="utf-8"), f
    assert (ROOT / "rl" / "models" / "tracker_prior.npz").exists()
