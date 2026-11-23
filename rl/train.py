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
from rl.features import D_OBS, NACT, load_priors

HID = 256
NAMES = {v: k for k, v in BASELINE_IDS.items()}
BASE_W = {"station": 1.0, "maniac": 3.0, "nit": 1.0, "random": 0.5, "reference": 1.0,
          "lag": 3.0, "station_raiser": 3.0}
SNAP_W = 3.0
CLONE_IDS = {}   # spec -> controller id (200 + k), filled when --clones is given


def install_clones(path, bots=False):
    from rl import clones
    CLONE_IDS.clear()
    for k, spec in enumerate(clones.load(path, bots=None if bots else [])):
        CLONE_IDS[spec] = 200 + k


def init_params(seed=0, hid=HID, no_hist=False):
    rng = np.random.default_rng(seed)

    def lin(i, o, gain):
        w = (rng.standard_normal((i, o)) * (gain / np.sqrt(i))).astype(np.float32)
        return w, np.zeros(o, np.float32)

    p = {}
    for pre, out, g in (("p", NACT, 0.01), ("v", 1, 1.0)):
        p[pre + "w0"], p[pre + "b0"] = lin(D_OBS, hid, np.sqrt(2))
        p[pre + "w1"], p[pre + "b1"] = lin(hid, hid, np.sqrt(2))
        p[pre + "w2"], p[pre + "b2"] = lin(hid, out, g)
    if no_hist:
        keep = np.ones(D_OBS, np.float32)
        keep[STAT_COLS] = 0
        p["keep"] = keep
    return p


STAT_COLS = list(range(46, 53)) + [54, 55]


def np_forward(p, obs, value=True):
    if "keep" in p:
        obs = obs * p["keep"]
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
    def __init__(self, n_envs, seed, profiles=None):
        """profiles: {name: NST counts} (--seed-profiles); a bot:NAME opponent with an entry is seen by the hero
        through those counts at match start."""
        self.profiles = profiles
        self.E = n_envs
        self.pool = Pool(n_envs)
        self.rng = np.random.default_rng(seed)
        self.seed = seed * 1000003
        self.opp = [None] * n_envs      # opponent key per env
        self.opp_id = [None] * n_envs   # with ids: the pool file behind that key when the match started
        self.ids = None
        self.has_prev = [False] * n_envs
        self.phi_prev = [0.5] * n_envs
        self.started = False
        self.counter = 0

    def _new_match(self, i, weights, n_snaps):
        keys = list(weights.keys())
        w = np.array([weights[k] for k in keys], dtype=np.float64)
        k = keys[self.rng.choice(len(keys), p=w / w.sum())]
        hero = int(self.rng.integers(2))
        if k.startswith("snap:"):
            oc = EXT + int(k[5:])
        elif k in CLONE_IDS:
            oc = CLONE_IDS[k]
        else:
            oc = BASELINE_IDS[k]
        ctrl = [0, 0]
        ctrl[hero] = EXT
        ctrl[1 - hero] = oc
        self.counter += 1
        if self.profiles is not None:
            prof = self.profiles.get(k[4:]) if k.startswith("bot:") else None
            self.pool.set_prior(i, hero, prof)
            self.pool.set_prior(i, 1 - hero, None)
        self.pool.reset(i, self.seed + self.counter, ctrl[0], ctrl[1], hero)
        self.opp[i] = k
        if self.ids is not None and k.startswith("snap:"):
            self.opp_id[i] = self.ids[int(k[5:]) - 1]
        self.has_prev[i] = False
        self.phi_prev[i] = 0.5

    def _obs(self, idx, pol):
        obs, mask, meta, amts = self.pool.obs(idx)
        if "keep" in pol:
            obs = obs * pol["keep"]
        return obs, mask, meta, amts

    def collect(self, params, snaps, weights, T, greedy=False, ids=None):
        """ids (optional): one identity per snaps entry, the pool file name or None. A match whose snap:j
        slot now holds another identity is restarted unreported, so no result spans two pool files."""
        pol = params
        spol = [None] + list(snaps)
        E = self.E
        allidx = np.arange(E, dtype=np.int32)
        self.ids = ids
        if not self.started:
            for i in range(E):
                self._new_match(i, weights, len(snaps))
            self.started = True
        elif ids is not None:
            # the previous collect ended every open trajectory with a bootstrap, so a restart loses no step
            for i in range(E):
                if self.opp[i].startswith("snap:"):
                    j = int(self.opp[i][5:]) - 1
                    if j >= len(ids) or ids[j] != self.opp_id[i]:
                        self._new_match(i, weights, len(snaps))
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
            obs, mask, meta, _ = self._obs(allidx, pol)
            acts = act_all(obs, mask, meta, True)
            self.pool.step(allidx, acts)
            finish_done(self.pool.info(allidx))

        # bring every env to a hero decision so each open step gets reward + bootstrap
        boot = {}
        for _ in range(200):
            obs, mask, meta, _ = self._obs(allidx, pol)
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
        obs, mask, meta, _ = self._obs(allidx, pol)
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


