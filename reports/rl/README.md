# RL track: opponent-conditioned PPO trained on match wins

Branch `holdem-rl`. Everything heavy ran on gb10-d in `~/poker-ai-lab-rl/` (own venv, 4 busy processes at most).
Numbers below are from the logs named in each section; all matches are seat swapped, real format
(10,000 stacks, blinds 100 to 1000, play to bust), 95% Wilson intervals over matches.

## What was built

| piece | file |
|---|---|
| lean C match engine (same rules as `holdem/engine.py` after 4deda52: short big blind, 800 and 1000 levels), the 7 baselines and the replay clones in C | `rl/fastenv.c`, `rl/fastenv.py`, `rl/clones.py` |
| reference feature extractor (56 floats) used at runtime, mirrored in C | `rl/features.py` |
| PPO trainer with a PFSP league, exploiter mode, no-history ablation | `rl/train.py`, `tools/rl_*.sh` |
| numpy-only runtime and the candidate `Bot` | `rl/runtime.py`, `rl/bot.py` (`RLBot`) |
| per-type specialists | `rl/specialists.py`, `rl/models/spec_*.npz` |
| match-value network | `rl/matchvalue.py`, `rl/models/match_value.npz` |
| fast evaluator, SDK-arena evaluator, latency, adaptation report | `rl/eval_fast.py`, `rl/eval_arena.py`, `rl/latency.py`, `rl/adapt_report.py` |

Candidate for the league: module `rl.bot`, class `RLBot` (constructor `RLBot(seed=None, model=..., temperature=1.0)`,
default weights `rl/models/best.npz`, 330 KB). It needs `chipzen`, `numpy`, and `chipzen_bot/` plus the repo root on
`sys.path` (importing `rl` does both).

## Method and why

* **Algorithm: PPO** (GAE lambda 0.95, gamma 1, two 256 unit ReLU MLPs for policy and value). The 2026 evidence
  (ICLR 2026 reevaluation, VRPO) is that tuned generic policy gradient beats NFSP, PSRO and ESCHER, and PPO is
  sample efficient enough here because the C engine does about 60,000 decisions per second on 4 cores.
* **Objective: match win probability.** Reward is potential shaped by chip share (phi = my chips / all chips at hand
  start, 1 or 0 at bust). With gamma 1 this telescopes to the match outcome, so the optimum is unchanged; it only
  gives a dense signal. Blinds follow the real schedule including 800 and 1000.
* **Actions:** fold, check/call, raise 0.5, 1, 2 pot, all-in, mapped to legal amounts with duplicates masked.
* **Opponent conditioning (meta-RL by features, no recurrence).** The observation holds the in-match statistics of the
  opponent from finished hands: open raise rate, fold to preflop raise, 3-bet, fold to postflop bet, raise vs bet,
  bet when checked to, VPIP, showdown rate, and a confidence term. The policy learns to read these inside one match.
* **Population:** 7 baselines, the 6 archetype clones from the league, and past snapshots of itself.
  **The 10 per-bot clones are held out of training** and used only as test.
* **Sampling: PFSP.** Weight of an opponent = base * (0.15 + (1 - x)^2), x = our running win rate against it.
  The floor 0.15 matters: without it (floor 0.05) the policy forgot the easy opponents (lag 94 percent to 73 percent in
  one 8 minute chunk). Base weights favour maniac, lag, station_raiser.
* **PPO settings after the forgetting episode:** clip 0.1, learning rate 1.5e-4, entropy 0.01.
* **Engine equivalence:** `tests/test_rl_env.py`, `tests/test_rl_clones.py`, `tests/test_rl_rules.py` (43 tests, run on
  gb10-d). Details below.

## Engine equivalence evidence

* Evaluator: C and Python scores identical on 30,000 random 5, 6 and 7 card hands.
* Rules and features: 12 full matches between two random-legal actors played through `holdem/engine.py`
  (fixed engine, merged 102b05e); every decision is replayed in C with the same decks and compared on to-call, min and
  max raise, pot, stack, legal action mask, the raise amount of each of the six actions, and all 56 features
  (tolerance 2e-5); final stacks and hand counts must match.
