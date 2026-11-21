#!/bin/bash
# One foreground training chunk (<= 9.5 min) for the adaptive and the no-history policy, run on gb10-d:
#   ssh gb10-d 'bash ~/poker-ai-lab-rl/tools/rl_chunk.sh 8.5'
# Each run resumes from its state.pt; 2 workers each so four busy processes in total.
cd ~/poker-ai-lab-rl && . .venv/bin/activate
M=${1:-8.5}
EXTRA=${2:-}
python -m rl.train --out ckpt/adapt --workers 2 --envs 96 --steps 16000 --max-minutes $M --clones data/clones.npz $EXTRA > logs/adapt.out 2>&1 &
python -m rl.train --out ckpt/nohist --no-hist --workers 2 --envs 96 --steps 16000 --max-minutes $M --clones data/clones.npz $EXTRA > logs/nohist.out 2>&1 &
wait
for r in adapt nohist; do echo "== $r"; tail -n 1 ckpt/$r/train.jsonl | cut -c1-1200; done
