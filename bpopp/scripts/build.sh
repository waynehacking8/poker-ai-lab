#!/bin/bash
# Run ON gb10-d after fetch.sh. The build may use the network (apt, PyPI, Docker Hub).
set -e
cd ~/bp-src/code
docker build -f ~/poker-ai-lab-bp/src/bpopp/Dockerfile --build-context ours=$HOME/poker-ai-lab-bp/src/bpopp -t bpopp:v010 .
