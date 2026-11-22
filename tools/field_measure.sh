#!/bin/sh
# 400 matches, seed 3, for every field bot: (a) our shipped policy as hero, (b) the old heuristic bot as hero.
# Runs on gb10-d in ~/poker-ai-lab-fb, at most 4 worker processes. Output: ~/fb_results/<bot>.<a|b>.json
cd ~/poker-ai-lab-fb || exit 1
PY=~/poker-ai-lab-rl/.venv/bin/python
mkdir -p ~/fb_results
for bot in ${BOTS:-sdkref ashwing_value ashwing_hive ashwing_v2 ashwing_adaptive ashwing_search ashwing wolf wolf_v5 wolf_v2 wolf_v1 autodidact_fast autodidact}; do
  [ -s ~/fb_results/$bot.a.json ] || $PY -m rl.eval_arena --model rl/models/h4_it000300.npz --opp ext:$bot --matches 400 --seed 3 --workers 4 > ~/fb_results/$bot.a.json 2> ~/fb_results/$bot.a.err
  [ -s ~/fb_results/$bot.b.json ] || $PY -m rl.eval_arena --hero chipzen --opp ext:$bot --matches 400 --seed 3 --workers 4 > ~/fb_results/$bot.b.json 2> ~/fb_results/$bot.b.err
done
echo finished > ~/fb_results/DONE
