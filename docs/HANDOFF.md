# HANDOFF: Chipzen Season 16 hold'em bot

Updated 2026-11-25 05:39 UTC. Read "Now" first; the session context is compacted often, so this file is
the working memory. Update it at every step that changes state.


## Now (2026-11-26 19:40 UTC, box clock UTC+8)

**Standing rules from Wayne:** English in this project; when he writes "中文說明", answer in Traditional Chinese.
Think from first principles, not narrowly. Goal is the long-term "future king", not Season 16. Act on Fable's
recommendations; open questions go to the Fable roadmap agent, never to Wayne. Uploads, swaps and L0 live
challenges need his explicit yes and are not raised. Process gates hold: plan-verifier READY/REVISE (cap 2),
outcome verifier CONFIRMED/REFUTED (cap 2). Memory and docs English only. On every new result, update the matching
doc (experiments, roadmap, HANDOFF) and drop what is stale. Plan of record: `docs/research/roadmap.md` on branch
research ("Where we are" at the top). Times here come from `ssh gb10-d 'date -u +%H:%M'`.

**Where it stands (details in experiments 14.30 to 14.37 and the roadmap):**
* B1 (14.36): RULE FAIL. bp100 +5.4 of T1's +19.9, but P1's own ext families lost 3.4 to 4.6 points against
  fb2-900. No v5; v4 stays entered. Chosen checkpoint it001200 (rows in ~/poker-ai-lab-x2r/logs/b1/confirm/cand).
* 14.37: weighted by hands, the counts name the opponent for 53% of hands and 71% of bp100's, so seeding (AD1) has
  limited room. AD1 and S7 dropped by AD0 rule 1 (14.39).
* **D0 (14.38, research 31825b5): rule INCONCLUSIVE.** Valid run (void check ok). Pooled four ext cells: D0 vs
  fb2-900 -2.70 [-4.02, -1.38] (straddles -2.0), D0 minus B1 +1.07 [-0.28, +2.43]. Three families sit within 0.2 of
  B1 (the loss stays without the new data); `ext:ashwing_hive` recovers 4.2 of B1's 4.6. No lever decision, no
  D-null by the rule. Verifier CONFIRMED the numbers, REFUTED wording (corrected, research 280bdd4). Fable: run **C0** now,
  hold D-null.
* **C0 (14.40, research 6e11f07): PEAK.** fb2 it700 -2.90 [-4.43, -1.37], it800 -2.83 [-4.35, -1.31], it965 -0.97
  pooled on the three Ashwing cells vs fb2-900. fb2-900 is a local high; B1/D0 guard losses are within the run's
  checkpoint spread. D-null, P1b, restore-the-shares closed; future PPO screens add the Ashwing cells and
  autodidact_fast at 500 each. Outcome verifier CONFIRMED (research 87a09ff).
* **AD0 (14.39, research eb2281c): RULE 1, W1 passes.** Play 1 (seed 95, 21:56 to 22:31): W1 (256 raw, 30
  epochs) bp100 +19.4 [+16.9, +21.8], `small_ball` +19.8 [+17.8, +21.7], ext +1.1 [-0.7, +2.9] vs fb2-900; W2s also
  passes, W1s and W2 fail on the ext lower bound. B1's shortfall is the training method; next is a distil-then-PPO
  candidate slice (full process); AD1 and S7 drop. Data overran its time line (deviation recorded in the amendment,
  research 2513a6f). A1 converged refits (students_a1) exist, not played (A2). Outcome verifier CONFIRMED; Fable asked
  for the next slice's spec and whether D-null still runs. Students: ~/ad0-run/students/W1.npz etc.
