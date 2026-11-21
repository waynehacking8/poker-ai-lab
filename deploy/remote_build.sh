#!/bin/bash
# Box side of build_on_box.sh: build, export, hash, local match. usage: remote_build.sh MODEL TAG
set -e
MODEL=$1; TAG=$2
cd ~/build-rl
# The local match server runs as root and can leave root-owned files in repo/ and res/.
docker run --rm -v "$PWD:/w" python:3.12-slim rm -rf /w/repo /w/res
mkdir repo; tar -x -C repo -f ctx.tar
cp repo/deploy/run_local_match.sh .; sed -i 's/\r$//' run_local_match.sh; chmod +x run_local_match.sh
docker buildx build --platform linux/amd64 --provenance=false --sbom=false --load \
  --build-arg MODEL="$MODEL" -f repo/deploy/Dockerfile -t "$TAG" repo
docker save "$TAG" | gzip > "$TAG.tar.gz"
sha256sum "$TAG.tar.gz"; ls -l "$TAG.tar.gz"
IMAGE="$TAG" ./run_local_match.sh lag 7
