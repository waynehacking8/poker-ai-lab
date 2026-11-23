# Roadmap: the long-term strongest Chipzen HUNL bot

Set 2026-11-22. Wayne's goal: the long-term strongest bot, a "future king". The Season 16 deadline does
not matter. The Season 16 entry is `poker-ai-lab-v4` (rl-fb2-900 plus the all-in answer of S0, image sha256
0291ee39...) since 2026-11-22 18:45 UTC, Wayne approved. `poker-ai-lab-v3` (rl-fb2-900) stays uploaded.

## Revision 2 (2026-11-23): the problem from first principles

Wayne: "The biggest fault that you made is thinking too narrowly." S0, S2 and the diversity slice I had
proposed after experiments 14.11 were one move made bigger: enlarge the opponent list of a reactive policy.
Such a policy is only as robust as its training distribution, so every style outside it is a new hole, and
the all-in jam was one. This revision decomposes the objective first and orders the work by measured headroom.

**Objective.** The most season wins, then fewer hands per win, against a real field that changes between
seasons. Runtime: 0.5 vCPU, 256 MB, 5 s per action, Python and numpy. Offline: gb10-d.

**Measured facts.**
* **Short matches.** 330 poker replays: median 26 hands, and 140 (42%) end before the first blind step at
  hand 21 (`tools/analyze_chipzen_replays.py`). A few big pots decide a match.