* **Next:** **G0 read: GUARD FAIL** (experiments 14.47, driver 08:32 to 10:51 UTC 2026-11-26, all steps rc 0): chosen G50 (screen 0.7597 vs G80 0.7326); bp100 +15.2 [+13.7, +16.8], small_ball +16.1 [+14.2, +17.9], sticky_overbettor -5.9 [-7.2, -4.6] (fresh seed 113 -6.4), chipzen +2.6 under its +5.10 line, other held-out cells within 1 point of level; headline +10.23. Misfire: G50 leaves the default on 24.4% of sticky_overbettor hands (to the small_ball expert), so the rule names the classifier; the failure is open-set. Outcome verifier CONFIRMED (10:58 UTC). Fable: next slice **G0b**, a gate that can say "none of these" (spec pending). **G80 post hoc read done** 12:23 UTC (experiments 14.48, research 0ee6c17): guards hold (sticky_overbettor -0.4, fresh -1.4 [-2.0, -0.8]), gains just short (bp100 +11.4 [+9.9], small_ball +11.1 [+9.4]); own play drifts to the small_ball expert on sticky_overbettor (43.7% past hand 40). Probe (11:02 UTC, 14.37 raw counts): fold-facing-a-bet separates small_ball (0.63) from sticky_overbettor (0.14) but has 2.7 events per match by hand 20, so a count-only gate cannot separate them in time; G0b needs opponent bet-size inputs and new logging. **G0b spec** written with Fable (research 595e71b: one logging run under fb2-900 and G50 with raw counts and action histories, seed 114; gate GS = Beta-binomial terms over the eight count pairs plus six bet-size terms, classes bp100/small_ball/chipzen/population, support test at 0.01; offline lines S1/S2 before play; then G80/GS50/GS80 with 20 new styles, seeds 115-117); plan review 1 REVISE (6 blockers, revised f5301b4), review 2 REVISE at the cap, fixed first-hand and recorded (research 8ee007a, 11:12 UTC). **G0b build**: steps A to C built (`g0b-rl` 72714fd, 47 tests, 87/87 plants; full logging run estimated 65 min at 6 workers, launch `cd ~/g0b-run/code && setsid -f bash tools/g0b_run.sh all` after shipping the archive), verifier 1 REFUTED (step C buckets and row wiring unpinned, fixed c3a1ee3), verifier 2 REFUTED (16 wiring mutations untested; code correct), cap: fixed first-hand 4a4a5f1 (60 tests, 115/115 plants, all applicable verifier mutations caught). **G0b steps A to C done 14:36 UTC: S1 and S2 PASS** (experiments 14.49, outcome verifier CONFIRMED by independent recompute): GS50 routes sticky_overbettor at most 4.8%, GS80 0%, against G80's 65% past hand 40; GS80 routes 91 to 100% of true bp100 and small_ball hands from hand 11; the six size terms carry it. Run stopped twice (13:13 D4 bots missing, 13:49 opponents.py pin) and resumed (g0b-rl b9031b1, e87a5f5; trees ~/g0b-run/code.crashed-*). **G0b step D done 16:44 UTC: VERDICT PASS, GS50 chosen** (experiments 14.50): bp100 +18.4 [+16.7, +20.1], small_ball +18.8 [+16.9, +20.7], chipzen +7.0, sticky_overbettor seed 113 -0.2 [-0.7, +0.3], test styles pooled -0.1; screen 23 of 23 league opponents at 80% or more (200 each). Outcome verifier CONFIRMED 16:55 UTC. **Next: C1v5** (roadmap spec, research ef66f4f; Fable: ship the gate arm itself, fresh seeds 118 to 120, no backup arm): step 1 deployment check (limits, purity, parity, a new size-record chip-conservation guard, fault counter, latency), step 2 fresh confirmation, step 3 E1 pairs 200-399 plus head-to-head over 102b05e, step 4 card. Plan reviews 1 and 2 REVISE (3 and 4 blockers); cap reached, fixed first-hand (research 051de3a). **C1v5 built** (local, not pushed): `c1v5-root` 620a975 (worktree poker-ai-lab-c1v5root; 25 tests, 44/44 plants), `c1v5` 2458104 (poker-ai-lab-c1v5x2r; 55 tests, 82/82 plants). Step 1 PASS: tar.gz 64.6 MB (sha256 3758ca7f...), peak memory 99 MB, no scipy, parity 200/200 vs 27773b0 (seed 901), guard 0 skips (2,000 engine matches; 330 replays, 10,516 hands, equal to the engine reference), fault fallback via deploy/bot.py, latency at 0.5 vCPU mean 2.1 ms max 53 ms; sha256 list ~/c1v5-run/bot_files.sha256 equal across context, image, export. Item 13 probe: Blueprint routed 60% to T1, other names mostly default. Items 14 (E3) and 15 (prose) not built (card only). Build verifier 1 REFUTED (18:18 UTC): the gate and item 9 driver steps were not fail-closed (`| tee` and `;` kept rc 0 and a stale PASS verdict when the read failed), plus 9 surviving test mutations; step 1 artifact, runtime, guard, fault path and counters held. Fixed: `c1v5-root` b14b176 (tests only; image byte-identical, 26 tests, 45/45 plants), `c1v5` 712010d (fail-closed reader steps under pipefail with stage-stamped results, step 2 cumulative 300 min stop, 67 tests, 100/100 plants); box dirs ~/c1v5-run/code-root-2, code-x2r-2. Build verifier 2 REFUTED (19:2x UTC): a PASS could come from rows whose counters were never checked (judge reused existing rows, reader required no counter record), the slice-end order and a PASS verdict beside `failed` were untested, verdict-changing literals in b1_read (1.96, GUARD_DROP) and the judge (league counts, bp100 counters, styles sha) were unpinned, and the step 2 budget test was flaky (whole-second clock); artifact and parity held. Review cap: fixed first-hand at 19:40 UTC, `c1v5` 1564a53 (reader stops without a record for each of the 34 counted v5 runs and the league run, own Z and guard, judge replays counted cells, driver refuses a non-empty LOGS or league out and keeps the order in `run_all`, nanosecond step 2 clock; 30 new plants); box dir ~/c1v5-run/code-x2r-3, suite x3 and plant runner running (~/c1v5-run/x2r3_check). Launch when they pass: `ssh gb10-d 'cd ~/c1v5-run/code-x2r-3 && setsid -f bash tools/c1v5_drive.sh > ~/c1v5-run/drive.out 2>&1 < /dev/null'`. markers ~/c1v5-run/progress, done, failed, verdict; rollback `tools/c1v5_judge.sh registry-rollback`. Rows ~/poker-ai-lab-x2r/logs/g0b, read ~/g0b-run/logs/drive_read.out. **Release rule (Wayne 2026-11-26):** once a candidate is strong enough and goes on board (full upload gate plus his own yes for the Chipzen upload), push all research records and the shipped model to Hugging Face; HF repo private first while Season 16 runs; the PC has huggingface-cli but is not logged in (he runs `huggingface-cli login`), gb10-d has no HF CLI. Step D code: worktrees poker-ai-lab-g0broot (`g0b-root` from 0e3b521) and poker-ai-lab-g0bx2r (`g0b` from 77f0c00, which adds tools/g0_posthoc_g80.sh). Earlier: V5b DEFAULT FAIL (14.46, verified). G0 worktrees (local, not pushed): poker-ai-lab-g0rl (`g0-rl` bad56dd), poker-ai-lab-g0root (`g0-root` 0e3b521), poker-ai-lab-g0x2r (`g0` 44759f4). Box: ~/g0-run (students g50/g80, clf.npz, logs, progress), rows ~/poker-ai-lab-x2r/logs/g0, registry copy ~/g0-run/seed_registry.pre-g0. V5b kept as comparison: worktrees poker-ai-lab-v5broot (`v5b-root` a4ec310), poker-ai-lab-v5bx2r (`v5b` bedc22e), poker-ai-lab-v5brl (`v5b-rl` 377ec9f, WIP commits to squash before any push); box ~/v5b-run, rows ~/poker-ai-lab-x2r/logs/v5b. ~/b1-build can go.
  W1 (30 epochs, 9bc31660…) and its A1 refit (3c375498…) as the candidate with no PPO: B1's screen (seed 94, league
  400-499, filter 78.0%), B1's rule on seed 95, fresh-seed check seed 108 (bp100 lb > +5.4, small_ball lb > +6.5), E1
  gate, eval card with E3; **TT** (tier 2): T-a reads
  br_ashwing and br_autofast on seed 95 (cores 18-19 after C0); T-b 60-min specialists vs sticky_overbettor,
  loose_passive (port to holdem-rl), never_fold_pre, chipzen, read on seed 109; lb +8.0 joins V5b. Dropped: AD1, S7,
  D-null, P1b, B1v, the seeding path.