* Baselines: for each of the 7 baselines, 40 full matches against a random-legal actor; the C baseline must pick the
  same action as the Python class at every decision (random baselines are driven by one shared uniform stream).
  Mutating a threshold in C makes these tests fail (checked for station_raiser, lag, nit).
* Replay clones: 16 real clones from `data/clones.npz` (6 archetypes, 10 bots) plus synthetic tables, 30 matches each,
  with `league.clone.CloneBot` driven by the same stream.
* Server rules: `tests/test_rl_rules.py` checks the schedule to 1000 and both short big blind cases.
* Defect found and fixed during the work: neighbouring match seeds produced shifted random streams in C (the
  generator state advanced by a constant). That inflated some early fast evaluations (maniac 85 percent and random
  76 percent where the SDK arena says 78 and 87). The seed is now hashed; fast and arena numbers agree afterwards.

## Training curve

Match win rate against the training population while training (sampled policy; PFSP weights, so the mix shifts
towards hard opponents over time). Raw rows are in `reports/rl/data/train_*.jsonl`. About 150M decisions in total.

| stage | cumulative steps | maniac | lag | station_raiser | note |
|---|---|---|---|---|---|
| first run, 3 min | 11M | 0.77 | 0.95 | 0.95 | baselines only, about 60k decisions per second on 4 cores |
| first run, 9 min | 31M | 0.77 | 0.99 | 0.94 | baselines only |
| adaptive, it1300 | 42M | 0.79 | 0.91 | 0.91 | 6 archetype clones added, PFSP floor 0.05 |
| adaptive, it1940 | 62M | 0.73 | 0.73 | 0.86 | forgetting: floor too low, discarded |
| adapt2 (restart from it1300) | +30M | 0.805 | 0.948 | 0.940 | floor 0.15, clip 0.1, lr 1.5e-4 |
| final (`ablA` plus one 8.5 min chunk) | +76M | 0.81 | 0.94 | 0.95 | fast eval, 400 matches |

## Final evaluation (best checkpoint `rl/models/best.npz`, about 76M decisions after the last restart, about 150M including the early runs)

### All 23 gate opponents, fast C engine, 400 seat swapped matches each (`reports/rl/data/eval_final.jsonl`)

| opponent | match wins | win rate | 95% CI | hands per win |
|---|---|---|---|---|
| station | 385/400 | 0.963 | 0.939 to 0.977 | 22.3 |
| maniac | 325/400 | 0.812 | 0.771 to 0.848 | 10.7 |
| nit | 395/400 | 0.988 | 0.971 to 0.995 | 77.2 |
| random | 345/400 | 0.863 | 0.825 to 0.893 | 16.3 |
| reference | 396/400 | 0.990 | 0.975 to 0.996 | 83.1 |
| lag | 375/400 | 0.938 | 0.909 to 0.957 | 47.2 |
| station_raiser | 378/400 | 0.945 | 0.918 to 0.963 | 21.3 |
| arch:0 | 364/400 | 0.910 | 0.878 to 0.934 | 28.1 |
| arch:1 | 385/400 | 0.963 | 0.939 to 0.977 | 19.2 |
| arch:2 | 348/400 | 0.870 | 0.833 to 0.899 | 28.2 |
| arch:3 | 344/400 | 0.860 | 0.823 to 0.891 | 17.3 |
| arch:4 | 359/400 | 0.897 | 0.864 to 0.924 | 34.9 |
| arch:5 | 336/400 | 0.840 | 0.801 to 0.873 | 32.2 |
| bot:Blueprint | 340/400 | 0.850 | 0.812 to 0.882 | 30.4 |
| bot:Kimiko | 393/400 | 0.983 | 0.964 to 0.991 | 21.2 |
| bot:AutodidactInnovations | 337/400 | 0.843 | 0.804 to 0.875 | 34.6 |
| bot:SolvencyCheck | 370/400 | 0.925 | 0.895 to 0.947 | 39.9 |
| bot:DeepStack | 389/400 | 0.973 | 0.951 to 0.985 | 16.8 |
| bot:mr_hide | 356/400 | 0.890 | 0.856 to 0.917 | 21.4 |
| bot:MercuryRetrograde | 360/400 | 0.900 | 0.867 to 0.926 | 27.0 |
| bot:qwentom-leap | 346/400 | 0.865 | 0.828 to 0.895 | 29.0 |
| bot:InfernalMonarch | 350/400 | 0.875 | 0.839 to 0.904 | 28.3 |
| bot:PoetAndCoder | 320/400 | 0.800 | 0.758 to 0.836 | 18.9 |

