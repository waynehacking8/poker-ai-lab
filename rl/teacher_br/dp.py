"""Match-win best response against the Maniac: inner betting expectimax + outer hand DP.

Inner game (one hand): our hand is summarised by an equity bucket per street; the Maniac
ignores its cards (raises/shoves/calls with fixed probabilities), so its range stays uniform.
Every node returns, for each bucket of ours on the current street, the match-win probability
under optimal play.  Leaves are interpolated from V_{h+1}(stack).
Outer game: V_h(stack, we_are_dealer) over the hand number h, backward from a late hand.

Chips are kept exact (engine rules: min-raise, short all-in does not reopen, refunds); the
stack grid only affects the interpolation of V.

State vector S: 0 sU, 1 sO, 2 bU, 3 bO, 4 level, 5 last_raise, 6 canraise U, 7 canraise O,
8 acted U, 9 acted O, 10 first (the other seat still has to act after a passive action).
Seat 0 is us, seat 1 the Maniac.
Context tuple C: 0 sU0, 1 oU0, 2 bb, 3 raise fractions, 4 we_dealer, 5 grid, 6 V_next,
7 EQW, 8 EQT, 9 Ks, 10 TR.
"""

from __future__ import annotations

import numpy as np
from numba import njit, prange

TOTAL = 20000
# Real server (coordinator note 2026-11-21): 800 from hand 121, 1000 from hand 141, then held.
SCHEDULE = ((20, 100), (40, 150), (60, 200), (80, 300), (100, 400), (120, 600), (140, 800))
FINAL_BB = 1000


def bb_for(h: int) -> int:
    for last, bb in SCHEDULE:
        if h <= last:
            return bb
    return FINAL_BB


@njit
def vfin(C, x):
    return np.interp(float(x), C[5], C[6])


@njit
def showdown(C, street, sU, sO):
    s0 = C[0]
    o0 = C[1]
    m = min(s0 - sU, o0 - sO)
    vw = vfin(C, s0 + m)
    vt = vfin(C, s0)
    vl = vfin(C, s0 - m)
    K = C[9][street]
    out = np.empty(K)
    for b in range(K):
        w = C[7][street, b]
        t = C[8][street, b]
        out[b] = w * vw + t * vt + (1.0 - w - t) * vl
    return out


@njit
def after_call(S, a, to_call):
    S2 = S.copy()
    paid = min(to_call, S[a])
    S2[a] -= paid
    S2[2 + a] += paid
    S2[8 + a] = 1
    return S2


@njit
def after_raise(S, a, amount):
    S2 = S.copy()
    paid = amount - S[2 + a]
    S2[a] -= paid
    S2[2 + a] = amount
    S2[8 + a] = 1
    inc = amount - S[4]
    if inc >= S[5]:
        S2[5] = inc
        S2[6] = 1
        S2[7] = 1
    elif S[8 + (1 - a)] == 1:
        S2[6 + (1 - a)] = 0
    S2[4] = amount
    S2[10] = 0
    return S2


@njit
def node(C, mode, street, actor, S, depth, oa, ok):
    """mode 0: ``actor`` to move; 1: betting round ended; 2: ``actor`` just called/checked."""
    sU0 = C[0]
    oU0 = C[1]
    bb = C[2]
    K = C[9][street]
    sU = S[0]
    sO = S[1]
    if mode == 2:
        if S[10] == 1:
            S2 = S.copy()
            S2[10] = 0
            return node(C, 0, street, 1 - actor, S2, depth + 1, oa, ok)
        return node(C, 1, street, actor, S, depth + 1, oa, ok)
    if mode == 1:
        if street == 3 or sU == 0 or sO == 0:
            return showdown(C, street, sU, sO)
        S2 = np.zeros(11, np.int64)
        S2[0] = sU
        S2[1] = sO
        S2[5] = bb
        S2[6] = 1
        S2[7] = 1
        S2[10] = 1
        # post-flop the non-dealer acts first: us if we are not the dealer
        first = 0 if C[4] == 0 else 1
        nxt = node(C, 0, street + 1, first, S2, depth + 1, oa, ok)
        Kn = C[9][street + 1]
        out = np.zeros(K)
        for b in range(K):
            acc = 0.0
            for b2 in range(Kn):
                acc += C[10][street, b, b2] * nxt[b2]
            out[b] = acc
        return out
    # ---- mode 0 ----
    me = actor
    my_stack = S[me]
    other_stack = S[1 - me]
    level = S[4]
    to_call = max(level - S[2 + me], 0)
    if my_stack == 0 or (to_call == 0 and other_stack == 0):
        if S[10] == 1 and my_stack == 0 and other_stack > 0:
            S2 = S.copy()
            S2[10] = 0
            return node(C, 0, street, 1 - me, S2, depth + 1, oa, ok)
        return node(C, 1, street, actor, S, depth + 1, oa, ok)
    pot = (sU0 - sU) + (oU0 - sO)
    minr = level + S[5]
    maxr = S[2 + me] + my_stack
    can_raise = other_stack > 0 and my_stack > to_call and S[6 + me] == 1
    lo = min(minr, maxr)
    if actor == 1:
        # Maniac: shove 0.25, 0.8-pot raise 0.5, else call/check (never folds)
        S3 = after_call(S, 1, to_call)
        v3 = node(C, 2, street, 1, S3, depth + 1, oa, ok)
        if not can_raise:
            return v3
        size = level + 0.8 * (pot + to_call)
        tgt = max(size, float(minr))
        amt = int(max(float(lo), min(float(maxr), tgt)))
        v1 = node(C, 0, street, 0, after_raise(S, 1, maxr), depth + 1, oa, ok)
        v2 = node(C, 0, street, 0, after_raise(S, 1, amt), depth + 1, oa, ok)
        out = np.zeros(K)
        for b in range(K):
            out[b] = 0.25 * v1[b] + 0.5 * v2[b] + 0.25 * v3[b]
        return out
    # ---- our decision ----
    best = np.full(K, -1.0)
    ba = np.zeros(K, np.int64)
    bamt = np.zeros(K, np.int64)
    if to_call > 0:
        fv = vfin(C, sU)
        for b in range(K):
            best[b] = fv
            ba[b] = 0
    vc = node(C, 2, street, 0, after_call(S, 0, to_call), depth + 1, oa, ok)
    for b in range(K):
        if vc[b] > best[b]:
            best[b] = vc[b]
            ba[b] = 1
    if can_raise:
        fr = C[3]
        nt = 0
        tg = np.zeros(len(fr) + 1, np.int64)
        for i in range(len(fr) + 1):
            if i < len(fr):
                a = int(level + fr[i] * (pot + to_call))
                a = max(lo, min(maxr, a))
            else:
                a = maxr
            dup = False
            for j in range(nt):
                if tg[j] == a:
                    dup = True
            if dup:
                continue
            tg[nt] = a
            nt += 1
            v = node(C, 0, street, 1, after_raise(S, 0, a), depth + 1, oa, ok)
            for b in range(K):
                if v[b] > best[b] + 1e-12:
                    best[b] = v[b]
                    ba[b] = 2
                    bamt[b] = a
    if depth == 0:
        for b in range(K):
            oa[b] = ba[b]
            ok[b] = bamt[b]
    return best


