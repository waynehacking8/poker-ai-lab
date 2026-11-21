"""Numba 7-card evaluator and exact equity enumeration (cards are ints rank*4+suit).

The score ordering matches chipzen_bot/nlhe/evaluator.py (checked in tests/test_br.py).
"""

from __future__ import annotations

import numpy as np
from numba import njit


def _tables():
    straight = np.full(8192, -1, dtype=np.int64)
    top5 = np.zeros(8192, dtype=np.int64)
    for mask in range(8192):
        for high in range(12, 3, -1):
            window = 0b11111 << (high - 4)
            if mask & window == window:
                straight[mask] = high
                break
        else:
            if mask & 0b1000000001111 == 0b1000000001111:
                straight[mask] = 3
        if bin(mask).count("1") >= 5:
            ranks = [r for r in range(12, -1, -1) if mask >> r & 1][:5]
            v = 0
            for r in ranks:
                v = (v << 4) | r
            top5[mask] = v
    return straight, top5


STRAIGHT, TOP5 = _tables()


@njit(cache=True)
def _pack(a, n):
    v = 0
    for i in range(5):
        v <<= 4
        if i < n:
            v |= a[i]
    return v


@njit(cache=True)
def evaluate(cards, n, STRAIGHT, TOP5):
    cnt = np.zeros(13, np.int64)
    sm = np.zeros(4, np.int64)
    sc = np.zeros(4, np.int64)
    for i in range(n):
        c = cards[i]
        r = c >> 2
        s = c & 3
        cnt[r] += 1
        sm[s] |= 1 << r
        sc[s] += 1
    flush_mask = 0
    for s in range(4):
        if sc[s] >= 5:
            flush_mask = sm[s]
            break
    if flush_mask:
        sf = STRAIGHT[flush_mask]
        if sf >= 0:
            return (8 << 20) | (sf << 16)
    quad = -1
    trips = np.zeros(3, np.int64)
    nt = 0
    pairs = np.zeros(3, np.int64)
    npr = 0
    singles = np.zeros(7, np.int64)
    ns = 0
    rank_mask = 0
    for r in range(12, -1, -1):
        c = cnt[r]
        if c:
            rank_mask |= 1 << r
            if c == 1:
                singles[ns] = r
                ns += 1
            elif c == 2:
                pairs[npr] = r
                npr += 1
            elif c == 3:
                trips[nt] = r
                nt += 1
            else:
                quad = r
    if quad >= 0:
        rest = -1
        for r in range(12, -1, -1):
            if cnt[r] and r != quad:
                rest = r
                break
        return (7 << 20) | (quad << 16) | (rest << 12)
    if nt and (nt > 1 or npr):
        pair = -1
        if nt > 1:
            pair = trips[1]
        if npr and pairs[0] > pair:
            pair = pairs[0]
        return (6 << 20) | (trips[0] << 16) | (pair << 12)
    if flush_mask:
        return (5 << 20) | TOP5[flush_mask]
    st = STRAIGHT[rank_mask]
    if st >= 0:
        return (4 << 20) | (st << 16)
    if nt:
        a = np.zeros(3, np.int64)
        a[0] = trips[0]
        k = 1
        for i in range(min(2, ns)):
            a[k] = singles[i]
            k += 1
        return (3 << 20) | _pack(a, k)
    if npr >= 2:
        kick = singles[0] if ns else -1
        if npr == 3 and pairs[2] > kick:
            kick = pairs[2]
        a = np.zeros(3, np.int64)
        a[0] = pairs[0]
        a[1] = pairs[1]
        a[2] = kick
        # the reference packs -1 as an all-ones nibble pattern; mirror it exactly
        return (2 << 20) | _pack_signed(a, 3)
    if npr:
        a = np.zeros(4, np.int64)
        a[0] = pairs[0]
        k = 1
        for i in range(min(3, ns)):
            a[k] = singles[i]
            k += 1
        return (1 << 20) | _pack(a, k)
    return _pack(singles, min(5, ns))


@njit(cache=True)
def _pack_signed(a, n):
    # mirrors python: v = (v << 4) | r with r possibly -1, then << 4*(5-n)
    v = 0
    for i in range(n):
        v = (v << 4) | a[i]
    return v << (4 * (5 - n))


def py_evaluate(cards):
    c = np.array(cards, dtype=np.int64)
    return int(evaluate(c, len(c), STRAIGHT, TOP5))


@njit(cache=True)
def river_eq(hole0, hole1, board, STRAIGHT, TOP5):
    """(win, tie) probability vs a uniform random opponent hand on a full 5-card board."""
    used = np.zeros(52, np.bool_)
    used[hole0] = True
    used[hole1] = True
    for i in range(5):
        used[board[i]] = True
    mine = np.zeros(7, np.int64)
    mine[0] = hole0
    mine[1] = hole1
    theirs = np.zeros(7, np.int64)
    for i in range(5):
        mine[2 + i] = board[i]
        theirs[2 + i] = board[i]
    ms = evaluate(mine, 7, STRAIGHT, TOP5)
    w = 0
    t = 0
    n = 0
    for a in range(52):
        if used[a]:
            continue
        theirs[0] = a
        for b in range(a + 1, 52):
            if used[b]:
                continue
            theirs[1] = b
            os_ = evaluate(theirs, 7, STRAIGHT, TOP5)
            n += 1
            if ms > os_:
                w += 1
            elif ms == os_:
                t += 1
    return w / n, t / n


@njit(cache=True)
def turn_eq(hole0, hole1, board4, STRAIGHT, TOP5):
    b5 = np.zeros(5, np.int64)
    for i in range(4):
        b5[i] = board4[i]
    used = np.zeros(52, np.bool_)
    used[hole0] = True
    used[hole1] = True
    for i in range(4):
        used[board4[i]] = True
    w = 0.0
    t = 0.0
    n = 0
    for r in range(52):
        if used[r]:
            continue
        b5[4] = r
        a, b = river_eq(hole0, hole1, b5, STRAIGHT, TOP5)
        w += a
        t += b
        n += 1
    return w / n, t / n


@njit(cache=True)
def flop_eq(hole0, hole1, board3, STRAIGHT, TOP5):
    """Exact all-in equity from the flop vs a random hand, enumerating runouts x opp hands."""
    used = np.zeros(52, np.bool_)
    used[hole0] = True
    used[hole1] = True
    for i in range(3):
        used[board3[i]] = True
    mine = np.zeros(7, np.int64)
    mine[0] = hole0
    mine[1] = hole1
    theirs = np.zeros(7, np.int64)
    for i in range(3):
        mine[2 + i] = board3[i]
        theirs[2 + i] = board3[i]
    w = 0
    t = 0
    n = 0
    for tc in range(52):
        if used[tc]:
            continue
        mine[5] = tc
        theirs[5] = tc
        for rc in range(tc + 1, 52):
            if used[rc]:
                continue
            mine[6] = rc
            theirs[6] = rc
            ms = evaluate(mine, 7, STRAIGHT, TOP5)
            for a in range(52):
                if used[a] or a == tc or a == rc:
                    continue
                theirs[0] = a
                for b in range(a + 1, 52):
                    if used[b] or b == tc or b == rc:
                        continue
                    theirs[1] = b
                    os_ = evaluate(theirs, 7, STRAIGHT, TOP5)
                    n += 1
                    if ms > os_:
                        w += 1
                    elif ms == os_:
                        t += 1
    return w / n, t / n
