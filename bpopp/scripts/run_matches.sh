#!/bin/bash
source ~/poker-ai-lab-bp/src/bpopp/scripts/env.sh
OUT=~/bp-logs; mkdir -p $OUT
( while :; do docker stats --no-stream --format '{{.Name}} {{.MemUsage}} {{.CPUPerc}}' $(docker ps -q --filter name=bpopp-) >> $OUT/mem.txt 2>/dev/null; sleep 5; done ) &
SAMPLER=$!
clean() { docker ps -q --filter name=bpopp- | xargs -r docker kill > /dev/null 2>&1; }
trap 'kill $SAMPLER; clean' EXIT
export BP_LOG=$OUT/smoke; rm -rf $BP_LOG; mkdir -p $BP_LOG
for o in random lag; do
  $PY -m rl.eval_arena --hero bp100 --opp $o --matches 20 --seed 3 --workers 2 2>&1 | tail -3 | tee -a $OUT/results.txt
  clean
done
echo SMOKEDONE | tee -a $OUT/results.txt
run() { # name, args...
  name=$1; shift
  export BP_LOG=$OUT/$name; rm -rf $BP_LOG; mkdir -p $BP_LOG
  echo "== $name" | tee -a $OUT/results.txt
  $PY -m rl.eval_arena "$@" --opp bp100 --matches 400 --seed 3 --workers 4 2>&1 | tail -3 | tee -a $OUT/results.txt
  clean
}
run h4_300 --model rl/models/h4_it000300.npz
run h4_900 --model rl/models/h4_it000900.npz
run heur --hero chipzen
echo ALLDONE | tee -a $OUT/results.txt
