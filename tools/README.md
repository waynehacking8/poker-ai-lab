# tools

Scripts around the Chipzen replays. The replays themselves live in `.cache/chipzen-replays`
(gitignored), one JSON file per match, shaped `{"match": ..., "replay": ...}`.

* `python tools/fetch_chipzen_replays.py OUT_DIR [MAX_MATCHES] [DELAY]` downloads completed
  heads-up poker replays from the public API, skipping files already on disk.
* `python tools/analyze_chipzen_replays.py .cache/chipzen-replays` prints the match format
  (blind steps, match lengths) and field tendencies.
* `python tools/match_ceiling.py [chipzen_bot/nlhe/data/preflop_equity.json]` solves the
  fold-or-shove dynamic program against the maniac and prints a lower bound on the best
  achievable match win rate.
* `python tools/chipflow.py --model M --opp bp100 --out F.jsonl` logs every hand of one policy against one
  opponent and prints where the chips go: by effective stack, by how hands end, and all-in luck (actual
  minus expected chips from the hero's equity when the money went in). Needs the BP_* env for bp100.
  `--opp` also takes `model:<npz>` and the extreme bots (`jam`, `jam_half`, `jam_post`, `minraiser`).
* `python tools/allin_tables.py rl/models/allin_v.npz` solves the match-value tables that `rl/allin.py`
  uses to answer a preflop all-in from a frequent shover (roadmap S0).
* `bash tools/allin_gate.sh [MODEL]` is the S0 gate on the box: each opponent group with and without the
  all-in answer (`RL_ALLIN=off`) on the same seeds, plus fire counts. `ALLIN_COUNT_LOG=F python
  tools/allin_count.py <rl.eval_arena args>` runs one evaluation and logs every decision the answer changed.
  `python tools/allin_ceiling.py oracle jam` is the ceiling with the shove range known from hand 1.
* `bash tools/rl_exploit.sh OUT TARGET [MINUTES]` trains an exploiter of one frozen policy in the C engine
  (`INIT=<full checkpoint>` when TARGET has no value weights).
* `bash tools/exploit_probe.sh INIT_CKPT TARGET_NPZ NAME TRAIN_SEED EVAL_SEED [ITERS]` is the fixed-budget
  exploitability probe (roadmap E3): a fresh exploiter, then 400 SDK matches against TARGET.
* `bash tools/rl_s2.sh OUT INIT [MINUTES] [FROM]` is roadmap S2: the fb2 recipe against a rotating pool of
  exploiters of the main agent (`tools/s2_exploiters.sh`) and the shover bots, with screens and stop conditions
  (`tools/s2_screens.sh`, `tools/s2_screen.py`). The end reason lands in `logs/OUT/end.txt`. FROM resumes a
  finished run with its state and its 4 newest pool files (S2b).
* `python tools/probe_pool.py NAME...` pools probes with distinct eval seeds: wins, matches, Wilson interval.
* `bash tools/rl_br.sh OUT INIT OPPS [MINUTES] [NSDK]` fine-tunes INIT against SDK field bots only (best-response
  headroom, roadmap M1).
* `bash tools/m1_eval.sh [WORKERS]` waits for the rl_br runs, then evaluates fb2-900 and the fine-tunes (roadmap M1).
* `python tools/style_map.py replays|sim|compare ...` puts the real field (replays) and our opponents (simulated
  against one hero) on one 8-axis style map and lists each field bot's nearest pool member.
* `bash tools/eval_card.sh NAME POLICY_NPZ INIT_CKPT [KING_NPZ]` writes the eval card of one candidate
  (roadmap E2 to E4) to `logs/eval_card/NAME.json` on the box, about 75 minutes.
* `python tools/replay_conformance.py [REPLAY_DIR] [--show N]` replays every real NLHE hand
  through `holdem/engine.py` and lists each hand where the engine asks something else, offers
  other actions, posts other blinds or ends with other stacks (exit code 1 on any difference).
  `tests/test_replay_conformance.py` runs the same check and skips without the replay folder.
  The replays are not synced by `scripts/holdem_remote.sh`; copy `.cache/chipzen-replays` to
  `~/poker-ai-lab-sim/.cache/` on the box once to run it there.

## Rate limit

Chipzen blocks the IP for 900 s after a burst of requests. Keep at least 3 s between
requests, stop on the first HTTP 429, and run one fetcher at a time.
* `python tools/oppmodel_fit.py fit --data DIR` fits, selects and scores the X1 opponent model (`rl/oppmodel.py`, `rl/models/oppmodel.npz`) on the poker replays; `bench` replays the held-out actions and prints p50 and p99 of update plus prediction (roadmap X1; fit needs torch, bench only numpy).
