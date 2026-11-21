#!/bin/bash
# Long run: PPO against the 23 league opponents (C env, with ManiacBR distillation) plus the heuristic HoldemBot
# played in the SDK engine by dedicated workers. Resumable: rerun the same command, state.pt is reloaded.
#
#   bash tools/rl_heur_long.sh [OUT] [NC] [NSDK] [MINUTES] [INIT] [CLONES]
#
# Busy processes = NC (C workers, the learner is one of them) + NSDK (heuristic workers).
# Default 4 processes: NC=1 NSDK=3. After more cores free up: NC=2 NSDK=5.
# Run from the box, detached by the caller; log goes to logs/OUT.out.
cd ~/poker-ai-lab-rl && . .venv/bin/activate
OUT=${1:-heur2}; NC=${2:-1}; NSDK=${3:-3}; MIN=${4:-360}; INIT=${5:-ckpt/heur1/latest.npz}; CLONES=${6:-data/clones.npz}
mkdir -p ckpt/$OUT logs pool_fixed
[ -f pool_fixed/a_ablA.npz ] || cp ckpt/ablA/latest.npz pool_fixed/a_ablA.npz
[ -f pool_fixed/b_distill1.npz ] || cp ckpt/distill1/latest.npz pool_fixed/b_distill1.npz
exec python -m rl.train --out ckpt/$OUT --init $INIT --workers $NC --sdk-workers $NSDK --heur-batch $((1000 * NSDK)) \
  --envs 96 --steps 4000 --max-minutes $MIN --lr 1.5e-4 --clip 0.1 --floor 0.15 --snap-w 0.3 \
  --clones $CLONES --pool-dir pool_fixed --distill data/maniac_labels.npz --distill-w 0.5 >> logs/$OUT.out 2>&1
