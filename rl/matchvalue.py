"""Match-value network: P(win the match) from the state at the start of a hand.

Inputs (columns of the policy observation): button, chip share, blind level, hands to the next
level, hand number, final-level flag, and (optionally) the opponent-model statistics.
Trained on simulated matches of the RL policy against the training population; exported as
numpy weights for use as a search leaf (rl/models/match_value.npz).

    python -m rl.matchvalue --model ckpt/adapt/latest.npz --matches 3000 --out rl/models/match_value.npz
"""

from __future__ import annotations

import argparse
import json

import numpy as np

import rl  # noqa: F401
from rl import clones, fastenv
from rl.eval_fast import run_matches
from rl.fastenv import BASELINE_IDS

BASIC = [27, 36, 37, 38, 39, 40]
OPPM = [46, 47, 48, 49, 50, 51, 52, 54, 55]
COLS = BASIC + OPPM
NAMES = ["button", "chip_share", "log_bb", "hands_to_next_level", "hand_no", "final_levels",
         "opp_open_raise", "opp_fold_to_pf_raise", "opp_3bet", "opp_fold_to_bet", "opp_raise_vs_bet",
         "opp_bet_when_checked", "opp_conf", "opp_vpip", "opp_showdown_rate"]


def gather(params, opp_ids, matches, seed):
    X, y, g = [], [], []
    gid = 0
    for name, cid in opp_ids.items():
        rec = []
        run_matches(params, cid, matches, seed + gid, rec=rec, rec_cols=COLS)
        for feats, label, _ in rec:
            X.append(feats)
            y.append(np.full(len(feats), label, dtype=np.float32))
            g.append(np.full(len(feats), gid, dtype=np.int32))
            gid += 1
    return np.concatenate(X), np.concatenate(y), np.concatenate(g)


def forward(p, x):
    h = np.maximum(x @ p["w0"] + p["b0"], 0)
    h = np.maximum(h @ p["w1"] + p["b1"], 0)
    return 1 / (1 + np.exp(-(h @ p["w2"] + p["b2"])[:, 0]))


def fit(X, y, cols, epochs=30, seed=0):
    import torch
    import torch.nn as nn
    torch.manual_seed(seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    Xt = torch.from_numpy(X[:, cols]).to(dev)
    yt = torch.from_numpy(y).to(dev)
    net = nn.Sequential(nn.Linear(len(cols), 64), nn.ReLU(), nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 1)).to(dev)
    opt = torch.optim.Adam(net.parameters(), 2e-3)
    lf = nn.BCEWithLogitsLoss()
    n = len(Xt)
    for ep in range(epochs):
        perm = torch.randperm(n, device=dev)
        for s in range(0, n, 8192):
            ix = perm[s:s + 8192]
            loss = lf(net(Xt[ix])[:, 0], yt[ix])
            opt.zero_grad(); loss.backward(); opt.step()
    p = {f"w{i}": net[2 * i].weight.data.cpu().numpy().T.copy() for i in range(3)}
    p.update({f"b{i}": net[2 * i].bias.data.cpu().numpy().copy() for i in range(3)})
    return p


def metrics(p, X, y, cols):
    q = np.clip(forward(p, X[:, cols]), 1e-6, 1 - 1e-6)
    ll = float(-(y * np.log(q) + (1 - y) * np.log(1 - q)).mean())
    brier = float(((q - y) ** 2).mean())
    order = np.argsort(q)
    ranks = np.empty(len(q)); ranks[order] = np.arange(1, len(q) + 1)
    pos = y > 0.5
    auc = float((ranks[pos].sum() - pos.sum() * (pos.sum() + 1) / 2) / (pos.sum() * (~pos).sum()))
    return {"logloss": round(ll, 4), "brier": round(brier, 4), "auc": round(auc, 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--clones", default="data/clones.npz")
    ap.add_argument("--matches", type=int, default=3000)
    ap.add_argument("--out", default="rl/models/match_value.npz")
    args = ap.parse_args()
    z = np.load(args.model)
    params = {k: z[k] for k in z.files}
    specs = clones.load(args.clones)  # arch 0-5 then the 10 held-out bots
    train_ids = dict(BASELINE_IDS)
    test_ids = {}
    for k, s in enumerate(specs):
        (train_ids if s.startswith("arch") else test_ids)[s] = 200 + k
    X, y, g = gather(params, train_ids, args.matches, 11)
    Xh, yh, _ = gather(params, test_ids, max(args.matches // 3, 300), 12)
    rng = np.random.default_rng(0)
    groups = np.unique(g)
    val = set(rng.choice(groups, len(groups) // 5, replace=False).tolist())
    vm = np.array([x in val for x in g])
    out = {"samples": int(len(X)), "pos_rate": round(float(y.mean()), 3)}
    variants = {"full": list(range(len(COLS))), "no_opponent_model": list(range(len(BASIC))),
                "chip_share_and_level_only": [1, 2]}
    models = {}
    for name, cols in variants.items():
        p = fit(X[~vm], y[~vm], cols)
        models[name] = (p, cols)
        out[name] = {"held_out_matches": metrics(p, X[vm], y[vm], cols),
                     "held_out_bot_clones": metrics(p, Xh, yh, cols)}
    # constant predictor for reference
    c = float(y.mean())
    out["constant"] = {"logloss": round(float(-(y * np.log(c) + (1 - y) * np.log(1 - c)).mean()), 4)}
    p, cols = models["full"]
    p = fit(X, y, list(range(len(COLS))))
    np.savez(args.out, columns=np.array(COLS), names=np.array(NAMES), **p)
    print(json.dumps(out, indent=1))


def predict(path, feats):
    """Match-win probability for rows of the 15 input features (order of NAMES)."""
    z = np.load(path)
    return forward({k: z[k] for k in z.files if k[0] in "wb"}, np.asarray(feats, dtype=np.float32))


if __name__ == "__main__":
    main()
