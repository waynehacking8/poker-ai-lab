#!/bin/bash
# Gate for the all-in answer (rl/allin.py, roadmap S0): the same policy with the answer (on) and without
# (off, RL_ALLIN=off) on the same seeds, plus how often the answer fires (tools/allin_count.py).
# Results in logs/allin/. The ext: bots are not seeded, so their on and off rows differ by chance; the
# fire counts say whether a difference can come from the answer at all.
#
#   bash tools/allin_gate.sh [MODEL]
cd ~/poker-ai-lab-rl && . .venv/bin/activate
M=${1:-rl/models/fb2_it000900.npz}; L=logs/allin; mkdir -p $L
run() {  # NAME OPPS SEED WORKERS
  python -m rl.eval_arena --model $M --opp $2 --matches 400 --seed $3 --workers $4 --rows $L/$1_on.rows > $L/$1_on.jsonl 2> $L/$1_on.err
  RL_ALLIN=off python -m rl.eval_arena --model $M --opp $2 --matches 400 --seed $3 --workers $4 --rows $L/$1_off.rows > $L/$1_off.jsonl 2> $L/$1_off.err
}
run extremes jam,jam_half,jam_post,minraiser,maniac,station,nit 3 4
run wolf ext:wolf,ext:wolf_v1,ext:wolf_v2,ext:wolf_v5,ext:sdkref,ext:autodidact 3 4
run ashwing ext:ashwing,ext:ashwing_search,ext:ashwing_hive,ext:ashwing_v2 5 4
run h2h policy:$M 3 4
rm -f $L/count_*.log
ALLIN_COUNT_LOG=$L/count_h2h.log python tools/allin_count.py --model $M --opp policy:$M --matches 400 --seed 3 --workers 4 > /dev/null
ALLIN_COUNT_LOG=$L/count_ext.log python tools/allin_count.py --model $M --opp ext:ashwing,ext:ashwing_search,ext:ashwing_hive,ext:ashwing_v2,ext:autodidact --matches 400 --seed 5 --workers 4 > /dev/null
export BP_DATA=$HOME/bp-data BP_RUN=run-pcs-production_opens-to12k-d100-145201-6584 BP_AT=65000 BP_THRESHOLD=0.35 BP_IMAGE=bpopp:v011
run bp100 bp100 3 2
echo DONE > $L/gate.done
