#!/bin/bash
# Train against real Chipzen field bots (rl/field_bots, holdem-fieldbots) from h4-300. Same recipe as
# the ctl arm of tools/rl_gen.sh except the SDK workers, so ctl1 is its control at equal iterations.
#
#   bash tools/rl_fb.sh OUT [MINUTES]
#
# SDK opponents, round robin per worker: the heuristic HoldemBot twice (it is a ship gate) and four
# field bots: ext:ashwing_v2 (the live Chipzen entry), ext:ashwing_value, ext:ashwing_adaptive and
# ext:autodidact_fast.
# Held out from training:
#   validation, sibling bots: ext:ashwing, ext:ashwing_search, ext:ashwing_hive, ext:autodidact
#   test, other families: ext:wolf*, ext:sdkref, the real Blueprint (bp100), plus rl-17cf03f.
# 8 SDK workers and an 8000 sample batch keep about 2700 heuristic samples per update.
cd ~/poker-ai-lab-rl && . .venv/bin/activate
OUT=$1; MIN=${2:-180}
mkdir -p ckpt/$OUT logs pool_gen
cp -n pool_fixed/a_ablA.npz pool_fixed/b_distill1.npz pool_gen/
OPPS=chipzen,ext:ashwing_v2,ext:ashwing_value,chipzen,ext:ashwing_adaptive,ext:autodidact_fast
exec python -m rl.train --out ckpt/$OUT --init ckpt/heur4/it000300.npz --workers 2 --sdk-workers 8 \
  --sdk-opps $OPPS --heur-batch 8000 --envs 96 --steps 4000 --max-minutes $MIN --lr 1.5e-4 --clip 0.1 \
  --floor 0.15 --snap-w 0.3 --snap-every 25 --clones data/clones.npz --pool-dir pool_gen \
  --distill data/maniac_labels.npz --distill-w 0.5 >> logs/$OUT.out 2>&1
