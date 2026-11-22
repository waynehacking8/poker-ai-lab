#!/bin/bash
# Run ON gb10-d. Fetches the pinned poker-solver code and the blueprint tar, verifies
# the tar against the published sha256, extracts to ~/bp-data. Parallel ranged curl:
# a single GitHub release connection ran at ~30 KB/s here, 16 ranges at ~4 MB/s.
set -e
SHA=4ee3132b6e802c0efc74d469ec190b9c47727d7b   # tag v0.1.0
BASE=https://github.com/matteo-psnt/poker-solver/releases/download/v0.1.0
SIZE=1947260928
N=16
mkdir -p ~/bp-data ~/bp-src ~/bp-parts
cd ~/bp-src
[ -d code ] || { mkdir code_tmp && curl -fsSL https://github.com/matteo-psnt/poker-solver/archive/$SHA.tar.gz | tar xz -C code_tmp --strip-components=1 && mv code_tmp code; }
cd ~/bp-data
curl -fL -o blueprint-100bb.tar.sha256 $BASE/blueprint-100bb.tar.sha256
cd ~/bp-parts
CH=$(( (SIZE + N - 1) / N ))
for i in $(seq 0 $((N-1))); do
  s=$((i*CH)); e=$((s+CH-1)); [ $e -ge $SIZE ] && e=$((SIZE-1))
  ( while :; do have=$(stat -c %s part$i 2>/dev/null || echo 0); [ "$have" -ge $((e-s+1)) ] && break
      curl -sfL -r $((s+have))-$e $BASE/blueprint-100bb.tar >> part$i || sleep 2; done ) &
done
wait
cat $(for i in $(seq 0 $((N-1))); do echo part$i; done) > ~/bp-data/blueprint-100bb.tar
cd ~/bp-data && sha256sum -c blueprint-100bb.tar.sha256   # must say OK before the next line
tar xf blueprint-100bb.tar
rm -rf ~/bp-parts
