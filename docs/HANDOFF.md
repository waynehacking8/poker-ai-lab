# HANDOFF: Chipzen Season 16 hold'em bot

Updated 2026-11-25 05:39 UTC. Read "Now" first; the session context is compacted often, so this file is
the working memory. Update it at every step that changes state.


## Now (2026-11-25 14:10 UTC, box clock UTC+8)

**Standing rules from Wayne:** English in this project; when he writes "中文說明", answer in Traditional Chinese.
Think from first principles, not narrowly. Goal is the long-term "future king", not Season 16. Act on Fable's
recommendations; open questions go to the Fable roadmap agent, never to Wayne. Uploads, swaps and L0 live
challenges need his explicit yes and are not raised. Process gates hold: plan-verifier READY/REVISE (cap 2),
outcome verifier CONFIRMED/REFUTED. Memory and docs English only. On every new result, update the matching doc
(experiments, roadmap, HANDOFF) and drop what is stale. Plan of record: `docs/research/roadmap.md` on branch
research ("Where we are" at the top). Times here come from `ssh gb10-d 'date -u +%H:%M'`.

**State (details in experiments 14.27 to 14.31 and the roadmap's B1 spec):**
* T1 (14.31, verifier CONFIRMED the numbers, one sentence corrected): bp100-trained 79.7% vs fb2-900 59.85%,
  +19.9 [+18.1, +21.6]. B1 takes branch A (P1, with bp100). B0 step 1 does not run (river call-offs 594 → 57).
* C1 (14.30): `small_ball` 75.7% → 97.6%; `small_ball` is in B1's training.
* **B1 TRAINING STOPPED 13:27 UTC by the entropy guard** (minute 263 of 360, it 2290: entropy 0.465 → 0.195 and
  policy loss 0.64 in one iteration; last good checkpoint it002200, latest.npz excluded). Read set therefore 300 to
  2,100 (seven). Containers gone, lock free. **False alarm (14.35, research a0789f3; Fable review, reproduced):**
  train.py logs the last minibatch, often a 1 to 306 sample tail; the weights moved normally. Read unaffected.
  Fix for the next run (batch-mean logging, approx_kl and n, tail fold, 3-row guard) is with an executor on b1-rl;
  next-run budget 180 minutes needs a dated amendment.
  * **Screen done 13:49 UTC: chosen it001200** (sha256 5e9c6fc6…). Score 70.53 (bp100 65.3, tight_sticky 92.0,
    sticky_overbettor 78.6, small_ball_b 80.4; never_fold_pre 93.8, loose_passive 90.6; league lowest 83.5). All
    seven pass the 78% league filter; scores 68.8 to 70.5. Rows x2r logs/b1/screen/, league out/b1/screen-itITER.
  * **Confirmation running since 13:50 UTC** (`b1_judge.sh confirm .../it001200.npz`, log logs/b1/confirm_run.out,
    rc ~/b1_confirm.rc). The cores 18-19 baseline job (ext:autodidact, then ext:wolf) still runs; confirm skips
    finished fb2 cells. **After both end:** move logs/b1/confirm/fb2/ext:wolf.* to confirm/fb2_1819/, rerun the same
    confirm (only wolf's fb2 arm runs), then `b1_read.py confirm` with --gate after the E1 gate.
  * Code shipped: b1-rl a4d765d → ~/poker-ai-lab-rl, b1-league 857660c → ~/poker-ai-lab-league, b1-x2r 50b0a28 →
    ~/poker-ai-lab-x2r. Verifier 1 REFUTED (4 launch defects, fixed); verifier 2 REFUTED only on the judge's bp100
    cells not pinned (x2r's own bpopp lacked BP_CPUSET), training side all held. Fixed in b1-x2r 50b0a28 (test and
    plant caught, 29 x2r tests pass, live probe from ~/poker-ai-lab-x2r prints --cpuset-cpus 0-17). Verifier cap
    reached on this claim; the fix was checked first-hand.
  * After training: `tools/b1_judge.sh` from ~/poker-ai-lab-x2r (screen seed 94 and league pairs 400-499, then
    confirm seed 95, then gate pairs 200-399 plus heuristic head to head); it calls bare `python`, so put
    ~/poker-ai-lab-rl/.venv/bin on PATH. Report the chipflow shove table (14.33). Fallback P1b if no checkpoint
    passes the league screen. Delete ~/b1-build after the reads.
  * **Amendment 10:09 UTC before any read (research 4732eda):** read set to 2,700 plus latest; `loose_passive`
    guard cell (mr_hide's style); headroom and decision-share lines; fb2-900's seed-95 baseline arm now on cores
    18-19. Built in b1-x2r e3cc88d, verifier CONFIRMED; then 8be6e38 (confirm stops on a missing guard cell,
    37 B1 tests, plant caught), all shipped to ~/poker-ai-lab-x2r. **Before confirm:** move
    logs/b1/confirm/fb2/ext:wolf.* to confirm/fb2_1819/ so wolf's fb2 arm reruns with the candidate's placement
    (wolf thinks on a 300 ms wall clock). `loose_passive` params frozen (distance 0.152 and 0.150 on seeds 3 and 4). fb2-900 baseline arm
    (`b1_judge.sh baseline`, cores 18-19) wrote 10 of 12 cells to logs/b1/confirm/fb2/; ext:autodidact and
    ext:wolf finish about 13:00 to 13:30 UTC, marker ~/x2r_baseline.rc (0 = complete; rerun the same command if it
    dies, finished cells are skipped).
* **14.32 G1 (corrected, research a591050), rule 2:** a known-name model. Verifier REFUTED the first record:
  rule 2 had joined opponents' rows (149 names); fixed in holdem-d2 3e988c8 (test 9, 2 plants caught), rule rerun:
  29 names, R +0.183 [+0.123, +0.266], P -0.306 better than per-name X1. Unseen names fail; cold start stays X1.
* **14.33:** T1's shoves are chip-positive on every street (P0 retired as a decision statistic; B1's read adds the
  shove class table). Pure bp100 specialization costs -13.4 [-14.9, -11.8] on other styles (seed 98), so B1's
  guards are the risk; fallback P1b (bp100 2 of 12, seeds 99/100, league pairs 500-599) pre-registered.
* **14.34 G1 step 2a (research 5b1c5ca): rule FAIL** on one calibration bucket (autodidact_fast largest bucket
  5.16 points vs 5.0); the R condition passes for all three bots (G1 fine-tuned beats λ by +0.43 to +0.64 and D2a
  from scratch by +0.13 to +0.47 nats at 1,000 matches). Per the rule G1 gets no more GPU; any follow-up is a new
  pre-registered slice. Branch g1-2a f3d1afd (local). Verifier: numbers confirmed; FAIL holds under the spec's
  postflop bucket definition (7.07 points, stable over three seeds), research 13712ca. Fable: no new G1 slice; the
  lookahead line stays parked until B1's read shows the adaptation headroom per class.

**gb10-d:** bpopp queue and cores 0-17: B1 confirmation. Cores 18-19: B1 judge work and fb2-900's seed-95 baselines. GPU: idle (Fable: nothing worth it). Fetcher pid
1838186, the only one.

**Branches not pushed (local only, by rule):** holdem-x2r (poker-ai-lab-x2r, 159e9ba), holdem-d2
(poker-ai-lab-d2, 2520b27; `python tools/d2_mutate.py --jobs 4` must catch every plant after a change),
holdem-rl (poker-ai-lab-rl, 114a136), and the three B1 branches above (merge into holdem-rl, holdem-x2r,
holdem-league after B1's read).

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
- **Live (read 2026-11-25 14:05 UTC, chipzen.ai/season/16 in ego-browser):** 44 bots; round robin Tue 24 to Fri 27
  Nov, playoffs Sat 28 to Sun 29 Nov; prize $120/$60/$10/$10. v4 is 15th, 1-1: lost to MonteCarlo (R1, 24 Nov
  18:30), beat fermat-mini (R2, 22:50). Next: stebin-bot-here 25 Nov 18:10 UTC (R3), ALEXANDRA 22:30 (R4). Season
  replays carry `match_type: "challenge"`.
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
