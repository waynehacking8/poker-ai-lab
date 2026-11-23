#!/bin/bash
# Best-response headroom: fine-tune INIT against SDK field bots only, to measure how much more a policy
# specialized on one opponent wins than INIT does. The C engine side is a small mirror against INIT itself
# (200 decisions per iteration next to a 3000 sample SDK batch), so nearly every update comes from OPPS.
#
#   bash tools/rl_br.sh OUT INIT OPPS [MINUTES] [NSDK]
#
# OPPS: comma separated SDK opponents (ext:<field bot>, chipzen). Busy processes: NSDK plus the learner.
# Run from the box, detached by the caller; log goes to logs/OUT.out. Evaluate with tools/eval_card.sh
# or rl.eval_arena on held-out seeds.
cd ~/poker-ai-lab-rl && . .venv/bin/activate
OUT=$1; INIT=$2; OPPS=$3; MIN=${4:-90}; NSDK=${5:-3}
[ -e ckpt/$OUT ] && { echo "ckpt/$OUT exists"; exit 1; }
mkdir -p ckpt/$OUT logs
exec python -m rl.train --out ckpt/$OUT --init $INIT --workers 1 --sdk-workers $NSDK \
  --sdk-opps $OPPS --heur-batch 3000 --envs 16 --steps 200 --max-minutes $MIN --lr 1.5e-4 --clip 0.1 \
  --fixed-opp $INIT >> logs/$OUT.out 2>&1
