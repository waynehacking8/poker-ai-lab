import numpy as np

from rl.oppmodel import (ALLIN, CALL, FOLD, RAISE_OVER, RAISE_POT, HandTracker, OppModel, PublicState,
                         classify, save_params)


def _tiny_params(names=("alice",)):
    rng = np.random.default_rng(0)
    d = 14
    edges = [0.5]
    nb = 4 * (len(edges) + 2)
    counts = np.zeros((len(names), nb, 5), np.float32)
    counts[0, 3] = [1, 1, 8, 0, 0]
    return {"W1": rng.normal(size=(8, d)).astype(np.float32), "b1": rng.normal(size=8).astype(np.float32),
            "W2": rng.normal(size=(5, 8)).astype(np.float32), "b2": rng.normal(size=5).astype(np.float32),
            "edges": np.array(edges, np.float32), "names": np.array(list(names)), "counts": counts,
            "scalars": np.array([0, 5.0, 1.0, 2.0])}


STATE = PublicState(1, 1, 0.0, 200.0, 9900.0, 9900.0, 100.0, 1, 0)


def test_class_mapping_on_hand_built_hands():
    tr = HandTracker({0: 10000, 1: 10000}, 100)
    tr.apply(0, "post_small_blind", 50)
    tr.apply(1, "post_big_blind", 100)
    # SB completes: call for 50
    assert tr.apply(0, "call", 50) == CALL
    # BB checks
    assert tr.apply(1, "check", 0) == CALL
    tr.new_street(1)  # pot 200
    # small bet: 100 into 200
    assert tr.apply(1, "raise", 100) == RAISE_POT
    # 450 more facing 100 = 350 over the call, pot after the call is 400: still up to the pot
    assert tr.apply(0, "raise", 450) == RAISE_POT
    # facing 450 (pot 750): raise to 2000, 1550 over the call vs pot after call 1200: above the pot
    assert tr.apply(1, "raise", 2000 - 100) == RAISE_OVER
    # fold
    assert tr.apply(0, "fold", 0) == FOLD


def test_all_in_and_call_all_in():
    # the whole stack beyond the call is all-in
    assert classify("raise", 9950, 0, 150, 9950) == ALLIN
    # calling for the whole stack is still a call
    assert classify("call", 1155, 1155, 3000, 1155) == CALL
    # a raise that only matches the bet is a call
    assert classify("raise", 500, 500, 1000, 500) == CALL
    # a raise just under the stack is not all-in
    assert classify("raise", 5000, 0, 400, 9950) == RAISE_OVER


def test_tracker_state():
    tr = HandTracker({0: 10000, 1: 10000}, 100)
    tr.apply(0, "post_small_blind", 50)
    tr.apply(1, "post_big_blind", 100)
    s = tr.state(0)
    assert s.is_sb == 1 and s.to_call == 50 and s.pot == 150 and s.rem == 9950 and s.last_cls == 5
    tr.apply(0, "raise", 250)
    s = tr.state(1)
    assert s.is_sb == 0 and s.to_call == 200 and s.last_cls == RAISE_POT and s.n_raises == 1


def test_observing_moves_prediction_toward_the_action():
    m = OppModel(_tiny_params())
    for name in ("alice", "stranger"):
        m.start_match(name)
        before = m.predict(STATE)
        assert abs(before.sum() - 1.0) < 1e-6
        for _ in range(6):
            m.observe(STATE, ALLIN)
        after = m.predict(STATE)
        assert after[ALLIN] > before[ALLIN]
        m.start_match(name)  # the in-match state resets
        assert np.allclose(m.predict(STATE), before)


def test_name_profile_matters():
    m = OppModel(_tiny_params())
    m.start_match("stranger")
    unseen = m.predict(STATE)
    m.start_match("alice")
    known = m.predict(STATE)
    assert known[RAISE_POT] > unseen[RAISE_POT]  # alice mostly raised here


def test_npz_round_trip(tmp_path):
    p = _tiny_params()
    f = tmp_path / "m.npz"
    save_params(f, p)
    a, b = OppModel(p), OppModel.load(f)
    for name in ("alice", "bob"):
        a.start_match(name)
        b.start_match(name)
        for cls in (1, 2, 1, 4):
            assert np.allclose(a.predict(STATE), b.predict(STATE))
            a.observe(STATE, cls)
            b.observe(STATE, cls)
