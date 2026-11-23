"""Style map: the same playing-style statistics for the real Chipzen field (replays) and for our training and
evaluation opponents (simulated in the SDK engine against one hero), to see which styles the pool covers.

    python tools/style_map.py replays REPLAY_DIR OUT.json [MIN_HANDS]
    python tools/style_map.py sim OPP[,OPP...] HERO_NPZ MATCHES SEED WORKERS OUT.json
    python tools/style_map.py compare FIELD.json POOL.json [POOL2.json ...]

OPP: a holdem/opponents.py name (baselines and extremes), chipzen (the heuristic bot), ext:<field bot>,
model:<npz> (with the all-in answer) or policy:<npz> (without). The C-engine clones are not covered.

Style vector, each in [0, 1]: VPIP and PFR on the first preflop decision (both positions), preflop shove rate
(a raise that commits 90% of the hand-start stack), fold to a preflop raise, post-flop aggression (share of
post-flop actions that bet or raise), post-flop fold to a bet, mean post-flop bet size over the pot before it
(divided by 2, capped at 1), and the showdown rate.
"""
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AXES = ("vpip", "pfr", "shove", "fold_pre_raise", "post_aggr", "post_fold_bet", "bet_size", "showdown")
AGGR = ("raise", "bet", "all_in")


def hand_stats(c, events, target, start_stack, showdown):
    """events: (street, seat, kind, chips added). Counts the target seat's decisions into c."""
    contrib, committed, pot, cur, bb, first = [0, 0], [0, 0], 0, None, 0, True
    for street, seat, kind, added in events:
        if street != cur:
            cur, contrib = street, [0, 0]
        if kind.startswith("post_"):
            if kind == "post_big_blind":
                bb = added
        elif seat == target:
            facing = contrib[1 - seat] > contrib[seat]
            aggr = kind in AGGR and contrib[seat] + added > contrib[1 - seat]
            if street == "preflop":
                if first:
                    first = False
                    c["pre_dec"] += 1
                    c["vpip"] += kind in ("call",) + AGGR
                    c["pfr"] += aggr
                    c["shove"] += aggr and committed[seat] + added >= 0.9 * start_stack
                if facing and contrib[1 - seat] > bb:
                    c["faced_pre_raise"] += 1
                    c["fold_pre_raise"] += kind == "fold"
            else:
                c["post_act"] += 1
                c["post_aggr"] += aggr
                if aggr and pot > 0:
                    c["bet_size_sum"] += min(added / pot, 2.0)
                    c["bet_size_n"] += 1
                if facing:
                    c["post_faced"] += 1
                    c["post_fold_bet"] += kind == "fold"
        pot += added
        contrib[seat] += added
        committed[seat] += added
    c["hands"] += 1
    c["showdown"] += bool(showdown)


def vector(c):
    def r(a, b):
        return c[a] / c[b] if c[b] else None
    bs = r("bet_size_sum", "bet_size_n")
    return {"vpip": r("vpip", "pre_dec"), "pfr": r("pfr", "pre_dec"), "shove": r("shove", "pre_dec"),
            "fold_pre_raise": r("fold_pre_raise", "faced_pre_raise"), "post_aggr": r("post_aggr", "post_act"),
            "post_fold_bet": r("post_fold_bet", "post_faced"), "bet_size": None if bs is None else bs / 2,
            "showdown": r("showdown", "hands"), "hands": c["hands"]}


def replays(directory, out, min_hands=100):
    per = defaultdict(Counter)
    for fn in sorted(os.listdir(directory)):
        if not fn.endswith(".json"):
            continue
        d = json.load(open(os.path.join(directory, fn), encoding="utf-8"))
        if d.get("match", {}).get("game_type") != "poker":
            continue
        for h in d["replay"]["hands"]:
            events = [(st["street"], a["seat"], a["action_type"], a.get("amount") or 0)
                      for st in h["streets"] for a in st["actions"]]
            for s in h["starting_stacks"]:
                hand_stats(per[s["name"]], events, s["seat"], s["starting_stack"], h.get("showdown"))
    res = {n: vector(c) for n, c in per.items() if c["hands"] >= min_hands}
    json.dump(res, open(out, "w"), indent=1)
    print(f"{len(res)} bots with at least {min_hands} hands -> {out}")


