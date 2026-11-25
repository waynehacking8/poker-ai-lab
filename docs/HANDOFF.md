# HANDOFF: Chipzen Season 16 hold'em bot

Updated 2026-11-25 05:39 UTC. Read "Now" first; the session context is compacted often, so this file is
the working memory. Update it at every step that changes state.


## Now (2026-11-25 06:42 UTC, box clock UTC+8)

**Standing rules from Wayne:** English in this project (he may write Chinese; when he asks for an explanation in Chinese, answer in
Traditional Chinese). Think from first principles, not narrowly. Goal is the long-term "future king", not the
Season 16 deadline. He accepts my recommendations when worth it; uploads and swaps still need his explicit yes.
Process gates still hold: plan-verifier READY/REVISE (cap 2), outcome verifier CONFIRMED/REFUTED. Keep gb10-d
busy on purpose. Plan of record: `docs/research/roadmap.md` on branch research ("Where we are" at the top).

**Done this session (research a6fd1d3, pushed):**
* 14.24 X4 step 2: k_im sweep, CHOSEN none (best k_im 4, lower bound -0.0001); k_im stays 8. Verifier CONFIRMED.
* 14.25 D2a stage 2: Wolf and autodidact clones trusted from 1,000 matches; Ashwing not (5,000 clone +6.8).
  Every adaptive clone is easier than the real bot by 2 to 7 points; better likelihood, weaker clone.
* 14.26 M3 first read. CORRECTION: the MonteCarlo loss (2026-11-24 18:30 UTC, match 4b2a2beb) IS v4's Season 16
  round 1 fixture, the fermat-mini win (22:50 UTC) round 2; the API labels both `challenge`. Season 1-1 after 2
  of 8 rounds. Flop overfold measured (60.7% folds vs a 39.5% break-even at half pot); river shoves pay against
  callers. The site's "1-0, 100%" counts rated matches only (round 1 is unrated). Probes: holdem-chipzen
  `tools/m3_leaks.py`, `tools/m3_flop_aggr.py` (a6ff531).
