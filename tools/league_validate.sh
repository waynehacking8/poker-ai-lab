#!/usr/bin/env bash
# Refit clones on the box and validate them on held-out replays (70/30 split by match id).
# Run from ~/poker-ai-lab-league: tools/league_validate.sh   (about 10 minutes at 4 workers)
set -euo pipefail
export PYTHONPATH=.
PY=.venv/bin/python
$PY -m league.fit --data data --out league/data/clones.npz
$PY -m league.fit --data data --out out/clones_train.npz --holdout 0.3 > out/fit_train.log
$PY -m league.validate --model out/clones_train.npz --sims 600 --bot-sims 300 --workers 4 \
    --out out/validation.json
$PY -m league.validation_md out/validation.json out/clone_validation.md > /dev/null
