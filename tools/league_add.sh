#!/usr/bin/env bash
# Add a candidate to the league and refresh the leaderboard, in one command.
#
#   tools/league_add.sh <repo dir> <branch or commit> <name> <module> <class>
#   e.g. tools/league_add.sh /c/Users/WEI-CHENG/Desktop/poker-ai-lab holdem-chipzen chipzen-tip bot HoldemBot
#
# Steps: sync the league code to gb10-d, export the branch (git archive, read only), register it
# in candidates.json (with an import smoke test), play only that entrant's matches (plus any
# baseline rows still missing; finished matches are skipped) against every archetype, every
# per-bot clone, every baseline and every earlier candidate, then rebuild the leaderboard into
# reports/league/leaderboard.md. The job runs detached on the box (nohup); this script polls it,
# so a dropped connection is safe: rerun the same command and it resumes.
# Env: WORKERS (default 4), PAIRS (duplicate pairs per opponent, default 200), H2H_PAIRS (100).
set -euo pipefail
[ $# -eq 5 ] || { sed -n '2,13p' "$0"; exit 2; }
repo=$1; ref=$2; name=$3; module=$4; cls=$5
WORKERS=${WORKERS:-4}; PAIRS=${PAIRS:-200}; H2H_PAIRS=${H2H_PAIRS:-100}
cd "$(dirname "$0")/.."
BOX='cd ~/poker-ai-lab-league'

tools/league_sync.sh
tools/league_export.sh "$repo" "$ref" "$name"
ssh gb10-d "$BOX && .venv/bin/python tools/league_register.py '$name' '$module' '$cls'"

if ssh gb10-d "pgrep -f 'league.run.*--only $name' > /dev/null"; then
  echo "league.run for $name is already running on gb10-d; waiting for it"
else
  ssh -n gb10-d "$BOX && mkdir -p logs out/league && rm -f logs/add-$name.done && \
    { nohup bash -c 'PYTHONPATH=. .venv/bin/python -m league.run --candidates candidates.json \
      --out out/league --only $name --pairs $PAIRS --h2h-pairs $H2H_PAIRS --workers $WORKERS; \
      echo \$? > logs/add-$name.done' > logs/add-$name.log 2>&1 < /dev/null & }"
fi

until ssh gb10-d "$BOX && test -f logs/add-$name.done"; do
  sleep 60
  ssh gb10-d "$BOX && tail -n 1 logs/add-$name.log" || true
done
code=$(ssh gb10-d "$BOX && cat logs/add-$name.done")
[ "$code" = "0" ] || { echo "league.run exited with $code, see logs/add-$name.log on gb10-d"; exit 1; }

ssh gb10-d "$BOX && PYTHONPATH=. .venv/bin/python -m league.report --out out/league --md out/leaderboard.md > /dev/null"
scp -q gb10-d:poker-ai-lab-league/out/leaderboard.md reports/league/leaderboard.md
echo "leaderboard written to reports/league/leaderboard.md"
sed -n '1,/^## Gate/p' reports/league/leaderboard.md | head -30
