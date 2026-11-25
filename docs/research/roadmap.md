# Roadmap: the long-term strongest Chipzen HUNL bot

Set 2026-11-22. Wayne's goal: the long-term strongest bot, a "future king". The Season 16 deadline does
not matter. The Season 16 entry is `poker-ai-lab-v4` (rl-fb2-900 plus the all-in answer of S0, image sha256
0291ee39...) since 2026-11-22 18:45 UTC, Wayne approved. `poker-ai-lab-v3` (rl-fb2-900) stays uploaded.

## Where we are (2026-11-24 10:55 UTC)

The bot is three parts (Wayne, 2026-11-21): an opponent model, a decision procedure that maximizes the match
win probability against it, and a safety blend. The work since revision 2, in order, each step read against
its ceiling:

1. **The procedure has headroom** (X2r, experiments 14.17): rollout lookahead with the opponent's true rules
   beats the policy alone by +4.2 points on the rule cells.
2. **With the model we have, it loses** (X2m, 14.18): with X1 in place of the true rules, -4.6.
3. **The loss is the range at the root** (ablation, 14.19): 9.0 of the 8.8-point gap; the continuation 1.0.
4. **Today's range is worse than no range** (X3a, 14.20): X1's band range scores below the uniform prior. The
   λ range fixes the sign everywhere (+1.09 nats on held-out replays). Frequency error is the larger part.
5. **The lookahead with the λ range** (X3b, 14.21): real bots +5.1 [+2.5, +7.7] (Ashwing +9), rule cells
   -1.7 [-3.6, +0.3], up from -4.6, all of the loss in sticky_overbettor (-11.7). Not a candidate (rule pool).
6. **It fits the arena at N = 32 and keeps the gain** (R1, 14.22): `ext:` +2.8 [+0.9, +4.7] paired, rule pool
   +0.1 [-1.6, +1.8]; about 0.4 s per decision on one core. N = 8 loses 12 points. Not a candidate yet.
7. **X1 predicts the middle** (X4 where, 14.23): an unnamed opponent's frequencies stay near the population
   prior through the match (k_im = 8, about 10 actions per spot per match).

Running unattended (2026-11-24): the X4 step 2 k_im sweep (pre-registered below; its code is not yet
verified), D2a stage 2 (clone fidelity of three bots), and D's replay fetch.

Next, in this order:
* Read the k_im sweep and D2a stage 2 against their pre-registered rules.
* **X4** next step from that read: the N = 32 match read with a chosen k_im, or the per-name prior from D's
  archive.
* **D3** (style population, GPU training) if D2a's clones pass.
* M3: v4's Season 16 matches (round robin 24 to 27 Nov) from the fetched replays.

Plan review (2026-11-24, Wayne asked whether this is the best and clean plan): three gaps were found and
fixed. Runtime was out of scope of every X slice (now R1); the floor had no slice since S2b (now E3 on
every X candidate, below); and the `ext:` reads were unpaired because Ashwing and autodidact ran unseeded
(seeded since holdem-x2r 30cfa1a, so `ext:` cells now read paired with `tools/paired_stats.py`).

Deployed: `poker-ai-lab-v4` stays entered; nothing from X or D reaches the deployed bot until a candidate
passes the gate (80% against every league opponent, a head-to-head win over the old heuristic bot, a fresh
verifier, and Wayne's yes).

## Revision 3 (2026-11-25): re-aim the judge at the classes that decide titles (in progress)

### Ordering after Phase 0 (2026-11-25 05:00 UTC, the roadmap agent's recommendation, adopted)

Wayne's aim: do not waste time; the roadmap agent sets direction. Everything below is a measurement except B1 and
B0a; only those two can change the bot, and T1 (running next) decides both: its gain sets B1's direction, and its
chipflow read (`tools/p0_read.py` on `logs/t1/flow_br.jsonl`) shows whether training alone removes the river
call-off B0 aims at. Nothing else is built for the bot until T1 reads. Season 16 cannot be changed (no candidate
exists), so nothing is rushed for 27 Nov.

* **Cut:** K1 as a slice (K = 2 ln(p / (1 - p)) from the estimated rate, or an empirical V table where data exist,
  is now a definition, 14.28); B0b (14.28: the flop shove is about break-even in match value).
* **Merged:** X5 into B0a (the posterior gate at a terminal node is its smallest form) and later the lookahead.
* **Deferred:** T2 (14.28 answered the K question; what is left needs a better model, 14.18 to 14.22; about 50
  core-hours) returns after G1. D2b and D2c (bp100 plays 22 matches a second, so B1 trains against the real code;
  only Blueprint has the 1,000 archive matches a clone needs; no code exists for the small-ball family): revisit
  only if B1 trained on bp100 fails to transfer to the live solver names. A0 Part 3 (bp100 and tags in
  `x2r_oracle.py`) goes with T2.
* **Held:** B0 step 1 until T1's chipflow read. If the bp100-trained policy still makes river call-offs at more
  than half of fb2-900's rate (594 per 4,000 matches at equity 0.198, 14.27), step 1 runs as revised below; if not,
  training fixes it for known bots and B0a returns later as the unseen-name version on top of G1.
* **Now:** A0 Parts 1 and 2 (archive tool, `small_ball`); G1's data extraction on idle cores, then G1 fits on the
  GPU (L5, L9; no bpopp queue).
* **Critical path:** T1 read (25 Nov) → B1 spec (one page, full process; population fb2-900's league mix plus bp100
  at a fixed share plus `small_ball` and `sticky_overbettor`, from fb2-900) → B1 training 26 to 28 Nov → candidate
  `v5 = B1 + S0 (+ B0a if it survives)` read on real code 29 Nov (bp100, `ext:` families, `small_ball`, E1 league,
  heuristic head to head, E3 reported) → fresh verifier, then Wayne, 30 Nov at the earliest. Guesses: T1 gain
  ≥ +8 → B1 +4 to +7 against the solver family; < +4 → B1 becomes representation work (one to two weeks) and B0a
  (+1 to +2.5 against the solver family) is the near-term change.
* **Process tiers (the deploy gate is untouched):** (1) reads of data we hold and archive tools: a committed script
  with tests, a decisive number re-derived once by a second method, no plan review, a verifier only when a roadmap
  decision hangs on one number. (2) Experiments that cannot reach the bot, under two box-hours, rerunnable: a
  pre-registration paragraph and at most one plan review; the outcome verifier checks the read. (3) Anything that
  trains a candidate or changes what the bot plays (B1, B0a, candidate reads) and oracle designs: the full chain.
  B1's spec lifts T1's run plumbing (seeded bp100 job, rate stop, cleanup check, registry seed check) into one
  verified queue runner that later specs cite.
* **After A0 (14.29, the roadmap agent's decisions, adopted 2026-11-25):**
  * Judge weights follow what an entrant faces (the two-pool finding), not seat shares. One judge class
    "solver-like", proxy bp100, about 35% of entrant seats (Blueprint, fermat6, NashForge, hoops, MonteCarlo); the
    second cluster is flagged unvalidated against bp100 and not split until we hold its code or live matches.
  * No play-time exploit slice: the over-folding classes need a policy that bets into them and stops over-folding
    itself (fb2-900 folds 60.7% to half-pot flop bets, 14.26); an override keyed to frequencies is 14.18 again.
  * **C1 (tier 2, CPU only, before T1 reads):** the T1 ceiling test against the rule cells. (a) fb2-900 against
    `small_ball` and `tight_sticky`, 2,000 matches each, seed 93: done, 75.7% and 94.3% (14.29). (b) best-response
    fine-tune from fb2-900 against `small_ball`, 60 minutes, then the same read on seed 93 paired against (a).
    Rule as T1's: gain lower bound ≥ +8 → `small_ball` joins B1's training; upper bound < +4 → it does not help.
    Result (14.30): +21.9 [+19.9, +23.8] on `small_ball`, -4.0 on `tight_sticky`: fired, `small_ball` joins B1.
  * B1's population: fb2-900's league mix (E1 holds), bp100, and `small_ball` if C1 fires. `tight_sticky` and
    `sticky_overbettor` stay untrained as honest judges; `small_ball_b` (the mean vector of BonnieBlue,
    Chaos_Incarnate, Velvet_Shark) is added as a judge-only cell if `small_ball` is trained on.
  * B1's judge: headline weights by entrant seats, recomputed from A0's tables at B1's spec (draft: bp100 0.62,
    `tight_sticky` 0.20, `sticky_overbettor` 0.07, `small_ball_b` 0.05, `ext:` 0.06); a top-table line with bp100
    and `small_ball_b` equal; pass = headline paired lower bound above zero, no cell losing more than 2 points,
    deploy gate unchanged. The regulars' pool stays E1's guard. E3 is reported, not primary.
  * G1's known-name outcome now matters most (under 1% of seats are a first match). D2b stays deferred; the core
    (fermat6 990, NashForge 884, hoops 842, mr_hide 826, r0ckGarden 774) nears the 1,000-match clone size as the
    fetch runs: first clone work after B1's first pass, training opponents only.
* **Box:** bpopp queue: T1, then B1; B0 step 1 (about 45 minutes) in a B1 pause if it runs. Cores 18-19 at nice 19:
  A0's archive read, G1's extraction. GPU: G1. PC: `small_ball` and its style check.

A fresh first-principles pass over the whole plan (a Fable 5.2 agent, read-only, 2026-11-25; its facts
re-checked first-hand where a decision hangs on them) found the judge pointed at the wrong opponents. Measured:
the `ext:` pool is mostly one family (R1's +2.8 is Ashwing +3.0 to +6.0, autodidact +2.3, Wolf -2.0; 14.22);
v4's only live loss, its Season 16 round 1 fixture, was to MonteCarlo (14.26); our one real-code proxy of a
solver-like bot, bp100, played 4,000 matches in 182 s on 6 workers (S2r, gb10-d
`~/poker-ai-lab-rl/logs/s2r/fb2.jsonl`), yet every earlier read of it used n = 400 (59.0 [54.1, 63.7], 14.9). **Unmeasured, to A0:** that the archive's top is a solver-like family (Blueprint,
NashForge, fermat6, MonteCarlo) plus small-ball aggressors (slopBot), and that MonteCarlo belongs to the
first. These come from the agent's one-pass archive reads (style vectors, a crude Bradley-Terry); only
slopBot's 0.95 flop bet share and its 125 of 199 against Blueprint are recorded (14.26).

**What decides the long-term win rate** (the decomposition the revision orders by): a field-weighted sum
over opponent classes of P(win | class); within a class, per-hand edge over variance at the current depth,
where one or two stack-sized pots carry most of the variance (unmeasured, to A0: the one-pass read says 76% of
archived matches have a hand that moves half a stack or more). Classes (unmeasured, to A0): stationary house
bots, the solver family, small-ball aggressors, and a long tail of new names. Levers, with the evidence that
sets their weight:

| lever | evidence | weight now |
|---|---|---|
| L1 base strategy against the top classes | bp100 59.0 [54.1, 63.7] (14.9); never measured against aggressors; fb2-900 raises 350 of 11,012 small-blind first actions in a match's first 10 hands (D2a fitting logs, gb10-d `~/poker-ai-lab-d2s2/logs/d2/*/fit`, read 2026-11-25) | under: raise |
| L2 big-pot decisions | 14.26: river shoves pay against callers; against bp100 the lost matches end in underdog all-ins (unmeasured, to P0: gb10-d `~/poker-ai-lab-rl/logs/eval_card/fb2-900/flow_bp100.out`); every model score weights a 16x shove like a min-bet (X1 log loss, X3a nats, D2a read 2) | under: raise |
| L3 real-arena measurement | E7 has 7 matches (14.26); 14.25: only real code and the real arena judge | under: needs Wayne (L0) |
| L4 exploitation of a known bot | M1 +11 to +15 per bot (14.12); the lookahead realizes +2.8 on one family (14.22) | right |
| L5 opponent model at the root | 14.19, 14.20; the oracle's +4.2 against +0.1 today (14.17, 14.22) | right, scored wrong (L2) |
| L6 model-uncertainty safety (Wayne's third part) | the Z gate tests rollout noise only; X2m lost 4.6 with every override past 2.6 standard errors (14.18) | missing: add |
| L7 risk attitude K | K = 4.68 fixed from the clone-league rate, which 14.3 and 14.25 show is overstated | under: cheap arm in T2 |
| L8 floor against a white-box exploiter (E3) | 96.5 to 78.7 then a plateau (14.10, 14.15); unmeasured, to A0: whether the field's top bots are themselves highly exploitable | over if A0 confirms; if not, it stays a primary metric as in Revision 2 |
| L9 cold start and name families | 14.24 (one weight cannot serve deterministic and mixing bots) | under: in G1 |
| L10 policy representation (range-aware equity, sizes) | the bust hand of 14.26, a pair of jacks on a king-high board (5s Kd Jd Th 8d, match 4b2a2beb hand 26) shoved 16x the pot; the only hand feature is equity against a random hand (`rl/features.py`) | unmeasured: T1 separates it from population |

**Stopped or changed by this revision:** X4's per-name prior as specified (every simulated cell is nameless,
so it cannot reach the X3b match read; folded into G1); D3 (no gain from generated archetypes in 14.2, and the
training question for clones was never asked; D2c first); resuming S2 (14.15: the recipe is finished); the
`ext:` pool as "real bots" (pool by family from now on); bp100 reads at n = 400 (default 4,000).

**Shared constraints (every slice below inherits them; a slice spec may not contradict them):**
* **Deploy gate (Wayne):** nothing from Phase 0 or Phase 1 reaches the deployed bot unless a candidate passes
  E1 (at least 80% match wins against every one of the 23 league opponents, each separately, over at least 400
  matches), beats the old heuristic bot head to head (holdem-chipzen 102b05e, at least 400 matches, Wilson 95%
  lower bound above 50%), gets a fresh outcome verifier, and Wayne says yes.
* **No outward arena action** (upload, swap, challenge, the L0 series, any request beyond the one replay
  fetcher) without Wayne's explicit yes.
* **Seeds:** a read seed is never a training seed and is fresh per read, with one allowed exception: a read
  may reuse an earlier read's seed when that earlier run is its named paired baseline and the seed was never
  seen in training. Registry: 81 S2r; 81 again for T1's read (its named baseline is S2r's fb2-900 rows); 82 T2;
  83 and 84 D2b (fitting logs, held-out logs); 85 D2b read 1 (86 its control rerun); 87 T1's `ext:` cost check (unpaired); 88 B0 step 1 fit logs; 89 unused (B0b cut); 90 A0's strength sanity (bp100 against `small_ball`); 91 B0 step 1's
  optional reread; 92 G1 step 1's folds and draw; 93 C1's reads (rule cells, paired); 94 B1 screen; 95 B1 confirmation; 96 B1 rerun if a
  harness fault voids a read; 97 `small_ball_b`'s strength note. Training seeds stay those of
  `tools/rl_br.sh`. A new read takes the next unused number and writes it here.
