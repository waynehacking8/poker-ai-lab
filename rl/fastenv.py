"""ctypes wrapper around rl/fastenv.c (built on first import with gcc)."""

from __future__ import annotations

import ctypes as C
import os
import subprocess

import numpy as np

from nlhe import preflop as pf
from rl.features import D_OBS, NACT, NST

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "fastenv.c")
LIB = os.path.join(HERE, "libfastenv.so")

BASELINE_IDS = {"station": 0, "maniac": 1, "nit": 2, "random": 3, "reference": 4,
                "lag": 5, "station_raiser": 6}
EXT = 100  # controller id of external slot k is EXT + k


def _build():
    if not os.path.exists(LIB) or os.path.getmtime(LIB) < os.path.getmtime(SRC):
        subprocess.check_call(["gcc", "-O2", "-Wall", "-shared", "-fPIC", "-o", LIB, SRC, "-lm"])


_build()
_lib = C.CDLL(LIB)
_i = C.POINTER(C.c_int)
_f = C.POINTER(C.c_float)
_d = C.POINTER(C.c_double)
_u8 = C.POINTER(C.c_ubyte)
_lib.fe_set_rules.argtypes = [C.c_int]
_lib.env_reset_stacks.argtypes = [C.c_void_p, C.c_int, C.c_uint64, C.c_int, C.c_int, C.c_int, C.c_int, C.c_int, C.c_int]
_lib.pool_new.restype = C.c_void_p
_lib.pool_new.argtypes = [C.c_int]
_lib.pool_free.argtypes = [C.c_void_p]
_lib.fe_set_tables.argtypes = [_d, _d]
_lib.fe_evaluate.argtypes = [_i, C.c_int]
_lib.env_reset.argtypes = [C.c_void_p, C.c_int, C.c_uint64, C.c_int, C.c_int, C.c_int, C.c_int, C.c_int]
_lib.env_set_injection.argtypes = [C.c_void_p, C.c_int, _i, C.c_int, _d, C.c_int]
_lib.env_set_prior.argtypes = [C.c_void_p, C.c_int, C.c_int, _d]
_lib.env_apply_raw.argtypes = [C.c_void_p, C.c_int, C.c_int, C.c_int]
_lib.env_apply_discrete.argtypes = [C.c_void_p, C.c_int, C.c_int]
_lib.pool_step.argtypes = [C.c_void_p, _i, _i, C.c_int]
_lib.pool_obs.argtypes = [C.c_void_p, _i, C.c_int, _f, _u8, _i, _i]
_lib.pool_info.argtypes = [C.c_void_p, _i, C.c_int, _d]
_lib.env_state.argtypes = [C.c_void_p, C.c_int, _i]
_lib.env_hist.argtypes = [C.c_void_p, C.c_int, _i]
_lib.env_stats.argtypes = [C.c_void_p, C.c_int, C.c_int, _d]

_VSR = np.ascontiguousarray(pf.VS_RANDOM, dtype=np.float64)
_PCT = np.ascontiguousarray(pf.PCT, dtype=np.float64)
_lib.fe_set_tables(_VSR.ctypes.data_as(_d), _PCT.ctypes.data_as(_d))


def set_rules(v2):
    _lib.fe_set_rules(1 if v2 else 0)


def evaluate(cards) -> int:
    a = np.asarray(cards, dtype=np.int32)
    return _lib.fe_evaluate(a.ctypes.data_as(_i), len(a))


def _p(a, t):
    return a.ctypes.data_as(t)


