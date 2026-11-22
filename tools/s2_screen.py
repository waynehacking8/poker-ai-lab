"""One S2 screen verdict (roadmap S2): pool statistics from the main run's train.jsonl since the previous
screen, the exploitability probe and the held-out Ashwing pair, then stop conditions 1 and 2.

    python tools/s2_screen.py OUT ITER PREV_ITER

Writes logs/OUT/screen_itNNNNNN_pool.json and prints it. Exit 0 continue, 11 stop 1 (no gain), 12 stop 1
(under-sampled), 2 stop 2 (field cost); anything else is a failed screen.
"""
import json
import sys

# fb2-900 pooled seed-5 rate minus two standard errors of one 400-match run (roadmap S2, stop condition 2)
TRIPWIRE = {"ext:ashwing": 0.695, "ext:ashwing_search": 0.683}

out, it, prev = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
N = f"{it:06d}"
c_total = pool_m = pool_won = 0.0
per_file, files = {}, []
for line in open(f"ckpt/{out}/train.jsonl"):
    r = json.loads(line)
    if not prev < r["it"] <= it:
        continue
    sdk = {"heuristic" if k == "chipzen" else k for k in r.get("sdk_samples", {})}
    pool = r.get("pool", [])
    files += [nm for nm in pool if nm not in files]
    for k, (m, w) in r["wr"].items():
        if k in sdk or k.startswith("ext:"):
            continue
        c_total += m
        if k.startswith("snap:") and int(k[5:]) <= len(pool):
            f = per_file.setdefault(pool[int(k[5:]) - 1], [0, 0.0])
            f[0] += m
            f[1] += m * w
            pool_m += m
            pool_won += m * w
probe = json.load(open(f"logs/exploit_probe/{out}_it{N}.json"))["eval"]
ash = {d["opponent"]: d["win_rate"] for d in map(json.loads, open(f"logs/{out}/screen_it{N}.jsonl"))}
share = pool_m / c_total if c_total else 0.0
rec = {"it": it, "since": prev, "probe_win_rate": probe["win_rate"], "probe_ci95": probe["ci95"],
       "ashwing": ash, "c_engine_matches": int(c_total), "pool_matches": int(pool_m),
       "pool_share": round(share, 4), "pool_win_rate": round(pool_won / pool_m, 4) if pool_m else None,
       "pool_files": files,
       "per_file": {k: {"matches": int(v[0]), "win_rate": round(v[1] / v[0], 4)} for k, v in per_file.items() if v[0]}}
with open(f"logs/{out}/screen_it{N}_pool.json", "w") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec))
if all(ash[k] < TRIPWIRE[k] for k in TRIPWIRE):
    sys.exit(2)
if it == 400 and probe["win_rate"] >= 0.90:
    sys.exit(12 if share < 0.20 else 11)
sys.exit(0)
