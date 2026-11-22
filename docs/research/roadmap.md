# Roadmap: the long-term strongest Chipzen HUNL bot

Set 2026-11-22. Wayne's goal: the long-term strongest bot, a "future king". The Season 16 deadline does
not matter. The Season 16 entry is `poker-ai-lab-v4` (rl-fb2-900 plus the all-in answer of S0, image sha256
0291ee39...) since 2026-11-22 18:45 UTC, Wayne approved. `poker-ai-lab-v3` (rl-fb2-900) stays uploaded.

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

A new king must hold E1, E2 and E4 and improve E3, or improve E2 with E3 no worse.

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
