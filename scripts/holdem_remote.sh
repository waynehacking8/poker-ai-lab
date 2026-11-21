#!/usr/bin/env bash
# Sync the working tree to the simulation box and run the arena there.
#   scripts/holdem_remote.sh "<opp list or all>" <matches> [seed]
# Results land in ~/poker-ai-lab-sim/logs/ on the box and are printed here.
set -euo pipefail
cd "$(dirname "$0")/.."
OPPS="${1:-all}"; N="${2:-200}"; SEED="${3:-1}"
tar czf - --exclude=.git --exclude=.venv --exclude=.venv-chipzen --exclude=.cache \
  --exclude=__pycache__ --exclude=reports --exclude=results --exclude=docs . \
  | ssh gb10-d 'mkdir -p ~/poker-ai-lab-sim/logs && tar xzf - -C ~/poker-ai-lab-sim'
ssh gb10-d "cd ~/poker-ai-lab-sim && .venv/bin/python -m holdem.arena --opp $OPPS --matches $N --seed $SEED --workers 8"