* A Fable 5.2 agent rethought the roadmap (read-only). Adopted as roadmap **Revision 3** (research ef5bb38): the
  judge is aimed at the wrong opponents (ext: pool is one family; the archive's top is a solver-like family,
  Blueprint/NashForge/fermat6/MonteCarlo, plus small-ball aggressors like slopBot). X4 per-name prior and D3
  stopped; Phase 0 = S2r, P0, T1, A0, T2, D2b, L0 (L0 = live challenge series, needs Wayne's yes).
  Facts re-checked first-hand: fixture times, fb2-900 opens 3% of SBs in the first 10 hands, R1 per-cell
  numbers, bp100 at 400 matches in 70 s.

**Results since (research 4107aa1, 85447e2):**
* 14.27 S2r: fb2-900 vs bp100 59.85% [58.3, 61.4] at n = 4,000 (seed 81); it1800 minus fb2-900 -1.1 [-2.8, +0.6]
  paired, so B1 starts from fb2-900. P0: fb2-900's lost matches end in a commitment under 0.35 equity 77.6% of
  the time, bp100's 47.8%: +29.8 [+26.7, +32.9], **B0 fires** (big-pot play-time logic goes before G1, X5, B1).
  Main ways: flop shoves called (chip-positive, bust-heavy: a match-equity error), river calls of bp100's
  shoves at 0.198 equity (-2.46M chips). River shoves pay (+5.8M), leave them.
* Revision 3 envelope settled (reviews 1 and 2 REVISE, fixed, cap reached, standing approval).
* T1 spec final after plan reviews 1 and 2 (research 173d776; cap reached, standing approval). Executor in a
  holdem-rl worktree builds `make_opp("bp100")`, `tests/test_t1_bp100.py` (4 tests with plants), `tools/t1_run.sh`;
  then a fresh verifier; then I launch `tools/t1_run.sh` with `setsid -f` (120 min training, 4,000-match read).
* 14.28: match value vs bp100 is near linear (K = 0.80, not 4.68); 14.27's flop-shove reading withdrawn.
* **Ordering adopted (research 71c52db, roadmap "Ordering after Phase 0", Fable's):** K1 and B0b cut; T2, D2b,
  A0 Part 3 deferred; B0 step 1 HELD until T1's chipflow read (revised exact-oracle design recorded); critical path
  T1 read → B1 spec → B1 training 26-28 Nov → candidate reads 29 Nov → verifier, then Wayne, 30 Nov earliest.
* 14.29 (research 543d0d4): A0 field map. Two pools: entrants face the ten regulars in 5.4% of seats; they face
  Blueprint 15.4%, fermat6 6.8%, NashForge 6.1%, hoops 5.8%, mr_hide 5.7%, r0ckGarden 5.3%, slopBot 2.7%. slopBot
  rates first and over-folds small flop bets by 44 points; 5 of top 10 exploitable (L8 over-weighted). Verifier
  found an inverted best-opponent rate; fixed (holdem-x2r 1d2dd06) and rerun.
* **T1 RUNNING** since 05:38 UTC on gb10-d (verifier CONFIRMED; `tools/t1_run.sh`, 120 min training, then the
  4,000-match read; outputs ~/poker-ai-lab-rl/logs/t1/, ckpt/br_bp100). Read expected about 07:50 UTC; then
  `tools/p0_read.py` on logs/t1/flow_br.jsonl decides B0 step 1 (ordering). Strength sanity: bp100 beats
  `small_ball` 57.0% (strength cell).
* G1 RUNNING since 05:35 UTC (holdem-d2 `tools/g1_run.sh`; ~/poker-ai-lab-d2s2/logs/g1/run.log, per-step
  .done markers, `failed` on error, rule in logs/g1/rule.txt). base_fold0 crashed 06:01 (x3_range KeyError on
  one-sided showdown reveals); fixed in `g1_read.lam_scores` (holdem-d2, those hands replayed, not scored),
  resumed 06:03; fold 0 and 1 done at 06:30.
* **14.30 C1 FIRED (research 16fb10b):** best response vs `small_ball` 97.6% vs fb2-900 75.7%, paired +21.9
  [+19.9, +23.8]; `tight_sticky` -4.0 [-5.5, -2.4]. `small_ball` joins B1's training.
* **B1 spec in roadmap (research 6e0f647, 4435d81):** Fable's draft; plan review 1 REVISE (E1 command and
  disjoint pair ranges 400-499 screen / 200-399 gate via new holdem-league `tools/league_fresh.py`; test 1 unit;
  literal `rl.train` command with pinned input hashes and frozen `pool_b1`), fixed; plan review 2 REVISE
  (registry, screen score, test 1 keys, P2 branch and lock, writes and rollback), fixed (research d23f111); cap
  reached, standing approval. **Executor building since 06:42 UTC** in worktrees poker-ai-lab-b1rl (b1-rl),
  poker-ai-lab-b1x2r (b1-x2r), poker-ai-lab-b1lg (b1-league); box test copies under ~/b1-build only; no
  container job before T1 ends. Then a fresh verifier, then I launch `tools/b1_run.sh P1|P2` (T1 picks).
* A0 and T1 agent worktrees sit under poker-ai-lab/.claude/worktrees
  (commits already cherry-picked); remove them at cleanup.
* **Wayne 2026-11-25: act on Fable's recommendations, open questions go to Fable; memory and docs English only**
  (reading guide translated on all five branches, 90208e5 here). L0 stays parked: outward.

**gb10-d:** bpopp queue: T1 run (until about 07:50 UTC), then B1. Cores 0-5: free (C1 done). Cores 18-19:
G1 (running). GPU: G1 fits. Fetcher pid 1838186, the only one.

**Branches not pushed (local only, by rule):**
* holdem-x2r, `C:\Users\WEI-CHENG\Desktop\poker-ai-lab-x2r`, tip cb12f5f (X3a/X3b/R1/X4 tools; ext bots
  seeded since 30cfa1a).
* holdem-d2, `C:\Users\WEI-CHENG\Desktop\poker-ai-lab-d2`, tip d621a16 (D2a; 21 tests; `python
  tools/d2_mutate.py --jobs 4` must report 25 of 25 plants caught after any change).
* Leftover agent worktrees under `poker-ai-lab\.claude\worktrees\` are harvested (their commits are in
  holdem-x2r); delete them when convenient.

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
