#!/bin/bash
# Roadmap M1b: after br_mix training and tools/m1_eval.sh end, play br_mix against both M1 targets on seed 21,
# the same settings as M1 (800 matches against ext:ashwing, 400 against ext:autodidact), so it compares
# directly with fb2-900 and the two single-target fine-tunes.
#
#   bash tools/m1b_eval.sh WORKERS PID...    (waits until every PID has exited; pids, not pgrep patterns)
# Output: logs/m1/br_mix_OPP.jsonl, marker logs/m1/mix_done; a failed eval is listed in logs/m1/failed.
cd ~/poker-ai-lab-rl && . .venv/bin/activate
W=$1; shift
for p in "$@"; do while kill -0 "$p" 2> /dev/null; do sleep 60; done; done
for o in ashwing:800 autodidact:400; do
  opp=${o%%:*}; k=${o#*:}
  python -m rl.eval_arena --model ckpt/br_mix/latest.npz --opp ext:$opp --matches $k --seed 21 --workers $W \
    > logs/m1/br_mix_$opp.jsonl 2> logs/m1/br_mix_$opp.err || echo "br_mix_$opp" >> logs/m1/failed
done
touch logs/m1/mix_done
