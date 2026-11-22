#!/bin/bash
# Eval card of one candidate (roadmap E2, E3, E4; E1 is the league gate, recorded by reference).
#   E2  real bots: Ashwing family (seed 5), Wolf family, SDK reference, autodidact (seed 3), seeded
#       Blueprint bpopp:v011 (seed 3, 2 workers), and all-in adjusted chip EV per hand against it.
#   E3  exploit_probe.sh INIT_CKPT POLICY_NPZ (train seed 1, eval seed 3).
#   E4  head to head against the king (model:, seeded), 400 matches, seed 3. The fb2-900 mirror on the same
#       seeds reads 45.0%.
# Output: logs/eval_card/NAME.json (raw lines in logs/eval_card/NAME/). Refuses an existing card.
#
#   bash tools/eval_card.sh NAME POLICY_NPZ INIT_CKPT [KING_NPZ]
set -u
cd ~/poker-ai-lab-rl && . .venv/bin/activate
NAME=$1; M=$2; INIT=$3; KING=${4:-rl/models/fb2_it000900.npz}
D=logs/eval_card/$NAME
[ -e "$D" ] && { echo "$D exists"; exit 1; }
mkdir -p $D
ev() {  # FILE SEED WORKERS OPPS
  python -m rl.eval_arena --model $M --opp $4 --matches 400 --seed $2 --workers $3 > $D/$1.jsonl 2> $D/$1.err \
    || { echo "eval $1 failed, see $D/$1.err"; exit 1; }
}
ev ashwing 5 4 ext:ashwing,ext:ashwing_search,ext:ashwing_hive,ext:ashwing_v2
ev wolf 3 4 ext:wolf,ext:wolf_v1,ext:wolf_v2,ext:wolf_v5,ext:sdkref,ext:autodidact
ev king 3 4 model:$KING
export BP_DATA=$HOME/bp-data BP_RUN=run-pcs-production_opens-to12k-d100-145201-6584 BP_AT=65000 \
  BP_THRESHOLD=0.35 BP_IMAGE=bpopp:v011
ev bp100 3 2 bp100
python tools/chipflow.py --model $M --opp bp100 --matches 400 --seed 3 --workers 2 --out $D/flow_bp100.jsonl \
  > $D/flow_bp100.out 2>&1 || { echo "chipflow failed, see $D/flow_bp100.out"; exit 1; }
bash tools/exploit_probe.sh $INIT $M card_$NAME 1 3 > $D/probe.out 2>&1 || { echo "probe failed, see $D/probe.out"; exit 1; }
python - $D $NAME $M $KING card_$NAME > logs/eval_card/$NAME.json <<'PY'
import json, sys
d, name, model, king, probe = sys.argv[1:]
lines = lambda f: [json.loads(l) for l in open(f"{d}/{f}.jsonl") if l.startswith("{")]
pick = lambda r: {k: r[k] for k in ("opponent", "matches", "wins", "win_rate", "ci95", "seed")}
rows = [x for m in map(json.loads, open(f"{d}/flow_bp100.jsonl")) for x in m["rows"]]
adj = sum((x["ev_delta"] if x["end"] == "allin" else x["delta"]) / x["bb"] for x in rows)
card = {
    "name": name, "model": model,
    "E2": [pick(r) for f in ("ashwing", "wolf", "bp100") for r in lines(f)]
          + [{"opponent": "bp100", "chip_ev_bb_per_hand_allin_adjusted": round(adj / len(rows), 4), "hands": len(rows)}],
    "E3": json.load(open(f"logs/exploit_probe/{probe}.json")),
    "E4": dict(pick(lines("king")[0]), king=king, mirror_fb2_900_seed3=0.45),
}
print(json.dumps(card))
PY
cat logs/eval_card/$NAME.json