* **Pairing:** every A/B is paired on (seed, hero seat) with a paired 95% interval (`tools/paired_stats.py`,
  holdem-x2r), and real-code opponents are pooled by family (Ashwing, autodidact, Wolf, bp100), equal weight
  per family; the aggressor family joins the pools only once A0's aggressor cell exists.
* **Box (gb10-d, 20 cores, one GPU):** every job that starts bpopp containers runs alone in one serial queue,
  because the containers are not pinned to cores: S2r, then T1, then B0 step 1's logged runs (seeds 81, 88) and range queries, then D2b's
  generation (seeds 83, 84), then T2
  (after A0). D2b's fits run on the GPU while the queue moves on; P0 runs on cores 18-19 (CPU minutes); A0 is
  written and tested on the PC and reads the archive on gb10-d cores 18-19 at nice 19. Phase 0 aggregate
  budget: 12 box-hours; past 24, Phase 0 stops and what finished is recorded and judged.

**Phase 0 (cheap reads that order everything after; slice IDs are stable).** Each line: question; rule; what
it unlocks.
* **S2r** (done, 14.27: it1800 -1.1 [-2.8, +0.6], B1 starts from fb2-900). Does S2 it1800 beat fb2-900 on bp100 at a size that decides? Rule: reported;
  if it1800 leads with its paired lower bound above zero, it goes to Wayne next to E1. Unlocks: B1's starting
  checkpoint (it1800 if it leads, else fb2-900).
* **P0**, big-pot audit (data: S2r's fb2-900 run against bp100, seed 81). **Done, 14.27: +29.8 [+26.7,
  +32.9], B0 fires.** Does fb2-900 lose its matches
  through worse stack-sized decisions than its opponent makes? Hindsight equity alone cannot say (nearly every
  lost match ends in an all-in the loser was behind in), so the reference is bp100 itself in the same matches.
  For each match, the loser's last voluntary commitment: the final shove that was called, or the call of an
  all-in, made while a cheaper legal action (fold or check) existed; its equity against the winner's actual
  hand. Statistic: the share of fb2-900's lost matches whose last voluntary commitment had equity under 0.35,
  minus the same share for bp100's lost matches, with a two-proportion 95% interval. Under "no relative
  decision error" the difference is about zero. Rule: if the difference is at least +10 points with its lower
  bound above zero, **B0** (a big-pot slice: range-aware river and all-in logic at play time, specified then)
  runs before G1, X5 and B1; otherwise B0 is not specified and the order stays. If chipflow's rows lack the
  final hand's cards and actions, the same 4,000 matches are replayed with hand logging on seed 81.
* **T1**, best-response ceiling against bp100 (spec after S2r's, below). Population or representation limit?
  Rule in its spec (gain thresholds +8 and +4). Unlocks: B1's direction.
* **A0**, re-aimed judge. Instrument, no rule. Delivers a committed archive tool (classes, a rating, style
  vectors, fold by size, cold-start shares) that measures or refutes the "unmeasured, to A0" claims above, and
  two judge cells: bp100 and a slopBot-style aggressor (style check distance under 0.25, as E6), pooled by
  family. Unlocks: T2 (needs the cells), the L8 weight, the family pools of every later read.
* **T2**, the lookahead against the solver proxy and the aggressor. Prerequisite: A0's aggressor cell and
  bp100 support in `tools/x2r_oracle.py`. Does the lookahead at N = 32 gain on these two families, and does K
  matter? Arms at N = 32, Z = 2.6: K = 4.68 and K = 0.80 (the measured curve, 14.28), each paired against the N = 1 arm, 1,000 seed pairs
  per cell (bp100 and the aggressor), seed 82. Rule: an arm gains when its paired lower bound against N = 1 is above zero; the K arms separate
  when the paired interval of (K = 0.80 minus K = 4.68) excludes zero. Every override is logged with a
  decision-class tag (facing an all-in; hero shove with a cheaper action legal; other), so the read splits its
  gain by class and B0b (the flop-shove veto) is read from that split, seed 89, not built separately. Unlocks: K1 only if they separate; the
  lookahead's place in the Phase 2 candidate only if an arm gains.
* **D2b** (GPU), is the solver proxy clonable? D2a's protocol and rule on bp100 (sizes 100, 1,000, 2,000,
  control first). Pass at some size: archive clones of the solver-family names with at least that many
  matches may serve as training opponents in B1 and as subjects of D2c's transfer test, never as judges (14.25:
  even passing clones are biased by about +2 to +3 points; candidates are judged on real code and the real
  arena). Fail at 2,000: no clone of that family is used, and B1 trains against bp100 itself.
* **L0**, challenge series, gated on Wayne's yes (proposed, not run). What is v4's real win rate per class,
  and how far is each sim proxy from it? Instrument; one rule: a class more than 10 points under its sim
  proxy's rate sends that proxy back to A0. About 300 unrated challenges at most 20 a day, one at a time, stop
  on any HTTP 429, opponents fixed in advance across the classes. Unlocks: L3's weight, E7, the class weights
  of the field-weighted sum.

**Phase 1, chosen by Phase 0's reads.** Each gets its own spec and review before it runs.
* **B0** big-pot play-time logic (P0 fired, 14.27). Step 1 (spec below): the headroom of a river all-in answer
  against bp100, offline, with bp100's true range read from its container. B0a (the play-time answer) only if
  step 1's rule fires; B0b (flop-shove veto) only from T2's tagged split.
* **X5** model-uncertainty gate: rollouts draw the opponent's frequencies from their posterior, so the Z gate
  covers model error (the safety blend).
* **G1** one card-conditioned opponent model fitted on the archive (D2a's network with profile inputs, a
  pot-weighted loss, a leave-name-out read), subsuming X4's hierarchical prior.
* **D2c** clone-to-real transfer: fine-tune on the 1,000-match clones, play the real bots, transfer ratio
  against M1.
* **B1** base policy for the top classes: its direction from T1, its start from S2r, its training opponents
  from D2b; judged on real code (bp100, A0's cells, the `ext:` families) and the real arena only.

**Review record:** plan review 1 REVISE (no rule or consumer for A0, T2, D2b, P0; no shared constraints;
unsourced claims); review 2 REVISE (D2b against the serial bpopp rule and clones as judges; P0's rule could not
come out negative; L0 and the missing T1 spec; the seed-81 reuse and T2's A0 prerequisite; two unsourced
details). All fixed here. The cap was reached, so no third review; Wayne's standing approval (2026-11-23,
2026-11-16: decide by my recommendation) carries it, as with D2a.
* **K1** K from the estimated edge, only if T2's K arms separate.

### S2r and P0 data: fb2-900 and S2 it1800 against bp100 at n = 4,000 (pre-registered 2026-11-25, before the run)

* **Why:** the two policies were never compared against the strongest family at a size that can tell them
  apart (S2 it1800 read 57.0 against 59.0 at n = 400). The same run is the baseline for the best-response
  ceiling test (T1) and the data of the big-pot audit (P0).
