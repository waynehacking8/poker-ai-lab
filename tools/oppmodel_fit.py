"""Fit, select and score the opponent model (roadmap X1), or benchmark its runtime.

    python tools/oppmodel_fit.py fit   --data DIR [--out LOGDIR] [--model rl/models/oppmodel.npz]
    python tools/oppmodel_fit.py bench --data DIR [--model rl/models/oppmodel.npz] [--limit N]

fit: poker replays sorted by metadata.start_time; the latest 30% are held out, the latest 20% of the rest are
validation. Every choice (prior features and hidden size, bucket edges, shrinkage k, in-match weight w, the
in-match-only strength k_im) is made on validation with the model fit on the other training matches. The
chosen model is refit on all training matches, frozen, saved, and scored once on the held-out subsets.
fit needs torch (training only); bench and the runtime module need numpy only.
"""
import argparse
import copy
import glob
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from rl.oppmodel import (NCLS, OppModel, bucket, extract_replay, features, n_buckets,  # noqa: E402
                         prior_probs, save_params, describe)

N_MIN = 200        # training actions that make a name "known"
M_MIN_MATCHES = 10
M_MIN_NAMES = 3
UNSEEN_FROM_HAND = 10   # 0-based hand index
HIDDEN = (0, 32, 64, 128)
EDGE_SETS = ([], [0.5], [0.35, 0.8], [0.3, 0.6, 1.2])
K_GRID = (0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500)
W_GRID = (0.25, 0.5, 1, 2, 4, 8)
KIM_GRID = (0.25, 0.5, 1, 2, 4, 8, 16, 32, 64)
MAX_EPOCHS = 40
BOOT = 5000


# ---------------------------------------------------------------- data

def load_samples(data_dir):
    ms = []
    for f in sorted(glob.glob(os.path.join(data_dir, "*.json"))):
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        if d["match"].get("game_type") != "poker":
            continue
        r = d["replay"]
        ms.append((r["metadata"]["start_time"], os.path.basename(f), r))
    ms.sort(key=lambda t: (t[0], t[1]))
    rows = []
    for mi, (_, _, r) in enumerate(ms):
        for hi, seat, name, st, cls in extract_replay(r):
            rows.append((mi, hi, seat, name, st, cls))
    return ms, rows


class Data:
    def __init__(self, data_dir):
        self.ms, rows = load_samples(data_dir)
        self.n_matches = len(self.ms)
        self.mi = np.array([r[0] for r in rows])
        self.hand = np.array([r[1] for r in rows])
        self.seat = np.array([r[2] for r in rows])
        self.names = sorted({r[3] for r in rows})
        nid = {n: i for i, n in enumerate(self.names)}
        self.nid = np.array([nid[r[3]] for r in rows])
        self.states = [r[4] for r in rows]
        self.y = np.array([r[5] for r in rows])
        self.X = {fs: np.stack([features(s, fs) for s in self.states]) for fs in (0, 1)}
        self.n_held = round(0.3 * self.n_matches)
        self.t_train = self.n_matches - self.n_held                  # first held-out match index
        self.n_val = round(0.2 * self.t_train)
        self.t_sub = self.t_train - self.n_val                       # first validation match index
        self.bcache = {}

    def buckets(self, edges):
        key = tuple(edges)
        if key not in self.bcache:
            self.bcache[key] = np.array([bucket(s, edges) for s in self.states])
        return self.bcache[key]

    def name_counts(self, limit):
        """Training actions per name for matches < limit."""
        return np.bincount(self.nid[self.mi < limit], minlength=len(self.names))

    def ctx(self, edges, limit):
        """Per-sample name counts n (from matches < limit) and in-match counts m (before the action)."""
        b = self.buckets(edges)
        nb = n_buckets(edges)
        C = np.zeros((len(self.names), nb, NCLS))
        tr = self.mi < limit
        np.add.at(C, (self.nid[tr], b[tr], self.y[tr]), 1.0)
        n = C[self.nid, b]
        m = np.zeros((len(self.y), NCLS))
        cur = {}
        for i in range(len(self.y)):
            key = (self.mi[i], self.seat[i])
            a = cur.get(key)
            if a is None:
                a = cur[key] = np.zeros((nb, NCLS))
            m[i] = a[b[i]]
            a[b[i], self.y[i]] += 1.0
        return C, n, m


