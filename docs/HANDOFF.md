# HANDOFF: Chipzen Season 16 hold'em bot

Updated 2026-11-23 21:05 UTC (box clock). Read "Now" first; the session context is compacted often, so this file is
the working memory. Update it at every step that changes state.

## Now
- **Wayne, 2026-11-23:** "The biggest fault that you made is thinking too narrowly"; reason from first
  principles. English only in this project, replies included. He accepts my recommendations when I judge
  them worth it (swaps still need his yes; chipzen.ai rate rules hold).
- **Plan: roadmap Revision 2** (`docs/research/roadmap.md`, research 12db6b1, committed and pushed). Levers: the floor (E3; S2, S2b), exploitation through an explicit opponent model plus a
  decision procedure (X1 model, X2 search with a safety blend), and real-arena measurement (M3: Season 16
  replays of v4). Headroom is measured first (M1). Review 1: REVISE, 4 blockers: X1 per-name
  check must compare against prior plus in-match; X1 held-out subsets, counts, minimum sizes, train-only
  fitting; M1 needs one statistic that 400 matches resolve, and a miss is inconclusive, not "floor leads";
  X1 runtime measured at 0.5 vCPU and 256 MB with a percentile. Review 2: REVISE, 3 blockers (selection
  on a validation split and held-out scored once; a stop for each acceptance; X1 ownership and cores).
  All fixed; the cap was reached, so no third review; Wayne's standing approval carries it (tell him).
- **X1 done** (holdem-rl 0967e71, merged and pushed; box tree synced): acceptance 1 PASS (known names,
  15,426 actions in 91 matches: prior+name+in-match 0.5438 vs prior+in-match 0.6237 nats, gain 0.0799
  [0.0681, 0.0923]); acceptance 2 PASS (unseen names, 1,425 actions in 10 matches, 4 names: prior+in-match
  0.7248 vs prior 1.1025, gain 0.3777 [0.1551, 0.5753], weak: 10 matches); acceptance 3 NOT TESTED until the
  box is quiet (PC p99 0.12 ms on 300 actions). Command, in the deployed amd64 image under QEMU (slower than
  the real host, so a pass is conservative): `docker run --rm --network none --cpus 0.5 --memory 256m
  --entrypoint python -v $HOME/poker-ai-lab-x1:/x1:ro -w /x1 holdem-rl-fb2-900-allin:latest
  tools/oppmodel_fit.py bench --data data --model rl/models/oppmodel.npz`. Selected: MLP prior hidden 64 on core+extras features, edges [0.35, 0.8],
  k 20, w 2, k_im 8; 11.8 KB npz, 66 names. Outputs `~/poker-ai-lab-x1/logs/x1/`. I read the fit code: splits,
  train-only counts and causal in-match counts are right. Fresh verifier CONFIRMED (no leakage; reproduced byte for byte). Recorded in research 14.13.
  Replays hide hole cards except at showdown (`hole_cards_hidden`), so ranges cannot be fit from replays
  directly.
