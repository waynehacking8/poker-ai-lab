#!/usr/bin/env bash
# Export a branch of another checkout (read only, git archive) to gb10-d as a league candidate.
# Usage: tools/league_export.sh <repo dir> <branch> <name>
#   -> ~/poker-ai-lab-league/candidates/<name>/   (add it to candidates.json on the box)
set -euo pipefail
repo=$1; branch=$2; name=$3
git -C "$repo" archive "$branch" | ssh gb10-d "rm -rf ~/poker-ai-lab-league/candidates/$name && mkdir -p ~/poker-ai-lab-league/candidates/$name && tar x -C ~/poker-ai-lab-league/candidates/$name"
git -C "$repo" rev-parse "$branch" | ssh gb10-d "cat > ~/poker-ai-lab-league/candidates/$name/.commit"
echo "exported $branch of $repo as candidates/$name"