All 23 point estimates are at or above 0.80 (minimum bot:PoetAndCoder 0.800); the minimum Wilson lower bound is 0.758, so the 95 percent bound gate is not met for the tightest opponents (maniac, PoetAndCoder, archetype 5, AutodidactInnovations, Blueprint).

### Real SDK arena, fixed engine (merged 102b05e), runtime `RLBot`, 400 matches (`reports/rl/data/arena_final.jsonl`, seed 3)

| opponent | match wins | win rate | 95% CI | hands per win |
|---|---|---|---|---|
| station | 389/400 | 0.973 | 0.951 to 0.985 | 21.5 |
| maniac | 319/400 | 0.797 | 0.755 to 0.834 | 10.9 |
| nit | 399/400 | 0.998 | 0.986 to 1.000 | 79.6 |
| random | 323/400 | 0.807 | 0.766 to 0.843 | 15.8 |
| reference | 396/400 | 0.990 | 0.975 to 0.996 | 81.4 |
| lag | 384/400 | 0.960 | 0.936 to 0.975 | 45.9 |
| station_raiser | 376/400 | 0.940 | 0.912 to 0.959 | 21.8 |
| chipzen | 184/400 | 0.460 | 0.412 to 0.509 | 32.1 |

In this seed maniac reads 0.797 and random 0.807 (the same checkpoint read 0.80 and 0.88 in an earlier arena run; the sampling noise of a 400 match estimate is about plus or minus 0.04). Head to head against the current `chipzen_bot` bot: 0.460 here, 0.495 and 0.525 for two earlier checkpoints: an even matchup, not a win.

### Per-type specialists (fine-tuned 1.5 to 1.7 minutes from the generalist, fast engine, 400 matches)

| type | generalist | specialist |
|---|---|---|
| station | 0.963 | 0.998 [0.986,1.000] |
| maniac | 0.812 | 0.860 [0.823,0.891] |
| nit | 0.988 | 0.998 [0.986,1.000] |
| random | 0.863 | 0.850 [0.812,0.882] |
| reference | 0.990 | 0.998 [0.986,1.000] |
| lag | 0.938 | 0.978 [0.958,0.988] |
| station_raiser | 0.945 | 0.988 [0.971,0.995] |
| arch_0 | 0.910 | 0.870 [0.833,0.899] |
| arch_1 | 0.963 | 0.973 [0.951,0.985] |
| arch_2 | 0.870 | 0.973 [0.951,0.985] |
| arch_3 | 0.860 | 0.920 [0.889,0.943] |
| arch_4 | 0.897 | 0.945 [0.918,0.963] |
| arch_5 | 0.840 | 0.920 [0.889,0.943] |

Files `rl/models/spec_<name>.npz`, loader `rl.specialists.make(name, seed)` (a `Bot` subclass), list in `rl.specialists.NAMES`. Specialists exist for the 7 baselines and the 6 archetypes only; there are none for the per-bot clones (held out).


## Adaptation curve (adaptive vs the same policy without the history input)

Both were trained identically for about 1000 iterations (adaptive it1000, no-history it1055), fast evaluator, 400
seat swapped matches per opponent (`reports/rl/data/curve_*.jsonl`, aggregated by `rl.adapt_report`).
Chip leader after N hands is the share of matches still running after N hands in which the policy holds more than
half the chips, so it is a survivor statistic.

| group | policy | match win rate | chip leader after 10 | after 20 | after 40 |
|---|---|---|---|---|---|
| baselines | adaptive | 0.879 | 0.639 | 0.731 | 0.784 |
| baselines | no history | 0.835 | 0.559 | 0.625 | 0.700 |
| archetype clones | adaptive | 0.840 | 0.570 | 0.643 | 0.679 |
| archetype clones | no history | 0.838 | 0.502 | 0.575 | 0.598 |
| held-out bot clones | adaptive | 0.831 | 0.549 | 0.587 | 0.625 |
| held-out bot clones | no history | 0.808 | 0.499 | 0.559 | 0.515 |

