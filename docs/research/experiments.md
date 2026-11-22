# Experiment log

Everything here was measured on my own hardware (a 20-core aarch64 box with
an NVIDIA GB10 GPU), with code in this repository. Match counts and 95%
confidence intervals are given wherever a number decides something. The code
lives on local work branches that are not published yet; file paths below are
relative to the repository root on those branches.

The ship gate I set for the bot: at least 80% simulated match wins against
every test opponent, each one separately.

## 1. The real match format and field (Chipzen replays)

Source: 412 completed heads-up replays from the public match API, fetched
politely (3 s between requests, stop on the first HTTP 429; the site blocks an
IP for 900 s after a burst). 330 are no-limit hold'em, with 10,516 hands and
70 distinct bots; the rest are 2-7 draw, OFC and another game. Tools:
`tools/fetch_chipzen_replays.py`, `tools/analyze_chipzen_replays.py`.

* Format: 10000-chip stacks, blinds 50/100. The big blind steps to 150, 200,
  300, 400 and 600 at hands 21, 41, 61, 81 and 101. Play continues until one
  bot busts. No hold'em replay reaches hand 121; OFC replays on the same
  platform go on to 800 at hand 121 and 1000 at hand 141, so I assume the same
  for hold'em.
* Match length: median 25.5 hands, mean 31.9 over all 330 matches. The 29
  Season 15 fixtures I read first had a median of 44.
* Field tendencies (Season 15 fixtures): the button raises first in about 75%
  of the time, button VPIP is about 90%, the big blind defends about 55%, and
  about 40% of players fold to a raise.

## 2. Simulator conformance

