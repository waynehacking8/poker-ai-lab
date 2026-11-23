#!/bin/bash
# S2 (roadmap): the fb2 recipe against a rotating pool of exploiters of the main agent, plus the shover bots.
# Starts the main run, tools/s2_exploiters.sh and tools/s2_screens.sh, waits for all three, and writes
# logs/OUT/end.txt with the reason the run ended: "stop N ..." (logs/OUT/STOP), "crash rc=..." or max-minutes.
#
#   bash tools/rl_s2.sh OUT INIT [MINUTES] [FROM]        e.g. rl_s2.sh s2 ckpt/fb2/it000900.npz 300
#
# FROM (roadmap S2b) resumes a finished S2 run: its state.pt (weights, optimizer, snapshots, win rates and
# iteration; INIT is then unused) and the last 4 files of pool_FROM. New exploiters number on from the last
# copied file, and screens run 400, 800, 1200 and 1600 iterations past the state's, rounded up to 100.
#
# Changes from tools/rl_fb2.sh: --pool-dir pool_OUT with --pool-w 1.0 (the pool holds the 4 newest exploiters,
# x000 is the final ex1), jam and jam_half in the SDK round robin (2 of 8 slots), MINUTES default 300.
set -u
cd ~/poker-ai-lab-rl && . .venv/bin/activate
OUT=$1; INIT=$2; MIN=${3:-300}; FROM=${4:-}; POOL=pool_$OUT; L=logs/$OUT
[ -e ckpt/$OUT ] && { echo "ckpt/$OUT exists"; exit 1; }
START=1; SCREENS="200 400 600"
if [ -n "$FROM" ]; then
  [ -f logs/$FROM/end.txt ] && [ -f ckpt/$FROM/state.pt ] || { echo "$FROM: no logs/$FROM/end.txt or ckpt/$FROM/state.pt"; exit 1; }
  mkdir -p ckpt/$OUT $L $POOL
  cp ckpt/$FROM/state.pt ckpt/$OUT/state.pt.part && mv ckpt/$OUT/state.pt.part ckpt/$OUT/state.pt
  for f in $(ls pool_$FROM/x*.npz | LC_ALL=C sort | tail -n 4); do
    b=$(basename $f); cp $f $POOL/$b.part && mv $POOL/$b.part $POOL/$b
  done
  last=$(ls $POOL | LC_ALL=C sort | tail -n 1); last=${last#x}; last=${last%.npz}
  START=$((10#$last + 1))
  IT0=$(python -c "import sys, torch; print(torch.load(sys.argv[1], weights_only=False)['it'])" ckpt/$OUT/state.pt)
  SCREENS=""
  for d in 400 800 1200 1600; do SCREENS="$SCREENS $(( (IT0 + d + 99) / 100 * 100 ))"; done
  echo "resume $FROM at it $IT0: pool $(ls $POOL | xargs), first cycle $START, screens$SCREENS"
else
  mkdir -p ckpt/$OUT $L $POOL
  [ -e $POOL/x000.npz ] || { cp ckpt/ex1/latest.npz $POOL/x000.npz.part && mv $POOL/x000.npz.part $POOL/x000.npz; }
fi
OPPS=chipzen,ext:ashwing_v2,ext:ashwing_value,jam,chipzen,ext:ashwing_adaptive,ext:autodidact_fast,jam_half
python -m rl.train --out ckpt/$OUT --init $INIT --workers 2 --sdk-workers 10 \
  --sdk-opps $OPPS --heur-batch 10000 --envs 96 --steps 3000 --max-minutes $MIN --lr 1.5e-4 --clip 0.1 \
  --floor 0.15 --snap-w 0.3 --snap-every 25 --clones data/clones.npz --pool-dir $POOL --pool-w 1.0 \
  --opp-w arch:5=4,arch:2=3 --distill data/maniac_labels.npz --distill-w 0.5 >> logs/$OUT.out 2>&1 &
MAIN=$!
echo $MAIN > $L/main.pid
bash tools/s2_exploiters.sh $MAIN ckpt/$OUT $POOL 1000 $START > $L/exploiters.out 2>&1 &
XP=$!
bash tools/s2_screens.sh $MAIN $OUT "$SCREENS" > $L/screens.out 2>&1 &
SC=$!
wait $MAIN; RC=$?
wait $XP
wait $SC
if [ -f $L/STOP ]; then echo "stop $(cat $L/STOP)"; elif [ $RC -ne 0 ]; then echo "crash rc=$RC"; else echo max-minutes; fi > $L/end.txt
cat $L/end.txt
