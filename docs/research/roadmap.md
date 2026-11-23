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

**Progress is distance to the ceiling, not to v4** (Wayne, 2026-11-23: "my point was never swapping today,
because v4 cannot possibly be the best"). v4 is a reference point and the rollback, never the target. Each
result is read against what is attainable, and the gaps measured so far set the order:

| lever | where we are | ceiling | gap |
|---|---|---|---|
| floor: a fresh exploiter's win rate against us (E3) | v4 96.5%; S2 it1800 78.7% | 50% (unexploitable) | about 29 to 47 points |
| exploitation of a known bot (M1) | v4 75.5% vs Ashwing, 79.25% vs autodidact | the single-bot fine-tune: 90.25% and 90.25% | 11 to 15 points per bot |
| a strong bot: the real Blueprint (E2) | v4 59.0%, S2 it1800 57.0% | unknown, above 59% | open |

A candidate is worth more only when it moves one of these gaps without opening another. The swap window
is a side effect: a candidate enters when it is clearly better, whatever the date.

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
* **M1b (added 04:19 UTC, after M1's chip flow showed a whole-strategy shift worth about 20 points against
  Ashwing):** one fine-tune on the mixture `ext:ashwing,ext:autodidact_fast`, same recipe, evaluated like
  M1. If it holds both exploits, the generalist's gap is its training population, and X2 can be a
  policy that takes X1's predictions as inputs, trained on a broad population. If it falls well short of the
  two single fine-tunes, X2 needs explicit conditioning or search.
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

### M1 result and the X2 choice (2026-11-23 05:01 UTC)

* **M1 is positive.** On seed 21, br_ashwing wins 722 of 800 against `ext:ashwing` (90.25%), fb2-900 604 of
  800 (75.5%): gain 14.75 points, Newcombe 95% [11.1, 18.4]. The autodidact half and M1b land later and are
  recorded in experiments 14.12; they do not change the branch.
* **The gain is a whole-strategy shift** (chip flow, seed 31): the first preflop action is a raise 64.7% of
  the time (fb2-900 32.3%), showdowns where we bet last turn from -261k to +531k chips, and river shoves
  fall from 635 to 248 with better equity when called. A search that acts only on river and all-in
  decisions would miss most of it.
* **Choice: X2 is a learned decision procedure under an explicit opponent model.** The policy already reads
  in-match opponent counts (the `Tracker` in `rl/features.py`, `NST` = 15 slots of which 0 to 13 are used,
  mirrored as `stats[2][NST]` in `rl/fastenv.c`) through 9 smoothed features (f[46] to f[52], f[54], f[55]). X1 showed that a name's long-run profile predicts that
  opponent better than in-match counts alone (14.13). X2 seeds those same counts at match start with the
  opponent name's long-run counts from the replays, scaled to a fixed weight, and trains the policy across a
  broad population so it learns to act on them. This keeps the observation at 56 floats: every checkpoint,
  pool member and the E3 probe keep working, and the C engine needs only a setter for the initial counts.
  X1's per-context prior network is not ported. It stays the opponent model for decision-time search, the
  next option if X2 fails E6 (search needs opponent ranges, which X1 does not give, and full-hand
  continuation values within 1 s at 0.5 vCPU).
* **The contribution of each part is measured, not assumed:** X2b has arms without the seeding and without
  the style grid (below).
* Review of the first X2a draft (a 12-float X1 block in both engines): REVISE, 5 blockers (no C interface
  for the model and its state; a width change breaking every 56-wide consumer; parity that could pass
  without reaching the profile path, the in-match path or the opponent seat; undefined probe states; no
  name rule for SDK and E6 opponents). This revision removes the width change and the C model, and answers
  the rest below.
* Review 2: REVISE, 3 blockers, each checked first-hand and fixed below: a setter called after `env_reset`
  would overwrite hands the engine already played inside the reset (`env_reset_stacks` runs `start_hand` and
  `run` before it returns); per-seat parity could never reach the opponent seat's seeded path through the
  hero-only caller; the profile check round-tripped synthetic hands, so it could not catch a wrong reading
  of real replays (all-in amounts, all-ins for less than the call). That is the second automatic REVISE for
  this unit, so the policy cap is reached; I proceed on Wayne's standing approval ("I accept all the
  recommendations from you if you think it's worth", 2026-11-23), and the outcome verifier still gates the
  result.

### Correction (2026-11-23, Wayne: "the point is the universal approach I asked for at the start, and you
### listed the limits yourself")

The X2 choice above drifted back into the move this revision opened by rejecting: X2b's base and grid arms
enlarge the opponent list of a reactive policy, and the seeded arm only adds an input to it. A reactive
policy is only as robust as its training distribution, so a broader grid moves the holes, it does not
remove them. M1's whole-strategy shift does not argue against search either: "search acts only on river and
all-in decisions" was my own strawman, while the planned X2 (New order, item 3) searches at every decision.

* **X2 returns to the universal design:** X1 (done) as the explicit opponent model, a decision procedure
  that best-responds to it at decision time, and a safety blend toward the floor policy while the belief
  is broad. A style the model can express is covered without ever training against it.
* **The limits I listed, each now a work item of X2s:**
  1. X1 predicts actions, not hands. A best response needs the opponent's range: a hand-conditioned
     opponent policy whose action frequencies match X1's (data-biased frequency matching, Ganzfried and
     Sandholm 2011), with Bayesian range updates on each action, and showdowns as extra evidence corrected
     for selection (showdown censoring, arXiv 2608.09954).
  2. Continuation values: depth-limited search with fb2-900's value head (`v*` keys) at the leaf, or
     rollouts with our policy for us and the model for them.
  3. Runtime: about 1 s per decision at 0.5 vCPU in Python and numpy; measured on the deployed image.
  4. Safety: exploitation weighted by the model's confidence (evidence count, posterior spread), the floor
     policy otherwise (safe exploitation, Ganzfried and Sandholm 2015; confidence-gated exploitation,
     arXiv 2607.28520).
  5. Objective: match win probability, not chips, in short winner-take-all matches.