@njit
def start_state(C, we_dealer, bb):
    S = np.zeros(11, np.int64)
    S[0] = C[0]
    S[1] = C[1]
    sb = bb // 2
    d = 0 if we_dealer == 1 else 1
    pd = min(sb, S[d])
    S[d] -= pd
    S[2 + d] += pd
    pb = min(bb, S[1 - d])
    S[1 - d] -= pb
    S[3 - d] += pb
    S[4] = max(pd, pb)  # the bet to match is the larger post (engine rule)
    S[5] = bb
    S[6] = 1
    S[7] = 1
    S[10] = 1
    return S, d


@njit
def hand_value(C, we_dealer, bb, prior):
    oa = np.zeros(169, np.int64)
    ok = np.zeros(169, np.int64)
    S, d = start_state(C, we_dealer, bb)
    if S[3 - d] <= S[2 + d]:
        # big blind all in for no more than the small blind: no action, excess refunded
        v = showdown(C, 0, S[0], S[1])
    else:
        v = node(C, 0, 0, d, S, 0, oa, ok)
    acc = 0.0
    for c in range(169):
        acc += prior[c] * v[c]
    return acc


@njit
def hand_policy(C, we_dealer, bb):
    oa = np.zeros(169, np.int64)
    ok = np.zeros(169, np.int64)
    S, d = start_state(C, we_dealer, bb)
    v = node(C, 0, 0, d, S, 0, oa, ok)
    return v, oa, ok


@njit(parallel=True)
def layer(grid, Vn, bb, we_dealer, fr, EQW, EQT, Ks, TR, prior):
    """One hand-number layer: V over ``grid`` given V_{h+1} of the opposite role."""
    n = len(grid)
    out = np.zeros(n)
    for i in prange(n):
        s = int(grid[i])
        if s <= 0:
            out[i] = 0.0
        elif s >= TOTAL:
            out[i] = 1.0
        else:
            C = (s, TOTAL - s, bb, fr, we_dealer, grid, Vn, EQW, EQT, Ks, TR)
            out[i] = hand_value(C, we_dealer, bb, prior)
    return out


def make_ctx(s, we_dealer, bb, grid, Vn, tab, fr):
    return (int(s), int(TOTAL - s), int(bb), np.asarray(fr, float), int(we_dealer),
            np.asarray(grid, float), np.asarray(Vn, float), tab["EQW"], tab["EQT"],
            tab["Ks"].astype(np.int64), tab["TR"])


def default_grid(step_mid=500):
    g = (list(range(0, 2000, 100)) + list(range(2000, 18000, step_mid))
         + list(range(18000, 20001, 100)))
    return np.array(g, dtype=float)


def solve_match(tab, fr=(0.5, 1.0, 2.0), hmax=200, grid=None, verbose=False):
    """Backward DP.  Returns (grid, V) with V[h][role][i]; role 1 = we deal on hand h."""
    grid = default_grid() if grid is None else grid
    EQW, EQT, TR, prior = tab["EQW"], tab["EQT"], tab["TR"], tab["prior"]
    Ks = tab["Ks"].astype(np.int64)
    fr = np.asarray(fr, float)
    share = grid / TOTAL
    V = {hmax + 1: {0: share.copy(), 1: share.copy()}}
    for h in range(hmax, 0, -1):
        bb = bb_for(h)
        V[h] = {}
        for role in (0, 1):
            V[h][role] = layer(grid, V[h + 1][1 - role], bb, role, fr, EQW, EQT, Ks, TR, prior)
        if verbose and h % 10 == 0:
            i = int(np.searchsorted(grid, 10000))
            print(h, V[h][0][i], V[h][1][i], flush=True)
    return grid, V
