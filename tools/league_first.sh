#!/usr/bin/env bash
# First leaderboard on gb10-d: clone validation (train/test split), then the league. Run from
# ~/poker-ai-lab-league with: nohup tools/league_first.sh > logs/first.log 2>&1 &
set -euo pipefail
export PYTHONPATH=.
PY=.venv/bin/python
$PY -m league.fit --data data --out out/clones_train.npz --holdout 0.3 --iters 8 > out/fit_train.log
$PY -m league.validate --model out/clones_train.npz --sims 600 --bot-sims 300 --workers 4 \
    --out out/validation.json | tee out/validation.log
$PY -m league.run --candidates candidates.json --out out/league --field-pairs 400 \
    --bot-pairs 30 --base-pairs 60 --h2h-pairs 100 --workers 4
$PY -m league.report --out out/league --md out/leaderboard.md
echo FINISHED
