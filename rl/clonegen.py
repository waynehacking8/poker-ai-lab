"""Generated clone opponents: mixes of fitted archetypes with random style tilts (tools/gen_clones.py,
tools/adv_clones.py). Theta axes: street(4), position(2), facing class(10), stack depth(4),
strength bucket(8), action(5) with actions fold, check, call, raise, all-in."""

from __future__ import annotations

import json

import numpy as np

FOLD, CHECK, CALL, RAISE, ALLIN = range(5)


def tilt(theta, rng, scale=1.0):
    """Random style tilt of a theta table: fold, aggression, shove, and raise against hand strength."""
    logit = np.log(np.clip(theta, 1e-6, None))
    zero = theta <= 0
    shared = rng.normal(0, 0.6 * scale, 4)
    strength = (np.arange(8) - 3.5) / 3.5
    for s in range(4):
        t = shared + rng.normal(0, 0.3 * scale, 4)
        logit[s, ..., FOLD] += t[0]
        logit[s, ..., RAISE] += t[1]
        logit[s, ..., ALLIN] += t[1] + t[2]
        logit[s, :, :, :, :, RAISE] += t[3] * strength[None, None, None, :]
    p = np.exp(logit - logit.max(-1, keepdims=True))
    p[zero] = 0
    return p / p.sum(-1, keepdims=True)


def scale_sizes(table, f):
    return {k: [round(min(max(x * f, 0.1), 4.0), 4) for x in v] for k, v in table.items()}


def sample(arch, arch_sizes, rng):
    """One generated clone from the fitted archetypes: (theta, sizes, recipe)."""
    a, b = rng.choice(len(arch), 2, replace=False)
    w = rng.uniform(0.2, 0.8)
    th = tilt(w * arch[a] + (1 - w) * arch[b], rng)
    f = float(np.exp(rng.normal(0, 0.35)))
    return th, scale_sizes(arch_sizes[a], f), {"a": int(a), "b": int(b), "w": round(float(w), 3),
                                               "size_scale": round(f, 3)}


def mutate(theta, sizes, recipe, rng, scale=0.5):
    """A child of a generated clone: a smaller extra tilt and a small change of bet sizes."""
    f = float(np.exp(rng.normal(0, 0.15)))
    r = dict(recipe, size_scale=round(recipe["size_scale"] * f, 3), gen=recipe.get("gen", 0) + 1)
    return tilt(theta, rng, scale), scale_sizes(sizes, f), r


def write(path, base, thetas, sizes, recipes, extra=None):
    """Save the fitted archetypes plus generated ones as a clones file (arch:6 and up are generated)."""
    d = np.load(base, allow_pickle=False)
    meta = json.loads(str(d["meta"]))
    arch, naive = d["arch_theta"], d["arch_naive"]
    k, n = len(arch), len(thetas)
    meta["arch_sizes"] = meta["arch_sizes"][:k] + list(sizes)
    meta["arch_names"] = meta["arch_names"][:k] + [f"G{i}" for i in range(n)]
    meta["generated"] = {"n": n, "first": k, "recipe": list(recipes), **(extra or {})}
    theta = np.concatenate([arch, np.array(thetas, dtype=np.float32)]) if n else arch
    np.savez(path, arch_theta=theta, bot_theta=d["bot_theta"],
             arch_naive=np.concatenate([naive, np.repeat(naive[:1], n, 0)]),
             meta=np.array(json.dumps(meta)))
