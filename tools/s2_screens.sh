#!/bin/bash
# S2 screens at main iterations 200, 400 and 600, and on the last checkpoint when the run ends without a stop:
# the exploitability probe (logs/exploit_probe/OUT_itN.json), held-out ext:ashwing and ext:ashwing_search
# (logs/OUT/screen_itN.jsonl) and the pool statistics (logs/OUT/screen_itN_pool.json). tools/s2_screen.py
# applies stop conditions 1 and 2; on a stop this writes logs/OUT/STOP and kills the main run.
#
#   bash tools/s2_screens.sh MAIN_PID OUT
set -u
cd ~/poker-ai-lab-rl && . .venv/bin/activate
MAIN=$1; OUT=$2; C=ckpt/$OUT; L=logs/$OUT; prev=0
mkdir -p $L
stopit() { echo "$(date -u +%FT%TZ) STOP $1"; echo "$1" > $L/STOP; kill $MAIN 2>/dev/null; exit 0; }
screen() {  # ITER
  local N ck
  N=$(printf %06d $1); ck=$C/it$N.npz
  for try in 1 2 3 4 5 6; do
    python -c "import numpy as np, sys; z = np.load(sys.argv[1]); assert 'vw0' in z.files" $ck 2>/dev/null && break
    sleep 10
  done
  echo "$(date -u +%FT%TZ) screen it$N"
  bash tools/exploit_probe.sh $ck $ck ${OUT}_it$N 1 3 > $L/probe_it$N.out 2>&1
  python -m rl.eval_arena --model $ck --opp ext:ashwing,ext:ashwing_search --matches 400 --seed 5 --workers 4 \
    > $L/screen_it$N.jsonl 2> $L/screen_it$N.err
  python tools/s2_screen.py $OUT $1 $prev > $L/screen_it$N.verdict 2>&1
  case $? in
    0) ;;
    11) stopit "1 no gain at it$N" ;;
    12) stopit "1 under-sampled at it$N" ;;
    2) stopit "2 field cost at it$N" ;;
    *) stopit "3 screen it$N failed, see $L/screen_it$N.verdict" ;;
  esac
  prev=$1
}
for it in 200 400 600; do
  while [ ! -f $C/it$(printf %06d $it).npz ]; do
    [ -f $L/STOP ] && exit 0
    kill -0 $MAIN 2>/dev/null || break 2
    sleep 30
  done
  screen $it
done
while kill -0 $MAIN 2>/dev/null; do sleep 30; done
[ -f $L/STOP ] && exit 0
last=$(ls $C/it*.npz 2>/dev/null | sed 's/.*it0*\([0-9]*\)\.npz/\1/' | sort -n | tail -n 1)
[ -n "$last" ] && [ "$last" -gt "$prev" ] && screen $last
exit 0
