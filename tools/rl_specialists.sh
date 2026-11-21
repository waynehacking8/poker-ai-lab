#!/bin/bash
# Fine-tune one specialist per opponent type from the adaptive generalist (gb10-d, 4 busy processes):
#   ssh gb10-d 'bash ~/poker-ai-lab-rl/tools/rl_specialists.sh 2.5 maniac lag station_raiser'
# Types: station maniac nit random reference lag station_raiser arch:0 .. arch:5
cd ~/poker-ai-lab-rl && . .venv/bin/activate
M=$1; shift
for t in "$@"; do
  d=ckpt/spec_${t//:/_}
  mkdir -p $d
  [ -f $d/state.pt ] || cp ckpt/adapt/latest.npz $d/init.npz
  INIT=""; [ -f $d/state.pt ] || INIT="--init $d/init.npz"
  python -m rl.train --out $d $INIT --workers 4 --envs 96 --steps 16000 --max-minutes $M \
    --clones data/clones.npz --only "$t" --lr 1e-4 --ent 0.003 > logs/spec_${t//:/_}.out 2>&1
  echo "$t: $(tail -n 1 $d/train.jsonl | cut -c1-300)"
done
