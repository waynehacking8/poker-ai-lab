#!/bin/sh
# 3-iteration smoke of rl.train with SDK field-bot opponents (scratch out dir, random init).
cd ~/poker-ai-lab-fb || exit 1
rm -rf smoke_out
exec ~/poker-ai-lab-rl/.venv/bin/python -m rl.train --out smoke_out --workers 1 --envs 8 --steps 300 --iters 3 \
  --sdk-workers 2 --heur-batch 400 --sdk-opps chipzen,ext:ashwing_v2,ext:autodidact_fast,ext:wolf