* **AD1 built** (local: holdem-rl `ad1` 0482bff, holdem-x2r `ad1-x2r` eb5d747; `sdk_prior.npz` c77f058e…, record in
  the roadmap AD1 spec). Verifier 1 REFUTED: amendment items 2 to 4 (B1 arm on seed 104,
  "AD1 minus B1" reading with D0's verdict) missing; fixed on ad1-x2r 4b85994; verifier 2 REFUTED the GAINS ONLY line
  (it ignored a cell's "seeding hurt"); fixed first-hand in 91510c3 at 17:37 (86 tests, 24 of 24 amendment plants).
  Verifier cap reached on this claim; AD1 build done (ad1-x2r 91510c3).
  Not trained: dropped by AD0 rule 1.
* **AD0 built** (holdem-rl `ad0` 8b7ea8b, holdem-x2r `ad0-x2r` 541bf81; worktrees poker-ai-lab-ad0, poker-ai-lab-ad0x2r;
  record in the roadmap AD0 spec). Fit corrected to the spec (at most 30 epochs, best held-out epoch, patience 3) and
  hold-out by pair. Verifier CONFIRMED; shipped 17:56 to ~/ad0-run/code and code-x2r, pins match. Runners: `tools/ad0_run.sh check|data|fit|relabel|refit`
  in ~/ad0-run/code (holdem-rl archive), `tools/ad0_play.sh play N|read N` in ~/ad0-run/code-x2r; `AD0_TASKSET`
  for cores 18-19 while D0 runs. Then data (seed 106), GPU fits, play (seed 95) after D0's reads.
* **Merges (local) done:** holdem-rl fast-forwarded to b1-rl db446d7, then b047c04 drops rl/bot_b1.py and
  rl/models/b1.npz (kept at b1-rl 59b1ad3). holdem-league 57a63b8 commits the leaderboard with cand:rl-b1 (rank 4,
  PASS 23/23). Delete ~/b1-build after the AD builds no longer need it (AD0 and AD1 tests link it).

**gb10-d:** idle since 16:44 UTC. **T-a done** (14.45, research cc3e662): br_ashwing +16.0 ashwing, +15.4 search, +8.2 hive; br_autofast +13.4 autodidact; not used by V5b (held-out cells), kept for a later slice. bpopp queue free. GPU idle. Fetcher pid 1838186, the only one.

**Branches not pushed (local only, by rule):** holdem-rl, holdem-x2r, holdem-league, holdem-d2 (`python
tools/d2_mutate.py --jobs 4` must catch every plant after a change), b1-rl, b1-x2r, b1-league, d0, ad1, ad1-x2r,
ad0, ad0-x2r.

## Goal and gate
- Heads-up NLHE bot for Chipzen.ai Season 16. Registration closes Mon 23 Nov 23:59 UTC.
- Ship gate (Wayne): at least 80% match wins against every one of the 23 league opponents,
  each separately, over at least 400 matches (point estimate; report the Wilson lower bound).
  Added 2026-11-21 (Wayne): the shipped bot must also beat the old heuristic bot (holdem-chipzen
  102b05e) head to head: at least 400 matches, Wilson 95% lower bound above 50%.
  No upload or registration before a candidate passes both and a fresh verifier confirms it.
- Design rule (Wayne): adaptation comes from a decision model (online opponent model plus a
  procedure that maximizes match-win probability plus a safety blend), not switched fixed strategies.

## State (league on the corrected engine, `reports/league/leaderboard.md` on holdem-league f07923f)
| entrant | branch / commit | passed | field | weakest |
|---|---|---|---|---|
| rl-fb2-900-allin (ENTERED as poker-ai-lab-v4) | holdem-rl ad5ec3a | 23/23 | 91.2 | identical to fb2-900 everywhere except jam 49.0 -> 62.75; verifier CONFIRMED |
| rl-fb2-900 (uploaded as poker-ai-lab-v3) | holdem-rl 56c4419 | 23/23 | 91.2 | A5 84.5 (fresh 84.75, LB 80.9); heuristic h2h 66.2 (fresh 70.25, LB 65.6); verifier CONFIRMED |
| rl-fb1-900 (uploaded as poker-ai-lab-v2) | holdem-rl 82b1921 | 23/23 | 89.8 | A5 83.8 (fresh seeds 86.0, LB 82.3); heuristic h2h 64.0 (fresh 69.0, LB 64.3); verifier CONFIRMED |
| rl-h4-300 (previous entry, bot poker-ai-lab) | holdem-rl 5493fc6 | 23/23 | 88.8 | A5 83.2 (fresh seeds 80.2); heuristic h2h 69.8 (fresh 67.5) |
| rl-distill1 | holdem-rl 22b46de | 23/23 | 91.5 | qwentom-leap clone 85.0; heuristic h2h 43.0 |
| adapt-v2 | holdem-adapt 4a4b419 | 23/23 | 89.4 | SolvencyCheck clone 80.8; heuristic h2h 29.5 |
| rl-17cf03f | holdem-rl 17cf03f | 22/23 | 89.4 | PoetAndCoder clone 79.5 |
| adapt-v1 | holdem-adapt | 22/23 | 86.0 | maniac 74.5 |
| chipzen-102b05e | holdem-chipzen 102b05e | 8/23 | 76.0 | A5 64.0 |
- Maniac best response confirmed: 87.55% [86.0, 88.9] over 2000 matches (holdem-br, `br/bot.py` ManiacBR).
- Blueprint (holdem-blueprint 06b654d): 1/23 alone; safety anchor and range model only.
- Research log: branch `research`, `docs/research/` (pushed, 8e83c3a).

## Branches and worktrees (Desktop)
poker-ai-lab (holdem-chipzen), -league, -rl, -adapt, -br, -blueprint, -search, -research, -x2r, -d2.

## Goal (Wayne, 2026-11-22 13:30 UTC)
The long-term strongest bot, a "future king". The Season 16 deadline no longer matters, and fb2-900 stays
entered. Plan: `docs/research/roadmap.md` on branch research, slices S1 to S7: measurement harness, league
with exploiters, showdown memory, range belief, a wider bet set, river search, then capacity. Key fact:
an exploiter trained 2 minutes against fb2-900 beats it 96.5% (fb2-900 folds after the flop too often), so
exploitability (E3) is a primary metric next to the league and the real bots.

## Season 16 entry (swapped 2026-11-22 18:45 UTC, Wayne approved)
- **Live (read 2026-11-26 01:25 UTC, chipzen.ai/season/16 in ego-browser):** 44 bots; round robin Tue 24 to Fri 27
  Nov, playoffs Sat 28 to Sun 29 Nov; prize $120/$60/$10/$10. v4 is **5th, 3-1**: lost to MonteCarlo (R1), beat
  fermat-mini (R2), stebin-bot-here (R3, 25 Nov 18:10), ALEXANDRA (R4, 22:30). Leaders typeshii, MonteCarlo, Yezi1
  at 4-0. Next: Velvet_Shark 26 Nov 18:10 UTC (R5); 8 rounds in all. Season replays carry `match_type: "challenge"`.
- Entered: Chipzen bot `poker-ai-lab-v4` (id dbdfde29-f098-4a79-9249-a4bdbe3157f3) = rl-fb2-900-allin, image
  `.cache/images/holdem-rl-fb2-900-allin.tar.gz` sha256 0291ee39ca557a2fb60bfb397184328eff767c6ac324c42e141704c32ea44f53.
  Review about 1 minute. Season page reads "poker-ai-lab-v4 is entered" after reload.
- The account holds at most 3 bots and code cannot be replaced in place. To upload v4, `poker-ai-lab`
  (rl-h4-300) was deleted (Wayne approved; its image stays in `.cache/images/holdem-rl-h4-300.tar.gz`).
- Previous entry 10:15 to 18:45 UTC: Chipzen bot `poker-ai-lab-v3` (id 116f047c-da11-4879-be63-136232ec7913) = rl-fb2-900, image
  `.cache/images/holdem-rl-fb2-900.tar.gz` sha256 058280d4c18ae58d0efa8a8aef522d2412f9c452fcafffe9c612e781b28468c4
  (weights md5 4ad6e363). Review about 4 minutes; warm-up beat PluriBot. Season page reads
  "poker-ai-lab-v3 is entered" after reload.
- Also uploaded, for switching back until Mon 23 Nov 23:59 UTC (Season 16 page, Change bot):
  `poker-ai-lab-v3` (rl-fb2-900) and `poker-ai-lab-v2` (rl-fb1-900, sha256 8b4b4a45...).
- Registered at 18:45 UTC (9): HRT, poker-ai-lab-v4, kangaroo, Shadow, bp_bot, 6BP9, allin_9-1, microholdem,
  Ashwing_v3.
  House bots top up after the deadline.
- Hugging Face (2026-11-22, PRIVATE): https://huggingface.co/waynehacking8/poker-ai-lab-hunl-ppo holds the
  fb2-900 package (model card, MIT, weights.npz plus model.safetensors, the image's runtime files). Built by
  `deploy/hf_package.sh` (holdem-rl 4f8adde), uploaded through the web UI (no HF token on this PC), all 16
  files read back byte identical. Make it public in the repo Settings when Wayne wants.

## S0 all-in fix (2026-11-22, research experiments 14.7)
- Wayne found online that spamming all-in beats v3: fb2-900 wins 49.0% against `jam`. Fix: `rl/allin.py`
  (holdem-rl 65ef2b7, deploy ad5ec3a), a play-time answer to a near-certain preflop shover from solved
  match-value tables `rl/models/allin_v.npz`. jam 62.75% (ceiling 65.5%). League, Wolf family, seeded
  Blueprint and seeded h2h vs v3 byte identical; 0 fires in 2400 matches against v3, Ashwing family, autodidact.
- Image on gb10-d `~/build-rl/holdem-rl-fb2-900-allin.tar.gz`, sha256
  0291ee39ca557a2fb60bfb397184328eff767c6ac324c42e141704c32ea44f53. League row holdem-league fcb34c0.
- Gate tools: `tools/allin_gate.sh`, `tools/allin_count.py`, `tools/allin_ceiling.py`; logs in
  `logs/allin/` on gb10-d. Uploaded and entered as poker-ai-lab-v4 (Wayne approved).
- ex1 exploiter finished (30,790 iterations): fb2-900 wins 1.0 to 1.5% against it (experiments 14.8).

## Open work
0. S1 done (research 14.9, baseline card `logs/eval_card/fb2-900.json` on gb10-d; verifier CONFIRMED).
   S2 done (research 14.10): ran 2026-11-22 19:47 to 2026-11-23 00:50 UTC, ended at max-minutes (it 1835),
   no stop. Probe 96 to 97% fell to 74.5 to 89.75%, field and E4 level, so acceptance (E3 under 70%) is not
   met and v4 stays. The five review fixes are in holdem-rl a0ba32c. Cards on gb10-d:
   `logs/eval_card/s2-it400.json`, `s2-it1800.json`; chip flow against probe exploiters in `logs/s2/flow/`.
   S2b RUNNING since 2026-11-23 01:56 UTC (ends about 06:56 UTC plus a final screen): `bash tools/rl_s2.sh
   s2b ckpt/fb2/it000900.npz 300 s2` (holdem-rl 0670e94; resumed at it 1836, pool x070 to x073, cycles from
   74, screens 2300 2700 3100 3500, logs `logs/s2b/`, end reason `logs/s2b/end.txt`). Plan reviewed twice,
   second REVISE fixed, then capped; code verifier CONFIRMED after the rotation restart fix (0670e94).
   S2's it1800 is the best so far: E4 53.25 against the 45.0 mirror, card probe 71.0 (screen 74.5).
   Acceptance adds E5, the extreme bots, no worse than v4 (`logs/allin/fb2_900_on.jsonl`).
   The style map is done (see Now); the diversity slice was replaced by roadmap Revision 2. E3 for the
   candidate uses three fresh probes `R_itN_f2/f3/f4` (train seeds 2 to 4, eval seeds 12 to 14) and
   `tools/probe_pool.py`.
1. Swap again only if a candidate beats rl-fb2-900 on the real field bots and ties or beats it on both gates, on fresh seeds; ask Wayne first.
2. rl-h4-900 (holdem-rl 4500e65): league FAIL 22/23 (A5 79.8; holdem-league f5441a0), h2h vs h4-300 60.5,
   heuristic 72.0. Not a swap candidate. Lesson: A5 sits on the 80% line; same-seed screening overstates.
3. Generalization A/B (gen1 with 48 generated archetypes vs ctl1, both from h4-300): stopped 02:44 UTC at
   about it1000. No gain: both plateau at field 90 with A5 around 80, both about 50% vs rl-17cf03f
   (research/experiments.md 14.2, research fff0d48). Screens in logs/sp_watch_{gen1,ctl1}/ on gb10-d.
4. Real field bots (holdem-fieldbots, merged into holdem-rl 71cbb87; 13 bots as `ext:<name>`, read in full,
   stdlib+numpy, Wolf in a --network none container): h4-300 wins only 49 to 64% against the Ashwing family
   and autodidact (clones of the same entrants: 84 to 89%). The 23-opponent gate does not measure the live
   field. docs/field_bots.md, research 14.3.
   fb1 (180 min, done): held-out Ashwing mean 57.4 (h4-300) -> 71.3 (it900); Wolf 84-90 -> 93-96.
   Candidate rl-fb1-900 = fb1 it900, weights rl/models/fb1_it000900.npz md5 f7428123. Fresh-seed verifier
   CONFIRMED (gb10-d ~/poker-ai-lab-league/out/verify-fb1-900). Image .cache/images/holdem-rl-fb1-900.tar.gz,
   sha256 8b4b4a45038c9fdc475895654c20ff26a1e7b028a51bf0764a199a3b8f3bd56f, local match vs lag won, 0 protocol
   problems, peak 93 MB. Test: ext:autodidact 71.8 (h4-300 63.7), real Blueprint 59.3 (h4-300 55.5); logs/fb_test/fb1_900.out.
   fb2 (from fb1-900, `tools/rl_fb2.sh`): it900 = rl-fb2-900, held-out Ashwing 77.2, autodidact 75.5, Blueprint 62.3.
   fb3 (same recipe from fb2-900) stopped at it300: overfits (held-out 75.5 -> 73.4, A5 79.7). Research 14.5.
5. Blueprint 100bb (matteo-psnt/poker-solver v0.1.0, 1.9 GB; Wayne approved, Docker with --network none
   only): branch holdem-bpopp, box dirs ~/poker-ai-lab-bp and ~/bp-data.
6. Image builds: `deploy/build_on_box.sh <model npz> <tag>` on holdem-rl (4d50c2a fixes root-owned cleanup).

## Traps
- A `bash -c "while pgrep -f PATTERN"` chain matches its own command line and never ends; wait on a pid
  with `kill -0`, then check what the pattern matches with `ps -eo pid,cmd | grep -F PATTERN`.
- `tools/league_add.sh`: never edit it while a run of it is active (bash reads scripts lazily).
- RL weights are `*.npz` and gitignored: commit with `git add -f`, or the league export has no model.
- numba is not deployable (pure Python plus numpy only on the host).
- chipzen.ai: one fetcher, stop on the first 429 (900 s IP block).
- gb10-d clock is UTC+8.
- `deploy/Dockerfile` copies rl files by name: a new runtime module or table must be added there and in
  `deploy/hf_package.sh`, or the image fails on import.
- Live NLHE round_start `stacks` are post-blind; take hand-start stacks from the previous round_result.
- ~/poker-ai-lab-rl on gb10-d is a copied tree (no git, CRLF files): sync every changed file, deploy/ included.
  A CRLF shell script there fails at once (`.venv/bin/activate
`): check `file x.sh` after syncing.
  Images are built from `git archive HEAD` by `deploy/build_on_box.sh`, not from that tree.
- `ext:` field bots are unseeded in holdem-rl, so on/off runs there differ by chance; holdem-x2r 30cfa1a seeds
  the Ashwing family and autodidact (pair them). `model:`, `policy:` and bpopp:v011 are seeded per match
  (holdem-rl acb29e9) and repeat byte for byte.
- An experiment's tests can pass while the result-deciding parts are wrong: commit a fault-plant runner with
  them (D2a: tools/d2_mutate.py, 25 plants).
