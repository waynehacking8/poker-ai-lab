#!/bin/bash
# Assemble a Hugging Face model repo folder for one policy: the model card (deploy/hf/README.md), LICENSE,
# the weights as rl/models/weights.npz and model.safetensors, and the runtime files the Chipzen image ships
# (deploy/Dockerfile) at the same paths, so bot.py runs unchanged. Writes OUT.sha256 next to the folder.
#
#   bash deploy/hf_package.sh rl/models/fb2_it000900.npz OUT_DIR
set -euo pipefail
cd "$(dirname "$0")/.."
MODEL=$1; OUT=$2
git cat-file -e "HEAD:$MODEL" || { echo "$MODEL is not committed at HEAD"; exit 1; }
[ -e "$OUT" ] && { echo "$OUT exists"; exit 1; }
mkdir -p "$OUT/rl/models" "$OUT/nlhe/data"
cp deploy/hf/README.md LICENSE deploy/bot.py deploy/requirements.txt "$OUT/"
cp rl/__init__.py rl/bot.py rl/features.py rl/runtime.py "$OUT/rl/"
cp "$MODEL" "$OUT/rl/models/weights.npz"
cp chipzen_bot/nlhe/__init__.py chipzen_bot/nlhe/cards.py chipzen_bot/nlhe/evaluator.py \
  chipzen_bot/nlhe/preflop.py "$OUT/nlhe/"
cp chipzen_bot/nlhe/data/preflop_equity.json chipzen_bot/nlhe/data/pushfold.json "$OUT/nlhe/data/"
python - "$OUT" <<'PY'
import sys
import numpy as np
from safetensors.numpy import load_file, save_file
out = sys.argv[1]
z = np.load(f"{out}/rl/models/weights.npz", allow_pickle=False)
t = {k: np.ascontiguousarray(z[k]) for k in z.files}
save_file(t, f"{out}/model.safetensors", metadata={"format": "np"})
back = load_file(f"{out}/model.safetensors")
assert set(back) == set(t) and all(np.array_equal(back[k], t[k]) for k in t)
print("safetensors matches npz,", sum(a.size for a in t.values()), "params")
PY
(cd "$OUT" && find . -type f | sort | xargs sha256sum) > "$OUT.sha256"
