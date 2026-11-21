#!/bin/bash
# Self-play test. Same recipe as rl_heur_long.sh (C env league, heuristic HoldemBot in SDK workers,
# ManiacBR distillation), but past snapshots weigh SNAP_W (heur4 used 0.3) and are taken every 10
# iterations (heur4: 25), and the fixed pool holds four earlier policies: ablA, distill1, h4-300
# (the shipped bot) and rl-17cf03f. Starts from h4-300.
#
#   bash tools/rl_selfplay.sh [OUT] [SNAP_W] [MINUTES]
#
# Run from the box, detached by the caller; log goes to logs/OUT.out. Screen with tools/sp_watch.sh.
cd ~/poker-ai-lab-rl && . .venv/bin/activate
OUT=${1:-sp1}; SW=${2:-2.0}; MIN=${3:-240}
mkdir -p ckpt/$OUT logs pool_sp
cp -n pool_fixed/a_ablA.npz pool_fixed/b_distill1.npz pool_sp/
cp -n rl/models/h4_it000300.npz pool_sp/c_h4_300.npz
cp -n rl/models/best.npz pool_sp/d_rl17cf.npz
exec python -m rl.train --out ckpt/$OUT --init ckpt/heur4/it000300.npz --workers 3 --sdk-workers 10 \
  --heur-batch 10000 --envs 96 --steps 4000 --max-minutes $MIN --lr 1.5e-4 --clip 0.1 --floor 0.15 \
  --snap-w $SW --snap-every 10 --clones data/clones.npz --pool-dir pool_sp \
  --distill data/maniac_labels.npz --distill-w 0.5 >> logs/$OUT.out 2>&1
