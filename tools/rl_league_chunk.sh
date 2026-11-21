#!/bin/bash
# League chunk on gb10-d: the main adaptive agent plus one main exploiter trained only against it (2 + 2 processes).
#   ssh gb10-d 'bash ~/poker-ai-lab-rl/tools/rl_league_chunk.sh 8.5 exploit1'
# The exploiter starts from scratch when its directory is new (periodic reset = use a new name).
# Afterwards its checkpoint is copied into ckpt/pool/, where the main agent samples it (PFSP).
cd ~/poker-ai-lab-rl && . .venv/bin/activate
M=${1:-8.5}; X=${2:-exploit1}
mkdir -p ckpt/pool
python -m rl.train --out ckpt/adapt --workers 2 --envs 96 --steps 16000 --max-minutes $M --clones data/clones.npz --pool-dir ckpt/pool > logs/adapt.out 2>&1 &
python -m rl.train --out ckpt/$X --workers 2 --envs 96 --steps 16000 --max-minutes $M --fixed-opp ckpt/adapt/latest.npz --seed 5 > logs/$X.out 2>&1 &
wait
cp ckpt/$X/latest.npz ckpt/pool/$X.npz
for r in adapt $X; do echo "== $r"; tail -n 1 ckpt/$r/train.jsonl | cut -c1-1200; done
