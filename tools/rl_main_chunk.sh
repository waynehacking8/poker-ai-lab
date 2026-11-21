#!/bin/bash
# One chunk of the main adaptive agent only (4 busy processes):  ssh gb10-d 'bash ~/poker-ai-lab-rl/tools/rl_main_chunk.sh 8.5 [out] [extra args]'
cd ~/poker-ai-lab-rl && . .venv/bin/activate
M=${1:-8.5}; OUT=${2:-adapt2}; shift; shift
python -m rl.train --out ckpt/$OUT --workers 4 --envs 96 --steps 16000 --max-minutes $M --clones data/clones.npz "$@" > logs/$OUT.out 2>&1
tail -n 1 ckpt/$OUT/train.jsonl | cut -c1-1500