* **X2b:** its training arms are not run. Its code (the style grid, the held-out judge, the profile eval)
  is kept as the test bed: X2s is judged on E6 and on the style grid, none of which it trains on.
* **Next:** the X2s spec, grounded in the cited work and open-source implementations, then review and
  build.

### X2s. Search under X1: the smallest end-to-end version

Wayne (2026-11-23): "do it clean and tidy, do not overdesign, it might cause a local optimum, not the
global." So X2s is the simplest complete loop of the universal design: measure it, then improve only the
part the numbers show is weakest.

* **At each of our decisions,** for each legal action in the policy's action table, a one-street chip EV:
  * **Opponent range:** weights over the opponent's possible hole cards, uniform at hand start. After each
    opponent action, X1 gives the five class probabilities at that state; the opponent's combos are ranked
    by strength (preflop percentile `nlhe.preflop.PCT`; postflop evaluator rank on the board); the band the
    action falls in (bottom for fold, top for raises, the middle for check or call, in X1's proportions)
    keeps weight 1, all other combos weight 0.1 (bluffs and model error).
  * **EV:** fold 0; check or call `c`: `q * (pot + c) - c`, with `q` our equity against the range (200
    Monte Carlo runouts); bet or raise putting in `r` chips (`r > c`, `c = 0` when nothing is to call):
    `f * pot + (1 - f) * (q' * (pot + 2r - c) - r)`, with `f` X1's fold probability for the opponent facing
    it (`to_call = r - c`), and `q'` our equity against the range's top `1 - f` (the part that continues).
    `pot` already holds the opponent's chips this street. Later streets are ignored. (Review: the first
    draft omitted `- c`, which credited every raise facing a bet with a phantom `(1 - f) q' c`.)
* **Safety blend:** play the argmax only when X1 has evidence (a named profile, or at least 10 opponent
  actions this match) and its EV beats the policy's own choice by more than 0.05 of the pot; otherwise the
  policy plays.
* **Code:** `rl/search.py` (range, equity, EV, choice, and the public state X1 reads, built from the SDK
  state); `RLBot(search=True)`, off by default; `tests/test_search.py` (range update, EV signs on
  constructed spots, the blend, and that `search=False` plays byte for byte as before).
* **Measure:** fb2-900 with and without search, through X2b's held-out judge (the six `ext:` cells and the
  four rule cells, 300 matches each, seed 31), plus E5 (seeded, 400 each). Decision time p99 at 0.5 vCPU.
  Each search decision is logged (state, chosen versus policy action, EV gap) for diagnosis.
* **Read:** the held-out score difference (Newcombe 95%) and the share of the M1 specialist gap closed on
  Ashwing and autodidact. Whatever the result, the decision log names the weakest part (range, equity, X1's
  fold estimates, or the one-street horizon), and that part is the next change.
* **Budget:** build and tests about 3 hours; judge about 3 box-hours. Nothing is deployed.

### X2r. Does lookahead on top of the policy have headroom? (oracle first)

14.16: a one-street search equals the policy even with the opponent's true rules, so a better X1 alone
cannot gain. The procedure has to start from the policy. Policy improvement by rollouts (Tesauro and
Galperin 1996; Bertsekas, rollout algorithms) does: for each of our candidate actions, play the rest of the
hand with our policy for us and the opponent model for them, and keep the policy's action unless another is
clearly better. With an exact model this is never worse than the base policy beyond Monte Carlo error. X2r
measures the headroom with the true model before any runtime or model work.

* **Tool, offline only** (`tools/x2r_oracle.py`, nothing deployed). The hero is fb2-900's `RLBot`, search off,
  temperature 1.0 as deployed. At each of its decisions:
  * the policy picks its action as now;
  * for each legal action of the six-action table, N = 16 rollouts with common random numbers (rollout i
    uses the same opponent hole cards, board and seeds for every action);
  * the opponent hole cards are drawn from the exact posterior of the StyleBot named by `--opp`
    (`tools/x2s_ablate.py` `Oracle`), the rest of the board uniformly;
  * a rollout rebuilds the hand with `holdem.engine.Hand` at the same stacks, dealer, blinds and hand number.
    Replay wrappers return the recorded actions up to this decision. Then our seat plays the candidate
    action, then a deep copy of the hero (no further rollouts inside) and a fresh seeded StyleBot finish the
    hand;
  * the value is `rl.search.win_prob` of our end-of-hand chips (field K);
  * the hero plays the action with the highest mean value only when its mean paired gain over the policy's
    action exceeds two standard errors; otherwise it plays the policy's action;
  * every decision is logged: the policy's action, the chosen action, the means and the gain's standard
    error.
* **Measure:** the four rule cells (`raise_station`, `sticky_overbettor`, `tight_sticky`, `never_fold_pre`),
  300 matches each, seed 41. Compare against the judge's search-off run on the same seeds
  (`logs/x2s_judge/off.jsonl`). Before the full run, one small check: with N = 1 and the gate never met, the
  hero must play exactly as search off (the same match results on 20 seeds).
* **Read:** the pooled difference with a Newcombe 95% interval (`tools/x2s_stats.py` layout).
  * Lower bound above zero: lookahead on the policy has headroom. Next come the runtime question and a
    model good enough to stand in for the oracle.
  * Otherwise: against bots this policy already beats 83 to 95% of the time, search on top of it has little
    headroom, and the work moves to the gap that remains (the strong and adaptive bots) by another lever,
    chosen in a new revision.
