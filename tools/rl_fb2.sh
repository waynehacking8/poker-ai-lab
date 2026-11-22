#!/bin/bash
# Continue from an fb1 checkpoint with more weight on the real field bots and on the archetypes
# at the gate line. fb1 (tools/rl_fb.sh) plateaued after about 200 iterations, when the field bots were
# about half of each batch.
#
#   bash tools/rl_fb2.sh OUT INIT [MINUTES]
#
# Changes from fb1:
#   10 SDK workers and a 10000 sample batch, with 3000 C engine decisions per worker (6000 in total),
#   so the field bots and the heuristic make up about 60% of each update (fb1: about 50%).
#   A5 and A2, the weakest clone archetypes (around the 80% line), at base weight 4 and 3 (others 1.5).
# Same SDK opponents and held-out sets as fb1, so its validation screens stay comparable.
cd ~/poker-ai-lab-rl && . .venv/bin/activate
OUT=$1; INIT=$2; MIN=${3:-180}
mkdir -p ckpt/$OUT logs pool_gen
OPPS=chipzen,ext:ashwing_v2,ext:ashwing_value,chipzen,ext:ashwing_adaptive,ext:autodidact_fast
exec python -m rl.train --out ckpt/$OUT --init $INIT --workers 2 --sdk-workers 10 \
  --sdk-opps $OPPS --heur-batch 10000 --envs 96 --steps 3000 --max-minutes $MIN --lr 1.5e-4 --clip 0.1 \
  --floor 0.15 --snap-w 0.3 --snap-every 25 --clones data/clones.npz --pool-dir pool_gen \
  --opp-w arch:5=4,arch:2=3 --distill data/maniac_labels.npz --distill-w 0.5 >> logs/$OUT.out 2>&1
