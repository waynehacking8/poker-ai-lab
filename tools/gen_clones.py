"""Generate perturbed clone opponents for training (domain randomization over the clone family).

    python tools/gen_clones.py data/clones.npz data/clones_gen.npz [N] [SEED]

Keeps the 6 fitted archetypes as arch:0..5 and appends N generated ones as arch:6.. . Each generated
clone mixes two archetypes, then tilts the action logits by a random style: fold (tight or loose),
raise and all-in (aggression), all-in alone (shove tendency), and raise against hand strength (value
heavy or bluff heavy). The tilts have a shared part and a per-street part. Bet sizes come from the
first archetype, scaled by a random factor. The per-bot clones (bot_theta) are copied unchanged so they
stay a held-out family: train without --bot-clones and they are never trained against.
Theta axes: street(4), position(2), facing class(10), stack depth(4), strength bucket(8), action(5)
with actions fold, check, call, raise, all-in.
"""

import json
import sys

import numpy as np

FOLD, CHECK, CALL, RAISE, ALLIN = range(5)


def tilt(theta, rng):
    logit = np.log(np.clip(theta, 1e-6, None))
    zero = theta <= 0
    shared = rng.normal(0, 0.6, 4)
    for s in range(4):
        t = shared + rng.normal(0, 0.3, 4)
        logit[s, ..., FOLD] += t[0]
        logit[s, ..., RAISE] += t[1]
        logit[s, ..., ALLIN] += t[1] + t[2]
        strength = (np.arange(8) - 3.5) / 3.5
        logit[s, :, :, :, :, RAISE] += t[3] * strength[None, None, None, :]
    p = np.exp(logit - logit.max(-1, keepdims=True))
    p[zero] = 0
    return p / p.sum(-1, keepdims=True)


def scale_sizes(table, f):
    return {k: [round(min(max(x * f, 0.1), 4.0), 4) for x in v] for k, v in table.items()}


def main():
    src, dst = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 48
    rng = np.random.default_rng(int(sys.argv[4]) if len(sys.argv) > 4 else 7)
    d = np.load(src, allow_pickle=False)
    meta = json.loads(str(d["meta"]))
    arch, naive = d["arch_theta"].astype(np.float64), d["arch_naive"]
    k = len(arch)
    gen, sizes, names, recipe = [], [], [], []
    for g in range(n):
        a, b = rng.choice(k, 2, replace=False)
        w = rng.uniform(0.2, 0.8)
        th = tilt(w * arch[a] + (1 - w) * arch[b], rng)
        f = float(np.exp(rng.normal(0, 0.35)))
        gen.append(th)
        sizes.append(scale_sizes(meta["arch_sizes"][a], f))
        names.append(f"G{g}-{a}x{b}")
        recipe.append({"a": int(a), "b": int(b), "w": round(float(w), 3), "size_scale": round(f, 3)})
    meta["arch_sizes"] = meta["arch_sizes"] + sizes
    meta["arch_names"] = meta["arch_names"] + names
    meta["generated"] = {"n": n, "first": k, "recipe": recipe}
    np.savez(dst, arch_theta=np.concatenate([arch, np.array(gen)]).astype(np.float32),
             bot_theta=d["bot_theta"], arch_naive=np.concatenate([naive, np.repeat(naive[:1], n, 0)]),
             meta=np.array(json.dumps(meta)))
    print(f"{dst}: {k} fitted + {n} generated archetypes, {len(d['bot_theta'])} held-out bot clones")


if __name__ == "__main__":
    main()
