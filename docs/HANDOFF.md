# HANDOFF: Chipzen Season 16 hold'em bot

Updated 2026-11-23 04:20 UTC (box clock). Read "Now" first; the session context is compacted often, so this file is
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
  Targets from `poker-ai-lab/.cache/style_field.json`. On report: verify, merge into holdem-rl, sync the box
  only after S2b and M1 end.
- br_ashwing ended 04:11 UTC at it 580 (last window 92.4%); its chip flow runs; br_autofast ends about 04:17,
  then `tools/m1_eval.sh` starts.
- **M1 preliminary (chip flow, seed 31, 400 matches each, unpaired):** br_ashwing wins 90.2% against Ashwing,
  fb2-900 69.8% (gain about 20 points, interval roughly [15, 26]). The gain is a whole-strategy shift: first
  preflop action raise 64.7% (fb2 32.3%), showdowns where we bet last +531k chips (fb2 -261k), fewer but
  better-called river shoves (248 vs 635). The formal M1 statistic (`tools/m1_eval.sh`, running since 04:17
  UTC, ends about 07:00) decides. Files `logs/m1/flow_{fb2,br}_ashwing.txt`.
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
