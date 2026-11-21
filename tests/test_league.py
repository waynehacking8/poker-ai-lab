"""League harness tests: replay parsing, context parity, de-censoring, hosting, determinism."""

from __future__ import annotations

import numpy as np
import pytest

from holdem.engine import MatchConfig, play_match
from league import run as league_run
from league.clone import CloneBot, load_model
from league.context import F_OPEN, RAISE, ctx_of_state, event_of_act
from league.fit import LEGAL, SeatRec, fit_table, smooth
from league.hosting import RemoteBot
from league.replays import check_conservation, parse_hand
from league.report import stratified
from league.stats import rec_from_engine
from league.strength import PRE_BUCKETS, NCOMBO


def _hand(streets, stacks_after, payouts):
    return {
        "hand_number": 1, "community_cards": ["2c", "7d", "9h"],
        "starting_stacks": [{"seat": 0, "name": "a", "starting_stack": 10000},
                            {"seat": 1, "name": "b", "starting_stack": 10000}],
        "blinds": {"small_blind": 50, "big_blind": 100},
        "streets": streets, "showdown": None, "payouts": payouts,
        "stacks_after": stacks_after, "result": {"winner_seats": [0]},
    }


def test_replay_raise_amount_is_chips_added():
    pre = [{"seat": 0, "action_type": "post_small_blind", "amount": 50},
           {"seat": 1, "action_type": "post_big_blind", "amount": 100},
           {"seat": 0, "action_type": "raise", "amount": 150},  # raise-to 200
           {"seat": 1, "action_type": "fold", "amount": 0}]
    h = parse_hand("m", _hand([{"street": "preflop", "actions": pre}],
                              {"0": 10100, "1": 9900}, {"0": 300}))
    assert check_conservation([h]) == (2, 2)
    assert h.acts[0].raise_total == 200 and h.acts[0].put == 200
    ctx, code, frac = event_of_act(h.acts[0], True)
    assert ctx[2] == F_OPEN and code == RAISE
    assert frac == pytest.approx(100 / 200)  # raise over the call, in pots after calling


def test_smooth_keeps_illegal_actions_at_zero_and_rows_normalised():
    C = np.zeros((4, 2, 10, 4, 8, 5))
    C[0, 1, 0, 2, 3, 3] = 5
    th = smooth(C)
    assert np.allclose(th.sum(-1), 1.0)
    assert th[0, 1, 0, 2, 3, 1] == 0 and th[0, 1, 0, 2, 3, 0] > 0  # facing: no check
    assert np.all(th[:, :, 1, :, :, 0] == 0)  # limp option: no fold


def test_em_decensors_folded_hands():
    rng = np.random.default_rng(0)
    ctx = (0, 1, F_OPEN, 3)
    recs = []
    for _ in range(1500):
        combo = int(rng.integers(NCOMBO))
        weak = PRE_BUCKETS[combo] < 4
        code = 0 if weak else 3  # fold weak, raise strong
        known = None if code == 0 else combo  # folded cards are never shown
        recs.append(SeatRec([(ctx, code, 0.7)], known, [PRE_BUCKETS]))
    naive, _ = fit_table(recs, naive=True)
    em, _ = fit_table(recs, iters=8)
    weak_fold = lambda t: t[ctx][:4, 0].mean()  # noqa: E731
    assert weak_fold(naive) <= 0.3 and weak_fold(em) > 0.6
    assert em[ctx][7, 3] > 0.9


def test_context_parity_between_state_and_replay_record():
    """The context the clone computes live equals the context the fitter counts."""
    seen = []

    class Spy(CloneBot):
        def decide(self, state):
            seen.append((state.your_seat, ctx_of_state(state)[0]))
            return super().decide(state)

    hands = []
    for seed in range(5, 12):
        bots = [Spy("arch:0", seed), Spy("arch:2", seed + 50)]
        play_match(bots, seed, MatchConfig(), strict=False,
                   on_hand=lambda h, r: hands.append(rec_from_engine(
                       ["a", "b"], r, h.dealer, h.bb, h.start_stacks)))
    replay = [(a.seat, event_of_act(a, a.seat == h.button)[0]) for h in hands for a in h.acts]
    assert seen == replay and len(seen) > 10


def test_clone_actions_are_legal_in_strict_engine():
    for seed in range(5):
        bots = [CloneBot("arch:3", seed), CloneBot("bot:Kimiko", seed + 100)]
        play_match(bots, seed, MatchConfig(), strict=True)


def test_clone_match_is_deterministic():
    def one():
        return play_match([CloneBot("arch:1", 3), CloneBot("arch:4", 4)], 9, MatchConfig(),
                          strict=False)
    a, b = one(), one()
    assert (a.hands, a.stacks) == (b.hands, b.stacks)


def test_field_archetype_prefix_matches_weights():
    w = load_model().meta["weights_rated"]
    draws = [league_run.field_arch(p, w) for p in range(300)]
    for k, wk in enumerate(w):
        assert abs(draws.count(k) / 300 - wk) < 0.03


def test_remote_candidate_plays_and_counts_errors(tmp_path):
    (tmp_path / "dummybot.py").write_text(
        "from chipzen import Action, Bot\n"
        "class Dummy(Bot):\n"
        "    def __init__(self, seed=None):\n"
        "        super().__init__()\n"
        "    def decide(self, state):\n"
        "        return Action.call() if 'call' in state.valid_actions else Action.check()\n")
    remote = RemoteBot(tmp_path, "dummybot", "Dummy", decision_timeout=5)
    try:
        remote.new_match(1)
        res = play_match([remote, CloneBot("arch:0", 1)], 2, MatchConfig(), strict=False)
        assert res.hands >= 1 and remote.errors == 0 and remote.ms
    finally:
        remote.close()


def test_run_task_is_deterministic_and_pairs_swap_seats():
    league_run._CFG.update({"candidates": {}, "model": str(league_run.Path(league_run.__file__)
                            .parent / "data" / "clones.npz"), "decision_timeout": 5})
    t = {"a": "base:nit", "opp": "arch:2", "oppkey": "field", "pair": 3, "seat": 0,
         "key": "k"}
    r1, r2 = league_run.run_task(t), league_run.run_task(dict(t))
    assert {k: r1[k] for k in ("hands", "a_win", "a_chips")} == \
           {k: r2[k] for k in ("hands", "a_win", "a_chips")}
    r3 = league_run.run_task({**t, "seat": 1})
    assert r3["seed"] == r1["seed"]  # duplicate deal: same seed, swapped seats


def test_stratified_estimate_uses_weights():
    rows = ([{"opp": "arch:0", "pair": p, "a_win": 1.0} for p in range(10)]
            + [{"opp": "arch:1", "pair": p, "a_win": 0.0} for p in range(10)])
    est, lo, hi, n = stratified(rows, [0.75, 0.25])
    assert est == pytest.approx(0.75) and lo == hi == pytest.approx(0.75) and n == 20


def test_legal_matrix_shape():
    assert LEGAL.shape == (10, 5)
