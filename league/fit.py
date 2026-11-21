"""Fit field archetypes and per-bot clones from Chipzen replays.

Pipeline: parse NLHE replays -> per-bot statistics -> k-means archetypes -> for every
population (archetype or single bot) fit an action table indexed by
(street, position, facing class, effective stack, strength bucket) with EM over the
hidden hole cards of players whose hand ended in a fold, then backoff smoothing.

    python -m league.fit --data data --out out/clones.npz --holdout 0.2
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from nlhe.cards import card_from_str

from .context import (F_BET_L, F_BET_M, F_BET_S, F_BET_XL, F_LIMP, F_NOBET, F_OPEN, F_RAISED,
                      F_VS_3BET, F_VS_OPEN, NA, NFCL, NPOS, NSTK, NSTREET, RAISE, event_of_act)
from .replays import load_dir
from .stats import CLUSTER_STATS, add_hand, new_counter
from .strength import NB, NCOMBO, PRE_BUCKETS, board_buckets, combo_index

TABLE_SHAPE = (NSTREET, NPOS, NFCL, NSTK, NB, NA)
K_G, K_P, K_F, K_BOT = 2.0, 8.0, 6.0, 12.0
FACING = (F_OPEN, F_VS_OPEN, F_VS_3BET, F_BET_S, F_BET_M, F_BET_L, F_BET_XL, F_RAISED)
SIZE_CAP = 300


def legal_matrix() -> np.ndarray:
    m = np.zeros((NFCL, NA))
    for f in range(NFCL):
        if f in FACING:
            m[f, [0, 2, 3, 4]] = 1
        elif f in (F_LIMP, F_NOBET):
            m[f, [1, 3, 4]] = 1
    return m


LEGAL = legal_matrix()


def split_of(match_id: str, holdout: float, seed: int) -> bool:
    """True if the match belongs to the held-out set (stable hash split)."""
    h = int(hashlib.sha256(f"{seed}:{match_id}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return h < holdout


# --------------------------------------------------------------------------------------
# smoothing
# --------------------------------------------------------------------------------------
def smooth(C: np.ndarray, prior: np.ndarray | None = None) -> np.ndarray:
    """Backoff-smoothed action probabilities from (expected) counts ``C``.

    Full cell -> (street, position, facing, strength) -> (street, facing, strength) ->
    masked uniform; with ``prior`` (an archetype table) a single shrink toward it.
    """
    if prior is not None:
        return (C + K_BOT * prior) / (C.sum(-1, keepdims=True) + K_BOT)
    legal = LEGAL[None, None, :, None, None, :]
    U = legal / np.maximum(legal.sum(-1, keepdims=True), 1)
    G = C.sum(axis=(1, 3), keepdims=True)
    thG = (G + K_G * U) / (G.sum(-1, keepdims=True) + K_G)
    Pn = C.sum(axis=3, keepdims=True)
    thP = (Pn + K_P * thG) / (Pn.sum(-1, keepdims=True) + K_P)
    return (C + K_F * thP) / (C.sum(-1, keepdims=True) + K_F)


# --------------------------------------------------------------------------------------
# hand-seat records
# --------------------------------------------------------------------------------------
class SeatRec:
    __slots__ = ("events", "known", "tabs")

    def __init__(self, events, known, tabs):
        self.events = events  # [(ctx, code, frac)]
        self.known = known    # combo index when the hole cards were shown, else None
        self.tabs = tabs      # per event: np.int8[NCOMBO] bucket by combo (-1 = blocked)


def seat_records(hands):
    """Yield (name, SeatRec) for every hand-seat with at least one decision."""
    for h in hands:
        board = [card_from_str(c) for c in h.board]
        tab_cache = {}
        for seat in (0, 1):
            evs, tabs = [], []
            for a in h.acts:
                if a.seat != seat:
                    continue
                ctx, code, frac = event_of_act(a, seat == h.button)
                street = ctx[0]
                if street == 0:
                    tab = PRE_BUCKETS
                else:
                    n = (3, 4, 5)[street - 1]
                    if len(board) < n:
                        continue
                    if n not in tab_cache:
                        tab_cache[n] = board_buckets(tuple(sorted(board[:n])))
                    tab = tab_cache[n]
                evs.append((ctx, code, frac))
                tabs.append(tab)
            if not evs:
                continue
            known = None
            if seat in h.hole and len(h.hole[seat]) == 2:
                c = [card_from_str(x) for x in h.hole[seat]]
                known = combo_index(c[0], c[1])
            yield h.names[seat], SeatRec(evs, known, tabs)


def fit_table(recs, iters=8, prior=None, naive=False):
    """EM over hidden holdings.  Returns (theta, counts); ``naive`` drops folded hands."""
    C = np.zeros(TABLE_SHAPE)
    for r in recs:
        if r.known is not None:
            for (ctx, code, _), tab in zip(r.events, r.tabs):
                C[ctx][tab[r.known], code] += 1
    theta = smooth(C, prior)
    if naive:
        return theta, C
    unknown = [r for r in recs if r.known is None]
    base = C.copy()
    for _ in range(iters):
        Cn = base.copy()
        for r in unknown:
            logw = np.zeros(NCOMBO)
            for (ctx, code, _), tab in zip(r.events, r.tabs):
                blocked = tab < 0
                p = theta[ctx][np.where(blocked, 0, tab), code]
                logw += np.log(np.maximum(p, 1e-9))
                logw[blocked] = -np.inf
            w = np.exp(logw - logw.max())
            w /= w.sum()
            for (ctx, code, _), tab in zip(r.events, r.tabs):
                ok = tab >= 0
                np.add.at(Cn[ctx][:, code], tab[ok], w[ok])
        C = Cn
        theta = smooth(C, prior)
    return theta, C


def collect_sizes(recs):
    out = defaultdict(list)
    for r in recs:
        for ctx, code, frac in r.events:
            if code == RAISE and frac is not None:
                out[(0 if ctx[0] == 0 else 1, ctx[2])].append(round(min(max(frac, 0.05), 8.0), 3))
    return out


# --------------------------------------------------------------------------------------
# clustering
# --------------------------------------------------------------------------------------
def bot_vectors(hands, shrink=20.0):
    """Per-bot shrunk statistic vectors; returns (names, X, n_hands)."""
    per = defaultdict(new_counter)
    for h in hands:
        for s in (0, 1):
            add_hand(per[h.names[s]], h, include=lambda x, s=s: x == s)
    pooled = new_counter()
    for h in hands:
        add_hand(pooled, h)
    names = sorted(per, key=lambda n: (-per[n]["hands"][0], n))
    X, nh = [], []
    for n in names:
        row = []
        for k in CLUSTER_STATS:
            num, den = per[n][k]
            pn, pd = pooled[k]
            prior = pn / pd if pd else 0.0
            row.append((num + shrink * prior) / (den + shrink))
        X.append(row)
        nh.append(per[n]["hands"][0])
    return names, np.array(X), np.array(nh)


def kmeans(X, w, k, seed, restarts=20):
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(restarts):
        idx = [int(rng.choice(len(X), p=w / w.sum()))]
        for _ in range(k - 1):
            d = np.min([((X - X[i]) ** 2).sum(1) for i in idx], axis=0) * w + 1e-12
            idx.append(int(rng.choice(len(X), p=d / d.sum())))
        C = X[idx].copy()
        for _ in range(100):
            lab = np.argmin(((X[:, None] - C[None]) ** 2).sum(-1), axis=1)
            Cn = np.array([np.average(X[lab == j], axis=0, weights=w[lab == j])
                           if (lab == j).any() else C[j] for j in range(k)])
            if np.allclose(Cn, C):
                break
            C = Cn
        inertia = float((w * ((X - C[lab]) ** 2).sum(1)).sum())
        if best is None or inertia < best[0]:
            best = (inertia, lab, C)
    return best


def silhouette(X, lab, w):
    k = int(lab.max()) + 1
    if k < 2:
        return -1.0
    s = []
    for i in range(len(X)):
        d = np.sqrt(((X - X[i]) ** 2).sum(1))
        own = (lab == lab[i]) & (np.arange(len(X)) != i)
        a = d[own].mean() if own.any() else 0.0
        b = min(d[lab == j].mean() for j in range(k) if j != lab[i] and (lab == j).any())
        s.append((b - a) / max(a, b, 1e-9))
    return float(np.average(s, weights=w))


def cluster(X, nh, seed, kmin=4, kmax=6, min_share=0.05):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = (X - mu) / sd
    w = np.sqrt(nh.astype(float))
    best, scores = None, {}
    for k in range(kmin, kmax + 1):
        _, lab, C = kmeans(Z, w, k, seed)
        share = np.array([w[lab == j].sum() for j in range(k)]) / w.sum()
        sil = silhouette(Z, lab, w)
        scores[k] = round(sil, 3)
        if share.min() >= min_share and (best is None or sil > best[0]):
            best = (sil, k, lab, C)
    sil, k, lab, C = best
    return {"k": k, "silhouette": sil, "scores": scores, "labels": lab, "centroids_z": C,
            "mu": mu, "sd": sd}


def archetype_name(cent_raw, feats=CLUSTER_STATS) -> str:
    raw = dict(zip(feats, cent_raw))
    if raw["fold_to_bet"] < 0.1 and raw["wtsd"] > 0.9:
        return "station"
    if raw["bb_fold_vs_open"] > 0.5:
        base = "bb-folder"
    elif raw["btn_open"] > 0.55:
        base = "opener"
    elif raw["btn_limp"] > 0.6:
        base = "limper"
    else:
        base = "mixed"
    post = "aggro" if raw["post_agg"] >= 0.75 else "calm"
    return f"{base}-{post}" + ("-shover" if raw["pf_allin_short"] > 0.08 else "")


# --------------------------------------------------------------------------------------
# main fit
# --------------------------------------------------------------------------------------
def pack_sizes(sizes):
    return {f"{a}:{f}": v[:SIZE_CAP] for (a, f), v in sizes.items()}


def fit_all(hands, matches, seed=1, top_bots=10, min_bot_hands=150, iters=8):
    names, X, nh = bot_vectors(hands)
    cl = cluster(X, nh, seed)
    k = cl["k"]
    lab = {n: int(c) for n, c in zip(names, cl["labels"])}
    raw_cent = cl["centroids_z"] * cl["sd"] + cl["mu"]
    arch_names = [f"A{j}-{archetype_name(raw_cent[j])}" for j in range(k)]
    appear = np.zeros(k)
    for m in matches:
        for p in m["participants"]:
            if p["name"] in lab and m.get("rated"):
                appear[lab[p["name"]]] += 1
    hand_share = np.array([sum(nh[i] for i, n in enumerate(names) if lab[n] == j)
                           for j in range(k)], float)
    by_arch = {j: [] for j in range(k)}
    by_bot = defaultdict(list)
    for name, rec in seat_records(hands):
        by_arch[lab[name]].append(rec)
        by_bot[name].append(rec)
    arch_theta, arch_naive, arch_sizes = [], [], []
    for j in range(k):
        arch_theta.append(fit_table(by_arch[j], iters)[0])
        arch_naive.append(fit_table(by_arch[j], naive=True)[0])
        arch_sizes.append(pack_sizes(collect_sizes(by_arch[j])))
    all_sizes = pack_sizes(collect_sizes([r for rs in by_arch.values() for r in rs]))
    bots = [n for n in names if len(by_bot[n]) >= min_bot_hands][:top_bots]
    bot_theta, bot_sizes = [], []
    for n in bots:
        bot_theta.append(fit_table(by_bot[n], iters, prior=arch_theta[lab[n]])[0])
        bot_sizes.append(pack_sizes(collect_sizes(by_bot[n])))
    meta = {
        "k": k, "silhouette": round(cl["silhouette"], 3), "silhouette_by_k": cl["scores"],
        "arch_names": arch_names, "weights_rated": (appear / appear.sum()).tolist(),
        "weights_by_hands": (hand_share / hand_share.sum()).tolist(),
        "members": {str(j): [n for n in names if lab[n] == j] for j in range(k)},
        "bot_archetype": lab, "bots": bots, "cluster_stats": list(CLUSTER_STATS),
        "bot_vectors": {n: [round(float(v), 4) for v in X[i]] for i, n in enumerate(names)},
        "bot_hands": {n: int(nh[i]) for i, n in enumerate(names)},
        "centroids_raw": raw_cent.round(4).tolist(),
        "n_matches": len(matches), "n_hands": len(hands),
        "arch_sizes": arch_sizes, "bot_sizes": bot_sizes, "all_sizes": all_sizes,
    }
    return meta, np.array(arch_theta), np.array(bot_theta), np.array(arch_naive)


def save(path, meta, arch_theta, bot_theta, arch_naive):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, arch_theta=arch_theta.astype(np.float32),
                        bot_theta=bot_theta.astype(np.float32),
                        arch_naive=arch_naive.astype(np.float32),
                        meta=np.array(json.dumps(meta)))


def main(argv=None):
    global K_BOT
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="out/clones.npz")
    ap.add_argument("--holdout", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--iters", type=int, default=8)
    ap.add_argument("--k-bot", type=float, default=K_BOT, help="shrink of a bot clone toward its archetype")
    args = ap.parse_args(argv)
    K_BOT = args.k_bot
    ms = load_dir(args.data)
    train = [(m, hs) for m, hs in ms if not split_of(m["id"], args.holdout, args.seed)]
    test_ids = [m["id"] for m, _ in ms if split_of(m["id"], args.holdout, args.seed)]
    hands = [h for _, hs in train for h in hs]
    meta, at, bt, an = fit_all(hands, [m for m, _ in train], args.seed, iters=args.iters)
    meta["holdout"] = args.holdout
    meta["test_match_ids"] = test_ids
    save(args.out, meta, at, bt, an)
    print(json.dumps({k: meta[k] for k in ("k", "silhouette", "silhouette_by_k", "arch_names",
                                            "weights_rated", "n_matches", "n_hands", "bots")},
                     indent=1))


if __name__ == "__main__":
    main()