* **Run:** holdem-rl tree on gb10-d (`~/poker-ai-lab-rl`), `rl.eval_arena --opp bp100 --matches 4000 --seed 81
  --rows`, hero `rl/models/fb2_it000900.npz` (v4's network with the all-in answer) and `ckpt/s2/it001800.npz`;
  bpopp:v011 with the eval card's settings; then `tools/chipflow.py` on fb2-900 with the same seed and size.
  Seed 81 is fresh. bpopp:v011 and `model:` heroes are seeded per match, so rows pair on (seed, hero seat).
* **Read:** each policy's win rate with a Wilson 95% interval; it1800 minus fb2-900 paired, normal 95%
  interval (`tools/paired_stats.py` on holdem-x2r). **Rule:** reported only. If it1800 leads with its lower bound
  above zero, that goes to Wayne next to the E1 league gate that rejected it; nothing is deployed.
* **Cost:** about 30 box-minutes on cores 8-15.

### T1. Best-response ceiling against bp100 (spec, 2026-11-25; revised after plan review 1)

* **Question:** is fb2-900's 59.85% against the solver-family proxy (14.27) a limit of its training population
  or of its representation? M1's method (14.12) measured +11 to +15 against Ashwing and autodidact; it was
  never pointed at bp100.
* **Scope:** one opponent factory entry, one test file, one runner script, one training run, its reads.
  **Non-goals:** no change to `rl/train.py`, `tools/rl_br.sh`, `rl/eval_arena.py`, `bpopp/`, the deployed bot
  or any league or eval-card tool. **Owner and files** (executor, local branch holdem-rl, a worktree):
  `rl/sdk_rollout.py` (`make_opp` only), `tests/test_t1_bp100.py` (new), `tools/t1_run.sh` (new), `tools/paired_stats.py` (copied unchanged from holdem-x2r). **Writes on
  gb10-d:** `ckpt/br_bp100/`, `logs/br_bp100.out`, `logs/t1/`; nothing is copied into `rl/models/`, the image
  build or holdem-chipzen. **Rollback:** revert the holdem-rl commit, delete `ckpt/br_bp100/`,
  `logs/br_bp100.out` and `logs/t1/`.
* **Code:** `make_opp("bp100", seed, seat)` returns one `bpopp.opponent.BlueprintOpponent` per worker process
  (cached; its container loads in about a minute and is reused for every match of that process, as in
  `rl.eval_arena`), with `set_seed(seed * 13 + seat)` called before each match, before `on_match_start`, as
  `holdem/arena.py` does. No per-match close. BP_IMAGE must be bpopp:v011 (the module's default v010 ignores
  seeds): `make_opp` refuses to build bp100 under any other image.
* **Tests** (`tests/test_t1_bp100.py`, run on gb10-d with the eval card's BP_* exports):
  1. `make_opp("bp100", s, seat)` returns a BlueprintOpponent with `seed == s * 13 + seat`, and the same object
     on a second call in the same process (one `docker ps --filter name=bpopp-` entry after two matches).
  2. Two training-path matches (`play_one`) on the same seed give identical batches; a different seed gives a
     different batch.
  3. A short real run, `rl.train` through `tools/rl_br.sh` with `--sdk-opps bp100`, 2 SDK workers, 3 minutes:
     every `sdk_samples` entry in its `train.jsonl` is `bp100` only and `wr` has the key `bp100`.
  4. `docker ps --filter name=bpopp-` is empty within 60 s after the short run's normal `--max-minutes` exit,
     and within 60 s after the stop branch fires on a second short run, forced with `T1_CHECK_MIN=4
     T1_MIN_RATE=1000` (and the run's name and minutes overridable for the test: `T1_OUT=t1test`,
     `T1_MINUTES=8`); that case must also leave `logs/t1/stopped` written by the script after the kill.
* **Pre-run check (in `tools/t1_run.sh`):** the policy arrays (`pw0`..`pw2`, `pb0`..`pb2`) of
  `ckpt/fb2/it000900.npz` equal those of `rl/models/fb2_it000900.npz`, which S2r read; otherwise it stops.
  Checked by hand 2026-11-25: equal (the ckpt adds the value head `vw*`, `vb*` that the fine-tune needs, so the
  ckpt is INIT and the mirror opponent of `rl_br.sh`).
* **Train (`tools/t1_run.sh`, launched with `setsid -f`, alone in the bpopp queue):** exports the eval card's
  BP_* variables (BP_IMAGE=bpopp:v011, BP_DATA, BP_RUN, BP_AT=65000, BP_THRESHOLD=0.35) and BP_CPUS=1 for the
  training only, then launches `setsid bash tools/rl_br.sh br_bp100 ckpt/fb2/it000900.npz bp100 120 6 &`
  (plain `setsid`, not `-f`): `rl_br.sh` ends in `exec python -m rl.train`, so `$!` is both the learner's pid
  and the pgid of a new group that does not contain the script. **Rate stop:** at wall minute T1_CHECK_MIN
  (default 12) the script reads `ckpt/br_bp100/train.jsonl`. Qualifying rows are those with `min` at least 2.
  With two or more, rate = (it of the last qualifying row minus it of the first) over (their `min`
  difference); with fewer than two, or no file, rate = 0. If rate < T1_MIN_RATE (default 2): `kill -TERM
  -$PGID` (that pgid only, never the script's own group), `-KILL` after 30 s, `docker kill` on every `bpopp-`
  container (the run is alone in the queue, so all are its own), the rate and row count into
  `logs/t1/stopped`, exit 3. Otherwise it waits for the learner with `kill -0 $PGID` (never `pgrep -f`).
* **Read (same script, after training; identical to S2r's command except `--model` and the output paths):**
  first `unset BP_CPUS`, so `env | grep BP_` equals `tools/s2r_run.sh`'s exports exactly; then
  `taskset -c 8-15 nice -n 5 python -m rl.eval_arena --model ckpt/br_bp100/latest.npz --opp bp100
  --matches 4000 --seed 81 --workers 6 --rows logs/t1/rows_br.jsonl` (`latest.npz` holds the final
  parameters saved at the `--max-minutes` break; the `itNNNNNN.npz` files are every 100 iterations only), then `python tools/paired_stats.py logs/s2r/rows_fb2.jsonl logs/t1/rows_br.jsonl`
  (copied from holdem-x2r), which must join all 4,000 (seed, hero_seat) keys. Then `taskset -c 8-15 nice -n 5 python
  tools/chipflow.py --model ckpt/br_bp100/latest.npz --opp bp100 --matches 4000 --seed 81 --workers 6 --out
  logs/t1/flow_br.jsonl` (compares with S2r's chipflow,
  and with `tools/p0_read.py` gives P0's statistic for the fine-tune). Gain = br minus fb2-900, paired normal
  95% interval. Seed 81 is S2r's read seed, the named paired baseline, never seen in training.
* **Also reported, not deciding:** br_bp100 and fb2-900 on the `ext:` families, 400 matches per bot, seed 87
  (registered in the envelope); holdem-rl's `ext:` bots are unseeded, so this read is unpaired (Newcombe
  interval, as M1).
* **Rule (pre-registered):** gain lower bound at or above +8 points: population is the limit, a solver-family
  member enters training (B1) and the lookahead is expected to recover part of it (T2). Gain upper bound
  below +4: the reactive policy cannot exploit it, B1 goes to representation and sizing. In between: both,
  representation second. At n = 4,000 paired the interval half-width is about 1.7 points (S2r's), so the
  bands are decidable.
* **Budget and stop:** about 2.5 box-hours (tests 15 minutes, training 120, reads 20); stop at twice that.
  Nothing reaches the deployed bot.
* **Review record:** plan review 1 REVISE (INIT file not shown equal to S2r's model; read not pinned; seed 21
  unregistered; no rate-stop mechanism; tests did not prove bp100, seeding or cleanup on both exits; no scope,
  owner or rollback). Review 2 REVISE (the group kill would kill the script; the rate undefined with few rows
  and no test hook; chipflow's `--out`, the read model and BP_CPUS). All fixed here; cap reached, carried by
  Wayne's standing approval. The executor's work gets a fresh outcome verifier before the training starts.

### B0 step 1. Headroom of a river all-in answer against bp100 (spec, 2026-11-25; HELD until T1's chipflow read)

* **Revision after plan review 1 (REVISE: range from the last action only; sampled single actions; a reproduction
  check that confused hidden state with RNG position; a vacuous lower bound; an ambiguous fit set; ties).** The
  revised design supersedes the oracle, rule, cost and tests below where they differ:
  * A new container op `dist` (image bpopp:v012 = v011 plus `server.py`; solver code untouched) returns, per given
    holding, the blueprint's exact action distribution at a wire state: the decide path with the draw removed
    (`reconstruct`, `infoset_at(bucket_for(...))`, `blueprint_action_distribution`, uniform when unvisited, the pass
    frame on truncation or exception), every abstract action priced through the real `wire_action` and the client's
    clamp, moved into one pure `finalize(frame, state)` used by `decide` too. A raise matches on kind and exact
    finalized amount. The 0.35 threshold is applied at load, so zeros are the played policy's zeros. Source read
    in `~/bp-src/code` (poker-solver v0.1.0) by the roadmap agent; server time 0.21 to 0.35 ms per call (69,976
    logged decisions, 0 fallbacks, 0 truncations).
  * True range: w(h) = uniform card-removal prior x product over every bp100 decision in the hand of
    P(logged action | h, logged state), normalized.
  * Checks before scoring: `dist` identical across repeats, a fresh seat and reversed node order on 200 nodes;
    every logged bp100 action has positive probability with bp100's actual cards; 400 `decide` draws on 100 mixed
    nodes match `dist` (no zero-probability frame, pooled chi-square p > 0.001); v012 plays 20 seeded matches
    identically to v011. A calibration gate: realized wins against predicted under w, |z| > 3 stops.
  * Values: win, tie and loss at the engine's own end stacks; V from seed 88 only (and K = 0.80 reported).
  * Ways: policy; true range (exact optimum, so judged by size, not by a lower bound); fitted table variant A (all
    seed 88 bp100 river bets in the class with true cards) and variant B (called only, the archive case, reported);
    uniform prior (cold start, reported); true cards (hindsight). Each also valued by bp100's actual cards; the two
    valuations must agree within the realized estimate's 95% interval.
  * Rule: gates pass; true-range gain ≥ +1.0 point with bootstrap lower bound ≥ +0.5; variant A gains at least
    half of it with lower bound above zero. One range-model revision allowed, reread on seed 91. B0a is built only
    when both hold.
  * Cost: 2 to 3 s of `dist` per scored decision, at most 3,000 decisions, about 25 minutes on 6 containers; a
    50-decision pilot fixes it (over 90 minutes projected → first 2,000 matches only). Budget 2 box-hours, stop 4.
  * Tests (each with a plant): two-decision range product; card removal; C1 to C4 on gb10-d; raise amount match;
    tie stack; truncated and unvisited branches; seed 88 only in the fit and V; variants A and B distinct; four-way
    read with a negative table gain; literals.

* **Why:** P0 fired (14.27). Of its parts, only the river call of an all-in loses under every match-value
  curve (594 calls at equity 0.198, -2.46M chips; 14.27, 14.28). fb2-900's only hand input is equity against a
  random hand (`rl/features.py`), so it cannot see that bp100's river shoving range beats two pair. A river
  call-off is terminal (no runout), so its value is exact given the opponent's range, and the range is the
  only modelled object. This step measures the headroom before anything is built; the design follows S0
  (`rl/allin.py`: the policy acts, a narrow module may replace one action). The flop-shove veto (B0b) is a
  counterfactual that needs a continuation model; it is measured as a tagged split of T2's read, not here.
* **Decision class:** a hero decision on the river facing a bet that puts hero all in, or leaves hero less
  than 40% of its stack at the hand's start behind (to_call at least 60% of hero's remaining stack). Actions
  compared: fold and call (a raise is not legal or not considered).
* **Data (bpopp queue, after T1):**
  * Score logs: fb2-900 against bp100, seed 81, 4,000 matches, the same matches as S2r, with a hero-side log of
    every hero decision (hole cards, board, pot, to_call, both stacks, the action history, legal actions, the
    action taken) and both players' true hole cards for every hand.
  * Fit logs: the same on seed 88 (registered), 4,000 matches. Never scored.
  * Check: the seed 81 rerun with logging reproduces S2r's per-match results (`won`, `hands`) for all 4,000
    (seeded hero and bp100); otherwise stop.
* **Match value V:** the empirical curve P(win | hero stack at hand start) from the seed 88 logs (as in 14.28),
  in 10 bins of 2,000 chips, linear between bin centres. Reported also with K = 0.80.
* **Four ways to answer each decision, each valued in match-win probability with equity against bp100's true
  range at that node:** call value e V(s + m) + (1 - e) V(s - m), fold value V(s), where s is hero's stack
  before the call and m the chips at risk (the smaller of to_call and the matched stack, plus the pot share;
  the tool computes the exact end stacks for both outcomes).
  1. **Policy:** the action fb2-900 took.
  2. **True range (oracle):** bp100's probability of the action it took at its shoving node, for every holding
     consistent with the board and hero's cards, read from the container itself: the same wire state with each
     alternative hole-card pair, 8 seeds each, averaged. Before use, a reproduction check: resending the
     logged state with bp100's actual cards gives back its logged action distribution on 50 nodes; if the
     container keeps per-hand state that a single resend does not reproduce, the hand's earlier states are
     resent in order; if neither reproduces, step 1 stops with that finding.
  3. **Fitted table:** a range from the seed 88 logs only: for each shown bp100 river shove, its hand's
     strength percentile among all holdings on that board, histogrammed in 10 bins per shove-to-pot bucket
     (under 1, 1 to 3, 3 to 8, above 8); card removal at play time.
  4. **True cards:** call if hero's actual equity against bp100's actual hand beats the price. A hindsight
     bound, reported only.
  Ways 2 and 3 choose the action with the larger value under their own range; every way is then valued under
  the true range (2). Per decision, gain = value of the way's action minus the policy's; points of win rate =
  100 x (sum of gains) / 4,000. Bootstrap over matches (2,000 resamples, seed 47) for 95% intervals.
* **Calibration check (reported, gates the build):** on the seed 81 called river shoves, the fitted table's
  predicted hero equity against the realized result, in 5 bins, with counts.
* **Rule (pre-registered):** B0a (the river all-in answer at play time) is specified and built if the true-range
  way gains at least +1.0 point with its lower bound above zero. If the fitted table recovers less than half of
  the true-range gain, its range model is revised before any build (and the revision is read again on these
  logs). If the true-range gain is under +1.0, B0a is not built and the river loss is recorded as a
  representation problem for B1 (L10). Expected from the gross figure (about -4 points over all river
  call-offs, 14.27 split): +1 to +2.5; a guess, not a prior that changes the rule.
* **Code (holdem-rl, local, an executor in a worktree):** `tools/b0_log.py` (plays fb2-900 against bp100 with
  the hero-side log and true cards; the same seeding and hero as `rl.eval_arena`), `tools/b0_oracle.py` (the
  reproduction check, the range queries, the four ways, the read), `tests/test_b0.py` run on gb10-d, each test
  shown to fail on a planted fault: the log's stacks and pot conserve chips per hand; the seed 81 rerun matches
  S2r's rows; the fit path never opens the seed 81 logs; the oracle's range sums to 1 over the live holdings
  and excludes cards on the board or in hero's hand; a decision's call and fold values use the exact end
  stacks; the four-way read on a planted toy log returns hand-computed gains. Non-goals: no change to the
  deployed bot, `rl/bot.py`, `rl/allin.py` or any training code.
* **Cost:** the two logged runs about 10 box-minutes each (S2r ran 4,000 in 182 s without logging); range
  queries about 1,000 decisions x up to 990 holdings x 8 seeds against the container, unmeasured, capped at 90
  minutes on 6 containers; scoring minutes. Budget 2 box-hours; stop at 4.
* **Runtime note for B0a (if built):** one river enumeration over at most 990 holdings per decision with numpy,
  well under R1's 0.4 s per lookahead decision (14.22); measured in B0a's own spec.

### B1. A base policy for the opponents an entrant faces (spec, 2026-11-25; full process; T1's number filled in at its read)

* **Question:** does continuing fb2-900 with the solver proxy and the small-ball aggressor in its population beat
  fb2-900 on the entrant-weighted judge, without losing the league gate?
* **Why:** C1 (14.30) showed the population is the limit for the aggressor class (+21.9), with a cost elsewhere when
  trained alone (`tight_sticky` -4.0). T1 gives the same reading for bp100: **T1 gain = ____ [____, ____]** (filled
  in at T1's read, 14.31). 14.29: an entrant meets a regular in 5.4% of its seats, so the judge is weighted by what
  an entrant faces.
* **Branch on T1 (the only blank):** A, T1's lower bound at or above +8, or between the thresholds: population P1
  (with bp100). C, T1's upper bound under +4: population P2 (without bp100; no containers, no bpopp queue) and a
  representation slice B1r (a range-aware hand feature) is specified next; in the "between" case B1r is specified
  after B1's read.
* **Facts it rests on (roadmap agent's read of holdem-rl 114a136):** `rl.train` feeds each update from C-engine
  workers (`--workers`, `--steps`: the league mix from `data/clones.npz`, snapshots and `--pool-dir`, PFSP weights)
  and SDK workers (`--sdk-workers`), each walking `--sdk-opps` round robin, one opponent per seat pair, staggered by
  worker index (`opps[(k // 2 + offset) % len(opps)]`); the learner waits for `--heur-batch` SDK samples. So an SDK
  opponent's share is its share of list entries, in matches. fb2's recipe (`tools/rl_fb2.sh`): 2 C workers x 3,000
  decisions, 10 SDK workers, `--heur-batch 10000`, SDK list `chipzen, ext:ashwing_v2, ext:ashwing_value, chipzen,
  ext:ashwing_adaptive, ext:autodidact_fast`, lr 1.5e-4, clip 0.1, floor 0.15, snapshots 0.3 every 25,
  `--opp-w arch:5=4,arch:2=3`, maniac distillation 0.5; 960 iterations in 180 minutes. A bp100 container holds
  2.365 GiB; ten fit.
* **Trains in holdem-rl on gb10-d, judged in holdem-x2r.** Patch into holdem-rl: `SmallBall`, `street_bet` and the
  STYLES entry (holdem-x2r 9939bd4) and the STYLES line of `make_opp` (159e9ba). Nothing else moves between trees.
* **Start:** `ckpt/fb2/it000900.npz`, with T1's policy-array check reused.
* **Population (fb2's recipe unchanged except the SDK list; 10 SDK workers):**
  * P1 (12 entries): `bp100, chipzen, small_ball, ext:ashwing_v2, bp100, ext:ashwing_value, bp100, chipzen,
    small_ball, ext:ashwing_adaptive, bp100, ext:autodidact_fast`: bp100 4 of 12, `small_ball` 2 of 12, fb2's six
    entries 6 of 12; the C-engine league mix stays about 38% of each update.
  * P2 (8 entries): fb2's six plus `small_ball` twice.
  * Not in training, so they stay honest judges: `tight_sticky`, `sticky_overbettor`, `never_fold_pre`,
    `raise_station`, `small_ball_b`, and E6's held-out `ext:` members.
* **Length and checkpoints:** 360 minutes; read set: iterations 300, 600, 900, 1200, 1500, 1800 that exist, plus
  `latest.npz`.
* **Queue runner `tools/bpq.sh` (lifted once from `tools/t1_run.sh`, sourced by every bp100 job from here on):** the
  single BP_* export block (bpopp:v011, BP_AT=65000, BP_THRESHOLD=0.35; BP_CPUS=1 only for training), `flock` on
  `~/bpq.lock`, launch in its own process group, T1's rate stop (with the half-written-row case counted as rate 0),
  wait with `kill -0`, a final empty `docker ps --filter name=bpopp-` check, markers `done`, `failed`, `stopped`, and
  a seed check against `tools/seed_registry.txt` (refuses an unregistered seed or one registered to another slice).
  T1's tests move with it.
* **Owner files (executor, holdem-rl worktree):** `tools/bpq.sh`, `tools/b1_run.sh`, `tools/seed_registry.txt`;
  `holdem/opponents.py`, `rl/sdk_rollout.py` (the patch); `tests/test_b1.py`, `tests/test_bpq.py`, plants in
  `tools/b1_mutate.py`. In holdem-x2r: `SmallBallB` in STYLES, its target in `tools/style_bots_check.py`,
  `tools/b1_judge.sh`, `tools/b1_read.py`, and the entrant-seat step in `tools/a0_field.py`. **Non-goals:** no change
  to `rl/train.py`, `rl/features.py`, the network, `rl/bot.py`, `rl/allin.py`, the eval card or the league tools;
  nothing into `rl/models/` or an image. **Writes on gb10-d:** `ckpt/b1/`, `logs/b1/` in both trees. **Rollback:**
  revert, delete those folders.
* **Reads: select on one seed, confirm on another.**
  * Screen, seed 94: each read-set checkpoint against bp100 (1,000 matches), `tight_sticky`, `sticky_overbettor`,
    `small_ball_b`, `never_fold_pre` (500 each), and the E1 league table in the C engine (23 opponents x 400, the
    command that produced v4's gate). Chosen: the highest screen headline among checkpoints with every league
    opponent at 80% or more; none → B1 ends with that finding.
  * Confirmation, seed 95, chosen checkpoint and fb2-900 on the same seeds, paired on (seed, hero seat): bp100 4,000;
    `tight_sticky`, `sticky_overbettor`, `small_ball_b`, `never_fold_pre`, `raise_station` 2,000 each; `small_ball`
    2,000 (reported, trained on); `ext:` held-out families (ashwing, ashwing_search, ashwing_hive, autodidact, wolf)
    1,000 each, seeded in holdem-x2r.
  * Seeds 94 screen, 95 confirmation, 96 one rerun if a harness fault voids a read, 97 `small_ball_b`'s strength note.
  * Cross-tree check before any read: fb2-900's action probabilities on 200 recorded states identical in holdem-rl
    and holdem-x2r; a holdem-rl checkpoint loads as hero in holdem-x2r's `rl.eval_arena`.
* **Judge weights (entrant seats, 14.29):** bp100 0.70 (Blueprint, fermat6, NashForge, hoops, MonteCarlo,
  tidewater_rnr, LimitLess: 36.9% of entrant seats), `tight_sticky` 0.10 (r0ckGarden 5.3%), `sticky_overbettor` 0.09
  (PluriBot, HRT), `small_ball_b` 0.08 (slopBot and its three nearest names), `ext:autodidact` 0.03. They cover 52% of
  entrant seats; mr_hide (5.7%), WSmithSimLab (2.3%) and the tail are not covered, said in the read. The executor
  recomputes the shares with the added `a0_field.py` step; a literal changes only if it differs by more than 0.02.
* **Rule (pre-registered):** headline = the weighted sum of paired gains over fb2-900 on seed 95, its interval from
  the cells' paired standard errors. Pass: headline 95% lower bound above zero; no cell (weighted or guard) with a
  paired gain under -2.0 and its upper bound under zero; E1 holds. Then the remaining gate: heuristic head to head
  (400 matches, Wilson lower bound above 50%), the eval card with E3 reported, a fresh outcome verifier, Wayne. A
  headline fail with a bp100 pass is recorded as "exploits the proxy, does not generalize" and feeds B1r.
* **`small_ball_b`, judge only:** target the mean of BonnieBlue, Chaos_Incarnate, Velvet_Shark in A0's
  `vectors.json`: vpip 0.75, pfr 0.54, shove 0.07, fold_pre_raise 0.33, post_aggr 0.58, post_fold_bet 0.56,
  bet_size 0.38, showdown 0.12 (0.35 from `small_ball`'s target). Acceptance: under 0.25 from its target on style
  seeds 3 and 4 (300 matches against fb2-900, explicit commands as A0's) and more than 0.25 from `small_ball`'s
  measured vector. Strength note: bp100 against it, 400 matches, seed 97.
* **Tests (each failing on its plant):** 1 a 3-minute P1 smoke run: `sdk_samples` has exactly P1's eight names and
  bp100's share of SDK matches is between 25% and 42% (plant: bp100 once in the list); 2 `small_ball` in holdem-rl
  plays the same actions as in holdem-x2r on a fixed stream, by a hash recorded in x2r (plant: `street_bet`
  dropped); 3 no judge-only name in the training command or any `sdk_samples` key (plant: `small_ball_b` added); 4
  the INIT and cross-tree checks (plant: a changed feature in one tree); 5 `bpq.sh`: a second container job blocks
  on the lock, the rate stop kills only its group and leaves no container, a normal exit leaves none within 60 s, an
  unregistered seed is refused, a half-written last row gives rate 0 (plants: lock removed; own-group kill;
  registry check skipped; JSON error uncaught); 6 `b1_read.py` on toy rows: selection reads only seed 94,
  confirmation only 95 (plant: selection on 95), weights are the literals and sum to 1, a cell at -3 with upper
  bound under zero fails the rule even when the headline passes (plant: guard dropped); 7 literals (360, the read
  set, 94 to 97, every n, 80%, -2.0, P1 and P2).
* **Stops:** rate stop at minute 15 (floor 2 per minute); entropy under 0.2 or a non-finite loss stops the run and
  keeps the last good checkpoint; budget 9 box-hours, stop at 18; a test still failing after two fix rounds stops the
  slice.
* **Box:** under P1 training holds the bpopp queue for 6 hours (10 containers at one CPU each), pinned to cores
  0-17; G1 keeps cores 18-19 and the GPU. Screen and confirmation after training, bp100 cells alone in the queue.
  Under P2 there are no containers and the queue is free for B0 step 1.
* **Consumers:** candidate v5 (with S0, and B0a if it survives T1's chipflow read); B1r's direction; later judges'
  weights.
* **Executor checks first:** v4's exact E1 command; a holdem-rl checkpoint loads in holdem-x2r; the iteration rate
  with this mix (smoke run); wall-clock effect of slow SDK opponents on bp100's share; whether fb2's recipe still
  moves past 900 (if no checkpoint beats fb2-900 on bp100 and `small_ball_b` at the screen, that is a finding and
  B1r comes forward).

### G1 step 1. Does one card-conditioned population model predict unseen names better than what we have? (pre-registration, 2026-11-25; tier 2)

* **Review record:** plan review 1 REVISE (P's outcome space; big-pot tag keyed on the action; unseen names not
  on the cold-start path; rule 2's baseline and bootstrap; tier budget). All fixed below; tier 2 allows one
  review, so none further.

* **Question:** on names the model never saw, does one network conditioned on hole cards and on a profile of the
  player give a better range at shown hands and a better prediction at big-pot decisions than X1's prior with the
  λ range (X3)? It decides whether G1 can replace X1 at the lookahead's root and feed B0a for unseen names. Clone
  strength is out of scope (14.25: clones never judge).
* **Expectation of size:** D2a measured 4.7 s per EM iteration at one bot's 1,000 matches; the archive (both seats)
  is about 32 times that, so a fit is roughly 25 to 30 GPU-minutes (unmeasured) and the twelve fits about 6
  GPU-hours. More GPU only if the rule fires.
* **Branch: holdem-d2** (feature builder, EM, tests, plant runner, `league/replays.py`). New files only:
  `tools/g1_extract.py`, `tools/g1_fit.py`, `tools/g1_read.py`, `tests/test_g1.py`, a G1 section in
  `tools/d2_mutate.py`'s plant list, one README line each. D2a's functions imported, not copied; D2a's literals and
  tests untouched. **Writes on gb10-d:** `~/poker-ai-lab-d2s2/data/g1/`, `logs/g1/`. **Rollback:** revert, delete
  both. **Non-goals:** no arena match, no container, no clone bot, no change to `rl/oppmodel.py` or the lookahead,
  nothing near the deployed bot.
* **Data:** poker files in `~/chipzen-replays` with modification time before 2026-11-25 12:00 UTC (file list and
  sha256 in `data/g1/manifest.json`). Inputs from A0 Part 1, cited not recomputed: per-name match counts, the class
  map (names with 30 or more matches), the name-stem grouping of version siblings. Fits start only after A0's
  tables exist; extraction does not need them.
* **Extraction (`g1_extract.py`, cores 18-19, nice 19):** every decision of both seats, so each match gives two
  modelled players. Per decision: D2a's 176 features from `base_vector` unchanged, the two profile blocks, action
  code and size bucket, legal mask, hand id, player and opponent name ids, match time, chips at stake (pot plus
  to_call in bb), the big-pot tag, from pre-action state only (facing an all-in or a bet of at least 60% of the
  remaining stack, or the player's remaining stack at most the pot before acting; never the action taken). Per hand: board mask, the player's hole cards if shown. Shards of 500 matches as npz.
  * Hidden cards: EM exactly as D2a (uniform prior over combos without board cards, posterior proportional to the
    product of that player's action likelihoods in the hand, K = 32 sampled combos, shown hands fixed with weight
    1, 5 start epochs on shown hands, 8 iterations). Both hands are shown at 99.9% of non-fold endings (215,203 of
    215,393), about 39% of hands.
* **Profile input, strictly causal:** (1) in-match: the player's own action-code frequencies per street over its
  earlier decisions in the match (20 numbers) and log1p counts (4); D2a's opponent-count block stays. (2) Archive
  history: the player's 8 style axes (`tools/style_map.py` definitions), fold to a postflop bet in three size
  buckets, share of unbet flops bet, all from that name's matches earlier than the current match; log1p of their
  number; a has-history flag (zero block, flag 0, for an unseen name). The history block is zeroed for a seeded
  random 30% of training matches, so one network learns both paths. No class label or name embedding as input.
* **Model:** D2a's MLP (two hidden layers of 256, ReLU, Adam 1e-3, batch 4,096), input widened by the 37 profile
  numbers; one network for all names; at most 300 training matches per name (seeded draw); a held-out name's
  matches all used in test.
* **Losses:** U, D2a's unweighted log-likelihood; W, each decision weighted by min(chips at stake in bb, 200),
  normalized to mean 1.
* **Held out:** (1) leave-name-out, 5 folds over names with 30 or more matches, stratified by A0's class, version
  siblings in one fold; a held-out name is never a modelled player in training (its matches still appear as other
  players' opponent: stated, not removed). (2) Time split: train before the 80th percentile of match time, test
  after; test rows grouped by the name's earlier matches: 0, 1 to 9, 10 to 99, 100 or more. Fits: 5 folds x 2
  losses plus the time split x 2 losses = 12.
* **Metrics:** R, range score: at held-out hands with the player's cards shown, log posterior of the actual holding
  after all its actions minus log uniform over live combos (nats per hand, as X3a); overall and for final pots of
  20 bb or more. P, public big-pot prediction: log loss of the action code at held-out big-pot decisions, the model
  marginalized over its own posterior range from earlier actions (no card given). P's outcome
  space is X1's five classes (`rl/oppmodel.py`: FOLD, CALL with check merged, RAISE_POT, RAISE_OVER, ALLIN): G1's
  CHECK and CALL map to CALL, its RAISE code and size bucket to RAISE_POT or RAISE_OVER by X1's own pot boundary;
  both models renormalized over the classes legal at the decision. Reported only: likelihood with
  true cards, its chip-weighted form, predicted against actual fold rate by bet-size bucket.
  * Baselines on the same rows: for R the λ range of X3 (`tools/x3_range.py`, holdem-x2r; +1.09 nats, 14.20), and
    uniform; for P, X1's prior with its in-match update (`rl/oppmodel.py`). If `x3_range.py` cannot run over an
    arbitrary hand list, a thin loop around its range function, pinned by a test to the tool's own output on 50
    hands.
  * Side check, reported, not in the rule: R, P and likelihood for D2a's nine clone cells on D2a's held-out logs
    (`~/poker-ai-lab-d2s2/logs/d2/<bot>/`, present), rank-correlated with their read 1 gaps (14.25).
* **Rule (pre-registered):** leave-name-out rows pooled over folds, bootstrap over held-out names (2,000 resamples,
  seed 47), for the better of U and W chosen by R on the training folds' own validation split (never on held-out
  names):
  The rule's unseen-name figures use the cold-start path: held-out names scored with the history block zeroed
  and flag 0; the filled path (history from the name's own earlier matches) is reported beside it.
  1. Pass: R beats the λ range by at least +0.10 nats per shown hand with the 95% lower bound above zero, and P is
     not worse than X1 (upper bound of G1's loss minus X1's under +0.02). Then G1 step 2: G1 as the lookahead's
     root range, read on real code as X3b was, plus capacity arms on the GPU.
  2. On the time split's "100 or more" group, against X1 with its per-name profile fitted on pre-cutoff matches
     plus in-match update (and the λ range under those frequencies), rule 1's thresholds pass, bootstrapped over
     the names in that group (seed 47), while rule 1 fails on unseen names: a known-name model; serves B0a and the
     lookahead for names with history; cold start stays with X1; no more GPU on the unseen-name question.
  3. Fail both: G1 stops; recorded.
  Why +0.10: X3a's range fix was about 1 nat and moved the lookahead about 3 points (14.20, 14.21); a tenth is the
  smallest change a read at n = 4,000 should see (approximate). Reported beside: W minus U on R, P and likelihood;
  R by prior-match group; R by A0 class.
* **Seeds:** fold assignment and the 300-match draw 92 (registered); profile dropout and EM torch seed 0 as D2a;
  bootstrap 47. No arena seed.
* **Tests (`tests/test_g1.py`, each failing on its plant):** 1 causality (plant: history from all matches); 2 no
  held-out name or sibling as a modelled player in its fold's training shards (plant: split by match); 3 unshown
  hands give no known combo, shown combo is the logged one (plant: opponent's cards); 4 extraction vectors equal
  `d2_clone.base_vector` for both seats (plant: seat swapped); 5 W's weights capped at 200, mean 1 (plant: no
  cap); 5b the big-pot tag reads no field of the predicted decision (plant: tag by the action taken); 5c held-out
  rows on the cold-start path carry a zero history block and flag 0 (plant: filled history); 5d G1 and X1
  probabilities on X1's five classes each sum to 1 on the same rows (plant: CHECK dropped from CALL); 6 the marginal public prediction sums to 1 and equals a brute-force combo sum on a toy net (plant: uniform
  prior marginal); 7 R on a toy equals hand-computed nats (plant: prior includes board cards); 8 literals (30, 5,
  300, 30%, 32, 8, 20 bb, 200, +0.10, +0.02, seeds 92 and 47, the cutoff time).
* **Cost and box:** extraction 1 to 2 core-hours on cores 18-19 at nice 19 (shared with A0's read); fits on the GPU
  one at a time, about 6 GPU-hours; baselines and reads about 1 core-hour. No container, so the bpopp queue is
  untouched. A pilot (fold 1, loss U, timed) fixes the estimate before the other eleven; if it projects the twelve past
  the stop, W is dropped from the folds first, then folds cut to 3. **Stop:** 24 GPU-hours or 8 core-hours of
  extraction; what finished is recorded. **Tier exception:** tier 2's two-box-hour cap is kept for cores and the
  bpopp queue (3 core-hours here at most besides extraction's stop); GPU-hours are exempt because the GPU has no
  other consumer under the ordering.
* **Consumers:** the lookahead's root range (step 2), B0a for names without code, X5's posterior, B1's population
  only indirectly.
* **Executor checks before the run:** the replay timestamp field (else order by API match id and say so); A0 Part
  1's table paths and format; EM memory at archive scale (D2a chunks 128 hands per E-step; the pilot shows it).

### A0. The re-aimed judge: field map from the archive, a small-ball aggressor cell, bp100 in the lookahead tool (spec, 2026-11-25)

* **Question:** which opponent classes exist, how strong and how common is each, and are the envelope's
  "unmeasured, to A0" claims true? Plus two judge cells for T2. Instrument, no rule, except the fixed acceptance
  checks and fixed definitions below (fixed so no number is chosen after seeing it).
* **Probe facts behind it (single pass, the roadmap agent's `a0probe.py` with `style_map.hand_stats`, 16,061
  files, 289 names):** slopBot (390 matches) bets 95% of unbet flops at about 0.44 pot and folds 77 to 86% when
  bet into; HRT and Shadow bet 1.3 to 1.6 pots and fold 16 to 23%. So "the aggressors" are two families: Shadow
  is 0.14 from the existing `sticky_overbettor` target (HRT 0.37), slopBot is nearly alone (nearest names 0.36).
  MonteCarlo is 0.09 to 0.16 from Blueprint, NashForge, fermat6 on the 8 axes, which cannot see hand selection or
  adaptation, hence step 6's second test.
* **Where it lives: holdem-x2r, one executor, one worktree.** The style vector that defines the 0.25 check is
  `tools/style_map.py` there, the rule bots are `holdem/opponents.py` there, and T2 runs `tools/x2r_oracle.py`
  there; one definition of the distance. B1 later cherry-picks the bot to holdem-rl.
* **Owner files:** `tools/a0_field.py`, `tests/test_a0_field.py` with fixtures `tests/data/a0/` (hand-written
  replay files), `holdem/opponents.py` (one StyleBot subclass, one attribute), `tools/style_bots_check.py` (one
  TARGETS entry), `tools/x2r_oracle.py` and `rl/search.py` (bp100, `--k`, the class tag), `tests/test_a0_cells.py`,
  `tools/a0_mutate.py` (plant runner), `tools/README.md` (one line per tool). **Non-goals:** no change to the
  fetcher, `rl/oppmodel.py`, the four existing style bots' behaviour, the deployed bot, training code; no clone;
  no request to chipzen.ai. **Writes on gb10-d:** `~/poker-ai-lab-x2r/logs/a0/` only (box tree refreshed from the
  commit). **Rollback:** revert the holdem-x2r commits, delete `logs/a0/`.
* **Part 1, `tools/a0_field.py ARCHIVE_DIR --out logs/a0`** (numpy and stdlib; one pass, JSON tables and a
  printed summary):
  1. Inventory: poker files, names, matches per name by `match_type` and `rated` (if no field separates rated
     fixtures from challenges, the tool prints "rated not separable" and omits every rated column, the rated refit
     and the rated shares), first and last match time per
     name. The executor reads the timestamp field name from a file; if none exists the tool orders by fetch
     listing and says so.
  2. Style vectors: `style_map.hand_stats` imported, not copied, for names with 100 or more hands; plus five reported
     statistics: fold to a postflop bet in three size buckets (under 0.8 pot, 0.8 to 3, above 3), share of unbet
     flops bet, and opening size (mean raise-to in big blinds of unraised first preflop actions).
  3. Fold by size against break-even: per name and street, fold rate in buckets 0.35 to 0.8, 0.8 to 1.5, 1.5 to 3,
     3 to 8, above 8 pot next to the bucket's mean b / (P + b) (the `m3_leaks.py` method), with counts.
  4. Classes: average-linkage clustering of names with 30 or more matches with exactly one distance, Euclidean
     over the 8 `AXES` with a missing axis = 0.5 (`style_bots_check.vec`), used for both linkage and the cut at
     0.25 (E6's threshold); the five extra statistics are reported only. Clusters are labelled by a seed name they
     contain (a cluster holding two seed names takes the one with more matches and lists the other as merged): Blueprint (solver),
     slopBot (small-ball aggressor), PluriBot (big-bet aggressor), DeepStack (station); else "other"; names under
     30 matches "tail". House bot: marked by the API if a field does (executor checks), otherwise a name in 20% or
     more of all other names' schedules. Reported: members, matches, share of all and of rated matches per class.
  5. Rating: Bradley-Terry by maximum likelihood, one parameter per name with 30 or more matches, the rest pooled
     as "tail", ridge prior of one virtual win and one loss against the mean player, 200 bootstrap resamples over
     matches (seed 47) for 90% intervals. Schedule checks printed beside it: largest connected component and who
     is outside; refit on rated matches only; every pair with 30 or more matches whose observed rate differs from
     the fitted one by more than 10 points (slopBot against Blueprint, 125 of 199, appears or not). Per name and
     class mean. Bradley-Terry over raw rates because it conditions on who was played; not Elo (order dependent,
     needs a K factor).
  6. MonteCarlo in the solver family: "yes" needs both: it falls in Blueprint's cluster in step 4, and its
     fold-by-size profile and shown river shove range (hand categories at called river all-ins) lie inside the
     min to max of Blueprint, NashForge and fermat6 per bucket, widened by its own binomial 90% interval.
     Adaptation probe (reported): its unbet-flop bet share per match against the opponent's fold-to-flop-bet rate
     in that match's earlier hands, slope with interval.
  7. Top bots exploitable: for the top 10 by rating, (a) best observed opponent: the highest Wilson 95% lower
     bound of any name's win rate against it over 30 or more matches; (b) over-folding: the largest excess of its
     fold rate over break-even in any bucket with 200 or more spots; (c) for the solver proxy, T1's gain (cited).
     "Exploitable" holds when (a) is above 55% or (b) above 10 points. L8 is over-weighted if that holds for at
     least 5 of the 10; otherwise E3 stays a primary metric as in Revision 2.
  8. Cold start: matches in time order; per seat, how many earlier archived matches its opponent's name had (0, 1
     to 9, 10 to 99, 100 or more); shares over all, rated, and the top 10. New names per week; share of names in
     the last 14 days that are a version suffix of an older name (same stem after stripping trailing digits and
     `-vN`).
  9. Swing: share of matches with a hand where a stack changed by at least half the smaller stack at that hand's
     start; and by at least 5,000 chips; street of the final hand's last all-in. Re-measures the 76% figure.
  10. Shown all-ins: called all-ins with both hands shown per name and street, counting covering-stack shoves.
* **Part 2, the small-ball cell `SmallBall(StyleBot)`, name `small_ball`, in STYLES** (evaluation only). StyleBot
  gains `street_bet = (1.0, 1.0, 1.0)`, a multiplier on `bet[i]` per flop, turn, river, default 1 so the four
  existing bots are unchanged. Starting parameters (tuned only against the style distance, never a win rate):
  `open_p 0.36, play_p 0.28, face_p 0.45, pre_size 2.5, bet (0.93, 0.95, 0.97, 1, 1), street_bet (1.0, 0.92,
  0.64), bet_size 0.44, rr (0, 0, 0.02, 0.1, 0.2), cont (0.03, 0.25, 0.75, 1, 1)`. Draft target `vpip 0.72, pfr
  0.64, shove 0.04, fold_pre_raise 0.40, post_aggr 0.73, post_fold_bet 0.80, bet_size 0.22, showdown 0.13`,
  replaced by Part 1's slopBot vector once the committed tool produces it (the tool's number is the target of
  record); `pre_size` follows Part 1's measured opening size.
  * Acceptance (as E6): `python tools/style_map.py sim small_ball rl/models/fb2_it000900.npz 300 3 4 logs/a0/sb3.json`
    and `python tools/style_map.py sim small_ball rl/models/fb2_it000900.npz 300 4 4 logs/a0/sb4.json` (arguments:
    matches, seed, workers), then `style_bots_check.py` on each: distance under 0.25 on both.
  * Strength sanity, reported, labels the cell: `BP_IMAGE=bpopp:v011 python -m rl.eval_arena --hero bp100 --opp
    small_ball --matches 400 --seed 90 --workers 6` under the eval card's BP_* exports (bpopp queue; if `--opp`
    does not accept a STYLES name, `rl/eval_arena.py` joins the owner files for that one change). If bp100
    wins more than 60%, the cell is labelled "style cell, not a strength proxy" wherever it is used and the
    aggressor class's strength judge is L0 only (slopBot beats the live Blueprint 63%, 14.26; a bot folding 80%
    to bets is easy for whoever bets).
  * The big-bet aggressor is the existing `sticky_overbettor`; T2's aggressor cell is `small_ball`.
  * Oracle paths read StyleBot attributes without `street_bet` (`tools/x2s_ablate.py` `Oracle._probs`,
    `tools/x2r_oracle.py --model oracle`, `tools/x3_range.py`'s rule-bot scorer): each refuses a bot whose
    `street_bet` is not all ones (owner files: those three), tested by `x2r_oracle --opp small_ball` exiting with
    an error (plant: guard removed).
  * If `small_ball` cannot get under 0.25 after three parameter rounds, it ships with its distance stated and T2
    names it "nearest reachable" (the reversible choice; the other is a new bot class).
* **Part 3 is DEFERRED with T2 (ordering above); when it returns, `--k` defaults to None (the module K) and test
  10's literals are win_prob(10000, 20000) = 0.9120 by default and 0.5987 at k = 0.80 (plan review 1).**
* **Part 3, bp100 in `tools/x2r_oracle.py` for T2** (today it refuses any non-STYLES name except `ext:`, line 422):
  1. `--opp bp100` with `--model x1` or `x3`, factory `rl.eval_arena.make_bp100`; refuses unless
     BP_IMAGE=bpopp:v011.
  2. `--k FLOAT` (default 4.68): `rl.search.win_prob(x, T, k=None)` takes an optional curvature (K is a module
     constant at `rl/search.py:36`) and the hero passes its own. Default output unchanged.
  3. Every decision row gains `cls`: `facing_allin` (B0 step 1's definition), `hero_shove_cheaper` (policy action
     all-in with another non-fold action legal), `other`.
  4. `--model oracle` with bp100 stays refused (a second container seat inside rollouts; B0 step 1 covers the
     true-range question offline).
* **Tests, each shown to fail on a planted fault (`tools/a0_mutate.py`, as `d2_mutate.py`):**
  1. Fixture archive of 6 names: Bradley-Terry order and one pair's fitted rate hand-computed (plants: wins and
     losses swapped; ridge removed, the unbeaten name diverges and the finite check fails).
  2. A fixture 2-pot bet lands in the 1.5 to 3 bucket and the fold counts for the folder (plant: size measured
     after the bet).
  3. Cold-start counts use only earlier matches (plant: all matches of the name).
  4. Swing: a 6,000-chip hand counts under both definitions; a 4,000-chip hand at 6,000 effective under the first
     only (plant: one definition aliased to the other).
  5. A fixture name's style vector equals `style_map.vector` on the same hands (plant: a copied, edited
     `hand_stats`).
  6. The shown all-in detector counts a covering-stack shove (plant: bettor's own stack only).
  7. The four existing style bots give the same actions on a fixed seed and state stream before and after the
     StyleBot change, as a hash recorded at the pre-change commit (plant: `street_bet` default 0.9).
  8. `small_ball` literals: the target, the 0.25 bound, seeds 3 and 4 (plant: bound 0.35).
  9. On gb10-d: `x2r_oracle --opp bp100 --model x3 --n 1 --matches 4 --seed 9 --workers 2` runs, twice gives
     identical rows, and refuses under BP_IMAGE=bpopp:v010 (plant: guard removed).
  10. `--k 0.80` gives `win_prob(5000, 20000)` = 0.5498 and the default stays 0.9120 (plant: hero ignores `--k`).
  11. A hand-built state facing an all-in is tagged `facing_allin`; a policy all-in with a legal call is tagged
      `hero_shove_cheaper` (plant: tags swapped).
  12. `docker ps --filter name=bpopp-` is empty within 60 s after test 9.
* **Where it runs:** tests 1 to 8, 10, 11 and the `small_ball` style sim on the PC or box without containers. The
  archive read on gb10-d cores 18-19 at nice 19 (under 10 minutes on one core by the probe). Tests 9 and 12 and
  the strength sanity start containers: one bpopp-queue slot, about 15 minutes, after T1 and B0 step 1.
* **Read:** one experiments.md section, a line per "unmeasured, to A0" claim: confirmed, refuted or changed, with
  the number. The class table, rating, cold-start shares and swing replace the envelope's one-pass figures.
* **Consumers:** T2 (the cells and Part 3), the L8 weight (step 7), family pools of later reads (step 4), L0's
  opponent list and weights (steps 4, 5, 8), G1 and B0a (steps 8, 10), X5 and K1 (class ratings as the prior win
  rate that sets K).
* **Review record:** plan review 1 REVISE (test 10 literals; `street_bet` unseen by the oracle paths; the class
  metric and multi-seed rule; the rated fallback and opening size; seed and commands of the Part 2 reads). All
  fixed above; Parts 1 and 2 are tier 1 and 2 under the ordering, so no second review.
* **Cost and stop:** executor about half a day; box about 0.5 box-hours. Stop at 2. An acceptance test still
  failing after two fix rounds stops the slice.
* **Flag carried to T2:** at R1's 0.4 s per lookahead decision a bp100 match is about 45 s of hero time, so 2,000
  matches per arm is about 25 core-hours; T2's spec takes a measured rate from test 9's run at N = 32 before it
  fixes n.
* **Unverified:** the timestamp and house-bot fields in the replay JSON; whether rated fixtures can be told from
  challenges (14.26: the API labels both `challenge`); the probe's style numbers.

### D2b. Is the solver proxy clonable? D2a's protocol on bp100 (spec, 2026-11-25; DEFERRED by the ordering)

* Plan review 1 REVISE (container tests outside the serial queue and `d2_mutate.py` hard-coded to `test_d2.py`;
  no owner, markers or test for the S2r replicate band and the runner hand-off; tree identity with holdem-rl
  f2d6c5d). To be fixed if D2b returns.

* **Question:** does D2a's neural clone, fitted to arena-visible logs of bp100, play like bp100 against us, and
  from how many matches (100, 1,000, 2,000)?
* **Unchanged from D2a (spec above, 14.25):** replay-shaped logs with hole cards only at showdowns and a separate
  true-cards file; feature builder, network, EM (start 5 epochs, 8 iterations, K = 32); the table baseline;
  read 1's cells, pairing on (seed, hero seat), z = 1.645, pass when the 90% interval lies within ±5 points; the
  control and its one rerun; read 2 on held-out logs. D2a's power figure carries over because fb2-900 is at
  59.85% against bp100 (14.27), the rate it assumed.
* **Changes:**
  1. The cloned bot is `bp100`: `d2_generate.make_target` and `d2_clone.make_opp` (kinds `real` and `control`)
     gain a bp100 branch returning `bpopp.opponent.make_bp100()`; its container is cached per process, so a
     worker loads the blueprint once. `play_one` already calls `set_seed(pair * 13 + hero_seat)` and `Offset`
     shifts it for the control. Both refuse bp100 unless BP_IMAGE=bpopp:v011. Eval card BP_* exports unchanged.
  2. Seeds: fitting logs 83 (2,000 matches), held-out 84 (1,000), read 1 85, control rerun 86. Sizes are the
     first matches by index.
  3. Hero mix: D2a's six, unchanged (fb2-900's bare policy, the heuristic bot, the four style bots, k mod 6):
     comparable with 14.25; archive names are logged against a mixed field, so a mix-fitted clone is the honest
     test; bp100 keeps no opponent statistics, so the mix changes coverage, not behaviour. At size 100 only about
     17 matches are against our policy; the ladder measures that.
  4. Read 1 cells: real, control, neural 1,000, neural 2,000, table 2,000; fb2-900 as hero with the all-in answer
     and search off (`rl.eval_arena.make_hero`), 3,000 matches per cell. The real cell replicates S2r: a value
     outside [56.5, 63.2] (S2r's interval widened by this cell's 1.8) stops the read as a harness fault.
  5. Read 2 additions, reported, not deciding: per-decision log-likelihood weighted by chips at stake (pot plus
     to_call, in big blinds), and unweighted on the big-pot class alone (B0 step 1's facing-all-in definition
     plus the bot's own all-ins). Tests 14.25's guess that cheap decisions dominate the score.
* **Rule (the envelope's):** the control passes first (one rerun on seed 86; a second failure leaves bp100
  unjudged, a harness fault). The neural method passes at the smallest of 1,000 and 2,000 whose cell passes. A
  pass at size S: archive clones of solver-family names (A0's cluster) with at least S matches may be training
  opponents in B1 and D2c subjects, never judges. Fail at 2,000: no clone of the family is used and B1 trains
  against bp100 itself. A 1,000 pass with a 2,000 fail reads as Ashwing in 14.25: not trusted. (Archive counts:
  S = 1,000 reaches Blueprint 2,242 only, fermat6 990 and NashForge 882 just under.)
* **Owner files (executor, holdem-d2, a worktree):** `tools/d2_generate.py` (`make_target`, the image guard),
  `tools/d2_clone.py` (`make_opp`, read 2's two lines), `tools/d2b_queue.sh` and `tools/d2b_fit.sh` (new),
  `tests/test_d2b.py` (new), `tools/d2_mutate.py` (plants extended). **Non-goals:** no change to the feature
  builder, network, EM, `d2_read.py`'s rule, `tools/d2_eval.sh`, D2a's literals or tests; nothing reaches the
  deployed bot. **Writes:** `~/poker-ai-lab-d2s2/logs/d2b/` only. **Rollback:** revert, delete `logs/d2b/`.
* **Two runners, so the serial bpopp queue holds:**
  * `tools/d2b_queue.sh`, the only one that starts containers, alone in its queue slot: generation seeds 83 and
    84, then read 1's `real:bp100` and `control:bp100` cells on 85 and on 86 (86's rows opened only if 85's
    control fails), 6 workers; ends by checking `docker ps --filter name=bpopp-` is empty, writes
    `logs/d2b/queue.done`.
  * `tools/d2b_fit.sh`, never starts a container: neural fits at 100, 1,000, 2,000 on the GPU, table fits beside
    them one core each, then the clone cells (neural 1,000, neural 2,000, table 2,000 on 85; 86 only if needed),
    `d2_read.py`, read 2. Pinned to cores 16-17, nice 10, 2 workers. Seeded, so sharing the box changes times,
    not outcomes; the executor first checks `holdem/engine.py` and `rl/bot.py` for any wall-clock limit that
    contention could trip.
* **Tests (`tests/test_d2b.py`, gb10-d, eval card exports), each shown to fail on a planted fault:**
  1. Two generated matches in one process use one container (plant: a new container per match).
  2. The same match index generated twice gives byte-identical files, a different index differs (plant:
     `set_seed` not called); under bpopp:v010 the generator and the arena cell refuse (plant: guard removed).
  3. D2a's test 1 on bp100 logs: chips conserve, hole cards only in showdown hands; a hand where the client
     repaired or clamped the container's frame logs the action the engine applied (plant: logging the frame).
  4. The control reaches the container with the offset seed and differs from the real cell in at least one of
     20 matches (plant: `Offset` not applied to bp100).
  5. The fit path never opens the true-cards file, on bp100 logs (D2a's test 3, parametrized).
  6. Fit-side vectors equal play-side vectors at the same bp100 decisions (D2a's test 2, parametrized).
  7. Literals: seeds 83 to 86, sizes 100, 1,000, 2,000, 3,000 matches, ±5, z 1.645, the S2r replicate band.
  8. `d2b_fit.sh` end to end on a 12-match toy leaves `docker ps --filter name=bpopp-` empty throughout (plant: a
     `real:` cell moved into it); `d2b_queue.sh` leaves it empty within 60 s of exit.
  9. Read 2's chip-weighted score on a two-decision toy equals the hand-computed value (plant: weights dropped).
* **Cost:** queue slot about 3,000 generated matches plus four cells of 3,000, roughly 12 container-minutes at
  S2r's rate (rule heroes unmeasured; budget 30). Off the queue: fits about 0.1 GPU-hour, table fits about 25
  CPU-minutes, clone cells about 1 core-hour on two cores. Under 1 box-hour; stop at 2.
* **Consumers:** B1 (training opponents: solver-family clones or bp100 itself), D2c (transfer subjects), G1
  (whether pot weighting moves the score toward strength).
* **Limits, stated in the read:** bp100 is the blueprint with the resolver off; whether the archive's Blueprint,
  NashForge or fermat6 resolve or adapt is unknown, so a pass licenses their clones as training opponents only.
  A passing clone is still biased easy by 2 to 3 points (14.25), so it never judges.

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
  widths p), but fractionally and by strength groups: the live combos of equal strength form one group (the
  suit variants of a preflop hand class, or a tie on the board), each group covers the interval of its
  pooled weight in the cumulative weight, and every member gets the fraction of the group's interval inside
  the band. So the band holds exactly the share p_k of the range, and no combo's weight depends on its index.
  R1 and R2 keep today's cut (`update_range`: midpoint quantile, ties by combo index), so the band rows and
  the λ rows of the read below also differ in this tie rule; V includes it.
  * For every λ the frequency of class k over the range is then exactly p_k: p stays the frequency model.
  * Range update after class k: w_h ×= λ · b_k(h) + (1 - λ) · p_k (in place of OUTSIDE). λ = 1 is a strict
    band, λ = 0 says the action tells nothing about the cards.
  * **λ from showdowns.** Chipzen shows both hands at every showdown (4,545 of 10,516 replay hands, no muck),
    so whether a combo is seen depends only on the actions, and by the line above P(actions) does not depend
    on λ. The likelihood of λ is therefore the product over shown combos of P(combo | its actions, λ): no
    selection correction.
  * Grid Λ = {0, 0.1, ..., 0.9, 0.95, 0.99}. One range per grid point; the range used is Σ_λ π(λ) w_λ / Σ_live w_λ
    (each grid range normalized over the viewer's live combos, then mixed), with π the posterior over λ
    (actions do not move it, so it changes only at showdowns, and a hand is always scored with π from the
    showdowns of earlier hands only).
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
    per player, named as the deployed bot names them (`start_match(player name)`; a name X1 has no counts for
    plays as unseen) with its in-match counts; each shown combo is scored at the end of its hand from the
    other player's view (dead cards: that player's hole and the board). Two X1 fits, same selected
    hyperparameters: X1-fit on the fitting matches only (a new `oppmodel_fit.py` option saves it as
    `rl/models/oppmodel_fitpart.npz`) and X1 as deployed (`rl/models/oppmodel.npz`, fitting plus validation).
    Steps, in this order:
    1. With X1-fit, on fitting matches: π0 and the per-name likelihoods, for the single λ and for the variant.
    2. With X1-fit, on validation matches: the variant replaces the single λ only if its score minus the
       single λ's has a 95% lower bound above zero. The decision is printed and frozen.
    3. With X1 as deployed: π0 and the per-name likelihoods refit on fitting plus validation matches with the
       frozen choice.
    4. With X1 as deployed: held-out matches scored once, for R1 and R4 (below). Held-out is the only place
       where neither X1 nor λ has seen the data.
  * **Simulation:** the policy alone plays (no lookahead), seed 47, 200 matches per cell, the four rule cells
    and the five `ext:` cells (14.18), all nameless (π0 from step 3). The opponent's true cards come from a
    wrapper around it (its own decide state); a hand updates π only if it reached a showdown. Ranges, side by
    side on the same matches (none changes play). On the rule cells they form a two-by-two, frequency source
    by reveal model:
    * R1, X1's frequencies, band with OUTSIDE (today; `update_range` itself);
    * R2, true frequencies, band with OUTSIDE: p_k = Σ_h w*_h P*(k | h) / Σ w*, sums over the viewer's live
      combos, with w* the oracle's exact range and P* the rule bot's per-combo probabilities (`tools/x2s_ablate.py` Oracle `_probs`); the raise
      mass goes to the class of the observed raise;
    * R4, X1's frequencies, λ (π0, then this match's showdowns);
    * R2λ, true frequencies, λ (π0, then this match's showdowns, under this model);
    * R5, the oracle's exact range: the ceiling, reported only.

    On the `ext:` cells only R1 and R4 exist (no true frequencies).
  * **Read, pre-registered** (pooled over the four rule cells unless named; all differences paired; a pooled
    value is the mean of per-cell means, its bootstrap resamples matches within each cell; held-out replays
    are one pool, resampled by match):
    * Frequency part F = ((R2 - R1) + (R2λ - R4)) / 2; reveal part V = ((R4 - R1) + (R2λ - R2)) / 2; each
      with its 95% interval. The interaction R2λ - R2 - R4 + R1 and the gap R5 - R1 are reported.
    * Four bounds: F, V, R4 - R1 on the `ext:` pool, R4 - R1 on held-out replays. "Clears" means a 95% lower
      bound above zero, each on its own. One action per outcome, printed by the tool:
      * V, `ext:` and held-out all clear: X3b runs;
      * V clears but `ext:` or held-out does not: no X3b; the λ fix does not transfer, recorded, and X3 is
        revised;
      * V does not clear: no X3b;
      * F clears: a frequency spec (X1's frequencies in the spots where they miss) is written, in addition
        to whichever of the three lines above holds;
      * neither F nor V clears: stop and rethink the model.
  * **Tests** (spec numbers pinned literally):
    * for random non-uniform ranges, each class and each λ in the grid, the updated range's band share is p_k
      to 1e-12, and a cut by the left edge of each combo in place of the fractional cut fails this;
    * λ = 1 leaves weight only inside the band (straddling combos by their fraction); λ = 0 leaves the
      normalized range unchanged;
    * R1 equals `update_range` on the same history; R5 equals the Oracle's range;
    * the variant decision reads no held-out match: changing held-out data leaves it unchanged;
    * permuting combo order within equal-strength groups (preflop, and a paired-board postflop spot) leaves
      the λ-updated range unchanged to 1e-12 for every grid λ, and a cut by combo index fails this;
    * a hand's score uses π without its own showdown: changing that hand's shown combo leaves its π unchanged;
    * on a two-point grid the mixture equals the normalized posterior predictive computed by hand;
    * R2's p sums to 1 and gives no weight to combos that hold the hero's or the board's cards;
    * X1-fit's per-name counts equal the counts over fitting matches only, and changing a validation match's
      actions leaves X1-fit unchanged;
    * the tool prints the single action the read gives for each of the 16 outcomes of the four bounds;
    * the grid, the 30-hand floor, seed 47 and 200 matches as literals; the prior scores 0.
  * **Budget:** build and tests about 3 hours on the PC; runs on gb10-d at most 4 box-hours: replays 1 core,
    at most 1 hour; simulation one core per cell (9 cores), at most 3 hours.
  * **Stop:** an acceptance test still failing after two fix rounds; a run past twice its budget; a crash,
    until its cause is known. The failure is recorded as the finding.
  * **Rollback:** tools and tests on holdem-x2r only; nothing is deployed; poker-ai-lab-v4 stays entered.
  * **Review:** two plan reviews, both REVISE (4 and 4 blockers: λ absorbing frequency error, variant
    chosen on held-out, approximate band cut, no budget; ties cut by index, π and mixture definitions, X1
    in-sample on the fitting data, an outcome with no action). All fixed; the cap was reached, so no third
    review, and Wayne's standing approval carries it.
**Result (2026-11-24 02:06 UTC, experiments 14.20):** F +0.48 [0.45, 0.51], V +0.20 [0.18, 0.22], R4 - R1
+0.33 [0.30, 0.35] on `ext:` and +1.09 [0.98, 1.22] on held-out replays: all clear, so X3b runs and a frequency
spec is written. Today's range R1 scores below the uniform prior (-0.34 rule pool, -0.73 held-out). The
interaction (-0.45) is as large as V: λ mainly guards against wrong frequencies.

* **X3b, the lookahead with the λ range:** `tools/x2r_oracle.py --model x3` = (R4 at the root, `X1Bot`
  finishing the hand). Only the root range changes, where the ablation put the loss. N = 128, Z = 2.6, seed
  49, the four rule cells and the five `ext:` cells, each with its own N = 1 off arm, read paired. A
  candidate if both pools have a 95% lower bound above zero, then confirmed on seed 51. Ceilings: the
  oracle's +4.2 on the rule cells; the specialist's 90% on Ashwing (M1).
* **Not in X3:** the deployed bot (the λ range stays in tools until a candidate passes the gate); the runtime
  cost of the lookahead; the continuation (rechecked after the range is fixed).

**X3b build (2026-11-24):** holdem-x2r d0008b9, `X3Root` drives `tools/x3_range.Ranges` from the hero's hooks
(pi0 in `rl/models/x3_pi0.json`); a fresh verifier confirmed it (70 tests, 9 planted mutations killed, the
four older arms byte identical, N = 1 under x3 plays as the policy on all nine cells). Run `tools/x3b_run.sh`
on gb10-d from 03:07 UTC. Decision time at N = 128 is the same as x1 (about 1.5 s).

**X3b result, rule cells (06:25 UTC, seed 49, 300 paired matches per cell, against the N = 1 off arm):**

| cell | difference | 95% interval |
|---|---|---|
| never_fold_pre | +3.0 | [+0.2, +5.8] |
| raise_station | +2.0 | [+0.2, +3.8] |
| sticky_overbettor | -11.7 | [-17.8, -5.5] |
| tight_sticky | +0.0 | [-2.9, +2.9] |
| pooled | -1.7 | [-3.6, +0.3] |

The rule pool does not clear, so X3b is not a candidate whatever the `ext:` cells give. Against X2m's x1 arm
(-4.6 on seed 43) the λ root recovers most of the loss; what is left is sticky_overbettor, where matches run
twice as long (38.2 hands per win against 17.9). `ext:` so far (unseeded, unpaired): ashwing 73.7% to 82.7%,
ashwing_search 74.7% to 83.3%.

**X3b result, complete (07:59 UTC, experiments 14.21):** `ext:` pool +5.1 [+2.5, +7.7] (ashwing +9.0,
ashwing_search +8.7, ashwing_hive +5.3, autodidact +2.0, wolf +0.7); rule pool -1.7 [-3.6, +0.3]. Only the
`ext:` pool clears, so X3b is not a candidate and seed 51 is not run. Next: X4 on sticky_overbettor, R1 for the
runtime.

### X4. Frequencies (owed by X3a; specified after X3b's `ext:` read)

* **Why:** with the true frequencies the band range already scores +0.37 nats where X1's scores -0.34
  (14.20); frequency is the larger part of the gap to the exact range, and λ mostly guards against it.
* **First, where:** per spot (street, facing a bet or not, bet size class), X1's class frequencies against
  the rule bot's true ones, from the X3a simulation's events; sticky_overbettor first, since it carries the
  whole X3b loss. The same spots on real data come from D's archive (showdown hands give the true classes).
* **Then, the smallest fix that closes the measured miss:** more weight on in-match counts, a per-name prior
  from D's archive, or a spot feature X1 lacks. Chosen by the measurement above, not in advance.
* **Read:** the X3a score (R4 with the new frequencies against R4 today) and the X3b match read on the same
  seeds.
* **Also checked there:** the continuation's lean on sticky_overbettor (-3.3 in 14.19).
* **Where, result (experiments 14.23):** X1 predicts the middle in every rule cell: sticky_overbettor bets
  0.76 to 0.83 when checked to, X1 says about 0.47; raise_station never bets postflop, X1 says 0.20. The cause
  is the in-match prior weight: an unnamed opponent's prediction is (counts + 8 x prior) / (count + 8), and a
  spot sees about 10 actions per match.
* **Step 2, the prior-weight sweep (pre-registered 2026-11-24, before any sweep result):**
  * Arms: `k_im` in {8 (today), 4, 2, 1}, nothing else changed (named profiles keep k = 20, w = 2).
  * Score: X3a's R4 score (nats about the true combo) with each arm's frequencies, seed 47, the same cells:
    4 rule cells, 5 `ext:` cells (seeded bots), and the 99 held-out replay matches.
  * Choice: the arm with the best pooled score on `ext:` cells plus held-out replays, the noisy real data; it is
    chosen only if its paired bootstrap 95% lower bound against `k_im` = 8 on that pool is above zero.
    Otherwise `k_im` stays 8 and X4 moves to the per-name prior from D's archive. The rule cells are reported
    but do not choose (a deterministic bot always prefers less prior).
  * Then, for a chosen arm only: the X3b match read at N = 32 (R1's setting), seed 49, against the N = 1 off
    arm with the same `k_im`, rule and `ext:` cells paired; candidate when both pools' lower bounds are above
    zero (the X3b rule).
  * A probe until a candidate exists: the deployed bot does not change.

### D. Real opponents: data and validated clones

* **Why:** the goal is to win against bots we have not seen. The opponent model is only as good as its
  data, and clones fitted to replays have overstated our results (84 to 89% against clones, 49 to 64%
  against the real code, 14.3). Training more against unchecked clones would teach the wrong lesson.
* **D1, the archive:** the public API lists 43,497 completed poker matches (2026-11-24); X1 used 330.
  `tools/fetch_chipzen_all.sh` (holdem-chipzen) fetches all of them on gb10-d into `~/chipzen-replays`: one
  fetcher, 3 s between requests, stop on HTTP 429 and resume 30 minutes later; about 3 days. v4's Season 16
  matches arrive with it (M3).
* **D2, clone fidelity first:** clone the 13 public bots we run as `ext:` (14.3) from their
  replays and compare our win rate against the clone with our win rate against the code. A clone
  method counts only when that gap is a few points; then the same method is trusted for names without code.
  Clones condition on cards through the showdowns, not only on action frequencies.
* **D3, cover the styles:** a parametric style population that covers the style map (14.11: 12 of 51 field
  bots play 4 styles no opponent of ours plays), weighted by the field's share of each style; inside it,
  train on the members the policy loses to (adversarial selection, `2026-11-22-hf-generalization/notes.md`).
* **D4, honest evaluation:** split by name. Bots never seen in fitting or training are the only ones that
  score generalization.
* **D5, live challenge matches:** the most real data, but outward-facing; only with Wayne's yes.

#### D2a. Can a clone fitted to arena logs play like the real bot? (GPU; spec, 2026-11-24)

* **Why now:** it needs no fetched data. The bots whose code we run generate their own logs, so the true
  answer is known, and it puts gb10-d's idle GPU on the question that decides how D uses the archive.
* **Why today's clones miss** (first principles, `league/fit.py` on holdem-league): an action table indexed by
  (street, position, facing class, stack bucket, strength bucket), fitted with EM over the hidden cards.
  It has no memory: nothing of the line earlier in the hand, nothing of the match so far. Ashwing's adaptive
  bots and autodidact condition on both (autodidact keeps opponent statistics), so a table cannot express
  them, whatever the data size.
* **Bots:** `ext:ashwing`, `ext:autodidact_fast` and `ext:wolf` (one adaptive Python family, one bot with an
  opponent model, one deterministic JavaScript bot). Seeded through `set_seed` (holdem-x2r 30cfa1a).
* **Data (CPU), written in the Chipzen replay JSON shape that `league/replays.py` reads,** so the same
  parsers later read the real archive. Only what the arena shows: every action and amount, the board, and
  hole cards only at showdowns, for both players. The true hole cards of every hand go to a separate file,
  read only by the evaluation.
  * Fitting logs: seed 61, 5,000 matches per bot; match k's opponent is hero k mod 6 of (fb2-900's policy,
    the old heuristic bot holdem-chipzen 102b05e, raise_station, sticky_overbettor, tight_sticky,
    never_fold_pre). The sizes 100, 1,000 and 5,000 are the first matches by index (nested).
  * Held-out logs for read 2: seed 62, 1,000 matches per bot, the same hero mix.
* **Clone (GPU, torch on gb10-d), `tools/d2_clone.py`:**
  * **One feature builder** over replay-shaped events (`league/replays.py`: a raise's amount is the chips
    added). At play time the engine's `action_history` is first converted into that shape (raise-to and
    `all_in` become chips added), then the same builder runs. Nothing else computes features.
  * Inputs per decision: the bot's two hole cards and the board (52-way multi-hot each); the combo's hand
    strength on this board (`rl.features.hand_strength`, the deployed bot's function); street (4) and
    button (1); pot, to-call, both stacks in big blinds (log1p); facing class (`league/context.py`
    facing_class, one-hot NFCL); the last 12 actions of the hand, each (actor is the bot, `act_code` one-hot
    5, `size_frac` clipped to 4), zero-padded; the match so far, from the bot's seat: its opponent's count of
    each `act_code` per street (20 counts) divided by that opponent's decisions on the street, and the hand
    number.
  * Outputs: the action code over `act_code`'s 5 classes, masked by `legal_mask`; for a raise, its size
    bucket by `BET_EDGES` (4 buckets), played at the median `size_frac` of that bucket in the fitting logs.
  * Network: MLP, two hidden layers of 256, ReLU; Adam, learning rate 1e-3, batch 4,096.
  * EM over hidden cards: the prior is uniform over the combos that hold no board card (no hole card is known
    in a hand without a showdown). An action's likelihood is P(code), times P(size bucket | raise) when the
    code is a raise. Start: 5 epochs on showdown hands only. Then 8 iterations, each an E-step (on the GPU,
    every live combo weighted by the prior times the product of the likelihoods of every action the bot took
    in the hand, normalized) and an M-step (2 epochs of weighted cross entropy on both heads with the same
    weights, over K = 32 combos per hand drawn from the posterior, each with weight 1/32). Showdown hands keep
    their known combo with weight 1. Fixed iteration count, no convergence rule.
* **Baseline:** the `league/fit.py` table clone (its own buckets, 8 EM iterations) fitted on the same
  5,000-match logs.
* **Read 1, strength against us (the decision read):** fb2-900 (search off) plays 3,000 matches, seed 63, against
  each of: the real bot; a **control**, the real bot again with its `set_seed` offset by 1,000,003 (an
  independent run of the true bot); the neural clone at 1,000 and 5,000 matches; the table clone at 5,000.
  Within one bot every cell uses the same seed pairs; rows pair on (seed, hero_seat), the cell is the arm.
  `tools/d2_read.py` computes, per cell against the real bot, the paired difference (b - c) / n with a normal
  interval at z = 1.645 (90%). A cell passes when that interval lies within ±5 points (an equivalence test).
  * Power: at a 60% win rate the unpaired standard error of the difference is 1.26 points and the 90%
    half-width 2.08, so a true clone passes when the observed gap is under 2.92 points: probability 0.979
    per cell, without the pairing's gain. A perfect method passes control and clone for one bot with
    probability 0.958.
  * Each bot is judged on its own; no rule needs all three. The control must pass before that bot's clone
    verdicts count; a failed control gets one rerun on seed 64, and a second failure stops that bot unjudged
    (a harness fault to find, not a method result). Wolf is deterministic, so its control is identical by
    construction and only checks the harness.
* **Read 2, how close the actions are:** per-decision log-likelihood of the bot's actual action with the
  true cards, on the held-out logs, neural clone against the table clone.
* **What it decides, per bot:** the neural method is trusted for a bot when its clone passes read 1; the
  smallest passing size (1,000 or 5,000) is how many matches per name D needs for bots like it, and D1's
  per-name counts say for how many names that is reachable. A 5,000-match clone that fails is the finding
  for that bot: replay clones are not trusted for bots like it, and D leans on the parametric styles (D3) and
  real-arena evaluation. Read 2 reports all three sizes (100, 1,000, 5,000) for both methods.
* **Acceptance tests** (`tests/test_d2.py`, each shown to fail on a planted fault):
  1. the generated JSON passes `league/replays.check_conservation`, and hole cards appear only in hands
     that reached a showdown (fails if a hole card is written in a hand without one);
  2. for recorded hands, the input vector built from the replay JSON equals the one built from the live
     engine state at the same decision, match counts included (fails if a raise amount is read as raise-to);
  3. the fit code path never opens the true-cards file;
  4. a raise's likelihood includes the size-bucket factor;
  5. `tools/d2_read.py` on two row files with different opponent labels pairs 3,000 rows and uses z = 1.645;
  6. the seeds 61, 62, 63, 64, the offset, the sizes, 12 actions, K = 32, 8 iterations, 3,000 matches, ±5
     and 90% as literals.
* **Budget, in two stages.**
  * Stage 1, build and timing: the tests above, then three measured rates on gb10-d: generation matches per
    core-hour per bot with the hero mix; one EM iteration on the 1,000-match logs; clone against fb2-900
    matches per core-hour over 40 matches. Measured so far (fb2-900's policy against each bot, one gb10-d
    core, 40 matches, 2026-11-24): `ext:ashwing` 720, `ext:autodidact_fast` 510, `ext:wolf` 1,570 matches
    per core-hour.
  * **Stage 1 built** (holdem-d2 81871fc; 7 tests, each acceptance test fails on its planted fault). Rates on
    one gb10-d core, 2026-11-24 about 07:35 UTC, 40 matches each: generation with the hero mix `ext:ashwing`
    2,311, `ext:autodidact_fast` 1,036, `ext:wolf` 1,759 matches per core-hour; fb2-900 (RLBot) against the
    real bots 1,897, 829 and 2,424; a clone against fb2-900 9,800 (from a weak clone, so a real one may be
    slower). One EM iteration on 1,000-match-scale data 4.7 s on the GPU. The earlier 720, 510 and 1,570
    were the x3 hero at N = 1, which carries the λ range bookkeeping.
  * **Stage 2 budget from those rates:** generation 11.8 core-hours, read 1 15.6 core-hours, about 1.7
    box-hours on cores 4-19 (2.7 if every control reruns); fits about 0.25 GPU-hours; the table fits about 25
    CPU-minutes per bot. Under both caps, so nothing is dropped.
  * Stage 2's budget is computed from stage 1's rates and written here before stage 2 starts. Caps:
    generation plus read 1 at most 8 box-hours on cores 4-19, fits at most 3 GPU-hours. Over a cap, drop
    `ext:wolf` first (its control is trivial and its family is the easiest for us), then cut read 1 to the
    5,000-match clones.
* **Stop:** a stage past twice its computed budget stops; the bots and sizes that finished are recorded and
  judged, the rest are not. An acceptance test still failing after two fix rounds stops the slice.
* **Code:** a new branch holdem-d2 off holdem-x2r d4c3cb8, with `league/` brought in from holdem-league
  d554b8a (holdem-x2r has no `league/`) (`tools/d2_generate.py`, `tools/d2_clone.py`,
  `tools/d2_eval.sh`, `tests/test_d2.py` with the numbers above pinned literally: seeds 61, 62, 63, the offset,
  sizes and the other literals of test 6). Nothing reaches the deployed bot.
* **Review:** plan review 1 REVISE (3 blockers: a pass rule that a perfect clone failed most of the time and no
  control; unnamed buckets, inputs, prior, split and seeds; a budget without measured rates). Plan review 2
  REVISE (5 blockers: no tool could pair cells with different opponent names, and z was 1.96; no test that
  fitting features equal play features or that logs show only what the arena shows; the all-three-bots rule
  passed a perfect method only about 56% of the time and a failed control had no next step; the EM and play
  costs were unmeasured; the size head's place in the likelihood was open). All fixed here. The cap was
  reached, so no third review; Wayne's standing approval (2026-11-23) carries it.

### R1. Can the lookahead run in the arena?

* **Why:** the arena gives 0.5 vCPU x86 and 5 s per action (we budget 1 s). X3b's lookahead takes about
  1.5 s per decision on a whole gb10-d core at N = 128. Every gain the X line proves is worth nothing in the
  arena if no affordable version keeps it.
* **Timing:** `tools/r1_timing.sh` (holdem-x2r) plays x3 at N = 128, 32 and 8 against tight_sticky and
  `ext:ashwing`, 2 matches, seed 49, one core, on the PC (x86) and on gb10-d, the same seeded matches on both,
  so the two compare decision for decision; `tools/dec_time.py` prints mean, p95 and max. Arena estimate:
  twice the PC's single-core time (0.5 vCPU); a cloud vCPU may be slower than the desktop core, so a setting
  fits only with mean at most 0.5 s and max at most 2 s on the PC.
* **Gain at smaller N:** x3 at the largest N that fits and at N = 8, Z = 2.6, seed 49, rule and `ext:`
  cells, against N = 1 off arms (the rule off arms of X3b are reused; the `ext:` off arms run again with the
  seeded bots), read paired.
* **Read:** if a fitting N keeps most of N = 128's gain, the lookahead can ship as it is once a candidate
  exists. If none does, the deploy path is distillation (train the policy on the search's choices, which the
  2026-11-21 adaptive-training study recommends), specified then.
* **E3 for a search candidate:** an exploiter cannot train against the Python lookahead in the C engine, so
  it trains against the candidate's policy, then plays the candidate with its lookahead in the SDK engine.
  That reads the floor the lookahead adds or loses on top of the policy's.
* Measurement only: nothing changes in the deployed bot. No plan review (a probe), per Wayne's standing
  approval of 2026-11-23.
* **Result (09:32 UTC, experiments 14.22):** N = 32 fits (box 0.25 to 0.43 s mean, 1.0 s max per decision) and
  keeps the gain: `ext:` +2.8 [+0.9, +4.7] paired, rule pool +0.1 [-1.6, +1.8] (sticky_overbettor -3.0).
  N = 8 loses 12 points on both pools. Deploy path: the lookahead at N = 32, no distillation for runtime. Not a
  candidate (rule pool lower bound -1.6); X4 is next.

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