* **Budget:** build about 3 hours; the run at most 3 box-hours on gb10-d (cores 4 to 19).

### X2m. Does the lookahead hold with the opponent model we have? (X1 in place of the oracle)

14.17: with the true model, rollouts on top of the policy add +3.8 [+1.9, +5.8] pooled on the four rule cells
(N = 128, Z = 2.6, chosen after the N = 16 run). The deployed bot does not have the rules, it has X1. X2m
changes only the model: X1 in place of the oracle, with the same rollouts, N, Z and gate (no evidence
condition, as in 14.17). It also adds the six `ext:` cells, which the oracle could not reach.

* **Prerequisite:** the seed 43 confirmation of 14.17. Its read, in `~/poker-ai-lab-x2r`:
  `cat logs/x2r_s43_off/rows_on_*.jsonl > /tmp/s43_off_rows.jsonl; $PY tools/paired_stats.py
  /tmp/s43_off_rows.jsonl logs/x2r_s43_on/rows_on_*.jsonl`. The pooled row (1200 pairs) decides; the
  `stats.txt` files in the s43 directories are not this read. If the pooled 95% lower bound is not above zero,
  X2m is not run: the code may be built, the result is recorded and the plan is revised.
* **Files:** `tools/x2r_oracle.py`, `tests/test_x2r.py`, `tools/x2r_run.sh`, one line in `tools/README.md`.
  Nothing else changes.
* **Tool:** `tools/x2r_oracle.py --model x1` (default `oracle`, unchanged). Under `x1`:
  * the root range and X1's in-match counts are an `rl.search.Search` (with `OppModel.load(OPPMODEL)`) driven
    by the hooks `RLBot` uses: `start_match(name, me, stack)` with `name = None`, the literal value both
    harnesses give, since their match_start carries no display name (holdem/engine.py), `_new_hand` and the
    hand-start stacks at round_start, `finish_hand` at round_result, and `_sync` before each decision. Its
    one-street override is not applied. With no name, X1 is its population prior plus this match's counts.
  * the rollout opponent is an `X1Bot`, created per rollout with a copy of the root range w. At each of its
    decisions:
    1. the public state comes from a fresh `HandTracker` replayed over the rollout state's whole
       action_history (both seats; raise-to converted to chips added and the level big blind, exactly as
       `Search._sync` does); X1 is used through `predict` only, never `observe`;
    2. u is its own combo's quantile from `ranked(w, strength(board), dead)` with dead = the hero's hole
       cards plus the current board, the same dead set as `Search._sync` (strength arrays cached per board
       for the decision);
    3. it plays the band class k: the class with sum(p[:k]) <= u < sum(p[:k+1]) (all-in when u is past the
       top), from the bottom fold, call, raise up to the pot, above the pot, all-in;
    4. class to action: fold, but check when nothing is to call; call or check; raise-to with extra chips
       of 0.75 (class 2) or 1.5 (class 3) times the pot after the call beyond the call, clipped to the legal
       raise range; all-in; a raise class that is not legal plays call;
    5. its range copy is updated with `update_range(w, p, c, strength(board), dead)`, where c is
       `classify` of the action actually played, the class the root `Search` would assign to it.
  * gate: X2r's, unchanged (Z standard errors of the paired gain).
  * `--opp` also accepts `ext:<name>` under `x1` only: the opponent is `functools.partial(rl.field_bots.build,
    name)` passed to `holdem.arena.run_arena`, as `rl.eval_arena` does for the judge.
  * `x2r_run.sh` takes `MODEL` (default `oracle`) and `CELLS` (default the four rule cells) as env.
* **Checks before the run** (`tests/test_x2r.py`):
  1. under `x1`, N = 1 plays exactly as the policy (20 seeds), and X2r's test 1 holds under `x1`, plus X1's
     in-match counts and the root range are unchanged by a decision's rollouts;
  2. the inverse property, exact: on a non-uniform range and a postflop board, for every live combo h with
     band class k(h), `update_range(w.copy(), p, k, ...)` keeps h's weight and multiplies it by OUTSIDE for
     every other k (equality to 1e-12). It must fail on three mutations: reversed band order, the opponent's
     own hole cards in the dead set, and a range update with the band class where the played class differs
     (a fold with nothing to call, a clipped raise that `classify` calls all-in).
* **Cost gate:** a smoke on gb10-d cores 0-1 (2 workers, 4 matches against raise_station and 4 against
  ext:ashwing, x1, N = 128) records seconds per decision. The projection uses the judge's off-arm hands per
  cell (rule cells 24k hands in all, `ext:` cells 67k). For each group, projected hours = off-arm hands x
  logged rollout decisions per hand in that group's smoke (`dec_*.jsonl` lines over smoke hands) x smoke
  mean seconds per logged decision / 16 workers / 3600; the rule cells use the raise_station smoke, the
  `ext:` cells the ext:ashwing smoke. Budget: rule cells 2.5 hours, `ext:` cells 6. If either projection
  exceeds 1.5 times its budget (3.75 or 9 hours), the full run is not launched and the plan is revised.
* **Run** (gb10-d, cores 4-19, after the prerequisite and the cost gate; one chain, rule cells first):
  * `N=128 Z=2.6 MODEL=x1 OUT=logs/x2m_rule bash tools/x2r_run.sh`
  * `N=128 Z=2.6 MODEL=x1 OUT=logs/x2m_ext CELLS="ext:ashwing ext:ashwing_search ext:ashwing_hive
    ext:autodidact ext:wolf ext:wolf_v5" bash tools/x2r_run.sh`
  * Each OUT holds on.jsonl, rows_on_<cell>.jsonl, dec_<cell>.jsonl, the judge's off.jsonl and stats.txt.