- **Running on gb10-d:**
  1. S2b (main pid 18898), ends about 06:56 UTC plus a final screen; `logs/s2b/` (screen_itNNNNNN.verdict,
     STOP, end.txt). Screens at 2300, 2700, 3100, 3500. Screen 2300 (03:18 UTC): probe 79.25% [75.0, 82.9]
     (S2's best screen 74.5), Ashwing 69.5 and ashwing_search 73.0, no stop; main wins 27.4% against its pool.
     Screen 2700 (04:5x UTC): probe 77.75% [73.4, 81.6], Ashwing 74.0, ashwing_search 74.0, no stop.
  2. M1 training windows at 03:58 UTC: br_ashwing 91.2% (102 matches), br_autofast 87.5% (128). M1 best-response runs, 90 minutes each, holdem-rl d643881: `bash tools/rl_br.sh br_ashwing
     ckpt/fb2/it000900.npz ext:ashwing 90 3` (02:41 UTC, about 6 iterations a minute), and `br_autofast`
     with `ext:autodidact_fast` (02:46 UTC). The first `br_autodidact` run on the full `ext:autodidact` got
     7 matches a minute and was killed; its partial `ckpt/br_autodidact/` is unused. Logs `logs/br_*.out`.
  3. `bash tools/m1_eval.sh 6` (holdem-rl 05c4865, started 02:46 UTC) waits for both runs, then plays
     fb2-900, br_ashwing and br_autofast on seed 21: 800 matches against ext:ashwing, 400 against
     ext:autodidact, into `logs/m1/NAME_OPP.jsonl`, marker `logs/m1/done`, failures in `logs/m1/failed`.
     ext: bots are unseeded, so the gain is an unpaired difference with a Newcombe interval.
  4. Chip flow for M1 (03:14 UTC): `tools/chipflow.py` of fb2-900 against ext:ashwing, 400 matches, seed 31,
     into `logs/m1/flow_fb2_ashwing.{jsonl,txt}`; after br_ashwing ends the same for `ckpt/br_ashwing/latest.npz`
     into `logs/m1/flow_br_ashwing.*`, marker `logs/m1/flow.done` (chain pid 110140 waits with `kill -0 51579`;
     the first chain matched its own pgrep pattern and was replaced). The difference shows which decisions the
     fine-tune's gain comes from, which is where X2 should act first. fb2-900 result (03:30 UTC): 69.8% won;
     post-flop folds lose 1.04M chips, non-all-in showdowns 0.65M (0.26M where we bet last), Ashwing folds
     preflop 1.4% (a sticky caller); our river shoves gain 0.80M.
- **X2 design notes (spec waits for M1; nothing built):** opponent hand ranges from X1's action frequencies
  by mapping classes onto strength quantiles of the belief range (fold = weakest, raise = strongest, a
  bluff share later from showdowns), as in DBBR (Ganzfried and Sandholm, AAMAS 2011: model = smallest
  deviation from a reference strategy that matches observed frequencies). Showdown data is biased
  (arXiv 2608.09954, 2026-07-20: folds hide cards, missing not at random). Safety: deviate from the policy
  only where the model's interval separates from the reference (CS-RNR, arXiv 2607.28520, 2026-07-30).
  Leaf values: the PPO value net (in `ckpt/fb2/it000900.npz`, not in the deployed npz). Cost: the
  policy's `hand_strength` enumerates every opponent hand per call, so a range needs one 7-card rank per
  hand and a vectorized strength, not 1326 calls.
- **Universal test (Wayne asked 04:05 UTC how the universal approach gets approved):** eval card E6 = held-out
  styles (four gap-style rule bots plus ext:ashwing, ashwing_search, ashwing_hive, autodidact, Wolf family,
  never used in tuning), E7 = real arena replays (research 59f2d6f). X2 must tune on other bots
  (ashwing_v2, ashwing_value, autodidact_fast, chipzen, clones). The four rule bots (raise_station,
  sticky_overbettor, tight_sticky, never_fold_pre) are being built since 04:20 UTC by an executor in worktree
  `Desktop/poker-ai-lab-e6`, branch `holdem-e6` (from holdem-rl 0967e71, not pushed), box dir `~/poker-ai-lab-e6`,
  2 cores; done = style vector within 0.25 of target on seeds 3 and 7, tests, existing baselines unchanged.
  Targets from `poker-ai-lab/.cache/style_field.json`. DONE: holdem-rl 86d4ab9 (merged, pushed; box tree NOT
  synced yet, sync `holdem/opponents.py` and `tools/style_bots_check.py` after S2b and M1 end). 240 matches vs
  fb2-900, seeds 3 and 7: distance 0.10 to 0.21 for all four (60 matches: sticky_overbettor 0.37 on seed 7
  from a sparse fold_pre_raise axis). 23 tests pass; station, lag, jam play byte for byte as before.
- br_ashwing ended 04:11 UTC at it 580 (last window 92.4%); its chip flow runs; br_autofast ends about 04:17,
  then `tools/m1_eval.sh` starts.
- **M1 POSITIVE (05:01 UTC):** br_ashwing vs ext:ashwing 722/800 = 90.25% vs fb2-900 604/800 = 75.5%, gain 14.75,
  Newcombe [11.1, 18.4] (research 14.12). X2 chosen: a learned decision procedure under X1 (policy takes X1's
  belief as input), search kept as the fallback; X2a (X1 block in features.py and fastenv.c, parity,
  zero-weight widening) and X2b sketch in the roadmap (research 70fa46b). Review 1: REVISE, 5 blockers (no C
  interface for X1, width change breaks 56-wide consumers, vacuous parity, undefined probe states, no name rule).
  Revised (research cad6d7f): X2a now seeds the existing tracker counts (NST=15) from a per-name replay profile
  scaled to 20 hands; obs stays 56 wide; C gets env_set_stats; train.py --seed-profiles; E6 always nameless.
  X2b arms: base, grid (StyleBot grid), grid+seeded. Review 2: REVISE, 3 blockers (setter after reset wipes
  hands played inside env_reset; opponent-seat parity unreachable; profile check synthetic only). All checked
  and fixed (research b675d5e: env_set_prior applied inside reset, direct both-seat priors, real-replay count
  check vs extract_replay, all-in-for-less = call). Cap reached; proceeding on standing approval.
  X2a DONE and MERGED: holdem-rl 90baa6b (pushed), research 14.14 (708230a). Verifier CONFIRMED; its two test
  gaps fixed (dealer slots st[0], st[1] now checked, big-blind-dealer mutation fails with 139 mismatches).
  Seeding is OFF by default in RLBot (priors=PATH turns it on). Box ~/poker-ai-lab-rl NOT synced yet: sync
  after S2b and M1 end. Open: live display_name vs replay player name, answered by M3.
  NEXT: X2b spec after M1b eval (br_mix window at it 430: ashwing 94%, autodidact_fast 92% on ~50 each).
- **M1 05:49 UTC:** br_ashwing vs ext:autodidact 312/400 = 78.0% [73.7, 81.8] vs fb2-900 79.25%: no measurable
  specialization cost, but matches run 63.9 hands vs 41.3.
- **M1 DONE 06:18 UTC (research be087fe, 14.12):** br_autofast vs ext:autodidact 90.25% vs fb2 79.25%, gain 11.0
  [6.1, 15.9]; vs Ashwing 76.4% (+0.9, no cost, 46.0 hands vs 41.7). Both fine-tunes: big gain on target, no
  win-rate cost elsewhere, slower wins elsewhere. M1b eval of br_mix started at 06:18 (Ashwing first).
- **M1b half (06:28 UTC):** br_mix vs ext:ashwing 666/800 = 83.25%: +7.75 [3.8, 11.7] over fb2, -7.0 [-10.3, -3.7]
  under br_ashwing. Confound: br_mix ran 455 iterations with 4 SDK workers split over two bots (about half
  br_ashwing's Ashwing data). Autodidact half running (about 25 min).
- **M1b DONE 06:47 UTC (research 2f9bb6c):** br_mix vs ext:autodidact 87.25%: +8.0 [2.8, 13.2] over fb2, -3.0
  [-7.4, 1.4] under br_autofast. One net keeps most of both exploits on half the data each -> X2 as one policy
  on a broad population is supported.
- **RE-CENTERED 2026-11-23 ~07:35 UTC (Wayne: the point is UNIVERSAL, as asked at the start, with the limits I
  listed):** X2b's grid arms repeated the narrow move (enlarge a reactive policy's opponent list). X2 is back
  to search under X1 + safety blend (research f56fc6b, roadmap 'Correction'). X2b TRAINING ARMS NOT RUN; its
  code (style grid, held-out judge, profile eval) is kept as the test bed. Next: X2s spec covering the five
  listed limits (ranges from action model via frequency matching, leaf values, 1 s at 0.5 vCPU, confidence
  gated safety, match-win objective), grounded in literature and open-source code, then review, build.
  Progress is read against ceilings, not v4 (roadmap Revision 2 table, research 000f1ed).
- **X2s (Wayne: clean and tidy, no overdesign, avoid local optimum):** smallest end-to-end search under X1
  (research d86ab03): one-street chip EV per legal action, range from X1 bands by hand strength (others
  weight 0.1), equity by 200 runouts, blend = argmax only with evidence and EV gap > 0.05 pot, else policy.
  RLBot(search=True) off by default. Judge: X2b held-out judge + E5, decision log names the weakest part.
  Review: REVISE 1 blocker (raise EV facing a bet missed `- c`), fixed (research e886fec).
  X2s EXECUTOR running since ~07:50 UTC: worktree C:\Users\WEI-CHENG\Desktop\poker-ai-lab-x2s, branch
  holdem-x2s from c348a59, box dir ~/poker-ai-lab-x2s, cores 4-7, 2 box-hours. Builds rl/search.py,
  RLBot(search=True), search log, tests; measures p99 at 0.5 vCPU and a 100-match smoke eval on/off.
  BUILT f70ce33; smoke (chip EV) LOST 25-29 pts. DIAGNOSED (research 14.16, 46b6e51): effective-stack bug
  (2bcedd8) minor; ROOT CAUSE = chip-EV objective: true-model (oracle) search lost 59/81 vs policy 96/95,
  match-win utility (gambler's ruin) won 100/98. 8007e33 puts match-win utility in rl/search.py with one
  field K = 4.68 (v4 league 91.2%): X1 search ext:ashwing 71-79 vs policy 61 (60% of specialist gap), stations
  88-89 vs 95-96 (oracle 98-99: X1 is now the weakest part: unobserved fold buckets, collapsing band range).
  HELD-OUT JUDGE DONE 09:25 UTC (research 14.16, 3e1ee83): search ON LOSES pooled 86.6 -> 80.8 [-7.6, -3.9];
  ashwing +3.3 (ns), wolf -10.7, rule bots -6 to -11. Smoke 'ashwing 79 vs 61' was noise (off = 73 on seed 41).
  ORACLE at seed 41 x 300 on the 4 rule cells: 1101 vs policy 1099 of 1200 -> a one-street search only EQUALS
  the policy even with the true model; X1 costs ~8 more. Verifiers: 2x REFUTED (trips-board crash dbe9e3e;
  short-bb + finish_hand guard e6b27b8), cap reached, no third. Lazy import fix b74030e (deployed image
  lacks rl/search.py, rl/oppmodel.py). MERGED holdem-rl = b74030e, pushed; search off by default.
  NEXT: X2r spec = policy-improvement rollouts (our policy for us, model for them, match-win utility),
  tested with the ORACLE model offline first; runtime and model work only if it beats the policy.
  X2r BUILT df4e3c3 (holdem-x2r, worktree C:\Users\WEI-CHENG\Desktop\poker-ai-lab-x2r, not merged; tests +
  8 mutations). N=16 Z=2: pooled -0.7 [-2.9, +1.6] (research 14.17, a87f3e8), overrides 6-9% ~ noise rate.
  N=128 Z=2.6 (post hoc) DONE: pooled +3.8 [+1.9,+5.8], paired +3.8 [+2.3,+5.4] (research 14.17 c6eab96).
  CONFIRMED seed 43: paired +4.2 [+2.7,+5.7] p<0.001, all 4 cells positive (research 14.17 5405176).
  X2m (roadmap e27b4ff): x1 model built (4d9c1ed), memo f6777b8 (exact), tests c81f95f (9), run script
  bc84803. Verifiers 1 and 2 both REFUTED the TESTS only (impl correct: v1 reference 0 mismatches; live log
  gate check: all 3249 overrides > 2.6 se). All real mutations now killed (f427155, 14 tests). Two REFUTED
  = cap: no third verifier; surfaced to Wayne. Box x2m code md5 == committed.
  X2m FULL RUN LAUNCHED 12:13 UTC: gb10-d ~/poker-ai-lab-x2m, tools/x2m_run.sh (setsid), cores 4-19:
  logs/x2m_rule DONE 13:11: R FAILS, paired -3.8 [-5.7,-1.8] (sticky_overbettor -10.7: folds every street;
  research 14.18 e5289a8). Diagnosis: band model (bets = strong) wrong for wide-range bettors = limit 1.
  logs/x2m_ext DONE 16:27: E HOLDS, 5 distinct bots +3.1 [+0.4,+5.8] (wolf_v5 == wolf, dropped; 6-cell
  +2.9 [+0.6,+5.3]); Ashwing +5.7, ashwing_search +6.0 (research 14.18).
  SEED-43 CONFIRMATION DONE 20:48 (tools/x2m_confirm.sh 5ee89f5, own N=1 off arms, paired): E DOES NOT
  CONFIRM, five bots +0.9 [-1.3,+3.2] p=0.44 (Newcombe +0.9 [-1.8,+3.6]); ashwing +3.3, search +4.3,
  hive -5.3, autodidact +1.0, wolf +1.3. R fails again: -4.6 [-6.6,-2.6] (sticky_overbettor -13.3,
  raise_station -7.7). Research 14.18 046e99e. VERDICT: lookahead with X1 is NOT a candidate; procedure is
  sound (oracle +4.2 confirmed), the model is the limit. holdem-x2r stays unmerged (5ee89f5).
  ABLATION DONE 22:20 UTC (holdem-x2r cf0a867, verifier CONFIRMED; ~/poker-ai-lab-x2m/logs/x2ma_*; research
  14.19 7b31e0d): paired vs oracle, oracle-range -1.0 [-2.2,+0.2] (continuation loss, not significant),
  x1-range -9.0 [-11.0,-7.0] (range loss), x1 -8.8. THE ROOT RANGE CARRIES THE WHOLE LOSS. Overrides:
  sticky_overbettor preflop raise->fold 525 vs 93 with the true range; raise_station check->raise on
  turn/river 105/157 vs 21/54. Causes not yet separated: X1 frequency (band width) vs reveal (band rule).
  NEXT: X3 SPEC in roadmap. Review 1 REVISE (4: lam absorbs frequency error; variant chosen on held-out;
  midpoint band cut makes invariance approximate; no budget) -> all fixed in research 8a6ecb3; review 2
  REVISE (4: index-ordered ties, pi/mixture definitions, X1 in-sample on lam fitting data -> new X1-fit npz,
  outcome with no action) -> all fixed in research 2ba401f. Cap reached; proceeding on standing approval
  (told Wayne). X3a BUILT (holdem-x2r 2ab688a fitpart npz made on gb10-d torch, 3f5fff8 tool/tests/run
  script, 0ee9436; not pushed): 28 tests, 7/7 planted mutations killed; PC full replay smoke: held-out R1
  -0.73 vs R4 +0.37 nats, pi0 at lam 0.3-0.4, variant not chosen (unverified until the box run + verifier).
  FULL RUN LAUNCHED 23:12 UTC on gb10-d ~/poker-ai-lab-x3 (git archive with core.autocrlf=false: plain
  archive gave CRLF scripts), cores 4-12, logs/x3a/{report.txt,replay.json,sim/,failed,done}; ~80 min,
  ext:autodidact is the long pole. Executor installed chipzen-bot 0.7.0 + websockets into the PC Python.
  VERIFIER 1 REFUTED (23:40 UTC): (1) sim Hero.on_round_result skips sync on no-showdown hands, so X1 never
  observes trailing opponent folds: sim R1 != deployed Search (test twin shared the bug); (2) 5 wiring
  mutations survive (R2/R2l get X1 p, R2l uses lp4, pre/post lam swapped, V = R4-R1); (3) report pools
  whatever cells exist. Replay path unaffected. First run INVALID for sim (logs/x3a in ~/poker-ai-lab-x3,
  autodidact killed): do not cite its sim numbers. Its replay part: held-out R4-R1 +1.09 [0.98,1.22],
  variant not chosen. FIXED in holdem-x2r 4e51db8 (32 tests, 14/14 mutations killed, verifier's
  r1_vs_search 0 differences in 5 cells). RERUN LAUNCHED 23:46 UTC: gb10-d ~/poker-ai-lab-x3v2 (fresh LF
  archive of 4e51db8), cores 4-12, logs/x3a (report refuses if a cell is missing). Verifier 2 (cap 2)
  running in parallel (~/x3-verify2, cores 13-19). VERIFIER 2 CONFIRMED 4e51db8 (32 + 29 tests pass; X1
  counts == extract_replay on all 330 matches; sim parity with Search). Test debt, code correct: 7 replay-leg
  mutations survive (viewer name/seat, dead cards, step-3 cut, held-out model, variant by mean, held-out
  pairing); X1-fit hyperparameters were themselves selected on validation (spec's rule). Add tests if the
  replay leg is reused. X3a DONE 02:06 UTC (research 1b9dcb6, experiments 14.20): F +0.48 [0.45,0.51],
  V +0.20 [0.18,0.22], R4-R1 ext +0.33 [0.30,0.35], held-out +1.09 [0.98,1.22]: all clear -> X3b runs AND a
  frequency spec is owed. R1 is below the uniform prior (rule -0.34, held-out -0.73). Interaction -0.45:
  lambda mostly guards against wrong frequencies (lambda adds -0.02 under true freq). pi0 mean lambda 0.35.
  X3b BUILD dispatched 02:2x UTC to an executor in poker-ai-lab-x2r: `--model x3` (R4 root, X1Bot
  continuation), rl/models/x3_pi0.json, tools/x3b_run.sh (seed 49, off arms N=1, rule + 5 ext), tests and
  mutations. Then: outcome verifier, run on gb10-d, read (both pools LB > 0 -> confirm seed 51).
  BUILT holdem-x2r d0008b9 (not pushed): X3Root reuses x3_range.Ranges; 70 tests pass; 5/5 mutations
  killed; 4 old arms byte identical on rule cells (PC); ext cells not reproducible on the PC, so no ext byte
  check yet. Also touched holdem/engine.py: round_result carries community_cards at showdowns (risk: any
  bot reading round_result). Timing x3 ~ x1 (1.4 to 1.6 s per decision at N=128). Run: `bash
  tools/x3b_run.sh` (SEED 49 default, PY/CORES/WORKERS as x2r_run.sh). Verifier 1 running (also checks ext
  byte identity and the engine change on gb10-d, cores 13-19, ~/x3b-verify). VERIFIER 1 CONFIRMED d0008b9
  (tests 70 pass; 9 planted mutations killed; old arms byte identical incl. ext:wolf and seeded ashwing and
  autodidact on the box; N=1 x3 == x1 == plain policy on all 9 cells; community_cards read by nothing else).
  Note: ext:ashwing* (Random(None)) and ext:autodidact (global random) are unseeded, so their cells are not
  paired run to run; ~/x3b-verify/seeded.py wraps them with set_seed. X3b SEED 49 RUN LAUNCHED 03:07 UTC:
  gb10-d ~/poker-ai-lab-x3b (LF archive of d0008b9), cores 4-19, workers 16, `tools/x3b_run.sh`, marker
  logs/x3b49_done, waiter byv63m47o. Read: paired_stats.py on rule rows, x2s_stats.py on logs/x3b49_ext;
  candidate if both pools LB > 0, then SEED=51.
  X3b RULE CELLS DONE 06:25 UTC: pooled -1.7 [-3.6,+0.3] (paired_stats on cat'd off rows): NOT a candidate.
  sticky_overbettor -11.7 carries it (38.2 vs 17.9 hands per win); others +3.0, +2.0, 0.0. ext so far:
  ashwing 73.7 -> 82.7, ashwing_search 74.7 -> 83.3 (unpaired); hive, autodidact, wolf running, ETA ~08:30
  UTC. Then experiments 14.21, then X4 (frequencies) spec.
  D1 FETCH RUNNING since 06:29 UTC on gb10-d: `tools/fetch_chipzen_all.sh` (holdem-chipzen 8128b64) in
  ~/chipzen-fetch, out ~/chipzen-replays (seeded with the 330), log ~/chipzen-fetch/run.log and
  ~/chipzen-replays.pass.log, marker ~/chipzen-replays.done. 43,497 public poker matches, ~4.5 s each, ~3
  days; on 429 waits 30 min and resumes. It is THE one fetcher: do not start another (M3 rides on it).
  Roadmap now opens with "Where we are" and has X4 and D sections (research f2fe7f8).
  PLAN REVIEW (Wayne asked, then "go ahead"; research ec6b9f8): R1 runtime probe added; E3 for search
  candidates (exploiter vs the policy, then played vs the lookahead in SDK); ext seeding committed holdem-x2r
  30cfa1a (set_seed on Ashwing family + autodidact; tests/test_field_seed.py, fails without it) so ext
  cells now read paired. R1 timing tools holdem-x2r (tools/r1_timing.sh, tools/dec_time.py); PC run
  started ~06:4x UTC into logs/r1_timing_pc (background b795zje2p). Next for R1: the same script on gb10-d
  one core after X3b frees it (CORE=4), then the N=32/N=8 gain runs with seeded ext off arms.
  R1 PC TIMING DONE (one x86 core, per lookahead decision, mean/p95/max s): N=128 1.43-1.57 / 2.88 / 3.13
  (does NOT fit: about 3 s mean, 6 s max at 0.5 vCPU, over the 5 s limit); N=32 0.40 / 0.66-0.69 / 0.77
  (fits the rule: mean <= 0.5, max <= 2); N=8 0.11-0.12 / 0.17-0.18 / 0.20. So the gain runs are N=32 and N=8.
  R1 ON THE BOX 06:59 UTC (idle cores 1-3 while X3b holds 4-19): ~/poker-ai-lab-r1 (LF archive of holdem-x2r
  d4c3cb8), /tmp/r1_box.sh: timing calibration on core 1 (logs/r1_timing_box), then x3 N=32 rule cells,
  3 workers, OFF = ~/poker-ai-lab-x3b/logs/x3b49_rule_off (logs/r1_n32_rule); marker logs/r1_box_done.
  Box use 06:58 UTC: 16 of 20 cores at 100% (X3b), cores 0-3 idle, GPU 0%, 8 of 121 GB memory.
  Earlier: 01:17 UTC: 8 of 9 cells done; ext:autodidact at match ~65 of 200 after 88 min
  (about 1.4 min per match), ETA about 04:20 UTC, under the 6 h stop line. Waiter b333ni0hv (until done or
  failed is nonempty). Season 16 (read via ego-browser, logged in, 01:4x UTC; /api/seasons/16 is 403
  without login): 44 bots, round robin of 8 rounds x 22 fixtures, Tue 24 Nov 00:00 to Fri 27 Nov 23:59 UTC
  (fixtures start 18:00 UTC daily, 10 min apart), playoffs 28 to 29 Nov. Prize $200 (120/60/10/10). No
  fixture played yet; v4 listed 2nd at 0-0. v4: R1 vs MonteCarlo Tue 24 Nov 18:30 UTC; R2 vs fermat-mini
  22:50 UTC. Each fixture is one match: high variance. M3 replay fetch starts after the first fixtures.
  X3a = range quality, CPU, no lookahead (tools/x3_range.py,
  tests/test_x3.py on holdem-x2r): log share of the true combo minus prior, at hero decisions. Replays first
  on X1's split (fit / validation picks the pre/post lam variant, frozen / refit / held-out scored once).
  Sim seed 47, 200 matches x (4 rule + 5 ext cells), two-by-two on rule cells: R1 X1+band, R2 true freq+band,
  R4 X1+lam, R2lam true+lam, R5 oracle (report). F = freq part, V = reveal part, paired bootstrap.
  V LB>0 and R4-R1 LB>0 on ext pool and held-out replays -> X3b (--model x3, seed 49, confirm 51);
  F LB>0 -> frequency spec; neither -> rethink. Fractional bands (exact p_k). Budget 4 box-hours.
- **X2b SPEC written (research 64c0ae4):** GridStyle `stylegrid` (20 params, reject within R=0.6 of E6 bots),
  arms base / grid / grid+seeded from fb2-900, 180 min, 6 cores each, all --bot-clones; judge on E6 (4 rule +
  6 field cells) and a seeded-vs-unseeded clone check. Training waits until today's swap acceptance runs end.
  Review 1 REVISE (5) and review 2 REVISE (3), all fixed (research fed03e6): no Ashwing/autodidact/Wolf code in
  training; grid styles excluded in STYLE space (ALLOWED whitelist, >0.35 from E6 targets and 11 gap sources);
  skip bot:DeepStack,PoetAndCoder,MercuryRetrograde,AutodidactInnovations,SolvencyCheck (held-out profile set);
  decision on the 6 ext: cells only, 98.33% Bonferroni, fixed order seeded > grid > base; profile eval tool
  tools/x2b_profile_eval.py with NOT TESTED rule. Cap reached, proceeding on standing approval.
  X2b CODE EXECUTOR running since 07:00 UTC: worktree C:\Users\WEI-CHENG\Desktop\poker-ai-lab-x2b, branch
  holdem-x2b from 2c9dba7, box dir ~/poker-ai-lab-x2b, 2 cores, 1.5 box-hours. Builds code, tests, ALLOWED;
  smoke runs only. Training gate: logs/swap_acc/done (I write it when swap acceptance runs end).
- **S2b ENDED 07:02 UTC (max-minutes):** screens 2300 79.25, 2700 77.75, 3100 82.25, 3300 80.5; none beats S2's
  it1800 (74.5). CANDIDATE = ckpt/s2/it001800.npz (sha256 4989481c5e7d5d8b).
  SWAP VERDICT 07:20 UTC: NOT GATED, NO SWAP, v4 stays entered (research 14.15, 01868c7; league d554b8a).
  E1 FAIL 21/23 field 88.0 (A5 78.5, Blueprint clone 79.2; v4 91.2); E3 fresh probes 77.0/79.0/80.0 pooled
  78.67 [76.3, 80.9] (bar 70, v4 96.5); E5 FAIL station 95.0 vs v4 97.75 [95.8, 98.8]; E2 pass; E4 53.25 pass.
  Floor recipe plateaued (7 screens it400 to it3300 read 74.5 to 88.75); next floor step needs a new plan
  revision, not S3 = more of the same. logs/swap_acc/done written on the box (X2b training gate open).
- **S2b screen 3100:** probe 82.25% [78.2, 85.7], Ashwing 73.25, search 74.5, no stop. S2b screens 79.25, 77.75,
  82.25 are all above S2's best (it1800 74.5, it400 74.75): continuing the recipe is not lowering the probe.
  Candidate is S2 it1800 unless screen 3500 or the end beats 74.5. Acceptance after S2b ends (about 07:00):
  three fresh probes `bash tools/exploit_probe.sh C C s2_it1800_fS S 1S` (S = 2, 3, 4), probe_pool under 70%,
  then E1, E2, E4, E5 (and E6), fresh verifier, then put the swap to Wayne (window closes 23:59 UTC).
- **M1b eval CHAINED:** `tools/m1b_eval.sh 6 168504 54302` (holdem-rl 2c9dba7), pid 286300, waits with kill -0
  on br_mix training and m1_eval, then br_mix vs ext:ashwing 800 + ext:autodidact 400, seed 21 ->
  logs/m1/br_mix_*.jsonl, marker logs/m1/mix_done, log logs/m1/m1b_eval.out.
- **M1 preliminary (chip flow, seed 31, 400 matches each, unpaired):** br_ashwing wins 90.2% against Ashwing,
  fb2-900 69.8% (gain about 20 points, interval roughly [15, 26]). The gain is a whole-strategy shift: first
  preflop action raise 64.7% (fb2 32.3%), showdowns where we bet last +531k chips (fb2 -261k), fewer but
  better-called river shoves (248 vs 635). The formal M1 statistic (`tools/m1_eval.sh`, running since 04:17
  UTC, ends about 07:00) decides. fb2-900 vs ext:ashwing on seed 21: 75.5% [72.4, 78.4] over 800. fb2-900 vs ext:autodidact: 79.25% [75.0, 82.9] over 400. Files `logs/m1/flow_{fb2,br}_ashwing.txt`.
- **M1b (04:19 UTC):** `bash tools/rl_br.sh br_mix ckpt/fb2/it000900.npz ext:ashwing,ext:autodidact_fast 90 4`.
  Question: does one network hold both exploits when trained on the mixture? If yes, the generalist's gap is
  the training population, and X2 can be an opponent-conditioned policy (X1 predictions as inputs) trained on
  a broad population; if it falls well short of the two BRs, conditioning or search is needed. Evaluate it
  like M1 (800 vs ext:ashwing, 400 vs ext:autodidact, seed 21) after m1_eval finishes.
- **Season 16 swap window closes today, 23:59 UTC.** An S2b candidate can be a swap option only if it
  passes acceptance before then, and only with Wayne's yes.
- **Done 2026-11-23:** style map (holdem-rl 3ef434e `tools/style_map.py`; research 14.11: 12 of 51 field
  bots play 4 styles no opponent of ours plays; data `logs/style/` on gb10-d). Protocol fact: match_start
  `seats[].display_name` is the opponent bot's platform name (chipzen-sdk TRANSPORT-PROTOCOL.md, aa8c55c);
  `participant_id` changes every match.
- **Correction owed to Wayne:** 140 of 330 poker replays (42%) end before hand 21, median 26. I had told him
  most matches end before the first blind step.
- **Next:** fix the review, second review, commit the roadmap; read M1 and apply its rule; then X1 or the
  floor. After S2b ends: three fresh probes `R_itN_f2/f3/f4`, `tools/probe_pool.py`, E1, E2, E4, E5, a fresh
  verifier, and Wayne's yes before any swap. From 24 Nov: fetch v4's Season 16 replays for M3 (one fetcher,
  stop on the first 429).

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
poker-ai-lab (holdem-chipzen), -league, -rl, -adapt, -br, -blueprint, -search, -research.

## Goal (Wayne, 2026-11-22 13:30 UTC)
The long-term strongest bot, a "future king". The Season 16 deadline no longer matters, and fb2-900 stays
entered. Plan: `docs/research/roadmap.md` on branch research, slices S1 to S7: measurement harness, league
with exploiters, showdown memory, range belief, a wider bet set, river search, then capacity. Key fact:
an exploiter trained 2 minutes against fb2-900 beats it 96.5% (fb2-900 folds after the flop too often), so
exploitability (E3) is a primary metric next to the league and the real bots.

## Season 16 entry (swapped 2026-11-22 18:45 UTC, Wayne approved)
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
- `ext:` field bots are unseeded, so on/off runs against them differ by chance; `model:`, `policy:` and
  bpopp:v011 are seeded per match (holdem-rl acb29e9) and repeat byte for byte.
