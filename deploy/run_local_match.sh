#!/bin/bash
# Play one full match: localmatch.py server in one container, the built image as the bot.
# usage: run_local_match.sh OPP SEED   (run on the box, in a dir holding repo/ and res/)
# Image limits mirror the platform: amd64, 0.5 vCPU, 256 MB, uid 10001, read-only, cap-drop.
OPP=$1; SEED=$2
cd "$(dirname "$0")"
docker network inspect rlnet >/dev/null 2>&1 || docker network create rlnet
docker rm -f rlsrv rlbot >/dev/null 2>&1
mkdir -p res; rm -f res/$OPP-$SEED.json
docker run -d --name rlsrv --network rlnet -v "$PWD/repo:/repo" -v "$PWD/res:/res" -w /repo python:3.12-slim \
  sh -c "pip install -q chipzen-bot==0.7.0 websockets numpy >/dev/null 2>&1 && python deploy/localmatch.py --opp $OPP --seed $SEED --out /res/$OPP-$SEED.json" >/dev/null
until docker exec rlsrv sh -c 'python -c "import socket;socket.create_connection((\"127.0.0.1\",8765),1)"' 2>/dev/null; do sleep 1; done
T0=$(date +%s.%N)
docker run -d --name rlbot --network rlnet --platform linux/amd64 --cpus 0.5 --memory 256m \
  --user 10001:10001 --read-only --cap-drop ALL --security-opt no-new-privileges \
  -e CHIPZEN_WS_URL=ws://rlsrv:8765/ws/match/m_local_1/bot holdem-rl-distill1 >/dev/null
# cold start: time until the server sees the bot's connection (its first decision request follows)
until docker logs rlsrv 2>&1 | grep -q CONNECTED || [ -f res/$OPP-$SEED.json ]; do sleep 0.1; done
echo "COLD_START_S=$(echo "$(date +%s.%N) - $T0" | bc)"
PEAK=0
while [ ! -f res/$OPP-$SEED.json ] && [ "$(docker inspect -f '{{.State.Running}}' rlbot)" = true ]; do
  M=$(docker exec rlbot cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo 0)
  [ "$M" -gt "$PEAK" ] 2>/dev/null && PEAK=$M
  sleep 2
done
M=$(docker exec rlbot cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo 0)
[ "$M" -gt "$PEAK" ] 2>/dev/null && PEAK=$M
echo "PEAK_BYTES=$PEAK"
sleep 3
echo "--- bot logs"; docker logs rlbot 2>&1 | tail -15
docker inspect -f 'exit={{.State.ExitCode}} oom={{.State.OOMKilled}} running={{.State.Running}}' rlbot
echo "--- result"; cat res/$OPP-$SEED.json
echo RUN_DONE
