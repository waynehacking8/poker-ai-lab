#!/bin/bash
# Generalization A/B from h4-300: the heur4 recipe (C env league, heuristic HoldemBot in SDK workers,
# ManiacBR distillation, snapshots weight 0.3 every 25 its) with and without 48 generated archetypes.
#
#   bash tools/rl_gen.sh OUT gen|ctl [MINUTES]
#
# gen: --clones data/clones_gen.npz (tools/gen_clones.py, 6 fitted + 48 generated) --gen-w 0.25
# ctl: --clones data/clones.npz (6 fitted)
# Both: fixed pool ablA + distill1 only, so rl-17cf03f and the per-bot clones stay held out.
# 2 C workers + 5 SDK workers each, so both arms fit on the box at once. Log: logs/OUT.out.
cd ~/poker-ai-lab-rl && . .venv/bin/activate
OUT=$1; ARM=$2; MIN=${3:-180}
mkdir -p ckpt/$OUT logs pool_gen
cp -n pool_fixed/a_ablA.npz pool_fixed/b_distill1.npz pool_gen/
if [ "$ARM" = gen ]; then CL="--clones data/clones_gen.npz --gen-w 0.25"; else CL="--clones data/clones.npz"; fi
exec python -m rl.train --out ckpt/$OUT --init ckpt/heur4/it000300.npz --workers 2 --sdk-workers 5 \
  --heur-batch 5000 --envs 96 --steps 4000 --max-minutes $MIN --lr 1.5e-4 --clip 0.1 --floor 0.15 \
  --snap-w 0.3 --snap-every 25 $CL --pool-dir pool_gen \
  --distill data/maniac_labels.npz --distill-w 0.5 >> logs/$OUT.out 2>&1