* **Read, pre-registered:**
  * R: the pooled 95% lower bound of `paired_stats.py ~/poker-ai-lab-x2s/logs/x2s_judge/rows_off.jsonl
    logs/x2m_rule/rows_on_*.jsonl` is above zero.
  * E: the pooled Newcombe 95% lower bound of `x2s_stats.py logs/x2m_ext` is above zero (unpaired: the `ext:`
    bots are unseeded).
  * E holds (with R or not): the universal procedure gains on real bots under the model we have. Next come
    the runtime (0.5 vCPU, about 1 s a decision) and the full card on fresh seeds.
  * E fails, R holds: X1 stands in for the rules but not for real bots, so the model is the bottleneck (limit
    1, ranges by frequency matching), with the oracle tool as the reference.
  * E fails, R fails: the X1 model fails even on rule bots. One ablation on the rule cells splits it: the
    oracle range with `X1Bot`, and the X1 range with the true StyleBot.
  * Reported either way: the rule-cell difference over +3.8, the share of the oracle's headroom X1 keeps.
* **Known limits:** `X1Bot` never bluffs beyond its bands and uses two fixed raise sizes, so against bots that
  bluff or size by hand its continuation is a simplification; the ablation separates that from the range.
  With no name, X1 starts every match from the population prior; on Chipzen a named profile can do better.

### X2m result and the ablation (2026-11-23 21:10 UTC)

Experiments 14.18. Seed 41: R fails (-3.8), E holds (+3.1). Seed 43 (paired on its own N = 1 off arm): R fails
(-4.6 [-6.6, -2.6]), E does not confirm (+0.9 [-1.3, +3.2]). Under the pre-registered read that is "E fails, R
fails", so the ablation runs: it splits X1's loss on the rule cells between the two places the model enters.

* **Arms** (`tools/x2r_oracle.py --model`, N = 128, Z = 2.6, seed 43, the four rule cells, `tools/x2m_ablate.sh`):
  * `oracle-range`: the opponent's cards from the oracle's exact range; the hand finished by an `X1Bot` that
    starts from that range;
  * `x1-range`: the cards from X1's range; the hand finished by the true StyleBot.
* **Reference arms, same seeds and pairs:** off (`x2r_s43_off`, equal to `x2m43_rule_off` match for match),
  oracle +4.2 (`x2r_s43_on`), x1 -4.6 (`x2m43_rule`). The gap to explain is 8.8 points.
* **Read, pre-registered:** each mixed arm's pooled paired difference against the oracle arm
  (`paired_stats.py` with the oracle rows as the first argument):
  * the continuation's loss is oracle minus `oracle-range`, the range's loss is oracle minus `x1-range`;
  * a part whose loss has a 95% lower bound above zero is a part the next model must fix; if only one does,
    it is fixed first; the two need not add up to 8.8 (they interact).
* **Next, either way:** X3, a card-conditioned opponent model, specified after this read.

**Result (2026-11-23 22:20 UTC, experiments 14.19):** the range's loss is 9.0 [7.0, 11.0], the continuation's
1.0 [-0.2, 2.2]. Only the range clears, so X3 fixes the range first.

### X3. The range at the root: separate frequency error from reveal error, then fix the one that matters

* **Why:** the range at the root is the whole loss (14.19). The range is the prior times one factor per
  opponent action, P(action class | combo). X1's factor is a band: the action's class keeps the slice of the
  range, ordered by strength, whose width is X1's probability of that class; every other combo is multiplied
  by 0.1 (`rl/search.py` OUTSIDE). It can be wrong in two ways:
  * (a) frequency: X1's probability of the class is wrong in that spot, so the band has the wrong width;
  * (b) reveal: the bot's action depends less on its cards than a strict band (raise_station checks with every
    hand, sticky_overbettor bets 65% of its worst; on replay showdowns, the chance a preflop raise outranks a
    non-raise is 0.68 to 0.97 per name and 0.76 pooled, where a strict band is 1.0: an exploration, showdown
    hands only).
* **The λ model** (a reveal model on top of a frequency model p): P(class k | combo h, spot s) = λ · b_k(h) +
  (1 - λ) · p_k(s), where b_k(h) is the fraction of combo h inside band k. The band is cut on this range as
  `update_range` cuts it (classes from the bottom: fold, call, raise up to the pot, above the pot, all-in;
  widths p), but fractionally: each live combo covers the interval of its weight in the cumulative weight,
  and a combo that straddles an edge counts for the part inside. So the band holds exactly the share p_k of
  the range.
  * For every λ the frequency of class k over the range is then exactly p_k: p stays the frequency model.
  * Range update after class k: w_h ×= λ · b_k(h) + (1 - λ) · p_k (in place of OUTSIDE). λ = 1 is a strict
    band, λ = 0 says the action tells nothing about the cards.
  * **λ from showdowns.** Chipzen shows both hands at every showdown (4,545 of 10,516 replay hands, no muck),
    so whether a combo is seen depends only on the actions, and by the line above P(actions) does not depend
    on λ. The likelihood of λ is therefore the product over shown combos of P(combo | its actions, λ): no
    selection correction.
  * Grid Λ = {0, 0.1, ..., 0.9, 0.95, 0.99}. One range per grid point; the range used is Σ π(λ) w_λ / Σ w_λ,
    with π the posterior over λ (actions do not move it, so it changes only at showdowns).
  * Population prior π0: the mean, over names with at least 30 shown hands in the fitting matches, of each
    name's posterior from a flat prior. A named opponent starts from π0 times its fitting likelihood; in a
    match, π is multiplied by the likelihood of each showdown so far.
  * One variant, pre-registered: a λ for preflop and a λ for later streets (the grid squared). The choice is
    made on X1's validation split only (below) and frozen before anything is scored on held-out matches.
