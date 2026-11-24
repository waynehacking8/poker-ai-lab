#!/bin/bash
# Fetch every completed heads-up poker replay from the public Chipzen API, politely, over days.
#   OUT=~/chipzen-replays PY=python3 bash tools/fetch_chipzen_all.sh
# One fetcher at a time (tools/fetch_chipzen_replays.py, DELAY seconds between requests). On HTTP 429 the
# fetcher stops at once; this loop then waits BACKOFF seconds (the block is 900 s) and resumes, skipping files
# already on disk. Any other error stops the loop. A pass that saves nothing ends it. Marker: $OUT.done
cd "$(dirname "$0")/.." || exit 1
OUT=${OUT:-$HOME/chipzen-replays}
PY=${PY:-python3}
DELAY=${DELAY:-3}
BACKOFF=${BACKOFF:-1800}
mkdir -p "$OUT"
for pass in $(seq 1 ${PASSES:-50}); do
  echo "pass $pass $(date -u +%FT%H:%MZ) files $(ls "$OUT" | wc -l)"
  $PY tools/fetch_chipzen_replays.py "$OUT" 1000000 "$DELAY" > "$OUT.pass.log" 2>&1
  rc=$?
  cat "$OUT.pass.log"
  if [ $rc -eq 1 ]; then sleep "$BACKOFF"; continue; fi
  [ $rc -ne 0 ] && { echo "stopped: exit $rc"; break; }
  grep -q "done: saved 0," "$OUT.pass.log" && break
done
date -u +%FT%H:%MZ > "$OUT.done"