def worker_main(conn, n_envs, seed, clones_path=None, bots=False, profiles_path=None):
    if clones_path:
        install_clones(clones_path, bots)
    col = Collector(n_envs, seed, load_priors(profiles_path) if profiles_path else None)
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
    ap.add_argument("--snap-window", type=int, default=6, help="past snapshots kept in the pool (ML-Agents window)")
    ap.add_argument("--max-minutes", type=float, default=1e9)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--clones", default=None)
    ap.add_argument("--pool-dir", default=None, help="extra opponents (exploiter checkpoints, *.npz)")
    ap.add_argument("--fixed-opp", default=None, help="exploiter mode: train only against this model (re-read every 20 its)")
    ap.add_argument("--clip", type=float, default=0.2, help="PPO clip range")
    ap.add_argument("--floor", type=float, default=0.15, help="PFSP floor: weight = w0 * (floor + (1 - winrate)^2)")
    ap.add_argument("--snap-w", type=float, default=0.3, help="base weight of each past snapshot / pool entry")
    ap.add_argument("--pool-w", type=float, default=None, help="base weight of each --pool-dir entry (default: --snap-w)")
    ap.add_argument("--no-hist", action="store_true", help="hide the in-match opponent statistics")
    ap.add_argument("--only", default=None, help="train against these opponent keys only (comma separated)")
    ap.add_argument("--sdk-workers", type=int, default=0, help="extra busy processes playing the heuristic HoldemBot in the SDK engine")
    ap.add_argument("--sdk-opps", default="chipzen", help="SDK opponents for the sdk workers, comma separated: chipzen (heuristic) and ext:<field bot>; round robin per worker")
    ap.add_argument("--heur-batch", type=int, default=3000, help="heuristic samples to wait for before each PPO update")
    ap.add_argument("--opp-w", default=None, help="base weight overrides, comma separated key=w (e.g. arch:5=4)")
    ap.add_argument("--skip", default=None, help="drop these opponent keys from the PFSP pool (comma separated, e.g. arch:1)")
    ap.add_argument("--distill", default=None, help="teacher labels npz from rl.teacher (obs, mask, label)")
    ap.add_argument("--distill-w", type=float, default=0.0, help="weight of the cross entropy toward the teacher action")
    ap.add_argument("--seed-profiles", default=None, metavar="PATH",
                    help="profile table (tools/tracker_profiles.py): a bot:NAME opponent with an entry starts the hero's counts from it")
    ap.add_argument("--bot-clones", action="store_true", help="also train on the per-bot clones (default: held out)")
    ap.add_argument("--gen-w", type=float, default=None,
                    help="base weight of generated archetypes (arch:6 and up, from tools/gen_clones.py)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.set_num_threads(1)

    params = init_params(args.seed, no_hist=args.no_hist)
    if args.init:
        z = np.load(args.init)
        params = {k: z[k] for k in z.files}
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
    snaps, wr, total_steps, it0, pool_wr = [], None, 0, 0, {}
    if os.path.exists(state_path):
        st = torch.load(state_path, weights_only=False)
        params, snaps, wr, total_steps, it0 = st["params"], st["snaps"], st["wr"], st["steps"], st["it"]
        pool_wr = st.get("pool_wr", {})
        load_to_torch()
        opt.load_state_dict(st["opt"])

    ctx = mp.get_context("spawn")
    conns, procs = [], []
    for w in range(args.workers - 1):
        a, b = ctx.Pipe()
        pr = ctx.Process(target=worker_main, args=(b, args.envs, args.seed * 100 + w + 1, args.clones, args.bot_clones, args.seed_profiles), daemon=True)
        pr.start()
        conns.append(a); procs.append(pr)
    sdk, sdk_path = [], None
    if args.sdk_workers:
        from rl.sdk_rollout import publish_params, sdk_worker_main
        sdk_path = os.path.join(args.out, "sdk_params.npz")
        publish_params(params, sdk_path)
        for w in range(args.sdk_workers):
            a, b = ctx.Pipe()
            pr = ctx.Process(target=sdk_worker_main, args=(b, args.seed * 100 + 50 + w, sdk_path, tuple(args.sdk_opps.split(",")), w), daemon=True)
            pr.start()
            sdk.append(a)
            procs.append(pr)
    if args.clones:
        install_clones(args.clones, args.bot_clones)
    local = Collector(args.envs, args.seed * 100, load_priors(args.seed_profiles) if args.seed_profiles else None)
    base_w = dict(BASE_W)
    for spec in CLONE_IDS:
        base_w[spec] = 1.5 if spec.startswith("arch") else 0.5
        if args.gen_w is not None and spec.startswith("arch:") and int(spec[5:]) >= 6:
            base_w[spec] = args.gen_w
    if args.opp_w:
        for kv in args.opp_w.split(","):
            k, v = kv.rsplit("=", 1)
            base_w[k] = float(v)
    if args.skip:
        base_w = {k: v for k, v in base_w.items() if k not in args.skip.split(",")}
    if args.only:
        keep_keys = args.only.split(",")
        base_w = {k: v for k, v in base_w.items() if k in keep_keys}

    import glob
    if wr is None:
        wr = {}
    for k in list(BASE_W) + list(CLONE_IDS):
        wr.setdefault(k, 0.5)
    dist = None
    if args.distill and args.distill_w > 0:
        z = np.load(args.distill)
        dist = [torch.from_numpy(z[k]).to(dev) for k in ("obs", "mask", "label")]
    dstat = [0.0, 0.0]
    t0 = time.time()
    log = open(os.path.join(args.out, "train.jsonl"), "a")
    from collections import defaultdict
    window = defaultdict(lambda: [0, 0, 0])
    sdk_buf = []
    sdk_n = {}
    ext, ext_names = [], []
    pool_w = args.snap_w if args.pool_w is None else args.pool_w
    for it in range(it0 + 1, it0 + args.iters + 1):
        # the pool changes only right after a log row, so each row's window has one file per snap:j key
        if args.pool_dir and (it == it0 + 1 or it % 10 == 1):
            files = sorted(glob.glob(os.path.join(args.pool_dir, "*.npz")))[-4:]
            names = [os.path.basename(f) for f in files]
            if names != ext_names:
                # pool entries keep their win rate per file while their snap:j position moves
                for j, nm in enumerate(ext_names, 1):
                    pool_wr[nm] = wr.get(f"snap:{j}", 0.5)
                ext, ext_names = [dict(np.load(f)) for f in files], names
                for j, nm in enumerate(ext_names, 1):
                    wr[f"snap:{j}"] = pool_wr.get(nm, 0.5)
        if args.fixed_opp and (it == it0 + 1 or it % 20 == 0):
            ext = [dict(np.load(args.fixed_opp))]
        # pool entries first, so their snap:j keys do not move as the snapshot window fills
        opp_models = ext + ([] if args.fixed_opp else snaps)
        # league sampling: prioritized fictitious self-play, opponents that beat us more are drawn more
        pf = lambda k, w0: w0 * (args.floor + (1.0 - wr.setdefault(k, 0.5)) ** 2)  # noqa: E731
        if args.fixed_opp:
            weights = {"snap:1": 1.0}
        else:
            weights = {k: pf(k, w0) * 4 for k, w0 in base_w.items()}
            for j in range(1, len(opp_models) + 1):
                weights[f"snap:{j}"] = pf(f"snap:{j}", pool_w if j <= len(ext) else args.snap_w) * 4
        # pool slots carry their file name, so a match in progress at a rotation is restarted, not misfiled
        ids = ext_names + [None] * len(snaps) if args.pool_dir and not args.fixed_opp else None
        for c in conns:
            c.send((params, opp_models, weights, args.steps, False, ids))
        if sdk:
            publish_params(params, sdk_path)
        batches = [local.collect(params, opp_models, weights, args.steps, False, ids)]
        batches += [c.recv() for c in conns]
        if sdk:
            nh = 0
            while True:
                for c in sdk:
                    while c.poll():
                        b, won, hands, oname = c.recv()
                        if b is not None:
                            sdk_buf.append((b, [("heuristic" if oname == "chipzen" else oname, 1 if won else 0, int(hands))]))
                            nh += len(b["obs"])
                            sdk_n[oname] = sdk_n.get(oname, 0) + len(b["obs"])
                if nh >= args.heur_batch:
                    break
                time.sleep(0.2)
            batches += sdk_buf
            sdk_buf = []
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
                pl = -torch.min(ratio * a, ratio.clamp(1 - args.clip, 1 + args.clip) * a).mean()
                ent = -(lsm.exp() * lsm.masked_fill(~mask[ix], 0)).sum(1).mean()
                vl = ((vnet(obs[ix])[:, 0] - ret[ix]) ** 2).mean()
                loss = pl + 0.5 * vl - args.ent * ent
                if dist is not None:
                    di = torch.randint(0, len(dist[0]), (1024,), device=dev)
                    dl = pnet(dist[0][di]).masked_fill(~dist[1][di], -1e9)
                    dce = nn.functional.cross_entropy(dl, dist[2][di])
                    loss = loss + args.distill_w * dce
                    dstat = [dce.item(), (dl.argmax(1) == dist[2][di]).float().mean().item()]
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
        if it % 5 == 0 or it == 1 or (args.sdk_opps != "chipzen" and it == it0 + args.iters):
            row = {"it": it, "steps": total_steps, "min": round((time.time() - t0) / 60, 1),
                   "pl": round(stats[0], 4), "vl": round(stats[1], 4), "ent": round(stats[2], 3), "wr": {}}
            if args.sdk_opps != "chipzen":
                row["sdk_samples"] = dict(sdk_n)
            if args.pool_dir:
                row["pool"] = ext_names
            if dist is not None:
                row["distill_ce"], row["distill_acc"] = round(dstat[0], 3), round(dstat[1], 3)
            for k, (m, wn, h) in window.items():
                if m:
                    row["wr"][k] = [m, round(wn / m, 3)]
                    wr[k] = 0.7 * wr.setdefault(k, 0.5) + 0.3 * wn / m
            window = defaultdict(lambda: [0, 0, 0])
            print(json.dumps(row), flush=True)
            log.write(json.dumps(row) + "\n")
            log.flush()
            np.savez(os.path.join(args.out, "latest.npz"), **params)
        if it % 100 == 0:
            np.savez(os.path.join(args.out, f"it{it:06d}.npz"), **params)
        if it % args.snap_every == 0:
            snaps.append({k: v.copy() for k, v in params.items()})
            snaps = snaps[-args.snap_window:]
        if (time.time() - t0) / 60 > args.max_minutes:
            break
    np.savez(os.path.join(args.out, "latest.npz"), **params)
    pool_wr.update({nm: wr.get(f"snap:{j}", 0.5) for j, nm in enumerate(ext_names, 1)})
    torch.save({"params": params, "snaps": snaps, "wr": wr, "steps": total_steps, "it": it,
                "opt": opt.state_dict(), "pool_wr": pool_wr}, state_path)
    for c in conns + sdk:
        c.send(None)


if __name__ == "__main__":
    main()
