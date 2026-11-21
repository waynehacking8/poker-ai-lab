#!/bin/bash
# One command from the PC (Git Bash): stage HEAD, build the amd64 image on gb10-d, export it,
# print the sha256 and play one full match against lag.
# usage: deploy/build_on_box.sh <model npz path in repo, e.g. rl/models/distill1.npz> <image tag>
# The model must be committed (it is read from HEAD). Output: gb10-d:~/build-rl/<tag>.tar.gz
set -e
MODEL=$1; TAG=$2
[ -n "$MODEL" ] && [ -n "$TAG" ] || { echo "usage: $0 <model npz in repo> <image tag>"; exit 1; }
cd "$(git rev-parse --show-toplevel)"
git cat-file -e "HEAD:$MODEL" || { echo "$MODEL is not committed at HEAD"; exit 1; }
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
git archive HEAD rl chipzen_bot/nlhe holdem deploy > "$T/ctx.tar"
ssh gb10-d 'mkdir -p ~/build-rl'
scp -q "$T/ctx.tar" gb10-d:build-rl/ctx.tar
scp -q deploy/remote_build.sh gb10-d:build-rl/remote_build.sh
ssh -n gb10-d "bash ~/build-rl/remote_build.sh '$MODEL' '$TAG'"
