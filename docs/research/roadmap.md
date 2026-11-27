# Roadmap: the long-term strongest Chipzen HUNL bot

Set 2026-11-22. Wayne's goal: the long-term strongest bot, a "future king". The Season 16 deadline does
not matter. The Season 16 entry is `poker-ai-lab-v4` (rl-fb2-900 plus the all-in answer of S0, image sha256
0291ee39...) since 2026-11-22 18:45 UTC, Wayne approved. `poker-ai-lab-v3` (rl-fb2-900) stays uploaded.
v5 (GS50, 14.51) passed the full upload gate on 2026-11-27 and is uploaded as `poker-ai-lab-v5`; the Season 16
swap window had closed, so v4 stays entered. To continue on a new machine, read `restore.md` first.

## Where we are (2026-11-27 08:23 UTC)

**Redirect (Wayne, 2026-11-27 08:23 UTC):** the known-opponent expert line (G0 to V6b) stops; it is not a global solution. The roadmap agent's plan is "### Global path" and its first slice "### GP0." (a measurement: the lookahead's ceiling where the base is weak, whether a model fitted only on arena-visible logs carries it on real code, and the sturdier base on the aggressor styles). V6b is parked (its Status line).


The bot is three parts (Wayne, 2026-11-21): an opponent model, a decision procedure that maximizes the match
win probability against it, and a safety blend. Revision 2's lookahead work (14.17 to 14.24) showed the
procedure has headroom but the opponent model at the root loses it; it is parked behind Revision 3.

Revision 3 re-aimed the judge at the opponents an entrant actually meets (14.29: the solver-like family about
37% of entrant seats, small-ball aggressors next). Its first reads settled the direction:
1. **Population, not capacity** (14.30, 14.31): one hour against `small_ball` lifts fb2-900 from 75.7% to 97.6%;
   two hours against bp100 from 59.9% to 79.7% (+19.9 [+18.1, +21.6]). The same network learns both once it
   meets them, at a cost on styles it stops seeing (`tight_sticky` -4.0).
2. **The river call-off leak is a training gap** (14.31): 594 to 57 per 4,000 matches, so B0 step 1 does not run.
   The bp100-trained policy still loses big pots on its own called shoves; whether those lose chips is open.
3. **Match value is near linear against bp100** (14.28), so chip EV is a fair training target there.