The adaptive policy converts early chip lead into match wins better and wins 0 to 4 points more matches. The bb per
hand blocks are in the data files and show no clear difference. This is a measured modest effect, not a large one.

## Ablations

1. **Opponent history input**: the table above.
2. **League exploiter.** One exploiter (fresh policy trained only against the main agent) beat the main agent 80.6
   percent after 8.5 minutes. Adding it to the main agent's pool for one chunk made things worse: arm A (no exploiter)
   mean 0.890, minimum 0.807, 23 of 23 at 0.80 or more; arm B (exploiter in the pool) mean 0.881, minimum 0.775, 22 of
   23 (`reports/rl/data/eval_abl*.jsonl`). The field does not adapt, so exploiters are dropped, as the research note
   suggests. Single seed, weak evidence.
3. **PFSP floor.** Floor 0.05 caused forgetting (lag 0.94 to 0.73, maniac 0.795 to 0.725 within one chunk); floor 0.15
   with clip 0.1 repaired it. Weight of each past self snapshot was lowered to 0.3.
4. **Match-value network** (AlphaGo style value net; inputs chip share, blind level, hands to next level, hand number,
   button, 9 opponent statistics; 361,756 hand start samples from simulated matches of the policy against the 13
   training opponents; evaluated on held-out matches and on the 10 held-out bot clones):

| inputs | logloss (held-out matches) | AUC | logloss (held-out bot clones) | AUC |
|---|---|---|---|---|
| chip share and blind level only | 0.2568 | 0.799 | 0.4251 | 0.707 |
| plus hand number, button, hands to level | 0.2564 | 0.800 | 0.4261 | 0.707 |
| plus opponent model statistics (shipped) | 0.2366 | 0.843 | 0.4014 | 0.741 |
| constant | 0.3008 | | | |

   Export: `rl/models/match_value.npz` (keys `w0 b0 w1 b1 w2 b2`, `columns`, `names`); `rl.matchvalue.predict(path, feats)`
   returns P(win match). Sanity check at hand 41 (blind 200), neutral opponent statistics, chip share 0.1, 0.25, 0.4,
   0.5, 0.6, 0.75, 0.9 gives 0.30, 0.47, 0.66, 0.76, 0.84, 0.92, 0.97. It is monotone and above stack share at every
   point because it is the win probability of this policy, which has an edge (about 0.89 mean win rate). Against the
   coordinator's DP reference (zero edge gives value equal to stack share), this net is consistent in direction, not
   comparable in level. The all-in flip threshold check (decline flips under 54 to 60 percent equity) was not run
   against this net.
5. **Expert iteration (AlphaZero style):** not implemented. It needs the decision model search, which did not exist
   when this ran.

## Held-out status

The 10 per-bot clones were never sampled in training. **The 6 archetype clone tables were NOT refit without those 10
bots**: they come from the league fit on all bots, so the archetypes carry some statistics of the held-out bots, and
the per-bot numbers are an optimistic estimate of transfer to unseen bots. I could not refit because I had no access
to the league replay data; the coordinator's note about this arrived after training finished. A clean retest needs
refit archetypes, then `rl.train --clones <new npz>`.

## Runtime

`taskset -c 0` on gb10-d, `rl.latency` over 30 matches versus lag (2,237 decisions): mean 1.2 ms, p95 2.8 ms,
p99 2.9 ms, max 3.0 ms. The postflop hand strength enumerates opponent holdings with the pure Python evaluator and
dominates. A 3x slowdown for 0.5 vCPU gives about 3.5 ms mean and 9 ms worst, far below the 200 ms budget.
Weights are 330 KB. `tests/test_rl_runtime.py` plays the shipped bot and all 13 specialists through the strict SDK
engine. Test suite: 57 passed.

## Known weaknesses

* Maniac sits at the 80 percent line (0.81 fast engine, 0.797 to 0.80 arena); PoetAndCoder (held out) 0.80. The
  minimum Wilson lower bound over the 23 opponents is 0.758, so a rule requiring the lower bound at 80 percent is not
  met at 400 matches.
