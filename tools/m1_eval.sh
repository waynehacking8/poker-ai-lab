#!/bin/bash
# Roadmap M1: wait for the best-response runs, then play fb2-900 and each fine-tune against both targets on
# seed 21 (fresh for all three): 800 matches against ext:ashwing, 400 against the slow ext:autodidact.
# ext: bots are unseeded, so the comparison is unpaired (difference of two proportions).
#
#   bash tools/m1_eval.sh [WORKERS]
# Output: logs/m1/NAME_OPP.jsonl, marker logs/m1/done; a failed eval is listed in logs/m1/failed.
cd ~/poker-ai-lab-rl && . .venv/bin/activate
W=${1:-6}
mkdir -p logs/m1
while pgrep -f "out ckpt/br_" > /dev/null; do sleep 60; done
for m in fb2:rl/models/fb2_it000900.npz br_ashwing:ckpt/br_ashwing/latest.npz br_autofast:ckpt/br_autofast/latest.npz; do
  n=${m%%:*}; f=${m#*:}
  for o in ashwing:800 autodidact:400; do
    opp=${o%%:*}; k=${o#*:}
    python -m rl.eval_arena --model $f --opp ext:$opp --matches $k --seed 21 --workers $W \
      > logs/m1/${n}_$opp.jsonl 2> logs/m1/${n}_$opp.err || echo "${n}_$opp" >> logs/m1/failed
  done
done
touch logs/m1/done