class Recorder:
    """Wraps the hero; feeds every finished hand's history into the opponent's counters."""

    def __init__(self, bot, seat, c):
        self.bot, self.seat, self.c, self.stacks = bot, seat, c, None

    def __getattr__(self, k):
        return getattr(self.bot, k)

    def on_round_result(self, message):
        self.bot.on_round_result(message)
        r = message["result"]
        from holdem.engine import MatchConfig
        start = self.stacks or [MatchConfig().starting_stack] * 2
        self.stacks = list(r["stacks"])
        contrib, cur, events = [0, 0], None, []
        for e in r["action_history"]:
            if e["phase"] != cur:
                cur, contrib = e["phase"], [0, 0]
            k, s = e["action"], e["seat"]
            added = e["amount"] - contrib[s] if k in AGGR else e["amount"]
            contrib[s] += added
            events.append((e["phase"], s, k, added))
        op = 1 - self.seat
        hand_stats(self.c, events, op, start[op], r.get("showdown"))


def make_opp(name, seed):
    if name.startswith("ext:"):
        from rl.field_bots import build
        return build(name)
    if name.startswith(("model:", "policy:")):
        from rl.eval_arena import make_policy_opp
        bot = make_policy_opp(os.path.abspath(name.split(":", 1)[1]), 1.0, name.startswith("policy:"))
        bot.set_seed(seed)
        return bot
    if name == "chipzen":
        from bot import HoldemBot
        return HoldemBot(seed=seed)
    from holdem.opponents import make_baseline
    return make_baseline(name, seed)


def sim_one(job):
    import rl  # noqa: F401
    from holdem.engine import MatchConfig, play_match
    from rl.eval_arena import make_hero
    opp_name, hero_npz, seed, seat = job
    c = Counter()
    hero = Recorder(make_hero(os.path.abspath(hero_npz), 1.0, seed * 7 + seat), seat, c)
    opp = make_opp(opp_name, seed * 13 + seat)
    bots = [None, None]
    bots[seat], bots[1 - seat] = hero, opp
    play_match(bots, seed, MatchConfig())
    if hasattr(opp, "close"):
        opp.close()
    return c


def sim(opps, hero_npz, matches, seed, workers, out):
    from multiprocessing import Pool
    res = {}
    with Pool(workers) as pool:
        for name in opps.split(","):
            jobs = [(name, hero_npz, seed * 100000 + k, s) for k in range(matches // 2) for s in (0, 1)]
            tot = Counter()
            for c in pool.map(sim_one, jobs, chunksize=2):
                tot.update(c)
            res[name] = vector(tot)
            print(name, json.dumps(res[name]), flush=True)
    json.dump(res, open(out, "w"), indent=1)


def compare(field_path, pool_paths):
    field = json.load(open(field_path))
    pool = {}
    for p in pool_paths:
        pool.update(json.load(open(p)))

    def vec(v):
        return [v[a] if v[a] is not None else 0.5 for a in AXES]

    def dist(a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5

    print(f"{'field bot':22} {'hands':>5} " + " ".join(f"{a[:7]:>7}" for a in AXES) + "  nearest pool member, distance")
    rows = []
    for n, v in field.items():
        best = min(pool, key=lambda m: dist(vec(v), vec(pool[m])))
        rows.append((dist(vec(v), vec(pool[best])), n, v, best))
    for d, n, v, best in sorted(rows, reverse=True):
        print(f"{n[:22]:22} {v['hands']:>5} " + " ".join(f"{x:7.2f}" for x in vec(v)) + f"  {best} {d:.2f}")
    print()
    print(f"{'pool member':40} " + " ".join(f"{a[:7]:>7}" for a in AXES))
    for m, v in pool.items():
        print(f"{m[-40:]:40} " + " ".join(f"{x:7.2f}" for x in vec(v)))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "replays":
        replays(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 100)
    elif mode == "sim":
        sim(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7])
    elif mode == "compare":
        compare(sys.argv[2], sys.argv[3:])
    else:
        sys.exit(__doc__)
