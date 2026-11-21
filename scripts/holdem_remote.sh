#!/usr/bin/env bash
# Sync the working tree to the simulation box (gb10-d) and run a command there.
#   scripts/holdem_remote.sh python -m holdem.arena --opp all --matches 400 --seed 1 --workers 8
#   scripts/holdem_remote.sh python -m pytest -q
# "python" resolves to the box venv (chipzen-bot, pytest, numpy installed).
set -euo pipefail
cd "$(dirname "$0")/.."
tar czf - --exclude=.git --exclude=.venv --exclude=.venv-chipzen --exclude=.cache \
  --exclude=__pycache__ --exclude=.pytest_cache --exclude=results . \
  | ssh gb10-d 'mkdir -p ~/poker-ai-lab-sim/logs && tar xzf - -C ~/poker-ai-lab-sim'
ssh gb10-d "cd ~/poker-ai-lab-sim && PATH=\$HOME/poker-ai-lab-sim/.venv/bin:\$PATH $(printf '%q ' "$@")"
