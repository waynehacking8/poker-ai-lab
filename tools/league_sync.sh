#!/usr/bin/env bash
# Copy the league code to gb10-d (work dir ~/poker-ai-lab-league). Usage: tools/league_sync.sh
# league/data/clones.npz is excluded: it is refit on the box (league.fit), then copied back with scp.
set -euo pipefail
cd "$(dirname "$0")/.."
tar cf - --exclude=league/data/clones.npz holdem league tests chipzen_bot pyproject.toml tools/*.sh tools/league_register.py | ssh gb10-d 'cd ~/poker-ai-lab-league && tar xf -'
