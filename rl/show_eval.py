"""Print eval_fast / eval_arena JSON lines as a table: python -m rl.show_eval logs/eval_x.jsonl ..."""
import json
import sys

for path in sys.argv[1:]:
    print("==", path)
    for line in open(path):
        try:
            d = json.loads(line)
        except ValueError:
            print(line[:200].rstrip())
            continue
        print(f"{d['opponent']:24s} {d['win_rate']:.3f} [{d['ci95'][0]:.3f},{d['ci95'][1]:.3f}] "
              f"hands/win={d.get('hands_per_win', d.get('mean_hands_per_win'))}")
