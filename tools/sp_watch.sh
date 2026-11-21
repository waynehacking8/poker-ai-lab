#!/bin/bash
# Screen the checkpoints of one run as they land, every EVERY iterations: the 23 league opponents (fast
# engine, 400 each, seed 21), the heuristic bot (SDK engine, 400, seed 1), and two earlier policies head
# to head in the SDK engine (400 each, seed 3): h4-300, the shipped bot, and rl-17cf03f, which beats it.
# One line per checkpoint in logs/sp_watch_RUN/summary.jsonl. Exits when the run has stopped and every
# checkpoint is screened. Screening only: a pick needs a fresh-seed confirmation.
#
#   bash tools/sp_watch.sh RUN [EVERY]
cd ~/poker-ai-lab-rl && . .venv/bin/activate
RUN=$1; EVERY=${2:-100}; W=logs/sp_watch_$RUN; mkdir -p $W
H4=rl/models/h4_it000300.npz; R17=rl/models/best.npz
while true; do
  alive=0; pgrep -f "rl.train --out ckpt/$RUN " > /dev/null && alive=1
  for f in $(ls ckpt/$RUN/it*.npz 2>/dev/null | sort); do
    it=$(basename $f .npz); n=$((10#${it#it}))
    [ $((n % EVERY)) -eq 0 ] || continue
    [ -f $W/$it.done ] && continue
    m=$W/$it.policy.npz
    python -m rl.export $f $m > $W/$it.export 2>&1
    python -m rl.eval_fast --model $f --matches 400 --clones data/clones.npz --seed 21 > $W/$it.fast 2>&1
    python -m rl.eval_arena --model $m --matches 400 --opp chipzen --workers 4 > $W/$it.heur 2>&1
    python -m rl.eval_arena --model $m --matches 400 --opp model:$H4,model:$R17 --seed 3 --workers 4 > $W/$it.h2h 2>&1
    python3 - $W $it >> $W/summary.jsonl <<'PY'
import json, sys
w, it = sys.argv[1], sys.argv[2]
rows = [json.loads(l) for l in open(f"{w}/{it}.fast") if l.startswith("{")]
wr = sorted(((x.get("opponent") or x.get("opp")), round(x["wins"] / x["matches"], 3)) for x in rows)
h = [json.loads(l) for l in open(f"{w}/{it}.heur") if l.startswith("{")][-1]
hh = [json.loads(l) for l in open(f"{w}/{it}.h2h") if l.startswith("{")]
low = sorted(wr, key=lambda t: t[1])[:3]
print(json.dumps({"it": it, "n_opp": len(wr), "min23": low, "below80": sum(v < 0.8 for _, v in wr),
                  "field": round(sum(v for _, v in wr) / max(len(wr), 1), 3),
                  "heur": h["win_rate"], "vs_h4_300": hh[0]["win_rate"], "vs_h4_300_ci": hh[0]["ci95"],
                  "vs_rl17": hh[1]["win_rate"], "vs_rl17_ci": hh[1]["ci95"]}))
PY
    touch $W/$it.done
  done
  [ $alive -eq 1 ] || break
  sleep 120
done
