"""PPO against a population, reward = match outcome (potential shaped by chip share).

    python -m rl.train --out ckpt/run1 --workers 4 --envs 96

Process layout: the main process is the learner and also one of the rollout
workers, so ``--workers 4`` means four busy processes in total.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import time

import numpy as np

import rl  # noqa: F401
from rl.fastenv import BASELINE_IDS, EXT, Pool
from rl.features import D_OBS, NACT

HID = 256
NAMES = {v: k for k, v in BASELINE_IDS.items()}
BASE_W = {"station": 1.0, "maniac": 3.0, "nit": 1.0, "random": 0.5, "reference": 1.0,
          "lag": 3.0, "station_raiser": 3.0}
SNAP_W = 3.0


def init_params(seed=0, hid=HID):
    rng = np.random.default_rng(seed)

    def lin(i, o, gain):
        w = (rng.standard_normal((i, o)) * (gain / np.sqrt(i))).astype(np.float32)
        return w, np.zeros(o, np.float32)

    p = {}
    for pre, out, g in (("p", NACT, 0.01), ("v", 1, 1.0)):
        p[pre + "w0"], p[pre + "b0"] = lin(D_OBS, hid, np.sqrt(2))
        p[pre + "w1"], p[pre + "b1"] = lin(hid, hid, np.sqrt(2))
        p[pre + "w2"], p[pre + "b2"] = lin(hid, out, g)
    return p


def np_forward(p, obs, value=True):
    h = np.maximum(obs @ p["pw0"] + p["pb0"], 0)
    h = np.maximum(h @ p["pw1"] + p["pb1"], 0)
    logits = h @ p["pw2"] + p["pb2"]
    if not value:
        return logits, None
    g = np.maximum(obs @ p["vw0"] + p["vb0"], 0)
    g = np.maximum(g @ p["vw1"] + p["vb1"], 0)
    return logits, (g @ p["vw2"] + p["vb2"])[:, 0]


def sample(logits, mask, rng, greedy=False):
    lg = np.where(mask, logits, -1e9)
    lg = lg - lg.max(1, keepdims=True)
    pr = np.exp(lg)
    pr /= pr.sum(1, keepdims=True)
    if greedy:
        a = pr.argmax(1)
    else:
        c = pr.cumsum(1)
        a = (c < rng.random((len(pr), 1))).sum(1)
        a = np.minimum(a, NACT - 1)
    lp = np.log(np.maximum(pr[np.arange(len(a)), a], 1e-12))
    return a, lp


class Collector:
    def __init__(self, n_envs, seed):
        self.E = n_envs
        self.pool = Pool(n_envs)
        self.rng = np.random.default_rng(seed)
        self.seed = seed * 1000003
        self.opp = [None] * n_envs      # opponent key per env
        self.has_prev = [False] * n_envs
        self.phi_prev = [0.5] * n_envs
        self.started = False
        self.counter = 0

    def _new_match(self, i, weights, n_snaps):
        keys = list(weights.keys())
        w = np.array([weights[k] for k in keys], dtype=np.float64)
        k = keys[self.rng.choice(len(keys), p=w / w.sum())]
        hero = int(self.rng.integers(2))
        if k == "snap":
            slot = int(self.rng.integers(1, n_snaps + 1))
            oc = EXT + slot
        else:
            oc = BASELINE_IDS[k]
        ctrl = [0, 0]
        ctrl[hero] = EXT
        ctrl[1 - hero] = oc
        self.counter += 1
        self.pool.reset(i, self.seed + self.counter, ctrl[0], ctrl[1], hero)
        self.opp[i] = k
        self.has_prev[i] = False
        self.phi_prev[i] = 0.5

    def collect(self, params, snaps, weights, T, greedy=False):
        pol = params
        spol = [None] + list(snaps)
        E = self.E
        allidx = np.arange(E, dtype=np.int32)
        if not self.started:
            for i in range(E):
                self._new_match(i, weights, len(snaps))
            self.started = True
        buf = [dict(o=[], m=[], a=[], lp=[], v=[], r=[], d=[]) for _ in range(E)]
        results = []
        collected = 0

        def finish_done(info):
            for i in np.nonzero(info[:, 0] > 0)[0]:
                phi = info[i, 3]
                if self.has_prev[i]:
                    b = buf[i]
                    b["r"][-1] += phi - self.phi_prev[i]
                    b["d"][-1] = 1.0
                results.append((self.opp[i], 1 if phi == 1.0 else 0, int(info[i, 2])))
                self._new_match(i, weights, len(snaps))

        def act_all(obs, mask, meta, record):
            nonlocal collected
            ctrl = meta[:, 1]
            acts = np.zeros(E, dtype=np.int32)
            for slot in np.unique(ctrl):
                rows = np.nonzero(ctrl == slot)[0]
                if slot == EXT:
                    lg, v = np_forward(pol, obs[rows])
                    a, lp = sample(lg, mask[rows], self.rng, greedy)
                    if record:
                        info = self.pool.info(rows.astype(np.int32))
                        for j, i in enumerate(rows):
                            b = buf[i]
                            phi = info[j, 3]
                            if self.has_prev[i]:
                                b["r"][-1] += phi - self.phi_prev[i]
                            self.phi_prev[i] = phi
                            self.has_prev[i] = True
                            b["o"].append(obs[i]); b["m"].append(mask[i]); b["a"].append(a[j])
                            b["lp"].append(lp[j]); b["v"].append(v[j]); b["r"].append(0.0)
                            b["d"].append(0.0)
                        collected += len(rows)
                    acts[rows] = a
                else:
                    lg, _ = np_forward(spol[slot - EXT], obs[rows], value=False)
                    a, _ = sample(lg, mask[rows], self.rng)
                    acts[rows] = a
            return acts

        while collected < T:
            obs, mask, meta, _ = self.pool.obs(allidx)
            acts = act_all(obs, mask, meta, True)
            self.pool.step(allidx, acts)
            finish_done(self.pool.info(allidx))

        # bring every env to a hero decision so each open step gets reward + bootstrap
        boot = {}
        for _ in range(200):
            obs, mask, meta, _ = self.pool.obs(allidx)
            non_hero = np.nonzero(meta[:, 1] != EXT)[0]
            if len(non_hero) == 0:
                break
            ctrl = meta[:, 1]
            acts = np.zeros(E, dtype=np.int32)
            for slot in np.unique(ctrl[non_hero]):
                rows = np.nonzero(ctrl == slot)[0]
                lg, _ = np_forward(spol[slot - EXT], obs[rows], value=False)
                a, _ = sample(lg, mask[rows], self.rng)
                acts[rows] = a
            self.pool.step(non_hero.astype(np.int32), acts[non_hero])
            finish_done(self.pool.info(allidx))
        obs, mask, meta, _ = self.pool.obs(allidx)
        info = self.pool.info(allidx)
        hero_rows = np.nonzero(meta[:, 1] == EXT)[0]
        if len(hero_rows):
            _, v = np_forward(pol, obs[hero_rows])
            for j, i in enumerate(hero_rows):
                if self.has_prev[i]:
                    buf[i]["r"][-1] += info[i, 3] - self.phi_prev[i]
                    self.phi_prev[i] = info[i, 3]
                    boot[i] = v[j]
                    self.has_prev[i] = False  # next collect starts a fresh trajectory
        # GAE with gamma = 1
        lam = 0.95
        O, M, A, LP, ADV, RET = [], [], [], [], [], []
        for i in range(E):
            b = buf[i]
            n = len(b["r"])
            if n == 0:
                continue
            v = np.array(b["v"], np.float32)
            r = np.array(b["r"], np.float32)
            d = np.array(b["d"], np.float32)
            nxt = np.append(v[1:], boot.get(i, 0.0))
            delta = r + (1 - d) * nxt - v
            adv = np.zeros(n, np.float32)
            g = 0.0
            for t in range(n - 1, -1, -1):
                g = delta[t] + lam * (1 - d[t]) * g
                adv[t] = g
            O.append(np.array(b["o"], np.float32)); M.append(np.array(b["m"], bool))
            A.append(np.array(b["a"], np.int64)); LP.append(np.array(b["lp"], np.float32))
            ADV.append(adv); RET.append(adv + v)
        cat = np.concatenate
        return dict(obs=cat(O), mask=cat(M), act=cat(A), lp=cat(LP), adv=cat(ADV), ret=cat(RET)), results


def worker_main(conn, n_envs, seed):
    col = Collector(n_envs, seed)
    while True:
        msg = conn.recv()
        if msg is None:
            return
        conn.send(col.collect(*msg))


def main():
    import torch
    import torch.nn as nn

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--envs", type=int, default=96)
    ap.add_argument("--steps", type=int, default=6000, help="hero decisions per worker per iteration")
    ap.add_argument("--iters", type=int, default=100000)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--ent", type=float, default=0.01)
    ap.add_argument("--init", default=None)
    ap.add_argument("--snap-every", type=int, default=25)
    ap.add_argument("--max-minutes", type=float, default=1e9)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.set_num_threads(1)

    params = init_params(args.seed)
    if args.init:
        z = np.load(args.init)
        params = {k: z[k] for k in params}
    pnet = nn.Sequential(nn.Linear(D_OBS, HID), nn.ReLU(), nn.Linear(HID, HID), nn.ReLU(), nn.Linear(HID, NACT)).to(dev)
    vnet = nn.Sequential(nn.Linear(D_OBS, HID), nn.ReLU(), nn.Linear(HID, HID), nn.ReLU(), nn.Linear(HID, 1)).to(dev)

    def load_to_torch():
        for net, pre in ((pnet, "p"), (vnet, "v")):
            for li, k in zip((0, 2, 4), (0, 1, 2)):
                net[li].weight.data = torch.from_numpy(params[f"{pre}w{k}"].T.copy()).to(dev)
                net[li].bias.data = torch.from_numpy(params[f"{pre}b{k}"].copy()).to(dev)

    def to_numpy():
        for net, pre in ((pnet, "p"), (vnet, "v")):
            for li, k in zip((0, 2, 4), (0, 1, 2)):
                params[f"{pre}w{k}"] = net[li].weight.data.cpu().numpy().T.copy()
                params[f"{pre}b{k}"] = net[li].bias.data.cpu().numpy().copy()

    load_to_torch()
    opt = torch.optim.Adam(list(pnet.parameters()) + list(vnet.parameters()), lr=args.lr, eps=1e-5)
    state_path = os.path.join(args.out, "state.pt")
    snaps, wr, total_steps, it0 = [], None, 0, 0
    if os.path.exists(state_path):
        st = torch.load(state_path, weights_only=False)
        params, snaps, wr, total_steps, it0 = st["params"], st["snaps"], st["wr"], st["steps"], st["it"]
        load_to_torch()
        opt.load_state_dict(st["opt"])

    ctx = mp.get_context("spawn")
    conns, procs = [], []
    for w in range(args.workers - 1):
        a, b = ctx.Pipe()
        pr = ctx.Process(target=worker_main, args=(b, args.envs, args.seed * 100 + w + 1), daemon=True)
        pr.start()
        conns.append(a); procs.append(pr)
    local = Collector(args.envs, args.seed * 100)

    if wr is None:
        wr = {k: 0.5 for k in BASE_W}
        wr["snap"] = 0.5
    t0 = time.time()
    log = open(os.path.join(args.out, "train.jsonl"), "a")
    window = {k: [0, 0, 0] for k in list(BASE_W) + ["snap"]}
    for it in range(it0 + 1, it0 + args.iters + 1):
        weights = {k: BASE_W[k] * (1 + 2 * max(0.0, 0.9 - wr[k])) for k in BASE_W}
        if snaps:
            weights["snap"] = SNAP_W
        for c in conns:
            c.send((params, snaps, weights, args.steps))
        batches = [local.collect(params, snaps, weights, args.steps)]
        batches += [c.recv() for c in conns]
        results = []
        data = []
        for bt, rs in batches:
            data.append(bt)
            results += rs
        cat = lambda k: np.concatenate([d[k] for d in data])  # noqa: E731
        obs = torch.from_numpy(cat("obs")).to(dev)
        mask = torch.from_numpy(cat("mask")).to(dev)
        act = torch.from_numpy(cat("act")).to(dev)
        olp = torch.from_numpy(cat("lp")).to(dev)
        adv = torch.from_numpy(cat("adv")).to(dev)
        ret = torch.from_numpy(cat("ret")).to(dev)
        adv = (adv - adv.mean()) / (adv.std() + 1e-8)
        n = len(obs)
        total_steps += n
        stats = [0.0, 0.0, 0.0]
        for ep in range(4):
            perm = torch.randperm(n, device=dev)
            for s in range(0, n, 4096):
                ix = perm[s:s + 4096]
                lg = pnet(obs[ix]).masked_fill(~mask[ix], -1e9)
                lsm = torch.log_softmax(lg, 1)
                lp = lsm.gather(1, act[ix][:, None])[:, 0]
                ratio = (lp - olp[ix]).exp()
                a = adv[ix]
                pl = -torch.min(ratio * a, ratio.clamp(0.8, 1.2) * a).mean()
                ent = -(lsm.exp() * lsm.masked_fill(~mask[ix], 0)).sum(1).mean()
                vl = ((vnet(obs[ix])[:, 0] - ret[ix]) ** 2).mean()
                loss = pl + 0.5 * vl - args.ent * ent
                opt.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(list(pnet.parameters()) + list(vnet.parameters()), 0.5)
                opt.step()
                stats = [pl.item(), vl.item(), ent.item()]
        to_numpy()
        for k, w_, h in results:
            window[k][0] += 1
            window[k][1] += w_
            window[k][2] += h
        if it % 5 == 0 or it == 1:
            row = {"it": it, "steps": total_steps, "min": round((time.time() - t0) / 60, 1),
                   "pl": round(stats[0], 4), "vl": round(stats[1], 4), "ent": round(stats[2], 3), "wr": {}}
            for k, (m, wn, h) in window.items():
                if m:
                    row["wr"][k] = [m, round(wn / m, 3)]
                    wr[k] = 0.7 * wr[k] + 0.3 * wn / m
            window = {k: [0, 0, 0] for k in window}
            print(json.dumps(row), flush=True)
            log.write(json.dumps(row) + "\n")
            log.flush()
            np.savez(os.path.join(args.out, "latest.npz"), **params)
        if it % 100 == 0:
            np.savez(os.path.join(args.out, f"it{it:06d}.npz"), **params)
        if it % args.snap_every == 0:
            snaps.append({k: v.copy() for k, v in params.items()})
            snaps = snaps[-6:]
        if (time.time() - t0) / 60 > args.max_minutes:
            break
    np.savez(os.path.join(args.out, "latest.npz"), **params)
    torch.save({"params": params, "snaps": snaps, "wr": wr, "steps": total_steps, "it": it,
                "opt": opt.state_dict()}, state_path)
    for c in conns:
        c.send(None)


if __name__ == "__main__":
    main()
