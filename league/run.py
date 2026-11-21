"""League runner: every entrant plays the field, the per-bot clones, the baselines and
every other external candidate in the real match format.

    python -m league.run --candidates candidates.json --out out/league \
        --field-pairs 150 --bot-pairs 20 --base-pairs 40 --h2h-pairs 60 --workers 4

Matches come in duplicate pairs: one deal seed, both seat assignments.  Every entrant
sees the same deal seeds and the same opponent draws (common random numbers).  Results
append to ``<out>/results.jsonl`` and finished matches are skipped on a rerun.
"""

from __future__ import annotations

import argparse
import atexit
import bisect
import json
import time
import zlib
from collections import OrderedDict
from multiprocessing import Pool
from pathlib import Path

from holdem.engine import MatchConfig, play_match
from holdem.opponents import BASELINES, make_baseline

from .clone import CloneBot, load_model
from .hosting import RemoteBot

GOLDEN = 0.6180339887498949
MAX_HOSTS = 2

_CFG = {}
_HOSTS: OrderedDict = OrderedDict()


def _init(cfg):
    _CFG.update(cfg)
    atexit.register(_close_hosts)


def _close_hosts():
    for h in _HOSTS.values():
        h.close()
    _HOSTS.clear()


def pair_seed(oppkey: str, p: int) -> int:
    return 1000 + zlib.crc32(f"{oppkey}|{p}".encode()) % 900_000


def field_arch(p: int, weights) -> int:
    """Low-discrepancy draw so any prefix of pairs matches the archetype weights."""
    cum, acc = [], 0.0
    for w in weights:
        acc += w
        cum.append(acc)
    return min(bisect.bisect(cum, (p * GOLDEN) % 1.0 * acc), len(weights) - 1)


def get_remote(name: str, seed: int) -> RemoteBot:
    if name in _HOSTS:
        _HOSTS.move_to_end(name)
    else:
        spec = _CFG["candidates"][name]
        _HOSTS[name] = RemoteBot(spec["root"], spec["module"], spec["class"],
                                 _CFG["decision_timeout"])
        while len(_HOSTS) > MAX_HOSTS:
            _HOSTS.popitem(last=False)[1].close()
    host = _HOSTS[name]
    host.new_match(seed)
    return host


def build(kind: str, key: str, seed: int):
    if kind == "cand":
        return get_remote(key, seed)
    if kind == "base":
        return make_baseline(key, seed)
    return CloneBot(f"{kind}:{key}", seed, load_model(_CFG["model"]))


def split(spec: str):
    kind, _, key = spec.partition(":")
    return kind, key


def run_task(task):
    a_spec, opp_spec, p, seat_a = task["a"], task["opp"], task["pair"], task["seat"]
    t0 = time.time()
    seed = pair_seed(task["oppkey"], p)
    a = build(*split(a_spec), seed * 7)
    b = build(*split(opp_spec), seed * 13)
    bots = [None, None]
    bots[seat_a], bots[1 - seat_a] = a, b
    res = play_match(bots, seed, MatchConfig(), strict=False)
    out = {"key": task["key"], "a": a_spec, "opp": opp_spec, "pair": p, "seat_a": seat_a,
           "seed": seed, "hands": res.hands,
           "a_win": 0.5 if res.winner is None else float(res.winner == seat_a),
           "a_chips": res.stacks[seat_a] - 10000, "capped": res.capped,
           "secs": round(time.time() - t0, 2)}
    for tag, bot in (("a", a), ("b", b)):
        if isinstance(bot, RemoteBot):
            out[f"{tag}_err"] = bot.errors
            out[f"{tag}_ms_mean"] = round(sum(bot.ms) / len(bot.ms), 2) if bot.ms else 0
            out[f"{tag}_ms_max"] = round(max(bot.ms), 1) if bot.ms else 0
    return out


def make_tasks(entrants, externals, meta, args):
    """Yield every match task; entrants are spec strings ('cand:x' or 'base:y')."""
    weights = meta["weights_rated"]
    for a in entrants:
        groups = []  # (opponent spec, seed key, pair index)
        for p in range(args.field_pairs):
            groups.append((f"arch:{field_arch(p, weights)}", "field", p))
        for name in meta["bots"]:
            groups += [(f"bot:{name}", f"bot:{name}", p) for p in range(args.bot_pairs)]
        for name in BASELINES:
            if a != f"base:{name}":
                groups += [(f"base:{name}", f"base:{name}", p) for p in range(args.base_pairs)]
        if a in externals:
            for e in externals[externals.index(a) + 1:]:
                if e in entrants:
                    groups += [(e, e, p) for p in range(args.h2h_pairs)]
        for opp, oppkey, p in groups:
            for seat in (0, 1):
                yield {"a": a, "opp": opp, "oppkey": oppkey, "pair": p, "seat": seat,
                       "key": f"{a}|{opp}|{p}|{seat}"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default=None, help="json {name: {root, module, class}}")
    ap.add_argument("--model", default=str(Path(__file__).parent / "data" / "clones.npz"))
    ap.add_argument("--out", default="out/league")
    ap.add_argument("--field-pairs", type=int, default=150)
    ap.add_argument("--bot-pairs", type=int, default=20)
    ap.add_argument("--base-pairs", type=int, default=40)
    ap.add_argument("--h2h-pairs", type=int, default=60)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--decision-timeout", type=float, default=10.0)
    ap.add_argument("--no-baseline-entrants", action="store_true")
    ap.add_argument("--only", default=None, help="comma list of entrant names to run")
    args = ap.parse_args(argv)

    cands = json.loads(Path(args.candidates).read_text()) if args.candidates else {}
    for c in cands.values():
        c["root"] = str(Path(c["root"]).resolve())
    externals = [f"cand:{n}" for n in cands]
    entrants = list(externals)
    if not args.no_baseline_entrants:
        entrants += [f"base:{n}" for n in BASELINES]
    if args.only:
        keep = {s.strip() for s in args.only.split(",")}
        entrants = [e for e in entrants if e.split(":", 1)[1] in keep]
    meta = load_model(args.model).meta
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    results = out / "results.jsonl"
    done = set()
    if results.exists():
        for line in results.read_text().splitlines():
            if line.strip():
                done.add(json.loads(line)["key"])
    tasks = [t for t in make_tasks(entrants, externals, meta, args) if t["key"] not in done]
    print(f"{len(tasks)} matches to play ({len(done)} done)", flush=True)
    cfg = {"candidates": cands, "model": args.model, "decision_timeout": args.decision_timeout}
    t0 = time.time()
    with Pool(args.workers, initializer=_init, initargs=(cfg,)) as pool, \
            results.open("a", buffering=1) as fh:
        for i, row in enumerate(pool.imap_unordered(run_task, tasks, chunksize=1), 1):
            fh.write(json.dumps(row) + "\n")
            if i % 25 == 0:
                rate = i / (time.time() - t0)
                print(f"{i}/{len(tasks)} {rate:.2f} matches/s eta {(len(tasks) - i) / rate / 60:.1f} min",
                      flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