# ---------------------------------------------------------------- prior training (torch)

def train_prior(Xtr, ytr, hidden, epochs, Xva=None, yva=None, seed=0):
    import torch
    import torch.nn as nn
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    d = Xtr.shape[1]
    net = nn.Linear(d, NCLS) if hidden == 0 else nn.Sequential(nn.Linear(d, hidden), nn.ReLU(),
                                                              nn.Linear(hidden, NCLS))
    opt = torch.optim.Adam(net.parameters(), lr=3e-3, weight_decay=1e-5)
    Xt, yt = torch.tensor(Xtr), torch.tensor(ytr, dtype=torch.long)
    g = torch.Generator().manual_seed(seed)
    best = (1e9, 0, None)
    curve = []
    for ep in range(1, epochs + 1):
        perm = torch.randperm(len(yt), generator=g)
        for i in range(0, len(perm), 256):
            idx = perm[i:i + 256]
            loss = nn.functional.cross_entropy(net(Xt[idx]), yt[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
        if Xva is not None:
            p = to_params(net, hidden)
            l = float(-np.log(prior_probs(p, Xva)[np.arange(len(yva)), yva] + 1e-12).mean())
            curve.append(l)
            if l < best[0]:
                best = (l, ep, p)
    return (to_params(net, hidden) if Xva is None else best[2]), best[:2], curve


def to_params(net, hidden):
    import torch.nn as nn
    ws = [m for m in net.modules() if isinstance(m, nn.Linear)]
    f = lambda t: t.detach().numpy().astype(np.float32)  # noqa: E731
    if hidden == 0:
        return {"W1": np.zeros((0, ws[0].in_features), np.float32), "b1": np.zeros(0, np.float32),
                "W2": f(ws[0].weight), "b2": f(ws[0].bias)}
    return {"W1": f(ws[0].weight), "b1": f(ws[0].bias), "W2": f(ws[1].weight), "b2": f(ws[1].bias)}


# ---------------------------------------------------------------- scoring

def p_of(num, y):
    return num[np.arange(len(y)), y] / num.sum(axis=1)


def ll_prior(p0, y):
    return -np.log(p0[np.arange(len(y)), y])


def ll_im(p0, m, y, kim):
    return -np.log(p_of(m + kim * p0, y))


def ll_full(p0, n, m, y, k, w):
    return -np.log(p_of(n + w * m + k * p0, y))


def bootstrap(mi, la, lb, rng):
    """Mean over actions of (la - lb), 95% interval over matches. Positive means b is better."""
    u, inv = np.unique(mi, return_inverse=True)
    sa = np.bincount(inv, weights=la)
    sb = np.bincount(inv, weights=lb)
    cnt = np.bincount(inv).astype(float)
    idx = rng.integers(0, len(u), (BOOT, len(u)))
    d = (sa[idx].sum(1) - sb[idx].sum(1)) / cnt[idx].sum(1)
    return float((sa.sum() - sb.sum()) / cnt.sum()), [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


def subsets(D, limit, lo, hi):
    """(known, unseen) boolean masks over samples for matches in [lo, hi); names judged on matches < limit."""
    cnt = D.name_counts(limit)
    inr = (D.mi >= lo) & (D.mi < hi)
    known = inr & (cnt[D.nid] >= N_MIN)
    unseen = inr & (cnt[D.nid] == 0) & (D.hand >= UNSEEN_FROM_HAND)
    return known, unseen


def size(D, mask):
    return {"actions": int(mask.sum()), "matches": int(len(np.unique(D.mi[mask]))),
            "names": int(len(np.unique(D.nid[mask])))}


# ---------------------------------------------------------------- fit

def fit(args):
    D = Data(args.data)
    log = []

    def say(*a):
        s = " ".join(str(x) for x in a)
        print(s, flush=True)
        log.append(s)

    say("matches", D.n_matches, "training", D.t_train, "held out", D.n_held,
        "| fit part", D.t_sub, "validation", D.n_val, "| actions", len(D.y), "| names", len(D.names))
    t0 = D.ms[D.t_train][0]
    say("held out from", t0, "; training from", D.ms[0][0], "to", D.ms[D.t_train - 1][0])
    kh, uh = subsets(D, D.t_train, D.t_train, D.n_matches)
    sz = {"known": size(D, kh), "unseen": size(D, uh)}
    say("held-out subset counts (before fitting): known names", sz["known"], "| unseen names", sz["unseen"])
    say("  unseen names:", sorted({D.names[i] for i in np.unique(D.nid[uh])}))

    # ---- selection on validation
    val = (D.mi >= D.t_sub) & (D.mi < D.t_train)
    fit_part = D.mi < D.t_sub
    yv = D.y[val]
    say("selection: validation actions", int(val.sum()))
    res = {}
    best = None
    for fs in (0, 1):
        for hid in HIDDEN:
            p, (l, ep), _ = train_prior(D.X[fs][fit_part], D.y[fit_part], hid, MAX_EPOCHS, D.X[fs][val], yv)
            res[f"fs{fs}_h{hid}"] = {"val_loss": l, "epoch": ep}
            say(f"  prior fs={fs} hidden={hid}: validation log loss {l:.4f} at epoch {ep}")
            if best is None or l < best[0]:
                best = (l, fs, hid, ep, p)
    _, fs, hid, ep, pp = best
    say(f"selected prior: feature set {fs} ({'core+extras' if fs else 'core'}), hidden {hid}, epochs {ep}")
    P0 = prior_probs(pp, D.X[fs])   # fit-part prior on every sample (only validation rows are used)

    vk, _ = subsets(D, D.t_sub, D.t_sub, D.t_train)      # validation, names known in the fit part
    vlate = val & (D.hand >= UNSEEN_FROM_HAND)
    say("validation known-name actions", int(vk.sum()), "| validation actions from hand 11 on", int(vlate.sum()))
    bestg = None
    for ei, edges in enumerate(EDGE_SETS):
        _, n, m = D.ctx(edges, D.t_sub)
        for k in K_GRID:
            for w in W_GRID:
                l = float(ll_full(P0[vk], n[vk], m[vk], D.y[vk], k, w).mean())
                if bestg is None or l < bestg[0]:
                    bestg = (l, ei, k, w)
    _, ei, k, w = bestg
    edges = EDGE_SETS[ei]
    say(f"selected edges {edges}, shrinkage k {k}, in-match weight w {w}: validation known-name loss {bestg[0]:.4f}")
    _, n, m = D.ctx(edges, D.t_sub)
    bi = min(((float(ll_im(P0[vlate], m[vlate], D.y[vlate], q).mean()), q) for q in KIM_GRID))
    kim = bi[1]
    say(f"selected in-match only strength k_im {kim}: validation loss (hand 11 on) {bi[0]:.4f}")
    say("  validation reference on those actions: prior", f"{float(ll_prior(P0[vlate], D.y[vlate]).mean()):.4f}")

    # ---- refit on all training, freeze
    tr = D.mi < D.t_train
    pf, _, _ = train_prior(D.X[fs][tr], D.y[tr], hid, ep)
    C, n, m = D.ctx(edges, D.t_train)
    cnt = D.name_counts(D.t_train)
    keep = np.where(cnt > 0)[0]
    params = dict(pf)
    params.update(edges=np.array(edges, np.float32), names=np.array([D.names[i] for i in keep]),
                  counts=C[keep].astype(np.float32), scalars=np.array([fs, k, w, kim], np.float64))
    os.makedirs(os.path.dirname(os.path.abspath(args.model)), exist_ok=True)
    save_params(args.model, params)
    say("saved", args.model, os.path.getsize(args.model), "bytes;", describe(params))

    # ---- score once on held-out
    P0 = prior_probs(pf, D.X[fs])
    rng = np.random.default_rng(0)
    out = {"sizes": sz, "selected": json.loads(describe(params)), "prior_selection": res, "subsets": {}}
    for label, mask in (("known", kh), ("unseen", uh)):
        s = sz[label]
        y = D.y[mask]
        cols = {
            "uniform": np.full(len(y), np.log(NCLS)),
            "prior": ll_prior(P0[mask], y),
            "prior+in-match": ll_im(P0[mask], m[mask], y, kim),
            "prior+name+in-match": ll_full(P0[mask], n[mask], m[mask], y, k, w),
        }
        if label == "known":
            cols["(extra) prior+name"] = ll_full(P0[mask], n[mask], m[mask], y, k, 0.0)
        r = {"size": s, "loss": {c: float(v.mean()) for c, v in cols.items()}}
        say(f"\n== held-out {label} names: {s['actions']} actions, {s['matches']} matches, {s['names']} names")
        if s["matches"] < M_MIN_MATCHES or s["names"] < M_MIN_NAMES:
            r["status"] = "NOT TESTED"
            say("  NOT TESTED (needs at least", M_MIN_MATCHES, "matches and", M_MIN_NAMES, "names)")
        for c, v in cols.items():
            say(f"  {c:24s} log loss {v.mean():.4f}")
        a, b = (("prior+in-match", "prior+name+in-match") if label == "known" else ("prior", "prior+in-match"))
        gain, ci = bootstrap(D.mi[mask], cols[a], cols[b], rng)
        status = r.get("status") or ("PASS" if ci[0] > 0 else "FAIL")
        r.update(status=status, compare=[a, b], gain=gain, ci95=ci)
        say(f"  acceptance {1 if label == 'known' else 2}: {b} vs {a}: gain {gain:.4f} nats/action, "
            f"95% interval over matches [{ci[0]:.4f}, {ci[1]:.4f}] ({BOOT} resamples; {s['matches']} matches, "
            f"{s['actions']} actions) -> {status}")
        out["subsets"][label] = r

    # ---- runtime path must reproduce the vectorized scores
    rt = OppModel.load(args.model)
    ref_rt = {}
    ref = {}
    for i in np.where((D.mi >= D.t_train))[0]:
        key = (D.mi[i], D.seat[i])
        if key not in ref:
            ref[key] = copy.copy(rt)
            ref[key].start_match(D.names[D.nid[i]])
        mdl = ref[key]
        pr = mdl.predict(D.states[i])
        ref_rt[i] = -np.log(pr[D.y[i]])
        mdl.observe(D.states[i], D.y[i])
    idx = np.array(sorted(ref_rt))
    got = np.array([ref_rt[i] for i in idx])
    kn = cnt[D.nid[idx]] > 0
    want = np.where(kn, ll_full(P0[idx], n[idx], m[idx], D.y[idx], k, w), ll_im(P0[idx], m[idx], D.y[idx], kim))
    err = float(np.abs(got - want).max())
    say(f"\nruntime check: oppmodel.py replay vs vectorized scores on {len(idx)} held-out actions, max abs diff {err:.2e}")
    out["runtime_max_diff"] = err
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "x1_result.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(args.out, "x1_fit.log"), "w") as fh:
        fh.write("\n".join(log) + "\n")


# ---------------------------------------------------------------- bench

def bench(args):
    D = Data(args.data)
    rt = OppModel.load(args.model)
    idx = np.where(D.mi >= D.t_train)[0]
    if args.limit:
        idx = idx[:args.limit]
    inst = {}
    ts = []
    for i in idx:
        key = (D.mi[i], D.seat[i])
        if key not in inst:
            inst[key] = copy.copy(rt)
            inst[key].start_match(D.names[D.nid[i]])
        mdl = inst[key]
        t = time.perf_counter()
        mdl.predict(D.states[i])
        mdl.observe(D.states[i], D.y[i])
        ts.append((time.perf_counter() - t) * 1000.0)
    ts = np.array(ts)
    print(f"bench: {len(ts)} held-out actions in order, update plus prediction: "
          f"p50 {np.percentile(ts, 50):.3f} ms, p99 {np.percentile(ts, 99):.3f} ms, max {ts.max():.3f} ms; "
          f"model file {os.path.getsize(args.model)} bytes (limit 5 MB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("fit", "bench"))
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="logs/x1")
    ap.add_argument("--model", default=os.path.join("rl", "models", "oppmodel.npz"))
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    (fit if a.mode == "fit" else bench)(a)


if __name__ == "__main__":
    main()
