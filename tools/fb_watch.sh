#!/bin/bash
# Screen a run's checkpoints against held-out real field bots, after tools/sp_watch.sh has exported
# them (logs/sp_watch_RUN/itN.policy.npz). 400 matches each, seed 5, SDK engine:
#   validation: ext:ashwing, ext:ashwing_search, ext:ashwing_hive (siblings of the trained Ashwing bots)
#   tracking:   ext:ashwing_v2 (the live Chipzen entry; in the fb1 training set)
# One line per checkpoint in logs/fb_watch_RUN/summary.jsonl. Exits when sp_watch for RUN has exited
# and every exported checkpoint is screened.
#
#   bash tools/fb_watch.sh RUN
cd ~/poker-ai-lab-rl && . .venv/bin/activate
RUN=$1; S=logs/sp_watch_$RUN; W=logs/fb_watch_$RUN; mkdir -p $W
OPPS=${FB_OPPS:-ext:ashwing,ext:ashwing_search,ext:ashwing_hive,ext:ashwing_v2}
while true; do
  alive=0; pgrep -f "sp_watch.sh $RUN" > /dev/null && alive=1
  for m in $(ls $S/it*.policy.npz 2>/dev/null | sort); do
    it=$(basename $m .policy.npz)
    [ -f $S/$it.done ] || continue
    [ -f $W/$it.done ] && continue
    python -m rl.eval_arena --model $m --matches 400 --opp $OPPS --seed 5 --workers 4 > $W/$it.out 2>&1
    python3 - $W $it >> $W/summary.jsonl <<'PY'
import json, sys
w, it = sys.argv[1], sys.argv[2]
rows = [json.loads(l) for l in open(f"{w}/{it}.out") if l.startswith("{")]
print(json.dumps({"it": it, **{r["opponent"]: [r["win_rate"], r["ci95"]] for r in rows}}))
PY
    touch $W/$it.done
  done
  [ $alive -eq 1 ] || break
  sleep 120
done