`holdem/engine.py` plays on the real SDK objects. `tools/replay_conformance.py`
replays every real hand through it in strict mode (any action outside the
engine's legal set fails) and compares ending stacks with the replay.

* An independent review found two rules that differed from the server. A big
  blind that is all in for no more than the small blind's post gets no
  small-blind prompt on the server; the excess is refunded. And blinds rose
  past 600 on the server but not in the engine.
* Before the fix 10,504 of 10,516 hands passed; after it, 10,516 of 10,516
  pass with ending stacks equal to the replay.
* The same review found a bot leak in that spot: facing a short all-in big
  blind (43 to win 186), the bot folded 15 of the 156 hand classes tested. It now calls
  exactly when equity is at least the pot odds.

## 3. Push/fold layer

CFR+ over 169 hand classes, stacks 2 to 25 BB, exploitability under 5e-6 bb
per hand. Compared with published heads-up Nash ranges (mean range width):

| stack | SB shove, ours / published | BB call, ours / published |
|---|---|---|
| 5 BB | 70.5 / 74.1 | 62.0 / 68.6 |
| 10 BB | 58.3 / 56.6 | 37.5 / 38.5 |
| 15 BB | 45.8 / 45.7 | 28.5 / 28.4 |
| 20 BB | 39.4 / 40.9 | 21.7 / 21.7 |

The 5 BB gap is unexplained. About 1% Monte Carlo noise in the class equity
matrix is one suspect.

## 4. Heuristic bot against seven baselines

400 seat-swapped duplicate matches per opponent, on the corrected engine
(`results/holdem/arena_seed1.jsonl`, `arena_seed2.jsonl`). Seed 2 was never
used for tuning.

| opponent | seed 1 | seed 2 |
|---|---|---|
| station | 96.0% | 95.5% |
| reference | 90.2% | 90.0% |
| nit | 88.2% | 86.0% |
| random | 83.0% | 79.0% |
| maniac | 71.8% | 72.8% |
| lag | 71.5% | 69.2% |
| station_raiser | 69.8% | 72.0% |

Decision latency on one core: p50 2.9 ms, p99 10.3 ms, max 29.4 ms.

What I tried before this, from `reports/holdem-iterations.md`:

1. Replacing rule-based postflop play with one EV rule over fold, call and
   several bet sizes raised the lag result from 60% to about 68%.
2. A win-probability utility instead of chips did not help, whether more
   risk-averse or more risk-seeking.
3. Raising Monte Carlo samples from 500 to 1500 per decision changed nothing,
   so equity precision is not the limit.
4. Against the maniac the bot wins about 8 bb per hand but loses matches to
   one or two all-ins.

## 5. League against replay clones

`league/` fits opponent clones to the replays. It clusters bots into 6
archetypes and fits 10 per-bot clones. EM over the hidden hole cards
de-censors folds, because cards are only shown at showdown. On held-out
replays the EM clones matched 10, 12, 12 and 10 of 15 statistics across four
archetypes. A naive showdown-only fit matched 5, 5, 12 and 5.

First leaderboard (older bot commit and older engine, so only indicative): a
field-weighted 77.8% match-win rate [75.1, 80.6], passing 9 of 23 opponents on
the point estimate.

Leaderboard on the corrected engine, 400 seat-swapped matches per opponent
(`reports/league/leaderboard.md` on `holdem-league`, commit 955a021). The gate
counts an opponent as passed when the point estimate is at least 80%.

| entrant | method | opponents passed | field win % [95% CI] | lowest opponent |
|---|---|---|---|---|
| rl-17cf03f | PPO policy, section 10 | 22 of 23 | 89.4 [88.2, 90.7] | PoetAndCoder clone 79.5 |
| adapt-v1 | decision model, first version | 22 of 23 | 86.0 [84.5, 87.4] | maniac 74.5 |
| chipzen-102b05e | heuristic bot, section 4 | 8 of 23 | 76.0 [74.3, 77.7] | archetype A5 64.0 |

Head to head, the RL policy beat adapt-v1 57.5% and was even with the
heuristic bot (48.0%) over 200 matches each. The heuristic bot beat adapt-v1
61.0%. Beating the field and beating each other are different skills here.

One caveat applies to both learned entrants. The six archetype clones they
trained against were fitted on replays that include the ten bots whose
per-bot clones are the held-out test, so their per-bot clone numbers are
somewhat optimistic. A refit without those ten bots is in progress.

## 6. Does knowing the opponent fix it? (oracle-prior probe)

`scripts/adapt_probe.py` first measures each opponent's true frequencies over
200 matches. It then gives the bot those frequencies from hand 1, with
near-infinite weight. 400 matches, seed 1.

| opponent | normal | oracle prior |
|---|---|---|
| station_raiser | 69.8% [65.1, 74.0] | 85.3% [81.4, 88.4] |
| maniac | 71.8% [67.1, 75.9] | 75.3% [70.8, 79.2] |
| lag | 71.5% [66.9, 75.7] | 62.8% [57.9, 67.3] |

Against station_raiser, the bot was simply learning too slowly. Against lag,
exact frequencies made it worse. Lag folds only to bets over three quarters of
the pot, but the bot's model has one fold rate for every bet size, so it
bluffs at the wrong sizes once it trusts the measured rate. This is why the
next design is a decision model: an online opponent model that is
conditioned on bet size, plus a search that maximizes match-win probability.
A single strategy with better statistics is not enough.

## 7. Best-response ceilings

* Fold-or-shove only, against the card-blind maniac (`tools/match_ceiling.py`,
  exact DP over hand number and stack): 66.6%. This was computed with the old
  600 cap. It restricts our strategy, so it is a lower bound on the true best
  response.
* Full best response against the maniac: an expectimax over the real betting
  tree inside an outer DP over hand number, stack and position. Hand strength
  is bucketed into 25 equity buckets per street. The computed match-win value
  is 87.4% at 10000 stacks. The bot that plays this table won 1751 of 2000
  arena matches, 87.55% [86.0, 88.9], 16.7 hands per won match. The DP value
  and the arena agree, so 80% against the maniac is reachable. The current
  heuristic bot gets 72% and the first decision model 74.5%.

## 8. River search and safe exploitation

`search/`: vectorized CFR+ over 1326 combos with a safe re-solve gadget, and
Ganzfried-Sandholm safe exploitation.

* Exploitability at 100 iterations: 1.6 to 1.9% of the pot.
* When the solver is given a too-narrow opponent range, the opponent's gain
  from the unsafe re-solve is 21 to 28% of the pot, against 0.6 to 0.7% with
  the safe gadget.
* A river resolve costs about 0.5 s median on the x86 estimate, which just
  fits. Turn solving does not fit (3.7 s).

## 9. Chip-EV blueprint

`blueprint/` on branch `holdem-blueprint`: external-sampling MCCFR with RM+
and linear averaging, tables at 15, 25, 40, 60 and 100 bb. Cards use 169
preflop classes and 64 equity buckets per street. Preflop actions are
open to 2 or 3 bb, 3-bet, 4-bet and all-in; postflop bets are 0.33, 0.66 and
1 pot plus all-in. The tables total 17.9 MB. A lookup takes about 1 ms
postflop in pure Python.

* As a bot on its own it wins 56 to 78% of matches against most opponents
  and passes 1 of 23 (reference, 95%). It is a chip-EV equilibrium
  approximation, and short winner-take-all matches against weak bots reward
  exploitation, not balance.
* Exploiting a known type from this base, measured against station_raiser
  with a counter solve capped in total variation from the blueprint, gave
  58.8% (blueprint), 67.5% (cap 0.3), 70.5% (cap 0.6) and 71.3% (uncapped),
  400 matches each. Exploitation from an equilibrium base is worth 10 to 12
  points, not enough on its own.
* A match-value DP says that with a real edge the bot should decline all-in
  flips under about 54 to 60% equity, at every blind level. With zero edge
  the match-win value equals the chip share.

Its role is the safety anchor and the opening-range model.

## 10. Reinforcement learning against the population

`rl/` on branch `holdem-rl`: PPO with numpy-only inference (330 KB of
weights, 1.4 ms mean per decision in the league). The reward is shaped by
a match-win potential and telescopes to the match result under the real
blind schedule. The input has 56 features, 9 of them opponent statistics
gathered within the current match, so the policy is conditioned on the
opponent it faces. Training ran in a fast C engine checked against the SDK
engine (rules, evaluator, baselines, clones, features), against a
prioritized fictitious self-play league of the 7 baselines, the 6 archetype
clones and past snapshots. The 10 per-bot clones were never trained on.

* League result: 22 of 23, field 89.4%. The weakest are the PoetAndCoder
  clone (79.5%), the Blueprint clone (81.5%), maniac (82.0%) and random
  (82.8%).
* Adding exploiter agents to the league did not help: minimum 0.807 without
  them against 0.775 with them, one seed each.
* Opponent conditioning against no opponent features, same training:
  baselines 87.9% against 83.5%, held-out bot clones 83.1% against 80.8%.
  The gain is real but modest.
* A PFSP floor of 0.05 caused forgetting (lag fell from 0.94 to 0.73);
  0.15 did not.

Next: retrain on archetype clones refit without the ten held-out bots, and
distill the confirmed maniac best response (section 7) into the policy.

## 11. Fresh-seed confirmation and the head-to-head gap

An independent check replayed the distilled RL policy (section 10 plus
distillation toward the maniac best response) against all 23 opponents on
deal seeds the league never used, 400 matches per opponent. It won 92.1%
overall, and every opponent's Wilson 95% lower bound was above 80%. The
weakest were the qwentom-leap clone (84.8%), maniac (85.8%) and random
(86.0%). It made 738,356 decisions with no errors and no illegal actions.
Peak memory was 47 MB, and the slowest decision on one core was 3.2 ms.

The same policy loses head to head to my earlier heuristic bot: 43.0% over
200 matches. The adaptive decision model does worse there (29.5%). Both were
trained or tuned against weak bots and replay clones of weak bots, and
neither had met a competent equity-based player. Beating that bot head to
head is now part of the ship gate, so the next RL round adds it to the
training pool.

## 12. Beating the heuristic bot, and the shipped candidate

Adding the heuristic bot to the RL training pool fixed the head-to-head gap.
SDK-engine worker processes play the real bot with the newest policy and
stream their matches to the learner. Each update is about 45% heuristic
samples and 55% from the C env (the 23 league opponents, the maniac
distillation term and two fixed past policies).

The checkpoint at iteration 300 of that run passed both gates twice:

| measurement | lowest of 23 opponents | against the heuristic bot |
|---|---|---|
| league, pairs 0 to 199 | A5 83.2% | 69.8% over 400 |
| fresh seeds, pairs 200 to 399 | A5 80.2% (321/400) | 67.5% over 400, CI [62.8, 71.9] |

It made 732,747 decisions in the fresh-seed run with no errors, fallbacks or
illegal actions. Peak memory was 47 MB, and the slowest decision on one core
was 1.9 ms.

Training further made A5 worse: iteration 600 won 74.8% against the
heuristic, but A5 fell to 77.7%. So I picked the checkpoint by both gates
instead of taking the latest one. Its A5 margin is thin.

The image passed the platform's review in minutes. Three warm-up matches on
the real server against house bots (DeepStack, Kimiko, glambot) were all
wins, and the bot is entered in Season 16.

## 13. Real Chipzen bots with public code

The evidence so far says the policy is strong against what it trained on
and weaker elsewhere. The heuristic head to head went from 43% to 70% only
after that bot joined training. The held-out per-bot clones scored 75.5% to
86%. The clones themselves are rough: qwentom-leap matches only 5 of 13
statistics, MercuryRetrograde 4 of 14. So I looked for the real bots. On
2026-11-22, a GitHub repo and code search for "chipzen" (`gh search`,
`gh api`) found these:

| bot on Chipzen | repo | language, license | usable as an opponent |
|---|---|---|---|
| Blueprint (in our field) | matteo-psnt/poker-solver | Python, MIT | no: DCFR ladder of 8 stack depths, blueprints not published |
| AutodidactInnovations (in our field) | autodidactinnovations-dev/poker-arena | Python, none | yes: Monte Carlo equity against pot odds, plays loose |
| Ashwing_v2 | Shaurya-S0603/PokerBots | Python, none | yes: search plus a short-stack equity policy, several variants |
| (unknown) wolfBot | mimaima699-ux/Chipzen-Poker-Bot | JavaScript, MIT | yes with node: range-aware Monte Carlo equity, opponent tracking |
| G5 | Nemandza82/g5-poker-bot | C#, MIT | build needed: opponent modelling |
| reference bot | chipzen-ai/chipzen-sdk | Python, Apache-2.0 | yes |
| pkr-chipzen-bot, cham-chipzen | elcoosp/* | Rust | no: needs an unpublished engine or blueprint |

robopoker (krukah) mentions a Chipzen tournament bot, but its blueprint is
not public either.

Wayne approved running the usable ones on gb10-d under these conditions:
each source is pinned to a commit and read in full, and only stdlib and
numpy imports are allowed (checked with an AST scan). Nothing contacts the
network. Work is on branch `holdem-fieldbots`. Next comes the shipped
policy's win rate against each of them, and then SDK-worker training
against them.

## 14. Does the policy overfit? Generalization by opponent family

Wayne asked whether the narrow gains are overfitting. I sorted the opponents
by whether a run trained on them.

**Inside the clone family the gap is small.** On the heur4 checkpoints
(seed 21, 400 matches each), the 13 trained opponents (7 baselines and 6
archetypes) score 90.1% to 90.9%. The 10 per-bot clones, never trained on,
score 88.1% to 89.4%. The gap is 1 to 3 points, so the policy is not
memorizing particular bots. The archetypes were fitted with those 10 bots
included, so this gap is a lower bound.

**Across families the gap is large.**
* Before the heuristic bot joined training, the policy won 43% against it.
* Against rl-17cf03f (another RL lineage, never in heur4's pool), heur4
  checkpoints 600 to 1200 score 51.8% to 57.5%. Against their own ancestor
  h4-300 they score 56% to 60.5%.

So progress inside a run transfers poorly to families it has not seen.

**Selection on the same seeds overstates.** heur4 checkpoint 900 screened at
A5 81.2% on seed 21. It scored 79.8% in the league (holdem-league f5441a0)
and failed the gate there; the league also shows 60.5% against h4-300 and
72.0% against the heuristic. Its A5 sits on the 80% line, like h4-300's
does.

**The sp1 head-to-head gains are in distribution.** sp1 has h4-300 and
rl-17cf03f in its fixed pool. Its 64% against h4-300 at iteration 300 is
therefore a training score, not evidence of generalization. sp1 was stopped
at iteration 400.

**What I'm doing about it.** Three opponent sets split by family:

| set | contents | use |
|---|---|---|
| train | baselines, archetypes, generated archetypes, heuristic, own snapshots | training |
| validation | 10 per-bot clones, rl-17cf03f | checkpoint choice |
| test | real Chipzen bots (Ashwing_v2, AutodidactInnovations, SDK reference, wolfBot), Blueprint 100bb | measured once, never trained on or selected on |

Then an A/B test from h4-300 with the same recipe and compute per arm:
* gen1 adds 48 generated archetypes (`tools/gen_clones.py`: mixes of two
  fitted archetypes with random fold, aggression, shove and value-or-bluff
  tilts and scaled sizes, weight 0.25 each).
* ctl1 does not.

Hypothesis: diversity inside the training family raises the scores on the
validation and test families. A side test averages heur4 checkpoints
(`tools/avg_ckpt.py`, `ckpt/swa1`).

### 14.1 Test opponent: the real Blueprint (100 bb release)

The poker-solver v0.1.0 blueprint (commit 4ee3132, tar sha256 3406d6c9...)
runs as an arena opponent from branch `holdem-bpopp`. It runs in Docker on
gb10-d with `--network none --read-only --cap-drop ALL`, a non-root user,
and the data mounted read-only. As in the live seat, the policy threshold
is 0.35 and there is no resolver. Only the 100 bb rung is published, so it
plays its 100 bb tree at every depth. Each line below is 400 matches, seed
3; the blueprint samples with an unseeded RNG, so a rerun can move a few
points.

| hero | win rate | 95% CI |
|---|---|---|
| h4-300 (shipped) | 55.5% | 50.6 to 60.3 |
| h4-900 | 55.0% | 50.1 to 59.8 |
| heuristic bot | 50.0% | 45.1 to 54.9 |

The same policy wins 81% to 88% against our replay clone of the field bot
Blueprint, whose live version is a newer 8-depth ladder. Against the real
blueprint it barely wins. That gap is the clone family's blind spot made
concrete: an equilibrium-style player is far harder than its behavioral
clone. The blueprint itself is weak against simple bots. In 100 matches
it won 63% against random and 61% against lag, where h4-300 wins 92% and
98%.

### 14.2 Result of the generalization A/B: no gain from generated archetypes

Both arms started from h4-300 with the same recipe and compute (180 minute
budget, stopped at 02:44 UTC after about 1000 iterations). Screens every 100
iterations (`tools/sp_watch.sh`; league set on seed 21, the others 400
matches each):

| run | below 80% (of 23) | field | weakest opponent | vs heuristic | vs h4-300 | vs rl-17cf03f |
|---|---|---|---|---|---|---|
| gen1, it100 to it900 | 0 to 1 | 90.2 to 90.8 | 79.2 to 82.5 | 64.8 to 75.3 | 48.8 to 57.0 | 49.0 to 55.5 |
| ctl1, it100 to it1000 | 0 to 2 | 89.5 to 90.5 | 77.0 to 81.2 | 67.3 to 72.5 | 51.0 to 58.8 | 45.5 to 56.0 |

* Neither arm moves after the first 100 iterations. The field average stays
  at 90%, and A5 wanders around the 80% line on noise.
* gen1 is not better than ctl1 on any of the three sets. Widening the clone
  family with random tilts did not raise the held-out scores, so the
  hypothesis in section 14 fails at this scale.
* Against rl-17cf03f, a lineage neither arm has seen, both stay at about
  50%. The 53% to 59% against their own ancestor h4-300 is a family effect,
  not general strength.

### 14.3 The real field bots: the clone metric overstates by 20 to 30 points

Branch `holdem-fieldbots` (merged into holdem-rl at 71cbb87) vendors 13
public Chipzen bots as SDK-engine opponents `ext:<name>`.
* All code was read in full and checked by `tools/check_vendor.py`: stdlib
  and numpy only, no network, file or process access. Wolf is JavaScript
  and runs in `docker run --network none --read-only --cap-drop ALL`.
* All 13 played 400 matches with 0 exceptions and 0 illegal actions.

Hero win rates, 400 matches each, seed 3, Wilson 95%:

| field bot | h4-300 (shipped) | heuristic bot |
|---|---|---|
| ext:ashwing_v2 (the live Chipzen entry Ashwing_v2) | 63.0% [58.2, 67.6] | 58.2% [53.4, 63.0] |
| ext:ashwing | 55.2% [50.4, 60.0] | 58.8% [53.9, 63.5] |
| ext:ashwing_search | 49.2% [44.4, 54.1] | 57.0% [52.1, 61.8] |
| ext:ashwing_hive | 58.8% [53.9, 63.5] | 59.0% [54.1, 63.7] |
| ext:ashwing_adaptive | 59.8% [54.9, 64.4] | 57.8% [52.9, 62.5] |
| ext:ashwing_value | 75.0% [70.5, 79.0] | 66.0% [61.2, 70.5] |
| ext:autodidact (poker-arena, 2000 trials) | 63.7% [58.9, 68.3] | 63.7% [58.9, 68.3] |
| ext:autodidact_fast (200 trials) | 58.8% [53.9, 63.5] | 64.8% [59.9, 69.3] |
| ext:wolf, wolf_v5, wolf_v2, wolf_v1 | 84.0% to 90.0% | 67.8% to 73.2% |
| ext:sdkref (SDK example) | 98.0% [96.1, 99.0] | 89.2% [85.8, 91.9] |

The per-bot clones of the same entrants score 84% to 89% for h4-300 in the
league (AutodidactInnovations clone about 85%). Against the real Ashwing and
autodidact code the policy wins 49% to 64%, and the old heuristic bot does
as well or better. Like the Blueprint in 14.1, the clone family is
missing whatever these bots do. The 23-opponent league gate measures
strength inside the clone family, not against the live field.

**Next run, fb1** (`tools/rl_fb.sh`, started 02:44 UTC on gb10-d, 180 minutes). It is
the ctl1 recipe from h4-300 with eight SDK workers cycling these opponents:
* the heuristic bot (twice, as it is a ship gate);
* four field bots: ext:ashwing_v2, ext:ashwing_value, ext:ashwing_adaptive
  and ext:autodidact_fast.

The opponent splits:
* **Validation, siblings of trained bots:** ext:ashwing, ext:ashwing_search,
  ext:ashwing_hive and ext:autodidact. `tools/fb_watch.sh` screens them on
  seed 5.
* **Test, other families:** Wolf, the SDK reference, the real Blueprint and
  rl-17cf03f.

ctl1 is the control at equal iterations.

### 14.4 fb1: training against real field bots generalizes, within and across families

fb1 (`tools/rl_fb.sh`, holdem-rl f76572e) ran 180 minutes from h4-300, about 1080 iterations. Its SDK
workers cycled the heuristic bot (twice), ext:ashwing_v2, ext:ashwing_value, ext:ashwing_adaptive and
ext:autodidact_fast. ctl1 is the control: the same recipe with the heuristic bot only.

Validation, the held-out Ashwing siblings (seed 5, 400 matches each):

| hero | ashwing | ashwing_search | ashwing_hive | mean | ashwing_v2 (trained) |
|---|---|---|---|---|---|
| h4-300 (shipped) | 57.3 | 55.3 | 59.8 | 57.4 | 59.3 |
| ctl1 it1000 | 59.8 | 61.3 | 66.8 | 62.6 | 67.8 |
| fb1 it100 | 62.3 | 59.5 | 68.8 | 63.5 | 69.3 |
| fb1 it200 | 64.0 | 64.8 | 75.0 | 67.9 | 73.0 |
| fb1 it600 | 66.8 | 67.3 | 75.5 | 69.8 | 74.5 |
| fb1 it700 | 68.3 | 67.8 | 76.8 | 70.9 | 74.0 |
| fb1 it900 | 66.0 | 67.5 | 80.3 | 71.3 | 76.0 |
| fb1 it1000 | 67.3 | 65.8 | 79.5 | 70.8 | 81.0 |

* **Pick:** it900, on the held-out mean and the weakest league screen (83.8%).
* **Clone league:** it stayed at field 91 to 92 throughout.
* **Against rl-17cf03f:** it rose from about 50% (ctl1) to 55 to 64%.

Test, other families, never trained or selected on (seed 3, 400 matches each):

| opponent | h4-300 | fb1-900 |
|---|---|---|
| ext:wolf | 84.0 | 93.3 [90.4, 95.3] |
| ext:wolf_v1 | 90.0 | 96.0 [93.6, 97.5] |
| ext:wolf_v2 | 88.0 | 94.3 [91.5, 96.1] |
| ext:wolf_v5 | 84.0 | 93.3 [90.4, 95.3] |
| ext:sdkref | 98.0 | 98.8 [97.1, 99.5] |

The gain carries to the Wolf family, which shares no code with the training bots.

Ship gate (holdem-league f07923f):
* **League screen, pairs 0 to 199:** PASS 23/23, weakest A5 83.8%. The heuristic head to head was
  64.0% over 400.
* **Fresh pairs 200 to 399** (independent verifier, `out/verify-fb1-900` on gb10-d, 9600 matches, 0
  errors or illegal actions): every opponent's Wilson lower bound is above 80%. The weakest is A5 at
  86.0% (LB 82.3), against h4-300's 80.25% (LB 76.1) on the same seeds. The heuristic head to head
  is 69.0% (LB 64.3), against h4-300's 67.5%.

Head to head against other policies (400 each): 47.2% against h4-300, 45.0% against h4-900, 60.0%
against rl-17cf03f. fb1-900 is slightly worse than its ancestors in a direct match, but much
stronger against every real bot we have. The ancestors are not in the field.
