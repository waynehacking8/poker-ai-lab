#!/bin/bash
# Cross-family test of one policy: opponents no fb run trained or selected on. 400 matches each, seed 3
# (the seed of the h4-300 numbers in docs/field_bots.md and research 14.1), SDK engine.
#   field bots: ext:wolf, ext:wolf_v1, ext:wolf_v2, ext:wolf_v5, ext:sdkref, ext:autodidact
#   the real Blueprint 100bb (bp100, isolated Docker; bpopp/scripts/env.sh), 2 workers
# Output: logs/fb_test/NAME.out (one JSON line per opponent).
#
#   bash tools/fb_test.sh MODEL NAME [WORKERS]
cd ~/poker-ai-lab-rl && . .venv/bin/activate
M=$1; N=$2; W=${3:-3}; mkdir -p logs/fb_test
python -m rl.eval_arena --model $M --matches 400 --seed 3 --workers $W \
  --opp ext:wolf,ext:wolf_v1,ext:wolf_v2,ext:wolf_v5,ext:sdkref,ext:autodidact >> logs/fb_test/$N.out 2>&1
export BP_DATA=$HOME/bp-data BP_RUN=run-pcs-production_opens-to12k-d100-145201-6584 BP_AT=65000 \
  BP_THRESHOLD=0.35 BP_IMAGE=bpopp:v010
python -m rl.eval_arena --model $M --matches 400 --seed 3 --workers 2 --opp bp100 >> logs/fb_test/$N.out 2>&1
echo DONE >> logs/fb_test/$N.out
