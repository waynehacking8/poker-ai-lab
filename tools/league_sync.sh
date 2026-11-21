#!/usr/bin/env bash
# Copy the league code to gb10-d (work dir ~/poker-ai-lab-league). Usage: tools/league_sync.sh
set -euo pipefail
cd "$(dirname "$0")/.."
tar cf - holdem league tests chipzen_bot pyproject.toml tools/*.sh | ssh gb10-d 'cd ~/poker-ai-lab-league && tar xf -'