* **X3a, range quality** (CPU, no lookahead; `tools/x3_range.py` and `tests/test_x3.py` on holdem-x2r):
  * **Score:** at a hero decision, the log of the share the range gives the opponent's true combo (weights
    normalized over the live combos), minus the same under the prior (uniform over the live combos): the
    nats the actions have told us. Scored only at decisions after the opponent has acted in the hand (before
    that every range is the prior). Per match, the mean over its scored decisions; per cell, the mean over
    matches. 95% intervals by bootstrap over matches (2,000 resamples), paired: every range is scored on the
    same matches and decisions.
  * **Replays first** (X1's split, `tools/oppmodel_fit.py`: matches sorted by start time, the latest 30% held
    out, the latest 20% of the rest validation, the rest fitting). Matches are replayed in order through X1
    (its in-match counts) per player; each shown combo is scored at the end of its hand from the other
    player's view (dead cards: that player's hole and the board). Steps, in this order:
    1. On fitting matches: π0 and the per-name likelihoods, for the single λ and for the variant.
    2. On validation matches: the variant replaces the single λ only if its score minus the single λ's has a
       95% lower bound above zero. The decision is printed and frozen.
    3. π0 and the per-name likelihoods are refit on fitting plus validation matches with the frozen choice.
    4. Held-out matches are scored once, for R1 and R4 (below).
  * **Simulation:** the policy alone plays (no lookahead), seed 47, 200 matches per cell, the four rule cells
    and the five `ext:` cells (14.18), all nameless (π0 from step 3). The opponent's true cards come from a
    wrapper around it (its own decide state); a hand updates π only if it reached a showdown. Ranges, side by
    side on the same matches (none changes play). On the rule cells they form a two-by-two, frequency source
    by reveal model:
    * R1, X1's frequencies, band with OUTSIDE (today; `update_range` itself);
    * R2, true frequencies, band with OUTSIDE: p_k = Σ_h w*_h P*(k | h) / Σ w*, with w* the oracle's exact
      range and P* the rule bot's per-combo probabilities (`tools/x2s_ablate.py` Oracle `_probs`); the raise
      mass goes to the class of the observed raise;
    * R4, X1's frequencies, λ (π0, then this match's showdowns);
    * R2λ, true frequencies, λ (π0, then this match's showdowns, under this model);
    * R5, the oracle's exact range: the ceiling, reported only.

    On the `ext:` cells only R1 and R4 exist (no true frequencies).
  * **Read, pre-registered** (pooled over the four rule cells unless named; all differences paired):
    * Frequency part F = ((R2 - R1) + (R2λ - R4)) / 2; reveal part V = ((R4 - R1) + (R2λ - R2)) / 2; each
      with its 95% interval. The interaction R2λ - R2 - R4 + R1 and the gap R5 - R1 are reported.
    * X3b runs if V's lower bound is above zero and R4 - R1 has a lower bound above zero pooled over the
      `ext:` cells and on held-out replays (the range X3b uses must beat today's where only X1 is available).
    * A frequency spec (X1's frequencies in the spots where they miss) is written if F's lower bound is above
      zero: alongside X3b when both parts clear, in its place when only F does.
    * If neither lower bound is above zero, stop and rethink the model.
  * **Tests** (spec numbers pinned literally):
    * for random non-uniform ranges, each class and each λ in the grid, the updated range's band share is p_k
      to 1e-12, and a cut by the left edge of each combo in place of the fractional cut fails this;
    * λ = 1 leaves weight only inside the band (straddling combos by their fraction); λ = 0 leaves the
      normalized range unchanged;
    * R1 equals `update_range` on the same history; R5 equals the Oracle's range;
    * the variant decision reads no held-out match: changing held-out data leaves it unchanged;
    * the grid, the 30-hand floor, seed 47 and 200 matches as literals; the prior scores 0.
  * **Budget:** build and tests about 3 hours on the PC; runs on gb10-d at most 4 box-hours: replays 1 core,
    at most 1 hour; simulation one core per cell (9 cores), at most 3 hours.
  * **Stop:** an acceptance test still failing after two fix rounds; a run past twice its budget; a crash,
    until its cause is known. The failure is recorded as the finding.
  * **Rollback:** tools and tests on holdem-x2r only; nothing is deployed; poker-ai-lab-v4 stays entered.
* **X3b, the lookahead with the λ range:** `tools/x2r_oracle.py --model x3` = (R4 at the root, `X1Bot`
  finishing the hand). Only the root range changes, where the ablation put the loss. N = 128, Z = 2.6, seed
  49, the four rule cells and the five `ext:` cells, each with its own N = 1 off arm, read paired. A
  candidate if both pools have a 95% lower bound above zero, then confirmed on seed 51. Ceilings: the
  oracle's +4.2 on the rule cells; the specialist's 90% on Ashwing (M1).
* **Not in X3:** the deployed bot (the λ range stays in tools until a candidate passes the gate); the runtime
  cost of the lookahead; the continuation (rechecked after the range is fixed).

### X2a. Name-seeded opponent counts in both engines

* **Outcome:** a per-name table of the tracker's counts (all `NST` slots) from the replays, a way to seed a match's
  counts from it in the deployed bot, in SDK rollouts and in the C engine, and tests that both engines
  agree.
* **Profile table** (`tools/tracker_profiles.py`, output `rl/models/tracker_prior.npz`): for every name
  in the 330 poker replays, convert each replay hand (`hands[].streets[].actions[]` with `action_type`,
  `seat`, `player`, `amount` as chips added; dealer = the small blind poster) to the engine's
  `action_history` form (raise amounts as raise-to), run it through `Tracker.update` itself with `me` set to
  the other seat, sum per name, then scale all counts so that the hand count `st[10]` equals H0 = 20 hands (a fixed weight; X2b measures its value).
  Names with fewer than 100 hands get no profile.
* **Name rule** (one table, stored in the tool's README line and the test):

  | where | opponent | name passed | profile |
  |---|---|---|---|
  | deployed bot | live opponent | `match_start` `seats[].display_name` of the other seat | if in the table |
  | C engine | `bot:NAME` clone (fitted to NAME's replays) | NAME | if in the table |
  | C engine | `arch:k` clones, baselines, snapshots, pool members | none | no |
  | SDK rollouts and every eval | `ext:` bots, `chipzen`, `model:`, StyleBots, extremes | none | no |

  So E6 (StyleBots and `ext:` bots) always runs nameless and stays held out; X2a reports the overlap
  between E6's arena-name counterparts and the table only as information. E7 uses real names.
* **Interfaces:**
  1. `Tracker(prior=None)` in `rl/features.py`: `st` starts as a copy of `prior` (`NST` floats) or zeros.
  2. `rl/bot.py` `on_match_start`: looks the other seat's `display_name` up in the table and seeds the
     tracker; `rl/sdk_rollout.py` passes no prior.
  3. C: `void env_set_prior(Pool *p, int i, int seat, const double *in)` stores `NST` doubles (or clears
     them with a null pointer) in a per-env slot that `env_reset_stacks` keeps across its `memset`, like
     `inj` and `urand`, and copies into `stats[seat]` after the `memset` and before `start_hand`, so hands
     played inside the reset count on top of the prior. Called before `env_reset`; wrapper
     `Pool.set_prior(i, seat, arr_or_None)` in `rl/fastenv.py`. A reset with no prior set behaves exactly as
     today.
  4. Caller: `Collector._new_match` in `rl/train.py`, for a `bot:NAME` opponent with a profile, seeds the
     hero seat's counts (the hero observes the clone). The new flag `--seed-profiles PATH` turns it on;
     without the flag nothing changes.
* **Acceptance:**
  1. **Profile counts on the real replays:** for every name, the unscaled counts from
     `tools/tracker_profiles.py` equal an independent count from `rl/oppmodel.py` `extract_replay` on the
     same 330 replays, exactly, for hands (`st[10]`), postflop decisions facing a bet (`st[5]`) and folds
     among them (`st[6]`), and preflop first actions (`st[11]`). Conversion rule: the deployed `Tracker` reads
     the live server's `action_history`, so a replay action is converted to what the live server sends for
     it (the executor establishes that convention from the SDK schema or a recorded live message and cites
     the source); an `all_in` that does not exceed the amount to call is a call. The tool prints the number
     of such all-ins. A mutation that leaves all-in amounts as chips added fails the check.
  2. **Parity, both seats:** the test calls `Pool.set_prior` directly with independent random priors on
     seat 0 and seat 1 (some matches with none), apart from the `--seed-profiles` caller. At every decision
     and after every finished hand, the C counts (`env_stats`) equal a Python `Tracker` seeded with the same
     prior and fed the same histories, for both seats, within 1e-9. The test prints, for seat 0 and seat 1
     separately, the compared decisions with a prior, without one, and with in-match evidence (at least one
     finished hand); each must be at least 500, or that branch is NOT TESTED. A named case has the opponent
     finish hand 1 inside the reset (forced with `env_set_injection`); the C counts must equal prior plus that
     hand. Mutations that skip the seeding in C, seed the wrong seat, or copy the prior after `start_hand`
     each make the test fail.
  2b. **Caller:** with `--seed-profiles`, a `bot:NAME` opponent with a profile gets its prior on the hero seat
     and nothing on the other seat; every other opponent gets none (unit test on `Collector._new_match`).
  3. **No-op by default:** without `--seed-profiles`, `rl.train` collects byte-identical batches to the
     current code on a fixed seed, and fb2-900 plays byte for byte as before in 200 seeded SDK matches
     against `model:` opponents (no prior anywhere).
  4. **Deployed path:** `rl/bot.py` seeds from a `match_start` message carrying a known name and not from an
     unknown one (unit test), and `deploy/Dockerfile` and `deploy/hf_package.sh` ship the table.
  5. The existing test suite passes.
* **Ownership:** `rl/features.py`, `rl/fastenv.c`, `rl/fastenv.py`, `rl/bot.py`, `rl/train.py`, `rl/oppmodel.py`
  (read only, for acceptance 1), `deploy/Dockerfile`,
  `deploy/hf_package.sh`, new `tools/tracker_profiles.py`, `rl/models/tracker_prior.npz`,
  `tests/test_tracker_prior.py`; results in experiments 14.14. Work happens in its own worktree from the
  holdem-rl tip. S2b and M1 use `rl/train.py`, `rl/features.py` and `rl/fastenv.c` on gb10-d: nothing is
  synced to `~/poker-ai-lab-rl` before both end (S2b's `end.txt` and M1's `logs/m1/done`); tests run in a
  separate box directory.
* **Non-goals:** training (X2b), any upload, the X1 network in C.
* **Known limit, for X2b:** the policy cannot tell seeded counts from observed ones (f[52] reads 20 hands at
  match start), and a `bot:NAME` clone is seeded with the real bot's profile, not the clone's own play. X2b
  reports the clone-vs-profile distance per name, so a mismatch that teaches the policy to distrust profiles
  is visible.
* **Budget:** at most 2 box-hours, 2 cores while S2b or M1 run. **Stop:** if acceptance 2 or 3 still fails
  after two fix rounds, X2a stops, the failure is recorded, and the next step goes to a new plan revision.
  **Rollback:** without `--seed-profiles` and without a table entry everything plays as today; nothing is
  deployed.

### X2b. Train one policy on a broad population and judge it on held-out opponents

* **Question:** does a broader training population, and then a per-name profile, move a single policy toward
  the specialists' gains on opponents it never trained on? M1 put the headroom at 11 to 15 points on a known
  bot; M1b showed one network keeps most of two different exploits with half the data each (14.12).
* **Reviews.** Review 1 (REVISE, 5 blockers): the draft trained on the Ashwing and autodidact code that E6
  evaluates and on clones of E6 sources; it measured the profile effect only on trained-on clones; it picked
  the best arm and decided on the same E6 run; its statistic mixed cell sizes; its start gate, `--out` and
  core count were missing. Review 2 (REVISE, 3 blockers): the grid is the E6 rule bots' own class, and a
  parameter-space ball rejects almost nothing in 20 dimensions; SolvencyCheck is one of the tight-sticky
  sources (14.11) but stayed in training; the profile measurement had no tool or pair definition. All were
  checked first-hand and are fixed below. Two automatic reviews is the cap, so I proceed on Wayne's standing
  approval; a fresh verifier still gates the result.
* **Outcome:** three policies trained from fb2-900 with the same recipe, seeds and minutes, differing only in
  population and seeding; a held-out table that tests each against fb2-900; and the profile effect on
  held-out named clones.
* **What is held out, and how:**

  | E6 cell | code or style sources (14.11) | relation to training |
  |---|---|---|
  | `ext:ashwing`, `ext:ashwing_search`, `ext:ashwing_hive` | vendor Ashwing package (all variants) | absent: no `ext:ashwing*` in any arm |
  | `ext:autodidact` | AutodidactBot (`autodidact_fast` is the same code) | absent: no `ext:autodidact*`; `bot:AutodidactInnovations` skipped |
  | `ext:wolf`, `ext:wolf_v5` | vendor Wolf | absent: no `ext:wolf*` in any arm |
  | `raise_station` | StyleBot; source DeepStack | same class as the grid; grid styles excluded in style space; `bot:DeepStack` skipped |
  | `sticky_overbettor` | StyleBot; source PluriBot (no clone) | same class; excluded in style space |
  | `tight_sticky` | StyleBot; sources r0ckGarden, SHADOW_REAPER, WSmithSimLab, SolvencyCheck, Humo-botv2 | same class; excluded in style space; `bot:SolvencyCheck` skipped |
  | `never_fold_pre` | StyleBot; sources Chatterbox, 5ur9e, PoetAndCoder, MercuryRetrograde | same class; excluded in style space; `bot:PoetAndCoder`, `bot:MercuryRetrograde` skipped |

  The six `ext:` cells are the held-out test; the four rule cells are reported as same-family
  generalization and do not decide anything. The `arch:k` clones stay in: 14.11 measured that no training or
  evaluation opponent, archetype clones included, plays these four styles. `tools/x2b_eval.sh` prints
  `data/clones.npz` meta and each arm's logged opponent keys, and refuses to judge if a skipped key or an E6
  code path appears.
* **Code (holdem-rl, own worktree):**
  1. `holdem/opponents.py`: `GridStyle(seed)`, a `StyleBot` whose 20 parameters are drawn from a parameter
     seed: `open_p`, `play_p`, `face_p` uniform in [0, 1] with `play_p <= open_p`; `pre_size` in [2, 4];
     `bet`, `rr`, `cont` per level uniform in [0, 1], each sorted non-decreasing in hand strength; `bet_size`
     in [0.33, 2.0]. The parameter seed is `ALLOWED[seed % len(ALLOWED)]`, where `ALLOWED` (in the new
     `holdem/stylegrid_seeds.py`) lists only parameter seeds whose measured style clears the exclusion
     below. Registered as `stylegrid`.
  2. `tools/stylegrid_seeds.py` builds `ALLOWED`: for parameter seeds 0 to 599, it plays 120 matches against
     fb2-900 (`tools/style_map.py sim`, style seed 5) and keeps a seed only if its style vector (the
     `tools/style_bots_check.py` distance, a missing axis counted as 0.5) is more than 0.35 from each of the
     four E6 targets and from each of the 11 gap sources named in the table above (their field vectors in
     `.cache/style_field.json`; 14.11 counts 12 gap bots, the 11 named there are used).
  3. `rl/sdk_rollout.py` `make_opp`: `stylegrid` builds `GridStyle(seed * 13 + seat)`.
  4. `tools/rl_x2b.sh ARM` (launcher), `tools/x2b_eval.sh` (E6 judge), `tools/x2b_profile_eval.py`
     (profile effect, below), `tools/x2b_stats.py` (statistics).
  5. `tests/test_style_grid.py`: legality in strict-engine matches, determinism per seed, monotone fold sets,
     and that every drawn parameter seed is in `ALLOWED`.
* **Arms.** `tools/rl_x2b.sh ARM` exits non-zero unless `logs/swap_acc/done` exists (written when today's
  swap acceptance runs end) and `ckpt/x2b_ARM` does not. It runs `python -m rl.train --out ckpt/x2b_ARM
  --init ckpt/fb2/it000900.npz --workers 2 --sdk-workers 3 --envs 96 --steps 3000 --heur-batch 6000
  --lr 1.5e-4 --clip 0.1 --floor 0.15 --snap-w 0.3 --snap-every 25 --clones data/clones.npz --bot-clones
  --skip bot:DeepStack,bot:PoetAndCoder,bot:MercuryRetrograde,bot:AutodidactInnovations,bot:SolvencyCheck
  --seed 7 --max-minutes 180` plus, per arm:
  1. **base:** `--sdk-opps chipzen,ext:sdkref,jam,jam_half`;
  2. **grid:** `--sdk-opps chipzen,ext:sdkref,jam,jam_half,stylegrid,stylegrid,stylegrid,stylegrid`;
  3. **seeded:** grid plus `--seed-profiles rl/models/tracker_prior.npz`.

  The S2 exploiter pool and distill term are left out: they serve the floor, not this question.
* **Judge, after all three arms end, never overlapping training:**
  * **Held-out cells:** fb2-900 and each arm's `latest.npz` against the six `ext:` cells, 300 matches each,
    seed 31, through `rl.eval_arena` (deployed settings, all-in answer on). **Same-family cells:** the four
    rule bots, 300 each, same seed.
  * **Profile effect (`tools/x2b_profile_eval.py MODEL`):** in the C engine, `install_clones(path,
    bots=True)`, against the 5 held-out named clones (`bot:DeepStack`, `bot:PoetAndCoder`,
    `bot:MercuryRetrograde`, `bot:AutodidactInnovations`, `bot:SolvencyCheck`) and separately the 5 trained-on
    ones (`bot:Blueprint`, `bot:Kimiko`, `bot:mr_hide`, `bot:qwentom-leap`, `bot:InfernalMonarch`), 200
    pairs each. A pair is two matches with the same env seed (deck stream), the same hero seat (seed mod 2)
    and the same hero sampling stream (`rl.runtime.Policy`, temperature 1.0 as deployed, seeded by the env
    seed): one with the hero prior set as `Collector` does, one with none. After each reset the tool reads
    `env_stats(hero)`; a play counts as "prior applied" when its hand count is at least 20. It prints, per
    name, the pairs, the plays with the prior applied, the wins with and without, and the paired difference.
    If any held-out seeded play lacks the prior (fewer than 1,000 applied), the effect is NOT TESTED.
* **Statistics (`tools/x2b_stats.py`, which prints the estimator, per-cell n and interval method):**
  * **Primary, held-out score:** a model's pooled win rate over its 1,800 `ext:`-cell matches (300 per cell,
    so it equals the cell mean). Arm minus fb2-900: Newcombe interval at 98.33% (95% Bonferroni-corrected
    over three arms). Pooling heterogeneous cells as one binomial overstates the variance, so the interval
    is conservative; at p near 0.8 the detectable difference is about 3.2 points.
  * Same-family score: the same over the four rule cells (1,200 matches), reported, deciding nothing.
  * Population effect: grid minus base on the held-out score, Newcombe 95%.
  * Profile effect: mean paired difference over the 1,000 held-out pairs, 95% normal interval of the per-pair
    differences; the trained-on pairs are reported beside it and do not count.
  * Ceiling share, the target reading: on `ext:ashwing` and `ext:autodidact`, (arm minus fb2-900) divided by
    (the M1 specialist minus fb2-900), that is how much of the 15 and 11 point specialist gaps a policy that
    never trained on those bots closes.
* **Acceptance (the finding, whichever way it falls):**
  1. `ALLOWED` has at least 200 seeds. On a fresh check, 40 randomly chosen allowed seeds, 240 matches each
     against fb2-900 on style seed 11, each lie more than 0.25 from every E6 target and gap source; one
     inside fails the acceptance. Grid code tests pass.
  2. Each arm runs 180 minutes without a crash; its training log lists only allowed opponent keys.
  3. `tools/x2b_eval.sh` checks the held-out table before any E6 match.
  4. The E6 tables (held-out and same-family, per cell rate and Wilson interval, four models), the three
     arm-minus-fb2 intervals, the population effect and the profile effect with its applied counts, each
     recomputable by hand from the per-cell wins.
* **Decision rule, pre-registered, no selection on E6:** an arm passes when its held-out 98.33% interval
  against fb2-900 is above zero and no `ext:` cell has the arm's 95% Wilson upper bound below fb2-900's point
  estimate. The next base is the first passing arm in the fixed order seeded, grid, base; it then goes
  through the full king card on fresh seeds (E1 to E5, a fresh verifier, then Wayne). Only a pass on the
  `ext:` cells supports a universality claim. If none passes, the population is not the bottleneck, and the
  next plan revision turns to decision-time search under X1. Seeding stays in the recipe only if the
  held-out profile effect's interval is above zero.
* **Ownership:** `holdem/opponents.py` (GridStyle only), new `holdem/stylegrid_seeds.py`, `rl/sdk_rollout.py`
  (`make_opp` only), new `tools/stylegrid_seeds.py`, `tools/rl_x2b.sh`, `tools/x2b_eval.sh`,
  `tools/x2b_profile_eval.py`, `tools/x2b_stats.py`, `tests/test_style_grid.py`, `tools/README.md`; outputs
  in `ckpt/x2b_*` and `logs/x2b/`; the arms were not run (Correction); X2s results are experiments 14.16. No change to `rl/train.py`, the features,
  the C engine or the network.
* **Order and budget:** code, tests and `ALLOWED` first (2 cores, at most 1.5 box-hours, any time).
  Training after `logs/swap_acc/done`: three arms in parallel, 6 processes each (learner, 2 workers, 3 SDK
  workers), 18 of gb10-d's 20 cores, 180 minutes: 9 box-hours. The judge after training: 40 runs of 300
  matches plus 4 profile runs, up to 3 in parallel at 6 workers, at most 6 box-hours (the autodidact and
  Wolf cells dominate; per-run seconds are recorded). **Stop:** a crash stops that arm; two crashes stop
  X2b until the cause is known. **Rollback:** nothing is deployed; poker-ai-lab-v4 stays entered.
* **Known limits:** removing the Ashwing and autodidact families makes the training field weaker than S2's,
  the price of a clean held-out test; if an arm passes, the king recipe adds them back. The grid draws one
  style per match and stays fixed, so it does not train against adaptive opponents. Excluding the gap
  styles from the grid also removes the styles the field shows we miss most; X2b tests generalization,
  and the king recipe may add them back once it is answered.

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
