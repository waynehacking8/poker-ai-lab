#!/bin/bash
# S2 (roadmap): the fb2 recipe against a rotating pool of exploiters of the main agent, plus the shover bots.
# Starts the main run, tools/s2_exploiters.sh and tools/s2_screens.sh, waits for all three, and writes
# logs/OUT/end.txt with the reason the run ended: "stop N ..." (logs/OUT/STOP), "crash rc=..." or max-minutes.
#
#   bash tools/rl_s2.sh OUT INIT [MINUTES]        e.g. rl_s2.sh s2 ckpt/fb2/it000900.npz 300
#
# Changes from tools/rl_fb2.sh: --pool-dir pool_OUT with --pool-w 1.0 (the pool holds the 4 newest exploiters,
# x000 is the final ex1), jam and jam_half in the SDK round robin (2 of 8 slots), MINUTES default 300.
set -u
cd ~/poker-ai-lab-rl && . .venv/bin/activate
OUT=$1; INIT=$2; MIN=${3:-300}; POOL=pool_$OUT; L=logs/$OUT
[ -e ckpt/$OUT ] && { echo "ckpt/$OUT exists"; exit 1; }
mkdir -p ckpt/$OUT $L $POOL
[ -e $POOL/x000.npz ] || { cp ckpt/ex1/latest.npz $POOL/x000.npz.part && mv $POOL/x000.npz.part $POOL/x000.npz; }
OPPS=chipzen,ext:ashwing_v2,ext:ashwing_value,jam,chipzen,ext:ashwing_adaptive,ext:autodidact_fast,jam_half
python -m rl.train --out ckpt/$OUT --init $INIT --workers 2 --sdk-workers 10 \
  --sdk-opps $OPPS --heur-batch 10000 --envs 96 --steps 3000 --max-minutes $MIN --lr 1.5e-4 --clip 0.1 \
  --floor 0.15 --snap-w 0.3 --snap-every 25 --clones data/clones.npz --pool-dir $POOL --pool-w 1.0 \
  --opp-w arch:5=4,arch:2=3 --distill data/maniac_labels.npz --distill-w 0.5 >> logs/$OUT.out 2>&1 &
MAIN=$!
echo $MAIN > $L/main.pid
bash tools/s2_exploiters.sh $MAIN ckpt/$OUT $POOL > $L/exploiters.out 2>&1 &
XP=$!
bash tools/s2_screens.sh $MAIN $OUT > $L/screens.out 2>&1 &
SC=$!
wait $MAIN; RC=$?
wait $XP
wait $SC
if [ -f $L/STOP ]; then echo "stop $(cat $L/STOP)"; elif [ $RC -ne 0 ]; then echo "crash rc=$RC"; else echo max-minutes; fi > $L/end.txt
cat $L/end.txt