class Pool:
    """N independent matches advanced in C; Python only supplies external actions."""

    def __init__(self, n):
        self.n = n
        self.h = _lib.pool_new(n)
        self._keep = {}

    def __del__(self):
        try:
            _lib.pool_free(self.h)
        except Exception:
            pass

    def reset(self, i, seed, ctrl0, ctrl1, hero, start_stack=10000, max_hands=1000):
        _lib.env_reset(self.h, i, seed, ctrl0, ctrl1, hero, start_stack, max_hands)

    def reset_stacks(self, i, seed, ctrl0, ctrl1, hero, s0, s1, max_hands=1000):
        _lib.env_reset_stacks(self.h, i, seed, ctrl0, ctrl1, hero, s0, s1, max_hands)

    def inject(self, i, decks=None, urand=None):
        decks = None if decks is None else np.ascontiguousarray(decks, dtype=np.int32)
        urand = None if urand is None else np.ascontiguousarray(urand, dtype=np.float64)
        self._keep[i] = (decks, urand)
        _lib.env_set_injection(self.h, i, _p(decks, _i) if decks is not None else None,
                               0 if decks is None else len(decks),
                               _p(urand, _d) if urand is not None else None,
                               0 if urand is None else len(urand))

    def set_prior(self, i, seat, counts=None):
        """Start seat's counts of env i's next reset from `counts` (NST floats); None clears. One reset only."""
        if counts is None:
            _lib.env_set_prior(self.h, i, seat, None)
            return
        a = np.ascontiguousarray(counts, dtype=np.float64)
        assert a.shape == (NST,)
        _lib.env_set_prior(self.h, i, seat, _p(a, _d))

    def step(self, idx, acts):
        idx = np.ascontiguousarray(idx, dtype=np.int32)
        acts = np.ascontiguousarray(acts, dtype=np.int32)
        _lib.pool_step(self.h, _p(idx, _i), _p(acts, _i), len(idx))

    def apply_raw(self, i, kind, amount=0):
        return _lib.env_apply_raw(self.h, i, kind, amount)

    def obs(self, idx):
        idx = np.ascontiguousarray(idx, dtype=np.int32)
        n = len(idx)
        obs = np.zeros((n, D_OBS), dtype=np.float32)
        mask = np.zeros((n, NACT), dtype=np.uint8)
        meta = np.zeros((n, 2), dtype=np.int32)
        amts = np.zeros((n, NACT), dtype=np.int32)
        _lib.pool_obs(self.h, _p(idx, _i), n, _p(obs, _f), _p(mask, _u8), _p(meta, _i), _p(amts, _i))
        return obs, mask.astype(bool), meta, amts

    def info(self, idx):
        """rows: done, winner, hand_no, phi, actor, hero, stack0, stack1"""
        idx = np.ascontiguousarray(idx, dtype=np.int32)
        out = np.zeros((len(idx), 8), dtype=np.float64)
        _lib.pool_info(self.h, _p(idx, _i), len(idx), _p(out, _d))
        return out

    def state(self, i):
        out = np.zeros(32, dtype=np.int32)
        _lib.env_state(self.h, i, _p(out, _i))
        keys = ["dealer", "h0a", "h0b", "h1a", "h1b", "b0", "b1", "b2", "b3", "b4", "stack0",
                "stack1", "pot", "to_call", "min_raise", "max_raise", "can_raise", "phase",
                "stacks0", "stacks1", "nh", "hand_no", "done", "bb"]
        return dict(zip(keys, out[:len(keys)].tolist()))

    def hist(self, i):
        out = np.zeros(48 * 4, dtype=np.int32)
        n = _lib.env_hist(self.h, i, _p(out, _i))
        return out[:n * 4].reshape(n, 4).tolist()

    def stats(self, i, seat):
        out = np.zeros(NST, dtype=np.float64)
        _lib.env_stats(self.h, i, seat, _p(out, _d))
        return out


NCL_MAX = 80
SZ_CAP = 300
_lib.fe_set_clones.argtypes = [C.c_int, _d, _d, _i]
_clone_keep = []


def set_clones(theta, sizes, counts):
    """theta (n,4,2,10,4,8,5), sizes (n,2,10,300), counts (n,2,10)."""
    theta = np.ascontiguousarray(theta, dtype=np.float64)
    sizes = np.ascontiguousarray(sizes, dtype=np.float64)
    counts = np.ascontiguousarray(counts, dtype=np.int32)
    _clone_keep[:] = [theta, sizes, counts]
    _lib.fe_set_clones(len(theta), _p(theta, _d), _p(sizes, _d), _p(counts, _i))