* Even against the current `chipzen_bot` bot (0.46 to 0.525 over 400 matches).
* Policy is stochastic (temperature 1.0); argmax was not tuned.
* No recurrent state; adaptation comes only from the nine summary statistics, and the field clones are memoryless.
* Exploiter and PFSP conclusions are single seed.

## Reproduce

```
ssh gb10-d
cd ~/poker-ai-lab-rl && . .venv/bin/activate
python -m pytest tests/test_rl_env.py tests/test_rl_clones.py tests/test_rl_rules.py tests/test_rl_runtime.py
bash tools/rl_main_chunk.sh 8.5 ablA --lr 1.5e-4 --clip 0.1
python -m rl.eval_fast --model ckpt/ablA/latest.npz --matches 400 --clones data/clones.npz
python -m rl.export ckpt/ablA/latest.npz rl/models/best.npz
python -m rl.eval_arena --model rl/models/best.npz --matches 400 --opp all --workers 6
```

## Round 2: distillation toward the exact maniac best response

Teacher: ManiacBR (`rl/teacher_br/`, vendored from `holdem-br`, exact best response to the maniac, 87.55 percent over 2000
arena matches). `rl/teacher.py` plays 500 matches against the maniac in the SDK engine, where the teacher acts with
probability 0.5 and the student otherwise (DAgger style), labels every visited state with the teacher's action (mapped to
the nearest legal discrete action) and writes `data/maniac_labels.npz` (18,365 states). `rl.train --distill ... --distill-w W`
adds W times a masked cross entropy toward those labels on a 1024 state minibatch every PPO minibatch.

One 7.5 minute chunk from the `ablA` checkpoint (6 workers, distill weight 0.5, label accuracy 0.98 by the end),
fast engine, 400 seat swapped matches, seed 21 (`reports/rl/data/eval_distill1.jsonl`, weights `rl/models/distill1.npz`):

| model | temperature | maniac | random |
|---|---|---|---|
| ablA | 1.0 | 0.812 | 0.863 |
| distill1 | 1.0 | 0.887 | 0.873 |
| ablA | 0.5 | 0.792 | 0.848 |
| distill1 | 0.5 | 0.873 | 0.860 |
| ablA | 0 (argmax) | 0.833 | 0.845 |
| distill1 | 0 (argmax) | 0.860 | 0.860 |

Distillation lifts the maniac by 7.5 points without hurting random. Temperature 1.0 is at least as good as argmax for
distill1 on both, so sampling at 1.0 stays the default. All 23 opponents for distill1 (temperature 1.0): minimum point
estimate 0.828 (qwentom-leap), minimum Wilson lower bound 0.787; maniac 0.887, PoetAndCoder 0.887. Real-arena numbers for
this checkpoint are not measured yet.

## Round 3: training against the heuristic HoldemBot (SDK engine workers)

The heuristic bot (`chipzen_bot/bot.py`, 102b05e) costs about 8 ms per decision and has a 620 line strategy with a
Monte Carlo equity step, so it was not ported to C. `rl/sdk_rollout.py` runs dedicated SDK engine workers that play the
real bot with the newest policy parameters and stream finished matches (obs, mask, act, logp, GAE advantage, return,
same potential shaped reward) to the learner (`rl.train --sdk-workers N --heur-batch K`); each PPO update waits for K
heuristic samples and mixes them with the C env batch (23 opponents, past main agents `ablA` and `distill1` as fixed
pool members via `--pool-dir`, ManiacBR distillation kept). Throughput: one SDK worker plays about 1.5 matches per
second (about 130 decisions per second); 3 workers plus the C learner gave about 4.9 s per PPO iteration.
Also: `Tracker` now takes the dealer from the `round_start` message (`state.dealer_seat`), falling back to the small
blind poster in the action history, then to the parity rule (`tests/test_rl_runtime.py::test_tracker_dealer_follows_the_server`).

Proving chunk (7.5 minutes, 4 processes, from distill1, `rl/models/heur1.npz`, about 1,900 heuristic matches):
SDK arena vs the heuristic, 400 matches, seed 11: heur1 0.5175 (CI 0.469 to 0.566), distill1 0.4675 (0.419 to 0.516).
The difference is inside the noise of one 400 match run; the long run is what has to move it. Launch script:
`tools/rl_heur_long.sh`.
