#!/bin/bash
# Swap acceptance runs of one candidate (roadmap S2b acceptance): three fresh exploit probes (train seeds 2 to 4,
# eval seeds 12 to 14, never the screens' seed 3) and E5, the extreme bots with the all-in answer on as deployed.
# E2 and E4 come from the candidate's eval card (tools/eval_card.sh); E1 is the league gate (league_add.sh).
#
#   bash tools/swap_acc.sh NAME CKPT_NPZ
# Output: logs/swap_acc/NAME/ (probe pool, e5.jsonl), marker logs/swap_acc/NAME/runs_done; a failed step is
# listed in logs/swap_acc/NAME/failed. Two probes run at a time (8 workers each), then the third with E5.
set -u
cd ~/poker-ai-lab-rl && . .venv/bin/activate
NAME=$1; C=$2; D=logs/swap_acc/$NAME
[ -e "$D" ] && { echo "$D exists"; exit 1; }
mkdir -p $D
probe() {  # S
  bash tools/exploit_probe.sh $C $C ${NAME}_f$1 $1 1$1 > $D/probe_f$1.out 2>&1 || echo "probe_f$1" >> $D/failed
}
probe 2 & P2=$!
probe 3 & P3=$!
wait $P2 $P3
probe 4 & P4=$!
python -m rl.eval_arena --model $C --opp jam,jam_half,jam_post,minraiser,station,maniac,nit,random,reference,lag,station_raiser \
  --matches 400 --seed 3 --workers 4 > $D/e5.jsonl 2> $D/e5.err || echo e5 >> $D/failed
wait $P4
python tools/probe_pool.py ${NAME}_f2 ${NAME}_f3 ${NAME}_f4 > $D/probe_pool.txt 2>&1 || echo probe_pool >> $D/failed
touch $D/runs_done