4. **One mixed policy loses on the old families** (14.36): B1 (bp100 a third of the SDK list plus `small_ball`)
   gains +5.4 on bp100 and +6.5 on `small_ball` (a quarter of each specialist's gain) and loses 3.4 to 4.6 on the
   Ashwing and autodidact cells, whose training share it halved. No v5; v4 stays. B1's stop was a logging false alarm (14.35).
5. **G1 fine-tuned per name reads ranges best but fails fold calibration** (14.34); no more GPU for it.

6. **The real-bot loss stays without the new data** (14.38, D0): B1's recipe on fb2's own population loses -2.70
   [-4.02, -1.38] pooled on the four Ashwing and autodidact cells; rule INCONCLUSIVE (straddles -2.0), no lever
   decision. Three families sit within 0.2 of B1; hive alone shows a new-data effect. C0 (14.40) reads PEAK: fb2's
   own it 700 and 800 lose 2.9 pooled on the Ashwing cells, so fb2-900 is a local high and these guard losses sit
   inside one run's checkpoint spread. D-null, P1b and "restore the shares" close.

7. **One network holds all three teachers** (14.39, AD0 rule 1): a plain 256-wide student distilled from T1, C1
   and fb2-900 plays bp100 +19.4, `small_ball` +19.8 and the two Ashwing cells +1.1 [-0.7, +2.9] against fb2-900.
   B1's shortfall is the training method (PPO on the mix), not identity or capacity. AD1 and S7 drop.

8. **A teacher for `chipzen`** (14.41, TT T-b): an hour of PPO from fb2-900 gains +11.8 [+9.4, +14.1] there (fb2-900
   wins 67.5%) and joins V5b; teachers for `sticky_overbettor`, `loose_passive` and `never_fold_pre` gain about 4.6
   where fb2-900 already wins 84 to 94% and do not.

9. **V5b, specialists plus coverage in one student, DEFAULT FAIL** (14.46): headline +10.57, bp100 +15.5, ten of
   eleven held-out cells inside the guard, but `sticky_overbettor` -4.2 [-6.1, -2.4] and `small_ball` only +7.3. A
   pooled cross-entropy student plays the row-weighted average of its teachers before it knows the opponent.
   Ensembling three fits adds nothing. T-a (14.45): `br_ashwing` +16.0 and +15.4, `br_autofast` +13.4, kept for later.

10. **G0, the gated mixture, GUARD FAIL** (14.47): chosen G50; small_ball +16.1 (V5b +7.3), bp100 +15.2, every other
   held-out cell within 1 point of level, but `sticky_overbettor` -5.9 [-7.2, -4.6] (fresh -6.4) and `chipzen` +2.6
   under its +5.10 line. The gate works on the opponents it names; it fails open-set: a closed four-way softmax routes
   an unseen bot to the expert it looks like, with rising confidence (92% off the default past hand 40).
11. **G0b steps A to C: S1 and S2 PASS** (14.49): with the six bet-size terms the gate routes `sticky_overbettor`
   at most 4.8% (GS50, G50-actor rows; 4.9% on fb2-900's) and 0% (GS80), against G80's 65% past hand 40, and GS80 routes 91 to 100% of true bp100 and
   `small_ball` hands from hand 11.
12. **G0b step D: GS50 PASS** (14.50): bp100 +18.4 [+16.7], `small_ball` +18.8 [+16.9], `chipzen` +7.0,
   `sticky_overbettor` -0.2 on fresh seed 113, test styles pooled -0.1; 23 of 23 league opponents at 80% or more
   on the screen.
13. **C1v5: v5 = GS50 as entered, VERDICT PASS** (14.51): headline +13.21 [+12.00], bp100 +18.9 [+17.2],
   `small_ball` +20.1 [+18.1], twenty new styles pooled -0.2; 23 of 23 league opponents at 80% or more over 400
   (lowest 83.25%); head to head over 102b05e 76.25% (Wilson lower 71.8%). The first candidate to clear the gate.

Next: **E2** (spec below): experts for the Ashwing and autodidact families, where v5 equals fb2-900, with R3 beside
it to size the solver class that follows.

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
* **Held, resolved 25 Nov (14.31):** river call-offs 57 against 594, so B0 step 1 does not run. Was: B0 step 1 until T1's chipflow read. If the bp100-trained policy still makes river call-offs at more
  than half of fb2-900's rate (594 per 4,000 matches at equity 0.198, 14.27), step 1 runs as revised below; if not,
  training fixes it for known bots and B0a returns later as the unseen-name version on top of G1.
* **Now (25 Nov 08:13 UTC):** A0, C1, T1 done; B1 built, outcome verifier running, then training; G1 on its last
  split.
* **Critical path (as planned 24 Nov; now about three days ahead: B1 training 25 Nov, candidate read 26 Nov):** T1 read (25 Nov) → B1 spec (one page, full process; population fb2-900's league mix plus bp100
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
  harness fault voids a read; 97 `small_ball_b`'s strength note; 98 T1's transfer read (14.33); 99 and 100 B1's fallback P1b
  screen and confirmation; G1 step 2a uses D2a's logs (61, 62) and bootstrap 47, no new arena seed. League pair ranges (seeds by `pair_seed`): 0-199 league row, 200-399
  E1 gate, 400-499 B1's screen, 500-599 P1b's screen. Training seeds stay those of
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
  trained alone (`tight_sticky` -4.0). T1 gives the same reading for bp100: **T1 gain = +19.9 [+18.1, +21.6]** (14.31):
  branch A, population P1. 14.29: an entrant meets a regular in 5.4% of its seats, so the judge is weighted by what
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
* **Branch switch:** `tools/b1_run.sh P1` (branch A) or `tools/b1_run.sh P2` (branch C); any other argument exits 2.
  P1 runs through `tools/bpq.sh` with `BPQ_CONTAINERS=1` (holds `~/bpq.lock` for the whole run); P2 with
  `BPQ_CONTAINERS=0` (no lock, so B0 step 1 can use the queue meanwhile). Both pass `BPQ_SLICE=B1 BPQ_SEED=1
  BPQ_KIND=train`.
* **Training command, literal (`tools/b1_run.sh P1`; run from `~/poker-ai-lab-rl`):**
  `python -m rl.train --out ckpt/b1 --init ckpt/fb2/it000900.npz --seed 1 --workers 2 --sdk-workers 10 --sdk-opps
  bp100,chipzen,small_ball,ext:ashwing_v2,bp100,ext:ashwing_value,bp100,chipzen,small_ball,ext:ashwing_adaptive,bp100,ext:autodidact_fast
  --heur-batch 10000 --envs 96 --steps 3000 --max-minutes 360 --lr 1.5e-4 --clip 0.1 --floor 0.15 --snap-w 0.3
  --snap-every 25 --clones data/clones.npz --pool-dir pool_b1 --opp-w arch:5=4,arch:2=3 --distill
  data/maniac_labels.npz --distill-w 0.5`. `P2` differs only in `--sdk-opps
  chipzen,ext:ashwing_v2,small_ball,ext:ashwing_value,chipzen,ext:ashwing_adaptive,small_ball,ext:autodidact_fast`.
  Every other flag is `tools/rl_fb2.sh`'s (holdem-rl 114a136), with `--seed 1` and the pool directory written out.
* **Pinned inputs, checked by `b1_run.sh` before anything starts; a mismatch stops the run naming the file (exit 4,
  `logs/b1/failed`):** `data/clones.npz` 93b5be2828166c7a6c2e20389e4ff24ce6cd1ac024ecbc762f9de6c02d3e0354;
  `data/maniac_labels.npz` 36534c2f5465f0f7a7c81f519aa7052c124c8fe2ab78eff123f64f4d08607057; `pool_gen/a_ablA.npz`
  4cf2a4183be22a16da010c66229e4beba2c5fedc7f63e4476c69e4c6b4e5b92b; `pool_gen/b_distill1.npz`
  6fafbb535ae8f6dd94e8e478ee734297a5bedb9117c8aa898a9fc425b2525dcd; `ckpt/fb2/it000900.npz` policy arrays equal to
  `rl/models/fb2_it000900.npz`. The pool is frozen: `b1_run.sh` creates `pool_b1/` (refusing if it holds other
  content), copies the two pool files after their hashes pass, and trains with `--pool-dir pool_b1` (`rl.train` takes
  the last four `*.npz` by name and re-reads the directory every 10 iterations). These two are fb2's pool: the only
  files in `pool_gen`, dated 2026-11-22 08:29 box time, before fb2's first checkpoint (14:03), and 14.4 says "two
  fixed past policies"; fb2's log does not name them. Every `train.jsonl` row's `pool` field must read
  `["a_ablA.npz", "b_distill1.npz"]`; the runner checks at its rate-stop minute and at the end and marks the run
  failed otherwise.
* **Length and checkpoints:** 360 minutes; read set: the checkpoints at 300, 600, 900, 1,200, 1,500 and 1,800
  iterations after the first row's `it` minus 1, as far as they exist, plus `latest.npz` (holds whether or not
  `--init` continues the iteration count).
* **Queue runner `tools/bpq.sh` (lifted once from `tools/t1_run.sh`, sourced by every bp100 job from here on):** the
  single BP_* export block (bpopp:v011, BP_AT=65000, BP_THRESHOLD=0.35; BP_CPUS=1 only for training), `flock` on
  `~/bpq.lock`, launch in its own process group, T1's rate stop (with the half-written-row case counted as rate 0),
  wait with `kill -0`, a final empty `docker ps --filter name=bpopp-` check, markers `done`, `failed`, `stopped`, and
  a seed check against `tools/seed_registry.txt`. T1's tests move with it.
  * Inputs: `BPQ_SLICE`, `BPQ_SEED`, `BPQ_KIND` (`read` or `train`), `BPQ_CONTAINERS` (1 or 0). With
    `BPQ_CONTAINERS=0` the job takes no lock, exports no BP_* and skips the docker checks; the process group, rate
    stop, markers and seed check stay.
  * Registry format: one line per entry, `seed slice kind`, whitespace separated, `#` comments. A read passes only if
    the line `BPQ_SEED BPQ_SLICE read` exists; a training job passes only if `BPQ_SEED * train` exists (training
    seeds are shared by every slice, as `tools/rl_br.sh` and `tools/rl_fb2.sh` share `rl.train`'s default 1).
    Literal initial contents (the envelope registry above; 89 is unused and absent):
    `1 * train` / `81 S2r read` / `81 T1 read` / `82 T2 read` / `83 D2b read` / `84 D2b read` / `85 D2b read` /
    `86 D2b read` / `87 T1 read` / `88 B0 read` / `90 A0 read` / `91 B0 read` / `92 G1 read` / `93 C1 read` /
    `94 B1 read` / `95 B1 read` / `96 B1 read` / `97 B1 read`.
* **Owner files (executor, holdem-rl worktree):** `tools/bpq.sh`, `tools/b1_run.sh`, `tools/seed_registry.txt`;
  `holdem/opponents.py`, `rl/sdk_rollout.py` (the patch); `tests/test_b1.py`, `tests/test_bpq.py`, plants in
  `tools/b1_mutate.py`. In holdem-x2r: `SmallBallB` in STYLES, its target in `tools/style_bots_check.py`,
  `tools/b1_judge.sh`, `tools/b1_read.py`, and the entrant-seat step in `tools/a0_field.py`. In holdem-league:
  `tools/league_fresh.py`, `tests/test_league_fresh.py`. In holdem-rl also `rl/bot_ckpt.py`, and after selection
  `rl/bot_b1.py` with `rl/models/b1.npz`. **Non-goals:** no change
  to `rl/train.py`, `rl/features.py`, the network, `rl/bot.py`, `rl/allin.py`, the eval card or the existing league
  tools (`league_fresh.py` is new); `rl/models/b1.npz` exists only after selection, in its own holdem-rl commit, and
  never enters an image, holdem-chipzen or the deployed bot.
* **Writes, each with its rollback:**
  1. Commits on holdem-rl, holdem-x2r, holdem-league (local branches): revert them.
  2. gb10-d `~/poker-ai-lab-rl/`: `ckpt/b1/`, `ckpt/b1_smoke_P1/`, `ckpt/b1_smoke_P2/`, `logs/b1/`, `pool_b1/`: delete.
  3. gb10-d `~/poker-ai-lab-x2r/logs/b1/`: delete.
  4. gb10-d `~/poker-ai-lab-league/`: `candidates/b1-src/`, `candidates/rl-b1/`, `out/b1/`, `out/verify-rl-b1/`,
     `logs/add-rl-b1.*`: delete; the `rl-b1` entry in `candidates.json`: remove; rows with `cand:rl-b1` in
     `out/league/results.jsonl` (copy the file to `results.jsonl.pre-b1` before `league_add.sh` runs): restore the
     copy; `out/leaderboard.md`: rebuild with `PYTHONPATH=. .venv/bin/python -m league.report --out out/league --md
     out/leaderboard.md`.
  5. PC `poker-ai-lab-league/reports/league/leaderboard.md` (written by `league_add.sh`): copy the rebuilt
     `out/leaderboard.md` back.
  6. `~/bpq.lock` (empty lock file): leave.
* **Reads: select on one seed, confirm on another.**
  * Screen, seed 94: each read-set checkpoint against bp100 (1,000 matches), `tight_sticky`, `sticky_overbettor`,
    `small_ball_b`, `never_fold_pre` (500 each), plus the league screen below. Selection: checkpoints ordered by the
    screen score; the first that passes the league screen filter is chosen; none → B1 ends with that finding.
  * **Screen score (literal):** the unpaired weighted win rate on seed 94 over four cells, the judge weights without
    `ext:autodidact` renormalized by 0.97: bp100 0.7216, `tight_sticky` 0.1031, `sticky_overbettor` 0.0928,
    `small_ball_b` 0.0825. `never_fold_pre` is reported at the screen and not ranked; it is guarded only by the
    confirmation rule. No fb2-900 run on seed 94 (ranking is among B1's checkpoints only).
  * **E1, the league guard: one tracked driver, two disjoint pair ranges.** A league match's seed is
    `pair_seed(opponent, pair index)` (`league/run.py`), so a pair range is a seed set: 0 to 199 is
    `tools/league_add.sh`'s league row; 200 to 399 is the eval card's E1 (fb2-900's rows:
    `~/poker-ai-lab-league/out/verify-fb2-900/results.jsonl`, 9,600 matches); 400 to 499 is new, B1's screen, spent
    after B1. Driver (new, holdem-league on d554b8a): `tools/league_fresh.py --name NAME --root DIR --module M --class C
    --p0 A --p1 B --workers W --out DIR [--h2h CAND]`, the verifier's untracked `~/verify-distill1/confirm.py` made a
    tool: NAME against the 23 opponents of `league/data/clones.npz` (hash asserted) on pairs A to B-1, both seats,
    through `league.run.run_task` unchanged, plus CAND when given; counts illegal actions and exceptions; resumes;
    writes `summary.json` (per opponent wins, n, rate, Wilson 95% lower bound; the lowest; the count at or above 80%).
    * Checkpoints enter the screen through holdem-rl `rl/bot_ckpt.py` (`class CkptBot(RLBot)`, model path from
      `RL_CKPT`, raising if unset), the B1 commit exported once with `tools/league_export.sh <holdem-rl> <B1 commit>
      b1-src`. Screen command (gb10-d, `~/poker-ai-lab-league`, per checkpoint ITER): `RL_CKPT=$HOME/poker-ai-lab-rl/
      ckpt/b1/itITER.npz PYTHONPATH=. .venv/bin/python tools/league_fresh.py --name b1-itITER --root
      candidates/b1-src --module rl.bot_ckpt --class CkptBot --p0 400 --p1 500 --workers 8 --out out/b1/screen-itITER`
      (4,600 matches, about 4 minutes). Screen filter: the lowest of the 23 at least 78.0% (slack for n = 200; it
      selects, it does not gate).
    * Gate, chosen checkpoint only, pairs never used in selection: a holdem-rl commit adds `rl/models/b1.npz` (its
      policy arrays) and `rl/bot_b1.py` (`class B1Bot(RLBot)`), the S2 it1800 way; then from the PC league checkout
      `tools/league_add.sh /c/Users/WEI-CHENG/Desktop/poker-ai-lab-rl <that commit> rl-b1 rl.bot_b1 B1Bot` (pairs 0
      to 199, the leaderboard row), and on gb10-d `PYTHONPATH=. .venv/bin/python tools/league_fresh.py --name rl-b1
      --root candidates/rl-b1 --module rl.bot_b1 --class B1Bot --p0 200 --p1 400 --h2h chipzen-102b05e --workers 8
      --out out/verify-rl-b1` (9,600 matches). **E1 holds** when all 23 opponents are at 80% or more over pairs 200 to
      399 (Wilson lower bounds reported) and the heuristic head to head on the same pairs has its Wilson 95% lower
      bound above 50%; the paired difference against fb2-900 per opponent is reported from its verify rows.
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
  paired gain under -2.0 and its upper bound under zero; E1 holds (gate command above). Then the remaining gate: heuristic head to head
  (covered by the E1 gate's `--h2h` cell), the eval card with E3 reported, a fresh outcome verifier, Wayne. A
  headline fail with a bp100 pass is recorded as "exploits the proxy, does not generalize" and feeds B1r.
* **`small_ball_b`, judge only:** target the mean of BonnieBlue, Chaos_Incarnate, Velvet_Shark in A0's
  `vectors.json`: vpip 0.75, pfr 0.54, shove 0.07, fold_pre_raise 0.33, post_aggr 0.58, post_fold_bet 0.56,
  bet_size 0.38, showdown 0.12 (0.35 from `small_ball`'s target). Acceptance: under 0.25 from its target on style
  seeds 3 and 4 (300 matches against fb2-900, explicit commands as A0's) and more than 0.25 from `small_ball`'s
  measured vector. Strength note: bp100 against it, 400 matches, seed 97.
* **Tests (each failing on its plant):** 1 a 5-minute P1 smoke run (`--max-minutes 5`, own `--out`): the last row's
  `sdk_samples` keys (decisions, cumulative, list spelling) are exactly P1's seven distinct names (bp100, chipzen,
  small_ball, ext:ashwing_v2, ext:ashwing_value, ext:ashwing_adaptive, ext:autodidact_fast); shares in matches: per
  opponent M = sum over rows of `wr[key][0]` (each row counts the matches since the previous one; the heuristic is
  keyed `heuristic`), S = the sum of `wr[k][0]` over exactly the SDK keys `bp100, heuristic, small_ball,
  ext:ashwing_v2, ext:ashwing_value, ext:ashwing_adaptive, ext:autodidact_fast` (C-engine keys in `wr` are
  excluded), S at least 240 counting those matches only (else inconclusive, the run is lengthened, never a pass):
  bp100 0.27 to 0.40, small_ball 0.11 to 0.23, heuristic 0.11 to 0.23 (plants: bp100 once; small_ball missing; a
  toy-row unit test with C-engine keys present gives bp100 = 1/3 on balanced SDK counts). P2 case, a 5-minute
  `b1_run.sh P2` smoke run: `sdk_samples` keys exactly the six distinct names of P2 (no bp100), S over the six SDK
  keys at least 240, heuristic 0.17 to 0.33 and small_ball 0.17 to 0.33 (plants: bp100 present; small_ball missing); 2 `small_ball` in holdem-rl
  plays the same actions as in holdem-x2r on a fixed stream, by a hash recorded in x2r (plant: `street_bet`
  dropped); 3 no judge-only name in the training command or any `sdk_samples` key (plant: `small_ball_b` added); 4
  the INIT and cross-tree checks (plant: a changed feature in one tree); 5 `bpq.sh`: a second container job blocks
  on the lock, the rate stop kills only its group and leaves no container, a normal exit leaves none within 60 s, an
  unregistered seed is refused, a half-written last row gives rate 0, the B1 training invocation (`BPQ_SLICE=B1
  BPQ_SEED=1 BPQ_KIND=train`) passes, `94` under `BPQ_SLICE=T1` is refused, unlisted `98` is refused, a
  `BPQ_CONTAINERS=0` job starts while the lock is held (plants: lock removed; own-group kill; registry check
  skipped; JSON error uncaught; slice ignored in the read check; P2 taking the lock); 6 `b1_read.py` on toy rows: selection reads only seed 94,
  confirmation only 95 (plant: selection on 95), the ranking is the literal screen score (plants: one weight
  changed; a seed 95 row added), weights are the literals and sum to 1, a cell at -3 with upper
  bound under zero fails the rule even when the headline passes (plant: guard dropped); 7 literals (360, the read
  set, 94 to 97, pairs 400-499 and 200-399, every n, 80%, 78.0%, -2.0, P1 and P2); 8 `league_fresh.py --p0 200 --p1
  202` for rl-fb2-900 reproduces row for row (seed, hands, a_win) its rows in `out/verify-fb2-900/results.jsonl`
  (plant: pair index shifted by one); 9 the opponent list is the clones file's 23 and its hash is asserted (plant: a
  baseline dropped); 10 with `RL_CKPT` at fb2-900, `CkptBot` plays the same matches as `Fb2b900Bot` on pairs 400 and
  401 against two opponents, and unset it fails (plant: a default path); 11 `b1_read.py` refuses a gate summary whose
  pairs overlap the screen's (plant: gate on 400 to 499); 12 a one-byte change in a copy of `maniac_labels.npz` makes
  `b1_run.sh` exit 4 before any process or container starts, naming the file (plants: check removed; a file compared
  with itself); 13 a third file in `pool_gen` does not enter: `pool_b1/` holds two files and the smoke rows read the
  pinned pool, for P1 and P2 (plant: `--pool-dir pool_gen`); 14 `b1_run.sh`'s P1 and P2 commands equal their
  literals token for token and differ from `tools/rl_fb2.sh` only in `--out`, `--init`, `--seed`, `--sdk-opps`,
  `--max-minutes`, `--pool-dir` (plants: `--opp-w` dropped; P2 carrying bp100).
* **Review record:** plan review 1 REVISE (E1 had no runnable command and the screen could select on the
  gate; test 1's name count and unit; the recipe depended on unpinned box state). Fixed above from the roadmap
  agent's first-hand reads (`league/run.py` `pair_seed`; the verifier's untracked fresh-seed driver; `pool_gen`'s two
  files and the input hashes on gb10-d). Plan review 2 REVISE (registry format and the training seed; the screen
  statistic undefined; test 1's denominator; branch C untested and the lock under P2; writes and rollback
  incomplete, `rl/models/` contradiction), fixed above. Readiness cap reached (two REVISE); proceeding under the
  standing approval, as for T1 and the envelope; the outcome verifier is the remaining check.
* **Stops:** rate stop at minute 15 (floor 2 per minute); entropy under 0.2 or a non-finite loss stops the run and
  keeps the last good checkpoint; budget 9 box-hours, stop at 18; a test still failing after two fix rounds stops the
  slice.
* **Box:** under P1 training holds the bpopp queue for 6 hours (10 containers at one CPU each), pinned to cores
  0-17; G1 keeps cores 18-19 and the GPU. Screen and confirmation after training, bp100 cells alone in the queue.
  Under P2 there are no containers and no lock (`BPQ_CONTAINERS=0`), so the queue is free for B0 step 1.
* **Added 25 Nov after 14.31 to 14.33 (reported, not deciding):** the read also runs `tools/chipflow.py` on the
  chosen checkpoint against bp100 (4,000 matches, seed 95) and reports 14.33's shove class table beside fb2-900's and
  T1's; P0 is printed for continuity only. B0 is closed for bp100 (training removed the river call-off); B0 step 1
  stays on file for a name we cannot train against. Match value is quoted under the candidate's own empirical curve.
* **Outcome, 25 Nov (14.36):** rule FAIL on four real-bot guard cells; headline +3.94, bp100 +5.4, E1 holds. No v5.
  The verifier corrected the reading: the failing families are P1's own at half fb2's share (dilution or
  interference, D0 separates them). P1b is parked (only relevant under D0's MIX reading); B1r is parked; the
  headroom (14.5 and 15.4 points against the 8-point aid) is the reason for AD1.
* **Fallback, pre-registered 25 Nov:** if no checkpoint passes the league screen filter, one rerun P1b, identical
  except bp100 at 2 of 12 entries (the two freed entries go to `chipzen` and `ext:ashwing_v2`), screen seed 99,
  confirmation seed 100, league screen pairs 500 to 599 (gate pairs unchanged, 200 to 399). A second failure ends B1
  at this representation and brings B1r forward. (14.33: a pure bp100 response costs 13 points on other styles.)
* **Amendment, 2026-11-25 10:09 UTC, before any checkpoint was read** (no `screen*` directory existed under
  `~/poker-ai-lab-x2r/logs/b1/` or `~/poker-ai-lab-league/out/b1/`; training at iteration 560; the outcome verifier
  confirms this from file times):
  1. Read set extended: training runs at about 8.8 iterations a minute (about 3,100 in 360 minutes), so the read set
     becomes 300, 600, 900, 1,200, 1,500, 1,800, 2,100, 2,400, 2,700 iterations after the first row's `it` minus 1,
     plus `latest.npz` (ten). Selection stays on seed 94 and league pairs 400 to 499.
  2. Guard cell `loose_passive` (judge only, holdem-x2r STYLES): mr_hide's style, 5.7% of entrant seats, 0.36 from
     the nearest cell. Target A0's `vectors.json` mr_hide: vpip 0.774, pfr 0.315, shove 0.015, fold_pre_raise
     0.200, post_aggr 0.269, post_fold_bet 0.210, bet_size 0.307, showdown 0.353. Acceptance as `small_ball_b`
     (under 0.25 from the target on style seeds 3 and 4, 300 matches against fb2-900). It enters the screen (500
     matches, reported, not ranked) and the confirmation (2,000, seed 95) as a guard under the existing -2.0 rule;
     the headline weights are unchanged, so the rule only gets stricter.
  3. Reported in the read, not deciding: adaptation headroom per class = the single-opponent ceiling (T1 +19.9 on
     bp100, C1 +21.9 on `small_ball`) minus B1's paired gain on that cell; and bp100's and `small_ball`'s share of
     `sdk_samples` (decisions) beside their share of matches from `wr`.
  4. fb2-900's baseline arm on seed 95 for every non-container confirmation cell runs before training ends (cores
     18-19), so tomorrow's confirmation needs only the candidate arm. Exception, 12:13 UTC (amendment verifier):
     `ext:wolf` runs Monte Carlo against a 300 ms wall-clock deadline, so its fb2-900 arm is rerun at confirmation
     with the candidate arm's placement (move the cores 18-19 rows to `confirm/fb2_1819/`, reported only). Confirm
     also stops if any weighted or guard cell is missing from either arm (b1-x2r 8be6e38).
* **Consumers:** candidate v5 (with S0); B1r's direction; later judges' weights.
* **Executor checks first:** v4's exact E1 command; a holdem-rl checkpoint loads in holdem-x2r; the iteration rate
  with this mix (smoke run); wall-clock effect of slow SDK opponents on bp100's share; whether fb2's recipe still
  moves past 900 (if no checkpoint beats fb2-900 on bp100 and `small_ball_b` at the screen, that is a finding and
  B1r comes forward).

### D0. Was B1's real-bot loss the new data or the mix? (spec, 2026-11-25; tier 2)

* **Question:** B1 lost 3.4 to 4.6 points on the Ashwing and autodidact cells and 8.5 on the heuristic (14.36). Does
  that loss come from the bp100 and `small_ball` samples (interference), or from the rest of B1's update (the C
  engine's larger share of the old data, or plain continued training from a selected checkpoint)?
* **Decision it feeds:** under NEW DATA the identity line (AD1) is the lever and no population reshuffle runs; under
  MIX OR CONTINUATION, D-null runs and the next population is set by C-engine steps. AD1's real-bot guard and its
  GAINS ONLY branch are read with D0's verdict. No candidate comes out of D0.
* **Why this design (the update rule):** PPO takes minibatches of 4,096 decisions from the whole iteration batch with
  a mean loss and Adam (the inline 4-epoch loop in `rl/train.py` at a4d765d), so the pull between families is set by
  their shares of the iteration batch, counted in decisions (`--heur-batch` is a threshold on SDK decisions,
  `sdk_samples` counts decisions). B1's own `ckpt/b1/train.jsonl`, first to last row (2,290 iterations): 16,287
  decisions per iteration, C engine 6,070, SDK 10,218 (bp100 3,238, `small_ball` 1,009, ext 4,530, heuristic 1,440;
  ext : heuristic 3.15). Shares of the batch:

  | Population | ext (4 names) | heuristic | bp100 | `small_ball` | C engine |
  |---|---|---|---|---|---|
  | B1 (P1, `--heur-batch 10000`) | 27.8% | 8.8% | 19.9% | 6.2% | 37.3% |
  | D0 target (fb2's 6 entries) | 37.6% | 12.0% | 0 | 0 | 50.4% |

  D0 keeps B1's old data and drops the rest: old-family SDK 5,971 per iteration (ext 4,530, heuristic 1,440), C engine
  6,070. `--heur-batch 5750` because the threshold overshoots by about 220 decisions per iteration (B1: 10,218 against
  10,000). Every B1 minibatch is 73.9% old data in that ratio plus 26.1% new data; every D0 minibatch is the old data
  alone in the same ratio, and at equal iterations both runs have seen the same old-family decisions. A higher
  `--heur-batch` (the withdrawn B1v) keeps ext : bp100 fixed and separates nothing. Every population table from here
  on states shares of the iteration batch in decisions, C engine included.
* **Code:** holdem-rl branch `d0` (local, worktree `poker-ai-lab-d0`) at 60ff10d: B1's training commit a4d765d (so
  the trainer and minibatch rule are B1's), `tools/bpq.sh` from 126c673 (the 3-row entropy guard of 14.35),
  `tools/b1_run.sh D0`, `tools/d0_read.py` (void check, paired cells, rule). Tests: `test_d0_prints_its_literal_command`,
  `tests/test_d0_read.py` (every row of the rule table, pairing refuses mismatched keys, pooled error, void check
  passes B1's mix and voids the 5,000-decision mix, literals); two plants (BOTH widened, old share scaled) caught.
  Box: 59 passed. Eval tree: holdem-x2r 8be6e38 archived at `~/d0-run/x2r`; fb2-900 on `ext:ashwing` seed 95 (60
  matches) reproduces the stored B1-judge rows 60 of 60.
* **Command (literal):** `python -m rl.train --out ckpt/d0 --init ckpt/fb2/it000900.npz --seed 1 --workers 2
  --sdk-workers 10 --sdk-opps chipzen,ext:ashwing_v2,ext:ashwing_value,chipzen,ext:ashwing_adaptive,ext:autodidact_fast
  --heur-batch 5750 --envs 96 --steps 3000 --max-minutes 190 --lr 1.5e-4 --clip 0.1 --floor 0.15 --snap-w 0.3
  --snap-every 25 --clones data/clones.npz --pool-dir pool_b1 --opp-w arch:5=4,arch:2=3 --distill
  data/maniac_labels.npz --distill-w 0.5`, through `B1_MINUTES=190 bash tools/b1_run.sh D0` (B1's pinned hashes,
  frozen pool, no containers). Run directory `~/d0-run` on gb10-d: the 60ff10d archive with `data/clones.npz`,
  `pool_gen/`, `ckpt/fb2/` and `.venv` linked from `~/poker-ai-lab-rl`; markers `logs/d0/`.
* **Length:** an 8-minute smoke (B1_OUT=d0smoke) ran 60 iterations in 7.6 minutes, 7.9 per minute, so it 1,200 needs about 152 minutes; 190 minutes leaves 25%. The smoke's void check: C engine 6,084, old-family SDK 5,919, ext : heuristic 2.99 (all within tolerance). A run that stops before it 1,200 (guard, time or crash) is void and is not read; it is
  recorded and rerun once with the same command from fb2-900.
* **Void check before reading:** `python tools/d0_read.py void ckpt/d0/train.jsonl` (first to last row of the
  cumulative `steps` and `sdk_samples`): C engine per iteration within 5% of 6,070, old-family SDK within 5% of
  5,971, ext : heuristic within 0.3 of 3.15. Outside: void, recorded, not read.
* **Read, no selection:** checkpoint it001200 only (B1's chosen iteration, equal old-data exposure).
* **Cells (seed 95, 1,000 each, after D0's training ends and before AD1's starts, so nothing else trains):** from
  `~/d0-run/x2r`, for each of `ext:ashwing`, `ext:ashwing_hive`, `ext:ashwing_search`, `ext:autodidact`:
  `taskset -c 0-17 nice -n 5 ~/poker-ai-lab-rl/.venv/bin/python -m rl.eval_arena --model ~/d0-run/ckpt/d0/it001200.npz
  --opp CELL --matches 1000 --seed 95 --workers 6 --rows ~/d0-run/logs/d0/read/it001200/CELL.jsonl` (B1's judge
  placement). None is a wall-clock bot. Rule: `python tools/d0_read.py rule ~/d0-run/logs/d0/read/it001200
  ~/poker-ai-lab-x2r/logs/b1/confirm/fb2 ~/poker-ai-lab-x2r/logs/b1/confirm/cand` (B1 it001200's rows are `cand`).
  Each cell's gain is paired on (seed, hero seat), in points of match win rate; the pooled gain is the mean of the
  four, its standard error sqrt(sum se²)/4, 95% interval ±1.96 se. No league cells.
* **Rule (pre-registered), on the pooled four ext cells, F = D0 against fb2-900, B = D0 minus B1:**

  | F | B | outcome |
  |---|---|---|
  | lower bound above -2.0 | lower bound above 0 | **NEW DATA**: the bp100 and `small_ball` samples caused the loss; identity is the lever, no population reshuffle runs |
  | upper bound under -2.0 | interval contains 0 | **MIX OR CONTINUATION**: the loss comes without new data; D-null runs (the same command at `--heur-batch 10000`, same read); D-null also down means continuation, D-null holding means the mix (next population sets C engine to ext near fb2's by cutting `--steps`) |
  | upper bound under -2.0 | lower bound above 0 | **BOTH**: report B as the part due to the new data |
  | any other combination | | **INCONCLUSIVE**: recorded with no lever decision (F straddles -2.0, B straddles 0 while F holds, or D0 worse than B1) |

* **Writes on gb10-d and rollback:** `~/d0-run` (rollback: delete the directory; it holds the code, `ckpt/d0`,
  `ckpt/d0smoke`, `logs/`, `x2r/`). Nothing in `~/poker-ai-lab-rl`, `~/poker-ai-lab-x2r` or `~/poker-ai-lab-league`.
  No push of `d0`.
* **Budget:** the training above, then about 40 minutes of reads on cores 0-17. AD1 starts after the reads.
* **Review record:** plan review 1 REVISE (match counts used where the update counts decisions, so `--heur-batch 5000`
  did not reproduce B1's old mix and the void check would void any honest run; no rate shown for 1,200 iterations and a
  short run would have been read; read side not literal; the catch-all rule gave a verdict to contradictory
  intervals). Fixed above with B1's logged decisions, a smoke rate, literal read commands and an INCONCLUSIVE row.
  Tier 2 allows one review; execution follows with the outcome verifier on the read.

### V5a. Is the distilled student itself the candidate? (spec, 2026-11-25; full process, the roadmap agent's call after 14.39)

* **Question:** does the 256-wide student distilled from T1, C1 and fb2-900 (AD0's W1) pass B1's registered rule and
  the deploy gate as it is, with no PPO?
* **Why (14.39, roadmap agent):** W1 at the deployed size holds T1's play on bp100 (+19.4 of +19.9), C1's on
  `small_ball` (+19.8 of +21.9) and fb2-900's on two Ashwing cells. B1 and D0 show that continued PPO from a good
  network costs about 3 points on the real-bot families, and the student already sits at both ceilings, so a PPO step
  has nothing to gain on the measured cells. AD0's rule 1 text "distil, then fine-tune with PPO" becomes "distil,
  judge, and fine-tune only if a named cell needs it"; there is no PPO in this slice.
* **Decision it feeds:** pass → eval card with E3, a fresh outcome verifier, then Wayne as v5 = the student plus S0
  (the all-in answer; no upload or swap without his yes). Fail on named cells → the repair round below; a second
  failure stops the slice and goes back to the roadmap agent.
  Revised after plan review 1: no repair round inside V5a (a fail goes back to the roadmap agent, which may specify
  one as its own slice); the fresh-seed check also covers the two Ashwing cells W1 was selected on.
* **Candidates (pinned, sha256 checked by the runner before any cell):** W1 at 30 epochs
  `~/ad0-run/students/W1.npz` (9bc31660a279f3c44069a8d92ea42011682c7b8a8f094e3f552d64b75f9cb4e9, the played one) and
  the A1 refit `~/ad0-run/students_a1/W1.npz` (3c37549815a9bb5bcc8bc78085a0d697321c9110d2fed4440f8053b94a9fd3fd).
  Raw counts, 256 wide. The files hold exactly fb2-900's policy keys and shapes (`pw0` 56x256 to `pb2` 6), so every
  B1 tool takes them through `--model` and `RL_CKPT` unchanged. Every arena cell (screen, confirmation, fresh-seed,
  both arms) runs `rl.eval_arena --model` from the tree of the fb2-900 baseline rows, holdem-x2r 8be6e38 at
  `~/d0-run/x2r` (C0's tree); the runner refuses any other code root. V5a's own scripts only drive that tree. W1s, W2, W2s are out (seeding needs live names and
  did not help in play; width did not help).
* **Screen, seed 94 (selection only):** per candidate B1's screen cells unchanged (bp100 1,000; `tight_sticky`,
  `sticky_overbettor`, `small_ball_b`, `never_fold_pre`, `loose_passive` 500 each) and the league screen on pairs 400
  to 499 (`tools/league_fresh.py` with `rl.bot_ckpt` `CkptBot`, `RL_CKPT` the candidate, 4,600 matches). Score: B1's
  literal (unpaired weighted win rate, bp100 0.7216, `tight_sticky` 0.1031, `sticky_overbettor` 0.0928,
  `small_ball_b` 0.0825). Filter: the lowest of the 23 league opponents at least 78.0%. Chosen: the higher score that
  passes the filter. Neither passes → V5a ends with that finding (the league clones have no Python logging path, so
  no repair round covers them).
* **Confirmation, seed 95, chosen candidate only:** B1's confirmation cells and counts (bp100 4,000; `tight_sticky`,
  `sticky_overbettor`, `small_ball_b`, `never_fold_pre`, `raise_station`, `small_ball`, `loose_passive` 2,000 each;
  `ext:ashwing`, `ext:ashwing_search`, `ext:ashwing_hive`, `ext:autodidact`, `ext:wolf` 1,000 each), paired on
  (seed, hero seat) against the fb2-900 arm on disk (`~/poker-ai-lab-x2r/logs/b1/confirm/fb2`; the `ext:wolf` fb2-900
  arm rerun with the candidate's placement, as B1's amendment 4). B1's arm (`.../confirm/cand`) is reported beside.
  The first 2,000 bp100 matches repeat AD0's play rows for the 30-epoch W1; if it is chosen, those must be
  identical row for row. A mismatch is a harness fault: the runner stops before any rule read, and it is recorded.
* **Rule (pre-registered), B1's verbatim plus one check:** headline = weighted sum of paired gains over fb2-900 on
  seed 95 (bp100 0.70, `tight_sticky` 0.10, `sticky_overbettor` 0.09, `small_ball_b` 0.08, `ext:autodidact` 0.03),
  interval from the cells' paired standard errors. **Pass** when all of: (1) headline 95% lower bound above zero;
  (2) no cell, weighted or guard, with a paired gain under -2.0 and its upper bound under zero; (3) the fresh-seed
  check below holds; (4) E1 holds. The fresh-seed check covers the selection of W1 among four students on four
  seed-95 cells (14.39): bp100, `small_ball`, `ext:ashwing`, `ext:ashwing_hive`.
* **Fresh-seed check, seed 108:** chosen candidate and a new fb2-900 arm on the same tree and command, bp100 2,000
  (k < 1,000), `small_ball` 2,000, `ext:ashwing` 1,000 and `ext:ashwing_hive` 1,000, paired on (seed, hero seat).
  Holds when all three: the bp100 gain has its 95% lower bound above +5.4; the `small_ball` gain has its 95% lower
  bound above +6.5 (B1's points); the pooled gain of the two Ashwing cells (mean, se sqrt(sum se^2)/2) has its 95%
  lower bound above -2.0 (AD0's line).
* **Gate E1 (B1's command, pairs never used in selection):** a holdem-rl commit adds `rl/models/v5a.npz` (byte-equal
  to the chosen file) and `rl/bot_v5a.py` (`class V5aBot(RLBot)`), the B1 way; from the PC league checkout
  `tools/league_add.sh <holdem-rl> <that commit> rl-v5a rl.bot_v5a V5aBot` (pairs 0 to 199, the leaderboard row);
  on gb10-d `tools/league_fresh.py --name rl-v5a --root candidates/rl-v5a --module rl.bot_v5a --class V5aBot --p0 200
  --p1 400 --h2h chipzen-102b05e --workers 8 --out out/verify-rl-v5a`. Holds when all 23 opponents are at 80% or
  more over pairs 200 to 399 (Wilson lower bounds reported) and the heuristic head to head has its Wilson 95% lower
  bound above 50%; per-opponent paired difference against fb2-900's verify rows reported.
* **Reported and flagged, not gating:**
  1. bp100's confirmation gain beside the Blueprint clone's paired E1 difference (14.37's literal: opposite signs
     with both intervals excluding zero is flagged to Wayne, not passed on the headline).
  2. The eval card (`tools/eval_card.sh v5a <chosen> <INIT>`, INIT the checkpoint fb2-900's card used): E2 real-bot
     families, E3 exploit probe, E4 against the king, and the chipflow file against bp100 read with
     `tools/p0_read.py` beside T1's `logs/t1/flow_br.jsonl` and fb2-900's card (the shove table; the student carries
     T1's shoving style and Wayne sees what a counter-strategy gets from it).
  3. Decision time: same architecture and code path as fb2-900 (identical keys and shapes), so equal by
     construction; stated, not measured.
  4. The fit's batch mix (bp100 30%, `small_ball` 15%, the rest 55%) beside the judge weights: it acts as the
     student's prior over opponents before the counts speak.
  5. The cells no teacher covered (`tight_sticky`, `sticky_overbettor`, `never_fold_pre`, `raise_station`,
     `loose_passive`, `small_ball_b`, `ext:autodidact`, `ext:ashwing_search`, `ext:wolf`, the clones, the heuristic)
     are expected to decide it: 14.33 put T1's play at -12 to -18 on `sticky_overbettor`, `small_ball` and
     `never_fold_pre`, and 14.37 has `never_fold_pre` and `sticky_overbettor` named late (12% and 27% of hands).
* **Seeds (registered as `N V5A read` in `~/poker-ai-lab-rl/tools/seed_registry.txt` and the branch):** 94, 95, 108;
  E3 uses the card's fixed seeds 1 and 3.
* **Tests (each failing on its plant; plant runner committed with them):** candidate sha256 refusal; screen weights,
  the 78.0% filter and the choice rule; the rule's four conditions (plants: guard dropped, headline bound at zero,
  fresh-seed bound 5.4 changed, the Ashwing cells dropped from the fresh-seed check, E1 dropped); the confirmation
  and fresh-seed cells and counts literal; the bp100 replay check stops the runner on a one-row mismatch; gate pairs
  200 to 399 never overlapping the screen's 400 to 499; seeds literal.
* **Owners and base:** holdem-x2r branch `v5a` from `ad0-x2r` 541bf81 (judge runner `tools/v5a_judge.sh` and reader;
  B1's runner and reader reused where they fit, rows under `logs/v5a/`); holdem-rl branch `v5a` from `ad0` 5b09abe
  (registry lines; `rl/models/v5a.npz` and `rl/bot_v5a.py` only after the confirmation passes); holdem-league for
  the leaderboard row. Non-goals: no training, no change to the deployed bot, no upload.
* **Writes, each with its rollback (B1's list adapted):**
  1. Commits on holdem-rl, holdem-x2r, holdem-league (local branches `v5a`): revert them.
  2. gb10-d `~/poker-ai-lab-x2r/logs/v5a/`; `~/poker-ai-lab-rl/logs/eval_card/v5a*` and `ckpt/probe_card_v5a/`;
     registry lines `94 V5A read`, `95 V5A read`, `108 V5A read`: delete.
  3. gb10-d `~/poker-ai-lab-league/`: `candidates/rl-v5a/`, `out/v5a/`, `out/verify-rl-v5a/`, `logs/add-rl-v5a.*`:
     delete; the `rl-v5a` entry in `candidates.json`: remove; rows with `cand:rl-v5a` in `out/league/results.jsonl`
     (the runner copies the file to `results.jsonl.pre-v5a` before `league_add.sh` runs, and refuses to run the add
     without that copy): restore the copy; `out/leaderboard.md`: rebuild with `PYTHONPATH=. .venv/bin/python -m
     league.report --out out/league --md out/leaderboard.md`.
  4. PC `poker-ai-lab-league/reports/league/leaderboard.md` (written by `league_add.sh`): copy the rebuilt
     `out/leaderboard.md` back.
  5. `~/bpq.lock` (empty lock file): leave.
* **Review record:** plan review 1 REVISE (the Ashwing selection cells were not in the fresh-seed check; "+6.5"
  read as a point or a bound; no action on a replay mismatch; the repair round could not run and contradicted the
  non-goal). Fixed above; the repair round was removed. Plan review 2 REVISE (the league writes of `league_add.sh`
  and the branch commits had no rollback). The review cap of two is reached; the one blocker was mechanical with a
  stated minimum revision, applied first-hand at 2026-11-25 22:43 UTC as the list above (B1's items 1, 4, 5), and recorded here.
* **Budget (measured rates):** screen about 25 minutes for both candidates (arena cells minutes, league 4 minutes
  each); confirmation about 90 minutes (`ext:autodidact` 1,000 about 57 minutes at 6 workers, B1's 3,392 s);
  fresh-seed check about 15 minutes (two Ashwing cells of about 3 minutes each, both arms); E1 about 10; eval card about 60 (E3 400 iterations). About 3.2 box-hours on
  cores 0-17; stop and record at two times any phase.
* **Limits:** the judge covers 52% of entrant seats by weight (B1's map); the clones are copies of past behaviour;
  a pass is a candidate for Wayne, not a deployment.
* **Built (2026-11-25, local only):** holdem-x2r `v5a` 186d423, 8ac3d47, 05ed829, de7c4f7 (on 541bf81):
  `tools/v5a_judge.sh` (check, screen, league-screen, choose, confirm, fresh, gate-prep, gate-commands),
  `tools/v5a_gate_add.sh` (runs the league checkout's `league_add.sh` for rl-v5a only when gb10-d holds
  `results.jsonl.pre-v5a`), `tools/v5a_read.py`, tests and plants; holdem-rl `v5a-rl` 9bebfb5 (registry 94, 95, 108
  V5A). Candidates named `w1` and `w1_a1`. Outcome verifier 1 REFUTED (nothing stopped `league_add.sh` before the
  rollback copy; fixed in 05ed829); verifier 2 REFUTED (the gate tests' fake ssh was not executable on Linux, so both
  failed there and the gate plant was caught by a broken test; a set `V5A_LOGS` reopened the tree and pin overrides).
  The cap of two is reached; fixed first-hand in de7c4f7 at 2026-11-25 23:17 UTC: overrides honoured only under `V5A_TEST=1`, the
  fake ssh made executable, three plants added. Checked on gb10-d from a clean archive: 33 of 33 tests pass, the
  unmodified tree passes 119 tests under the plant runner and 43 of 43 V5a plants are caught; the verifier's bypass
  (`V5A_LOGS`, `V5A_TREE`, a fake fb2 pin) exits 8; the real `check` passes the three pins and the tree; the gate
  wrapper exits 7 while the copy is missing. Verifiers' notes kept: a rows file of the right length is reused
  without checking its model (the chosen file is fixed per run); `read` does not check that the gate summary names
  rl-v5a (checked by hand at the gate).
* **Reading a fail (roadmap agent after 14.40):** the -2.0 guard against fb2-900 stays; fb2-900 is the bot a
  candidate replaces. A loss of 2 to 3 points on the Ashwing cells equals the spread between fb2's own checkpoints
  (14.40), so such a fail reads "did not keep the peak", not "the method breaks these families". It still fails.
* **Reported only, after V5a's cells (fit-seed spread):** W1 refit at 30 epochs with fit seeds 2 and 3 (holdem-rl
  ad0 9b2a1c7 `--seed`), same data, each played on seed 95: bp100 2,000 (k < 1,000), `ext:ashwing` and
  `ext:ashwing_hive` 1,000 each, paired against the fb2-900 arms on disk, from `~/d0-run/x2r`; the three fits' gains
  side by side. It sets how V5b chooses among students and how much of a student's ext number is fit noise; it does
  not touch V5a's chosen student or rule. Registered as `95 V5A read` (bp100 through the queue).

### V5b. Specialists plus coverage: one student that keeps the gains and plays fb2-900 elsewhere (spec, 2026-11-26, revision 2; full process, the roadmap agent's decision after 14.42)

* **Question:** does a student distilled from the specialists (T1 on bp100, C1 on `small_ball`, `br_chipzen` on
  `chipzen`) plus fb2-900's labels on the 23 league opponents and on 60 generated styles pass B1's whole judge, and
  does its default (fb2-900's play) hold on the eleven cells it is never fitted on?
* **Why:** V5a failed the league filter (14.42) on opponents AD0's data never covered (base:lag 64.5 and 74.5). The
  arena has 289 names, so play against unfitted opponents decides the long run: the fix teaches a default and keeps
  held-out cells to measure it. Missing labels are fixed with rows, not PPO (C0, D0).
* **Teachers (literal; sha256 pinned in full in the runner):** T1 `ckpt/br_bp100/latest.npz` (5eb525fb…), C1
  `~/poker-ai-lab-x2r/ckpt/br_small_ball/latest.npz` (97f051f3…), `br_chipzen` `ckpt/br_chipzen/latest.npz`
  (666a436345eb…, 14.41), fb2-900 `rl/models/fb2_it000900.npz` (f7a29a39…). T-a's teachers are not used whatever T-a
  reads: they are trained on and read against D4 cells, so using them would put held-out cells in the data.
* **Step 0, the `chipzen` opponent is seeded first (eval path only):** holdem-x2r branch `v5b-root` from 8be6e38 adds
  `set_seed` to `rl/eval_arena.py` `make_chipzen()`, rebuilding `HoldemBot(seed=s)` from the arena's per-match value
  (`opp.set_seed(pair_seed * 13 + hero_seat)`, `holdem/arena.py`). Tests first: two 50-match `chipzen` runs on one
  seed give identical rows; with the seeding removed they do not; `small_ball`, `ext:ashwing` and `tight_sticky` rows
  (50 matches each) are byte-identical to `~/d0-run/x2r`. The new root is `~/d0-run/x2r-v5b` (archive of that
  commit). Every judge cell runs from `~/d0-run/x2r` except the `chipzen` cell, which runs from `~/d0-run/x2r-v5b`
  for both arms (fb2-900 and the chosen student) on seed 95, 1,000 matches; `chipzen` is reported only, not a guard.
* **Seeding (one table for data and play):** every opponent of V5b's data (league, generated, `chipzen`, the ext
  names) is unseeded; the logged observation is the raw one (no `ad0_prior.npz` row), and the students play
  unseeded, as V5a's W1 did. A test resolves every data opponent to no profile row at data and at play (plant: a
  league opponent given a row at play).
* **Data (AD0's rows stay, pinned by sha256; AD0's fb2-900 `chipzen` rows are dropped; new rows logged by holdem-rl
  `tools/ad0_log.py` the AD0 way: hero's raw observation, label softmax(masked logits) before `AllInAnswer` and
  search, the legal mask, 10% held out by pair (both seats together) through AD0's `heldout(tag, pair_id)`, as
  the kept rows are; data seed 111):**
  * D1 league coverage: fb2-900 against all 23 league opponents, 300 matches each (6,900), labels fb2-900. The seven
    `base:` names map to holdem-rl BASELINES (`station`, `maniac`, `nit`, `random`, `reference`, `lag`,
    `station_raiser`). `arch:0` to `arch:5` and the ten `bot:` names (Blueprint, Kimiko, AutodidactInnovations,
    SolvencyCheck, DeepStack, mr_hide, MercuryRetrograde, qwentom-leap, InfernalMonarch, PoetAndCoder) are the
    league's `CloneBot`: an adapter `league:<spec>` imports it from `~/poker-ai-lab-league` (not a git checkout on
    gb10-d) and pins by sha256 every module it loads from there (`league/clone.py`, `league/context.py`,
    `league/strength.py`, `league/data/clones.npz`, and the `nlhe/` and `holdem/opponents.py` files it imports); a
    one-byte change in any of them stops the logger. Per match the adapter builds a new `CloneBot(spec, seed=s)` in
    `set_seed(s)`. Parity test, all 23 opponents: on 200 recorded states each, the adapter (and holdem-rl's
    BASELINES class for `base:`) returns the same action and size as the league's own build (`league/run.py`
    `build`, `make_baseline`) at the same seed value (plant: the adapter ignores the seed).
  * D2 default coverage: 60 generated StyleBots, 100 matches each (6,000), labels fb2-900. One tree measures every
    vector (exclusion and generated): holdem-x2r branch `v5b` (it holds `small_ball_b`, `loose_passive` and
    `style_bots_check.distance`), which owns the `make_opp` changes in `tools/style_map.py`: a `gen:<k>` name built
    from entry k of `styles.json`, and a `bp100` branch. A generated style is a `StyleBot` subclass with the drawn
    attributes, built per match as `make_baseline` builds a style, `StyleBot(seed)` from the per-match value
    (`seed * 13 + seat` in `style_map.sim_one`, `pair_seed * 13 + hero_seat` through `set_seed` in the arena), and it
    has `set_seed(s)` resetting its RNG so the logging arena reseeds it every match. holdem-rl `v5b-rl` carries the
    same `gen:<k>` class for logging; a parity test builds one `styles.json` entry in both trees and gets identical
    actions on 200 recorded states, and two 20-match data runs of a generated style on one seed give identical rows
    (plant: the per-match seed dropped). Draws from
    `random.Random(110)`, uniform on: `open_p` [0.05, 0.95], `play_p` [0.0, `open_p`], `face_p` [0.0, 0.95],
    `pre_size` [2.0, 6.0], each `bet[i]` [0.0, 1.0] then sorted ascending, `street_bet` each [0.5, 1.5],
    `bet_size` [0.25, 1.5], each `rr[i]` [0.0, 0.6] sorted ascending, each `cont[i]` [0.0, 1.0] sorted ascending
    with `cont[4]` = 1.0. Vector of a style = `tools/style_map.py sim <name> rl/models/fb2_it000900.npz 300 3 4`
    (hero fb2-900, 300 matches, style seed 3, 4 workers), as B1 measured its cells. Exclusion vectors measured once
    by the same command: `small_ball`, bp100 (a `bp100` branch in `make_opp` calling `rl.eval_arena.make_bp100`, run
    through the queue, `BPQ_SLICE=V5B BPQ_SEED=3`) and every D4 cell. A drawn style is redrawn while its vector is
    within 0.25 (`style_bots_check.distance`) of any exclusion vector; the 60 accepted styles and their vectors are
    written to `styles.json` (sha256 in the record).
  * D3 `br_chipzen` against `chipzen`, 1,000 matches, labels `br_chipzen`. `chipzen` is seeded at data time too:
    holdem-rl `v5b-rl` adds the same per-match `set_seed` to `tools/ad0_log.py`'s `make_chipzen`; two 20-match D3
    runs on one seed give identical rows (plant: the seeding removed).
  * D4 held out, never a data opponent of any teacher: `tight_sticky`, `sticky_overbettor`, `small_ball_b`,
    `never_fold_pre`, `raise_station`, `loose_passive`, `ext:ashwing`, `ext:ashwing_hive`, `ext:ashwing_search`,
    `ext:autodidact`, `ext:wolf`. A test fails if any D4 name appears in the data's opponent field.
  * D5 time: every new cell type (league clone, `base:`, generated style, `br_chipzen`) is estimated from a 20-match
    smoke on the logging path itself; the runner stops at twice the estimate.
* **Fit (holdem-rl `tools/ad0_fit.py` at ad0 9b2a1c7, extended for group weights):** F1 converged fits: cap 300
  epochs, patience 10, best epoch on the held-out loss kept, random init, fit seed 1, raw counts; a fit that reaches
  the cap keeps its best epoch and is recorded as capped. F2 batch weights by group, sum 100%: bp100 (T1) 20%,
  `small_ball` (C1) 10%, `chipzen` (`br_chipzen`) 10%, the four AD0 ext names (`ext:ashwing_v2`,
  `ext:ashwing_value`, `ext:ashwing_adaptive`, `ext:autodidact_fast`; fb2-900) 10%, league (D1) 30%, generated
  (D2) 20%; a test checks the realised shares within 1%. F3 two students, hidden 256 and 512 (56 inputs, two hidden
  layers, 6 actions).
* **Seeds (registered as `N V5B read` in `~/poker-ai-lab-rl/tools/seed_registry.txt` and the branch):** 3 (style
  vectors, bp100 through the queue), 111 (data), 94, 95, 108 (judge, as V5a), 110 (style draws; not a match seed,
  registered to keep it unused elsewhere).
* **Judge:** J1 screen exactly B1's (seed 94, its six cells and counts, league pairs 400-499, 78.0% filter), both
  students. Choice: among students that pass the filter, the 256 student unless the 512 student's screen score
  exceeds it by more than 0.005 in `b1_read.screen_score`'s unit (a fraction; 0.5 points); if only one passes, that
  one. Test: passing scores 0.006 apart choose the 512 student, 0.004 apart the 256 student (plant: margin moved). J2 confirmation, fresh-seed check and gate exactly
  V5a's text (seed 95 on every B1 cell against the arms on disk; seed 108 for bp100, `small_ball`, `ext:ashwing` and
  `ext:ashwing_hive` with V5a's bounds; E1 on pairs 200-399; heuristic head to head). League opponents are now
  fitted, so E1 is a fit check and D4 carries the generalisation claim. J3 at confirmation (seed 95; every D4 cell
  is a B1 confirmation cell with fb2-900's arm on disk): a table of the chosen student's gain on each D4 cell, and a
  flag when any is under -5.0. J4 reported: `chipzen` (step 0), bp100 beside the Blueprint clone, the shove table,
  E3 probes, decision time, the fit-seed spread.
* **Rule (first match, in order; each branch stops the slice and writes its verdict):**
  1. FILTER FAIL: no student passes the 78.0% filter. Per-opponent table to the roadmap agent; no second coverage
     round.
  2. DEFAULT FAIL: B1's guard fails on a D4 cell at confirmation (gain under -2.0 with upper bound under zero). The
     default does not generalise from 60 styles; next is a design question for the roadmap agent.
  3. RULE FAIL: any other part of B1's rule on seed 95 fails (headline lower bound not above zero, or a non-D4 cell's
     guard).
  4. FRESH FAIL: the seed-108 check fails (V5a's bounds).
  5. GATE FAIL: E1 or the heuristic head to head fails.
  6. PASS: fresh outcome verifier, then Wayne.
  Reported with any verdict: if the chosen student's bp100 gain on seed 95 has its lower bound under +10.0 or
  `small_ball`'s under +11.0, it is recorded as the price of coverage (it does not change the verdict). A reader
  test on synthetic results gives exactly one verdict for every combination of filter, headline, guard (D4 and
  non-D4), fresh-seed, E1 and head to head; plants dropping the D4 guard, the fresh-seed check or E1 each turn a
  pass into a fail.
* **Tests (each failing on its plant; plant runner committed with them):** step 0's three tests; the seeding table
  (plant above); the adapter's parity and pins (plants: seed ignored, a pinned file changed); D2's ranges and the
  0.25 exclusion literal, a planted style placed within 0.25 of `loose_passive` is redrawn (plant: the D4 exclusion
  dropped); no D4 name in the data (plant: `tight_sticky` added to D2's list); F2 shares within 1%; hold-out by
  pair (every pair has both seats on one side; plants: held out by match id, by row); the choice rule; the rule table above; every seed, registry line, count, epoch and
  patience value, the four ext names and the teacher sha256 values literal.
* **Owners and base:** holdem-rl branch `v5b-rl` from ad0 9b2a1c7 (adapter, generator, logging and fit changes,
  registry lines; `rl/models/v5b.npz` and `rl/bot_v5b.py` only after PASS); holdem-x2r branch `v5b-root` from
  8be6e38 (step 0) and branch `v5b` from v5a fee9b27 (judge runner and reader, reusing V5a's); holdem-league for the
  leaderboard row (V5a's gate wrapper adapted). Non-goals: no PPO, no change to the deployed bot, no upload.
* **Writes, each with its rollback (V5a's list adapted):**
  1. Commits on holdem-rl, holdem-x2r, holdem-league (local branches above): revert them.
  2. gb10-d `~/v5b-run/` (data, `styles.json`, students, logs), `~/d0-run/x2r-v5b/`, `~/poker-ai-lab-x2r/logs/v5b/`,
     `~/poker-ai-lab-rl/logs/eval_card/v5b*` and `ckpt/probe_card_v5b/`; registry lines `3`, `94`, `95`, `108`,
     `110`, `111 V5B read` (the runner copies the registry to `~/v5b-run/seed_registry.pre-v5b` first): delete, or
     restore the copy.
  3. gb10-d `~/poker-ai-lab-league/`: `candidates/rl-v5b/`, `out/v5b/`, `out/verify-rl-v5b/`, `logs/add-rl-v5b.*`:
     delete; the `rl-v5b` entry in `candidates.json`: remove; rows with `cand:rl-v5b` in `out/league/results.jsonl`
     (copied to `results.jsonl.pre-v5b` before `league_add.sh`, which the wrapper refuses to run without the copy):
     restore the copy; `out/leaderboard.md`: rebuild with `PYTHONPATH=. .venv/bin/python -m league.report --out
     out/league --md out/leaderboard.md`.
  4. PC `poker-ai-lab-league/reports/league/leaderboard.md`: copy the rebuilt `out/leaderboard.md` back.
  5. `~/bpq.lock`: leave.
* **Budget (estimates; each phase stops and is recorded at twice its number):** exclusion and style vectors about 60
  minutes (13 cells and up to about 120 draws of 300 matches; `ext:autodidact` dominates); data about 160 minutes
  (13,900 new matches at AD0's measured 9,000 in 97 minutes, replaced by D5's smoke); fit about 20 minutes for both
  students; screen about 10; confirmation about 90; fresh-seed check about 15; E1 about 10; eval card about 60.
  About 7 box-hours on cores 0-17.
* **Placement:** D1 and D2 logging start on cores 0-17 after the fit-seed spread; they do not wait for step 0. D3
  waits for step 0.
* **Not done:** PPO repair on the league (C0, D0 priced it; the fault is missing labels); judge style cells as data
  (it would hide the 289-name question); T-a teachers (above).
* **Amendment 1 (roadmap agent after 14.43, 2026-11-26 00:45 UTC, before any V5b data, fit or read):** a single fit is a draw
  (14.43: the fit seed alone moves pooled Ashwing by 4 points), so each candidate is the average of three fits.
  1. Fits: for each width (256, 512) fit seeds 1, 2 and 3, everything else as F1 to F3 (six fits).
  2. Students E256 and E512: at each decision the policy is the mean of the three members' masked action
     probabilities (softmax of each member's masked logits at temperature 1.0), and the action is drawn from that
     mean by the bot's existing rule, unchanged: `rl/runtime.py` `Policy.act`, one `rng.choice` draw from the
     probabilities at temperature 1.0 (argmax only at temperature 0).
  3. Artifact: one file per ensemble holding the three members' policy arrays, with each member's sha256 and the
     file's sha256 pinned in the runner. Test first: on 200 fixed states the ensemble's probabilities equal the mean
     of the three members computed separately within 1e-9 (plant: averaging logits instead of probabilities).
  4. Screen: E256 and E512 only (the six members are not screened); choice unchanged (E256 unless E512 exceeds it
     by more than 0.005).
  5. Confirmation, fresh-seed check and gate: the chosen ensemble only, text unchanged.
  6. Reported after the rule is read, never used to choose: the chosen ensemble's three members on seed 95, bp100
     2,000 and the pooled Ashwing cells (`ext:ashwing`, `ext:ashwing_hive` 1,000 each), beside the ensemble; and the
     ensemble's decision time per move. Dropped first if box time is tight.
  7. Budget: fit about 40 minutes for six fits (was 20); item 6 about 30 minutes.
  8. A tier-1 read before V5b's fit, reported only and changing nothing in V5b: the three AD0 W1 fits of 14.43
     (fit seeds 1, 2, 3) averaged as in item 2, played on seed 95 (bp100 2,000, `ext:ashwing` and
     `ext:ashwing_hive` 1,000 each) against the arms on disk, registered under `95 V5A read`. If it lands clearly
     under the members' mean (about +18 on bp100, about -0.8 pooled Ashwing) on either, it returns to the roadmap
     agent before V5b's fit.
  9. Where the ensemble loads: `rl/runtime.py` `Policy` on `v5b-root` learns the ensemble file; a single-network
     file takes the unchanged path, proven by step 0's neutrality test (`small_ball`, `ext:ashwing`, `tight_sticky`,
     50 matches each, byte-identical to `~/d0-run/x2r`), so fb2-900's arms on disk stay valid. Every candidate cell
     (screen, confirmation, fresh seed, item 6, item 8) runs from `~/d0-run/x2r-v5b`; the league screen and E1 use a
     candidate root `~/poker-ai-lab-league/candidates/v5b-src` (an archive of `v5b-root`, written by the runner;
     rollback: delete). `rl/bot_v5b.py` on holdem-rl carries the same loader, written only after PASS.
* **Review record:** plan review 1 REVISE (T-a teachers against held-out cells; StyleBot ranges, measurement and
  exclusion left to the builder; rule branches and J3's screen baseline missing; seeds, seeding table and fitter
  not named; the adapter's pins and per-match seeding; no tests, owners, writes or budget). Revised above
  (revision 2). Plan review 2 REVISE (the choice margin's unit; one tree for the style vectors and a per-match seed
  and parity for generated styles; D3's `chipzen` seeding at data time; hold-out by pair as AD0's kept rows). The
  review cap of two is reached; each blocker was mechanical with a stated minimum revision, applied first-hand at
  2026-11-26 00:36 UTC as above and recorded here.

### G0. The gated mixture: fb2-900 until the counts say who this is, then that opponent's teacher (spec, 2026-11-26; tier 2, a measurement; the roadmap agent's decision after 14.46)

* **Question:** with an explicit posterior over four opponent classes and fb2-900 as the default, does play keep the
  specialists' gains without V5b's misfire (`sticky_overbettor` -4.2 [-6.1, -2.4], 14.46)?
* **Why:** a student fitted by cross-entropy on pooled rows plays, before it knows the opponent, the row-weighted
  average of its teachers; an average of best responses is not an answer to an unknown opponent, and coverage rows
  that pull it back toward fb2-900 cost the specialists (V5b: `small_ball` +7.3 against AD0's +19.8). fb2-900 is
  PPO's answer to an unknown opponent, so the rule is stated explicitly: default fb2-900, move to a teacher only when
  the posterior is high. G0 has no fit loss beyond a small classifier, so it gives this design's ceiling and
  separates "wrong rule" from "the student could not learn it", which V5b could not.
* **Nature (state it on any card Wayne later sees):** G0 switches between fixed networks on a classifier's posterior.
  It is a measurement, not a bot candidate: no E1 gate, no head to head, nothing reaches the deployed bot. If it
  passes, the next slice distils G0 into one network from G0's own play (spec written from G0's numbers).
* **Classes and teachers (literal; sha256 pinned in full in the runner, as V5b):** bp100 -> T1
  `ckpt/br_bp100/latest.npz` (5eb525fb...), `small_ball` -> C1 `~/poker-ai-lab-x2r/ckpt/br_small_ball/latest.npz`
  (97f051f3...), `chipzen` -> `br_chipzen` `ckpt/br_chipzen/latest.npz` (666a436345eb...), other -> fb2-900
  `rl/models/fb2_it000900.npz` (f7a29a39...). T-a's teachers (`br_ashwing`, `br_autofast`) are not used; their cells
  stay held out.
* **Classifier (holdem-rl branch `g0-rl` from v5b-rl 377ec9f, `tools/g0_clf.py`):**
  1. Input: the nine observation features `[46, 47, 48, 49, 50, 51, 54, 55, 52]` of `rl/features.py` `build` (the
     eight Tracker rates and the hand count `f52`), from the unseeded Tracker; nothing else.
  2. Model: inputs standardised by the mean and standard deviation of the fit rows (train side only; a standard
     deviation under 1e-6 is set to 1.0), one hidden layer of 32 tanh units, softmax over the four classes in the
     order bp100, `small_ball`, `chipzen`, other; computed in float64. Chosen over a linear model because the posterior must sharpen with the hand count, an interaction a
     linear model cannot express. Fit with Adam (learning rate 1e-3, batch 4,096), cross-entropy, fit seed 1, at
     most 200 epochs, patience 10 on the held-out loss, best epoch kept; class shares as they fall in the rows (no
     reweighting: the large "other" share makes the classifier conservative, which is the side a misfire costs).
  3. Rows: every row of V5b's `~/v5b-run/data.npz` (sha256 18f88b37..., pinned in full; its opponent field gives
     the class: bp100, `small_ball`, `chipzen`; every league, generated and AD0 ext name is other) plus new rows
     with fb2-900 as actor against bp100, `small_ball` and `chipzen`, 1,000 matches each, through holdem-rl
     `tools/ad0_log.py`'s logging path (unseeded opponents; `chipzen` reseeded per match as V5b's D3; bp100 through
     the queue, `BPQ_SLICE=G0`), data seed 112. Reason for the new rows: counts depend on the hero's play, so each
     specialist class must be seen under both its teacher and the default as actor, or the classifier can learn "the
     hero is T1" instead of "the opponent is bp100". `chipzen` is added to the roadmap agent's two cells by the same
     reason (V5b dropped AD0's fb2-900 `chipzen` rows).
  4. Hold-out by pair, as V5b: V5b's `held` flag for its rows, `heldout(tag, pair_id)` for the new ones.
  5. Reported before play: held-out accuracy by hand-index bucket (1 to 10, 11 to 20, 21 to 40, over 40) and
     calibration (10 equal-width confidence bins, expected calibration error) per class.
  6. A test fails if any D4 name is in the classifier's rows (plant: `tight_sticky` rows added as other).
* **Policy (holdem-x2r branch `g0-root` from v5b-root a4ec310, `rl/runtime.py` `Policy` learns a G0 file, as it learned
  the ensemble file):** at each decision, p = the classifier's posterior on the current observation. For each
  specialist class c, w_c = clip((p_c - t) / 0.15, 0, 1); if the w_c sum above 1 they are scaled to sum to 1. The
  policy is sum_c w_c * teacher_c's masked probabilities + (1 - sum_c w_c) * fb2-900's masked probabilities (each
  softmax of that network's masked logits at temperature 1.0), and the action is one draw from it by the bot's
  existing rule (`Policy.act`, one `rng.choice`), with the all-in answer and everything else in `RLBot` unchanged.
  Two arms, fixed now: G80 (t = 0.80) and G50 (t = 0.50), each one npz with every component's sha256 and the
  file's pinned in the runner. File layout (literal): `g0_t` (t), `g0_ramp` (0.15), `g0_feat` (the nine indices),
  `g0_classes` (the four names), `clf_mean` and `clf_std` (9 each), `clf_w1` (9 x 32), `clf_b1` (32), `clf_w2`
  (32 x 4), `clf_b2` (4), all float64; then each teacher's arrays copied verbatim under `m0_` (T1), `m1_` (C1),
  `m2_` (`br_chipzen`), `m3_` (fb2-900) prefixes, including a `keep` array where the teacher has one, applied as
  the single-network path applies it (the ensemble loader's refusal of `keep` does not apply to G0 files).
  Tests first: (a) on 200 fixed states the G0 probabilities equal the formula computed from the five networks
  separately within 1e-9 (plants: weights not renormalised, ramp 0.10, threshold applied to the wrong class), on
  the G80 and G50 files and on a test-fixture G0 file with t = 0.30 (never a play arm; at t of 0.5 or more two
  specialist weights cannot both be positive, so renormalisation is unreachable there); the 200 states must include
  at least one where the fixture's unscaled weights sum above 1, so each plant changes a probability; (a2)
  cross-tree parity: on the first 200 held-out rows of `~/v5b-run/data.npz`, `tools/g0_clf.py`'s posterior (the one
  the calibration report and misfire table use) and the `g0-root` runtime's posterior from the same G0 file agree
  within 1e-9 (plants: tanh replaced by ReLU in the runtime, the input scaling dropped, float32 in the runtime); a
  G0 file built with a synthetic teacher that carries a `keep` array gives that teacher's single-network
  probabilities when its weight is forced to 1 (plant: `keep` dropped); (b)
  neutrality: a G0 file whose classifier is forced to "other" plays 50 matches each of `small_ball`,
  `ext:ashwing` and `tight_sticky` byte-identical to fb2-900's rows from `~/d0-run/x2r` on the same seed (plant: a
  constant 1e-6 added to a specialist weight); and 50 matches of that file against `chipzen` from `~/d0-run/x2r-g0`
  byte-identical to fb2-900's from `~/d0-run/x2r-v5b` on the same seed (plant: `chipzen` seeding removed in
  `g0-root`); (c) the literals 0.80, 0.50, 0.15, the feature list and the file layout.
* **Misfire table (reported before play, never used to tune or choose):** on 14.37's logs
  (`~/poker-ai-lab-rl/logs/ad1r/play/*.jsonl`, fb2-900 against 14 opponents, 200 matches each, seed 102, raw
  Tracker counts after every finished hand), the features of hand k come from the counts after hand k-1 (zero
  counts at hand 1) through `build`'s formulas; for each arm and opponent, the share of hands on which the arm leaves
  the default (sum_c w_c > 0), and the share on which it moves to each specialist. For the D4 cells this is the
  direct measure of misfire; for bp100, `small_ball` and `chipzen` it is identification by hand bucket.
* **Seeds (registered as `N G0 read`; the runner copies the registry to `~/g0-run/seed_registry.pre-g0` first):** 94
  (screen), 95 (read), 112 (classifier rows), 113 (fresh `sticky_overbettor`).
* **Judge (holdem-x2r branch `g0` from v5b bedc22e; V5b's judge and reader adapted; every G0 cell runs from
  `~/d0-run/x2r-g0`, an archive of `g0-root`; the league screen from `~/poker-ai-lab-league/candidates/g0-src`):**
  1. Screen: B1's screen (seed 94, its six cells and counts, league pairs 400 to 499, 78.0% filter), both arms.
     Chosen: the higher `b1_read.screen_score` among arms that pass the filter; G80 when the difference is 0.005 or
     less (a fraction, as V5b); if only one passes, that one. Test: passing scores 0.006 apart in G50's favour choose
     G50, 0.004 apart G80 (plant: margin moved).
  2. Read, chosen arm only, seed 95: every B1 confirmation cell and all eleven D4 cells at V5b's counts, paired
     against fb2-900's arms on disk (V5b's `confirm/fb2_wolf` for `ext:wolf`); `chipzen` 2,000 from `~/d0-run/x2r-g0`.
  2b. The `chipzen` line, measured before the read and independent of G0: `br_chipzen` and a new fb2-900 arm, each
     2,000 matches against the seeded `chipzen` from `~/d0-run/x2r-v5b` on seed 95 (V5b's 1,000-match rows are
     not reused). The line is half of `br_chipzen`'s paired point gain there (the +11.8 of 14.41 was against the
     unseeded opponent and is not used). G0's `chipzen` cell pairs against this new fb2-900 arm; test (b) makes the
     two roots comparable on `chipzen`.
  3. Fresh: `sticky_overbettor` 2,000 on seed 113, the chosen arm and a new fb2-900 arm from `~/d0-run/x2r`.
  4. Reported only: decision time per move; the departure share by hand bucket against each cell on 200 logged
     matches of the chosen arm (seed 95, the first 200); every D4 cell's gain (J3 flag under -5.0 kept).
* **Rule (first match, in order; each branch stops the slice and writes its verdict):**
  1. FILTER FAIL: no arm passes the 78.0% filter.
  2. GUARD FAIL: a D4 cell fails B1's guard on seed 95 (gain under -2.0 with upper bound under zero), or the fresh
     `sticky_overbettor` gain has its lower bound at or under -2.0. Read the misfire table for that cell: if the arm
     leaves the default on more than 10% of its hands, the classifier is the fault (its inputs or negatives are the
     next step); if 10% or less, the loss comes from play after a correct identification of a near neighbour and
     returns to the roadmap agent.
  3. RULE FAIL: the rest of B1's rule on seed 95 fails (headline lower bound not above zero, or a non-D4 guard).
  4. GAINS SHORT: guards hold but a lower bound misses bp100 +10.0, `small_ball` +11.0 or `chipzen`'s line from 2b
     (half of each teacher's gain; `chipzen` at 2,000 matches so its interval is near `small_ball`'s). Report that cell's departure share by hand bucket and its paired gain split by match
     length (under 20 hands, 20 or more); the next step is earlier identification (AD1's name seeding is ready),
     not more teachers.
  5. PASS: all of the above hold. Fresh outcome verifier, then the roadmap agent writes the distillation slice.
  A reader test on synthetic results gives exactly one verdict for every combination; plants dropping the D4 guard,
  the fresh check or one of the three bounds each turn a pass into a fail.
* **Tests (each failing on its plant; plant runner committed with them):** the classifier's input list, no D4 rows,
  hold-out by pair; the policy tests (a) to (c); teacher and data pins (plant: one byte changed); the choice rule;
  the rule table; every seed, registry line, count and literal above.
* **Owners and base:** holdem-rl `g0-rl` from v5b-rl 377ec9f (new rows, classifier, misfire table); holdem-x2r
  `g0-root` from v5b-root a4ec310 (G0 file and loader) and `g0` from v5b bedc22e (judge, reader, driver). Non-goals:
  no network trained beyond the classifier, no PPO, no change to the deployed bot, no upload, no E1.
* **Writes, each with its rollback:** commits on the three local branches (revert); gb10-d `~/g0-run/` (rows,
  classifier, G0 files, logs), `~/d0-run/x2r-g0/`, `~/poker-ai-lab-x2r/logs/g0/`, `~/poker-ai-lab-league/candidates/g0-src`
  and `out/g0/` (delete); registry lines `94`, `95`, `112`, `113 G0 read` (restore the copy). `~/bpq.lock`: leave.
* **Budget (each phase stops and is recorded at twice its number):** new rows about 15 minutes (replaced by a
  20-match smoke on the logging path), classifier about 5 minutes, misfire table about 1, the `chipzen` line about 15
  (4,000 matches), screens about 25 for both arms, read about 100, fresh about 10. About 2.5 box-hours on cores 0-17.
* **Held-out design (the roadmap agent, recorded before G0's read):** D4 stays exactly as V5b's for G0. When
  `br_ashwing` and `br_autofast` later join, `ext:ashwing`, `ext:ashwing_search` and `ext:autodidact` become fitted
  cells; `ext:ashwing_hive` and `ext:wolf` stay held out as the real-code cells, with all six style cells. The guard
  line stays at -2.0 and the -5.0 flag stays reported.
* **Housekeeping (not gating G0):** V5b's registry lines, data, e256 and e512 (with hashes) stay on gb10-d as
  comparison arms, not in the trunks' models. To the trunks: the `ad0_log` extensions, generated styles with
  per-match seeding, `chipzen` seeding and hold-out by pair (v5b-rl squashed first); the ensemble loader is not
  merged (14.46: ensembling adds nothing; dropped from future specs). T-a and T-b teachers stay on disk with hashes.
* **After G0 (decided 2026-11-26, before G0 reads; Wayne: design calls are ours, not his):** a gated mixture with
  weights continuous in a posterior and a default expert holding the uncertainty mass is an opponent model plus a
  decision procedure, so G0 itself may become the bot. The candidate slice after a G0 PASS judges two candidates on
  the same cells and fresh confirmation seeds: G0 (the chosen arm) and one 256 network distilled from G0's own play,
  chosen by the pre-registered judge only, G0 preferred on a tie inside the margin (no fit loss). Full process and
  the gate (E1, heuristic head to head, fresh verifier) for both, plus a deployment check for the mixture: every
  expert file and the classifier shipped and hash-pinned, decision time in the arena container, behaviour identical
  to the judged code on replayed matches. G0's current run stays a tier 2 measurement. Longer term (Wayne's MoE
  question): experts by style family defined by shared best response (a teacher-by-opponent gain matrix, which
  also sets the expert count), a learned gate with name-seeded history as prior, fb2-900 as default expert; the
  scarce input is validated stand-ins for the entrant-faced names of 14.29, ahead of more experts. Upload or swap
  stays Wayne's explicit yes on a candidate that passed the full gate.
* **Review record:** plan review 1 REVISE: (1) the classifier is fitted in holdem-rl and evaluated again in
  `g0-root` with no parity test and no fixed file layout; (2) the `chipzen` line of +5.9 sat on the lower bound of a
  1,000-match cell, came from the unseeded opponent, and paired across two roots untested. Revised above: the file
  layout, scaling, activation and precision are literal with a cross-tree parity test and `keep` test (test a2);
  `chipzen` is read at 2,000 against a new fb2-900 arm, with its line measured on the seeded opponent (2b), and test
  (b) covers `chipzen` across the roots. Plan review 2 REVISE: the renormalisation plant could never fire at
  t = 0.80 or 0.50. The review cap of two is reached; the stated minimum revision (a t = 0.30 test fixture with a
  state whose unscaled weights sum above 1) was applied first-hand at 2026-11-26 06:52 UTC and recorded here.

### G0b. A gate that can say "none of these": opponent bet sizes, a population class and a support test (spec, 2026-11-26; tier 2, a measurement; the roadmap agent's decision after 14.47)

* **Question:** does a gate that reads the opponent's bet sizes, weighs every expert against a population class and
  refuses an expert whose class cannot have produced the counts, keep G0's gains (14.47: `small_ball` +16.1, bp100
  +15.2) and stay on fb2-900 against opponents it has never seen?
* **Decision it feeds:** PASS opens the candidate slice (the gate arm itself beside its distillation, full process,
  fresh seeds, E1, deployment check). Nothing here reaches the deployed bot; no upload.
* **Why (14.47 and the probe of 2026-11-26 11:00 UTC):** G0's closed four-way softmax routed `sticky_overbettor` to
  the `small_ball` expert with rising confidence. On 14.37's raw counts the eight Tracker pairs differ between the two
  bots on one pair only (fold when facing a bet: 0.63 against 0.14), and that pair has 2.7 events per match by hand 20
  and 4.2 by hand 40; a Beta-binomial `small_ball` class beats a uniform unknown on 92% of `sticky_overbettor`
  matches at hand 20 and 100% at hand 40, and a per-pair support test rejects only 5% and 11%. No gate form fixes
  that; the inputs must carry more. Opponent bets happen on most hands (unfaced bet rate 0.84 and 0.78), so their
  sizes are the input to add. G50's own play also moved the counts toward `small_ball` (24.4% off the default on
  fb2-900's logs, 33.0% overall and 92.4% past hand 40 in its own play), so every gate figure is read on rows from
  both actors.
* **Prerequisite P0, G80 read post hoc (a measurement, not a verdict; recorded as experiments 14.48 before step D):**
  holdem-x2r `g0` 77f0c00 `tools/g0_posthoc_g80.sh`, run on gb10-d as `setsid -f bash ~/g0-run/g80_posthoc.sh`
  (byte-identical copy, sha256 01e612b0...) from `~/d0-run/x2r-g0`, file `~/g0-run/students/g80.npz` (verified against
  its pins first): `sticky_overbettor` 2,000 on seed 113; departure by hand bucket (`tools/g0_depart.py`, 200 matches,
  seed 95) on `sticky_overbettor`, `small_ball`, `chipzen` and `small_ball_b`; seed 95 on all thirteen B1 and D4
  cells at V5b's counts and `chipzen` 2,000. Rows under `~/poker-ai-lab-x2r/logs/g0/posthoc_g80/{fresh,depart,confirm}`,
  `done` marker there; paired by the same pairing as G0's read (fb2-900 arms on disk). Writes: that directory
  (delete); no registry line (seeds 95 and 113 are G0's, same arms). Budget 100 minutes, stop at 200. Started
  2026-11-26 10:59 UTC. Its read is G80's read in steps 19 and 20; S2 does not use it.

**Step A: one logging run (holdem-rl branch `g0b-rl` from `g0-rl` bad56dd, `tools/ad0_log.py` extended)**

1. Per hand, written per match: the raw Tracker counts `st` after the hand (15 numbers, unseeded Tracker) and the
   hand's engine `action_history` verbatim (seat, action, amount, phase; blinds included), plus the hand number and
   the hero seat. Nothing in the bot's play reads these; logging is a pure copy of what `round_result` delivers.
2. Actors: fb2-900 (`rl/models/fb2_it000900.npz`, f7a29a39...) and G50 (`~/g0-run/students/g50.npz`, 8b1a4cc0...).
   The logger loads a G0 file through a port of `g0-root`'s loader; test L1 below proves the port plays as `g0-root`.
3. Fitting cells, per actor: bp100, `small_ball`, `chipzen` 500 matches each (bp100 through the queue,
   `BPQ_SLICE=G0B`; `chipzen` seeded per match as V5b's D3); the 23 league opponents (`league:<spec>`) 100 each; V5b's
   60 generated styles (`gen:0` to `gen:59`, `~/v5b-run/styles.json`, draw seed 110) 50 each. 6,800 matches per
   actor.
4. Evaluation cells, per actor, never fitted: the eleven D4 cells (`rl/v5b_opps.py` `D4`), 200 matches each. They are
   written under a separate directory; the gate fitter refuses any D4 name (test L4).
5. Seed 114, registered `114 G0B read` (data). Smoke: 10 matches per cell type and actor on this path, timed; the
   runner computes the stop line from the smoke and stops at twice it.
6. Hold-out by pair: u = the first 8 bytes of sha256(`g0b-split:{cell}:{pair_id}`) as an integer / 2^64, where
   cell is the opponent cell name only (`small_ball`, `league:<spec>`, `gen:<k>`; never the actor), and pair_id =
   hero seed // 7 (`ad0_log.pair_of`). Test if u < 0.25, calibration if 0.25 <= u < 0.50, fit otherwise. Both seats
   of a pair and both actors of a pair id get the same label. Test L11: literal labels for six fixed (cell, pair_id)
   inputs, and one pair id under both actors gets one label (plants: the actor in the key, the bands swapped).

**Step B: gate GS (holdem-rl `g0b-rl`, `tools/g0b_gate.py`; float64 throughout)**

7. Terms, from the hands finished so far in the match (the features of hand k come from hands 1 to k-1, as G0's
   misfire table):
   * the eight Tracker count pairs of G0's features f46 to f51, f54, f55 (numerator slot, denominator slot):
     (1, 0), (3, 2), (4, 2), (6, 5), (7, 5), (9, 8), (12, 11), (13, 10);
   * six bet-size terms: each opponent bet or raise (actions `raise` and `all_in` by the opponent seat; calls, checks
     and blinds are not sized) gets the fraction f = (raise-to amount minus the street's current level) / (pot before
     the action), where the pot before the action is every chip committed in the hand so far, blinds included, and
     the level is the highest street bet before it; buckets f <= 0.5, 0.5 < f <= 1.0, f > 1.0; preflop and postflop
     apart. Each bucket is one term: its count over all opponent bets on that street group.
8. Classes: bp100, `small_ball`, `chipzen`, population (the 23 league opponents and the 60 generated styles together).
   No uniform unknown class (the probe above shows it cannot win against a near class).
9. Fit: per class and term, a Beta-binomial on the per-match counts at match end of the fit pairs (both actors
   together): mean from the pooled counts (clipped to [1e-3, 1 - 1e-3]), concentration by maximum likelihood over 60
   log-spaced values from 1 to e^8. Posterior at a decision: softmax over classes of T * (sum of the terms'
   log Beta-binomial likelihoods of the counts so far) + log prior, priors bp100 0.30, `small_ball` 0.10, `chipzen`
   0.05, population 0.55; one temperature T chosen on the calibration pairs (grid 0.05 to 1.0 by 0.05, minimum
   negative log-likelihood of the true class over every decision).
10. Support test per expert class k at a decision: for every term with at least 3 trials, the two-sided
   Beta-binomial tail probability of the observed count under class k (2 x min of the two tails, capped at 1). If any
   is under 0.01, class k is rejected for that decision.
11. Weight: w_k = clip((posterior_k - t) / 0.15, 0, 1) if class k passes the support test, else 0; scaled to sum 1 if
   above 1; the rest of the mass to fb2-900; one draw by `Policy.act`, as G0. Arms GS50 (t = 0.50) and GS80
   (t = 0.80).

**Step C: offline lines (before any play; read on the evaluation cells and the test pairs)**

12. Table: per opponent, actor, threshold and hand bucket (1 to 10, 11 to 20, 21 to 40, over 40), the share of hands
   routed to each expert (w_k > 0) and to any. Ablations in the same table, no line attached: without the six size
   terms; without the support test. Reference column in the same table: G80's offline routing (G0's classifier and
   weights from `~/g0-run/students/g80.npz`, features from the logged `st` after hand k-1, as in S2) on every
   evaluation cell under both actors.
13. Line S1: `sticky_overbettor`, G50-actor rows: routed to any expert on at most 10% of hands in every bucket, at
   both thresholds.
14. Line S2: true bp100 and `small_ball`, test pairs, hands 11 and later, each actor, per bucket (11 to 20, 21 to 40,
   over 40): GS80's share of hands routed to the right expert is at least 0.8 of G80's share on the same hands. G80's
   share is computed offline by G0's own classifier and weights (`~/g0-run/students/g80.npz`, through `g0-root`'s
   `Policy.g0_posterior` and `g0_weights`) on features built by `rl/features.py` `build`'s f46 to f55 formulas from
   the logged `st` after hand k-1, as G0's misfire table did; so both arms are read on the same hands in the same
   units.
15. Reported, no stop: every other D4 cell under both actors at most 10% in every bucket; a miss is named in step 20's
   read.
16. S1 or S2 fails: stop and return the table to the roadmap agent. No second input extension inside this slice.

**Step D: play (holdem-x2r `g0b-root` from `g0-root` 0e3b521, GS file and loader; `g0b` from `g0` 44759f4, judge,
reader and driver)**

17. GS file layout (literal): `gs_t`, `gs_ramp` (0.15), `gs_alpha` (0.01), `gs_min_trials` (3), `gs_temp`,
   `gs_classes` (the four names), `gs_prior` (4), `gs_pairs` (8 x 2), `gs_edges` (0.5, 1.0), `gs_alpha_beta`
   (4 classes x 14 terms x 2), all float64; teachers under `m0_` to `m3_` exactly as G0. Runtime interface
   (`g0b-root`): `RLBot` holds `self.sizes`, a `SizeRecord` (six counts and two totals) reset in `on_match_start` and
   updated only in `on_round_result`, after `self.tracker.round_result`, from that result's `action_history` and
   `self.tracker.me`. `RLBot.decide` calls `self.policy.act(f, mask, gate=(self.tracker.st, self.sizes))` when the
   policy is a GS file and `self.policy.act(f, mask)` otherwise; `Policy.act` and `Policy.probs` take `gate=None`.
   So the gate at a decision sees hands 1 to k-1 only. The observation, Tracker and all-in answer are unchanged.
18. Twenty new generated StyleBots, drawn by holdem-x2r `g0b` `tools/v5b_styles.py draw` with `--seed 115` and
   `--n 20` added (registered `115 G0B read`): V5b's sampler and ranges, V5b's exclusion set and bound literally
   (`~/v5b-run/excl.json`, sha256 5d2f4564..., vectors of `small_ball`, bp100 and the eleven D4 cells, reused, not
   remeasured; redraw within 0.25 by `style_bots_check.distance`), and a style equal in every attribute to one of
   V5b's 60 (`~/v5b-run/styles.json`, ddca5ac1...) is redrawn. Written to `~/g0b-run/styles_g0b.json` (sha256 in the
   record). Cell names `gen2:<k>`, k = 0 to 19, resolved to entry k of that file (env `G0B_STYLES`, default that path)
   by `holdem/gen_style.py` in `g0b-root` (ported from `v5b` bedc22e with the parity test V5b used) and in `g0b`'s
   `style_map.make_opp`; `gen:<k>` keeps V5b's file. Indices 0 to 9 validation, 10 to 19 test, fixed before any play.
   Validation play seed 116, test play seed 117 (registered).
19. Screen, per arm (G80, GS50, GS80): B1's screen (seed 94, six cells, league pairs 400 to 499, 78.0% filter) plus
   the ten validation styles, 200 matches each on seed 116, paired against a new fb2-900 arm on the same seed.
   Eligible: passes the filter, pooled validation gain lower bound above -2.0, no validation style gain under -5.0.
   Chosen: let S be the highest B1 screen score among the eligible; the tie set is every eligible arm with score at
   least S - 0.005 (ties are judged against the top score only, never pairwise); the chosen arm is the first of the
   tie set in the fixed order GS80, G80, GS50. None eligible: stop, return. Test: synthetic scores give exactly one
   arm for G80 and GS80 0.003 apart (GS80), GS50 0.004 above GS80 which is 0.004 above G80 (tie set GS50 and GS80:
   GS80), all three equal (GS80), GS50 0.006 above both others (GS50) (plants: the order removed, ties resolved
   pairwise).
20. Read, chosen arm: seed 95 on every B1 and D4 cell at V5b's counts against fb2-900's arms on disk, as G0; the ten
   test styles, 300 matches each on seed 117, against a new fb2-900 arm; `sticky_overbettor` 2,000 on seed 113
   against G0's fresh fb2-900 arm; `chipzen` 2,000 against G0's chipzen-line fb2-900 arm; departure by hand bucket
   from the arm's own play on every cell (200 matches, seed 95). If G80 is chosen, P0 supplies the seed 95 cells,
   `chipzen` and seed 113 (`~/poker-ai-lab-x2r/logs/g0/posthoc_g80/{confirm,fresh}`) and departure on
   `sticky_overbettor`, `small_ball`, `chipzen` and `small_ball_b` (`posthoc_g80/depart`); step 20 still runs the
   ten test styles with their fb2-900 arm and departure on the other ten cells (`~/poker-ai-lab-x2r/logs/g0b/read/g80`).
   Flag: the arm's own-play departure on `sticky_overbettor` rising more than 10 points in any bucket over its own
   step C figure on G50-actor rows (GS50 or GS80: GS routing at its threshold; G80: the reference column).
21. Rule, first match in order:
   1. GUARD FAIL: a D4 cell under -2.0 with upper bound under zero; or the pooled test styles under -2.0 with upper
      bound under zero; or a test style under -5.0 with upper bound under zero; or `sticky_overbettor` on seed 113
      with lower bound at or under -2.0. Return with the departure table.
   2. GAINS SHORT: a lower bound misses bp100 +10.0 or `small_ball` +11.0. Report gain by hand bucket; the next step
      is earlier identification (name seeding), not a looser gate.
   3. PASS. Fresh outcome verifier, then the roadmap agent writes the candidate slice.
   `chipzen` is reported against its +5.10 line and does not decide.

* **Tests (each failing on its plant; plant runner committed with them):** L1 logger parity: (a) on 200 logged decision states, chosen to
  include at least 20 with some 0 < w_k < 1 under G50 (the test asserts this precondition), the logger's G50 action
  probabilities equal `g0-root` `Policy.probs` from the same file within 1e-12 (plant: posterior in float32); (b) the G50 actor plays 50 matches of `small_ball` byte-identical in match results to
  `rl.eval_arena --model g50.npz` from `~/d0-run/x2r-g0` on the same seed, and fb2-900 likewise against
  `~/d0-run/x2r` (plant: a logging hook that consumes a random draw). L2 replay, on a 20-match smoke: every logged
  hand's list starts with `post_small_blind` and `post_big_blind`, and `Tracker.update` over the list reproduces the
  logged `st` (plants: the logger drops blinds, caught by the first assertion; the logger drops each hand's last
  action, caught by the second). L3 sizing: on ten
  hand-built histories with literal expected buckets (opening raise preflop, a 3-bet, a postflop bet into a pot,
  a raise over a bet, an all-in, a check-call street), the fraction and bucket match (plants: pot without the
  current street, level not subtracted, all-in not sized). L4 the fitter refuses D4 names (plant: `tight_sticky`
  among the fitting cells). L5 the Beta-binomial log-likelihood and tail against direct summation on small n
  (plant: tail one-sided, caught on a case whose two tails differ); and the support test on literal cases: a term
  at 2 trials whose tail is under 0.01 does not reject (plant: min trials 1); a term at 10 trials whose tail lies
  between 0.01 and 0.05 does not reject (plant: alpha 0.05); a term at 10 trials with tail under 0.01 rejects. The
  test asserts each case's tail lies in its stated range before asserting the decision. L6 cross-tree parity: the step A per-hand logs of 20 G50-actor
  matches each of `sticky_overbettor` and `small_ball` are replayed message by message (`on_match_start`,
  `on_round_start`, `on_round_result`, and a decision state at each logged decision) into a `g0b-root` `RLBot` with
  the GS50 file; at every decision its six size counts, summed log-likelihood per class, posterior and GS weights
  equal the fitter's, computed from the same log, within 1e-9 (plants: the size record updated in `decide` from the
  current hand, caught by the size counts; the support test skipped in the runtime, caught by the weights). The test
  asserts at least one decision with posterior_k > t and a support rejection; if the GS50 file gives none on these
  logs, the same replay runs with a test-fixture GS file at `gs_alpha` 0.5 (never a play arm), and the precondition
  is asserted there. L7 neutrality: a GS file forced to population
  gives, on 200 logged decision states, action probabilities equal to fb2-900's exactly (plant: 1e-6 on an expert
  weight), and plays 50 matches of `small_ball`, `ext:ashwing` and `tight_sticky` byte-identical to fb2-900 from
  `~/d0-run/x2r` (plant: the gate consumes a random draw). L8 the style draw: reads `~/g0b-run/styles_g0b.json` and `excl.json`; twenty styles,
  none within 0.25 of any of the thirteen exclusion vectors, none equal to a V5b style, split 0-9 and 10-19; a
  20-match play of `gen2:0` from `~/d0-run/x2r-g0b` builds entry 0 of the new file, not V5b's entry 0 (plants:
  exclusion dropped, `gen2:` resolved to V5b's file, split by order of play). L9 the rule table gives
  exactly one verdict for every combination (plants: each guard term dropped). L10 literals: every number above,
  the seeds and registry lines, the file layout.
* **Seeds:** 114 (logging), 115 (style draw), 116 (validation play), 117 (test play), registered `G0B read`; 94, 95
  and 113 reused as G0 (same arms on disk). The runner copies the registry to `~/g0b-run/seed_registry.pre-g0b`
  first.
* **Writes, each with its rollback:** commits on three local branches (revert); gb10-d `~/g0b-run/` (logs, gate fit,
  GS files, styles), `~/d0-run/x2r-g0b/`, `~/poker-ai-lab-x2r/logs/g0b/`, `~/poker-ai-lab-league/candidates/g0b-src`
  and `out/g0b/` (delete); registry lines 114 to 117 (restore the copy). `~/bpq.lock`: leave.
* **Owners:** holdem-rl `g0b-rl` from `g0-rl` bad56dd (logger, gate fit, step C); holdem-x2r `g0b-root` from
  `g0-root` 0e3b521 (GS file, loader, `SizeRecord`, `gen2:`), `g0b` from `g0` 77f0c00 (style draw, judge, reader,
  driver). Branch names differ from every existing branch of the shared holdem-x2r repo.
* **Budget (each phase stops at twice its number):** logging about 90 minutes (13,600 fitting and 4,400 evaluation
  matches; replaced by the smoke's estimate), gate fit and step C about 10, screen about 40 for three arms with the
  validation styles, read about 110, departure about 30. About 5 box-hours on cores 0-17, after P0.
* **Non-goals:** no network trained, no expert added, no change to the deployed bot, no upload, no within-match value
  estimate, no distillation before a gate passes. Held-out design from here: D4 stays the fixed regression set,
  `sticky_overbettor` included, reported every time; claims about unseen opponents rest on test styles drawn per
  slice and never reused once a design has responded to them; `ext:ashwing_hive` and `ext:wolf` stay the real-code
  held-out cells.
* **Review record:** plan review 1 REVISE: (1) G80's post hoc read was unspecified though S2 and steps 19 and 20 used
  it; (2) three cross-references pointed at the wrong items; (3) the float32, 1e-6 and blind-drop plants could not
  be seen by their assertions; (4) the three-way split was not literal; (5) the new styles had no file, prefix or
  literal exclusion set; (6) the GS runtime interface was undefined. Revised: P0 names the script, cells and writes;
  S2 reads G80's classifier offline on the same hands; the plants pair with exact-probability, blind-start and
  last-action assertions; the split, the styles file, `gen2:` and `excl.json`, and `RLBot`'s gate call are literal.
  Plan review 2 REVISE: (1) the choice could return two arms (G80 and GS80 share t = 0.80) and the G80 branch of the
  read and its flag had undefined inputs; (2) four plants (float32 posterior, support skipped, size update in
  `decide`, min trials and alpha) were not guaranteed to fire on the stated inputs. The review cap of two is reached;
  the stated minimum revisions were applied first-hand at 2026-11-26 11:12 UTC: a fixed order GS80, G80, GS50 with
  ties judged against the top score and a four-case test, the G80 branch's inputs by path, a G80 reference column in
  step C, and literal inputs with asserted preconditions for L1(a), L5 and L6.
* **Build record (steps A to C, `g0b-rl`):** built 72714fd (47 tests, 87 plants). Outcome verifier 1 REFUTED: step C's
  hand buckets and row wiring (S2 label, hand k-1 for the gate and G80) were unpinned; fixed c3a1ee3 (51 tests, 94
  plants). Outcome verifier 2 REFUTED: 16 of its 21 mutations of step B and C wiring (S2's threshold, support and
  expert; the fit's label, actor and class selection; the temperature rows and weights; the any share; the arm
  thresholds and the size ablation's gate and temperature; G80's features; the support test at exactly 3 trials)
  passed every test. The implementation was correct at HEAD on each point; the tests did not pin it. Cap reached;
  fixed first-hand at 2026-11-26 12:48 UTC (4a4a5f1): value tests for each point (two small functions,
  `gates_from` and `report_of`, carry what `main` did), 60 tests, 115 of 115 plants caught on gb10-d, and every
  applicable mutation of verifier 2's script caught (the three that no longer apply are covered by plants of the
  same change). Logging run launched 12:48 UTC from that commit (`~/g0b-run/code`).
* **Run fix (steps A to C):** the evaluation phase crashed at 13:13 UTC: holdem-rl lacked the D4 bots `small_ball_b`
  and `loose_passive` (the smoke ran one D4 rule bot). Ported verbatim from holdem-x2r (b9031b1) with a test that
  every cell builds and that both play byte-identical to x2r's G0 tree; 63 tests, 118 of 118 plants. Resumed 13:18 UTC
  (`tools/g0b_resume.sh`, finished cells skipped, the data stop line restarted from the resume).
  The resumed run stopped at 13:49 UTC on G50's first league cell: the league cells pin holdem-rl's
  `holdem/opponents.py` by sha256 (v5b_opps.LOADED_PINS) and the port had changed it. Repinned (e87a5f5) with a test
  that the file without the ported block is byte for byte the old pinned file (no league or V5b opponent changed); 64
  tests, 119 of 119 plants; every cell type smoked under both actors from that tree (bp100 runs only through its
  queue and had finished for both). Resumed 13:59 UTC. Lesson: a resume after a code change smokes every cell type.
* **Build record (step D, `g0b-root` and `g0b`):** built cb2643e and 2da6f7f. Outcome verifier 1 REFUTED: nine
  result-changing mutations untested (expert-to-network mapping and weight in the GS mixture, SizeRecord pot and call
  bookkeeping, the draw stream after either redraw, eligibility on per-style gain, the flag's bucket map); fixed
  27773b0 and 9521562 (20 tests, 58 plants; 47 tests, 160 plants). Outcome verifier 2 REFUTED on one: eligibility
  reading the pooled gain in place of its lower bound passed every test. Cap reached; fixed first-hand (g0b aaa17ad):
  a case with pooled gain -1.5 and lower bound -5.8, every style at -1.5; 48 tests, 161 of 161 plants on gb10-d.
  Its other 39 mutations were caught; three survivors judged equivalent (a tail of exactly 0.01; an exact float
  collision with a V5b style, which the real-file L8 step would catch; a default path equal to the explicit one).
  Step D launches from g0b-root 27773b0 and g0b aaa17ad.

### E2. Two more experts: the Ashwing and autodidact families (spec, 2026-11-27; the roadmap agent's decision after 14.51; plan reviews 1 and 2 REVISE, cap reached, fixed first-hand)

* **Why first:** Ashwing_v3 and AutodidactInnovations are the only arena entrants whose real code we hold (14.37), so a
  gain against them needs no stand-in argument. The teachers exist and are archived (`train-essentials`): `br_ashwing`
  +16.0 and +15.4, `br_autofast` +13.4 on real code (14.45). The gate machinery is proven (14.49 to 14.51). No training,
  short stages, which suits a box that may be recalled. It does not touch the largest class (solver-like names, about
  35% of entrant seats, 14.29); that is the slice after E2, sized by R3.
* **R3, tier 1, beside E2, reported only (does not gate E2):** on C1v5's replay population, asserted at 330 NLHE
  matches and 10,516 conformance-accepted hands: per entrant name, its seat share and the share of its hands v5's
  gate routes to each expert (C1v5 item 13's routing table, extended with Ashwing_v3 and AutodidactInnovations). It
  orders the work after E2 (the seat share of the Ashwing and autodidact names; whether any solver name routes to T1)
  and changes nothing inside E2.
* **Stage 1, gain matrix (seed 121), inputs fixed:**
  * Teachers, asserted by full sha256 in the runner (copies on archive branch `train-essentials`):
    `~/poker-ai-lab-rl/ckpt/br_ashwing/latest.npz` b247feb2e7c15e767fda96c5a654fa36243916083ba263af5f7a34ed6aeb80d6 and
    `~/poker-ai-lab-rl/ckpt/br_autofast/latest.npz` 08575045b55952d6b37ae8cfa8910442cde918328089fe257db6fe76cdcbbc45.
    The baseline arm is `rl/models/fb2_it000900.npz` (f7a29a39d1bedf08c9c52129205f72af2f73c5bfd59c25de5443629dd088c7d3), played new on seed 121; no rows are
    reused.
  * Cells: the three arms (br_ashwing, br_autofast, fb2-900) against `ext:ashwing`, `ext:ashwing_search`,
    `ext:ashwing_hive`, `ext:ashwing_v2`, `ext:ashwing_value`, `ext:ashwing_adaptive`, `ext:autodidact`,
    `ext:autodidact_fast` (all eight are keys of `rl/field_bots` REGISTRY at `c1v5-root` b14b176), 500 matches each
    (250 pairs, both hero seats), 24 cells. A dry run lists the 24 commands before anything plays.
  * Gain: per (teacher, name), the paired difference in match wins against the fb2-900 arm on the same
    (seed, hero seat) keys, with its two-sided 95% interval (z 1.96), as in 14.45.
  * Row checks (the reader, with plants): every cell has exactly 500 rows with distinct keys, each teacher cell's keys
    equal the fb2-900 cell's keys, and the cell's run log names the asserted checkpoint hash. A short, unpaired or
    wrong-hash cell is void: it is played once more whole on the same seed, and a second void stops the stage.
    Every run and rerun writes to a fresh directory and the driver refuses a non-empty one. A key mismatch between a
    teacher cell and its fb2-900 cell voids both, and both are replayed. A run interrupted by a box recall or any
    outside stop is discarded whole and Stage 1 restarts from its start; that is not a void. The stage table is
    written only from complete cells, and only after all 24 are complete.
  * Class rule, fixed now, one class per name for every pattern of the 16 lower bounds: a name joins a teacher's
    class when that teacher's 95% lower bound is +5.0 or more; if both teachers clear, it joins the one with the
    larger lower bound (exact tie: the ashwing family for `ext:ashwing*` names, the autodidact family otherwise); if
    neither clears, it goes to the population class. `ext:ashwing_hive` (and `ext:wolf`, not in the matrix) never
    join a class whatever their bounds; they stay the held-out real-code cells and are fitted as population.
  * Stop lines after Stage 1: both new classes empty stops E2 and the table returns to the roadmap agent; one class
    empty continues E2 with the other class alone (five classes, the empty class's prior added to population). A
    class whose only member is its teacher's training name (`ext:ashwing` for br_ashwing, `ext:autodidact_fast` for
    br_autofast) still counts as a class.
* **Held-out set, amended for E2 (the one change to G0b's design, made on purpose):** a D4 name that Stage 1 makes a
  class member (only `ext:ashwing`, `ext:ashwing_search` or `ext:autodidact` can be) leaves D4 for E2 and is judged
  by the NEW lines instead. Always held out, whatever Stage 1 says: `ext:ashwing_hive`, `ext:wolf` and the six rule
  bots (`tight_sticky`, `sticky_overbettor`, `small_ball_b`, `never_fold_pre`, `raise_station`, `loose_passive`).
  The fitter's L4 refusal becomes: refuse any D4 name except the Stage 1 members listed in `stage1_classes.json`, and
  admit those only from Stage 2's fit pairs (seed 122, pairs 0 to 199). Every ext name ends in exactly one of
  {fitted class member, held-out D4}; the non-members `ext:ashwing_v2`, `ext:ashwing_value`, `ext:ashwing_adaptive`,
  `ext:autodidact_fast`, when members, are new data opponents and were never D4. Test: a non-member D4 name added to
  the fit rows still fails L4 (plant: the member list ignored).
* **Stage 2, logging (seed 122):** the member names, 500 matches each under both actors (fb2-900 and v5; autodidact at
  300 if the smoke says it is too slow), action lists as in G0b; existing class rows reused by hash.
* **Stage 3, gate GS50+2, offline lines (one arm, nothing selected):**
  1. Classes bp100, small_ball, chipzen, ashwing family, autodidact family, population; priors 0.30, 0.10, 0.05, 0.05,
     0.05, 0.45; the same terms, support test and threshold 0.50 as v5.
  2. New classes: on Stage 2's held-out pairs (seed 122, pairs 200 to 249 of each member name, which the fit never
     reads; the fit uses pairs 0 to 199), hands 11 and later, at least 50% routed to the right expert.
  3. Misroute: every remaining D4 cell (hive and wolf always among them) and V5b's generated styles at most 10% routed to any expert in every hand
     bucket, under both actors.
  4. Old classes: the routed share to the right expert not more than 5 points under v5's on the same rows.
  5. Any line fails: stop and return the table to the roadmap agent.
* **Stage 4, read (confirmation seed 125; ten validation styles drawn on seed 123 and played on 124; ten test styles
  played on 126; new fb2-900 arms throughout):**
  6. Eligibility on B1's screen (seed 94, pairs 400 to 499, 78.0% filter) and the validation styles, as in G0b.
  7. Lines on seed 125, in order. GUARD: no cell under -2.0 with its upper bound under zero, hive and wolf included;
     test styles pooled lower bound above -2.0, none under -5.0 with its upper bound under zero. KEEP: bp100 lower
     bound above +10.0, small_ball above +11.0. NEW: lower bounds above +8.0 on ext:ashwing, +7.7 on
     ext:ashwing_search, +6.7 on ext:autodidact (half of each teacher's gain). A NEW miss with GUARD and KEEP holding
     is recorded and still goes on, since it is no worse than v5.
* **Stage 5, candidate v6:** C1v5's steps unchanged (deployment check with live-format parity for the gate inputs,
  fault counter with one record per run, E1 on pairs 200 to 399, the heuristic head to head, a fresh verifier, then
  Wayne). Entering it is his call for the next season.
* **Non-goals:** no network trained, no new teacher, no change to v5, v4 or the deployed bots, no upload or Chipzen
  action, no fetch from chipzen.ai, no change to D4 beyond the amendment above.
* **Review record:** plan review 1 REVISE (inputs not fixed, class rule incomplete, no envelope, rows could pass
  vacuously, R3 unbounded); revised. Plan review 2 REVISE (the held-out set changed silently, seed 94 unregistered,
  the void path could reuse rows or end on a recall, no tests or pins or non-goals, R3 without budget or writes). The
  cap of two is reached; fixed first-hand on 2026-11-27 (this text).
* **Recall care:** the fitted gate file and the class rows' hashes go to `train-essentials` at the end of stage 3;
  each stage's table is pushed to research before the next starts; `restore.md` gets the E2 state line each time.
* **Seeds:** 121 to 126 as above. Before Stage 1 the runner copies `~/poker-ai-lab-rl/tools/seed_registry.txt` to
  `~/e2-run/seed_registry.pre-e2` (once) and appends `94 E2 read` (Stage 4's B1 screen, pairs 400 to 499) and
  `121 E2 read` to `126 E2 read`; rollback restores the copy. A dry run greps the copy for one `E2 read` line per seed.
* **Tests and pins (branch `e2`, with a committed plant runner, every plant caught before launch):** a
  synthetic-bounds test of the class rule over every pattern (both teachers clear, one clears, an exact tie, neither
  clears, `ext:ashwing_hive` clearing yet staying out); the Stage 1 stop lines (both classes empty, one empty, a class
  of only its teacher's training name); the row checks (499 rows, a duplicate key, a shifted key set in one teacher
  cell, a wrong checkpoint hash, an interrupted cell, a non-empty cell directory); R3's population assertion (330
  matches, 10,516 hands). Literal pins in the reader itself: the +5.0 bar, z 1.96, 500 rows, seed 121, the three full
  sha256 values, and the eight registry keys asserted present in `rl/field_bots` REGISTRY of the run's root copy.
  Each Stage 1 run log records the root and x2r commit hashes and the three checkpoint hashes. Teacher arms load
  through `rl.eval_arena --model <npz>` from the root copy (`c1v5-root` b14b176), as fb2-900 does.
* **Owners and bases:** branch `e2-root` from `c1v5-root` b14b176 (runtime, the new gate file, packaging) and branch `e2`
  from `c1v5` 4767f28 (drivers, judges, readers, tests and plants); the training tree is read only. Box run dir
  `~/e2-run` (code copies `code-root`, `code-x2r`, logs, markers), rows `~/poker-ai-lab-x2r/logs/e2/`. R3: tool
  `tools/e2_r3.py` on `e2`, output `~/e2-run/r3.json` and `r3.out`.
* **Budget (each stage stops at twice its number), cores 0-17:** Stage 1 about 90 minutes (the six autodidact cells
  dominate: 1,000 `ext:autodidact` matches took 57 minutes at 6 workers in C1v5, so about 29 minutes per 500; three
  cells run at once, 6 workers each), Stage 2 about 60, Stage 3 about 20 (offline), Stage 4 about 150, Stage 5 about
  60 as in C1v5. R3 about 15 minutes, run on cores 18-19 beside Stage 1 (stop at 30).
* **Writes, each with its rollback:** commits on `e2-root` and `e2` (revert); `~/e2-run/` and
  `~/poker-ai-lab-x2r/logs/e2/` and R3's `~/e2-run/r3.*` (delete); registry lines 94 and 121 to 126 (restore the copy); at the end of Stage 3 the
  gate file and the class rows' hashes added to archive branch `train-essentials` (a new commit, revertible).
* **After E2 (outline, to be specified from R3):** the solver class. Make the stand-in a family, not one bot: run the
  solver image at several settings (play threshold, resolver on and off, other stack depths if the image allows;
  which knobs exist is unverified), measure each variant's A0 distance to Blueprint, fermat6, NashForge and hoops,
  train one teacher against the pooled variants nearest the real names, and fit the gate class on the pooled variants
  so its support covers the real names. Pre-registered check: R3's routing table repeated; the real solver names must
  route to that expert.
* **Unverified at writing:** the seat shares of the Ashwing and autodidact names; whether C1v5's reported table 4.2
  holds R3's numbers; the solver image's settings.

### Global path: decomposition and ranking (the roadmap agent after the Redirect, 2026-11-27 08:30 UTC)

Read only report; the first slice is "### GP0." below. Order: GP0, then GP1 chosen by GP0's outcome table (Path A the
lookahead as the bot, the safety blend first, Path C model work, or Path B a deeper procedure), a base slice only on
BASE-UP, live reads as seasons allow. V6b stays parked; v5 stays uploaded and not entered, no v5.1; v4 stays the default
entry. No new per-opponent expert.

#### 1.1 What decides match wins against the live field

* **Objective:** the field-weighted sum over opponents of P(match win), on what an entrant actually faces (14.29, 14,531 entrant seats): Blueprint 15.4%, fermat6 6.8%, NashForge 6.1%, hoops 5.8%, mr_hide 5.7%, r0ckGarden 5.3%, PluriBot 3.8%, slopBot 2.7%, WSmithSimLab 2.3%, the ten regulars 5.4%, a long tail for the rest. The solver-like cluster is about 35% of seats. The names we hold code for (Ashwing, autodidact) are 2 to 4%.
* **How a match is won:** 100 bb start, blind steps every 20 hands, median field match 26 hands, 42% end before hand 21 (experiments section 1, Revision 2). A hand of 5,000 chips or more occurs in 76.5% of matches (14.29). So a match is one or two stack-sized pots plus the small-pot drift that sets the stacks going into them. Match value is near linear in chips between near-equals (14.28, K 0.80 against bp100) and strongly concave when we have an edge (14.16), so the utility must follow the estimated edge.
* **Where our chips go today (real code and one live loss):** folding after the flop (60.7% folds to 0.4 to 0.8 pot flop bets against a 39.5% break-even, 14.26; the exploiter takes 1.09M chips there, 14.8); stack commitments at bad equity against the solver proxy (flop shoves called at 0.284, river call-offs at 0.198, 14.27); thin river raises into better hands (14.26).
* **The fact that orders everything:** we have no measurement of our own win rate against 96% of the live field. Live record is about ten matches (14.26, HANDOFF). Clones overstate by 20 to 30 points (14.3) and even good clones by 2 to 7 (14.25). bp100 sits at the edge of the solver cluster (0.250 from Blueprint, preflop raise +0.22, 14.37), T1 gains nothing on the Blueprint clone (14.53), and Blueprint cannot be told from bp100 on the gate's terms (14.56).
* **A fact about v5 that supports the owner's challenge (14.52, checked in the table):** on live names v5's small-ball expert fires on at most 0.2% of hands (slopBot, the bot it was styled on: 0.1%) and br_chipzen on at most 7%. Live, v5 differs from v4 almost only by T1 on solver-looking names (Blueprint 38.5% of hands, MonteCarlo 41%, NashForge 21%), where nothing measures T1. The +18.9 and +20.1 are gains on our stand-ins.
* **Why adaptation is still the right core:** the best responses conflict. Training on one class gains 12 to 22 points there (14.12, 14.30, 14.31, 14.41) and costs 6 to 18 elsewhere (14.33); one PPO policy on the mix keeps a quarter of the gains and loses 3 to 5 on other families (14.36). No single reactive policy is best against this field, so the gain has to come from knowing the opponent, and the owner's rule says how: a model plus a procedure plus a safety blend, applied identically to every name.

#### 1.2 Levers

| lever | evidence held | expected gain on the live field | cost here | risk |
|---|---|---|---|---|
| **E. Evaluation that reflects the field** | 14.3, 14.25, 14.37, 14.53, 14.56; about ten live matches | none directly; it is what tells the other levers apart on 96% of seats | zero compute. Archive reads are free; live challenges are the owner's standing limit and are not raised | without it every gain below is a claim about held-out real code and archive calibration, not about the arena |
| **M. Opponent model that generalizes from the field** | frequencies: name adds 0.080 nats, in-match +0.378 on unseen names (14.13); the λ range +1.09 nats on held-out replays (14.20); one population net fails cold start but passes for names with history (14.32); a per-name fine-tune gives R +1.00 against +0.57 at 1,000 matches and +0.88 at 100, failing only fold calibration at big postflop bets by 5 to 7 points (14.34); 75.1% of seats face a name with 100 or more archived matches, under 1% a first match (14.29) | sets how much of the procedure's ceiling is realized: true range +3.2 against X1's range -4.8 on the same seeds (14.19) | GPU minutes per name (0.06 GPU-hours for three bots, 14.34) | likelihood and strength move apart (14.25); big-bet calibration; runtime size in numpy is unmeasured |
| **P. Decision procedure** | match-win utility is required, a one-street search is not enough (14.16); rollouts with the true model +4.2 [+2.7, +5.7], losses halved, on cells we already win 92% (14.17); with X1 plus λ at N = 32: `ext:` +2.8 [+0.9, +4.7], rule pool +0.1, fits the arena (14.22); the specialists' gain is a whole-strategy shift of +12 to +22 (14.12, 14.30) | unknown where it matters: the ceiling was never measured on a cell the base wins under 80%. T2 was deferred | CPU only: about 0.3 s per decision at N = 32, 1.9 s at N = 128 | a one-step improvement over a policy that folds later streets may not reach a multi-street shift |
| **S. Safety of exploitation** | the Z gate tests rollout noise only: X2m lost 4.6 with every override past 2.6 standard errors (14.18); `sticky_overbettor` -11.7 at N = 128, -3.0 at N = 32 (14.21, 14.22); a closed gate misroutes an unseen bot with rising confidence (14.47), a support test fixes it (14.49) | turns "gains on one pool, level on the other" into something that can ship; worth the size of the guard losses, 3 to 12 points on wide bettors | small: an ensemble or posterior draw in the rollouts and a predictive-evidence gate | gating the gain away |
| **B. Base strategy exploitability** | a 2-minute exploiter wins 96.5% (14.9); the exploiter league brought it to 78.7% and then stopped paying, at -3 league points and -1.1 [-2.8, +0.6] on bp100 (14.10, 14.15, 14.27); 5 of the field's top 10 are themselves exploitable by over-folding and slopBot rates first by exploiting, not by being sturdy (14.29); the real blueprint wins only 63% against random (14.1) | against today's field: unproven, possibly zero. Never measured: whether the sturdier checkpoint wins more against the styles that take the over-fold. For the future field it is insurance against adaptive bots | a real recipe change is days of training with no known recipe; one read of the existing checkpoint is minutes | highest: the only attempt lost field win rate |

#### 1.3 Ranking and the order of slices

1. **GP0, the first slice (spec in Part 2): procedure ceiling and model transfer, measured on held-out real code with a model fitted only on what the arena shows.** It ranks first because it is the central claim of the owner's architecture, it has never been measured where the base is weak, it needs no training, and each stage can kill a path. It also carries a one-hour read of the sturdier base on the aggressor styles, which settles lever B's rank with data instead of argument.
2. **GP1, chosen by GP0's outcome table** (stop and switch rules are the table in the spec):
   * **Path A, the lookahead as the bot:** numpy port at N = 32, per-name fits over every archive name with 100 or more matches on the gb10-c GPU, K from the estimated edge, the safety blend, then the deploy gate. Taken when the fitted model carries the gain and guards hold.
   * **Safety first:** the blend alone on the failing cells, when the gain is there but a guard fails.
   * **Path C, model work:** pot-weighted calibration at big bets and capacity on the GPU, judged by GP0's Stage B rerun on fresh seeds, when the true model gains and the fitted one does not.
   * **Path B, a deeper procedure:** when rollouts cap low even with the true model. One policy conditioned on the model's posterior, trained on the GPU against the fitted models of the archive's names with fb2-900 as the anchor. Its own kill test comes first: a best response trained against the fitted model of `ext:ashwing` must keep at least half of br_ashwing's +14.2 on the real code.
3. **Base slice, only if GP0's Stage 0 reads BASE-UP,** written then for the gb10-c GPU beside GP1. On BASE-FLAT, E3 stays a reported number and the base's leaks are left to the procedure, which fixes them online against whoever takes them.
4. **Live read:** whatever is entered plays its season fixtures and the archive fetch brings them in. With about ten matches a season this confirms nothing per class; the per-class live judge exists only with a challenge series, which is the owner's standing limit. Until then the judge of record is held-out real code plus archive calibration, and every result says so.
* **Switch rule between slices:** a lever that fails its pre-registered line twice in a row drops one rank and the order is re-read, as 14.15 closed the exploiter league. No slice widens its own scope.
* **Standing rule kept from the Redirect:** no new per-opponent expert. GP0's cells are real-code bots used as held-out tests of a name-agnostic pipeline; nothing is trained against them and no class is added for them.

#### 1.4 V6b and v5

* **V6b: stays parked, no run, no verification, nothing deleted.** Checked: `v6` e23e5a9, `v6-rl` 6d56896 and `v6-root` e9a9d95 are on the archive and on origin, and the three local worktrees are clean. Two pieces are worth lifting later, by name: the explicit class-to-expert map with its refusal of a file that names a missing network, and the open-set support test of G0b, which is the natural form of the safety blend's "do I know this opponent" question. Its two families are 2 to 4% of seats and its solver decision (give up T1) is made moot by the path change.
* **v5: leave it uploaded and not entered; no v5.1, no further work on it.** Live it is v4 plus T1 on solver-looking names with no evidence either way (14.52 to 14.54), and a wrong expert costs 12 to 18 points where it plays (14.33). My judgment, not a measurement: v4 stays the default entry for the next season because it is the measured quantity; entering v5 would be a bet on T1 against the live Blueprint that eight fixtures cannot read. v5 keeps its value as the reference package (gate, card, HF copy) and as the rollback for a gated candidate.
* **Account note:** the account holds three bots (v3, v4, v5), so the next candidate's upload needs a deletion, and v3 is the one to give up. That is the owner's yes when a candidate exists, not now.
* **Recall risk found while checking:** the data GP0 needs is on gb10-d only. `ckpt/s2`, the G1 base fits (`fit_fold*_W.pt`) and D2a's logs are absent from archive branch `train-essentials` (checked: its checkpoints are br_ashwing, br_autofast, br_bp100, br_chipzen, br_small_ball, fb2). A recall before GP0 costs about 6 GPU-hours and 12 core-hours to rebuild them.

### GP0. Does a model fitted only on what the arena shows carry the lookahead on real code, and how high is the lookahead's ceiling where the base is weak? (spec, 2026-11-27; a measurement, nothing reaches the bot; the roadmap agent after the Redirect)

* **Why:** the Redirect asks for the global path: a model of the opponent, a procedure that maximizes match wins against it, a safety blend. Three things about that path were never measured, and each can end it or turn it:
  1. The procedure's ceiling where the base is weak. 14.17's +4.2 with the true model is on cells fb2-900 wins 83 to 95%. Against `small_ball` it wins 75.7% and training reaches 97.6% (14.30). Rollouts are a one-step improvement on a policy that folds later streets, so the ceiling there is open.
  2. Whether a model fitted from arena-visible logs carries that gain on real code. 14.34's per-name fine-tune reads ranges at +1.00 nats against the λ range's +0.57, and was stopped on one calibration bucket before it ever drove a decision. 14.25 warns that likelihood and strength move apart.
  3. Whether the sturdier base wins more against the styles that take fb2-900's over-fold. S2 it1800 (E3 78.7% against 96.5%) was read on bp100 and the league, never on the aggressor cells.
* **What this is not:** no expert, no gate class, no training against any cell. The pipeline (logs of a name, a fit, the lookahead) is the same for every name; the real-code bots are its held-out test, as the archive names will be its use.
* **Facts checked at writing (local refs of the archive, 2026-11-27):**
  * `tools/x2r_oracle.py` on `c1v5` 4767f28 has the arms oracle, x1, oracle-range, x1-range, x3; `ext:` opponents only under x1 and x3; no bpopp opponent.
  * The oracle refuses `small_ball` and `small_ball_b` (`tools/x2s_ablate.py` `refuse_street_bet`: its bet probability is `bet[i]` without the `street_bet` multiplier). `small_ball` is `street_bet` (1.0, 0.92, 0.64) and nothing else beyond StyleBot; `small_ball_b` also shoves preflop (`shove_p`).
  * `rl/search.py` holds K as a module constant, 2 ln(0.912 / 0.088) = 4.68.
  * The fit side lives on `g1-2a` f3d1afd (`tools/d2_generate.py`, `d2_clone.py` with a play-time `CloneBot`, `g1_tune.py`, `g1_2a_*.py`, `league/`), whose `holdem/opponents.py` has no `small_ball`; `c1v5` has the cells and no fit tools. Merge base d4c3cb8.
  * D2a's generator seats the bot against hero k mod 6 of (fb2_900_policy, heur_102b05e, raise_station, sticky_overbettor, tight_sticky, never_fold_pre). One match in six is against our own policy.
* **Envelope:**
  * **Owners:** the main session builds through an executor and runs the box; the roadmap agent owns the lines and the outcome table; a fresh outcome verifier checks each stage's read. Plan review as usual, cap 2.
  * **Branch to create:** `gp0` from `c1v5` 4767f28, with the fit tools and `league/` copied from `g1-2a` f3d1afd in one commit that names the source commit and file list. Owned files, new unless noted: `tools/gp0_drive.sh`, `tools/gp0_read.py`, `tools/gp0_fit.sh`, `tools/gp0_model.py` (numpy net, root posterior, rollout opponent), `tests/test_gp0.py`, `tests/gp0_plants.py`; edits to `tools/x2r_oracle.py` (arm `g`, K per run, the bpopp opponent), `tools/x2s_ablate.py` (the `street_bet` multiplier in `_probs`), `tools/d2_generate.py` (targets `small_ball`, `sticky_overbettor`, bp100), `rl/search.py` (`win_prob` takes K; default unchanged).
  * **Not created:** no `-rl` and no `-root` branch. The hero is fb2-900 as in X3b and R1; `c1v5-root` b14b176 is not touched.
  * **Box:** gb10-d, dir `~/gp0-run`, cores 0 to 17, bp100 cells alone in the serial bpopp queue. Fits on gb10-d's GPU under the GPU lock with the page cache dropped before and after (the base fits and logs are there); gb10-c's GPU is held for GP1.
  * **Writes:** branch commits (revert), `~/gp0-run` (delete), registry lines (remove). Rollback: nothing is deployed.
* **Seeds: next free from the registry, registered first.** Four read seeds in this order: Stage 0, Stage A screen, Stage A read, Stage B read; one more for the new fitting logs. Smoke runs use a seed outside the registry. D2a's 61 stays the fitting seed of its existing logs. Bootstrap 47.
* **K, fixed here (14.28's definition, K = 2 ln(p / (1 - p)) from the recorded fb2-900 rate, capped at 4.68):** `small_ball` 2.27 (75.7%, 14.29); `sticky_overbettor` 3.11 (82.6%, 14.33); `ext:ashwing` 2.08 (73.9%, 14.9); `ext:autodidact_fast` 2.45 (77.3%, 14.25); bp100 0.80 (59.85%, 14.27); `ext:wolf` 4.68 (cap).
* **Budget:** expected 22 box-hours on 16 cores, hard cap 40; GPU under 0.5 hours, cap 2. Per stage: Stage 0 about 0.5 (cap 1); Stage A about 6 (cap 10); Stage B about 15 (cap 28).
  * **Smoke on the real path before each stage:** 20 matches per (cell, arm) through the stage's own driver and reader, timed per decision. The scaled total over the stage's cap means the stage does not start and returns to the roadmap agent.
  * **Stops:** a stage past its cap stops and what finished is recorded, not judged. A crash stops the slice until the cause is known. A run interrupted by a recall or any outside stop is discarded whole and rerun in a fresh directory; the driver refuses a non-empty one.
* **Stage 0. The sturdier base on the styles that take the over-fold (tier 1, reported with one line).**
  * S2 it1800 (`ckpt/s2/it001800.npz`, sha256 prefix 4989481c5e7d5d8b, 14.15) and fb2-900, plain `rl.eval_arena`, 2,000 matches per cell, cells `small_ball`, `small_ball_b`, `sticky_overbettor`, `loose_passive`, paired on (seed, hero seat).
  * **BASE-UP:** it1800 minus fb2-900 on `small_ball` has its 95% lower bound at or above +4.0, and the four-cell pool's lower bound is above -2.0.
  * **BASE-FLAT:** the `small_ball` upper bound is under +4.0.
  * Otherwise BASE-OPEN, reported. If the file is missing or its hash differs: NOT RUN, recorded, and nothing waits on it.
* **Stage A. The lookahead's ceiling with the true model.**
  * **Build first:** the oracle models `street_bet` (bet probability `bet[i]` times the street's multiplier); `small_ball_b` stays refused.
  * **A1, K screen:** `small_ball`, 600 matches, arms off (N = 1), oracle N = 32 at K 2.27 and at K 4.68, Z = 2.6. The K rule for the rest of the slice is the per-cell table above if the 2.27 arm's point estimate is at or above the 4.68 arm's, else 4.68 everywhere. Chosen on the screen seed only.
  * **A2, the read, fresh seed:** `small_ball` 1,000 matches with arms off, oracle N = 32, oracle N = 128; `sticky_overbettor` 600 matches with arms off and oracle N = 32. Z = 2.6. Paired against off.
  * **Lines, on `small_ball` at N = 128, 95% paired interval** (reference: the trained response gains +21.9 [+19.9, +23.8], 14.30):
    * **A-HIGH:** lower bound at or above +8.0.
    * **A-LOW:** upper bound under +4.0. GP0 stops here; Stage B does not run; the next spec is Path B.
    * **A-MID:** anything else. Stage B runs.
  * Reported: N = 32 minus N = 128, `sticky_overbettor`'s gain, overrides by street and by kind, hands per win.
* **Stage B. The fitted model on real code.**
  * **Cells:** gain cells `ext:ashwing`, `ext:autodidact_fast`, bp100 (1,000 matches each); guard cells `ext:wolf`, `small_ball`, `sticky_overbettor` (600 each).
  * **Fitting logs, only what the arena shows and never our own policy:** D2a's seed-61 logs for the three `ext:` bots; new logs for `small_ball`, `sticky_overbettor` and bp100 from the same generator and hero mix. Matches whose hero is fb2_900_policy (k mod 6 = 0) are dropped; sizes 100 and 1,000 are the first matches by index after the drop. No fit opens a `true_cards.jsonl`.
  * **Fit:** 14.34's arm (c) with its literals: the W base fit of the fold that held the bot's name out (`fit_fold2_W.pt` for the Ashwing and autodidact names; fold 0 for names absent from the archive), start epochs 0, 4 EM iterations, Adam 3e-4, first 90% to fit, last 10% for the per-street fold bias. Exported to npz; the lookahead reads it with numpy only.
  * **Arm `g`:** the root range is the posterior over live combos under the fitted net's likelihood of every action the opponent took this hand; the rollout opponent is the same net acting on its sampled combo, with the in-match block causal and the history block fixed from the fitting split. No λ, no band.
  * **Arms, N = 32, Z = 2.6, the Stage A K rule:** off (N = 1); x3 (today's cold-start arm, 14.22); g1000 on every cell; g100 on the gain cells; the specialist at N = 1 where one exists (br_ashwing, br_autofast, br_bp100, br_small_ball); oracle N = 32 on the two rule cells, same seeds.
  * **Lines, 95% paired intervals; the gain pool is the gain cells present, equal weight:**
    * **CARRIES:** g1000 minus off, pooled, lower bound at or above +2.0. **NO-CARRY:** upper bound under +2.0. Else **MID**.
    * **MODEL-ADDS:** g1000 minus x3, pooled, lower bound above 0.
    * **GUARD FAIL:** any guard cell whose g1000 minus off has its upper bound below 0.
    * **MODEL-LOSS:** oracle minus g1000, pooled over the two rule cells, lower bound above 0.
    * **SIZE-100:** g100 minus off, pooled, lower bound above 0. Reported with one use: it says whether names with 100 to 999 matches are served in GP1.
  * Reported per cell: g1000's gain over the specialist's gain, x3 minus off (the unseen-name floor under the new K), overrides by kind, the fold calibration table by bet-size bucket, numpy seconds per decision.
* **Outcome table, one row per result:**

  | Stage A | Stage B | next |
  |---|---|---|
  | A-LOW | not run | Path B: a deeper procedure, its transfer test first |
  | HIGH or MID | CARRIES, MODEL-ADDS, no GUARD FAIL | Path A: the lookahead as the candidate (numpy port, per-name fits over the archive on gb10-c, K from the estimated edge, the safety blend, the deploy gate) |
  | HIGH or MID | CARRIES, GUARD FAIL | the safety blend alone, read on the failing cells on fresh seeds, then Path A |
  | HIGH or MID | CARRIES, not MODEL-ADDS, no GUARD FAIL | Path A with the cold-start model for every name; per-name fits are dropped |
  | HIGH or MID | MID or NO-CARRY, MODEL-LOSS | Path C: model work on the GPU, judged by Stage B again on fresh seeds |
  | HIGH or MID | NO-CARRY, not MODEL-LOSS | Path B |
  | HIGH or MID | MID, not MODEL-LOSS | returned to the roadmap agent with the per-cell table; no path is taken on it |

  Stage 0 adds to any row: BASE-UP means a base slice is specified beside the next one; BASE-FLAT means E3 stays reported and the base stays last.
* **Tests and plants (`tests/test_gp0.py`; `tests/gp0_plants.py` is the committed plant runner, and a kill counts only when the named assertion fails on the planted path):**
  * Oracle: its per-combo probabilities equal the bot's own `decide` frequencies on sampled spots for `small_ball` on each street (plants: multiplier dropped; the flop's multiplier used on the river); `small_ball_b` is still refused.
  * Every arm at N = 1 plays byte for byte as the policy on 20 seeds, arm `g` included.
  * Arm `g`: the root posterior equals a brute-force product on a toy net (plants: board cards left live; the hero's cards left live); the rollout opponent's input equals the fit-side vector at the same decision (plants: a raise read as raise-to; history block built from read-seed matches); numpy output equals torch within 1e-5 on 1,000 rows (plant: a bias dropped).
  * Fitting data: no match with hero fb2_900_policy (plant: k mod 6 = 1 dropped instead); sizes exactly 100 and 1,000 after the drop (plant: 1,000 before it); no `true_cards.jsonl` opened (plant); the base fit is the held-out fold (plant: a fold that trained on the name).
  * K: the six literals; `win_prob` uses the run's K (plant: the module constant); the A1 choice rule on a tie.
  * Reader: a missing key, a seed mismatch, a wrong row count (600, 1,000, 2,000) each fail; one override-count record per judged run, and an absent record fails closed.
  * Lines and table: the literals +8.0, +4.0, +2.0, 0 and -2.0 driven from both sides; the outcome table enumerated over every combination of its inputs, one outcome per cell.
  * Driver: a non-empty output directory, an interrupted run, a smoke estimate over the cap, a read seed without its registry line.
* **Non-goals:** no training of any policy; no gate, class or expert; no change to v4, v5 or the account; no fetch from chipzen.ai; no runtime port to the deployed image (seconds per decision are reported only); no safety blend (it is the next slice when the table says so); no archive-name fits; no change to G1's or D2a's recorded outputs.
* **Fallbacks fixed now:** if the bpopp opponent or bp100's fitting logs fail their tests after two fix rounds, bp100 is dropped, recorded, and the gain pool is the two `ext:` cells. If the play-time vector for the G1 profile blocks cannot be proven equal to the fit side in two rounds, arm `g` uses D2a's per-name network (14.34's arm (b), which has a play-time `CloneBot`) and the record says so.
* **Unverified at writing:**
  * That `ckpt/s2/it001800.npz`, the G1 base fits and D2a's fitting logs are still on gb10-d; none is on the archive.
  * The registry's live state: the copy in `environment/` ends at 120, while 121 (E2) and 127 (V6) are used and V6b named 122 to 126 without writing them.
  * Per-decision cost of the neural rollout opponent and hero decisions per match; the budget's 15 box-hours for Stage B assumes about 1.5 times the X1 arm's cost.
  * Whether a play-time builder for G1's 37 profile inputs exists beyond `embed_d2a`.
  * How the D2a generator and the lookahead tool drive a bpopp container as the opponent; neither does today.
  * Whether fold 0's base fit is the right one for bp100 and the rule cells (they are absent from the archive; Blueprint, a relative of bp100, is in its training names).
  * The K literals were computed by me from the cited rates and have no test yet.
  * Paired standard errors of about 1.3 points on the gain pool and 1.7 on `small_ball` are estimates from 14.17 and 14.22, not measured at these sizes.
* **Checked by the main session after writing (gb10-d, 2026-11-27 08:34 UTC):** `~/poker-ai-lab-rl/ckpt/s2/it001800.npz`
  sha256 prefix 4989481c5e7d5d8b (present); G1 base fits `~/poker-ai-lab-d2s2/data/g1/fit_fold{1,2,3,4}_W.pt` and
  `slice2k/fit_fold0_W.pt` (present); D2a logs under `~/poker-ai-lab-d2s2/logs/d2/<bot>/{fit,heldout}/` (present); the live
  registry holds 94, 121 to 126 (`E2 read`) and 127 (`V6 draw`), so the next free seed is 128. None of these files is on
  `train-essentials` yet.

### V6b. v6 without T1: experts only where we hold real code or our own judge cell (spec, 2026-11-27; the roadmap agent after 14.56; revision 1 after plan review 1)

* **Status: STOPPED 2026-11-27 08:23 UTC by Wayne, before any run.** He asked whether this is a global solution and judged it is not: every slice since G0 adds an expert for a known opponent behind a gate, which gains only where the gate names the opponent (v5: bp100, small_ball, chipzen; V6b's families are about 2 to 4% of live seats) and leaves the base strategy, which a 2-minute exploiter beats 96.5%, unchanged. Work returns to the global path (opponent model plus a decision procedure plus a safety blend, Wayne 2026-11-21). The partial build is parked unverified: `v6-root` e9a9d95, `v6-rl` 6d56896, `v6` e23e5a9 (no V6b commit); gb10-d scratch `~/v6b-build`. No seed, registry line or run directory was written.

* **Why:** 14.56 shows that on the gate's 14 terms arena Blueprint and bp100 overlap, and 14.53 shows T1 gains nothing
  on the Blueprint clone at 45.7% routing. Every hand T1 plays in the arena is on an opponent we have no evidence for,
  and the opponent it was built for (bp100) is not in the arena. v6b drops T1, adds the two E2 families, and holds
  solver-looking opponents on the default. v5's +18.9 on bp100 is given up on purpose. Rejected: another prior (the
  overlap is in the likelihood, and the prior would be chosen after the failure); new terms (separation has value only
  with an expert that is right for Blueprint, which is S1's job).
* **Rule for any expert in a candidate (standing from here):** an expert enters only for opponents where we hold real
  code, our own judge cell, or a stand-in accepted by S1's two lines; a stand-in-based expert is capped at weight 0.5
  until live matches exist. Any expert taking more than 10% of the hands of an archive name above 2% of entrant-faced
  seats, without real-code or live evidence for that name, gets that name's archive rows added to a default-routed
  class once (stage B, outcome rows R and S+R), and the stage B lines are read again.
* **Package (`rl/models/v6b.npz`, one file as gs50.npz is):** the gate plus five networks, each asserted by full sha256 of
  its source file before the build: fb2-900 (default) f7a29a39d1bedf08c9c52129205f72af2f73c5bfd59c25de5443629dd088c7d3,
  C1 97f051f381aaaae130072c2cbd010b236e0cfffd798fe111d5e1b08d0b2d0ed9, br_chipzen
  666a436345eb5fd7180a886916c6200a35632ab3fe10c441ee6da09359048989 (both as `tools/g0_build.py` TEACHER_SHA, the files
  gs50.npz was built from), br_ashwing b247feb2e7c15e767fda96c5a654fa36243916083ba263af5f7a34ed6aeb80d6, br_autofast
  08575045b55952d6b37ae8cfa8910442cde918328089fe257db6fe76cdcbbc45 (E2's literals). T1 is not in the file. The gate file
  carries an explicit class-to-expert map (`gs_class_expert`, one entry per class: an expert name or `default`); the
  runtime reads the map, never the class position, and refuses a file whose map names a network the file does not hold.
  Class-to-expert map, literal: small_ball to C1, chipzen to br_chipzen, ashwing to br_ashwing, autodidact to
  br_autofast, solver_like (and `solver_bp100`, `solver_arch`, `field_extra` if stage B adds them) and population to the
  default.
* **Envelope:**
  * Owners and bases: `v6-root` continues from 562cb58 (runtime: the map-driven `gs_route` with four experts, the
    five-network builder, packaging; T1 removed from the v6b path, v5's gs50.npz still loads and routes as before);
    `v6` continues from e23e5a9 (drivers, readers, judge, tests, plants); `v6-rl` continues from 79dc09a (fitter and
    stage A logger). Every commit is pushed to `origin` and `archive`. Box: `~/v6-run/b` (code copies `code-root`,
    `code-x2r`, `code-rl` with their `.commit` files, markers, gate files), stage A rows in one directory
    `~/v6-run/b/a/rows/<actor>/<name>/` with actors `fb2` and `v5`; stage C rows `~/v6-run/b/c/`; stage D
    `~/v6-run/b/d/` and the league run `~/poker-ai-lab-league/out/v6b/`. V6's `~/v6-run/a` is read only.
  * Seeds: 94 and 122 to 126 are E2's registered lines (`94 E2 read`, `121 E2 read` to `126 E2 read`), read here under
    E2's registration; the driver greps the registry for exactly one line each before stage A. Seed 128 is used only if
    stage B's standing rule fires: the driver then copies the registry to `~/v6-run/b/seed_registry.pre-v6b` (once),
    appends `128 V6b draw`, and greps for exactly one such line before the draw. Stage D's E1 pairs 200 to 399 and the
    head to head use C1v5's league keys unchanged (no seed).
  * Writes and rollback: commits on `v6-root`, `v6`, `v6-rl` (revert, including the T1 removal on `v6-root`);
    `~/v6-run/b` and `~/poker-ai-lab-league/out/v6b/` (delete); registry line 128 if written (remove that line; the
    pre-copy is the reference); the package `~/build-rl/holdem-v6b.tar.gz` (delete); after stage B one `train-essentials`
    commit with the gate file, its sha256 and the class row hash lists (revert).
  * Budget, hard cap at twice, each from a smoke on the real path before the stage (a scaled estimate over twice the
    number does not start the stage): stage A 60 minutes, B 20, C 150, D 60. Cores 0-17 only; the driver stops a stage
    when swap use on gb10-d rises above 12 GiB (gb10-d is shared with bench containers).
  * Stops: any count, floor, parity or hash assertion that fails stops the stage and returns it to the roadmap agent; a
    run interrupted by a recall or any outside stop is discarded whole and rerun in a fresh directory (the driver
    refuses a non-empty one); each stage's result is pushed to research and `restore.md` updated before the next stage
    starts (a `.pushed` marker per stage gates the next, as in V6).
  * Non-goals: no training, no new expert, no change to v4, v5 or the account, no fetch from chipzen.ai.
* **Stage A, logging (E2 Stage 2, amended):**
  1. Cells: ext:ashwing, ext:ashwing_search, ext:autodidact, ext:autodidact_fast, each under both actors fb2-900
     (`rl/models/fb2_it000900.npz`, f7a29a39...) and v5 (`rl/models/gs50.npz` of b14b176, f7d22324a4e7dcff00ebf67985702d1f98e1b26f443be50acfbd5c060a6891e6),
     seed 122, exactly 500 matches per cell (250 pairs, both hero seats, pair numbers as G0b's logger), eight cells,
     raw counts and action histories as G0b step A. No 300-match fallback: a smoke whose scaled estimate is over 120
     minutes stops the stage.
  2. Bands by pair number, the same for every cell and actor: pairs 0 to 149 fit, 150 to 199 calibration, 200 to 249
     held out. (E2 Stage 2 had fit 0 to 199 and held out 200 to 249; the calibration band is taken from E2's fit band
     so the new classes enter the temperature choice; held out is unchanged.)
  3. Row checks (E2 Stage 1's, carried over; the reader, with plants): every cell exactly 500 rows with distinct keys;
     the fb2 and v5 cells of a name have equal key sets; each cell's run log names the actor's asserted sha256 and the
     root commit; every row has a non-empty action history and per-hand term counts. A short, duplicated, mismatched or
     wrong-hash cell is void: it is played once more whole on seed 122 in a fresh directory; a second void stops stage A.
  4. Hand floors (checked at the end of stage A, before stage B): per name and actor, the held-out pairs' hands at 11 and
     later at least 300, else stage A stops; per name and actor, the calibration pairs at least 300 hands in all.
* **Stage B, gate fit and offline lines:**
  1. Classes and priors, literal, in this file order: small_ball 0.10 (C1), chipzen 0.05 (br_chipzen), ashwing 0.05
     (br_ashwing), autodidact 0.05 (br_autofast), solver_like 0.30 (default), population 0.45 (default); sum 1.00.
     Fit rows (match-end counts, as G0b): small_ball, chipzen and population from G0b's fit-labelled pairs in
     `~/g0b-run/data/fit/{fb2,g50}` (population: the league:* and gen:* cells, as v5); solver_like from G0b's
     fit-labelled bp100 pairs (both actors) pooled with the fit band of V6's seed 127 draw (Blueprint 500 matches,
     NashForge 280) in `~/v6-run/a/terms/terms.jsonl`; ashwing from stage A's fit pairs of ext:ashwing and
     ext:ashwing_search, autodidact from those of ext:autodidact and ext:autodidact_fast, both actors pooled.
  2. Pinned inputs, asserted before the fit (a mismatch stops): `tools/v6_g0b_rows.sha256` (G0b fit rows, unchanged from
     V6); a new committed `tools/v6b_inputs.sha256` listing `~/v6-run/a/terms/terms.jsonl`
     f6736310ea7e97212166c386dcb1df6a3259d9b1a16c43a65332bf88afa3e501, `~/v6-run/a/terms/drawn.json` and
     `~/v6-run/a/shadow/rows.jsonl` (their sha256 taken once by the build from the box files and committed), and every
     row file of `~/g0b-run/data/eval/{fb2,g50}`; band counts asserted literal: Blueprint calibration 250, held out 250,
     fit 500; NashForge 140, 140, 280. Stage A's own rows are listed with sha256 by stage A's reader and the list is read
     back before the fit.
  3. Temperature: chosen on G0b's grid (0.05 to 1.00 in steps of 0.05) by the least summed weighted negative
     log-likelihood of the true class over these calibration rows only: G0b's calibration-labelled pairs of bp100
     (true class solver_like), small_ball, chipzen and the population cells, both actors, weighted by the hero's
     decisions per hand; the calibration band of the seed 127 draw (Blueprint and NashForge, true class solver_like),
     weighted by the decisions of the seat facing the name; stage A's calibration pairs 150 to 199 (true class ashwing or
     autodidact), both actors, weighted by the hero's decisions. Fit-band and held-out rows never enter (asserted per row).
     Threshold 0.50, ramp 0.15, support test (alpha 0.01, at least 3 trials) on every expert class, as v5.
  4. Lines. "Routed" means an expert other than the default has weight above 0. Buckets hands 1 to 10, 11 to 40, 41 and
     later; a bucket with under 300 hands for a source is pooled into the bucket before it; a dry run prints every
     line's per-source, per-bucket hand counts before the fit. No judging line reads a fit or calibration row of any
     class in the fit being judged (asserted per row across every class's bands, seed 127, stage A, G0b and, in fit 2,
     seed 128 alike; an assertion failure is STOP_V6B).
     Before any line, the cross-tree runtime test (tests and plants, item 2) runs on the fitted gate; a failure stops
     stage B (STOP_V6B).
     a. Solver sources, at most 10% routed in every bucket, per source: Blueprint and NashForge on the seed 127
        held-out band (a name with under 300 held-out hands in hands 1 to 10 stops stage B); the 400 `bot:Blueprint`
        shadow keys replayed by `tools/v6_shadow.py` with the stage B gate beside the actor (each replayed row equal to
        E1's or the shadow source is void and not judged; under 300 hands in hands 1 to 10: reported, not judged);
        G0b's test-labelled bp100 pairs, under fb2 and under g50 separately. Sources for the outcome table: bp100 (either
        actor), Blueprint (archive or shadow), NashForge.
     b. New classes, per member name and actor (fb2, v5), on stage A's held-out pairs 200 to 249: at hands 11 and later,
        pooled, at least 50.0% of hands with the right expert's weight above 0 (ashwing names: br_ashwing; autodidact
        names: br_autofast).
     c. Old classes, per actor (fb2, g50), on G0b's test-labelled small_ball and chipzen pairs: the share of hands at 11
        and later with the right expert's weight above 0 (C1, br_chipzen) under the stage B gate is not more than 5.0
        points under v5's gate (gs50.npz) on the same rows.
     d. Misroute, per cell and actor (fb2, g50), at most 10% routed in every bucket: G0b's eval rows of tight_sticky,
        sticky_overbettor, small_ball_b, never_fold_pre, raise_station, loose_passive, ext:ashwing_hive and ext:wolf in
        `~/g0b-run/data/eval/{fb2,g50}` (200 matches each), and the test-labelled pairs of the gen:0 to gen:59 cells in
        `~/g0b-run/data/fit/{fb2,g50}` pooled per actor. Under 300 hands in hands 1 to 10: reported, not judged.
     e. Standing rule: item 5's walk (`tools/r5_arena.py route`) over A0's snapshot with the stage B gate through the
        `v6-root` runtime, for the names above 2% of entrant-faced seats, literal and asserted equal to the list
        `r5_route.json` gives: Blueprint, fermat6, NashForge, hoops, mr_hide, r0ckGarden, PluriBot, slopBot,
        WSmithSimLab. Per name, all its hands pooled; seed 127 fit and calibration matches excluded. A name fires when
        any one expert has weight above 0 on more than 10.0% of its hands (none of the nine has real-code or live
        evidence for any expert). Also reported, no line: every other A0 name's routing and Ashwing_v3 and
        AutodidactInnovations to their experts.
  5. Remedies (each at most once, applied together in fit 2): split, solver_like replaced by `solver_bp100` (G0b bp100
     rows) and `solver_arch` (Blueprint and NashForge rows) at 0.15 each, both default; field_extra, a default class at
     0.05 (population 0.45 to 0.40) fitted on the fired names' archive matches drawn with seed 128 (Blueprint and NashForge
     are already in solver_like: either firing is STOP_V6B and never enters field_extra, so no seed 128 band can hold a
     seed 127 match) by V6 stage A item
     1's procedure (per name sorted by match id, `numpy.random.default_rng(128).permutation(n)` per name in the list
     order above, first min(n, 1,000), index mod 4: 0 calibration, 1 held out, 2 and 3 fit; matches where both seats
     are fired names dropped and counted; a fired name with under 120 held-out matches stops), its calibration band
     entering the temperature choice and its held-out band the only rows line (e) reads for that name in fit 2.
  6. Outcome table, literal (STOP_V6B returns the table to the roadmap agent; nothing goes to stage C):

     | fit | condition | action |
     |---|---|---|
     | 1 | (a), (b), (c), (d) hold, (e) fires for no name | PASS: the gate goes to stage C |
     | 1 | (b), (c) or (d) fails, whatever (a) and (e) show | STOP_V6B |
     | 1 | (b), (c), (d) hold; (a) fails on one source; (e) fires for no name | fit 2 with the split |
     | 1 | (b), (c), (d) hold; (a) fails on two or three sources; (e) fires for no name | fit 2 with the split |
     | 1 | (a) to (d) hold; (e) fires for one or more names, none of them Blueprint or NashForge | fit 2 with field_extra over the fired names |
     | 1 | (b), (c), (d) hold; (a) fails; (e) fires, not for Blueprint or NashForge | fit 2 with the split and field_extra |
     | 2 | (a) to (d) hold and (e) fires for no name | PASS: the gate goes to stage C |
     | 2 | any of (a) to (d) fails | STOP_V6B |
     | 2 | a name added to field_extra still fires | STOP_V6B |
     | 2 | (e) fires for a name not in field_extra | STOP_V6B |
     | 1 or 2 | (e) fires for Blueprint or NashForge | STOP_V6B |
     | 1 or 2 | a per-row band assertion, an input hash, a floor stop or the cross-tree test fails | STOP_V6B |

     After a PASS the gate file, its sha256 and the row hash lists go to `train-essentials`.
* **Stage C, judge, registered before any play, one arm (v6b), fresh fb2-900 arms on the same keys:** eligibility on B1's
  screen (seed 94, pairs 400 to 499, 78.0% filter) and ten validation styles (drawn on 123, played on 124) as G0b;
  ineligible stops. Confirmation on seed 125 across every C1v5 item 9 cell (bp100 included, 4000 matches; the six
  rule bots 2000 each; small_ball and chipzen 2000 each; ext:ashwing, ext:ashwing_search, ext:ashwing_hive,
  ext:autodidact, ext:wolf 1000 each) plus ext:autodidact_fast 1000; twenty new generated styles drawn and played on
  seed 126. GUARD: no cell under -2.0 with its upper bound under zero (hive and wolf included); the twenty styles pooled
  lower bound above -2.0, none under -5.0 with its upper bound under zero. NEW: lower bounds above +8.0 on ext:ashwing,
  +7.7 on ext:ashwing_search, +6.7 on ext:autodidact. KEEP: small_ball lower bound above +11.0; chipzen reported
  against +5.10. A NEW or KEEP miss with GUARD holding is recorded and the candidate proceeds (at worst v4 on those
  cells); a GUARD failure stops. Counters: one fault-counter record per counted run, read fail-closed as C1v5.
* **Stage D, candidate:** C1v5 steps 1, 3 and 4 unchanged (step 2's fresh confirmation is stage C): deployment check
  (limits, purity, live-format parity for the gate inputs on the 330 replays and 2,000 engine matches, the size-record
  guard, the fault counter, latency at 0.5 vCPU, sha256 list equal across context, image and export), E1 on league pairs
  200 to 399 (23 opponents, 400 matches each, 80% each) and the head to head over 102b05e (400 matches, Wilson lower
  bound above 50%), then the card and a fresh outcome verifier, then Wayne for the swap yes. Card in plain words: v6b
  applies an expert only where we hold the opponent's real code or our own judge cell; against the solver names and
  every other live name it plays as v4; v5's bp100 gain is given up on purpose; v6b is meant to replace v5 on the
  account because v5 would play T1 against Blueprint on about 38% of hands with no evidence that it helps.
* **Tests and plants (committed with a plant runner per branch; every plant caught before launch):**
  1. `v6-rl`: the six-class prior vector literal and summing to 1.00 (and the split and field_extra vectors); class
     rows per class from the named sources only (a D4 name or a held-out pair in the fit fails); the band split by pair
     (149 fit, 150 calibration, 199 calibration, 200 held out); the temperature rows (a held-out or fit row entering
     fails; per-decision weights); the input hash lists (one changed row file, one changed terms.jsonl, wrong band
     counts fail); stage A row checks (499 rows, a duplicate key, unequal key sets between actors, a wrong actor hash,
     an empty action history, a non-empty cell directory).
  2. `v6-root`: the class-to-expert map literal with T1 absent (a file naming T1 or a missing network is refused); the
     five literal sha256 values in the builder (one byte changed in any source fails); gs50.npz still routes exactly as
     before on C1v5's 330 replays (parity with r3.json); an L6-form cross-tree test: stage A held-out rows plus G0b's
     test-labelled small_ball and chipzen pairs, both actors each, replayed through the `v6-root` runtime give class
     posteriors and per-expert weights equal to the fitter's within 1e-9, with, over that pooled set, at least one
     decision where each of the four expert classes has weight above 0 and one where solver_like's posterior is above
     0.50 with all expert weights 0 (plants: ashwing mapped to br_autofast, solver_like mapped to C1, the map read by
     position). It runs twice: before launch on a synthetic fixture gate with fixture rows, and in the stage B driver
     step on the fitted gate and the real rows, after the fit and before lines (a) to (e); each plant fails both runs.
  3. `v6`: thresholds at 10.0% (holds) and 10.1% (fails) for lines (a), (d) and (e); 50.0% (holds) and 49.9% (fails)
     for (b); 5.0 (holds) and 5.1 points (fails) for (c); the bucket pooling and the floors (stage A's 300-hand floors,
     line (a)'s stop at 299 archive hands, the shadow and line (d) not-judged branches at 299); the void shadow branch;
     the nine-name list against a fixture `r5_route.json` (a tenth name above 2% fails); every row of the outcome
     table, including the split on one source and on two, field_extra on one name, both remedies together, and each
     fit 2 stop; the seed 128 draw (literal order, both-seats-fired dropped, the 120 floor) and its registry line
     written only when (e) fires; a fixture where Blueprint fires ends STOP_V6B with no seed 128 draw; a plant putting
     one solver_like fit match into field_extra's held-out band fails the per-row assertion; stage C's GUARD, NEW and KEEP lines at their bounds; the driver's fresh-directory
     refusal, `.pushed` gating, fail-closed steps under pipefail, the budget stop from a planted smoke estimate over
     twice the number, and the swap stop.
* **S1 beside it (spare cores, its own spec later):** solver image variants at each setting the image exposes, 300
  logged matches each against fb2-900. A variant is a stand-in for a name when (1) its A0 distance to the name is at
  most 0.17 and (2) on the gate's 14 terms its held-out rows route to a class fitted on that name's archive rows on at
  least 50% of hands at 11 and later. A variant passing both gives a teacher worth training and a class that tells it
  from bp100; none passing closes the offline route to the solver class.
* **Review record:** plan review 1 REVISE (2026-11-27), five blockers: (1) temperature rule and calibration rows not
  fixed, no hash list of the seed 127 rows; (2) no literal stage B outcome table, the standing rule's class, prior,
  rows, seed and band, line (e)'s rows; (3) stage A rows (500 per name and actor, E2's row checks, hand floors, actors
  for (b) and (c), one row directory); (4) base commits and the writes and rollback list; (5) an enumerated test and
  plant list. Revised (this text): Stage B items 2, 3, 5, 6 and line (e); Stage A items 1 to 4; the envelope; the tests
  and plants list. Plan review 2 REVISE (2026-11-27), two blockers: (1) a seed 128 draw for Blueprint or NashForge would
  overlap seed 127's bands and the per-row assertion's scope was unstated; (2) the cross-tree test's rows could not give
  C1 or br_chipzen weight and its timing against the fitted gate was unstated. The cap of two is reached; fixed
  first-hand (Blueprint or NashForge firing is STOP_V6B, the assertion spans every class's bands, the test adds G0b's
  small_ball and chipzen pairs and runs on a fixture gate before launch and on the fitted gate before the lines).
* **Unverified at writing:** whether solver_like's three sources form one coherent class; whether chipzen-like bots
  play in the arena (br_chipzen's live value); the solver image's settings; v6b against any live opponent; the hands
  per match against the four stage A names (the floors decide).

### V6. One candidate: the solver names back to the default, plus E2's classes (spec, 2026-11-27; the roadmap agent after 14.54)

* **Why:** 14.54 sends Blueprint (15.4% of entrant-faced seats) and NashForge (6.1%) to the default. The one usable
  clone number agrees: v5 sent T1 at the Blueprint clone on 45.7% of hands and gained -0.25 [-3.89, +3.39], so T1's
  +18.9 on bp100 does not carry to that copy (14.53, 14.36). v5 is uploaded but not entered, so one candidate pays the
  candidate steps once: v6 = the solver-name change plus E2's two classes. Order is set for a recall: the refit and
  its offline lines first (archive only, minutes), the gate file archived, then E2's logging and classes.
* **Envelope:**
  * Owners: V6 supersedes E2's `e2-root` (never created) and continues `e2` as `v6`. Runtime, gate files and
    packaging on `v6-root` from `c1v5-root` b14b176; drivers, readers, tests and plants on `v6` from `r45` 973550f (which
    contains `e2`); the fitter on holdem-rl `v6-rl` from `g0b-rl` 9e413f6. Box: `~/v6-run` (code copies, markers, stage A rows
    and gate files), E2 Stage 2 to 5 rows under `~/v6-run/e2/` (E2 Stage 1's rows stay in `~/poker-ai-lab-x2r/logs/e2/`,
    read only). The `train-essentials` commit is made from `~/v6-run` by the main session.
  * Seeds: 127 `V6 draw`. Before stage A the driver copies the registry to `~/v6-run/seed_registry.pre-v6` (once),
    appends the line, and a dry run greps for exactly one `127 V6 draw`; rollback removes that line only. E2's 94 and
    122 to 126 are already registered.
  * Writes and rollback: branch commits (revert); `~/v6-run` (delete); registry line 127 (remove); the
    `train-essentials` commit (revert).
  * Budget, hard cap at twice, from a smoke on the real path before each stage (a scaled number over the cap means the
    stage does not start): stage A 30 minutes, E2 Stage 2 60, Stage 3 20, Stage 4 150, Stage 5 60.
  * Stops: any count, floor, parity or hash assertion that fails stops the stage and returns it to the roadmap agent;
    a run interrupted by a recall is discarded whole and rerun in a fresh directory (the driver refuses a non-empty
    one); each stage's result is pushed to research and `restore.md` updated before the next starts (a `.pushed`
    marker gates the next stage, as in R4R5).
  * Tests and plants: committed with a plant runner on `v6`; every plant caught before launch, including a planted
    smoke estimate over the cap.
  * Non-goals: no training, no new expert, no change to v4, v5 or the account, no fetch from chipzen.ai.
* **Stage A, the solver_live class:**
  1. Candidates and draw: every A0-snapshot poker match (item 5's population) with Blueprint or NashForge as a seat.
     Matches where both seats are target names (Blueprint against NashForge, or a name against itself) are dropped
     and counted. Per name, sorted by match id ascending; `numpy.random.default_rng(127).permutation(n)` per name
     (Blueprint first, a fresh generator per name), the first min(n, 1,000) kept in that order. Bands by position in
     the drawn order: index mod 4 = 0 calibration, 1 held out, 2 and 3 fit. Floor: at least 120 held-out matches per
     name, else stage A stops (lowered from 150 on 2026-11-27 after the build's dry run counted NashForge at 140 held
     out, 324 of its 884 matches being against Blueprint and dropped; no routing had been computed; the 300-hand
     bucket floor, the real power guard, is unchanged and NashForge's held-out buckets hold 1,341, 3,047 and 1,973).
  2. Rows: a rerun of item 5's walk (`tools/r5_arena.py route --dump-terms`, tracker from `rl/models/gs50.npz` of
     b14b176, output `~/v6-run/a/terms.jsonl`) writing, per drawn match, the 14 term counts after every hand for the
     seat opposite the target name. Fit rows use the match-end counts; calibration rows enter the temperature choice
     over every decision of the seat facing the name, weighted per decision as G0b's calibration pairs are (not per
     hand); held-out rows never reach the fit or the temperature choice.
     The reused G0b fit rows (`~/g0b-run/data/fit/fb2` and `.../g50`) are listed with sha256 in a committed
     `tools/v6_g0b_rows.sha256`, asserted before the fit (plant: one changed row file fails).
  3. Classes and priors in stage A, literal: bp100 0.30, solver_live 0.25 (expert: the default, fb2-900),
     small_ball 0.10, chipzen 0.05, population 0.30 (sum 1.00). bp100 keeps v5's 0.30 so that line (c) isolates the
     effect of the new class; solver_live's mass comes from population. (The roadmap agent proposed bp100 0.10; kept at
     0.30 here so a bp100 change cannot be traced to two causes; recorded as a design call.) Same terms, support test,
     threshold 0.50 and temperature grid as G0b step B.
  4. Runtime: if `Policy.gs_route` cannot map a second class to the default expert, `v6-root` adds that mapping, with
     (i) a test that v5's own gate file still routes exactly as before on C1v5's 330 replays (parity with r3.json), and
     (ii) a cross-tree test in G0b L6's form: held-out Blueprint and NashForge per-hand rows replayed through the
     `v6-root` runtime give class posteriors and per-expert weights equal to the fitter's within 1e-9, with at least
     one decision where solver_live's posterior is above 0.50 (plant: solver_live mapped to T1).
  5. Offline lines, in order. "Routed" means w_k > 0 for any expert other than the default; T1 is reported as a
     column. Buckets: hands 1 to 10, 11 to 40, 41 and later; a bucket with under 300 hands for a name is pooled into
     the bucket before it; a dry run prints the per-name, per-bucket hand counts of every line's rows before the fit.
     a. Archive: on each name's held-out matches, at most 10% of hands routed in every bucket. A name with under 300
        held-out hands in hands 1 to 10 stops stage A.
     b. Own hero, shadow only (nothing plays): Blueprint on the 400 `bot:Blueprint` keys of fb2-900's E1 run replayed
        with the stage A gate evaluated beside the actor (R4's recorder, each replayed row equal to the E1 fb2-900 row,
        or the source is void and (b) is not judged). R3's 330 replays are public matches between other bots, not
        ours (corrected 2026-11-27), so they are not an own-hero source; NashForge has no own-hero rows and is not
        judged by (b). At most 10% routed in every bucket. Under 300 hands in hands 1 to 10: reported, not judged.
        No judging line reads a match from the fit or calibration band (asserted per row).
     c. bp100: the held-out bp100 pairs of G0b step A, under each of its two logged actors (fb2-900 and G50, the test-labelled
        bp100 rows in `~/g0b-run/data/fit/<actor>/bp100`), with both v5's gate file and the stage A gate evaluated offline on the same rows; the
        share routed to T1 at hands 11 and later, pooled over those hands, per actor, not more than 5.0 points under
        v5's. A row set whose actor label is not fb2-900 or G50 fails a test.
     d. Outcomes: (a), (b) and (c) hold: pass. (a) and (b) hold and (c) misses by more than 5.0 but at most 10.0 points
        on either actor: pass with the bp100 price recorded; E2 Stage 3 line 4 then compares bp100 with stage A's share
        instead of v5's, and Stage 4 drops KEEP's bp100 line (bp100 stays a GUARD cell). (c) misses by more than 10.0
        points: stop. (a) or (b) fails: fit two classes once (Blueprint and NashForge apart, 0.125 each) and rerun (a)
        to (c); a second failure of (a) or (b) stops V6 and returns it to the roadmap agent.
  6. Reported, no line: routing after the refit for fermat6, MonteCarlo, PluriBot, mr_hide, DeepStack, Chatterbox
     and R3's 330-replay names.
  7. Known limit, on the record: archive counts come from other heroes and the class rows from fb2-900 and G50 (14.47
     showed the hero moves counts); line (b) is the own-hero check we can run without live play, and it is a shadow,
     not v6 playing.
  8. Tests and plants: the literal draw over a fixed candidate list, including one Blueprint-against-NashForge match
     and one Blueprint-against-Blueprint match (both dropped); the four-band split with no match in two bands; the
     120-match and 300-hand floors and the (b) not-judged branch at 160 hands; the bucket pooling; held-out rows
     reaching the temperature choice; the literal prior vector summing to 1.00; the reused-row hash list; both runtime
     tests and their plants; lines (a) and (b) with 10.1% to br_chipzen and 0% to T1 failing; line (c) at 5.0, 5.1,
     10.0 and 10.1 points per actor; every branch of (d).
* **E2 Stage 1's verdict decides the continuation (one path each):**
  * `CONTINUE both`: E2 Stages 2 to 5 as below.
  * `CONTINUE ashwing only` or `CONTINUE autodidact only`: Stages 2 to 5 for that family only; the empty family's 0.05
    stays in population.
  * `STOP E2`: no Stage 2; Stage 3 refits nothing new and uses stage A's gate as v6's gate (its lines 2 and 4 for the
    families drop; line 3 misroute and line 4 for the old classes and solver_live still apply); Stage 4 without its
    NEW lines; then Stage 5.
* **Then E2 Stages 2 to 5** as written in "### E2.", owned as in the envelope above, with these changes: Stage 3 fits
  all classes with stage A's priors (families at 0.05 each
  taken from population, which goes to 0.20) and the solver_live rows; Stage 3 line 4
  also covers solver_live (its held-out share routed not more than 5 points above stage A's); the stage A (d)
  comparator switch applies; the v6 card carries one line saying the headline measures gain on bp100 itself and is
  not an estimate of arena gain.
* **Review record:** plan review 1 REVISE (rows lacked per-hand counts and a calibration band, line (a) could pass
  on empty buckets and bounded T1 only, no own-hero check, priors summed to 0.90, branch (c) clashed with E2 Stage 3,
  two owners for Stages 2 to 5, no smoke, plant runner or registry copy); revised. Plan review 2 REVISE (no v5 rows on
  G0b's bp100 pairs, line (b) would stop on NashForge's sample, matches with both names, no path for each E2 verdict,
  no positive runtime test, the bp100 prior cut confounded line (c) and the price branch was unbounded, no fitter commit
  or row hashes); the cap of two is reached, fixed first-hand on 2026-11-27 (this text). Build verifier 1 REFUTED
  (line (b) read R3's third-party replays as own-hero rows, including fit and calibration matches; calibration weighed
  per hand, not per decision); fixed in the text above and in the build. Build verifier 2 REFUTED (the threshold 0.50, the
  support test and the gate feeding line (c)'s v6 count were not pinned by any test); the cap of two is reached, fixed
  first-hand: `v6-rl` 79dc09a pins threshold and support in `route_rows`, `v6` e23e5a9 moves line (c)'s counts into a
  tested function; on gb10-d v6 52 tests and 92 of 92 plants, v6-rl 21 tests and 42 of 42 plants.
* **After V6:** S1, the solver stand-in family (run the solver image at each setting it exposes, 300 logged matches
  each against fb2-900; a variant is a stand-in for a name when its A0 distance is at most 0.17); live play, which is
  Wayne's to start. Parked: lookahead, clone-trained experts, more style pooling.
* **Unverified at writing:** whether `gs_route` can map two classes to the default; whether NashForge has 1,000
  complete archive matches; E2 Stage 1's verdict.

### R4R5. Is T1 routing a liability on live names? (spec, 2026-11-27; the roadmap agent after R3)

* **R3 result (reported only, ~/e2-run/r3.out on gb10-d, C1v5's 330 replays):** E2's target names are about 3.6% of
  seats (Ashwing_v3 0.8%, Ashwing_v2 0.2%, AutodidactInnovations 2.7%), so E2 is worth about half a point of field
  win rate. v5's gate already sends T1 against live names it was never measured on: Blueprint 60.0% of hands,
  MonteCarlo 64.6%, Shuck1e1 82.6%, allin_v8 80.6%, cutewalrus 73.6%, MARK2R 51.3%, Awika-v7 40.9%, Chatterbox
  30.0%. Routing is not gain: T1 is a best response to bp100, and 14.33 priced a wrong expert at 12 to 18 points.
  The largest default-routed names (Kimiko 7.7%, DeepStack 7.6%, PoetAndCoder 6.8%, MercuryRetrograde 6.5%,
  Fabulous 6.1%, qwentom-leap 5.5%) go almost all to the default.
* **E2 rescoped:** Stage 1 finishes and its matrix is recorded (it fixes class membership); Stages 2 to 5 do not
  run as their own slice. The two classes ride along in the next candidate.
* **Facts checked on gb10-d (2026-11-27):** C1v5's E1 run `~/poker-ai-lab-league/out/c1v5/verify-rl-v5/results.jsonl`
  and the earlier `~/poker-ai-lab-league/out/verify-fb2-900/results.jsonl` each hold 9,600 rows on the same 9,600
  (opponent, pair, seat) keys, pairs 200 to 399, 400 per label, with the same match seed per key in both. The 24 labels
  are `arch:0` to `arch:5` (archetypes), `base:station`, `base:maniac`, `base:nit`, `base:random`, `base:reference`,
  `base:lag`, `base:station_raiser`, `cand:chipzen-102b05e`, and ten clones of archive names: `bot:Blueprint`,
  `bot:Kimiko`, `bot:AutodidactInnovations`, `bot:SolvencyCheck`, `bot:DeepStack`, `bot:mr_hide`,
  `bot:MercuryRetrograde`, `bot:qwentom-leap`, `bot:InfernalMonarch`, `bot:PoetAndCoder`. The clone map is the label
  itself (`bot:<name>` is the clone of archive name `<name>`, built by `league/clone.py` in `~/poker-ai-lab-league`).
  Neither results file holds routing counts or hands. 14.51 puts every E1 paired difference within -1.5 to +0.5
  (`bot:Blueprint` -0.2 [-3.9, +3.4]), so R4 has little power. The archive `~/chipzen-replays` holds per-action
  records. Style vectors: A0's eight axes (`tools/style_map.py`, each in [0, 1], a missing axis read as 0.5), distance
  Euclidean, field vectors `~/poker-ai-lab-x2r/logs/a0/vectors.json`.
* **Order:** R5 item 5 (routing on the archive), then R4, then the validity check, then R5 items 2 to 4 only if the
  check can pass, then the rule table.
* **R5 item 5, routing on the archive (runs first):** v5's gate walked over every archive poker match by C1v5's
  replay reader and conformance filter, asserting 16,099 poker matches (A0's snapshot: archive files with mtime up to 2026-11-25 13:24:17 +0800, 20,421
  files; the archive now holds 37,963 poker matches, not used, so the read stays on A0's population) and printing hands accepted and rejected per
  name. Parity first: on the 330 matches shared with C1v5's population, the per-name routing shares equal r3.json
  exactly, or R5 stops (plant: a perturbed gate input breaks it). Output per name: entrant-faced seat share (A0's
  filter) and routing shares. The target list is fixed from it: every name with T1 share of 25% or more here or in R3.
* **R4, the ten `bot:` clones under v5:** the reader asserts the label list literally (a label outside the 24 fails;
  only `bot:` labels map to names).
  1. Paired gain per clone: v5 `a_win` minus fb2-900 `a_win` on the same key, 400 keys, mean with a Wald 95% interval
     on the paired differences (z 1.96); 9,600 rows per file, identical key sets and seeds asserted.
  2. Routing: v5 replayed on the ten clones' 4,000 keys with a recorder, a wrapper in `tools/r4_clones.py` around
     `Policy.gs_route` of an unchanged root copy of `c1v5-root` b14b176 (per-file hashes asserted equal to the
     archive's before and after; root commit in every run log). Parity: each replayed row's `a_win`, `a_chips` and
     `hands` equal the E1 row, or that clone is void; more than 2 void clones void R4.
  3. A clone's R4 reading is usable for a name only when the clone is not void and its recorded T1 share is above 25%.
* **Validity check (licenses R5's style pooling):** counted clones are usable R4 readings whose interval excludes
  zero. Pass needs at least 5 counted clones and the pooled sign (item 4 below, applied to the clone's archive name)
  agreeing with R4's sign on all of them when there are 5 to 7, or on all but one when there are 8 to 10 (chance pass under random signs at most 9/256 = 3.52%, at 8 clones, asserted exactly by a test). Under 5 counted clones: fail without running items 2 to 4,
  and R5 gives no A, B or D for any name.
* **R5 items 2 to 4 (only when the check can pass):** per target name, every opponent with at least 20 archive matches
  against it (opponents absent from `vectors.json` dropped and counted); T1 and fb2-900 vectors played against the ten
  `bot:` clones, 25 matches each on seed 127 (registered `127 R5 read` only then); each opponent to the nearer of the
  two, dropped when the distances differ by under 0.05 or both exceed 0.35; per pool at least 3 distinct opponents and
  none above 50% of the pool's matches; difference T1-pool minus fb2-pool with a 95% interval from 2,000 bootstrap
  draws over opponents (seed 127).
* **Decision rule, one outcome per name:**
  * A target name (T1 share 25% or more in item 5 or R3):
    A. LIABILITY: its usable R4 clone's upper bound under zero, or (check passed) its R5 interval's upper bound under
       zero with the pool bars met. Action: v5.1, the gate refit with that name's real archive counts in the
       population class; C1v5's steps again before it replaces v5.
    B. SUPPORTED: not A, and its usable R4 clone's lower bound above zero, or (check passed) its R5 lower bound above
       zero with the pool bars met. Keep, recorded.
    D. NEUTRAL: not A or B, check passed and the pool bars met. Keep, recorded.
    C. NO EVIDENCE: everything else. Seat share above 2% (item 5, entrant-faced): treated as A. Otherwise kept.
  * Any other name: not judged, kept, reported.
  A and B cannot both hold, since B requires not A.
* **Stops:** any count, key, seed or parity assertion that fails stops that read and returns it to the roadmap agent;
  the void cap above; a run interrupted by a recall or any outside stop is discarded whole and rerun in a fresh
  directory, which the driver refuses to reuse when non-empty. Each read's output is pushed to research and the
  `restore.md` state line updated before the next starts.
* **Envelope:** branch `r45` from `e2` ddd487a (`tools/r4_clones.py`, `tools/r5_arena.py`, `tools/r45_drive.sh`,
  tests and plants with a committed plant runner); box dir `~/r45-run`; outputs `r5_route.json`, `r4.json`,
  `r5.json`, printed tables. Cores 18-19 while E2 Stage 1 runs, then 0-17. Expected and hard caps: item 5 about 40
  minutes (cap 90), R4 replay about 30 (cap 60), items 2 to 4 about 20 (cap 45); a smoke on the real path first (item
  5: 200 matches; R4: 40 keys; item 3: 2 matches per clone), scaled; a scaled number over the cap means the read does
  not start and returns to the roadmap agent. Writes: branch commits (revert), `~/r45-run` (delete), registry line
  `127 R5 read` if used (remove). Tests and plants: the label list (an outside label, a non-clone mapped); the paired
  reader (a missing key, a seed mismatch, 9,599 rows); routing parity (one changed row voids a clone, 3 voids void
  R4); a changed root file; item 5's parity; the validity check (zero-mean noise with intervals across zero fails;
  the chance pass rate asserted at most 3.5%); pooling (overlapping pools come out disjoint; equal style with
  different strength; a single-opponent pool of 150 matches gives no A or B; an opponent missing from vectors.json is
  dropped and counted); the rule table enumerated over (R5 above, across, below zero, pool bars unmet) x (R4 usable
  above, across, below, unusable) x (check pass, fail) x (share above or below 2%) x (T1 share 24.9% or 25%), one
  outcome per cell; the 16,099 and 9,600 assertions; an interrupted run; a non-empty output directory; a planted
  smoke estimate over the cap. Non-goals: no training, no gate refit (v5.1 is its own slice), no change to v5 or the
  account, no fetch from chipzen.ai.
* **Review record:** plan review 1 REVISE (no outcome for the middle band, R5's pooling not a valid stand-in without a
  check, item 5 unguarded, stops and recall handling, recorder ownership and budgets); revised. Plan review 2 REVISE
  (the E1 labels are not 24 clones, the validity check passes on noise, R4 used without T1 routing, pooled intervals
  ignore clustering, names without an outcome, no hard cap); the cap of two is reached, fixed first-hand on
  2026-11-27 (this text).
* **Map for the slice after:** for the large default-routed names, a counter-style with pooled win rate of 65% or
  more on at least 100 matches makes the name an expert target; its clone-trained teacher is accepted only if its
  style vector lies within 0.25 of that counter-style. No such counter-style: the name stays on the default.
* **Candidate after that:** v6 = v5.1's gate changes plus E2's two classes plus accepted clone-trained experts, one
  pass through C1v5's steps.
* **Unverified at writing:** whether the archive holds per-action records (to repeat R3 with A0's shares) or only
  outcomes and style counters; whether enough opponents sit near T1's style to reach 100 matches; whether E1's logs
  hold routing counts; Blueprint's true share (5.0% in R3, 15.4% in A0).

### C1v5. Candidate slice: GS50 as the entered bot (spec, 2026-11-26; tier 1, a candidate; the roadmap agent's decision after 14.50)

* **Question:** does v5 = GS50 (the gate file `~/g0b-run/students/gs50.npz`, sha256
  f7d22324a4e7dcff00ebf67985702d1f98e1b26f443be50acfbd5c060a6891e6, experts T1, C1, br_chipzen, default fb2-900) plus
  the unchanged all-in answer, packaged as it would be uploaded, keep G0b's read on seeds nothing has touched and pass
  the upload gate?
* **The artifact, one file set:** `c1v5-root` commits the GS50 file as `rl/models/gs50.npz` (`git add -f`, sha256
  above asserted in full by a test) and `rl/bot_v5.py` (`class V5Bot(RLBot)`, which only sets the model path
  `rl/models/gs50.npz` next to it, the B1Bot way; no other logic). The one build command, from that commit, is
  `deploy/build_on_box.sh rl/models/gs50.npz holdem-v5-c1v5`; the one image tag is `holdem-v5-c1v5` (export
  `~/build-rl/holdem-v5-c1v5.tar.gz`).
  The bot file set is every file the Dockerfile copies (`deploy/bot.py`, the `rl/` modules, `allin_v.npz`,
  `tracker_prior.npz`, the model as `weights.npz`, the `nlhe/` files). One sha256 list of that set is recorded and
  must match across the staged context, the image (read back with `docker run --entrypoint sha256sum`) and the league
  export `candidates/c1v5-src` (with `rl/models/gs50.npz` in place of `weights.npz`); the x2r judge loads the same
  commit's files. Any mismatch stops the slice.
* **Counters, on every judged path:** the fault fallback and `gate_faults` live in `rl/runtime.py` (`Policy`), the
  guard and `size_skips` in `rl/runtime.py` (`SizeRecord`), the counter record in `rl/bot.py` (`RLBot`): all files
  the Dockerfile copies, so the image and the judged bot run the same code. The engine and the league runner call no
  match-end hook (`holdem/engine.py` `play_match`), so the record is written where they do reach: `RLBot` draws a
  fresh uuid4 match key in `on_match_start`, and when the env `C1V5_COUNTERS` names a directory, every
  `on_round_result` rewrites `<dir>/<key>.json` with the hand number and the match's running `gate_faults` and
  `size_skips` (write to a temp name, then `os.replace`). Unset (as in the image), it writes nothing and plays the
  same. Steps 2 and 3 set it to a fresh directory under each run's out directory; the driver counts the files, which
  must equal the matches the run played, and sums the two counts.
* **Void and fail:** a nonzero `gate_faults` or `size_skips` total is a failed line (the bot misbehaves) and stops the
  slice. A file count that differs from the matches played (an interrupted or resumed run) voids that run only: it
  is rerun once, whole, on the same seeds and pairs with a fresh counter directory and fresh out directory; a second
  void is a failed line. A resumed `league_fresh.py` run is never counted.
* **Decision it feeds:** all lines pass, a fresh outcome verifier confirms the whole record, then Wayne is asked for
  his own yes to upload and swap (v4 stays entered until then; reversible while the season allows); after his yes and
  the upload, the HF release (private during Season 16). Any failed line stops the slice and returns to the roadmap
  agent; nothing is rerun on a new seed to rescue a line.
* **Design calls (roadmap agent):** ship the gate arm itself, no distillation (the gate reads bet sizes that are not
  among the 56 features; GS50 costs 0.03 ms a move); fresh seeds on every cell that carries the claim (seed 95 has
  informed four designs); one candidate, no backup arm.

**Step 1: deployment check (before any judged match; any failure stops, fix under a new commit, repeat step 1)**

1. Limits (source: the Season 16 registration notes in memory `chipzen-poker-bot`, hosted 0.5 vCPU, 256 MB, 5 s per
   decision, image under 200 MB, non-root): `holdem-v5-c1v5.tar.gz` from the one build command under 200 MB (the
   uploaded form; v4's export of the same base passed);
   peak resident memory under 256 MB in a full match. No new request to chipzen.ai.
2. Runtime purity: the image's site-packages hold no scipy; the gate's Beta-binomial uses `math.lgamma` only. Test:
   import scan of the staged context (`rl/`, `nlhe/`, `bot.py`) lists only the standard library, numpy and chipzen.
3. Parity: the staged context (the exact files the image copies, hashes asserted equal to the image's) plays 200
   seeded matches (40 each of bp100, `small_ball`, `sticky_overbettor`, `chipzen`, `ext:ashwing`) with actions
   identical to `g0b-root` 27773b0 with the GS50 file on the same seeds.
4. Size-record guard (new, in the runtime): `SizeRecord.update` first checks chip conservation for the finished hand:
   per seat, start stack minus end stack (`round_result` `stacks`) plus payout equals the chips the action history
   puts in under the protocol's semantics (a `raise` amount is the street total, a `call` amount the chips added,
   blinds the chips posted; `chipzen_bot/nlhe/history.py`); start stacks from the previous `round_result`, the first
   hand from `match_start`'s starting stack. A hand that fails is not counted in the six size terms and increments
   `size_skips`. Replay population for (b), (c) and item 13: the NLHE replays in `.cache/chipzen-replays` that
   `tools/replay_conformance.py` accepts, 330 matches and 10,516 hands (experiments sections 1 and 2), counts asserted
   literally; other files are out of scope; a hand failing conformance fails the test (never dropped). Tests:
   (a) 0 skips over 2,000 engine matches of mixed cells. (b) Each replay hand is converted to a protocol-form
   history (raise amounts turned from the replay's chips added into street totals) with start stacks, end stacks and
   payouts taken from the replay's own `starting_stacks`, `stacks_after` and `payouts`, never from the engine; fed
   through `SizeRecord.update` it gives 0 skips. Its six counts per match equal an independent reference: the same
   hand driven through `holdem/engine.py` by `replay_conformance.py`'s driver, where for each opponent `raise` or
   `all_in` f = (raise-to minus `max(bet)`) / `pot` read from the engine `Hand` state just before the action,
   bucketed with `GS_EDGES`, counted per street group (plant inside `SizeRecord.update`: the pot without the blinds,
   caught by this comparison). (c) The same replays converted with raise amounts left as chips added skip every hand
   where the two forms differ and count no size from those hands (plant: the guard removed). The guarded runtime
   keeps 14.50's read only if (a) and parity item 3 hold.
5. Fault path: any exception in the gate plays fb2-900's probabilities for that decision and increments
   `gate_faults` (`rl/runtime.py`); the fault-injection test runs through the staged context's `deploy/bot.py` entry
   (`RLBot` on `weights.npz`), not only `V5Bot`, and asserts fb2-900's probabilities and the count. Every judged match records `gate_faults` and `size_skips`; a
   nonzero total in steps 2 and 3 fails the line ("Void and fail" above).
6. Latency: the staged context in an arm64 container at `--cpus 0.5 --memory 256m` over at least 10,000 decisions:
   mean and maximum per decision, maximum under 100 ms; and three full matches of the amd64 image through
   `deploy/run_local_match.sh` (protocol smoke, QEMU timings reported, not judged).

**Step 2: fresh confirmation (holdem-x2r, the judged runtime is step 1's commit)**

7. Seed 118 (`118 C1V5 read`), v5 against a new fb2-900 arm on the same seeds, paired on (seed, hero seat): bp100
   4,000 (queue, `BPQ_SLICE=C1V5`); `small_ball`, `small_ball_b`, `tight_sticky`, `sticky_overbettor`,
   `never_fold_pre`, `raise_station`, `loose_passive` 2,000 each; `chipzen` 2,000 seeded per match as V5b's D3;
   `ext:ashwing`, `ext:ashwing_search`, `ext:ashwing_hive`, `ext:autodidact`, `ext:wolf` 1,000 each.
8. Twenty new styles, a third draw by `tools/v5b_styles.py draw --seed 120 --n 20` (`120 C1V5 read`), V5b's sampler,
   exclusion set and bound, redrawn if equal in every attribute to any style of `~/v5b-run/styles.json` or
   `~/g0b-run/styles_g0b.json`; file `~/c1v5-run/styles_c1v5.json` (sha256 recorded), cells `gen3:<k>`, k 0 to 19.
   Play seed 119 (`119 C1V5 read`), 200 matches each, against a new fb2-900 arm.
9. Lines: B1's rule on seed 118 (headline = B1's judge weights times the paired gains, 95% lower bound above zero; no
   cell under -2.0 with its upper bound under zero); bp100 lower bound above +10.0 and `small_ball` above +11.0; the
   pooled twenty styles lower bound above -2.0 and no style under -5.0 with its upper bound under zero. `chipzen` is
   reported against +5.10 and does not decide.

**Step 3: the upload gate (holdem-league, `tools/league_fresh.py`, the B1 gate path)**

10. E1: `tools/league_fresh.py --name rl-v5 --root candidates/c1v5-src --module rl.bot_v5 --class V5Bot --p0 200
    --p1 400 --h2h chipzen-102b05e --workers 8 --out out/c1v5/verify-rl-v5` with `C1V5_COUNTERS` under that out
    directory (9,600 matches): all 23 at 80% or more over 400 matches each (Wilson lower bounds reported); the paired
    difference against fb2-900 from its verify rows reported; counter totals zero over 9,600 files ("Void and fail" above).
11. Head to head: `--h2h chipzen-102b05e` on the same pairs: Wilson 95% lower bound above 50%.

**Step 4: reported on the card, not gating**

12. bp100 beside the Blueprint clone; opposite signs with both intervals excluding zero is flagged in words.
13. Expected arena effect: the gate run as an observer over item 4's replay population, per entrant-faced name
    (Blueprint, fermat6, NashForge, hoops, mr_hide, r0ckGarden, PluriBot, slopBot), the share of hands routed to each
    expert by hand bucket. If the support test keeps most real names on the default, the card says in those words
    that v5 plays as v4 against most of the live field and gains where an opponent matches an expert.
14. E3 exploit probes as the eval card, the shove table against bp100, decision time, the departure table.
15. The design in plain words for the card.

* **Rule order:** step 1, then item 9, then item 10, then item 11, then a fresh outcome verifier on the whole record,
  then Wayne's yes. No upload, swap or registration by the slice.
* **Seeds:** 118 (confirmation), 119 (style play), 120 (style draw), registered `C1V5 read` after a copy of the
  registry to `~/c1v5-run/seed_registry.pre-c1v5`. League pairs 200 to 399 are the E1 range (never used in
  selection).
* **Owners:** holdem-x2r `c1v5-root` from `g0b-root` 27773b0 (guard, fault counter, staging and image scripts),
  `c1v5` from `g0b` aaa17ad (draw, judge, reader, driver, arena-effect tool); holdem-league for E1 through the
  existing `tools/league_export.sh` and `league_fresh.py`.
* **Tests (each failing on its plant; plant runner committed with them):** items 2 to 5 as stated; the counter path
  (a 10-match `league_fresh.py` smoke with a plant raising inside the gate writes exactly 10 files with nonzero
  `gate_faults`; the same on a 10-match x2r judge cell); the sha256 list check (plant: one file of the export
  changed); `rl/bot_v5.py` holds only the model path; the rule table gives exactly one verdict per combination,
  void included (plants: each line dropped; a nonzero counter gives stop, a short file count gives one rerun, a
  second short count gives stop); literals: seeds, counts, lines, file paths, the GS50 sha256, the one build command
  and tag.
* **Review record:** plan review 1 REVISE (3): 4(b)'s comparison ran both sides through `SizeRecord.update`, so a
  plant inside it could not fail, and the converter's stacks were unsourced; the replay population (412 files, 330
  NLHE) was open; nothing tied E1 to the uploaded files and the league path recorded no counters. Revised: an engine
  `Hand` reference for every opponent raise, replay stacks and payouts from the JSON, the 330 and 10,516 population
  asserted, a committed model path and league class, one sha256 list across context, image and export, and a
  counter file per process summed by the driver. Plan review 2 REVISE (4): no judged path calls `on_match_end`; the
  fallback and counters had no home the image shares; three build commands and tags; "void" had no outcome. The
  review cap of two is reached; fixed first-hand at 2026-11-26 17:05 UTC: a per-match key file rewritten at every
  `on_round_result`, the fallback and counters in `rl/runtime.py` and `rl/bot.py` with the fault test through
  `deploy/bot.py`, one command and tag, and void defined (one whole rerun on the same seeds; counters nonzero or a
  second void stop the slice).
* **Build record:** step 1 PASS (image tar.gz 64.6 MB, peak memory 99 MB, no scipy, parity 200/200 against `g0b-root` 27773b0, guard 0
  skips over 2,000 engine matches and over the 330 replays equal to the engine reference, fault fallback through `deploy/bot.py`, latency at
  0.5 vCPU mean 2.1 ms, max 53 ms). Build verifier 1 REFUTED: the item 9 and gate driver steps kept rc 0 and a stale PASS when the read
  failed (`| tee` and `;`), and 9 test mutations survived; fixed (`c1v5-root` b14b176 tests only, image byte-identical; `c1v5` 712010d).
  Build verifier 2 REFUTED: a PASS could come from rows whose counters were never checked (the judge reused existing rows; the reader
  required no counter record), the slice-end order was untested, verdict-changing literals in `b1_read.py` and the judge were unpinned, and
  the step 2 budget test was flaky; the artifact and parity held. The cap of two is reached; fixed first-hand at 2026-11-26 19:40 UTC
  (`c1v5` 1564a53): the reader stops unless each of the 34 counted v5 runs, and at the gate the league run, has a counter record of the
  right count; item 9's bounds and guard use the reader's own Z 1.96 and -2.0; the judge replays counted cells; the driver refuses a
  non-empty LOGS or league out, removes a PASS verdict beside a failed step and keeps the step order in one function; the step 2 clock is in
  nanoseconds; one plant per surviving mutation (30 new).
* **Result (experiments 14.51): VERDICT PASS, the full upload gate met** (run 2026-11-26 23:03 to 2026-11-27 01:50 UTC from
  `c1v5` 4767f28, 86 tests, 130 of 130 plants): headline +13.21 [+12.00, +14.41], bp100 +18.9 [+17.2], `small_ball` +20.1 [+18.1],
  no guard failure, twenty new styles pooled -0.2 [-0.8]; E1 23 of 23 league opponents at 80% or more over 400 matches (lowest
  `arch:5` 83.25%); head to head over 102b05e 76.25%, Wilson lower 71.8%. Outcome verifier CONFIRMED. The Season 16 swap window
  closed on 23 Nov, so v4 stays entered; on Wayne's word (2026-11-27) v5 is packaged for the account and for Hugging Face.
* **Writes, each with its rollback:** commits on two local branches (revert); gb10-d `~/c1v5-run/`,
  `~/poker-ai-lab-x2r/logs/c1v5/`, `~/poker-ai-lab-league/candidates/c1v5-src`, `out/c1v5/` (delete); registry lines
  118 to 120 (restore the copy); the image tag `holdem-v5-c1v5` and `~/build-rl/holdem-v5-c1v5.tar.gz` on gb10-d
  (remove).
* **Budget (each phase stops at twice its number):** step 1 about 40 minutes, step 2 about 150 (bp100 queue the long
  pole), step 3 about 10, step 4 about 20. Cores 0-17.
* **Non-goals:** no new expert, no retrain, no change to v4 or the deployed bot, no fetch from chipzen.ai, no upload.

### TT. More teachers: single-opponent ceilings where the student has none (spec, 2026-11-25; tier 2)

* **Question:** which further opponents does a specialist beat by a wide margin over fb2-900, so that its play is
  worth distilling into a second student (V5b)?
* **Why:** 14.39 shows the method scales with teachers. 14.37 left open whether `ext:ashwing` and
  `ext:ashwing_search` (one shared profile) share a best response.
* **T-a (reads, no training):** the M1 specialists of 14.12 on disk: `~/poker-ai-lab-rl/ckpt/br_ashwing/latest.npz`
  (it 580, trained on `ext:ashwing`) on `ext:ashwing`, `ext:ashwing_search`, `ext:ashwing_hive`, and
  `ckpt/br_autofast/latest.npz` (it 240, trained on `ext:autodidact_fast`) on `ext:autodidact`; 1,000 matches each,
  seed 95, paired with the fb2-900 rows on disk (`~/poker-ai-lab-x2r/logs/b1/confirm/fb2`, written from holdem-x2r
  8be6e38). Run from that tree, `~/d0-run/x2r` (C0's tree), per cell: `taskset -c 18-19 nice -n 10 python -m
  rl.eval_arena --model CKPT --opp CELL --matches 1000 --seed 95 --workers 2 --rows
  ~/poker-ai-lab-x2r/logs/tt/a/NAME/CELL.jsonl`. The runner refuses to start from any other directory.
* **T-b (training, 60 minutes each):** `tools/rl_br.sh` from fb2-900 against `sticky_overbettor`, `loose_passive`,
  `never_fold_pre` and `chipzen`, 3 SDK workers each, C1's recipe; `loose_passive` is ported into the holdem-rl
  `holdem/opponents.py` STYLES from holdem-x2r (byte-equal class; holdem-rl has the other two). Read, seed 109 (fresh),
  from `~/d0-run/x2r`, for each of the four cells (`chipzen` included: `--opp chipzen` is the heuristic HoldemBot in
  `make_opp`) two arms on the same command: `taskset -c 0-17 nice -n 5 python -m rl.eval_arena --model M --opp CELL
  --matches 2000 --seed 109 --workers 6 --rows ~/poker-ai-lab-x2r/logs/tt/b/ARM/CELL.jsonl`, M the specialist's
  `latest.npz` (arm = its name) and `rl/models/fb2_it000900.npz` (arm `fb2`). Gain = paired difference in match
  win rate points on (seed, hero seat), 95% interval ±1.96 se. `tight_sticky` is left out (C1 found -4.0, no gain).
* **Use (pre-registered):** a teacher whose paired gain has a 95% lower bound of +8.0 or more joins V5b's data after
  V5a reads. V5a does not wait for these and is not changed by them.
* **Placement:** V5a has priority on cores 0-17. T-a runs on cores 18-19 (2 workers) after C0; T-b runs when V5a's
  confirmation is done or in gaps, four runs at 4 processes each (16 cores); its reads (eight arms of 2,000, minutes
  each at 6 workers) after training.
* **Tests:** the port of `loose_passive` is byte-equal to the holdem-x2r class and plays the same actions on 200
  recorded states; the reader's pairing, a missing baseline file fails the read (plant: baseline skipped), the +8.0
  line literal (plant: line moved), seeds 95 and 109 literal. Revised after plan review 1 (baselines, seeds, the
  chipzen read, the read tree); tier 2, one review.
* **Writes and rollback:** `~/poker-ai-lab-rl/ckpt/br_{sticky_overbettor,loose_passive,never_fold_pre,chipzen}`,
  `logs/`, `~/poker-ai-lab-x2r/logs/tt/`, registry lines `95 TT read` (T-a, named baseline B1's fb2-900 rows) and
  `109 TT read` (T-b, both arms fresh); delete to roll back.

* **T-b read (14.41, verifier CONFIRMED):** `br_chipzen` joins V5b (+11.8 [+9.4, +14.1]; the unpaired lower bound
  +9.03 is the recorded basis, T-b is not rerun); the other three do not.
* **V5b inputs (roadmap agent after 14.41):** the `chipzen` opponent in `rl/eval_arena.py` is unseeded
  (`HoldemBot(seed=None)`, no `set_seed`), so its rows do not repeat. V5b's spec seeds it before V5b is built:
  1. `make_chipzen()` gets a `set_seed` that reseeds from the match seed, through the derivation the other seeded
     opponents use (`holdem/arena.py`: `opp.set_seed(pair_seed * 13 + hero_seat)`).
  2. Tests first: two 50-match `chipzen` runs on one seed give identical rows; removing the seeding fails that test;
     `small_ball`, `ext:ashwing` and `tight_sticky` rows (50 matches each) are byte-identical to the 8be6e38 root.
  3. Non-`chipzen` cells keep their 8be6e38 rows; only the `chipzen` cell gets new arms from the new root (fb2-900,
     the V5a student if one is chosen, `br_chipzen`) on V5b's confirmation seed.
  4. Eval path only: teacher data (`ad0_log` through `holdem.arena.run_arena`) needs no `chipzen` seeding (V5b seeds
     it at data time anyway, D3, for repeatable rows).
  5. The gate's heuristic head to head is already seeded per match (checked 2026-11-26: `league/run.py` builds each
     candidate and opponent with `pair_seed * 7` or `* 13`, and `league/bot_host.py` constructs the bot with
     `cls(seed=...)` on every new match), so the gate needs no change.
  6. `br_chipzen` reached +11.8 in 400 iterations; it is not extended now. A longer run follows only if V5b's student
     keeps most of the gain.

### C0. Is fb2-900 a peak on the Ashwing families? (spec, 2026-11-25; tier 1, the roadmap agent's recommendation after 14.38)

* **Question:** do fb2's own neighbouring checkpoints lose to the Ashwing families as B1 and D0 did? If so, fb2-900 is
  a local high and the -2.0 guard sits inside one run's checkpoint spread; if not, D-null separates the old-data
  ratio (D0 ran C engine to old-family SDK about 1:1, fb2 about 6,250 to 10,000) from continued training.
* **Arms (no training, no containers):** fb2's run (`~/poker-ai-lab-rl/ckpt/fb2/`, one run, `train.jsonl` it 1 to 965
  monotonic) it000700 (1b102dbc…), it000800 (10b4cafd…) and latest = it 965 (a8507305…). Baseline: the fb2-900 rows
  on disk (`~/poker-ai-lab-x2r/logs/b1/confirm/fb2`; `ckpt/fb2/it000900.npz` holds the same policy arrays as
  `rl/models/fb2_it000900.npz`, checked). Reported beside them under D0's spec, no rule: D0 it000300 and it001600.
  B1's screen rows hold no ext cell.
* **Cells:** `ext:ashwing`, `ext:ashwing_hive`, `ext:ashwing_search`, 1,000 each, seed 95, from `~/d0-run/x2r`
  (holdem-x2r 8be6e38, the tree of the baseline rows), `rl.eval_arena --model CKPT --opp CELL --matches 1000 --seed 95
  --workers 2 --rows ~/d0-run/logs/c0/ARM/CELL.jsonl` under `taskset -c 18-19 nice -n 10` (AD0 holds cores 0-17;
  Ashwing uses no wall clock, 14.36). `ext:autodidact` is left out (slow; it moved with the others in D0).
* **Read:** per arm, each cell paired with fb2-900 on (seed, hero seat), points of match win rate; pooled = mean of the
  three, se sqrt(sum se²)/3, 95% interval ±1.96 se. Reader holdem-rl d0 `tools/c0_read.py`.
* **Rule (pre-registered), on the three fb2 checkpoints:**
  * **PEAK:** at least two of the three pooled points under -2.0 with upper bound under zero. D-null does not run;
    every future screen includes the three Ashwing cells and `ext:autodidact_fast` at 500 each and selection is among
    checkpoints that hold them; B1's and D0's guard losses are recorded as within the run's own checkpoint spread; P1b
    and any "restore the shares" slice close.
  * **NOT PEAK:** all three pooled points within [-2.0, +2.0] with intervals that include zero. D-null runs as
    specified (D0's command at `--heur-batch 10000`) once AD0's play frees cores 0-17.
  * **MIXED:** anything else. D-null runs only if AD0 lands on its rule 1 (distil, then PPO fine-tune).
  * **Amendment (2026-11-25 22:35 UTC, before C0's read was opened; the roadmap agent's call after 14.39):** D-null does not
    run under any outcome. It separated the old-data ratio from continued PPO, and after AD0's rule 1 neither is on
    the path (the next slice judges the distilled student with no PPO). C0 finishes and is recorded as the
    checkpoint-spread measurement; PEAK's screen line (the three Ashwing cells and `ext:autodidact_fast` at 500 each)
    still applies to future PPO screens if it reads PEAK.
* **Writes:** `~/d0-run/logs/c0/` and `~/d0-run/tools/c0_read.py` (rollback: delete). Nothing else.

### AD0. Can one network hold both specialists and fb2-900, and what does it need? (spec, 2026-11-25; tier 2)

* **Question:** can one policy network reproduce T1 against bp100, C1 against `small_ball` and fb2-900 against the
  rest, and what does that take: nothing new, seeded counts, more width, or both? Supervised fitting to the teachers
  takes PPO out of the answer, which no RL run can.
* **Why (14.37, roadmap agent 25 Nov):** B1 had bp100's identity in its counts for at least 71% of bp100 hands and
  kept 5.4 of T1's 19.9 points; perfect seeding scaled from that lands near +7.6, under AD1's +10.0, so AD1 would most
  likely spend seven box-hours to reach a fail branch. S7 (a wider trunk under the same PPO and mix) could sit at the
  same fixed point (B1's curve was flat from 300 to 2,100), and a null would not tell capacity from optimization.
  AD1 and S7 run only if AD0 points at them.
* **Decision it feeds:** the next slice: distillation then PPO (rule 1), AD1 from the seeded student (2, 6), S7
  (3, 4), or the opponent representation (5, 7). No candidate; students never reach the bot.
* **Teachers (pinned before data, sha256 in the runner):** T1 = the `ckpt/br_bp100` checkpoint 14.31 read (holdem-rl
  `tools/t1_run.sh` at 114a136 names it; latest.npz is 5eb525fb… on gb10-d), C1 = `~/poker-ai-lab-x2r/ckpt/
  br_small_ball/latest.npz` (97f051f3…, 14.30), fb2-900 = `rl/models/fb2_it000900.npz` (f7a29a39…). The network is
  56 inputs, hidden 256 and 256, 6 actions (`pw0` 56x256, `pw1` 256x256, `pw2` 256x6).
* **Seeding (one table for data and play):** only the two specialists' opponents are ever seeded. `rl/models/
  ad0_prior.npz` holds exactly the bp100 and `small_ball` rows of AD1's `rl/models/sdk_prior.npz` (fb2-900's own
  Tracker counts on seed 101, H0 = 40), its sha256 in the runner. Every other name (chipzen, every `ext:`) has no row,
  so it is unseeded at data time and at play for every student. A seeded student therefore learns "bp100's profile,
  `small_ball`'s profile, or unknown"; the ext guard cells see the same unseeded input they were trained on.
* **Data (holdem-rl `tools/ad0_log.py`, seed 106, registered `106 AD0 read`):** each teacher plays as hero through
  `holdem.arena.run_arena` with `RLBot` and the all-in wrapper of B1's reads: T1 against bp100 2,000 matches (queue:
  `BPQ_SLICE=AD0 BPQ_SEED=106 BPQ_KIND=read BPQ_CONTAINERS=1`); C1 against `small_ball` 2,000; fb2-900 against chipzen,
  `ext:ashwing_v2`, `ext:ashwing_value`, `ext:ashwing_adaptive`, `ext:autodidact_fast` 1,000 each. The `bot:` clones
  are dropped (they exist only as C-engine controllers, with no Python Tracker path). Per decision, logged by a hook
  around the bot's `Policy` that computes, without drawing any random number: the raw `build` observation (no
  teacher has a `keep` array, so none is applied); the label softmax(masked `Policy.logits(obs)` / 1.0), taken before
  `AllInAnswer` and search; the same observation from a second Tracker fed the same history and seeded from
  `ad0_prior.npz` (equal to the first for unseeded names); the legal mask; opponent, hand index, match id. 10% of
  matches held out by match id.
* **Read:**
  1. Offline, per student: held-out top-1 agreement and KL to the teacher by opponent; for bp100 also by hand index
     (1 to 5, 6 to 10, 11 to 20, 21 and later).
  2. Play, seed 95 (registered `95 AD0 read`; bp100 through the queue with `BPQ_SLICE=AD0 BPQ_SEED=95 BPQ_KIND=read
     BPQ_CONTAINERS=1`), holdem-x2r `rl.eval_arena`, 6 workers, cores 0-17 when no training runs; seeded students
     with `--profiles rl/models/ad0_prior.npz`. Paired on (seed, hero seat) against the fb2-900 and B1 it001200 rows on
     disk in `~/poker-ai-lab-x2r/logs/b1/confirm/`: bp100 the first 2,000 matches (k < 1,000), `small_ball` 2,000,
     `ext:ashwing` and `ext:ashwing_hive` 1,000 each.
  3. A student passes when its bp100 gain against fb2-900 is at least +10.0 with its 95% lower bound above +5.4, its
     `small_ball` gain at least +11.0 with its lower bound above +6.5, and the pooled gain of the two ext cells has its
     lower bound above -2.0.
* **Rule (pre-registered), the first line that applies:**
  1. W1 passes: neither identity nor capacity limits; B1's shortfall is the training method. Next: a candidate slice
     that distils the specialists into one network and fine-tunes it with PPO on P1 (full process). AD1 and S7 drop.
  2. W1s passes: identity. AD1 runs as amended, initialised from W1s.
  3. W2 passes: capacity. S7 at 512 wide, started from W2.
  4. W2s passes: both. S7 with seeding, from W2s.
  5. None passes and held-out bp100 agreement of every student is at least 0.90: the students drift to states the
     teachers never visited. One relabel round on seed 107 (registered `107 AD0 read`; bp100 through the queue with
     `BPQ_SLICE=AD0 BPQ_SEED=107`): each student plays 500 matches against each of the seven data opponents, its
     states are labelled by the teacher of that opponent, added to the data, all four students refit; then this
     rule once more. If still none passes, rule 7.
  6. None passes, and the best student's held-out bp100 agreement is under 0.90 in hands 1 to 10 but at least 0.90
     from hand 11 on: identity timing, as rule 2 (AD1 from W1s).
  7. Otherwise: the 56 features cannot carry it; next is the opponent representation (G1's descriptor as input).
  D0's verdict is read beside it: NEW DATA with W1 passing puts the conflict in PPO's gradient on the mix.
* **Tests (each failing on its plant; holdem-rl `tests/test_ad0.py`, plants in `tests/ad0_plants.py`):**
  1. On 20 fb2-900 matches the logged label equals a fresh masked softmax of `Policy.logits` on the logged
     observation, and the match outcomes equal an unlogged `RLBot` on the same seeds (plants: the post-wrapper action
     logged one-hot; the hook draws a random number).
  2. The seeded observation equals the unseeded one for an unseeded name and differs at hand 1 for bp100 (plant: the
     second Tracker never seeded).
  3. Every data opponent and every play cell resolves to the `ad0_prior` row or is unseeded exactly as listed above,
     and data and play read the same file (plant: `ext:ashwing` given a row at play).
  4. The hold-out is by match (plant: split by row); the batch mix is 30 / 15 / 55 within 1% over 100 batches
     (plant: uniform); the loss ignores illegal actions (plant: mask dropped).
  5. The 256 student loaded through the new loader plays fb2-900's arrays row for row as `RLBot`.
  6. The rule table maps as written on synthetic results (plant: rule 3 before rule 2).
  7. Literals: seeds 106, 95, 107; n per cell; 0.90; +10.0, +5.4, +11.0, +6.5, -2.0; widths 256 and 512; 30/15/55
     (plant: one changed).
* **Owners and base:** holdem-rl branch `ad0` from the AD1 builder's `ad1` tip (it carries the seeding code and
  `sdk_prior.npz`); holdem-x2r `ad1-x2r` tip for the eval flag. Non-goals: no change to the trainer, the deployed bot
  or the league; no candidate.
* **Writes on gb10-d and rollback:** `~/ad0-run` (code archive, data, students, rows; rollback: delete it); the
  registry lines `95 AD0 read`, `106 AD0 read`, `107 AD0 read` in `~/poker-ai-lab-rl/tools/seed_registry.txt` and
  in the branch (kept). Nothing else in `~/poker-ai-lab-rl` or `~/poker-ai-lab-x2r`.
* **Budget and order (rates from B1's seed-95 judge files: bp100 4,000 matches in 125 s, `small_ball` 2,000 in 17 s,
  `ext:ashwing` 1,000 in 169 s at 6 workers):** data 10,000 matches, about 15 minutes plus logging; fits minutes on
  the GPU; play 6,000 matches per student, about 7 minutes, 28 for four; relabel 3,500 per student, about 6 minutes,
  25 for four, plus refits. All play after D0's training ends (D0's reads first). Stop and record if any phase takes
  more than three times its estimate.
* **Amendment (registered 2026-11-25 21:58 UTC, before play 1's read was opened; the roadmap agent's call):**
  * **Deviation recorded:** the data phase ran 97 minutes (20:15 to 21:52) against "about 15 minutes plus logging",
    past the three-times stop line; fit and play 1 were launched past it unnoticed. The estimate took rl.eval_arena
    rates, but the data path is `holdem.arena.run_arena` in Python with the logging hook and a second Tracker per
    decision. Seconds per cell at 6 workers: bp100 2,000 in 102 (container-bound, as estimated), `small_ball` 2,000 in
    503 (30x), chipzen 1,000 in 582, `ext:ashwing_v2` 1,245, `ext:ashwing_value` 715, `ext:ashwing_adaptive` 1,204,
    `ext:autodidact_fast` 1,461 (about 7x). The rows are valid (rc 0, 991,921 rows, 9,000 matches, 93,880 held out);
    a time line protects box time, not the rows. Fit: all four students ran the 30-epoch cap with held-out loss still
    falling (W1 0.5703, W1s 0.5407, W2 0.5594, W2s 0.5314 best).
  * **A1. Converged refit:** the same four students, same data, same seed; cap 300 epochs, stop when held-out loss
    has not improved for 10 epochs, best-epoch weights kept. Report epochs run and held-out loss beside the 30-epoch
    values.
  * **A2. Use:** if any 30-epoch student passes in play 1, that pass stands (underfitting can only cost a student) and
    the refits are not played. If none passes, the refits play as play 2 on the same cells and seed 95, and rules 1
    to 4 are read on play 2. Rules 5 and 6 are read only after play 2.
  * **A3. Rules 5 and 6 replaced** (as written, rule 5 could not fire: W1's held-out bp100 agreement is 0.891). They
    apply only when no student passes after play 2, and are read on the refits, rule 6 first:
    * Rule 6 (identity): at both widths the seeded student beats the unseeded one on bp100 in play, paired lower
      bound above +2.0. Then AD1 runs as amended, initialised from the seeded refit. The offline hands 1 to 10 gap is
      reported as support, not as the trigger.
    * Rule 5 (drift): otherwise, if the best student by bp100 play gain has held-out bp100 agreement of at least 0.90,
      one relabel round as in A4, then rules 1 to 4 on its play, then rule 7.
    * Neither: rule 7 (the 56 features do not carry it; the opponent representation).
  * **A4. Relabel round, cut to the measured logging rate:** only the two students with the highest bp100 play gain;
    300 matches each against bp100, `small_ball`, chipzen, `ext:ashwing_v2` and `ext:ashwing_value`
    (`ext:ashwing_adaptive` and `ext:autodidact_fast` left out: the slowest loggers, and their teacher is fb2-900
    either way). The agent's call also listed the ten `bot:` clones at 100 each; they have no Python Tracker path (the
    reason the data dropped them), so they are left out. The estimate is computed from the per-cell seconds above and
    written here before launch; the stop line is two times that estimate, checked by the runner.
  * **Standing budget rule:** a time estimate for a new code path comes from a 20-match smoke on that path, per cell
    type.
* **Limits:** each teacher's data come from its own state distribution; one relabel round is the only correction; a
  pass shows the play is representable and strong, it is not a candidate.
* **Judge literal for the next candidate slice (any):** it reports the solver class on bp100 and on the Blueprint
  clone side by side; a candidate that gains on one and loses on the other with both intervals excluding zero is
  flagged for Wayne, not passed on the headline.
* **Built (2026-11-25, local only):** holdem-rl `ad0` 98058f7, f770230, 8b7ea8b (on 0482bff): `rl/models/ad0_prior.npz`
  (sha256 `2ea5aef1…6368`, the bp100 and `small_ball` rows of `sdk_prior.npz`), `tools/ad0_log.py`, `tools/ad0_fit.py`,
  `tools/ad0_run.sh check|data|fit|relabel|refit`, `rl/ad0_student.py`, registry 95/106/107. holdem-x2r `ad0-x2r`
  50b4d7e, 5209b6a, 541bf81 (on eb5d747): `rl.eval_arena --student`, `tools/ad0_play.sh play N|read N`,
  `tools/ad0_read.py`. Tests: holdem-rl 107 passed, 6 skipped with the data link; holdem-x2r 86 passed; plants 34 of 34
  and 28 of 28. Choices where the spec is silent or off: the listed data cells add to 9,000 matches (the "10,000" above
  was an addition slip); the hold-out is by pair seed, both seats together (seats share deals); the fit's patience is
  3 epochs, keeping the best held-out epoch (a first build ran fixed cosine steps and was corrected before any run);
  after the relabel round rules 1 to 4 then rule 7; "best student" in rule 6 is the highest overall held-out bp100
  agreement; relabel states of all four students are pooled. Outcome verifier: CONFIRMED (tests and plants
  reproduced; probes: the label equals the teacher's masked softmax within 3e-8 and the logged matches equal unlogged
  RLBot matches; data and play seed exactly bp100 and `small_ball` from the same file; a 256 student through
  `--student` plays byte-identical to `--model`; the whole chain runs end to end on toy sizes). Noted, not defects:
  no test covers a relabel label taken from the acting student (code and probes correct); `ad0_read.py` does not
  print D0's verdict beside the rule (read by hand). Shipped to `~/ad0-run/code` (8b7ea8b) and `~/ad0-run/code-x2r`
  (541bf81), pins checked.
* **Review record:** plan review 1 REVISE (no Python path for the `bot:` clones and their seeded rows described a
  different player; seeded students would meet seeded ext inputs at play never seen in data; the label at the
  wrapper was undefined; seeds 95 and the relabel round unregistered and unbudgeted). Fixed above: clones dropped,
  only bp100 and `small_ball` seeded at data and play, label and hook defined, every seed registered, budget from
  measured rates. Tier 2 allows one review; execution follows with the outcome verifier on the read.

### AD1. Seeded identity: does one network keep the specialists' gains when told who it faces? (spec, 2026-11-25; tier 2)

* **Question:** when the policy's opponent-count features are seeded with the opponent's own long-run profile, does
  one network keep at least half of each specialist's gain (T1 +19.9 on bp100, C1 +21.9 on `small_ball`) without the
  real-bot losses B1 showed?
* **Decision it feeds:** PASS starts X2b as a full-process candidate slice (profiles from the A0 archive, the live
  name rule, the E1 gate). The fail branches send the work to how the opponent enters the network, or to network
  capacity, and stop further population tuning. No candidate comes out of AD1; nothing reaches the bot.
* **Why (14.33, 14.36):** pure bp100 training costs 13.4 points on other styles; B1's mix keeps a quarter of each
  specialist's gain (+5.4, +6.5) and loses 2 to 5 points on every real-bot family, with the C-engine clone population
  unchanged from fb2's recipe. That is interference inside one set of weights: the policy's only opponent input is
  the in-match counts (f[44] to f[55]), a match is about 41 hands (14.12) and a spot sees about 10 actions per match
  (14.23), so most decisions are made before the counts say who is across the table. A KL anchor, more families or
  P1b pick another point on the same frontier; a range feature (B1r) improves the hand input, which the results do
  not point at. The arena gives identity for free (0.9% of entrant matches are a first meeting, A0; known names are
  predictable, 14.32), and X2a (14.14, verifier CONFIRMED) built the seeding in the Tracker, the C engine and the
  bot. AD1 is X2b cut down to the one question that decides the line.
* **Before launch, tier 1 (CPU, minutes):** R1, identification curve: nearest-profile accuracy of the 12 count
  features at hands 0, 5, 10, 20, 40 across bp100, chipzen, `small_ball` and the judge cells, from fb2-900 matches
  (seed 102 if fresh ones are needed). If two opponents with different best responses share a profile (bp100 against
  chipzen to watch), AD1 does not launch before the descriptor is widened. If identity is already clear by hand 5 to
  10, AD1 still runs but fail branch 4 (capacity) becomes the prior. R2: bp100's profile beside the archive profiles
  of Blueprint, fermat6, NashForge, hoops (A0's metric); if bp100 sits far from arena Blueprint, the 0.70 judge
  weight and any live seeding keyed to it are wrong and D2b's revisit condition is met (recorded; AD1's rule is
  unchanged).
* **Base commits (pinned):** holdem-rl b1-rl 126c673 (14.35's logging and guard fix, verifier CONFIRMED); holdem-x2r
  b1-x2r 8be6e38 (= holdem-x2r). `rl/features.py` is byte-identical in both (blob 348afb57). Worktrees: holdem-rl
  branch `ad1` from 126c673, holdem-x2r branch `ad1-x2r` from 8be6e38; executors never touch other worktrees.
* **Non-goals:** no change to `rl/features.py`, the network shape, `rl/bot.py`'s defaults, the deployed bot, the
  league tools or `data/`; no C-engine seeding (below); no candidate, no league row, nothing outward.
* **Build:**
  1. **Profiles (holdem-x2r `tools/sdk_profiles.py`):** for each name in the profile list (bp100, chipzen,
     `small_ball`, `small_ball_b`, `tight_sticky`, `sticky_overbettor`, `loose_passive`, `never_fold_pre`,
     `raise_station`, `ext:ashwing`, `ext:ashwing_hive`, `ext:ashwing_search`, `ext:autodidact`, `ext:wolf`) play
     fb2-900 against it through `holdem.arena.run_arena(opp, 500, seed=101, workers=6)` (match seeds 101·100000 + k,
     k < 250, disjoint from seed 104's), run every hand through `rl.features.Tracker.update` from the hero's seat,
     sum the 15 slots and scale so `st[10] = H0 = 40`. Output `rl/models/sdk_prior.npz` in `load_priors`' format,
     keyed by the exact name the hero receives at match start in each tree (the test pins the key for one SDK and one
     arena match). bp100 goes through the queue: `BPQ_SLICE=AD1 BPQ_SEED=101 BPQ_KIND=read BPQ_CONTAINERS=1`. The
     file is committed to both trees; its sha256 is written into this spec and both runners before training.
  2. H0 = 40 (X2a used 20): f[52] saturates at 40 hands, so a seeded match reads "opponent fully known" from hand 1
     and an unseeded one reads unknown. This is the near-oracle form; a pass can be relaxed later, a fail is clean.
  3. **Training seeding (holdem-rl `rl/sdk_rollout.py`):** new flags `--sdk-profiles PATH` and `--seed-share F`
     passed from `rl.train` to the SDK workers. Per SDK match, seeded iff `u < F` where u is a pure function of the
     match's own seed (a hash, not the process RNG); seeded means the hero's Tracker starts from the opponent's row,
     else from none; names absent from the file are never seeded. Without the flags the SDK batches are
     byte-identical to 126c673's for the same seeds. **The C-engine stream stays unseeded:** X2a's C-engine seeding
     keys only `bot:` clones, which P1 does not train against (no `--bot-clones`), and arch clones, snapshots and pool
     members are not named opponents; this is stated in the read, not built.
  4. **Eval (holdem-x2r `rl/eval_arena.py`):** new flag `--profiles PATH`; the hero is `RLBot(priors=PATH)`, so its
     Tracker starts from the row keyed by the opponent's name (no row: unseeded). Without the flag, rows are identical
     to 8be6e38's. The seeded and unseeded arms of a cell use the same `--seed` and n, so rows pair on (seed, hero
     seat).
  5. **Runner (holdem-rl `tools/ad1_run.sh`):** B1's `b1_run.sh` with `--out ckpt/ad1`, `--pool-dir pool_ad1` (a frozen
     copy of the same two pool files, checked by hash), `--max-minutes 240`, `--sdk-profiles rl/models/sdk_prior.npz
     --seed-share 0.75`, and the same guard (14.35). Before start it checks B1's pinned hashes (clones 93b5be28…,
     maniac_labels 36534c2f…, a_ablA 4cf2a418…, b_distill1 6fafbb53…, fb2 init) plus `sdk_prior.npz`'s, and exits
     non-zero on any mismatch. Judge: holdem-x2r `tools/ad1_judge.sh` (B1's judge pattern, BPQ_SLICE=AD1) and
     `tools/ad1_read.py`.
* **Training:** B1's literal command (population P1, init `ckpt/fb2/it000900.npz`) through `ad1_run.sh`, 240 minutes
  (seeded counts at hand 1 are a new input distribution; B1's flat curve does not transfer). Checkpoints read: 600,
  1,200, 1,800 and latest (latest only when the run ends with `done`).
* **Screen (seed 103):** bp100 seeded 1,000 and `small_ball` seeded 1,000 per checkpoint, each paired against fb2-900
  unseeded on the same seed; chosen = highest mean of the two paired gains. No league filter (no candidate).
* **Confirmation (seed 104, paired on (seed, hero seat) against fb2-900 unseeded; `ad1_judge.sh confirm`):**
  1. bp100 seeded 4,000 and fb2-900 4,000; bp100 unseeded 2,000 (the ablation). The ablation difference is seeded
     minus unseeded on the 2,000 shared matches (k < 1,000, both seats).
  2. `small_ball` seeded 2,000; unseeded 2,000; fb2-900 2,000.
  3. Profiles never trained on, seeded, 2,000 each: `small_ball_b`, `tight_sticky`, `sticky_overbettor`,
     `loose_passive`, `never_fold_pre`, `raise_station`.
  4. Real bots seeded, 1,000 each: `ext:ashwing`, `ext:ashwing_hive`, `ext:ashwing_search`, `ext:autodidact`,
     `ext:wolf`; unseeded `ext:ashwing` and `ext:ashwing_hive`, 1,000 each. All arms of a cell on the same cores and
     workers (cores 0-17, 6 workers), fb2-900's included, so no wall-clock bot differs between arms.
  5. Reported only: chipflow's shove table against bp100 (seeded hero, 4,000, seed 104); decision shares; the
     heuristic head to head seeded (chipzen row), 1,000.
  Example commands (holdem-x2r root): seeded `python -m rl.eval_arena --model CKPT --opp bp100 --matches 4000 --seed
  104 --workers 6 --profiles rl/models/sdk_prior.npz --rows logs/ad1/confirm/seeded/bp100.jsonl`; unseeded the same
  without `--profiles`, `--matches 2000`, rows `logs/ad1/confirm/unseeded/bp100.jsonl`.
  `tools/ad1_read.py confirm logs/ad1` pairs each cell's arm with `logs/ad1/confirm/fb2/` on (seed, hero seat) and
  prints the rule's branch; `ad1_read.py screen` reads only seed 103.
* **Rule (pre-registered), evaluated in this order:**
  1. Ablation A = seeded minus unseeded on bp100 (shared 2,000): **below** (upper bound under +2.0), **straddle**
     (interval contains +2.0), **above** (lower bound above +2.0).
  2. Gains G hold when seeded bp100 is at least +10.0 with its 95% lower bound above +5.4 and seeded `small_ball` is
     at least +11.0 with its lower bound above +6.5 (paired against fb2-900).
  3. Real-bot guard R passes when no seeded `ext:` cell is under -2.0 with its upper bound under zero.

  | A | G | R | branch |
  |---|---|---|---|
  | below | hold or miss | pass or fail | **FAIL 3, input ignored**: the network does not use the seed; if G holds, training alone moved the cells, not identity. Next: how the opponent enters the network |
  | straddle | any | any | **INCONCLUSIVE**: one rerun of bp100 seeded and unseeded, 4,000 each, seed 105, then reclassify A; still straddling counts as FAIL 3 |
  | above | hold | pass | **PASS**: X2b as a full-process candidate slice |
  | above | hold | fail | **GAINS ONLY**: identity works, the population is too narrow; X2b with the real families in the seeded population |
  | above | miss | pass or fail | **FAIL 4, used but short**: next is capacity (S7, wider trunk, same recipe), judged on these cells |

  The unseeded cells are also the unseen-name guard: reported against fb2-900, flagged if under -2.0 with the upper
  bound under zero; they inform X2b, they do not decide AD1.
* **Tests (each failing on its plant; holdem-rl `tests/test_ad1.py`, holdem-x2r `tests/test_ad1_judge.py`, plants in
  each tree's `tests/ad1_plants.py`, run by the existing mutate runners):**
  1. Without the flags, an SDK batch on fixed seeds equals 126c673's byte for byte (plant: seeding drawn even without
     the flags).
  2. The seeded share over 2,000 match seeds is 0.75 ± 0.03 and the same seed gives the same decision twice across
     processes (plant: drawn from the process RNG).
  3. Only the hero's Tracker is seeded and only for names in the file (plants: the opponent seat seeded; an unknown
     name seeded with a default row).
  4. `sdk_prior.npz` has `st[10] == 40` on every row and equals an independent count on a 3-hand toy (plant: H0 = 20).
  5. `ad1_run.sh` exits before training on any hash mismatch, `sdk_prior.npz` included (plant: the check removed).
  6. The seeded eval hero with no row for the opponent equals the unseeded hero row for row on 50 matches, and with a
     row differs (plant: `--profiles` ignored).
  7. `ad1_read.py` uses only seed 104 for the rule and only seed 103 for selection (plant: swapped); the ablation uses
     only the shared k < 1,000 pairs (plant: all 4,000 seeded rows).
  8. Every row of the branch table maps as written, on synthetic intervals (plant: straddle mapped to FAIL 4).
  9. Literals: 0.75, 40, 240, seeds 101 to 105, +10.0, +5.4, +11.0, +6.5, -2.0, +2.0, every n above (plant: one
     changed).
* **Writes on gb10-d and rollback:** `~/poker-ai-lab-rl`: `rl/models/sdk_prior.npz`, `pool_ad1/`, `ckpt/ad1/`,
  `logs/ad1/`, the code from `ad1` (ship by `git -c core.autocrlf=false archive`; rollback: re-ship 126c673's
  archive and delete the four paths). `~/poker-ai-lab-x2r`: the code from `ad1-x2r`, `rl/models/sdk_prior.npz`,
  `logs/ad1/`, `logs/ad1r/` (rollback: re-ship 8be6e38 and delete those). `tools/seed_registry.txt` gains the lines
  `101 AD1 read`, `102 AD1 read`, `103 AD1 read`, `104 AD1 read`, `105 AD1 read` (kept; registry lines are never
  removed). No push of `ad1` or `ad1-x2r`.
* **Budget and stop:** 240 minutes of training plus about 3 box-hours of reads, the bpopp serial queue as in B1.
  Stop and record if test 1 or 2 still fails after two fix rounds.
* **Registry:** seeds 101 (profiles), 102 (R1 if fresh matches are needed), 103 (screen), 104 (confirmation), 105
  (the INCONCLUSIVE rerun only). No league pairs (the league cell was dropped: AD1 yields no candidate). Seeds 99 and
  100 and pairs 500 to 599 stay reserved to P1b, retired.
* **Known limit:** a profile is measured with fb2-900 as hero and some slots depend on the hero's own betting. The
  live version has the same mismatch (archive profiles come from other heroes), so it is the realistic condition.
* **Amendment after 14.36's correction and D0 (2026-11-25, before any AD1 training):**
  1. Population stays P1 at `--heur-batch 10000` (B1's command plus the seeding flags), so AD1 and B1 differ only in
     seeding.
  2. Baseline arm: B1 it001200 (`ckpt/b1/it001200.npz`) is added on seed 104 to bp100 (4,000), `small_ball` (2,000)
     and the seeded real-bot cells (1,000 each), paired on (seed, hero seat). The thresholds stand (lower bounds above
     B1's +5.4 and +6.5, points +10.0 and +11.0).
  3. Real-bot guard reading: primary is AD1 seeded minus B1 per real-bot cell. Worse than B1 by more than 2.0 with
     its upper bound under zero: the seeding hurt. Not worse than B1 but still under -2.0 against fb2-900: B1's loss
     persists; under D0's NEW DATA that means identity as counts does not cure interference (FAIL 3 or 4 by the
     ablation), under MIX OR CONTINUATION it is the mix and says nothing against identity. At or above -2.0 against
     fb2-900: identity removed the loss.
  4. GAINS ONLY no longer means "population too narrow" on its own; it takes D0's verdict as in item 3.
  5. Order: AD1 trains after D0's training ends; it does not wait for D0's read.
* **Built (2026-11-25, local only, AD1 training gated by AD0):** holdem-rl `ad1` a115c0c, 0482bff (on 126c673);
  holdem-x2r `ad1-x2r` 5d7fcce, 809c438, eb5d747 (on 8be6e38). `rl/models/sdk_prior.npz` sha256 `c77f058e7e45…a612b0`
  (full hash in `ad1_run.sh` and `ad1_judge.sh`; pin the committed file, the zip timestamp makes a rebuild differ),
  14 rows, each `st[10] = 40`, from 500 fb2-900 matches per name on seed 101 (7,005 to 24,424 hands per row). Tests:
  holdem-rl 89 passed, 6 skipped; holdem-x2r 77 passed; plants 15 of 15 and 39 of 39 caught. Deviations: the engine
  sends no opponent name, so the hero wrappers inject the cell or training name as the other seat's `display_name`
  (`with_opp_name`, RLBot and engine untouched); `tools/chipflow.py` got `--profiles` for the shove table; the
  "decision shares" report is not built; two profile arms (`ext:ashwing_search`, `ext:autodidact`) ran beside other
  arms instead of alone (deterministic bots, no wall-clock effect). P1's four ext training names have no row and stay
  unseeded, so training seeds only bp100, chipzen and `small_ball`. Outcome verifier 1: REFUTED. Every built claim held (unseeded paths
  byte-identical to the bases, the `small_ball` row regenerated exactly, seeding only for the hero and the right
  name, tests and plants as stated), but amendment items 2 to 4 were not built: no B1 it001200 arm on seed 104 and
  no "AD1 seeded minus B1" reading with D0's verdict. Fixed on `ad1-x2r` a38e232, 2fb1dbd, 4b85994: `ad1_judge.sh confirm`
  adds B1 it001200 unseeded on seed 104 (hash 5e9c6fc6… pinned); `ad1_read.py confirm` requires `--d0` and reads
  each real-bot cell on its own (hurt: seeded minus B1 under -2.0 with upper bound under zero; else persists: seeded
  vs fb2-900 point under -2.0, meaning set by D0; else removed). 86 x2r tests, 95 of 95 plants. Verifier 2: REFUTED, on one point: the
  GAINS ONLY line took its meaning from D0 alone even when the failing cell read "seeding hurt". Fixed first-hand in
  91510c3 (a hurt cell reads as hurt whatever D0 says; D0 applies only to a persisting loss; test cases e and g and
  two plants): 86 tests pass, 24 of 24 amendment plants caught on gb10-d. The verifier cap (two REFUTED) is reached on
  this claim, so the fix stands on that first-hand check. Known wording limit: under NEW DATA the reader prints "FAIL
  3 or 4 by the ablation" and leaves the machine-readable branch at GAINS ONLY.
* **Review record:** plan review 1 REVISE (no owner files, non-goals, writes, rollback or tests; C-engine seeding
  would never fire under P1 and had no share knob; no seeded eval flag or AD1 reader; rule branches overlapped and
  left a gap; registry, profile command, base commit and runner unpinned). Fixed above; tier 2 allows one review,
  so execution follows with the outcome verifier on the read.
* **Consumers:** X2b's go or no-go; the opponent-representation or capacity slice on a fail.

### G1 step 2a. Does starting from the population model make a per-name model good at 100 and 1,000 matches? (pre-registration, 2026-11-25; tier 2)

* **Why:** 14.32 rule 2: G1 beats the λ range only for names in its fit; unseen names fail even with their history
  as input. The names we cannot train against directly (hoops 842 matches, mr_hide 826, r0ckGarden 774, NashForge
  884, fermat6 990) each have under 1,000 matches, where D2a's per-name fit was weak (14.25). This answers it with
  true cards, without containers, on logs that exist.
* **Data:** D2a's logs on gb10-d (`~/poker-ai-lab-d2s2/logs/d2/`) for `ext:ashwing`, `ext:autodidact_fast`,
  `ext:wolf`: fitting logs (seed 61, sizes 100 and 1,000 by index) and held-out logs (seed 62, 1,000 matches) with
  `true_cards.jsonl`. No new arena seed. Only the bot's seat is modelled and scored.
* **Adapter `tools/g1_2a_extract.py`:** D2a's match headers have no `started_at`/`completed_at`, so G1's extractor
  cannot read them unchanged. The adapter imports `g1_extract.match_arrays` and `player_rows` and supplies a synthetic
  match order (the log's match index k as time) and the history block defined in arm (d); no edit to
  `g1_extract.py`. If `match_arrays` still fails on D2a's files, stop and record.
* **Base fit per bot, by the held-out rule:** each bot uses the W fit of the fold in which its archive name and
  version siblings were held out (`data/g1/folds.json`: `Ashwing_v3` and `AutodidactInnovations` are in fold 2, so
  `fit_fold2_W.pt`). The executor records each bot's archive names and fold before any fit. Wolf: if its archive name
  is a held-out name, its fold's fit; if it is absent from the archive, fold 0's fit (it was never a modelled player)
  and that is recorded; if it was a modelled player in every fold's training, Wolf is dropped and the rule becomes
  both of the two remaining bots.
* **Fitting and calibration split:** arms (a), (b) and (c) fit on the first 90% of the N fitting matches by index;
  the calibration bias uses the last 10% (10 matches at size 100, 100 at 1,000). No fit or calibration reads any
  `true_cards.jsonl` (seed 61 or 62); hidden cards are handled by EM exactly as D2a and G1.
* **Arms, per bot and size N:** (a) the λ range under per-name X1 fitted on the fitting split; (b) D2a's per-name
  network from scratch on the fitting split (refit at both sizes so the split is the same); (c) the base fit
  fine-tuned on the fitting split: start epochs 0, 4 EM iterations, D2a's epochs per iteration (`d2_clone`'s constant,
  pinned by literal in the test), Adam learning rate 3e-4, history block filled with (d)'s fixed block in training and
  scoring; (d) the base fit as is, history block = `hist_vector(match_stats)` over the bot's fitting-split matches
  (log1p of their number, flag 1), the same fixed block for every held-out match; the in-match block as usual.
* **Calibration first:** a per-street bias on the fold logit fitted on the fitting logs' last 10%, applied to (c) and
  (d); the fold-rate table by bet-size bucket reported before and after.
* **Read** on the held-out logs (seed 62) with true cards: R on every hand that reached the river (not only shown
  hands): log posterior of the bot's true holding after its actions minus log uniform over live combos (1,326 minus
  combos touching the board or the other seat's true cards, as `x3_range`), joined on (held-out match index, hand
  number, bot seat). One row set per bot and size, scored by all four arms; the read fails if any arm drops or adds a
  row. P at big-pot decisions (G1 step 1's definition). Fold rate predicted against actual per bet-size bucket,
  buckets by `g1_extract.size_bucket3`. Bootstrap over held-out matches, 2,000, seed 47.
* **Rule:** (c) beats both (a) and (b) on R by at least +0.10 nats with the lower bound above zero at size 1,000 for
  at least two of the three bots, and its fold calibration error, measured on the held-out logs after the bias, is
  5 points or less in every `size_bucket3` bucket with 200 or more spots. Size 100 is reported only. Pass: G1 step 2b is specified (the lookahead with G1's range at the root against those bots, on real
  code, paired against the λ root as X3b was, on top of B1's candidate). Fail: G1 stays an archive analysis tool
  and gets no more GPU.
* **Box and cost:** GPU and cores 18-19 only; no bpopp, no containers. About 12 short fits, under 2 GPU-hours; reads
  about 2 core-hours. Stop at 8 GPU-hours.
* **Owner files (holdem-d2, executor worktree):** `tools/g1_2a_extract.py`, `tools/g1_tune.py`, `tools/g1_2a_read.py`, `tests/test_g1_2a.py`,
  plants in `tests/g1_plants.py`. **Non-goals:** no change to G1 step 1's tools or outputs, the lookahead, the bot.
  **Writes on gb10-d:** `~/poker-ai-lab-d2s2/data/g1_2a/`, `logs/g1_2a/`. **Rollback:** revert, delete those.
* **Tests (each failing on its plant):** the adapter on a toy D2a-shaped file with no `started_at` gives shards whose
  `base` rows equal `d2_clone.hand_decisions` (plant: k ignored); the base fit per bot is the held-out fold (plant: a
  fold where the bot was in training); no fit or calibration opens any `true_cards.jsonl` (plant: a fit reading seed
  61's); the fits use only the first 90% and the bias only the last 10% (plants: fine-tune including the last 10%;
  bias on held-out logs); (c)'s and (d)'s history block is the fixed fitting-split block (plants: history state
  flipped; history built from held-out matches); all four arms score the same rows (plant: one arm drops a row); R on
  river hands equals a hand computation on a toy; arm (a) equals `x3_range` on 50 hands; literals (+0.10, 5 points,
  200 spots, sizes 100 and 1,000, two of three, start epochs 0, 4 iterations, 3e-4, 90/10, `size_bucket3`).
* **Review record:** plan review 1 REVISE (no adapter for D2a's headers; base fit not tied to held-out folds; arms'
  knobs unpinned; calibration and true-card separation; read join, row equality, bucket function, size 100's role).
  Fixed above; tier 2 allows one review, so execution follows with the outcome verifier on the read.

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