* **The opponent is named at match start.** `seats[].display_name` is "the participant's platform name
  (for a bot, the bot's name)" (chipzen-sdk `docs/protocol/TRANSPORT-PROTOCOL.md`, main at aa8c55c,
  2026-11-22). `participant_id` changes every match in the replays (51 ids over Kimiko's 51 matches), so
  the name is the key. Names carry versions (Deep_Thought-v12, v17, v18).
* **The field's styles.** 12 of 51 bots play styles none of our opponents play (14.11).
* **No ground truth yet.** Our bots appear in none of the replays. The Season 16 round robin (24 to 27 Nov)
  plays v4 against every entrant.

**Levers.** Against one opponent, our result is a floor plus what we exploit on top of it.
1. **Floor:** what the best response to us wins. It protects against strong, unseen and adaptive bots.
   S2 and S2b raise it; E3 measures it.
2. **Exploitation:** what we take beyond the floor. A reactive policy exploits only styles it trained on.
   An explicit opponent model plus a decision procedure that best-responds to it covers every style the
   model can express, including unseen ones. This is the adaptive decision model Wayne asked for on
   2026-11-21: an online model with a population prior, a decision procedure, and a safety blend while the
   belief is broad.
3. **Measurement:** real arena results are the judge. The proxies (E1 to E5) are for iteration.

Review: plan-verifier REVISE twice (4 blockers, then 3), each fixed in this text; the second was the cap,
so no third review ran, and Wayne's standing approval (2026-11-23) carries it.

**Headroom before building.**
* **M1 (running since 02:41 UTC):** best-response fine-tunes of fb2-900 against one field bot each,
  90 minutes, 3 SDK workers (`tools/rl_br.sh`): `br_ashwing` against `ext:ashwing`, and `br_autofast`
  against `ext:autodidact_fast` (the same code as `ext:autodidact` with fewer trials; the full bot played
  7 matches a minute, too slow to train on). `tools/m1_eval.sh` then plays fb2-900 and both fine-tunes on
  seed 21, fresh for all three: 800 matches against `ext:ashwing`, 400 against `ext:autodidact`. fb2-900's
  card reads 72.75% and 74.5% against them (E2). A fine-tune is a lower bound on what exploiting one known
  opponent is worth; its result against the other bot shows what specializing costs.
* **M2:** the floor's headroom is E3: a fresh exploiter still wins 71 to 78% after S2 (14.10).
* **M3:** the Season 16 round robin replays of v4 give the first real results per opponent. They come in
  within days and move nobody's rating, so no challenge matches are played for measurement.

**Decision rule after M1.** The statistic is the gain: a fine-tune's win rate on its own target minus
fb2-900's, with a 95% Newcombe interval of the difference. `ext:` bots are unseeded, so the two samples are
unpaired. The interval resolves a gain of about 4.4 points at 800 matches a side and 6.2 at 400.
* **Positive** (lower bound above zero on either target): exploitation headroom is real, and X2 is
  specified right after X1.
* **Otherwise inconclusive:** a 90-minute reactive fine-tune only bounds headroom from below, so a miss
  does not show the headroom is small. X2 then waits for M3's per-opponent results and X1's predictive
  gains.
* X1 runs in both branches (CPU only, and both need it). The floor work (S2b, then S3) runs in parallel.

**New order.**
1. S2b finishes (floor). M1 and M3 measure.
2. **X1 opponent model** (below).
3. **X2 decision procedure:** a depth-limited search against the X1 model, with our policy as the leaf
   and rollout value, blended toward the floor policy while the posterior is broad (Ganzfried and
   Sandholm 2015 safe exploitation; Johanson et al. 2007 restricted Nash response). Acceptance: E2 and
   held-out style cells (rule bots for the 14.11 gap styles) improve, E3 no worse, decisions inside 1 s
   at 0.5 vCPU. Specified after X1, and before M3 only if M1 is positive.
4. S3 (showdown memory) and S4 (range belief) become X1 inputs. S6 becomes X2. S5 and S7 stay as A/B
   experiments.

### X1. Opponent model

* **Outcome:** a runtime model P(opponent action | public state, opponent name, match so far) and its
  measured predictive quality.
* **Data:** the 330 poker replays now (2026-11-19 22:10 to 2026-11-21 11:41 UTC); the Season 16 replays
  later, as a second test set across a season boundary. Both seats of every replay are modeled. Split by
  `start_time`: the latest 30% (99 matches, from 2026-11-21 02:26 UTC) are held out. The prior and the
  profiles are fit on the training split only.
* **Held-out subsets,** counted before any fitting (2026-11-23):
  1. **known names:** held-out actions of names with at least N = 200 actions in the training split,
     15,426 actions in 91 matches;
  2. **unseen names:** held-out actions from hand 11 on, of names with no training action, 1,425 actions
     in 10 matches, 4 names.

  A 20% split would leave the unseen subset 5 matches and 2 names, hence 30%. A subset under M = 10
  matches or 3 names is reported NOT TESTED, never a pass.
* **Model:** actions in five classes (fold, check or call, bet or raise up to the pot, above the pot,
  all-in). Three layers:
  1. a population prior: a small numpy model over public features (street, position, facing bet over pot,
     stack depth in big blinds, last action);
  2. a per-name profile: Dirichlet counts per context bucket (street by facing bet bucket), shrunk toward
     the prior;
  3. an in-match update of the same counts after every opponent action.
* **Acceptance:** mean log loss per opponent action, bootstrap 95% interval of the difference over
  matches, each reported next to its subset sizes:
  1. on known names, prior plus name plus in-match beats prior plus in-match (the name adds
     information), interval above zero;
  2. on unseen names, prior plus in-match beats the prior alone, interval above zero;
  3. runtime: under `docker run --cpus 0.5 --memory 256m` on gb10-d, replaying the held-out actions in
     order, update plus prediction under 5 ms at p99, model files under 5 MB. gb10-d is aarch64 and the
     host x86, so this is a proxy; X2 measures the whole bot on the deployed image.
* **Non-goals:** hand ranges (S4 later), runtime integration (X2), any upload.
* **Selection:** every choice is made on a validation split, the latest 20% of the training split by
  `start_time` (46 of its 231 matches): the prior's features and hidden size, the context bucket edges,
  the shrinkage strength of the profiles, and the weight of the in-match update. The model is then refit
  on the whole training split and frozen. Each frozen model is scored on the held-out subsets once.
* **Stop:** each acceptance has its own outcome.
  1. Acceptance 1 fails: per-name profiles are not used, and X2 is specified with the prior and the
     in-match update only.
  2. Acceptance 2 fails: X1 ends with the finding recorded. A revised in-match update is a new revision,
     tested on fresh data (the Season 16 replays), or labeled as reusing this held-out set.
  3. Acceptance 3 fails: X1 stops, the measured p99 and size are recorded, and the next step is chosen in
     a new plan revision.
* **Ownership:** X1 owns `rl/oppmodel.py` (the model), `tools/oppmodel_fit.py` (fit, select, score), the
  artifact `rl/models/oppmodel.npz`, `logs/x1/` on gb10-d, and experiments section 14.13 (14.12 is M1).
  It touches nothing S2b or M1 owns (`rl/train.py`, the `tools/rl_s2.sh` and `tools/s2_*` scripts,
  `tools/rl_br.sh`, `tools/m1_eval.sh`, `ckpt/`, `pool_s2b/`, `logs/s2b/`, `logs/m1/`).
* **Budget:** CPU only, at most 4 box-hours, at most 2 cores on gb10-d while S2b or M1 run. Acceptance 3
  is measured only on a quiet box (no training or evaluation running).
* **Limit:** the replays span 37 hours, so names barely change version across the split; the Season 16
  replays retest acceptance 1 across a season.
* **Rollback:** nothing is deployed; the king stays v4.

## Evidence that sets the order

* **Blueprint** (experiments 14.6): fb2-900 wins about 61%. The clearest leak is calling Blueprint's river
  shoves: 6 wins in 58 calls, -342k chips per 400 matches.
* **Exploitability** (2026-11-22): exploiter ex1 started as fb2-900 and trained only against it in the C
  engine for about 2 minutes, 400 iterations (`tools/rl_exploit.sh`).
  * In the SDK engine it beats fb2-900 96.5% [94.2, 97.9] over 400 matches, seed 3.
  * `tools/chipflow.py`: the exploiter almost never folds preflop (0.5%) and bets after the flop.
    fb2-900 folds after the flop 4759 times and loses 2.72M chips.
  * fb2-900 wins against the current field, but a counter-strategy trained against it wins easily.
  * For a long-term king, robustness is the first gap.

## Eval card (every candidate, one JSON per candidate)

| id | metric | how | target |
|---|---|---|---|
| E1 | field | 23-opponent league, fresh seed pairs 200 to 399 | at least 80% each, Wilson lower bound reported |
| E2 | real bots | Ashwing family, Wolf family, autodidact, SDK reference, seeded Blueprint; win rate and all-in adjusted chip EV per hand (`tools/chipflow.py`) | no family below the previous king |
| E3 | exploitability | a fresh exploiter from the candidate, 400 iterations in the C engine, then 400 SDK matches against the candidate | lower is better; fb2-900 is 96.5% |
| E4 | lineage | head to head against fb2-900, 400 seeded matches, seed 3 | at least the fb2-900 mirror on the same seeds (45.0%), with the Wilson interval reported |
| E5 | extreme bots | jam, jam_half, jam_post, minraiser, station, maniac, lag and the other baselines (defined in S2b) | no opponent below v4's interval |
| E6 | held-out styles | rule bots for the four 14.11 gap styles (raise then station, sticky over-bettor, tight then sticky, never folds preflop), plus `ext:ashwing`, `ext:ashwing_search`, `ext:ashwing_hive`, `ext:autodidact` and the Wolf family; none of them used in any training, tuning or selection of the candidate | better than the previous king on average, no cell below its interval |
| E7 | real arena | the entered bot's Chipzen replays per opponent (Season 16 on), with the opponent's name seen or unseen before | the judge of record |

A new king must hold E1, E2 and E4 and improve E3, or improve E2 with E3 no worse.
Added 2026-11-23 (Revision 2): a method is called universal only when it improves E6, which it was never
built or tuned on, and E7 confirms it.

## Budgets and stops (every slice)

* Each slice states a box-hours budget on gb10-d and numeric stop conditions before it starts.
* When an acceptance check fails at its cap, the slice stops. The failure is recorded as the finding,
  and the next step is chosen in a new plan revision. Scope is never widened silently.
* A crash of a long run stops the slice until the cause is known.

## Slices

Each slice keeps the previous king as the rollback. Code lands on `holdem-rl`, results in experiments.md
section 14.x, and state in HANDOFF.

### S0. All-in fix (inserted 2026-11-22, before S1)

Wayne found it online: spamming all-in beats v3. Measured: fb2-900 wins 49.0% [44.1, 53.9] against `jam`
(shoves every hand), 400 matches, seed 3. Facing a preflop shove it called 16% of hands with 60 to 70%
equity against a random hand, and took 2 of 533 profitable calls in the first five hands of a match.
Training never showed it an opponent that shoves any two cards.

* **Regression bots** (`holdem/opponents.py` EXTREMES, not in "all" or the league): `jam`, `jam_half` (any
  two, half its decisions), `jam_post` (shoves after the flop only), `minraiser`.
* **Decision at play time** (`rl/allin.py`, tables from `tools/allin_tables.py`): an online estimate of the
  opponent's preflop shove frequency and range, and a backward induction over (hand, stack) that gives the
  match value of calling and folding. Once the frequency reaches 0.7 (three shoves in three chances), a
  policy fold of a preflop all-in becomes a call when calling has the higher match value, and the small
  blind folds trash up front instead of limping into the shove.
* **Gate:** at least 62% against `jam` (known-range ceiling 65.5%), the league unchanged, the real bots,
  Blueprint and head to head no worse than fb2-900.
* **Not done here:** training against the shover family. It goes into S2's opponent pool together with
  the exploiters.
* **Result (2026-11-23, experiments 14.7):** gate passed. jam 49.0 -> 62.75% [57.9, 67.3] (ceiling 65.5%).
  The league, Wolf family, SDK reference, seeded Blueprint and the seeded head to head against v3 are
  identical. The answer fired 0 times in 2400 matches against v3, the Ashwing family and autodidact. Fresh
  verifier CONFIRMED. Entered as poker-ai-lab-v4 on 2026-11-22 18:45 UTC (Wayne approved).

### S1. Measurement harness (step 1)

**Owned files** (holdem-rl): `bpopp/server.py`, `bpopp/opponent.py`, `holdem/arena.py`, `rl/eval_arena.py`,
`tools/chipflow.py`, new `bpopp/Dockerfile.v011`, new `tools/exploit_probe.sh`, new `tools/eval_card.sh`,
`tools/README.md`.

**Non-goals:** no change to `rl/train.py` or the C engine. The probe uses the existing `--iters` and
`--seed` flags.

1. **Seeded Blueprint.** The blueprint samples with the global legacy `np.random`
   (`np.random.choice` in `src/engine/solver/mccfr/policy.py` in the image).
   * `bpopp/server.py` calls `np.random.seed(seed)` on `match_start` when the message carries `seed`.
     Without it nothing changes, which is today's behavior.
   * `bpopp/opponent.py` gets `set_seed(seed)` and sends `seed` with `match_start`. An image whose server
     predates this ignores the extra field.
   * `holdem/arena.py run_one` and `tools/chipflow.py run_one` call `opp.set_seed(pair_seed * 13 + hero_seat)`
     when the opponent has that method.
   * `bpopp:v011` is built on top of v010, so only the server changes:
     * `bpopp/Dockerfile.v011` is `FROM bpopp:v010` plus `COPY server.py /srv/server.py`.
     * Build command on the box: `docker build -f bpopp/Dockerfile.v011 -t bpopp:v011 bpopp`.
   * The poker-solver code, the venv and the base image are untouched. `bpopp:v010` stays on the box, the
     default in `opponent.py` stays v010, and `BP_IMAGE` selects the image.
   * Every bp100 run (eval_card.sh and the acceptance runs) exports the same `BP_DATA`, `BP_RUN`, `BP_AT` and
     `BP_THRESHOLD` as `tools/fb_test.sh`. Only `BP_IMAGE` changes (v011, or v010 for the control).
2. **Per-match rows.** `run_arena` keeps its aggregate output and also returns its rows. `rl.eval_arena`
   gets `--rows PATH`, which writes every match (seed, hero_seat, hands, won, final stacks) as JSON lines,
   sorted by (seed, hero_seat).
3. **`tools/exploit_probe.sh INIT_CKPT TARGET_NPZ NAME TRAIN_SEED EVAL_SEED`:**
   * It refuses to start if `ckpt/probe_NAME` exists, so a probe never resumes an old run.
   * It runs `python -m rl.train --out ckpt/probe_NAME --init INIT_CKPT --fixed-opp TARGET_NPZ --iters 400
     --seed TRAIN_SEED` with ex1's settings: `--workers 8 --envs 96 --steps 4000 --lr 3e-4 --clip 0.2
     --snap-every 25`.
   * It then evaluates `ckpt/probe_NAME/latest.npz` against `model:TARGET_NPZ` with `rl.eval_arena`
     (400 matches, seed EVAL_SEED, 4 workers).
   * It writes `logs/exploit_probe/NAME.json` holding the eval line plus the training seed and iteration
     count.
4. **`tools/eval_card.sh NAME POLICY_NPZ INIT_CKPT`** writes `logs/eval_card/NAME.json` with:
   * **E2:** `rl.eval_arena`, 400 matches each.
     * Seed 5: ext:ashwing, ext:ashwing_search, ext:ashwing_hive and ext:ashwing_v2 (the fb_watch seed).
     * Seed 3: ext:wolf, ext:wolf_v1, ext:wolf_v2, ext:wolf_v5, ext:sdkref and ext:autodidact (the fb_test
       seed).
     * Seed 3: bp100 with `BP_IMAGE=bpopp:v011`, 2 workers.
     * Chip EV per hand, all-in adjusted, against bp100 from `tools/chipflow.py` (seed 3).
   * **E3:** `exploit_probe.sh` with TRAIN_SEED 1 and EVAL_SEED 3.
   * **E4:** `rl.eval_arena --opp model:rl/models/fb2_it000900.npz`, 400 matches, seed 3.
   * E1 stays the league gate (`tools/league_add.sh` plus the fresh-seed driver) and is recorded by
     reference.

**Rollback:** every change is additive or behind an option. Reverting the S1 commits and using
`BP_IMAGE=bpopp:v010` restores today's harness.

**Budget:** at most 6 box-hours on gb10-d and at most 2 probe pairs, the second at 800 iterations.

**Stop conditions:**
1. If the seeded v011 row files are not byte-identical, S1 stops and reports it. The image source is not
   modified. One possible cause is numba-jitted sampling with its own RNG.
2. If the probes still disagree at 800 iterations, S1 stops and records the variance.
3. If a probe or eval run crashes, S1 stops until the cause is known.

**Acceptance:**
* **Repeatable Blueprint.** Two v011 runs of fb2-900 against bp100 (400 matches, seed 3, `--rows`) give
  byte-identical row files. That holds both with the same `--workers` and with 2 against 3 workers, which
  shows that a reused container does not leak RNG state between matches.
* **Negative control.** A run with `BP_IMAGE=bpopp:v010` (unseeded) differs from the seeded rows in at least
  one row, and it still completes with the new `opponent.py`.
* **Images.** `docker images` on the box lists both bpopp:v010 and bpopp:v011. `docker history bpopp:v011`
  shows exactly one layer over v010 (the server.py COPY), and the two `/srv/server.py` files differ only by
  the seed lines.
* **Probe.**
  * Two probes of fb2-900 (TRAIN_SEED 1 and 2) each create a new checkpoint directory and log exactly
    400 iterations.
  * Their Wilson intervals overlap each other and ex1's [0.942, 0.979]. If they do not, the pair is run
    once more at 800 iterations. If they still disagree, S1 stops, and the variance is recorded as the
    finding.
* **Baseline.** `logs/eval_card/fb2-900.json` exists with the named E2 opponents and seeds, plus E3 and E4.

**Result (2026-11-22, experiments 14.9):** acceptance met. Seeded v011 rows are byte identical (2 and 3
workers), v010 differs in 310 of 400, v011 is one layer over v010, probes read 97.25 and 97.5 (overlapping
ex1's 96.5), and `logs/eval_card/fb2-900.json` is the baseline card.

### S2. League with exploiters (step 3)

**Owned files** (holdem-rl):
* new `tools/rl_s2.sh`, `tools/s2_exploiters.sh` and `tools/s2_screens.sh`;
* `rl/sdk_rollout.py`: `make_opp` also builds the `holdem/opponents.py` EXTREMES bots;
* `rl/train.py`, three changes:
  1. a `--pool-w` option, the base PFSP weight of pool entries (default `--snap-w`, so old recipes keep
     their weights);
  2. pool entries come first in the opponent list, so their `snap:j` keys no longer shift as the snapshot
     window fills;
  3. win rates of pool entries are kept per file name. When the pool's file list changes, each surviving
     file carries its win rate to its new `snap:j` key, a new file starts at 0.5, and the log row records the
     file names (`"pool"`);
* `tools/README.md`.

**Non-goals:** no change to the C engine, the features or the network size. No upload.

**Measured inputs:**
* gb10-d has 20 cores.
* fb2 (`tools/rl_fb2.sh`, alone on the box) reached iteration 400 at 74 minutes and 900 at 167 minutes, about
  5.4 iterations per minute.
* In fb2 each pool policy drew about 2% of the C-engine matches, and the C engine played 46% of all matches.

1. **Launcher and main agent:** `tools/rl_s2.sh OUT INIT [MINUTES]`, started as
   `rl_s2.sh s2 ckpt/fb2/it000900.npz 300` after the S1 baseline card has finished.
   * **Before the main run starts**, it copies the final ex1 (`ckpt/ex1/latest.npz`) to `pool_s2/x000.npz`:
     a temp name that does not match `*.npz`, then a rename.
   * **Main run:** `tools/rl_fb2.sh`'s command with these changes:
     * `--pool-dir pool_s2 --pool-w 1.0` instead of `--pool-dir pool_gen`. `rl/train.py` keeps the last 4
       files by name, so the pool holds the newest exploiters, and fb2's two pool policies leave.
     * The SDK round robin gains `jam` and `jam_half` (2 of 8 slots).
     * `--max-minutes 300`. Everything else stays as in fb2.
   * **Exploiter loop and screens:** `tools/s2_exploiters.sh` and `tools/s2_screens.sh`, both started with
     the main run's pid.
   * **When the main run ends**, the launcher waits for both and writes `logs/s2/end.txt` with the reason:
     * `stop N` when `logs/s2/STOP` exists;
     * `crash` when the main run exited nonzero without a STOP file;
     * `max-minutes` otherwise.
   * **Weights:** at `--pool-w 1.0`, a fresh exploiter (main agent win rate near 0.03) weighs about 4.4.
     fb2's other C-engine opponents weigh about 19.5 in total at fb2's final win rates. That total is
     consistent with each fb2 snapshot drawing 2.2% at weight 0.37. So one exploiter makes about 18% of
     C-engine matches, and four make about 47%. These are upper bounds: a new file starts at win rate 0.5
     (weight 1.6) until the EMA catches up, so the screens measure the real share.
2. **Exploiter loop** `tools/s2_exploiters.sh MAIN_PID MAIN_OUT POOL [CYCLES=1000]`. The cycles are
   k = 1 to CYCLES, and the loop refuses to start if `POOL/x001.npz` exists. Each cycle k:
   * waits until `MAIN_OUT/latest.npz` is newer than the last target;
   * copies it with a temp name plus rename to `ckpt/s2x/target_k.npz`, and checks that `np.load` reads the
     policy and value weights, retrying up to 3 times;
   * runs `rl.train --out ckpt/s2x/c_k --init target_k --fixed-opp target_k --iters 400 --seed k --workers 4
     --steps 8000 --envs 96 --lr 3e-4 --clip 0.2`. That is 4 × 8000 decisions per iteration, the same as ex1
     and the probe at 8 × 4000;
   * copies `c_k/latest.npz` to `POOL/x{k:03d}.npz` with a temp name plus rename.

   Each exploiter restarts from the current main agent, as AlphaStar's main exploiters reset. The loop exits
   0 when MAIN_PID is gone. If an `rl.train` cycle fails, it writes a log line and exits 1, which is stop
   condition 3.
3. **Screens** `tools/s2_screens.sh MAIN_PID OUT`. It waits for `ckpt/OUT/it000200.npz`, `it000400` and
   `it000600` in turn. For each checkpoint C at iteration N:
   * `exploit_probe.sh C C s2_itN 1 3`, output `logs/exploit_probe/s2_itN.json`;
   * `rl.eval_arena --model C --opp ext:ashwing,ext:ashwing_search --matches 400 --seed 5 --workers 4`, output
     `logs/s2/screen_itN.jsonl`;
   * from `ckpt/OUT/train.jsonl` since the last screen: the pool file names, the pool keys' match count, win
     rate and share of C-engine matches, and the `x{k}` files added. Output `logs/s2/screen_itN_pool.json`.

   It then applies stop conditions 1 and 2. On a stop it writes `logs/s2/STOP` (number and reason) and
   kills MAIN_PID. When the main run ends past the last screened iteration, it screens the last
   `itNNNNNN.npz` the same way. Expected timing: 600 at about 110 minutes alone, at most 1.6 times slower with
   the loop and screens, so well inside the cap.

**Budget:** 300 minutes of main training with the loop and screens running alongside, at most 6 box-hours on
gb10-d.

**Stop conditions:**
1. **No gain.** If the probe at iteration 400 is still at 90% or more while the pool's share of C-engine
   matches since iteration 200 is at least 20%, S2 stops. The finding is that training against the newest
   exploiters at that share does not cut exploitability at this budget. If the share is under 20%, the
   finding is "under-sampled" instead: S2 also stops, and the next plan revision raises `--pool-w`.
2. **Field cost (the tripwire).** If both held-out Ashwing bots fall below fb2-900's pooled rate minus two
   standard errors of one 400-match run at a screen, S2 stops. Those lines are 69.5 for ashwing (fb2-900
   1183/1600 over four seed-5 runs) and 68.3 for ashwing_search (1164/1600). Single runs of fb2-900 range
   72.75 to 75.25 and 71.5 to 74.75. The finding is that the robustness costs field strength.
3. **Crash.** If the main run crashes, or the exploiter loop exits 1, S2 stops until the cause is known.

**Acceptance.** The candidate is the screened checkpoint with the lowest probe whose screen did not trigger
stop condition 2.
* **E3:** the probe is under 70%. fb2-900's probes read 96.5, 97.25 and 97.5%.
* **E1:** the league gate holds, 23/23 at 80% or more, fresh seeds.
* **E2:** `tools/eval_card.sh`, with no family below the fb2-900 card beyond its interval.
* **E4:** a seeded head to head against `model:rl/models/fb2_it000900.npz` (RLBot with the all-in answer, as
  entered in poker-ai-lab-v4) of at least the 45.0% mirror.
* A fresh verifier confirms the claim. A swap is then put to Wayne.

**Rollback:** the changes are additive, and the `rl/train.py` defaults keep old recipes' weights.
poker-ai-lab-v4 (image sha256 0291ee39...) stays entered until Wayne approves a swap, and poker-ai-lab-v3
stays uploaded.

**Result (2026-11-23, experiments 14.10):** no stop fired, and the run ended at max-minutes (iteration
1835). Acceptance is not met, because E3 stayed above 70%. Screen probes read 93.0, 74.75, 88.75 and 74.5
at iterations 200, 400, 600 and 1800, and probes repeated on one checkpoint spread from 74.75 to 87.0. The
Ashwing pair never fell below both lines at once: ashwing read 65.75 to 73.75 (65.75 at it600) and
ashwing_search 70.25 to 72.5. The it400 card matches the fb2-900 card within its
intervals, and E4 at it400 reads 44.75 against the 45.0 mirror. The exploiters' own end-of-cycle win rate
fell from 0.90 (cycles 1 to 10) to 0.77 (cycles 61 to 73). Against a fresh 400-iteration exploiter, the
chip loss fell from 2.51 bb per hand (fb2-900) to 0.84 (it1800). The leaks are the same ones, smaller:
post-flop folds, and shoves called by better hands.

### S2b. Continue S2 (revision 1)

S2 was still improving when the clock ran out, so S2b resumes it for another 300 minutes under the same
recipe. The only recipe changes are the bookkeeping fixes of holdem-rl a0ba32c and 0670e94: the pool rotates
right after a log row, and a match in progress against a slot whose file changed is restarted unreported, so
each file's win rate gets only its own matches. E3 becomes a pooled probe, because single probes of
one checkpoint spread about 12 points.

**Owned files** (holdem-rl): `tools/rl_s2.sh`, `tools/s2_exploiters.sh`, `tools/s2_screens.sh`, new
`tools/probe_pool.py`, `tools/README.md`.

**Non-goals:** no change to `rl/train.py`, the C engine, the features, the network or the recipe flags. No
upload.

1. **`rl_s2.sh OUT INIT [MINUTES] [FROM]`.** Without FROM nothing changes. With FROM, a finished S2 run:
   * It refuses unless `logs/FROM/end.txt` and `ckpt/FROM/state.pt` exist and `ckpt/OUT` does not.
   * It copies `ckpt/FROM/state.pt` to `ckpt/OUT/state.pt` (temp name, then rename). `rl/train.py` resumes
     from it: weights, optimizer, self-play snapshots, win rates and iteration count. INIT is then unused.
   * It copies the last 4 files of `pool_FROM`, by name, into `pool_OUT` (temp names, then renames)
     instead of x000.
   * The exploiter loop starts at cycle START, one past the number of the last copied file, so new files
     sort after the copied ones and the pool keeps the 4 newest.
   * Screens run at IT0 + 400, + 800, + 1200 and + 1600, rounded up to a multiple of 100, where IT0 is the
     state's iteration. When the run ends past the last one, the last checkpoint is screened as before.
   * The S2 state predates a0ba32c and carries no per-file pool win rates, so the 4 copied files start
     at 0.5 until the moving average catches up (a few log rows).
2. **`s2_exploiters.sh MAIN_PID MAIN_OUT POOL [CYCLES] [START]`.** Cycles run from START (default 1). It
   refuses to start if `POOL/x{START}.npz` exists.
3. **`s2_screens.sh MAIN_PID OUT [ITERS]`.** ITERS is the list of screen iterations (default `200 400 600`).
   Stop condition 1 stays tied to iteration 400, so it cannot fire in S2b.
4. **`tools/probe_pool.py NAME...`** prints the pooled win rate, match count and Wilson 95% interval of the
   named `logs/exploit_probe/NAME.json` files.

Started as `rl_s2.sh s2b ckpt/fb2/it000900.npz 300 s2` once the S2 it1800 card has finished.

**Budget:** 300 minutes of main training with the loop and screens, at most 6 box-hours on gb10-d, plus three
fresh probes for the candidate (about 7 minutes each).

**Stop conditions:** S2's condition 2 (field cost, the same Ashwing lines) and condition 3 (crash).

**Acceptance.** The candidate is the screened checkpoint of S2 or S2b with the lowest screen probe whose
screen did not trigger condition 2. The screen probe only picks it: as the minimum of about nine noisy
probes it reads low, so it is left out of E3.
* **E3:** three fresh probes of the candidate C (`ckpt/R/itN.npz`, screen name `R_itN`), each with its own
  train seed and its own eval seed. Every screen probe used eval seed 3, so the same 400 deals would carry
  the selection's luck, and the fresh probes never use seed 3:
  `bash tools/exploit_probe.sh C C R_itN_fS S 1S` for S = 2, 3, 4 (eval seeds 12, 13 and 14). S2's
  existing `_t2` probes (eval seed 3) do not count. `python tools/probe_pool.py R_itN_f2 R_itN_f3 R_itN_f4`
  gives the pooled rate over the 1200 matches, which must be under 70%.
* **E1, E2 and E4** as in S2.
* **E5, the extreme bots.** E1 to E4 hold no shover, and that is how the all-in hole went unseen (14.7).
  `python -m rl.eval_arena --model C --opp jam,jam_half,jam_post,minraiser,station,maniac,nit,random,reference,lag,station_raiser
  --matches 400 --seed 3 --workers 4`, with the all-in answer on as deployed. No opponent may fall below v4's
  reading beyond its interval (`logs/allin/fb2_900_on.jsonl` on gb10-d: jam 62.75, jam_half 84.5, jam_post
  84.5, minraiser 96.0, station 97.75, maniac 85.5, nit 97.5).
* A fresh verifier confirms the claim. A swap is then put to Wayne.

If E3 is still not met, the finding is recorded, and S3 starts from S2b's final weights.

**Rollback:** every new argument is optional, and the old calls behave as in S2. poker-ai-lab-v4 stays
entered.

### S3. Showdown memory (step 2, part 1)

* **New tracker statistics** from cards shown at showdown, by street and bet size. Example: shown hand
  strength after the opponent's river bet of at least the pot.
* **Same features in the C engine** (`rl/fastenv.c`), with `tests/test_rl_env.py` parity.
* **Surgery:** new input weights start at zero, so the first checkpoint plays exactly like its parent.
* **Acceptance:** the Blueprint river call-off leak shrinks, with E1 to E4 no worse.

### S4. Range belief (step 2, part 2)

* **A belief network** trained in simulation, where hole cards are known, predicts the opponent's hand class
  from the public betting and the tracker.
* **Equity features** use that range instead of a random hand.
* **Acceptance:** E2 chip EV rises against the solver-style opponents (Blueprint, our MCCFR blueprint), and
  E3 is no worse.

### S5. Wider bet set (step 4)

* The AlphaHoldem set: bets of 1/2, 3/4, 1, 3/2 and 2 pots, plus all-in.
* Needs the C engine, the mask and amounts, and a new action head initialized from the old one.
* **Acceptance:** E2 chip EV rises, and the 30 to 60 bb band against Blueprint turns positive.

### S6. Decision-time search (step 5)

* **River re-solve** with the `search/` CFR+ (about 0.5 s), using the S4 range as the opponent range.
* **Ganzfried and Sandholm safe exploitation.**
* **Acceptance:** search on beats search off in E2 and E3, at 0.5 vCPU with decisions well inside 5 s.

### S7. Capacity (step 6)

* An A/B of a wider network on the S2 to S6 setup, judged on E1 to E4.

## Order and parallelism

1. S1 first, because every later slice is judged with it.
2. The `ex1` exploiter run finished (30,790 iterations): fb2-900 wins 1.0 to 1.5% against it
   (experiments 14.8). Its snapshots are the first pool members for S2.
3. S3 can be built while S2 trains, because both touch only their own files until S3's retrain.
