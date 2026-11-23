#!/bin/bash
# X2s held-out judge (roadmap X2s): fb2-900 with the search off and on, against the six ext: cells and the
# four rule cells, 300 matches each, seed 41 (fresh: the smoke eval and every ablation used seed 31).
# Writes logs/x2s_judge/{off,on}.jsonl (one summary per cell), rows_{off,on}.jsonl, failed, done.
cd "$(dirname "$0")/.." || exit 1
D=logs/x2s_judge
mkdir -p $D
PY=${PY:-$HOME/poker-ai-lab-rl/.venv/bin/python}
CELLS=ext:ashwing,ext:ashwing_search,ext:ashwing_hive,ext:autodidact,ext:wolf,ext:wolf_v5
CELLS=$CELLS,raise_station,sticky_overbettor,tight_sticky,never_fold_pre
for arm in off on; do
  flag=""
  [ $arm = on ] && flag=--search
  OMP_NUM_THREADS=1 nice -n 10 taskset -c ${CORES:-4-19} $PY -m rl.eval_arena \
    --model rl/models/fb2_it000900.npz --matches ${MATCHES:-300} --opp ${OPPS:-$CELLS} --seed 41 \
    --workers ${WORKERS:-16} $flag --rows $D/rows_$arm.jsonl > $D/$arm.jsonl 2> $D/$arm.err || echo $arm >> $D/failed
done
touch $D/done
