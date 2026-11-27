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
| ext:autodidact (2000 trials; sibling of a trained bot) | 63.7 | 71.8 [67.1, 75.9] |
| real Blueprint 100bb (bp100) | 55.5 | 59.3 [54.4, 64.0] |

The gain carries to the Wolf family, which shares no code with the training bots, and the
Blueprint's lower bound moves above 50%.

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

### 14.5 fb2 and fb3: more field bot weight helps once, then overfits

fb2 (`tools/rl_fb2.sh`, holdem-rl dc0e0c3) continued from fb1-900 for 180 minutes (about 965
iterations), with two changes:
* the field bots and the heuristic made up about 60% of each update, against 50% in fb1;
* A5 and A2 were weighted up (`--opp-w arch:5=4,arch:2=3`).

| checkpoint | held-out Ashwing mean | ashwing_v2 (trained) | weakest league screen | heuristic screen |
|---|---|---|---|---|
| fb1-900 (start) | 71.3 | 76.0 | 83.8 | 67.3 |
| fb2 it100 | 73.1 | 79.8 | 82.0 | 63.5 |
| fb2 it500 | 74.0 | 80.0 | 83.3 | 66.0 |
| fb2 it700 | 75.3 | 85.3 | 83.0 | 68.3 |
| fb2 it900 | 77.2 | 85.3 | 84.3 | 67.5 |

The pick was fb2-900.

Ship gate (holdem-league 1056c33):
* **League screen, pairs 0 to 199:** PASS 23/23, field 91.2, A5 84.5. The heuristic head to head was 66.2% over 400.
* **Fresh pairs 200 to 399** (verifier, `out/verify-fb2-900`, 0 errors):
  * The weakest opponent is A5 at 84.75% (LB 80.9).
  * The heuristic head to head is 70.25% (LB 65.6).
  * On the same seeds fb1-900 scored 86.0% and 69.0%, and the matches won by only one of the two
    split close to evenly, so on the gate the two are indistinguishable.
  * A5's extra weight did not raise A5.

Test, other families (seed 3, 400 each):

| opponent | h4-300 | fb1-900 | fb2-900 |
|---|---|---|---|
| ext:wolf, v1, v2, v5 | 84.0 to 90.0 | 93.3 to 96.0 | 96.0 to 97.0 |
| ext:sdkref | 98.0 | 98.8 | 98.5 |
| ext:autodidact | 63.7 | 71.8 | 75.5 [71.1, 79.5] |
| real Blueprint 100bb | 55.5 | 59.3 | 62.3 [57.4, 66.9] |

Head to head, fb2-900 against fb1-900 is 49.2% over 400. That fits the pattern: each step against
real bots shows up on every real bot, but not against our own lineage.

fb3 ran the same recipe from fb2-900 and was stopped at iteration 300:
* The held-out Ashwing mean went 75.5, 75.4, then 73.4.
* A5 fell to 79.7% on the screen.

A third round of the same signal overfits the training bots, so the next gain needs new opponents,
not more iterations against these four.

### 14.6 Why fb2-900 wins only about 61% against the real Blueprint

Tool: `tools/chipflow.py` (holdem-rl), which logs each hand from our side, 400 matches per run, seed 3.
The blueprint samples with an unseeded RNG, so five runs read 62.3, 61.0, 61.2, 57.8 and 60.8%.

**Blueprint beats nobody by much either** (Blueprint as hero, 400 each):

| opponent | Blueprint | fb2-900 |
|---|---|---|
| Ashwing v2 | 57.3 [52.4, 62.0] | 85.3 |
| Ashwing | 56.8 [51.9, 61.5] | 74.5 |
| Wolf | 64.0 [59.2, 68.6] | 96.0 |

Close to equilibrium, it rarely gives up much and rarely takes much. A 61% match win against it fits that.

**Our edge per hand is a third of what it is against Ashwing:**
* Against Blueprint, +0.30 bb per hand (+4917 bb over 16616 hands); against Ashwing, +0.87 (+14537 bb over 16683).
* At about 41 hands a match, that is the difference between 61% and 75%.
* This is not card luck. The all-in luck was +52k and +54k chips in our favour in two runs.

**Where the difference comes from:**
* Against Ashwing, about half our net chips (+1.04M of 2.0M) come from river all-ins where it calls with
  worse; our mean equity there is 0.70. Blueprint does not pay off like that.
* Calling Blueprint's river shoves is the clearest leak: we called 58 times, won 6 and lost 342k chips.
  Against Ashwing, the same spot is 25 calls, 3 wins and -100k.
* Our own shoves are profitable against Blueprint on every street:

  | street | shoves | folds | net chips |
  |---|---|---|---|
  | preflop | 302 | 77% | +81k |
  | flop | 491 | 67% | +125k |
  | turn | 154 | 60% | +207k |
  | river | 536 | 73% | +731k |

  When a flop shove is called we hold 35% equity, and that is how about a third of the lost matches end. The
  folds pay for it in chips, but the variance is concentrated where the match is decided.
* Non-all-in showdowns lose 862k, of which 519k are after our own last raise and 341k after Blueprint's.

**Next:**
* Add a solver-style opponent to training, keeping Blueprint held out: the holdem-blueprint MCCFR tables
  (section 9) are the candidate.
* Its river shoves are value-heavy, which is the spot the training field never taught.

### 14.7 Spamming all-in beat v3 (roadmap S0)

Wayne found it online: an opponent that shoves every hand beats the entered bot. Measured with
`rl.eval_arena`, 400 matches, seed 3: fb2-900 wins 49.0% [44.1, 53.9] against `jam` (shoves any two
cards every hand).

* **Why:** training never showed it an any-two shover. Facing a preflop shove it called about 16% of
  hands, although nearly every hand with 60 to 70% equity against a random hand is a profitable call.
* **Fix at play time** (`rl/allin.py`, holdem-rl 65ef2b7):
  * An online estimate of the opponent's preflop shove frequency and of how wide it shoves (the weakest
    shown shoving hand widens the range at once).
  * Match-value tables over (hand number, stack) from backward induction (`tools/allin_tables.py`).
  * Once the frequency reaches 0.7 (three shoves in three chances), a policy fold of a preflop all-in
    becomes a call when calling has the higher match value. On the first small-blind decision, it also
    folds trash instead of limping into the shove.
  * The module only overrides those two spots, so it cannot change play against anyone who does not
    shove most hands.
* **Ceiling:** with the shove range known from hand 1 (`tools/allin_ceiling.py oracle jam`), 65.5% [60.7, 70.0].

Gate (`tools/allin_gate.sh`, `RL_ALLIN=off` for the old behavior, same seeds):

| opponent | off (v3) | on |
|---|---|---|
| jam | 49.0 | 62.75 [57.9, 67.3] |
| jam_half, maniac | 85.0, 85.75 | 84.5, 85.5 |
| jam_post, minraiser, station, nit, random, reference, lag, station_raiser | | identical |
| 23-opponent league | 23/23, 91.2 | identical |
| Wolf, Wolf v1, v2, v5, SDK reference | 96.0, 97.0, 96.5, 96.0, 98.5 | identical |
| Blueprint (seeded bpopp:v011) | 59.0 | 59.0, rows byte identical |
| head to head against v3 (seeded) | 45.0 | 45.0, rows byte identical |

* **Fire counts** (`tools/allin_count.py`): the answer never fired in 400 head-to-head matches or in 2000
  matches against the Ashwing family and autodidact. Against `jam` it fired 131 times in 20 matches.
* **The unseeded bots differ by chance.** The Ashwing family and autodidact are not seeded, and on and off
  differed in 1192 of 1600 rows, so their gaps (for example autodidact 75.25 off, 76.5 on) are noise. The
  fire counts show the answer played no part.
* **Seeding the policy opponents.** Before, `model:` and `policy:` opponents were unseeded, and two identical
  head-to-head runs read 47.25% and 49.0%. They now have a set_seed hook (holdem-rl acb29e9), and runs repeat
  byte for byte.
* **E4 needs a paired baseline.** fb2-900 against itself on the seeded pairs of seed 3 reads 45.0%
  [40.2, 49.9], so a flat 50% bar on one seed set would fail the incumbent itself. A candidate's head to head
  is compared with this mirror on the same seeds.
* **Image:** `holdem-rl-fb2-900-allin.tar.gz`, sha256 0291ee39..., ships `rl/allin.py` and the 1 MB tables.
  A fresh-context verifier reran the tests, the jam result (251 of 400), ten on/off pairs and the image, and
  fuzzed 200,000 states with no exception: CONFIRMED.

### 14.8 The exploiter after 150 minutes

ex1 (`tools/rl_exploit.sh`, started as fb2-900 and trained only against it in the C engine) ran its full
150 minutes: 30,790 iterations, about 990M steps. In the C engine it ends at 98 to 99% against fb2-900.

* **SDK engine, 400 matches, seed 3:** fb2-900 wins 1.0% [0.4, 2.5] with the all-in answer and 1.5%
  [0.7, 3.2] without. At 400 iterations it was 3.5%. E3 at a fixed 400 iterations already sits near the top
  for fb2-900, so it will separate candidates only once they are much more robust.
* **How it wins** (`tools/chipflow.py`, 200 matches):
  * fb2-900 folds after the flop 2374 times and loses 1.09M chips there. The exploiter bets into it.
  * Preflop, the exploiter raises first 29.7% of the time and almost never folds (1.3%).
  * fb2-900's preflop shoves are called 162 of 210 times at 40.5% mean equity (-114k expected). The
    exploiter calls with the hands that beat the shove range.
  * fb2-900's river shoves still fold it out 90% of the time, but the 54 calls come at 24% equity.
* **Use:** the ex1 snapshots (every 25 iterations in `ckpt/ex1` on gb10-d) are the first pool members for S2,
  the league with exploiters.

### 14.9 The measurement harness (roadmap S1)

Everything later is judged with this, so it had to repeat exactly.

* **Seeded Blueprint.** `bpopp:v011` is v010 plus one layer, a `server.py` that seeds the global NumPy RNG
  on `match_start`. Apart from line endings (v011's copy is CRLF), the two servers differ only by those four lines. fb2-900 against it, 400 matches, seed 3:
  * byte-identical rows across three runs, with 2 and 3 workers: 236 wins, 59.0%;
  * the unseeded v010 differs in 310 of 400 rows (57.5%), so the seed is what makes it repeat.
* **Seeded policy opponents.** `model:` and `policy:` opponents now repeat byte for byte. The fb2-900 mirror
  read 45.0% twice.
* **Exploitability probe** (`tools/exploit_probe.sh`: a fresh exploiter, 400 iterations in the C engine, then
  400 SDK matches). Four probes of fb2-900:

  | probe | exploiter win rate |
  |---|---|
  | ex1 at 400 iterations | 96.5 [94.2, 97.9] |
  | train seed 1 | 97.25 [95.1, 98.5] |
  | train seed 2 | 97.5 [95.5, 98.6] |
  | card, train seed 1 | 95.0 [92.4, 96.7] |

  The intervals overlap, so the probe is stable to about two points. Training is not deterministic across
  runs; the eval is. The two seed probes' JSON files were rewritten after the runs: their iteration field
  first counted log lines (81), and now records the last logged iteration (400), which the probe script
  also does since holdem-rl 2834f8d.
* **Baseline card** `logs/eval_card/fb2-900.json` (`tools/eval_card.sh`), for the entered bot
  (fb2-900 plus the all-in answer):

  | opponent | win rate |
  |---|---|
  | Ashwing, search, hive, v2 (seed 5) | 72.75, 71.5, 85.5, 84.25 |
  | Wolf, v1, v2, v5, SDK reference (seed 3) | 96.0, 97.0, 96.5, 96.0, 98.5 |
  | autodidact (seed 3) | 74.5 |
  | Blueprint (seeded) | 59.0, +0.25 bb per hand all-in adjusted |
  | E3 probe | 95.0 |
  | E4 mirror | 45.0 |

  The Ashwing bots and autodidact are not seeded. Over four seed-5 runs fb2-900 reads 1183/1600 (73.9%)
  against Ashwing and 1164/1600 (72.75%) against ashwing_search. Single runs spread about plus or minus two
  points.

### 14.10 S2: the league with exploiters (roadmap S2)

`tools/rl_s2.sh s2 ckpt/fb2/it000900.npz 300` (holdem-rl 8739676) on gb10-d, 2026-11-22 19:47 UTC to
2026-11-23 00:50 UTC. It is the fb2 recipe with a pool of the 4 newest exploiters at `--pool-w 1.0`, plus
`jam` and `jam_half` in the SDK round robin. An exploiter loop trained a fresh exploiter of the newest main
weights every 4 to 5 minutes (400 iterations) and dropped it into the pool: 73 cycles. No stop condition fired.
The run ended at max-minutes, at iteration 1835.

* **Screens** (probe: train seed 1, eval seed 3; Ashwing pair at seed 5; pool statistics since the last
  screen):

  | iteration | probe | ashwing | ashwing_search | pool share | main against pool |
  |---|---|---|---|---|---|
  | 200 | 93.0 [90.1, 95.1] | 73.75 | 71.5 | 27.6% | 20.9% |
  | 400 | 74.75 [70.3, 78.8] | 70.25 | 70.25 | 38.9% | 19.1% |
  | 600 | 88.75 [85.3, 91.5] | 65.75 | 72.25 | 36.3% | 22.4% |
  | 1800 | 74.5 [70.0, 78.5] | 72.0 | 72.5 | 34.9% | 24.3% |

  ashwing at it600 sits under its line (69.5), but ashwing_search does not, so the tripwire (both under)
  did not fire.
* **The probe is noisier away from its ceiling.** On it400 the same nominal seeds gave 74.75 (screen) and
  87.0 (card), and train seed 2 gave 82.0. Together that is 975 of 1200, 81.25%, though all three replay the same
  400 deals (eval seed 3). On it600 train seeds 1 and 2 gave 88.75 and 89.75. Probe training is not
  deterministic, and near 97% the binomial spread hid that. One probe cannot rank S2 checkpoints, so S2b
  judges E3 on three fresh probes with their own eval seeds.
* **The exploiters got weaker.** Their own win rate against their target, at the end of each 400-iteration
  cycle, averaged 0.90 over cycles 1 to 10, 0.82 to 0.85 over cycles 11 to 50, 0.80 over cycles 51 to 60, and 0.77 over cycles 61 to 73.
  Each target was the newest main agent, so the main agent got harder to exploit at a fixed budget.
* **How a fresh exploiter wins now** (`tools/chipflow.py`, 400 matches, seed 3, each bot against its own
  400-iteration probe exploiter):

  | | fb2-900 | S2 it1800 |
  |---|---|---|
  | matches won | 2.8% | 24.0% |
  | chips lost per hand | 2.51 bb | 0.84 bb |
  | post-flop folds, net of the opponent's | -1.61M | -0.95M |
  | showdowns | -1.02M over 2484 | -0.49M over 6370 |
  | preflop all-ins after the bot's last raise: count, mean equity | 303, 0.369 | 353, 0.448 |
  | turn all-ins after the bot's last raise: count, mean equity | 57, 0.309 | 91, 0.352 |

  The leaks are the same as in 14.8 and smaller. The bot still folds too often after the flop, and its
  shoves are called by better hands. The exploiter against S2 raises first 37.1% preflop, against 21.6%
  for fb2-900's exploiter.
* **Card at it400** (`logs/eval_card/s2-it400.json`) against the fb2-900 card: Ashwing 73.5, search 71.0,
  hive 83.0, v2 84.75; Wolf 95.0, v1 98.0, v2 97.0, v5 95.0, SDK reference 98.25; autodidact 74.5; Blueprint
  59.25 at +0.27 bb per hand (59.0 and +0.25). All are within the baseline's intervals. E3 87.0. E4 44.75%
  [40.0, 49.6] against the 45.0 mirror, so the head to head against the entered policy is level.
* **Card at it1800** (`logs/eval_card/s2-it1800.json`): Ashwing 69.25, search 72.5, hive 84.25, v2 81.75;
  Wolf 95.0, v1 96.5, v2 96.75, v5 95.0, SDK reference 99.5; autodidact 74.25; Blueprint 57.0 at +0.22 bb per
  hand. All are within the fb2-900 card's intervals. E3 71.0 [66.4, 75.2], and a second probe (train seed 2)
  78.25. **E4 53.25% [48.4, 58.1] against the 45.0 mirror:** the first candidate that beats the entered policy
  head to head on the seeded pairs.
* **Extreme bots** (E5, added to S2b's acceptance after Wayne asked how diverse the opponents are; 400 matches,
  seed 3, all-in answer on), v4 then it400 then it1800: jam 62.75, 63.0, 63.0; jam_half 84.5, 85.0, 83.25;
  jam_post 84.5, 84.25, 84.0; minraiser 96.0, 96.25, 95.25; station 97.75, 96.5, 95.0; maniac 85.5, 84.75,
  83.5; nit 97.5, 98.25, 98.25; random 84.5, 83.75, 86.25; reference 98.5, 98.25, 99.5; lag 94.5, 90.75,
  92.25; station_raiser 96.5, 95.5, 96.75. Two readings sit under v4's interval: station at it1800 (95.0
  against [95.8, 98.8]) and lag at it400 (90.75 against [91.8, 96.3]).
* **Verdict:** acceptance not met. E3 needs a probe under 70%, and the lowest was 74.5. Nothing else got
  worse. The trend in the exploiters' rates and in the chip flow says the run was still improving, so the
  next step is S2b, which resumes S2 (roadmap).
* **Bookkeeping fix after the run** (holdem-rl a0ba32c, from the S2 code review): the pool rotated at
  `it % 10 == 0`, inside a 5-iteration log window, so 4 of every 5 iterations around a rotation were
  credited to the wrong file. Rotation now happens right after a log row. That alone was not enough: matches run across
  iterations, so a match in progress at a rotation finished against the slot's new file and was credited to it
  (27 of 53 pool results in a 30-iteration check, found by the second review). Such matches are now restarted
  unreported (0670e94), and the same check reads 0 of 54. The state also saves per-file pool win rates, so a
  resume keeps them. The screen's pool share counts matches, not files, so it is unaffected.

### 14.11 Style map: which real-field styles our opponents cover

Wayne asked how diverse opponents are generated, beyond the extreme bots. Before building anything, I measured
coverage. `tools/style_map.py` (holdem-rl 3ef434e) computes one 8-axis style vector per player:
* VPIP and PFR on the first preflop decision;
* the preflop shove rate;
* fold to a preflop raise;
* the post-flop aggression share;
* post-flop fold to a bet;
* the mean post-flop bet over the pot (halved, capped at 1);
* the showdown rate.

It reads the 330 poker replays among the 412 Chipzen replay files (51 bots with at least 100 hands) and 60 simulated matches of each of our
opponents against fb2-900 (the baselines and extremes, the heuristic bot, the 13 real field bots, three S2
exploiters, S2's it1800 and fb2-900 itself). Each field bot is matched to its nearest pool member (Euclidean
distance; a missing axis reads 0.5). Files are in `logs/style/` on gb10-d.

* **Covered (distance 0.16 to 0.40):** the loose middle of the field, including Blueprint, InfernalMonarch,
  mr_hide, lil-b3b, the Deep_Thought versions and most of the 100 to 200 hand bots. Their nearest members
  are autodidact, Ashwing, fb2-900 and, for the aggressive ones, the S2 exploiters (x010 is nearest to 10 bots).
* **Gaps (0.42 to 0.74, 12 of 51 bots), four styles no opponent of ours plays:**

  | style | field bots (distance) | what they do |
  |---|---|---|
  | preflop raiser, then a station | DeepStack (0.74) | VPIP 0.89 and PFR 0.67, never bets or folds after the flop, showdown 0.88 |
  | sticky over-bettor | PluriBot (0.58) | post-flop aggression 0.72, bets about 1.4 pots, folds to a bet 11% |
  | tight preflop, sticky after | r0ckGarden (0.54), SHADOW_REAPER (0.52), WSmithSimLab (0.49), SolvencyCheck (0.47), Humo-botv2 (0.46) | VPIP 0.24 to 0.39, post-flop aggression 0.23 to 0.40, folds to a bet 18 to 33% (WSmith 56%) |
  | loose, never folds preflop | Chatterbox (0.51), 5ur9e (0.50), PoetAndCoder (0.43), MercuryRetrograde (0.42) | fold to a preflop raise 0 to 6%, showdown 0.64 to 0.95 |

  Our tight bots (nit, reference, SDK reference) fold to a post-flop bet 66 to 88% of the time, and Wolf has
  post-flop aggression 0.12. No opponent of ours is tight before the flop and sticky after it. The twelfth
  bot, BOTV8 (0.43, nearest the heuristic bot), fits none of the four.
* **Limits:** a pool member's style is measured against fb2-900, and a field bot's against its whole season
  of opponents. Eight axes cannot tell apart bots that differ in hand selection at equal frequencies. The
  C-engine clones (fitted to these replays) are not measured, because the map reads SDK hand histories.
* **Use:** the gaps are the first targets of the diversity slice. Opponents are trained to hold a gap style
  while winning as much as they can (quality-diversity), not built as random tilts, because 14.2 showed
  weak tilted clones teach nothing. The gap bots that have replays also become held-out evaluation targets.

### 14.13 X1: an explicit opponent model predicts real bots far better than a population prior

Roadmap Revision 2, slice X1 (holdem-rl 0967e71: `rl/oppmodel.py`, `tools/oppmodel_fit.py`,
`tests/test_oppmodel.py`, `rl/models/oppmodel.npz`). The model predicts an opponent's next action in five
classes (fold, check or call, bet or raise up to the pot, above the pot, all-in) from the public state,
in three layers:
1. a population prior: an MLP with 64 hidden units over street, position, facing bet over pot, effective
   stack, the previous action, raises this street, call over remaining stack, and pot and own stack in
   big blinds;
2. a per-name profile: training counts per context bucket (street by facing bet, edges 0.35 and 0.8 of
   the pot), shrunk toward the prior with strength k = 20;
3. an in-match update: this match's counts so far, weight w = 2 (k_im = 8 when the name is unknown).

Data: the 330 poker replays, sorted by start time. The latest 99 are held out, and the rest split into a
185-match fit part and a 46-match validation part. Every choice was made on validation, and the model was
refit on all 231 training matches and scored once. Mean log loss per action, in nats:

| held-out subset | actions / matches / names | uniform | prior | prior + in-match | prior + name + in-match |
|---|---|---|---|---|---|
| known names (at least 200 training actions) | 15,426 / 91 / 16 | 1.609 | 0.741 | 0.624 | **0.544** |
| unseen names (hand 11 on) | 1,425 / 10 / 4 | 1.609 | 1.103 | **0.725** | (no profile) |

* **Acceptance 1 PASS:** the name adds 0.080 nats per action over prior plus in-match, 95% match
  bootstrap [0.068, 0.092], better in 88 of 91 matches. With the baseline's k_im tuned on the held-out set
  itself (an oracle in the baseline's favor) the gain is still 0.067 [0.056, 0.079].
* **Acceptance 2 PASS, weak:** in-match updating gains 0.378 [0.155, 0.575] on unseen names. The gain is
  uneven: 5ur9e (never folds preflop) +1.16, mochi +0.27, WSmithSimLab +0.17, MOTONAKA +0.004. Without
  5ur9e it is about +0.16. The prior alone is worst exactly on the unusual bots, which is the 14.11 gap.
* **Acceptance 3 NOT TESTED** (box busy): the file is 11.8 KB and loading imports numpy only; on the PC,
  300 actions take p99 0.12 ms. The 0.5 vCPU, 256 MB container measurement waits for a quiet box.
* **Verification:** a fresh verifier reproduced every number from a clean `git archive` (identical fit log
  and arrays). Scrambling all held-out labels and features left every selected setting and saved array
  unchanged, so no held-out row reaches the fit. Per-name counts total the 42,219 training rows exactly;
  in-match counts are read before each update; the replay pot chain matches `pot_after` on all 27,273
  streets, and all 696 all-in labels empty the stack. Verdict CONFIRMED.
* **Limits:** the replays span 37 hours, so a name's profile barely ages across the split; Season 16 replays
  retest it across a season. Replays hide hole cards except at showdown, so the model predicts actions,
  not hands; a range model for X2 needs simulation or showdown data.

### 14.12 M1: exploiting one known opponent is worth about 15 points

Roadmap Revision 2, M1. `tools/rl_br.sh` fine-tuned fb2-900 for 90 minutes against one SDK field bot only
(3 SDK workers; a 200-decision C-engine mirror per iteration). `br_ashwing` trained against `ext:ashwing`
(580 iterations). `br_autofast` trained against `ext:autodidact_fast`, because the full `ext:autodidact`
played 7 matches a minute. `tools/m1_eval.sh` then played each model on seed 21, fresh for all of them.
`ext:` bots are unseeded, so comparisons are unpaired (Newcombe interval of the difference).

| model | vs ext:ashwing (800) | vs ext:autodidact (400) |
|---|---|---|
| fb2-900 | 75.5% [72.4, 78.4] | 79.25% [75.0, 82.9] |
| br_ashwing | **90.25% [88.0, 92.1]** | 78.0% [73.7, 81.8] |
| br_autofast | 76.4% [73.3, 79.2] | **90.25% [86.9, 92.8]** |
| br_mix | 83.25% [80.5, 85.7] | 87.25% [83.6, 90.2] |

* **Decision statistic:** br_ashwing gains 14.75 points on its target, Newcombe 95% [11.1, 18.4]; br_autofast,
  trained only on the fast variant, gains 11.0 [6.1, 15.9] on the full `ext:autodidact`. Both lower bounds
  are above zero, so exploitation headroom is real, and the roadmap's positive branch applies: X2 is
  specified after X1.
* **Specialization cost, measured on the other target:** none in win rate (br_ashwing on autodidact
  -1.25 [-6.9, 4.4]; br_autofast on Ashwing +0.9 [-3.3, 5.1]). It shows up as match length: br_ashwing needs
  63.9 hands per match against autodidact (fb2-900 41.3), br_autofast 46.0 against Ashwing (fb2-900 41.7).
  Each fine-tune keeps fb2-900's floor against the other bot but wins it more slowly.
* **Where the gain comes from** (`tools/chipflow.py`, 400 matches on seed 31, `logs/m1/flow_*_ashwing.txt`):
  fb2-900 won 69.8%, br_ashwing 90.2%.

  | | fb2-900 | br_ashwing |
  |---|---|---|
  | first preflop action: raise / call | 32.3% / 50.0% | 64.7% / 20.6% |
  | Ashwing's answer: call / raise | 43.5% / 35.6% | 72.5% / 20.0% |
  | showdowns without all-in, we bet last | 3,270 hands, -261k chips | 4,832 hands, +531k |
  | all showdowns without all-in | -647k | +299k |
  | river shoves (folds) | 635 (66%) | 248 (56%), called ones at +364k expected |
  | opponent folds after the flop | +2.70M | +3.62M |

  Against a sticky caller the fine-tune raises twice as often before the flop, value-bets thinner and
  bluffs less: a whole-strategy shift, not one leak.
* **M1b, one fine-tune on both bots** (`tools/rl_br.sh br_mix ... ext:ashwing,ext:autodidact_fast 90 4`,
  455 iterations, `tools/m1b_eval.sh`, same seed and sizes): it keeps most of both exploits. Against Ashwing
  +7.75 [3.8, 11.7] over fb2-900, 7.0 [3.7, 10.3] under br_ashwing (about half of that gain kept); against
  autodidact +8.0 [2.8, 13.2] over fb2-900, 3.0 [-1.4, 7.4] under br_autofast (not significantly less).
  Confound: br_mix got about half of each single fine-tune's data per bot (4 SDK workers split over two bots,
  455 iterations against 580 for br_ashwing), so the Ashwing shortfall is partly data, not capacity.
* **Reading for X2:** a single network conditioned only on in-match statistics already carries two different
  exploits at once, so the gap between fb2-900 and the specialists is mostly its training population. That
  supports X2 as one policy trained on a broad population with the opponent's profile as input (X2a seeds
  it); X2b gives each opponent family enough data to separate the population effect from data volume.

### 14.14 X2a: name-seeded opponent counts in both engines

Roadmap Revision 2, slice X2a (holdem-rl 25cd281, 7e54bf4, 90baa6b). The policy's in-match opponent
counts (`Tracker`, `NST` = 15 slots) can now start from a per-name long-run profile instead of zeros: in the
deployed bot (`RLBot(priors=PATH)`, keyed by the other seat's `match_start` `display_name`) and in the C
engine (`env_set_prior` / `Pool.set_prior`, applied inside the reset before the first hand; `rl.train
--seed-profiles PATH` seeds the hero seat against `bot:NAME` clones). Nothing is trained yet; X2b does that.

* **Profile table** (`tools/tracker_profiles.py`, `rl/models/tracker_prior.npz`, 5.3 KB): 330 poker replays,
  70 names, 21,032 name-hands; 51 names with at least 100 hands get a profile, scaled to 20 hands. All 10
  `bot:` clone names are covered. The replays hold no `all_in` records and no raise that adds no more than
  the call, so the all-in-for-less rule never fires on them.
* **Acceptance 1 PASS:** unscaled counts equal an independent count from `rl/oppmodel.py` `extract_replay`
  for every name on st[10], st[5], st[6], st[11], and (added after verification) the dealer-dependent
  st[0] and st[1]. Raise amounts left as chips added: fails. Big blind poster as dealer: fails (139
  mismatches).
* **Acceptance 2 PASS:** Python and C counts and features agree within 1e-9 on both seats at every decision
  of 96 seeded matches (seat 0: 1,726 decisions with a prior, 1,873 without, 3,357 with in-match evidence;
  seat 1: 2,015, 1,584, 3,357), and when the opponent finishes hand 1 inside the reset (43 decks). Killed
  mutations: no seeding, wrong seat, copy after `run`, prior kept across resets, aliased prior. The
  "copy after `start_hand`" mutation the spec named cannot be killed: `start_hand` never touches the
  counts, so it is the same program.
* **Acceptance 2b, 3, 4, 5 PASS:** only the hero seat is seeded and only for named clones; without the flag
  three fixed-seed `Collector` batches hash identically to the base (`tools/collector_hash.py`, 54,168 rows)
  and SDK match rows are byte-identical; `RLBot` seeds only with `priors=PATH` and only for a known
  opponent name; the full suite passes (189 passed, 2 skipped by the box environment).
* **Deployed default is off.** fb2-900 was not trained on seeded counts and would read a profile as 20 hands
  already seen, so `deploy/bot.py` keeps today's behavior until a seeded policy ships.
* **Verification:** a fresh verifier reproduced every part from `git archive` on gb10-d, regenerated the
  table byte for byte, matched all 15 slots for all 70 names with a counter written from the raw JSON, and
  confirmed the raise-to and dealer conventions against `holdem/engine.py` and the SDK's `models.py`.
  Verdict CONFIRMED; its two test gaps (dealer slots, a self-comparing assert) are fixed in 90baa6b.
* **Open:** whether the live `display_name` equals the replay player name is not checkable offline; M3
  (Season 16 replays of our own matches) answers it before seeding is turned on.

### 14.15 S2b and the swap candidate: the floor recipe has stopped paying

Roadmap S2b resumed S2 from its final state (screens at it 2300 and on) for 300 minutes (`tools/rl_s2.sh s2b ckpt/fb2/it000900.npz 300 s2`), ending
at it 3300 (max-minutes, no stop). Screen probes (eval seed 3, 400 matches; lower is sturdier): it 2300 79.25,
2700 77.75, 3100 82.25, 3300 80.5. Ashwing and Ashwing search stayed at 69.5 to 74.5. None beat S2's it 1800
(74.5), so the acceptance candidate was `ckpt/s2/it001800.npz` (sha256 4989481c5e7d5d8b).

| check | rule | S2 it1800 | v4 (fb2-900) | result |
|---|---|---|---|---|
| E1 league, pairs 0 to 199 | 23/23 at 80% | 21/23, field 88.0 [86.7, 89.4]; A5 78.5, Blueprint clone 79.2 | 23/23, 91.2; A5 84.5, Blueprint 86.0 | FAIL |
| E2 real bots (card) | no family below v4 | all cells within v4's intervals | | pass |
| E3, three fresh probes (seeds 12 to 14) | pooled under 70% | 77.0, 79.0, 80.0; pooled 78.67% [76.3, 80.9] | 96.5% | FAIL (improves on v4) |
| E4 head to head (card) | at least the 45.0 mirror | 53.25% [48.4, 58.1] | 45.0 | pass |
| E5 extreme bots (seed 3, 400 each) | none below v4's interval | station 95.0 [92.4, 96.7] against v4 97.75 [95.8, 98.8]; the other 10 within | | FAIL |

* **Verdict: not gated, no swap.** poker-ai-lab-v4 stays entered for Season 16. The E5 rerun reproduced 14.10's
  numbers exactly (seeded rule bots), and the league result is holdem-league d554b8a.
* **What it gains and loses:** it is much harder to exploit (78.7% against 96.5%) and wins the head to head
  against v4, but it loses about 3 points of field win rate in the league, mostly against the A5 opener and
  the Blueprint clone, and 2.75 points against a pure calling station.
* **Reading:** across S2 and S2b, the seven screens from it 400 to it 3300 read 74.5 to 88.75 with no downward trend
  after it 400. The exploiter-pool recipe bought one large step in sturdiness (96.5 to about 78) and then
  stopped; more of it does not lower the probe and costs field win rate. The roadmap's next floor step
  ("S3 starts from S2b's final weights") needs a new plan revision rather than more of the same recipe.

### 14.16 X2s, search under X1: match-win utility is required, and a one-street search cannot beat the policy

X2s (roadmap) is the smallest end-to-end search: at each decision a one-street value per legal action against
an X1-updated range, overriding the policy when X1 has evidence and the gain beats 0.05 of the pot. Code on
holdem-x2s (worktree `poker-ai-lab-x2s`, not merged): f70ce33 build, 2bcedd8 effective stack, 8007e33
match-win utility; diagnosis tool `tools/x2s_ablate.py`. All runs fb2-900, 100 matches, seed 31, on gb10-d
(`~/poker-ai-lab-x2s/logs/abl*`); intervals are about plus or minus 9 points.

| configuration | raise_station | tight_sticky | ext:ashwing |
|---|---|---|---|
| search off (policy alone) | 96 | 95 | 61 |
| chip EV, as specified | 71 | 66 | 43 |
| chip EV, effective stack fixed | 70 | 66 | 49 |
| + no fold equity (f0) | 71 | 68 | 37 |
| + river and all-in decisions only (exact) | 80 | 82 | 52 |
| + 1,000 common runouts (crn) | 72 | 70 | 57 |
| + range never updated (flat) / softer update (soft) | 82 / 78 | 64 / 65 | 33 / 46 |
| best chip-EV combination (exact, crn, flat or soft) | 93 | 85 | 57 |
| **true opponent model (oracle), chip EV** | **59** | **81** | |
| true model, exact | 77 | 81 | |
| **true model, match-win utility, K per opponent** | **100** | **98** | |
| X1, match-win, K per opponent | 94 | 88 | 57 |
| **X1, match-win, one field K** | 89 | 88 | **71** |
| X1, match-win, one field K, crn | 89 | 88 | **79** [70.0, 85.8] |
| true model, match-win, one field K | 99 | 98 | |

* **Bug:** the first EVs ignored the effective stack. A shove counted chips the opponent did not have
  (half of all shove overrides covered the opponent). Fixed with a failing test first; worth little alone.
* **Root cause, the objective:** with the opponent's exact rules as the model (`oracle`: exact Bayesian
  range and fold probability of the StyleBot), the chip-EV search still lost 37 and 14 points to the
  policy, mostly by shoving preflop coin flips instead of calling (103 of 165 overrides against
  raise_station). Chip EV is the right objective only between equals. A player with an edge should
  decline flips the policy declines, because the policy was trained on match wins. With match-win
  utility, gambler's ruin `W(x) = (1 - exp(-K x / T)) / (1 - exp(-K))`, the same oracle search won 100%
  and 98%, so search plus an accurate model beats the policy. This was limit 5 in the Correction list.
* **One K for all opponents:** `K = 2 ln(w / (1 - w))` from v4's league field win rate (91.2%, E1) gives
  K = 4.68. With it the X1 search reached 71% and 79% against Ashwing (policy 61%). That closes about 60% of
  the M1 specialist gap (90.25%) with no training on Ashwing. On the stations it trails the policy by 7
  points, where the true model reaches 98 to 99.
* **Weakest part now, the opponent model:** X1 against the oracle is 10 points on both stations. The logs
  show why. X1 gives a 42 to 60% fold chance to river shoves into a bot that never folds (an unobserved
  bucket falls back to the population). And the band update, 0.1 per action outside the band, compounds,
  so a station's range collapses to weak hands after three checks.
* **Verifier (fresh context, 2026-11-23):**
  * The EV arithmetic matched an independent chip-flow model on 20,000 random spots (max relative error
    2.5e-8).
  * Search off plays byte for byte as c348a59. The tracker and X1 bookkeeping matched the engine at 1,406
    decisions.
  * One crash: on a trips or quads board the strength table scored impossible combos, the evaluator raised,
    and the bot check-folded the rest of that hand. It was fixed in dbe9e3e before the judge's search-on arm.
    Every run in the table above had it; it hits about one hand in a few hundred, in every configuration alike.
  * The oracle's call likelihood is wrong when the bot cannot raise (facing an all-in). Its fold probability
    is exact, and we make no later decision in such a hand, so no result above depends on it.
* **Held-out judge (`tools/x2s_judge.sh`, dbe9e3e, 300 matches per cell, fresh seed 41, `tools/x2s_stats.py`):
  search on LOSES.**

  | cell | off | on | difference [95%] |
  |---|---|---|---|
  | ext:ashwing | 73.0 | 76.3 | +3.3 [-3.6, +10.3] |
  | ext:ashwing_search | 74.7 | 76.3 | +1.7 [-5.2, +8.5] |
  | ext:ashwing_hive | 86.7 | 80.3 | -6.3 [-12.3, -0.4] |
  | ext:autodidact | 76.3 | 74.0 | -2.3 [-9.2, +4.6] |
  | ext:wolf, ext:wolf_v5 | 94.3 | 83.7 | -10.7 [-15.7, -5.7] |
  | raise_station | 94.7 | 88.3 | -6.3 [-10.9, -1.9] |
  | sticky_overbettor | 83.0 | 71.7 | -11.3 [-17.9, -4.6] |
  | tight_sticky | 95.3 | 86.3 | -9.0 [-13.7, -4.4] |
  | never_fold_pre | 93.3 | 87.7 | -5.7 [-10.5, -1.0] |
  | pooled | 86.6 | 80.8 | -5.7 [-7.6, -3.9] |

  The 100-match smoke reading for Ashwing (search off 61%, on 71 to 79%) was mostly noise. On seed 41 the
  policy alone wins 73%.
* **Oracle at the judge's size and seed (`x2s_ablate.py oracle`, field K, 300 matches, seed 41):**

  | cell | policy alone | search, true model | search, X1 |
  |---|---|---|---|
  | raise_station | 94.7 | 96.7 | 88.3 |
  | sticky_overbettor | 83.0 | 80.0 | 71.7 |
  | tight_sticky | 95.3 | 98.3 | 86.3 |
  | never_fold_pre | 93.3 | 92.0 | 87.7 |

  Pooled, that is 1,099 against 1,101 of 1,200, so the search equals the policy even with the true model.
* **Reading:**
  * A one-street search is not a better decision maker than the trained policy, even when it knows the
    opponent's exact rules. So improving X1 alone cannot produce a gain.
  * The procedure has to start from the policy and add the model's information. The candidate is policy
    improvement by rollouts: our policy for us, the model for them, scored in match-win utility. It
    improves on its base policy when the model is right (Tesauro and Galperin 1996; Bertsekas, rollout
    algorithms).
  * The next test is that procedure with the oracle model, offline, before any runtime or model work.
* **Kept:** match-win utility, the effective stack, the oracle tool, the judge and stats tools. holdem-rl
  b74030e has the search off by default. It plays byte for byte as c348a59, and the bot imports the search
  lazily, because the deployed image ships neither `rl/search.py` nor `rl/oppmodel.py`; a top-level import
  would have broken the next build (caught before the merge).

### 14.17 X2r: rollout lookahead on the policy, with the true model, adds about 4 points

Roadmap X2r. Tool: `tools/x2r_oracle.py` on holdem-x2r (df4e3c3; worktree `poker-ai-lab-x2r`, not merged).
At each decision the policy acts as usual. For each candidate action, N rollouts rebuild the hand by
replay, play the candidate, then finish the hand with a copy of the policy for us and a fresh StyleBot for
them. The opponent's cards come from the exact posterior of its rules, the board is common across
candidates, and the value is `win_prob` at the end of the hand. The hero overrides when the best paired
gain beats Z standard errors.

Tests (`tests/test_x2r.py`): the rebuilt spot equals the real GameState at every decision, rollouts leave
the real hero, its tracker and the opponent untouched, and with N = 1 and no gate it plays exactly as the
policy on 20 seeds. Eight mutations were caught.

**N = 16, Z = 2 (300 matches per cell, seed 41; policy alone from the 14.16 judge on the same seeds):**

| cell | off | on | difference [95%] | overrides |
|---|---|---|---|---|
| raise_station | 94.7 | 94.0 | -0.7 [-4.5, +3.2] | 8.9% |
| sticky_overbettor | 83.0 | 83.0 | +0.0 [-6.0, +6.0] | 6.1% |
| tight_sticky | 95.3 | 91.3 | -4.0 [-8.2, +0.0] | 7.5% |
| never_fold_pre | 93.3 | 95.3 | +2.0 [-1.8, +5.9] | 7.8% |
| pooled | 91.6 | 90.9 | -0.7 [-2.9, +1.6] | |

* **No headroom found.** Matches got shorter: hands per win fell in every cell, for example 31.8 to 20.4
  against tight_sticky. The win rate did not change.
* **The null was a power problem.** With 16 rollouts, a 2 standard-error gate and about 5 candidates, noise
  alone passes the gate on roughly a tenth of the decisions, close to the observed 6 to 9%, and the predicted
  gains per override (0.02 to 0.04 in match-win probability) did not appear in the results.

**N = 128, Z = 2.6 (chosen after the N = 16 run, so post hoc; same seeds):**

| cell | off | on | difference [95%] | paired [95%] | b / c | overrides |
|---|---|---|---|---|---|---|
| raise_station | 94.7 | 98.0 | +3.3 [+0.3, +6.7] | +3.3 [+1.1, +5.6] | 11 / 1 | 14.3% |
| sticky_overbettor | 83.0 | 88.0 | +5.0 [-0.7, +10.7] | +5.0 [+0.6, +9.4] | 30 / 15 | 7.1% |
| tight_sticky | 95.3 | 97.0 | +1.7 [-1.5, +5.0] | +1.7 [-0.9, +4.2] | 10 / 5 | 9.2% |
| never_fold_pre | 93.3 | 98.7 | +5.3 [+2.2, +8.8] | +5.3 [+2.5, +8.2] | 18 / 2 | 9.1% |
| pooled | 91.6 | 95.4 | +3.8 [+1.9, +5.8] | +3.8 [+2.3, +5.4] | 69 / 23 | |

* Paired: matches paired on opponent, seed and seat (`tools/paired_stats.py`); b counts matches only the
  lookahead won, c only the policy. Losses fall from 8.4% to 4.6%.
* **What the overrides do:** against raise_station, check instead of betting (it raises bets); against
  sticky_overbettor, fold instead of calling its big bets (the largest gain, about 0.07 per override);
  against tight_sticky, both folds and calls.
* **Cost:** about 1.9 s per decision on one box core, so it does not fit the deployed budget as it stands.

**Confirmed on fresh seeds** (seed 43; the off arm is N = 1, which plays exactly as the policy; then N = 128,
Z = 2.6; `~/poker-ai-lab-x2r/logs/x2r_s43_off` and `x2r_s43_on`):

| cell | off | on | paired [95%] | b / c |
|---|---|---|---|---|
| raise_station | 97.0 | 98.3 | +1.3 [-0.3, +2.9] | 5 / 1 |
| sticky_overbettor | 83.0 | 90.0 | +7.0 [+2.5, +11.5] | 35 / 14 |
| tight_sticky | 94.0 | 98.0 | +4.0 [+1.3, +6.7] | 15 / 3 |
| never_fold_pre | 94.7 | 99.0 | +4.3 [+1.8, +6.8] | 14 / 1 |
| pooled | 92.2 | 96.3 | +4.2 [+2.7, +5.7], p < 0.001 | 69 / 19 |

Unpaired, the pooled difference is +4.2 [+2.3, +6.1]. Losses fall from 7.8% to 3.7%. **With the true model,
rollout lookahead on top of the policy halves the losses against these bots.** The next question is the
model we actually have (roadmap X2m).

### 14.18 X2m: with X1 in place of the true rules, the lookahead loses on wide bettors and does not reliably gain on real bots

Roadmap X2m. Tool: `tools/x2r_oracle.py --model x1` on holdem-x2r (4d9c1ed, memo f6777b8, tests f427155; two
fresh verifiers found the implementation right and the tests short, and every real mutation they found now
fails a test). N = 128, Z = 2.6, seed 41, 300 matches per cell, paired against the judge's search-off rows.

| cell | off | on | paired [95%] | b / c | overrides |
|---|---|---|---|---|---|
| raise_station | 94.7 | 89.3 | -5.3 [-8.6, -2.1] | 5 / 21 | 12.9% |
| sticky_overbettor | 83.0 | 72.3 | -10.7 [-16.4, -4.9] | 24 / 56 | 9.6% |
| tight_sticky | 95.3 | 93.7 | -1.7 [-4.5, +1.2] | 7 / 12 | 10.4% |
| never_fold_pre | 93.3 | 96.0 | +2.7 [-0.4, +5.7] | 15 / 7 | 10.7% |
| pooled | 91.6 | 87.8 | -3.8 [-5.7, -1.8], p < 0.001 | 51 / 96 | |

* **R fails.** With the true rules the same procedure added +3.8 on these seeds; with X1 it loses 3.8. The
  procedure is not the problem (14.17); the model is.
* **Where it loses:** against sticky_overbettor, X1's lookahead turns calls into folds on every street (flop
  487, turn 298, river 108 overrides, against 136 flop folds with the true rules), and its matches double in
  length (17.8 to 35.2 hands per win). Against raise_station it raises the river into the bot (219 checks
  turned into raises) where the true model checks.
* **Reading:** X1 predicts action frequencies well (14.13), but the rollout opponent and the root range both
  assume an action reveals a band of hand strength (weak fold, middle call, strong raise). These bots bet and
  raise with wide ranges, so the model makes every bet look strong and the lookahead folds too much. This is
  limit 1 of the universal design (ranges from an action model by frequency matching).

**The `ext:` cells** (unpaired against the judge's off arm, Newcombe; `~/poker-ai-lab-x2m/logs/x2m_ext`):

| cell | off | on | difference [95%] | overrides |
|---|---|---|---|---|
| ext:ashwing | 73.0 | 78.7 | +5.7 [-1.2, +12.5] | 13.9% |
| ext:ashwing_search | 74.7 | 80.7 | +6.0 [-0.7, +12.6] | 14.0% |
| ext:ashwing_hive | 86.7 | 85.7 | -1.0 [-6.6, +4.6] | 10.3% |
| ext:autodidact | 76.3 | 79.3 | +3.0 [-3.7, +9.6] | 12.5% |
| ext:wolf | 94.3 | 96.3 | +2.0 [-1.5, +5.6] | 9.8% |
| pooled, five bots | 81.0 | 84.1 | +3.1 [+0.4, +5.8] | |

* `ext:wolf_v5` plays exactly as `ext:wolf` (300 of 300 matches the same on, 299 of 300 off), so it is one
  bot; the pre-registered six-cell pool, which counts it twice, reads +2.9 [+0.6, +5.3].
* **E holds, R fails.** Under the pre-registered read the procedure gains on real bots with the model we
  have, and the largest gains are on the Ashwing family, the gap the roadmap targets (73 against a
  specialist's 90). It also loses on bots that bet wide (sticky_overbettor -10.7), so it cannot ship as is:
  a field with such bots would pay for it.

**Confirmation on fresh seeds** (seed 43, `tools/x2m_confirm.sh` at 5ee89f5; each arm has its own off run
with N = 1, which plays exactly as the policy, so the read is paired; `~/poker-ai-lab-x2m/logs/x2m43_*`):

| cell | off | on | paired [95%] | b / c | overrides |
|---|---|---|---|---|---|
| ext:ashwing | 75.7 | 79.0 | +3.3 [-2.0, +8.7] | 39 / 29 | 13.7% |
| ext:ashwing_search | 76.0 | 80.3 | +4.3 [-1.1, +9.7] | 41 / 28 | 13.5% |
| ext:ashwing_hive | 85.7 | 80.3 | -5.3 [-10.9, +0.2] | 28 / 44 | 10.4% |
| ext:autodidact | 79.3 | 80.3 | +1.0 [-4.3, +6.3] | 34 / 31 | 12.6% |
| ext:wolf | 95.7 | 97.0 | +1.3 [-1.1, +3.8] | 9 / 5 | 9.8% |
| pooled, five bots | 82.5 | 83.4 | +0.9 [-1.3, +3.2], p = 0.44 | 151 / 137 | |
| raise_station | 97.0 | 89.3 | -7.7 [-11.0, -4.4] | 2 / 25 | 12.7% |
| sticky_overbettor | 83.0 | 69.7 | -13.3 [-19.3, -7.4] | 24 / 64 | 10.2% |
| tight_sticky | 94.0 | 93.7 | -0.3 [-3.5, +2.8] | 11 / 12 | 11.6% |
| never_fold_pre | 94.7 | 97.7 | +3.0 [+0.5, +5.5] | 12 / 3 | 10.7% |
| pooled, rule cells | 92.2 | 87.6 | -4.6 [-6.6, -2.6], p < 0.001 | 49 / 104 | |

The pre-registered E read (unpaired Newcombe on the five bots) is +0.9 [-1.8, +3.6].

* **E does not confirm; R fails again.** On fresh seeds the gain on real bots shrinks to +0.9 with an
  interval across zero, and ashwing_hive turns to -5.3. The Ashwing and Ashwing search cells still lean
  positive (+3.3, +4.3), but no single cell clears its interval on either seed. The loss on wide bettors
  replicates and grows (-4.6 pooled, sticky_overbettor -13.3, raise_station -7.7).
* **Verdict:** the lookahead with X1 is not a candidate. The procedure is sound (14.17: +4.2 with the true
  model, confirmed); the model is the limit. Seed 41's +3.1 was the high end of a small effect.
* **Next:** limit 1, the opponent model. X1 says how often an opponent acts, not with what hands; the
  lookahead needs the second. The fix is a card-conditioned opponent model (what each action means for the
  hand), learned where cards are seen. Its spec goes in the roadmap before any code.

### 14.19 X2m ablation: X1's range at the root carries the whole loss

Roadmap "X2m result and the ablation". Tool: `tools/x2r_oracle.py --model oracle-range | x1-range` on
holdem-x2r (cf0a867; a fresh verifier confirmed that the `oracle` and `x1` arms still play byte for byte as
before over 120 matches, and the tests kill 6 of 7 planted mutations). N = 128, Z = 2.6, seed 43, the four
rule cells, 300 matches per cell, paired on the same seeds as the reference arms (`tools/x2m_ablate.sh`,
`~/poker-ai-lab-x2m/logs/x2ma_*`).

Paired against the oracle arm (the true rules for both the range and the rest of the hand; a negative number
is what the arm loses to it):

| cell | oracle-range (X1 finishes the hand) | x1-range (X1's range at the root) | x1 (both, 14.18) |
|---|---|---|---|
| never_fold_pre | +0.0 [-1.3, +1.3] | -4.3 [-6.8, -1.8] | -1.3 [-2.9, +0.3] |
| raise_station | -0.3 [-2.1, +1.4] | -12.3 [-16.2, -8.5] | -9.0 [-12.4, -5.6] |
| sticky_overbettor | -3.3 [-7.1, +0.5] | -15.0 [-20.6, -9.4] | -20.3 [-25.9, -14.8] |
| tight_sticky | -0.3 [-2.1, +1.4] | -4.3 [-7.3, -1.4] | -4.3 [-7.0, -1.7] |
| pooled | -1.0 [-2.2, +0.2] | -9.0 [-11.0, -7.0] | -8.8 [-10.6, -6.9] |

Against the off arm: `oracle-range` +3.2 [+1.6, +4.7] (the oracle arm's +4.2, nearly all of it), `x1-range`
-4.8 [-6.9, -2.7].

* **Read (pre-registered):** the range's loss is 9.0 [7.0, 11.0], lower bound above zero; the continuation's
  loss is 1.0 [-0.2, 2.2]. Only the range clears, so it is fixed first. The range alone accounts for the whole
  8.8-point gap; the continuation's lean on sticky_overbettor (-3.3) is rechecked after the range is fixed.
* **Where:** against sticky_overbettor, X1's range turns the policy's preflop raises into folds (525
  overrides, against 93 with the true range) and its flop and turn calls into folds (480 and 275, against 107
  and 56). Against raise_station it bets into the bot on the turn and river after it checks (check to raise
  105 and 157, against 21 and 54).
* **Mechanism, with the rules in `holdem/opponents.py`:** raise_station checks and calls after the flop with
  every hand; sticky_overbettor bets 65% of its worst hands. The band rule reads the first's checks as
  weakness and the second's bets as strength. Two causes are not separated yet: X1's frequencies in that
  context (a band whose width is wrong) and the band rule itself (an action that says nothing about the cards
  still cuts the range). X3 separates them before changing either.

### 14.20 X3a: today's range is worse than no range; the λ range fixes it, and frequency error is the larger part

Roadmap X3a. Tool: `tools/x3_range.py` on holdem-x2r 4e51db8 (a first run was invalid: the simulation
skipped X1's update on hands without a showdown; fixed, and a fresh verifier confirmed the fix), run by
`tools/x3_run.sh` on gb10-d (`~/poker-ai-lab-x3v2/logs/x3a`), 23:46 to 02:06 UTC. Score: nats the actions
told us about the opponent's true combo (log share of the true combo minus the uniform prior's), at hero
decisions after the opponent acted; 0 is "no better than knowing nothing".

| cell | R1 (today) | R2 (true freq, band) | R4 (X1 freq, λ) | R2λ (true freq, λ) | R5 (exact) |
|---|---|---|---|---|---|
| never_fold_pre | +0.012 | +0.453 | +0.231 | +0.376 | +0.815 |
| raise_station | -0.803 | +0.467 | +0.019 | +0.286 | +0.554 |
| sticky_overbettor | -0.158 | +0.175 | +0.001 | +0.211 | +0.632 |
| tight_sticky | -0.397 | +0.379 | +0.095 | +0.502 | +0.955 |
| rule pool | -0.336 | +0.369 | +0.086 | +0.344 | +0.739 |
| ext:ashwing | -0.050 | | +0.237 | | |
| ext:ashwing_hive | -0.118 | | +0.248 | | |
| ext:ashwing_search | -0.083 | | +0.234 | | |
| ext:autodidact | +0.095 | | +0.277 | | |
| ext:wolf | -0.289 | | +0.187 | | |
| held-out replays (99 matches) | -0.727 | | +0.366 | | |

200 matches per simulated cell, seed 47. Pooled reads, 95% intervals (bootstrap over matches, paired):

* F (frequency part) +0.481 [+0.453, +0.511]; V (reveal part) +0.199 [+0.177, +0.222]; interaction
  -0.447 [-0.479, -0.416]; gap R5 - R1 +1.075 [+1.031, +1.119].
* R4 - R1: `ext:` pool +0.325 [+0.301, +0.352]; held-out replays +1.093 [+0.978, +1.221] (R4 above R1 in 97
  of 99 matches).
* All four bounds clear. Printed action: **X3b runs, and a frequency spec is written.**
* λ: the pre/post-flop variant was not chosen (validation, 46 matches: +0.005 [-0.006, +0.017]). π0 puts
  0.31 on λ = 0.3 and 0.30 on λ = 0.4 (mean 0.35); nothing above 0.7.

Read:
* **Today's range misleads.** R1 is below zero on every rule cell but one, on 4 of 5 `ext:` cells and on
  held-out replays (-0.73): X1's band with OUTSIDE = 0.1 puts less weight on the true combo than the uniform
  prior does. This is the 14.19 loss from the other side.
* **The λ range fixes the sign everywhere,** most on real data (held-out +1.09). Real bots reveal about a
  third of what a strict band assumes (λ ≈ 0.35).
* **The interaction is as large as V,** so the two parts are not separate effects. Simple effects (rule pool):
  λ adds +0.42 with X1's frequencies but -0.02 with the true ones; the true frequencies add +0.70 under the
  band and +0.26 under λ. λ mostly protects against wrong frequencies. With right frequencies the band is
  nearly as good as λ (R2 +0.369 vs R2λ +0.344), and per cell λ helps where the bot reveals little
  (sticky_overbettor, tight_sticky) and hurts where the band fits (raise_station -0.18, never_fold_pre -0.08).
* **Ceiling:** R4 closes 0.42 of the 1.08 gap. True frequencies reach about two thirds of it; the last third
  (R5 - R2) is what a strength-ordered band cannot express. So frequency is the larger lever, which is what
  the frequency spec targets.
* Not yet known: whether a better range wins matches. X3b measures that.

### 14.21 X3b: the lookahead with the λ range gains on the real bots, still loses to one wide bettor

Roadmap X3b. Tool: `tools/x2r_oracle.py --model x3` on holdem-x2r d0008b9 (`X3Root`: the λ range R4 of 14.20
at the root, `X1Bot` finishing the hand; a fresh verifier confirmed it), `tools/x3b_run.sh` on gb10-d
(`~/poker-ai-lab-x3b/logs/x3b49_*`), 03:07 to 07:59 UTC. N = 128, Z = 2.6, seed 49, 300 matches per cell,
against the N = 1 off arm on the same seeds (which plays as the policy).

| cell | off | on | difference | 95% interval | hands per win off/on |
|---|---|---|---|---|---|
| never_fold_pre | 94.3 | 97.3 | +3.0 | [+0.2, +5.8] | 15.7/15.7 |
| raise_station | 95.3 | 97.3 | +2.0 | [+0.2, +3.8] | 12.9/12.2 |
| sticky_overbettor | 81.7 | 70.0 | -11.7 | [-17.8, -5.5] | 17.9/38.2 |
| tight_sticky | 95.0 | 95.0 | +0.0 | [-2.9, +2.9] | 32.0/34.8 |
| rule pool (paired) | | | -1.7 | [-3.6, +0.3] | |
| ext:ashwing | 73.7 | 82.7 | +9.0 | [+2.4, +15.5] | 39.1/43.5 |
| ext:ashwing_search | 74.7 | 83.3 | +8.7 | [+2.1, +15.1] | 40.0/44.5 |
| ext:ashwing_hive | 84.7 | 90.0 | +5.3 | [-0.0, +10.7] | 47.2/47.7 |
| ext:autodidact | 77.0 | 79.0 | +2.0 | [-4.6, +8.6] | 37.1/43.9 |
| ext:wolf | 97.7 | 98.3 | +0.7 | [-1.8, +3.3] | 22.3/24.4 |
| ext pool (unpaired) | 81.5 | 86.7 | +5.1 | [+2.5, +7.7] | |

Rule cells paired (`tools/paired_stats.py`); `ext:` cells unpaired (Newcombe), since Ashwing and autodidact
were unseeded in this run (seeded since holdem-x2r 30cfa1a). The lookahead overrode the policy at 7 to 12% of
its decisions in every cell.

* **Read (pre-registered):** a candidate needs both pools' lower bounds above zero. The `ext:` pool clears,
  the rule pool does not, so X3b is **not a candidate**, and seed 51 is not run.
* **Against the earlier arms:** X2m's x1 arm lost 4.6 on the rule pool (14.18); the λ root brings it to -1.7.
  On the real bots the same lookahead now gains +5.1, against no reliable gain in 14.18. The Ashwing family,
  the bots the policy was weakest against (M1: specialist ceiling 90%), gains the most.
* **The loss is one cell.** Against sticky_overbettor (bets 65% of its worst hands, 14.19) matches run twice as
  long and the lookahead loses 11.7. X3a found X1's frequencies are the larger error (14.20), and 14.19 found
  a -3.3 lean of the continuation in that cell. Both are untouched here; X4 starts from this cell.
* **Runtime:** N = 128 does not fit the arena (R1: about 3 s mean and 6 s max at 0.5 vCPU). R1 measures
  whether N = 32 keeps this gain.

### 14.22 R1: N = 32 fits the arena and keeps the lookahead's gain; N = 8 loses badly

Roadmap R1. holdem-x2r d4c3cb8 on gb10-d (`~/poker-ai-lab-r1/logs/r1_*`), 2026-11-24, finished 09:32 UTC. x3 at
Z = 2.6, seed 49, 300 matches per cell. Rule cells read paired against X3b's N = 1 off arm; `ext:` cells read
paired against a new N = 1 off arm with the seeded bots (holdem-x2r 30cfa1a). `tools/paired_stats.py`.

| arm | rule pool | sticky_overbettor | `ext:` pool | box seconds per decision, mean / max |
|---|---|---|---|---|
| N = 128 (X3b, 14.21) | -1.7 [-3.6, +0.3] | -11.7 | +5.1 [+2.5, +7.7] unpaired | about 1.5 / - |
| N = 32 | +0.1 [-1.6, +1.8] | -3.0 [-8.6, +2.6] | +2.8 [+0.9, +4.7] | 0.25 to 0.43 / 1.0 |
| N = 8 | -12.4 [-14.8, -10.0] | -11.0 | -11.9 [-14.3, -9.5] | 0.07 / 0.22 |

N = 32 `ext:` cells: ashwing +4.7, ashwing_search +6.0, ashwing_hive +3.0, autodidact +2.3, wolf -2.0 [-4.3, +0.3].

* **Fits:** a gb10-d core times like the PC core (R1 timing), so N = 32 is inside the pre-registered bound (mean
  at most 0.5 s, max at most 2 s); the arena's 0.5 vCPU doubles it to about 0.9 s mean, 2 s max, under 5 s.
* **Keeps the gain:** the `ext:` pool still gains (+2.8, lower bound above zero), and the rule pool no longer
  loses (+0.1; sticky_overbettor -3.0 against -11.7 at N = 128). So the deploy path is the lookahead at N = 32;
  distillation is not needed for runtime.
* **Not a candidate yet:** the X3b rule (both pools' lower bounds above zero) is not met; the rule pool's is
  -1.6. Not re-scored under a looser rule.
* **N = 8 loses in every cell,** wolf included (-18). With 8 samples the gate at Z = 2.6 still lets through
  overrides that are noise. Any later N below 32 needs its own read.
* The two `ext:` reads differ in kind (N = 128 unpaired against unseeded bots, N = 32 paired against seeded
  ones), so +2.8 against +5.1 is not a measured loss from the smaller N.

### 14.23 X4 where: X1 stays near its population prior inside a match

Roadmap X4, first step. Tool: `tools/x4_where.py` on holdem-x2r 8aba00c (an optional probe hook in
`tools/x3_range.py`, scores unchanged with it on; 2 tests), X3a's simulation (seed 47, 200 matches per rule cell),
PC, 2026-11-24. Per opponent action: X1's prediction before it against the bot's true frequencies on the viewer's
live combos, collapsed to fold / call / raise; KL(true || X1) in nats. Table: holdem-x2r `logs/x4/table.txt`.

| cell | actions | KL per action | top spots (share of the cell's KL) |
|---|---|---|---|
| sticky_overbettor | 7,794 | 0.268 | preflop facing a small bet 32%, flop no bet 21%, turn no bet 15%, preflop no bet 11%, river no bet 11% |
| raise_station | 11,390 | 0.247 | preflop facing a small bet 14%, flop / turn / river no bet 13% each, preflop no bet 9% |
| tight_sticky | 14,105 | 0.122 | preflop facing a small bet 45%, river no bet 12%, preflop facing a medium bet 10% |
| never_fold_pre | 11,692 | 0.113 | river no bet 20%, preflop facing a small bet 16%, turn no bet 13%, river facing a big bet 10% |

* **One pattern in every cell: X1 predicts the middle.** sticky_overbettor bets 0.76 to 0.83 when checked to
  on the flop, turn and river; X1 says 0.46 to 0.49. raise_station never bets postflop; X1 says 0.19 to 0.20.
  tight_sticky folds 0.63 to a small preflop raise; X1 says 0.42.
* **Why:** for an opponent without a name profile (every simulated rule bot), X1 predicts
  (in-match counts + 8 x prior) / (count + 8) per spot. A spot sees about 10 actions in a match (2,107 flop
  no-bet actions over 200 matches), so the population prior carries most of the weight for most of the match.
  The prior network is fitted to the pooled population, which bets about half the time.
* So the first fix to test is the prior weight `k_im` (today 8), measured where it can hurt: on the real bots
  and held-out replays, which are noisier than the rule bots. Specified in roadmap X4.

### 14.24 X4 step 2: a lighter in-match prior does not help on real bots; k_im stays 8

Roadmap X4, step 2, pre-registered before the run. Code: holdem-x2r cb12f5f (`OppModel` and `tools/x3_range.py`
take a `k_im` override; `tools/x4_sweep.py`, `tools/x4_sweep_run.sh`), gb10-d cores 0-3, 2026-11-24 10:40 to 11:17
UTC. Every arm is X1 with that `k_im` end to end (its own pi0, its own scores); the simulated matches are played
once and every arm scores the same match, so the arms are paired. Score: X3a's R4 (nats about the opponent's true
combo, higher is better), seed 47, 200 matches per simulated cell, the 99 held-out replay matches. Difference
against `k_im` = 8 with a paired bootstrap 95% interval (2,000 resamples). Output on gb10-d
`~/poker-ai-lab-x4s/logs/x4s/report.txt`.

| pool | k_im 8 | 4 minus 8 | 2 minus 8 | 1 minus 8 |
|---|---|---|---|---|
| **`ext:` + replays (deciding, six parts equal)** | +0.2530 | +0.0036 [-0.0001, +0.0073] | -0.0042 [-0.0096, +0.0013] | -0.0217 [-0.0290, -0.0149] |
| `ext:` cells | +0.2304 | +0.0049 [+0.0007, +0.0090] | -0.0044 [-0.0107, +0.0021] | -0.0228 [-0.0308, -0.0152] |
| held-out replays | +0.3660 | -0.0026 [-0.0117, +0.0040] | -0.0029 [-0.0113, +0.0039] | -0.0161 [-0.0324, -0.0032] |
| rule cells (reported, do not choose) | +0.0863 | +0.0217 [+0.0163, +0.0269] | +0.0371 [+0.0292, +0.0453] | +0.0352 [+0.0239, +0.0464] |

* **Verdict by the pre-registered rule: none.** The best arm on the deciding pool is `k_im` 4, and its lower
  bound against 8 is -0.0001, not above zero. The half-and-half weighting (the `ext:` pool and the replays
  each half) gives none as well. `k_im` stays 8; X4 moves to the per-name prior from D's archive.
* **The size is the finding, not only the sign.** Even the best arm moves the real-bot score by 0.004 nats,
  against the 1.09 nats the λ range gained in 14.20. The rule bots want less prior (deterministic play, +0.037
  at `k_im` 2); the real bots do not (autodidact and Wolf lose 0.02 to 0.05 at `k_im` 1 and 2). A lighter prior
  fixes "X1 predicts the middle" for a bot that always does the same thing and adds noise for a bot that
  mixes, so a single weight cannot serve both.
* **Power limit, measured before the read:** 90.1% of the held-out replay actions go through a named profile
  (k = 20, w = 2), only 9.9% through `k_im`, so the replay part barely moves with `k_im` and the decision is
  carried by the simulated `ext:` cells.
* **Checks.** The `k_im` = 8 arm reproduces 14.20 exactly (max per-match difference 0) on the four rule cells,
  `ext:wolf`, the held-out replays and pi0. The four Ashwing and autodidact cells differ because 14.20 ran those
  bots unseeded (seeding came in holdem-x2r 30cfa1a): two runs of 14.20's code on the same seed differ from
  each other, two runs of today's code are identical and equal the sweep's rows. The four pi0 tables are
  identical across arms because every fitting-match action goes through a named profile, where `k_im` has no
  effect. Tests: 43 pass (test_x4_sweep, test_oppmodel, test_x3). Fresh outcome verifier CONFIRMED (its own
  recompute from the raw rows; the choice is none at five other bootstrap seeds, lower bound -0.00014 to
  -0.00019).

### 14.25 D2a stage 2: clones of the adaptive bots are easier than the real bots, and more data makes it worse

Roadmap D2a, pre-registered. Code: holdem-d2 3f0d58d (21 tests; `tools/d2_mutate.py` kills 25 of 25 planted
faults), gb10-d cores 4-19 plus GPU, 2026-11-24 09:32 to 12:28 UTC (about 2.9 box-hours against a computed 1.7
and a stop at twice that; no control reran). Read 1: fb2-900 plays 3,000 matches per cell, seed 63, paired on
(seed, hero seat); the difference is our win rate against the cell minus against the real bot, positive when
the cell is easier; 90% interval (z 1.645); a cell passes when the interval lies inside ±5 points. Read 2:
per-decision log-likelihood (code and size) of the bot's actual action with the true cards, held-out logs
(seed 62). Output on gb10-d `~/poker-ai-lab-d2s2/logs/d2/<bot>/read1_63.json`, `read2_*.json`.

| bot (our win rate against the real bot) | control | neural, 1,000 matches | neural, 5,000 | table, 5,000 |
|---|---|---|---|---|
| ext:ashwing (73.5) | +0.8 [-0.4, +2.1] pass | +3.3 [+1.8, +4.8] pass | **+6.8 [+5.3, +8.2] fail** | **+5.9 [+4.4, +7.4] fail** |
| ext:autodidact_fast (77.3) | +0.4 [-0.9, +1.7] pass | +1.9 [+0.4, +3.3] pass | +3.3 [+1.9, +4.8] pass | **+4.1 [+2.7, +5.6] fail** |
| ext:wolf (96.6) | 0 (deterministic) pass | -0.5 [-1.2, +0.2] pass | +0.6 [-0.1, +1.2] pass | -0.0 [-0.7, +0.7] pass |

| read 2, log-likelihood per decision | neural 100 | neural 1,000 | neural 5,000 | table 100 | table 1,000 | table 5,000 |
|---|---|---|---|---|---|---|
| ext:ashwing | -0.334 | -0.322 | **-0.200** | -0.251 | -0.236 | -0.229 |
| ext:autodidact_fast | -0.616 | -0.364 | **-0.205** | -0.482 | -0.446 | -0.438 |
| ext:wolf | -0.564 | -0.492 | **-0.317** | -0.493 | -0.444 | -0.434 |

* **Verdict per bot, by the pre-registered rule.** Wolf: the neural method is trusted from 1,000 matches (the
  table clone passes too). autodidact_fast: trusted from 1,000 matches. Ashwing: the 5,000-match clone fails,
  and the rule makes that the finding: replay clones are not trusted for bots like it, even though the
  1,000-match clone passed.
* **Closer actions, weaker clone.** With 5,000 matches the neural clone predicts the actual actions best of
  every method on every bot (read 2), yet against Ashwing it is easier than the 1,000-match clone (+6.8 against
  +3.3), and against autodidact as well (+3.3 against +1.9). Per-decision likelihood and strength against us
  move apart. A likely reason, not tested here: likelihood is dominated by the many cheap decisions, while
  the match is decided by the few big pots, where the clone's errors cost the most.
* **Every clone of the two adaptive bots is easier than the real bot** (all six lower bounds above zero), the
  same direction as 14.3's 84 to 89% against clones and 49 to 64% against the code, now 2 to 7 points instead of
  20 to 35. Even a passing clone is biased by about +2 to +3 points, the size of the effects we read (R1's
  lookahead gain is +2.8). So clones do not judge candidates; only the real code and the real arena do.
* **What D does next.** For adaptive bots D leans on D3 (the parametric style population) and real-arena
  evaluation, as the rule says. For bots like Wolf and autodidact the neural method is usable from 1,000
  matches; 13 names in the archive have that many (19,488 files at 2026-11-25 03:50 UTC, fetch running).

### 14.26 M3, first read: v4's Season 16 round 1 loss, and which of its two visible leaks is real

Data: the archive on gb10-d (`~/chipzen-replays`, 19,488 files at 2026-11-25 03:50 UTC), D2a's fitting logs
(fb2-900's policy, v4's network, against the real code of Ashwing, autodidact_fast and Wolf, about 2,500
matches, true cards from `true_cards.jsonl`). Probes: `m3_leaks.py` and `flop_aggr.py` (gb10-d `~/m3/`; to move
into a tools folder with the M3 slice). The probe reproduces the live match's three river all-ins.

* **Live record of our bots in the archive: 7 matches, 6 won.** The loss: poker-ai-lab-v4 against MonteCarlo,
  2026-11-24 18:30 UTC (match 4b2a2beb), busted in 26 hands. Correction (same day): this is v4's Season 16
  round 1 fixture, and the win against fermat-mini at 22:50 UTC is round 2 (fixture times in
  `docs/handoff-log-2026-11-24.md` on holdem-chipzen). The API labels both `challenge`; the round 1 match is
  unrated, the round 2 match rated. Season record after two of eight rounds: 1-1.
* **The live loss, by hand:** about 3,500 chips folded to flop and turn bets (hands 7, 9, 15, 21, 23, 25);
  about 3,500 on river value raises into better hands (hands 4, 17); the bust in hand 26, a river all-in of
  4,798 into a 300 pot (blinds 75/150) with a pair of jacks, called by two pair. v4 had shoved the river into
  small pots twice before and got folds (hands 1 and 16).
* **The river overbet all-in is not a measured leak against the real code.** fb2-900 shoves the river 4,075
  times in those logs, almost all with made hands, median 9 to 22 times the pot; the bots call 42 to 53% and
  every made-hand class nets +3,400 to +4,700 per shove (one pair +3,867). Hands below 0.6 strength: 134,
  net +77,045. Against a bot that calls only with better hands it would lose; none of the three does. So it is
  not a leak against these callers; MonteCarlo belongs to the solver-like family (Revision 3), and against
  that family's proxy bp100 the lost matches end in underdog all-ins (P0 measures it at n = 4,000).
* **The flop fold is a measured leak.** Facing a flop bet of 0.4 to 0.8 pot, fb2-900 folds 60.7% (8,764
  spots), where a bet with any two cards breaks even at 39.5% folds; 0.8 to 1.5 pot: 60.1% against 46.4%. The
  turn is at the line (38.4% against 38.2%); the river is over it (49.1% against 36.9%). The old heuristic bot
  shows the same shape. This matches the exploiter (14.8: fb2-900 folds after the flop too often).
* **The field has the style that takes it.** Of 154 names with at least 200 unbet flop decisions, 22 bet 70% or
  more of them (1,783 matches), among them two Season 16 entrants, HRT (0.97) and Shadow (0.77). slopBot (0.95)
  beats Blueprint 125 of 199. MonteCarlo bets 0.30 of unbet flops across its 195 matches but bet most flops
  against v4, a hint that it adapts (one match, not tested).

### 14.27 S2r and P0: it1800 does not beat fb2-900 against bp100; fb2-900 loses its matches through worse stack commitments

Roadmap Revision 3, S2r and P0, both pre-registered before the run. gb10-d `~/poker-ai-lab-rl` (holdem-rl
tree; runner `tools/s2r_run.sh`, holdem-rl f2d6c5d), 2026-11-25 04:20 to 04:28 UTC, bpopp:v011 with the eval
card's settings, seed 81 (fresh), 4,000 matches per arm, 6 workers. Output `logs/s2r/`.

* **S2r:** fb2-900 59.85% [58.3, 61.4]; S2 it1800 58.73% [57.2, 60.2]. Paired on (seed, hero seat)
  (`tools/paired_stats.py`): it1800 minus fb2-900 **-1.1 [-2.8, +0.6]** (567 against 612 discordant pairs,
  sign test p 0.20). By the rule: it1800 does not lead, nothing goes to Wayne, and B1 starts from fb2-900.
  The n = 400 read of 14.9 (59.0) is confirmed with a quarter of the width.
* **P0** (`tools/p0_read.py`, holdem-rl 8d77826, on chipflow's 4,000 matches of fb2-900, same seed). Per match,
  the final hand, which is always an all-in here; the loser made the last voluntary commitment in it (its
  shove was called, or it called the other's all-in); its equity against the winner's actual hand at that
  moment. Matches whose loser started the hand with 1 bb or less are forced and left out (19 of fb2-900's
  losses, 535 of bp100's: fb2-900 grinds bp100 down more often than the reverse).

  | | fb2-900's losses (1,587) | bp100's losses (1,859) |
  |---|---|---|
  | loser equity under 0.35 | **77.6%** | **47.8%** |
  | mean loser equity | 0.200 | 0.368 |
  | biggest ways to lose | flop shove called 37% (mean equity 0.284); river shove called 20%; river call of an all-in 15%; preflop shove called 14% (0.419) | preflop call of an all-in 35% (0.511); flop call 20% (0.396); river call 12%; turn call 11% (0.230) |

  Difference **+29.8 points [+26.7, +32.9]** against the pre-registered trigger of +10 with the lower bound
  above zero: **B0 runs before G1, X5 and B1.**
* **What the split says B0 must address** (read with chipflow's summary, `logs/s2r/flow_fb2.out`):
  * Flop shoves: 4,642, bp100 folds 65% (+3.55M chips), called 1,610 at an expected -1.80M, net +1.75M. In
    chips they pay; in matches they are fb2-900's main way to bust (592 losses). A chip-positive, bust-heavy
    play against an opponent we already beat 60% of the time is a match-equity error, so B0 must decide by
    match-win value (the K of `rl/search.py`), not chips.
  * Calls of bp100's river shoves: 594 at mean equity 0.198, expected -2.46M chips. A plain chip leak.
  * River shoves by fb2-900: 5,467, folds 73%, net +5.82M. Not to touch.
* **Caveat on the statistic:** a river all-in leaves the loser at equity 0 by construction, so the share also
  carries the street mix; fb2-900 gets its stack in on the flop and river, bp100 before the flop at near coin
  flips. That mix is itself the policy's choice, and the flop-shove and river-call lines above are each a
  decision error on their own terms, so the conclusion does not rest on the mix alone.

### 14.28 Match value against bp100 is near linear: K = 4.68 overstates it, and 14.27's flop-shove reading is withdrawn

Data: S2r's chipflow rows (14.27; fb2-900 against bp100, seed 81, 4,000 matches, 173,553 hands). Hero stack at
each hand start (10,000 plus the running sum of `delta`; every match ends at 0 or 20,000) against the match
result. Tool: `kcal.py` (gb10-d `~/m3/`; moves into holdem-rl tools with B0). `win_prob(x, T) =
expm1(-K x / T) / expm1(-K)` from `rl/search.py` (holdem-x2r), where K = 2 ln(0.912 / 0.088) = 4.68 comes from
v4's league field rate.

| hero stack (k chips) | hands | empirical P(win) | win_prob, K = 0.80 | win_prob, K = 4.68 |
|---|---|---|---|---|
| 2 to 4 | 5,122 | 0.220 | 0.205 | 0.509 |
| 6 to 8 | 21,808 | 0.456 | 0.443 | 0.813 |
| 8 to 10 | 39,774 | 0.584 | 0.549 | 0.887 |
| 12 to 14 | 19,753 | 0.775 | 0.736 | 0.961 |
| 16 to 18 | 10,203 | 0.947 | 0.896 | 0.990 |

(The K columns are win_prob at the bin's midpoint, checked by hand for 3k: 0.205 and 0.509.)

* **Against bp100 the match value is close to the chip share.** K = 2 ln(p / (1 - p)) from fb2-900's 59.85%
  gives 0.80, and that curve sits within about 0.04 of the data in every bin. K = 4.68 claims 51% with
  3,000 of 20,000 chips; the data say 22%.
* **Correction to 14.27:** its bullet "flop shoves are a match-equity error, so B0 must decide by the K of
  `rl/search.py`" assumed K = 4.68. At the measured curve the flop shoves' net match value is unresolved (a
  single-pass read by the roadmap agent puts all flop shoves at about +0.2 to +0.6 points of win rate, valued
  against a hand that moves no chips, not against the cheaper action; unverified). Whether a cheaper action
  beats them is a counterfactual nobody has measured; B0b's oracle read is that measurement. P0's rule still
  fired as pre-registered, and the river call-offs (594 at equity 0.198, -2.46M chips) are a loss under every
  curve.
* **Consequence for the lookahead:** every X2/X3/R1 match read used K = 4.68 (`rl/search.py`), which is right
  only against opponents we beat about 91% of the time. Against the strong families the utility is too
  risk-averse. T2 takes the calibrated K as an arm (0.80 replaces the 0.73 of the envelope draft), and the K1
  slice (K from the estimated edge) gains direct evidence.

### 14.29 A0 field map: the archive is two pools; slopBot rates first and over-folds; 5 of the top 10 are exploitable

Tool: holdem-x2r `tools/a0_field.py` (12d4160, 9939bd4, 150aa1b, fix 1d2dd06), run on gb10-d over `~/chipzen-replays`
(16,099 poker matches, 289 names, ordered by `match.started_at`; outputs `~/poker-ai-lab-x2r/logs/a0/`). Outcome
verifier: REFUTED on one fault (step 7(a) reported the top bot's own best result instead of its best opponent's;
"mr_hide beats NashForge 80.8%" was NashForge winning 105 of 130), fixed with a test and plant (11 of 11 plants
caught), the read rerun; every other claim confirmed by its independent re-derivation (Bradley-Terry by MM, fold
excess, swing, clusters, `small_ball` distance).

* **Two pools.** Ten regulars (Fabulous, K3PO, PoetAndCoder, Chatterbox, DeepStack, Kimiko, MercuryRetrograde,
  glambot, qwentom-leap, SolvencyCheck) play each other: 8,441 matches among themselves, 785 against anyone else,
  6,873 among everyone else (re-derived by `pools.py`, gb10-d `~/m3/`, same numbers as the roadmap agent's count).
  An entrant faces a regular in 5.4% of its seats. What an entrant faces (14,531 seats): Blueprint 15.4%, fermat6
  6.8%, NashForge 6.1%, hoops 5.8%, mr_hide 5.7%, r0ckGarden 5.3%, PluriBot 3.8%, slopBot 2.7%, WSmithSimLab 2.3%.
  So A0's per-seat class shares (65% of rated seats in the regulars' pool) are the wrong weights for us.
* **Classes (8 axes, average linkage, cut 0.25):** Blueprint's cluster has 11 names; fermat6, NashForge, hoops,
  MonteCarlo, LimitLess, Dexter form a separate cluster (0.12 to 0.16 from Blueprint's); slopBot alone; PluriBot
  with Shadow; DeepStack alone. MonteCarlo fails "in the solver family" (cluster test; its 0.8 to 1.5 pot fold
  bucket 46.8% against 55.7 to 62.0 ± 5.4), but 152 of its 195 matches are against PluriBot, so its style is
  confounded by one opponent.
* **Rating (Bradley-Terry, ridge, 90% bootstrap):** slopBot first, θ 1.11 [0.93, 1.36], 75% against the mean player
  (279 of 390; 125 of 199 against Blueprint). Seven of the top ten have under 110 matches; the rated-only refit
  reorders them (max change 1.43). Ratings are not used as weights.
* **Exploitable (fixed reading):** 5 of the top 10 (slopBot, ALLIN-v3, Deep_Thought-v12, Chaos_Incarnate,
  NashForge), all by over-folding: slopBot folds 80.8% to flop bets of 0.35 to 0.8 pot against a 36.7% break-even
  (n 921); NashForge 71.1% to river bets of 0.8 to 1.5 pot against 51.1% (n 805). Best opponents: Blueprint wins
  37.2% against slopBot, 44.1% against NashForge. So **L8 is over-weighted**: E3 becomes a reported number. Under the
  rated-only ratings the count is 7.
* **Cold start:** 75.1% of seats face an opponent with 100 or more archived matches (top ten 64.8%); under 1% face a
  first match. 76 names new in 14 days, 21% version suffixes.
* **Swing:** a 5,000-chip hand in 76.5% of matches (re-measures the 76%).
* **Shown all-ins (called and shown):** river 11,529; Blueprint 1,039, fermat6 374, NashForge 316, hoops 221.
* **`small_ball`** (StyleBot with `street_bet`): distance 0.185 and 0.173 (seeds 3, 4) to slopBot's vector, under
  0.25. **fb2-900 against it: 75.7% [73.8, 77.5]; against `tight_sticky` 94.3% [93.1, 95.2]** (seed 93, 2,000
  matches each, no containers). Strength sanity: **bp100 beats `small_ball` 57.0% [52.1, 61.8]** (seed 90, 400
  matches), under the 60% line, so `small_ball` is labelled a strength cell, not a style-only cell. fb2-900 beats it
  by more (75.7%) than bp100 does.

### 14.30 C1: the small-ball class is a population limit (+21.9), so `small_ball` joins B1's training

Pre-registered in roadmap "After A0" (C1, tier 2, seed 93). Best-response fine-tune from fb2-900 against
`small_ball` only (`rl.train` with `--sdk-opps small_ball`, 4 SDK workers, 60 minutes, 3,395 iterations, holdem-x2r
159e9ba on gb10-d cores 0-5, `ckpt/br_small_ball/latest.npz`), read on the same seed-93 matches as fb2-900
(2,000 per cell), paired on (opponent, seed, hero seat) with `tools/paired_stats.py`:

| cell | fb2-900 | best response | paired diff | 95% interval |
|---|---|---|---|---|
| `small_ball` | 75.7% | 97.6% | +21.9 | [+19.9, +23.8] |
| `tight_sticky` | 94.3% | 90.3% | -4.0 | [-5.5, -2.4] |

* **Rule fires:** the gain's lower bound (+19.9) clears +8, so for this class the training population is the limit,
  not the representation: the same network learns to beat a bet-fold aggressor almost always once it meets one.
  `small_ball` joins B1's training population, and `small_ball_b` (the mean vector of BonnieBlue, Chaos_Incarnate,
  Velvet_Shark) becomes the judge-only cell for the class.
* **The cost is real:** a pure best response loses 4 points on `tight_sticky`; B1 trains on a mix so E1 and the
  untrained judges hold.
* Single run, one seed; the training-time win rate rose from about 0.82 to 0.97 within the hour.

### 14.31 T1: training against bp100 lifts fb2-900 from 59.9% to 79.7% (+19.9); B1 takes branch A, B0 step 1 does not run

Pre-registered in roadmap "T1" (tier 3, verifier CONFIRMED the runner). Best response from fb2-900 against bp100 as
the only SDK opponent (plus `rl_br.sh`'s frozen fb2-900 mirror, about 5% of matches; `tools/t1_run.sh`, holdem-rl 114a136, 120 minutes, `ckpt/br_bp100`), read on seed 81, 4,000 matches, paired
on (seed, hero seat) with S2r's fb2-900 rows (`logs/t1/paired.out`, 4,000 pairs joined):

| arm | win rate vs bp100 | paired diff | 95% interval |
|---|---|---|---|
| fb2-900 (S2r) | 59.85% | | |
| best response | 79.7% [78.5, 80.9] | +19.9 | [+18.1, +21.6] (1,110 vs 315 discordant) |

* **Rule fires (lower bound +18.1 at or above +8):** against the solver proxy, the training population is the
  limit, not the representation. B1 takes branch A (population P1, with bp100); B1r is not specified now.
* **B0 trigger (roadmap "Held"):** river call-offs of bp100's shoves fell from 594 per 4,000 matches at mean
  equity 0.198 (-2.46M chips expected) to 57 at 0.675 (+0.11M). Under half of fb2-900's rate, so B0 step 1 does
  not run: training fixes it for a known bot, and B0a returns later as the unseen-name version on top of G1.
* P0's statistic on the same rows (`tools/p0_read.py`): loser equity under 0.35 in 54.5% of the best response's
  losses against bp100's 26.3%, +28.1 [+24.1, +32.1] (fb2-900: +29.8): the gap did not shrink. The losses moved
  off the river calls (the hero's own calls end only 89 of 775 losses) onto the hero's own shoves being called:
  preflop 217 (mean loser equity 0.541, 28% under 0.35), turn 212 (0.455, 48%), flop 143 (0.376, 60%), river 114
  (0, 100%). Only the preflop bucket looks like variance; whether the flop, turn and river shoves lose chips cannot
  be judged from P0 (chipflow counts river shoves +6.69M net including the folds they win). Lost matches 811:
  final hand all-in as favourite 304, as underdog 507. Where the remaining losses come from is an open reading for
  B1's candidate, not settled here.
* Outcome verifier: every number, the 4,000-pair join, the seeds, the checkpoint provenance and both rule
  applications reproduced; one sentence ("mostly variance in big pots") was refuted against P0's own buckets and
  is replaced by the bullet above.
* Single run, one seed; a pure best response, so its cost on other opponents is unmeasured here (B1 trains on a
  mix and judges on held-out cells for that reason; C1 showed -4.0 on `tight_sticky` for a pure response).

### 14.32 G1 step 1: one archive model wins for names with history, not for unseen names (rule 2)

Pre-registered in roadmap "G1 step 1" (tier 2). One card-conditioned MLP over the archive with a causal profile
input (holdem-d2 2520b27, `tools/g1_run.sh` on gb10-d, 12 fits: 5 leave-name-out folds plus a time split, losses U
and W; rule in `~/poker-ai-lab-d2s2/logs/g1/rule.txt`). Loss chosen on the training folds' validation split: W
(validation R: W -0.06, U -0.34; both negative on that small split, dominated by a few names with heavy-tail misses; the pilot fit read train +0.45, test +0.33, validation median -0.21).
Bootstrap over names, 2,000 resamples, seed 47.

| test | metric (G1 minus baseline) | mean | 95% interval | rows / names | threshold | result |
|---|---|---|---|---|---|---|
| rule 1, unseen names (cold start) | R vs the λ range, nats per shown hand | -0.087 | [-0.243, +0.046] | 411,740 / 84 | at least +0.10, lower bound above 0 | fail |
| | P log loss vs X1 at big-pot decisions | +0.074 | [+0.032, +0.119] | 96,030 / 85 | upper bound under +0.02 | fail (worse) |
| rule 2, time split, names with 100+ earlier matches | R vs λ under per-name X1 | +0.183 | [+0.123, +0.266] | 70,418 / 29 | at least +0.10, lower bound above 0 | pass |
| | P log loss vs per-name X1 | -0.306 | [-0.438, -0.189] | 15,072 / 29 | upper bound under +0.02 | pass |

* **Verdict (rule 2):** G1 is a known-name model. It serves B0a and the lookahead for names with archive history;
  cold start (an unseen name) stays with X1 and the λ range; no more GPU on the unseen-name question.
* Reported: on unseen names G1 also loses to λ with its filled path (-0.125 [-0.409, +0.101]) and does not beat
  uniform clearly (+0.079 [-0.134, +0.288]); at final pots of 20 bb or more it is worse than λ (-0.230 [-0.448,
  -0.062]). By earlier-match group on held-out names, λ scores +0.14 to +0.18 everywhere while G1 is +0.06 to
  +0.12 cold and +0.02 to +0.19 filled, reaching λ only at 10 to 99 matches with the filled path. W minus U: R
  +0.161 [-0.004, +0.371] (not clearly different), P loss +0.125 [+0.084, +0.167] (W predicts actions worse). G1 over-predicts folds against every bet size
  bucket (for example 0.64 against an actual 0.54 at the largest bucket; X1 under-predicts, 0.48).
* By A0 class (unseen names, R vs λ): other -0.10 [-0.29, +0.04] (66 names), solver +0.20 [-0.08, +0.23] (11),
  tail +0.06 (3), big_bet -0.98 [-1.00, -0.84] (2), small_ball +0.32 (1), station -0.20 (1); single-name classes
  carry no interval.
* Outcome verifier: REFUTED the first record. Rule 2's rows had joined the opponents of the 100+ players (the
  baseline scores both seats), 7,881 R rows from 122 names with fewer than 100 earlier matches; only 30 archive names
  have 100 or more matches. Fixed in `g1_read.split_rows` (holdem-d2 3e988c8, test 9 with two plants caught), rule
  step rerun: R +0.183 [+0.123, +0.266], P -0.306 [-0.438, -0.189] on 29 names, equal to the verifier's own
  recomputation; the verdict holds. The first rule output is kept as `logs/g1/rule_v1_bug.txt`. Text fixes: the class
  line (other, tail, big_bet's interval) and the by-group range.
* Run note: base_fold0 crashed once on archive showdowns that reveal one hand (x3_range needs both); fixed in
  `g1_read.lam_scores` by replaying those hands without scoring them (holdem-d2 2520b27), about 0.1% of showdowns.
* What it means for the roadmap: the archive's regulars and the solver family all have history, so the names that
  decide titles are the ones G1 models well; an entrant's first matches against a new name still use X1.

### 14.33 T1's open question: the bp100-trained shoves are chip-positive; pure specialization costs 13 points elsewhere

Two tier-1 reads on data and seeds outside any rule.

**(a) Shove classes of T1's best response against bp100** (`logs/t1/flow_br.jsonl`, seed 81, 4,000 matches).
Chips from `tools/chipflow.py`'s own table (`logs/t1/flow_br.out`), re-derived by a second pass (the roadmap agent's
scratch script, which also gives points: the summed change in match-win probability per 4,000 matches under the
policy's own empirical P(win | stack) curve; one pass, approximate):

| street | shoves | called | equity when called | chips when bp100 folds | chips when called (expected) | chips total | points |
|---|---|---|---|---|---|---|---|
| preflop | 9,242 | 1,576 | 0.477 | +3.62M | +1.22M | +4.84M | +0.26 |
| flop | 6,346 | 1,568 | 0.352 | +5.22M | -0.65M | +4.56M | -0.36 |
| turn | 4,519 | 1,572 | 0.745 | +1.74M | +6.32M | +8.07M | +2.10 |
| river | 3,508 | 1,048 | 0.831 | +1.46M | +5.23M | +6.69M | +3.12 |

* Every street is chip-positive once the folds are counted; the called flop shoves lose 0.65M, mostly under 30 bb
  (about 1,000 called at equity 0.24), ordinary fold-equity play. In match value only the flop is about flat. The
  table shows the shoves pay against a no-chips baseline, not that they are the best action.
* So 14.31's P0 gap (+28.1) is not a leak: a policy that wins 80% by shoving into folds ends its losses in called
  shoves. P0 did its job once (it found the river call-off that training removed) and is retired as a decision
  statistic; this class table replaces it in candidate reads (B1's read reports it).
* fb2-900 on the same seeds: flop shoves +1.75M chips; river call-offs -2.46M, -4.11 points.

**(b) What pure specialization on bp100 costs elsewhere** (seed 98, new; 1,000 matches per cell, paired on (seed,
hero seat), holdem-x2r `rl.eval_arena`, cores 18-19; `~/poker-ai-lab-x2r/logs/t1x/`):

| cell | fb2-900 | T1 best response | paired diff | 95% interval |
|---|---|---|---|---|
| `tight_sticky` | 93.5% | 87.0% | -6.5 | [-9.0, -4.0] |
| `small_ball` | 76.3% | 59.7% | -16.6 | [-20.3, -12.9] |
| `sticky_overbettor` | 82.6% | 64.7% | -17.9 | [-21.3, -14.5] |
| `never_fold_pre` | 93.4% | 81.0% | -12.4 | [-15.0, -9.8] |
| pooled | | | -13.4 | [-14.9, -11.8] |

* Two hours against bp100 alone (+19.9 there) costs 6 to 18 points on every other style; C1's pure response cost
  -4.0 on `tight_sticky`. B1's population (bp100 a third of the SDK matches, the rest fb2's mix plus `small_ball`,
  the C-engine league about 38% of each update) and its guard cells are what this read says they must be; the B1
  read's risk is the guards, and its pre-registered fallback P1b halves bp100's share.

### 14.34 G1 step 2a: fine-tuning G1 gives the best per-name ranges at 100 and 1,000 matches, but the rule fails on one calibration bucket

Pre-registered in roadmap "G1 step 2a" (tier 2, one plan review). Three real bots with true cards (D2a's logs: fit
seed 61, held-out seed 62, 1,000 matches), four arms per bot and size; holdem-d2 branch g1-2a f3d1afd, outputs
`~/poker-ai-lab-d2s2/data/g1_2a/` (`rule.json`, `read_<bot>_<N>.json`, `records.json`). Base fit by the held-out
rule: Ashwing_v3 and AutodidactInnovations held out in fold 2 (`fit_fold2_W.pt`); Wolf is not in the archive
(`fit_fold0_W.pt`). Rows equal across arms (checked). R in nats per river hand (higher better), bootstrap over
held-out matches, 2,000, seed 47.

| bot | R at 1,000: (a) λ per-name X1 | (b) D2a from scratch | (c) G1 fine-tuned | (d) G1 + history | (c) minus (a) | (c) minus (b) |
|---|---|---|---|---|---|---|
| ashwing | +0.571 | +0.691 | +1.001 | +0.344 | +0.429 [+0.416, +0.443] | +0.310 [+0.291, +0.329] |
| autodidact_fast | +0.629 | +1.139 | +1.267 | +0.525 | +0.638 [+0.624, +0.654] | +0.128 [+0.103, +0.154] |
| wolf | +0.488 | +0.507 | +0.980 | +0.498 | +0.492 [+0.474, +0.510] | +0.473 [+0.444, +0.504] |

* At size 100 (reported only) (c) also leads: +0.879, +1.007, +0.760 against (a) +0.57, +0.61, +0.50. P (log loss
  at big-pot decisions) is lowest for (c) in every cell (for example ashwing 0.512 vs X1-based 0.721 at 1,000).
  Arm (d), G1 with the bot's history as input only, is no better than λ: the gain comes from fitting on the name.
* **Rule: FAIL.** The R condition passes for all three bots. The calibration condition (fold error 5 points or
  less, held-out, after the bias, every `size_bucket3` bucket with 200 or more spots) fails for autodidact_fast's
  largest bucket: 681 spots, actual 0.555, predicted 0.607, error 5.16 points (5.56 before the bias). Every other
  bucket is within 1.8 points except Wolf's largest (303 spots, actual 0.000, predicted 0.034, 3.4 points). Spots
  were defined by the builder as every bot decision facing a bet, preflop included (see the verifier's note below).
* **Outcome verifier: numbers CONFIRMED, verdict REFUTED as recorded.** Every R, P and calibration figure
  reproduced from the raw logs by a separate code path (rows identical across arms; 990 live combos per row as
  specified; the splits, base folds and no-true-cards rule hold). Two things the first record missed:
  1. The builder counted preflop spots, but `size_bucket3` is defined for postflop bets (its edges are "fold to a
     postflop bet", `match_stats` uses it postflop only). Under that reading the largest-bucket error is 7.07
     points for autodidact_fast (390 spots) and the fail is stable across three fine-tune seeds (6.90, 5.89, 6.72).
  2. Under the builder's reading the verdict sits inside rerun noise: CUDA EM is nondeterministic, and reruns of
     the same fine-tune gave 4.82 (pass), 1.77 (pass) and 5.66 (fail).
  A big-pot-rows reading with the bias refit on big-pot spots would pass (3.78), but that is not the spec's text.
  The verdict stands as **FAIL under the spec's postflop bucket definition**, now robust across seeds. Also: about
  100 river hands per bot are unscored (the bot only posted a blind all-in, no decision; R 0 for every arm).
* Per the pre-registered text, G1 stays an archive analysis tool and gets no more GPU. The range gain is large and
  consistent while fold calibration on big postflop bets is not; any follow-up is a new pre-registered slice.
* Builder's choices to note: the fold bias is a per-street fold-logit shift after the network, clamped to ±5; arm
  (c) fine-tunes with the unweighted likelihood (D2a's) from a W-trained base; arm (b) is scored through G1's scorer
  with zero weights on the profile columns; arm (a) lets only shown hands into the per-match state. GPU about 0.06
  hours; the whole run 0.41 hours.

### 14.35 B1's training stop at it 2290 was a guard false alarm (a logging artifact); the read is unaffected

B1 (roadmap B1, P1) was stopped at minute 262.7 of 360 by the entropy guard: logged row it 2290 had entropy 0.195
(guard 0.2) and policy loss 0.641. The policy had not collapsed:
* **Weights:** step sizes around the stop equal the steps before it. Policy weight distance it002000→it002100 1.662
  (relative 0.0279), it002100→it002200 1.673 (0.0280), it002200→latest (90 iterations) 1.611 (0.0269). Mean total
  variation of action probabilities on 18,365 fixed states (`data/maniac_labels.npz`): 0.0041, 0.0050, 0.0044.
  Entropy on that set: it002200 0.027, latest 0.027; all weights finite. Reproduced first-hand on gb10-d.
* **Cause:** `rl/train.py` (holdem-rl 114a136, lines 457-481) logs the pl, vl and entropy of the *last minibatch of
  the last epoch*, and keeps the tail minibatch. Iterations collect 16,122 to 16,690 samples against four full
  minibatches of 16,384, so whenever n is above 16,384 the logged row is a minibatch of 1 to 306 samples. That
  explains all fourteen |pl| > 0.15 spikes (random sign, gone the next row) and why the lowest logged entropies sit
  on spike rows. Those tiny tail minibatches also take a gradient step (bounded by clip 0.5 and lr 1.5e-4; no damage
  in the weight distances). The exact n at it 2290 is not logged.
* **Read unaffected:** the chosen checkpoint is it001200, written 1,090 iterations before the stop; the screen is
  flat from 300 to 2,100 (68.8 to 70.5) and the policy moved 0.005 mean TV between 1,200 and 2,200, so 2,400 and
  2,700 would not have changed selection. The stop record's "latest.npz is not good" is wrong; latest is a normal
  continuation (the file is left as is).
* **Population held:** SDK match shares bp100 0.333, heuristic 0.167, small_ball 0.167, each ext name 0.083 over
  241,027 matches; decision shares bp100 0.317, heuristic 0.141, small_ball 0.099. Pool on every row: a_ablA,
  b_distill1.
* **Next run (B1r or P1b), from Fable's review:** log batch means over the last epoch plus approx_kl and n; fold a
  tail minibatch under 2,048 samples; guard on batch-mean entropy under 0.2 for 3 consecutive rows (non-finite stays
  immediate). No change to clip, learning rate or KL stop. Budget 180 minutes with read set 300 to 1,500 plus
  latest (B1 gains nothing after 300); both need a dated amendment before launch.

### 14.36 B1 fails its rule: +5.4 on bp100 and +3.94 on the headline, but 3 to 5 points lost on four real-bot families

Pre-registered in roadmap "B1" (branch A, population P1; amendment 10:09 UTC 25 Nov). Training holdem-rl b1-rl a4d765d,
09:04 to 13:27 UTC, stopped at it 2290 by a guard false alarm (14.35). Screen seed 94 plus league pairs 400-499 on
it 300 to 2,100: every checkpoint passed the league filter (lowest 81.0 to 85.5%), scores 68.8 to 70.5 (flat);
chosen **it001200** (sha256 5e9c6fc6…; policy arrays as `rl/models/b1.npz` fc396112…, b1-rl 59b1ad3). Confirmation
seed 95, paired on (seed, hero seat) against fb2-900, holdem-x2r 8be6e38 (`~/poker-ai-lab-x2r/logs/b1/confirm/`,
`confirm_result.json`); fb2's non-container cells ran on cores 18-19 except `ext:wolf` (wall-clock bot), rerun
with the candidate's placement. Gate: league_fresh pairs 200-399 plus the heuristic head to head
(`~/poker-ai-lab-league/out/verify-rl-b1/`).

| cell | weight | n | paired gain | 95% interval |
|---|---|---|---|---|
| bp100 | 0.70 | 4,000 | +5.4 | [+3.8, +7.0] |
| tight_sticky | 0.10 | 2,000 | +0.1 | [-1.1, +1.3] |
| sticky_overbettor | 0.09 | 2,000 | +0.7 | [-0.7, +2.0] |
| small_ball_b | 0.08 | 2,000 | +2.5 | [+0.4, +4.5] |
| ext:autodidact | 0.03 | 1,000 | **-3.4** | [-6.2, -0.6] |
| small_ball (guard) | | 2,000 | +6.5 | [+4.6, +8.3] |
| never_fold_pre (guard) | | 2,000 | -0.8 | [-1.8, +0.3] |
| raise_station (guard) | | 2,000 | -0.6 | [-1.4, +0.2] |
| loose_passive (guard) | | 2,000 | -0.2 | [-1.5, +1.0] |
| ext:ashwing (guard) | | 1,000 | **-3.4** | [-6.1, -0.7] |
| ext:ashwing_hive (guard) | | 1,000 | **-4.6** | [-7.2, -2.0] |
| ext:ashwing_search (guard) | | 1,000 | **-3.7** | [-6.3, -1.1] |
| ext:wolf (guard) | | 1,000 | -1.7 | [-3.2, -0.2] |

* **Rule: FAIL.** Headline +3.94 [+2.79, +5.10] (passes); E1 holds (23 of 23 at 80% or more, lowest arch:2 83.8%,
  Wilson lower 79.8%); four cells under -2.0 with their upper bound under zero: the three Ashwing families and
  autodidact. Ashwing and autodidact use no wall clock (seeded RNG; autodidact's `time.time` only logs), so fb2's
  arm on cores 18-19 does not bias them.
* **The league, against fb2-900 on pairs 200-399 (n 400 each, point estimates):** the ten `bot:` clones pooled
  -1.62 [-2.65, -0.60] (Blueprint -4.0 [-8.0, +0.0], AutodidactInnovations -2.8, InfernalMonarch -2.8, mr_hide -2.2,
  Kimiko -2.0 [-3.95, -0.05], SolvencyCheck -2.0, DeepStack -1.8, MercuryRetrograde -1.0, PoetAndCoder +1.0,
  qwentom-leap +1.2; only Kimiko's own interval excludes zero); `base:` styles pooled +0.0; `arch:2` -3.25 [-7.4,
  +0.9], `arch:4` -1.75; the heuristic head to head 61.8% (Wilson lower 56.9%), -8.5 against fb2-900.
* **Reading (corrected after the outcome verifier):** the four failing cells are *not* outside B1's population.
  `ext:autodidact` is the same code as P1's `ext:autodidact_fast`, and the three Ashwing cells come from the same
  vendor package as P1's `ashwing_v2`, `ashwing_value`, `ashwing_adaptive` (`ext:ashwing_hive` is the same
  `hive_mind` strategy as `AshwingV2Bot`). P1 kept fb2's SDK entries but doubled the list to 12 to add four bp100
  and two `small_ball` entries, so every fb2 family's SDK share halved: the four `ext:` names from 4 of 6 to 4 of 12
  (each 0.083 of 241,027 matches), the heuristic from 2 of 6 to 2 of 12, and B1 lost on exactly those (-3.4 to -4.6
  on the Ashwing and autodidact cells, -8.5 against the heuristic). Two readings fit and this read cannot separate
  them: **dilution** (the old families got half the training and regressed) and **interference** (one set of
  weights cannot serve bp100 and the old families at once). Dilution points at the population mix (keep the old
  families' share while adding bp100); interference points at identity or representation. The pre-registered
  phrase "exploits the proxy, does not generalize" was for a headline fail with a bp100 pass; here the headline
  passes and only guards fail, so that label is not applied.
* **Small deviation:** the amendment's read set listed `latest.npz`; `read_set` drops it for a stopped run, and 14.35
  later showed latest was a normal continuation. Not screened; selection unaffected (the curve is flat).
* **Adaptation headroom (reported):** bp100 ceiling +19.9 minus +5.4 = **+14.5**; small_ball +21.9 minus +6.5 =
  **+15.4**. One mixed policy keeps about a quarter of each specialist's gain.
* **Decision shares (reported):** bp100 31.7% of SDK decisions against 33.3% of SDK matches; small_ball 9.9%
  against 16.7%.
* **Shove classes against bp100** (`tools/chipflow.py`, it001200, 4,000 matches, seed 95, 64.9% wins;
  `~/poker-ai-lab-rl/logs/b1/flow/`), beside T1's (14.33, seed 81):

| street | B1 shoves | bp100 folds | net chips (called at expected value) | T1 shoves | T1 net |
|---|---|---|---|---|---|
| preflop | 2,902 | 80% | +0.98M | 9,242 | +4.84M |
| flop | 4,170 | 67% | +2.82M | 6,346 | +4.56M |
| turn | 2,818 | 62% | +3.74M | 4,519 | +8.07M |
| river | 4,058 | 73% | +4.47M | 3,508 | +6.69M |

  B1 shoves less preflop than T1 and as often or more on the river; all four streets are chip-positive. River
  call-offs (all-in showdowns where bp100 made the last raise): 387, -1.31M expected.
* **Consequences:** no v5 from B1; v4 stays entered. P1b does not run (its trigger was no checkpoint passing the
  league screen; all seven passed). The next slice has to separate dilution from interference before it spends
  training on either (roadmap agent's call).
* **Outcome verifier:** every number, the pairing, arm comparability (fb2 at 6 workers and the candidate at 2
  reproduced the stored rows exactly for Ashwing and autodidact), checkpoint identity, gate, screen and chipflow
  CONFIRMED; the first reading REFUTED (the failing families are P1's own, at half fb2's share); corrected above.

### 14.37 AD1's tier-1 reads: the counts name the opponent slowly; bp100 is a coarse Blueprint stand-in (2026-11-25)

* **Setup:** fb2-900 (`rl/models/fb2_it000900.npz`) against 14 opponents, 200 matches each (100 pairs, both seats),
  seed 102 (registered `102 AD1 read`), 2,800 matches; bp100 through the bpopp queue (rc 0). Per match the hero's own
  live Tracker counts (no prior) after every finished hand, and the opponent's 8-axis style counters. Code: holdem-rl
  b1-rl `tools/ad1r_read.py` (4074c7f, b7fafeb, renamed db446d7; `distance` copied from holdem-x2r's
  `style_bots_check.py`). `small_ball_b` and `loose_passive` ran with holdem-x2r's `holdem/opponents.py` copied in
  (additions only). Rows: `~/poker-ai-lab-rl/logs/ad1r/` on gb10-d (`play/*.jsonl`, `report.txt`).
* **R1, identification curve:** features f46 to f51, f54, f55 (the eight Tracker rates; f44 and f45 are facts of the
  current hand, f52 is the hand count, f53 raise legality). Profile = pooled final counts of the other pairs (held out by
  pair); nearest by raw Euclid; n = matches that reached k hands. Chance at k = 0 is 1/14 = 0.071.

  | opponent | k 5 | k 10 | k 20 | k 40 (n) |
  |---|---|---|---|---|
  | bp100 | .56 | .69 | .73 | .83 (98) |
  | chipzen | .36 | .52 | .69 | .79 (77) |
  | `small_ball` | .28 | .33 | .52 | .84 (49) |
  | `small_ball_b` | .50 | .65 | .72 | .96 (28) |
  | `tight_sticky` | .35 | .58 | .76 | .92 (61) |
  | `sticky_overbettor` | .09 | .21 | .49 | .68 (19) |
  | `loose_passive` | .21 | .30 | .38 | .73 (22) |
  | `never_fold_pre` | .01 | .05 | .16 | .46 (13) |
  | `raise_station` | .52 | .87 | 1.00 | 1.00 (12) |
  | `ext:ashwing` | .00 | .06 | .17 | .28 (85) |
  | `ext:ashwing_hive` | .27 | .52 | .78 | .93 (116) |
  | `ext:ashwing_search` | .29 | .39 | .53 | .52 (92) |
  | `ext:autodidact` | .47 | .50 | .59 | .64 (92) |
  | `ext:wolf` | .42 | .50 | .63 | .83 (40) |
  | macro mean | .31 | .44 | .58 | .74 |

  Standardized Euclid gives .08, .18, .39, .61 (near-constant features blow up at small k). Median match lengths:
  `raise_station` 10 hands, `never_fold_pre` 13, `sticky_overbettor` 15, bp100 39, `ashwing_hive` 47; only 49% of
  bp100 matches and 39% of chipzen's reach 40 hands.
* **Confusions:** `ext:ashwing` and `ext:ashwing_search` share a profile (distance 0.018; two-class accuracy 0.46 to
  0.50 at every k: never separable by counts). `small_ball` and `small_ball_b` 0.224 (two-class 0.62 at k 5, 0.95 at
  k 40). bp100 and chipzen 0.247 (fifth closest pair; two-class 0.62, 0.70, 0.77, 0.89 at k 5, 10, 20, 40).
* **R2, bp100 beside the archive (A0 metric, 8 style axes, bound 0.25, 256 names; bp100 pooled 8,535 hands):**
  Blueprint 0.250, fermat6 0.255, NashForge 0.232, hoops 0.237, AutodidactInnovations 0.416, Ashwing_v3 0.601.
  Blueprint is not among bp100's ten nearest (lil-b3f 0.128 first). The gap is preflop: bp100 minus Blueprint pfr
  +0.22, fold to a preflop raise -0.08, the rest within 0.05. In tracker space (51 archive profiles at 20 hands)
  Blueprint 0.236 (rank 9), hoops 0.224, while Blueprint's own nearest names sit at 0.135 to 0.171. Among the 14
  simulated opponents `ext:autodidact` (0.227) is nearer Blueprint than bp100; chipzen is 0.411.
* **Hand-weighted (added after the outcome verifier):** for every hand h, the nearest profile from the counts after
  h - 1 hands (k 0 at chance): pooled over the 2,800 matches 53.0% of hands are played after the counts already
  name the right opponent (macro 50.0%). bp100 70.6% (only 22% of its hands are hands 1 to 10), `tight_sticky`
  70.9%, `ext:ashwing_hive` 74.9%, chipzen 63.9%, `ext:autodidact` 61.2%; `never_fold_pre` 11.8%, `ext:ashwing`
  16.1% (its errors are mostly `ext:ashwing_search`), `sticky_overbettor` 26.9%. Raw-Euclid nearest profile is a
  weak classifier, so these bound the counts' information from below (standardized Euclid names bp100 at 0.89 at
  k 5).
* **Reading (corrected after the outcome verifier):**
  1. Weighted by hands, the counts already name the opponent for about half of all hands and for 71% of bp100's.
     Identity is slow only for the short-match styles and the Ashwing pair. So B1 had the identity for most of its
     bp100 hands and still kept only +5.4 of the +19.9 specialist gain: missing identity explains at most part of
     the gap. Under AD1's own spec ("identity already clear by hand 5 to 10: AD1 still runs, fail branch 4 becomes
     the prior") the bp100 cell is borderline (raw .56 and .69 at hands 5 and 10, standardized .89 and .74), so AD1
     runs as specified with fail branch 4 (used but short, capacity) as the prior, not the reverse.
  2. The R1 launch condition (two opponents with different best responses on one profile) is not decided by this
     read for `ext:ashwing` and `ext:ashwing_search`: they share a profile (0.018, never separable), and whether
     their best responses differ was not tested (fb2-900 wins 155 and 162 of 200; B1's deltas -3.4 and -3.7 are
     consistent with one response, not a test of it). Both are judge-only guard cells, so a shared seed can only
     cost one of them, which AD1's guard reports; AD1 does not wait on it. bp100 and chipzen have distinct profiles
     (0.247, two-class 0.62 to 0.89), so the condition is not met for them.
  3. bp100 is in the solver cluster but at its edge (Blueprint at 0.250, the bound; 42 archive names nearer than
     Blueprint), and much more aggressive preflop (pfr +0.22). That fits B1's +5.4 on bp100 against -4.0 on the
     Blueprint clone without proving it. AD1's spec ties D2b's revisit to "bp100 far from arena Blueprint": at the
     bound, the condition is recorded as met in part; D2b (cloning the solver proxy) stays deferred, and a candidate
     slice after AD1 should weigh the solver class with a proxy nearer Blueprint or several solver proxies. The 0.70
     judge weight stands for AD1.
* **Outcome verifier:** every number, the hold-out, the features, the A0 distance copy, R2 and the opponents copy
  CONFIRMED; the first reading REFUTED (unweighted accuracy against match medians overstated how late identity
  arrives; the Ashwing condition was declared on an assumption; D2b's condition was not stated). Corrected above.
* **Limits:** profiles are fb2-900's view of each bot, archive profiles the whole field's; k-40 cells with n under 30
  are noisy; wolf is wall-clock (run at 4 workers with nothing else running); early-k accuracy depends on the metric.

### 14.38 D0: without bp100 and `small_ball` data the real-bot loss mostly stays; rule INCONCLUSIVE (2026-11-25)

Pre-registered in roadmap "D0" (research b640cfe). Training holdem-rl d0 60ff10d in `~/d0-run`, 15:53 to 19:03 UTC
(time stop at it 1,730), B1's command minus the bp100 and `small_ball` SDK entries, `--heur-batch 5750`. Void check
(`tools/d0_read.py void`, first to last row): C engine 6,069.9 decisions per iteration (target 6,070), old-family
SDK 5,926.5 (5,971, -0.7%), ext : heuristic 3.151 (3.15): **valid**. Read: it001200 only, seed 95, 1,000 matches per
cell from `~/d0-run/x2r` (holdem-x2r 8be6e38) on cores 0-17, 6 workers; rows `~/d0-run/logs/d0/read/it001200/`;
paired on (seed, hero seat) with the fb2-900 and B1 it001200 rows of 14.36 (`~/poker-ai-lab-x2r/logs/b1/confirm/fb2`,
`cand`). `ext:autodidact` took 3,641 s (B1's arm 3,392 s, fb2-900's 11,361 s; the bot is slow, not the box).

| cell | D0 vs fb2-900 | 95% interval | D0 vs B1 | 95% interval | B1 vs fb2-900 (14.36) |
|---|---|---|---|---|---|
| ext:ashwing | -3.3 | [-6.1, -0.5] | +0.1 | [-2.7, +2.9] | -3.4 |
| ext:ashwing_hive | -0.4 | [-2.7, +1.9] | **+4.2** | [+1.8, +6.6] | -4.6 |
| ext:ashwing_search | -3.9 | [-6.7, -1.1] | -0.2 | [-2.9, +2.5] | -3.7 |
| ext:autodidact | -3.2 | [-5.9, -0.5] | +0.2 | [-2.7, +3.1] | -3.4 |
| **pooled** | **-2.70** | [-4.02, -1.38] | **+1.07** | [-0.28, +2.43] | |

* **Rule: INCONCLUSIVE** (F's interval straddles -2.0 and B's straddles 0; the table gives no lever decision, and
  D-null runs only under MIX OR CONTINUATION).
* **Described, not decided:** the loss against fb2-900 is real without the new data (upper bound -1.38). On three of
  the four families D0 sits within 0.2 points of B1, so the bp100 and `small_ball` samples add nothing measurable
  to B1's loss there; on `ext:ashwing_hive` D0 recovers 4.2 of B1's 4.6 points, so the new data's harm, where it
  shows, is on that one family. Per family neither rule row is met (hive's F interval [-2.7, +1.9] is not above -2.0; the
  other three F upper bounds, -0.5 to -1.1, are not under -2.0), so this is a description, not a per-family verdict.
* **For AD0:** its "D0 beside it" line (NEW DATA with W1 passing) does not apply.
* **Outcome verifier:** void check, checkpoint (60 of 60 stored rows reproduced from it001200, 17 of 60 from
  it001100), eval tree (412 files of 8be6e38), pairing, every cell and pooled number, the B1 column and the rule
  CONFIRMED; REFUTED on one rounding (-0.8% for -0.7%), an understated fb2-900 timing, and a sentence that gave rule
  readings to single families. Corrected above.

### 14.39 AD0: one network distilled from the three teachers keeps both specialists' gains; rule 1 (2026-11-25)

Pre-registered in roadmap "AD0" (built and verified record research 7815d1b; amendment 2513a6f registered 21:58 UTC, before this read was
opened). Code holdem-rl ad0 8b7ea8b in `~/ad0-run/code`, holdem-x2r ad0-x2r 541bf81 in `~/ad0-run/code-x2r`.
* **Data** (seed 106, 20:15 to 21:52 UTC, cores 0-17, 6 workers): 9,000 teacher matches, 991,921 rows, 93,880 held
  out by pair. Overran the three-times time line (97 minutes against about 15): the estimate took rl.eval_arena
  rates, the logging path is Python `run_arena` with a hook and a second Tracker (7x to 30x slower). Recorded as a
  deviation in the amendment; the rows are valid.
* **Fit** (21:54 to 21:55, GPU): every student ran the 30-epoch cap with held-out loss still falling. The converged
  refit of amendment A1 (cap 300, patience 10, holdem-rl ad0 5b09abe, 21:59 to 22:02) is not played: A2 lets a
  30-epoch pass stand.

  | student | width, input | epochs (A1) | held-out loss 30 / A1 | held-out bp100 agreement 30 / A1 | hands 1-10 / 11+ (30) |
  |---|---|---|---|---|---|
  | W1 | 256, raw | 201 | 0.570 / 0.543 | 0.891 / 0.914 | 0.821 / 0.912 |
  | W1s | 256, seeded | 137 | 0.541 / 0.523 | 0.911 / 0.929 | 0.874 / 0.921 |
  | W2 | 512, raw | 147 | 0.559 / 0.536 | 0.900 / 0.921 | 0.840 / 0.918 |
  | W2s | 512, seeded | 159 | 0.531 / 0.514 | 0.918 / 0.941 | 0.888 / 0.927 |

* **Play 1** (seed 95, 21:56 to 22:31, cores 0-17, 6 workers; rows `~/ad0-run/play/STUDENT/CELL.jsonl`), gain in
  match-win points against fb2-900, paired on (seed, hero seat) with the 14.36 rows; ext = `ext:ashwing` and
  `ext:ashwing_hive` pooled. Pass: bp100 at least +10.0 with lower bound above +5.4, `small_ball` at least +11.0
  with lower bound above +6.5, ext lower bound above -2.0.

  | student | bp100 (2,000) | small_ball (2,000) | ext (2,000) | vs B1 it001200: bp100, small_ball | pass |
  |---|---|---|---|---|---|
  | W1 | +19.4 [+16.9, +21.8] | +19.8 [+17.8, +21.7] | +1.1 [-0.7, +2.9] | +13.8, +13.3 | **PASS** |
  | W1s | +19.6 [+17.0, +22.1] | +20.4 [+18.5, +22.4] | -0.9 [-2.8, +0.9] | +14.0, +14.0 | fail (ext) |
  | W2 | +17.0 [+14.5, +19.4] | +19.4 [+17.5, +21.3] | -1.1 [-3.0, +0.7] | +11.3, +13.0 | fail (ext) |
  | W2s | +19.7 [+17.1, +22.2] | +20.9 [+19.0, +22.9] | +0.1 [-1.7, +1.8] | +14.1, +14.5 | **PASS** |

* **Rule 1:** W1 passes. Neither identity nor capacity limits; B1's shortfall is the training method. Next: a
  candidate slice that distils the specialists into one network and fine-tunes it with PPO on P1 (full process).
  AD1 and S7 drop. D0's verdict (INCONCLUSIVE) adds no reading. Play 2 does not run (A2).
* **Described, not decided:** the plain 256-wide network, the deployed size, matches T1 on bp100 (+19.4 against
  T1's +19.9 at n 4,000) and C1 on `small_ball` (+19.8 against C1's +21.9), with no measurable loss on the two
  Ashwing cells. W1s and W2s sit within 0.3 of W1 on bp100 and W2 2.4 below it; no ext difference between
  students is outside its noise. The pass is a representability result, not a
  candidate: the students saw only four play cells, and the guard families beyond the two Ashwing cells are untested.
* **Outcome verifier: CONFIRMED.** An independent recompute (no import of the reader) reproduces every gain,
  interval and verdict: row counts, unique (seed, hero seat) keys, seed ranges, bp100 paired on k < 1,000, the ext
  pooling. W1's ext cells alone: `ext:ashwing` +2.2, `ext:ashwing_hive` 0.0. Seed-clustered errors give the same
  verdicts (ext lower bounds W1 -0.72, W2s -1.75, W1s -2.84, W2 -3.04). Provenance: 40 `small_ball` matches per
  student re-run match the recorded rows 40 of 40 with the recorded profile setting and 1 to 9 of 40 with the other,
  so the rows come from these student files, seeded students with the pinned prior and unseeded without it. It
  caught one date slip (these entries said 2026-11-26; the UTC date is 2026-11-25), corrected.

### 14.40 C0: fb2-900 is a peak on the Ashwing families; rule PEAK (2026-11-25)

Pre-registered in roadmap "C0" (research a5fd3ed; amendment e57f2d0 before the read: D-null does not run under any
outcome). Arms from fb2's own run (`~/poker-ai-lab-rl/ckpt/fb2/`), 1,000 matches per cell on seed 95 from
`~/d0-run/x2r` (holdem-x2r 8be6e38), 2 workers on cores 18-19, 20:23 to 22:49 UTC; paired on (seed, hero seat) with
the fb2-900 rows of 14.36; reader holdem-rl d0 6c3f594 `tools/c0_read.py`. Gain in match-win points against fb2-900.

| arm | ext:ashwing | ext:ashwing_hive | ext:ashwing_search | pooled | 95% interval |
|---|---|---|---|---|---|
| fb2 it000700 | -1.4 | -4.8 | -2.5 | **-2.90** | [-4.43, -1.37] |
| fb2 it000800 | -2.9 | -2.2 | -3.4 | **-2.83** | [-4.35, -1.31] |
| fb2 latest (it 965) | +0.6 | -3.3 | -0.2 | -0.97 | [-2.48, +0.54] |
| D0 it000300 (reported) | -4.9 | -3.9 | -5.1 | -4.63 | [-6.21, -3.05] |
| D0 it001600 (reported) | -1.2 | -1.8 | -2.2 | -1.73 | [-3.25, -0.22] |

Cell standard errors 1.16 to 1.45.
* **Rule: PEAK** (two of the three fb2 pooled points under -2.0 with upper bounds under zero). fb2-900 is a local
  high on these families: its own neighbours 100 and 200 iterations earlier lose about 2.9 points, as B1 (-3.4 to
  -4.6 per family) and D0 (-2.70 pooled on four cells) did. Their guard losses are recorded as within the run's own
  checkpoint spread. P1b and any "restore the shares" slice close; D-null does not run (amendment). Every future
  PPO screen includes the three Ashwing cells and `ext:autodidact_fast` at 500 each, and selection is among
  checkpoints that hold them.
* **Described, not decided:** the -2.0 guard against fb2-900 on these cells measures distance from a peak, not from
  a typical checkpoint. AD0's students (14.39), fitted to fb2-900's labels on Ashwing-family data, hold that peak
  (W1 +1.1 [-0.7, +2.9] on two of these cells), which supports distillation over PPO for keeping it.
* **Outcome verifier: CONFIRMED.** Independent recompute (no reader import) of every cell and pooled number; keys
  identical to the baseline, 1,000 rows each, seed-clustered errors within 0.06 of the reader's; checkpoint sha256
  prefixes match the spec and the driver's paths; the run tree's code equals the baseline tree; 20 matches each of
  two C0 arms and of the fb2-900 baseline re-run byte-identical.

### 14.41 TT, T-b: a 60-minute teacher clears +8.0 only against `chipzen` (2026-11-26)

Pre-registered in roadmap "TT" (T-b part; line +8.0 on the 95% lower bound). Four `tools/rl_br.sh` runs of 60 minutes
from fb2-900 with its value head (`ckpt/fb2/it000900.npz`), 3 SDK workers and 4 cores each, 23:03 to 00:03 UTC
(2026-11-25 to 26; the first start at 23:01 failed on the policy-only init, KeyError 'vw0', and was moved aside before
any training). Reads 00:03 to 00:11 UTC, seed 109 (fresh), 2,000 matches per arm and cell, from `~/d0-run/x2r` (holdem-x2r 8be6e38) on
cores 0-17; runner and reader holdem-rl tt 3682d23 `tools/tt_run.sh`, `tools/tt_read.py`. Gain = teacher minus
fb2-900, paired on (seed, hero seat), in match-win points.

| teacher (sha256 prefix, last it) | cell | fb2-900 | teacher | gain | 95% interval | verdict |
|---|---|---|---|---|---|---|
| br_sticky_overbettor (2a4fe259a591, 2205) | sticky_overbettor | 84.3% | 88.8% | +4.5 | [+2.7, +6.3] | no |
| br_loose_passive (ac2389b0e073, 2755) | loose_passive | 92.0% | 96.6% | +4.6 | [+3.3, +5.9] | no |
| br_never_fold_pre (1f4d70e65b49, 2515) | never_fold_pre | 94.05% | 98.65% | +4.6 | [+3.5, +5.7] | no |
| br_chipzen (666a436345eb, 400) | chipzen | 67.5% | 79.25% | **+11.8** | [+9.4, +14.1] | **joins V5b** |

* **Rule:** `br_chipzen` joins V5b's teacher set; the other three do not. Each of the three gains about 4.6 points
  where fb2-900 already wins 84 to 94%, so their room is under 16 points and an hour buys about a third of it.
* **Described, not decided:** `chipzen` ran 400 iterations in the hour against about 2,200 to 2,750 for the others
  (its opponent is slower per hand), so its teacher is the least trained and still the largest gain: fb2-900 is
  furthest from its ceiling there (67.5%).
* **The `chipzen` cell does not repeat run to run:** `rl/eval_arena.py` `make_chipzen()` builds `HoldemBot(seed=None)`
  with no `set_seed`, so the opponent's own randomness is unseeded (two fresh 20-match fb2 runs agreed on 4 rows). Its
  rows pair on cards and hero seed only; the paired se stays valid but looser, and even the unpaired lower bound
  (+9.03) clears +8.0. Any later judge that reads `chipzen` exactly needs that opponent seeded first.
* **Outcome verifier: CONFIRMED.** Independent recompute (no reader import), paired on (seed, hero seat) with n-1
  variance: every gain, se and interval matches; 8 files of 2,000 rows, seeds 10900000 to 10900999, key sets equal
  between arms; read commands, checkpoint sha256 prefixes, iteration counts, training init, cores and times match
  the logs; the box runner and reader equal tt 3682d23 byte for byte; a 20-match rerun of the sticky_overbettor
  teacher matched all 20 rows.
* T-a (the M1 specialists on the Ashwing cells and `ext:autodidact`, seed 95) is still reading on cores 18-19.

### 14.42 V5a: both distilled students fail the league screen on the aggressive heuristics; chosen none (2026-11-26)

Pre-registered in roadmap "V5a" (judge W1 with no PPO; B1's screen and 78.0% league filter). Runner holdem-x2r `v5a`
de7c4f7 `tools/v5a_judge.sh` from `~/v5a-run/code`, arena cells from `~/d0-run/x2r` on cores 0-17, 00:12 to 00:19 UTC.
Candidates `w1` (30 epochs, 9bc31660…) and `w1_a1` (converged refit, 3c375498…), both sha256-checked. Screen seed 94;
league `league_fresh.py` pairs 400-499 (4,600 matches each, 0 illegal, 0 exceptions).

| candidate | screen score | bp100 | tight_sticky | sticky_overbettor | small_ball_b | never_fold_pre | loose_passive | league lowest |
|---|---|---|---|---|---|---|---|---|
| w1 | 77.33 | 77.8 | 92.0 | 56.2 | 78.6 | 93.8 | 92.4 | **64.5** (base:lag) |
| w1_a1 | 77.09 | 76.7 | 91.2 | 60.4 | 81.6 | 91.6 | 92.4 | **74.5** (base:lag) |

League opponents under 80%: w1 base:lag 64.5, base:maniac 70.0, arch:2 76.0, base:random 78.5, arch:5 79.0 (18 of 23
at 80% or more); w1_a1 base:lag 74.5, base:maniac 77.5 (21 of 23). For comparison, B1's seven PPO checkpoints on the
same pairs all held 81% or more (lowest 81.0 to 85.5), and fb2-900 on pairs 200-399 (`out/verify-fb2-900`) plays
base:lag 94.3, base:maniac 87.3, arch:2 87.0, base:random 86.3, arch:5 84.8.

* **Rule:** neither candidate passes the 78.0% filter, so `choose` writes chosen none and V5a ends with this
  finding (confirm exited 5 before any cell; nothing was confirmed, gated or carded). The fail goes to the roadmap
  agent.
* **Described, not decided:** the students lose most where fb2-900 is strongest and where AD0's data never went.
  AD0's data (roadmap AD0) played only bp100, `small_ball`, `chipzen`, three Ashwing-family bots and `ext:autodidact_fast`; it holds no
  hyper-aggressive heuristic (`lag`, `maniac`) and no `arch:` opponent. Against base:lag W1 drops 30 points from
  its teacher. The converged refit (A1) recovers 10 of them, so part is fit quality and part is coverage. Not
  tested: whether adding those opponents to the data closes the gap.
* Fit-seed spread (reported only) launched after the screen on cores 0-17, 00:25 UTC.
* **Outcome verifier: CONFIRMED.** Screen cells and scores recomputed from the rows with B1's weights (77.33, 77.09);
  league rates recomputed from `results.jsonl` (23 opponents, 4,600 unique rows, pairs 400-499) match the summaries;
  confirm died with exit 5 before any cell (no `confirm/` rows); candidate and fb2 sha256 match the pins; the box
  runner equals de7c4f7; 40 matches per candidate on two cells replayed byte-identical from `~/d0-run/x2r`; B1's
  lowest rates 81.0 to 85.5 and fb2-900's comparison rates confirmed; `~/ad0-run/data.npz` holds exactly the seven
  opponents named above.
* **Next (roadmap agent):** V5b, specialists plus fb2-900 coverage data with held-out cells (roadmap "V5b").

### 14.43 V5a fit-seed spread: the fit seed alone moves the pooled Ashwing gain by 4 points (2026-11-26; reported only)

Pre-registered in roadmap "V5a" (reported only; `95 V5A read`). W1's 30-epoch fit on AD0's data with fit seeds 2
(289f6d47…) and 3 (f64f8ce0…) besides seed 1 (14.39's W1, 9bc31660…); each played seed 95 from `~/d0-run/x2r`
(holdem-x2r v5a fee9b27 `tools/v5a_spread.sh`; bp100 through the queue), cores 0-17, 00:25 to 00:43 UTC. Paired on
(seed, hero seat) against B1's fb2-900 rows on disk (`logs/b1/confirm/fb2`; bp100 on its first 2,000 keys, which
are seed 1's keys).

| fit seed | bp100 (2,000) | ext:ashwing (1,000) | ext:ashwing_hive (1,000) | Ashwing pooled |
|---|---|---|---|---|
| 1 (14.39) | +19.4 [+16.9, +21.8] | +2.2 [-0.6, +5.0] | +0.0 [-2.3, +2.3] | +1.1 [-0.7, +2.9] |
| 2 | +18.2 [+15.7, +20.7] | -0.7 [-3.4, +2.0] | -0.4 [-2.8, +2.0] | -0.6 [-2.4, +1.3] |
| 3 | +16.3 [+13.8, +18.8] | -2.3 [-5.1, +0.5] | -3.6 [-6.2, -1.0] | **-3.0 [-4.9, -1.0]** |

* **Reported, not decided:** the same data, network and epochs give pooled Ashwing gains from +1.1 to -3.0 by fit
  seed alone; seed 3 would fail V5a's pooled Ashwing bound (-2.0 with the upper bound under zero). bp100 holds
  (+16.3 to +19.4). A student's Ashwing number is about as much fit noise as the guard's width, so a single fit is
  a draw, not the method's value; how V5b chooses among students is for the roadmap agent.
* Check: the same reader on seed 1's rows reproduces 14.39's verified numbers exactly (bp100 +19.4 [+16.9, +21.8],
  pooled +1.1 [-0.7, +2.9]); every arm pairs on all its keys (no missing pair).

### 14.44 Averaging the three W1 fits lands at their mean, not above it (2026-11-26; V5b amendment 1 item 8, reported only)

The three AD0 W1 fits of 14.43 (fit seeds 1, 2, 3) averaged as one policy (mean of the members' masked action
probabilities, one draw by `Policy.act`'s rule; file `w1_ens.npz` bf9d8d42…, member hashes pinned), played seed 95
from `~/d0-run/x2r-v5b` (holdem-x2r v5b-root e4808d6; runner v5b 952d9cd `ad0-ens-build`, `ad0-ens-play`), cores
0-17, 01:10 to 01:19 UTC, registered `95 V5A read`; paired against B1's fb2-900 rows on disk.

| cell | ensemble | members (fit seeds 1, 2, 3) |
|---|---|---|
| bp100 (2,000) | +17.8 [+15.3, +20.3] | +19.4, +18.2, +16.3 (mean +18.0) |
| ext:ashwing (1,000) | -0.6 [-3.3, +2.1] | +2.2, -0.7, -2.3 |
| ext:ashwing_hive (1,000) | -1.7 [-4.2, +0.8] | +0.0, -0.4, -3.6 |
| Ashwing pooled | -1.2 [-3.0, +0.7] | +1.1, -0.6, -3.0 (mean -0.8) |

* **Reading (pre-registered in item 8):** neither cell is clearly under the members' mean (upper bounds above it),
  so nothing returns to the roadmap agent and V5b's fit proceeds as amended. Averaging gives one policy at about the
  members' mean: it removes the luck of a single draw, it does not add strength.
* Check: an independent reader (my own pairing script, no import of `v5b_read.py`) gives the same three gains and
  intervals; every row pairs (no missing key).

### 14.45 TT, T-a: the M1 specialists clear +8.0 on three of four cells; not used by V5b (2026-11-26)

Pre-registered in roadmap "TT" (T-a part, line +8.0 on the 95% lower bound). The M1 specialists of 14.12 on disk,
`~/poker-ai-lab-rl/ckpt/br_ashwing/latest.npz` (b247feb2e7c1…) and `br_autofast/latest.npz` (08575045b559…), 1,000
matches per cell on seed 95 from `~/d0-run/x2r`, 2 workers on cores 18-19, 2026-11-25 23:01 to 2026-11-26 02:39 UTC
(`ext:autodidact` alone 10,977 s); paired on (seed, hero seat) with B1's fb2-900 rows on disk; reader holdem-rl tt
3682d23 `tools/tt_read.py --part a` (rc 0).

| teacher | cell | gain | 95% interval | verdict |
|---|---|---|---|---|
| br_ashwing | ext:ashwing | +16.0 | [+13.1, +18.9] | over the line |
| br_ashwing | ext:ashwing_search | +15.4 | [+12.6, +18.2] | over the line |
| br_ashwing | ext:ashwing_hive | +8.2 | [+5.7, +10.7] | no |
| br_autofast | ext:autodidact | +13.4 | [+10.7, +16.1] | over the line |

* **Rule as amended by V5b:** the line is met on three cells, but V5b does not use T-a's teachers: every T-a cell is
  one of V5b's held-out D4 cells (roadmap V5b, Teachers; decided before this read). The teachers stay on disk for a
  later slice; that choice is the roadmap agent's.
* **Described, not decided:** the Ashwing specialist gains about 16 points on two Ashwing profiles where fb2-900
  holds roughly level (14.40), so the room on those families is large; on `ext:ashwing_hive` it gains half that.
* **Run note:** `tools/tt_run.sh` was replaced on the box at 23:03 (the 3682d23 training fix) while mode `a` ran
  from 23:01. Bash had parsed the whole `case` before running it, so all four cells ran the original code to the
  full count (1,000 rows each); reading the changed file after `esac` gave a syntax error and `a.rc` 2. The read
  (`read_a.rc` 0) is unaffected. Lesson: never replace a script a running bash is executing.
* Check: an independent pairing script (no reader import) gives the same four gains and intervals; every file has
  1,000 rows on seed 95, all paired with the baseline; the run log names each teacher's `latest.npz`.

### 14.46 V5b: DEFAULT FAIL on sticky_overbettor; bp100 holds +15.5 with coverage (2026-11-26)

Pre-registered in roadmap "### V5b" (revision 2 plus Amendment 1). Driver `tools/v5b_drive.sh` (holdem-x2r v5b bedc22e)
on gb10-d, 2026-11-26 02:10 to 06:39 UTC, every step rc 0: vectors 50 min, draw 5, D1+D2 data 57, D3 9, fit 8
(1,874,255 rows), judge 2 h 20. Seeds 3, 94, 95, 108, 110 and 111 registered V5B read.

* **Choice:** screen scores e256 76.98, e512 77.24 (difference under the 0.5-point margin), both through the 78.0%
  league filter (e256 lowest arch:5 79.5%, 22 of 23 at 80%; e512 lowest bot:Blueprint 80.0%, 23 of 23): **e256**.
* **Confirm, seed 95, paired against fb2-900 on (seed, hero seat):**

| cell | weight | n | gain | 95% interval |
|---|---|---|---|---|
| bp100 | 0.70 | 4000 | +15.5 | [+13.7, +17.2] |
| tight_sticky (D4) | 0.10 | 2000 | +0.0 | [-1.2, +1.2] |
| sticky_overbettor (D4) | 0.09 | 2000 | **-4.2** | **[-6.1, -2.4]** |
| small_ball_b (D4) | 0.08 | 2000 | +2.1 | [-0.1, +4.2] |
| ext:autodidact (D4) | 0.03 | 1000 | -1.5 | [-4.3, +1.3] |
| small_ball | 0 | 2000 | +7.3 | [+5.3, +9.4] |
| never_fold_pre (D4) | 0 | 2000 | -0.9 | [-2.1, +0.3] |
| raise_station (D4) | 0 | 2000 | +0.8 | [+0.0, +1.6] |
| loose_passive (D4) | 0 | 2000 | +0.1 | [-1.2, +1.4] |
| ext:ashwing (D4) | 0 | 1000 | -1.9 | [-4.7, +0.9] |
| ext:ashwing_search (D4) | 0 | 1000 | -2.6 | [-5.3, +0.1] |
| ext:ashwing_hive (D4) | 0 | 1000 | -1.1 | [-3.5, +1.3] |
| ext:wolf (D4) | 0 | 1000 | -0.4 | [-1.8, +1.0] |

* Headline +10.57 [+9.33, +11.81]. Guard: one failure, the D4 cell sticky_overbettor (gain under -2.0 with the
  upper bound under 0). **Verdict: branch 2, DEFAULT FAIL.** The E1 gate was not run (not needed past branch 2).
* **Fresh seed 108 (reported, past the deciding branch):** bp100 +13.8 [+11.4, +16.2] holds, pooled Ashwing holds
  (ashwing +0.6, hive +0.8), small_ball +7.4 [+5.5, +9.4] does not hold (lower bound under +6.5), so branch 4
  would also have failed.
* **J3:** no D4 cell under -5.0 (lowest sticky_overbettor -4.2). **Price of coverage:** bp100 lower bound +13.7
  over its +10.0 line; small_ball +5.3 under its +11.0 line (recorded).
* **Members (item 6, seed 95):** ensemble bp100 +16.4, pooled Ashwing -1.5; members +16.8/+16.6/+16.9 and
  -1.1/-1.9/-1.1. The ensemble sits inside the members' spread; averaging did not add gain here.
* **Chipzen (step 0, reported only):** +4.0 [+0.6, +7.4].
* **Described, not decided:** coverage kept bp100 near AD0's level (+15.5 vs the AD0 ensemble's +17.8, 14.44) and moved every held-out
  real-bot cell to within about 3 points of level, none clearly up; the one clear loss is the held-out rule bot
  sticky_overbettor. small_ball gains +7.3, under its price line.
* **Outcome verifier CONFIRMED:** own pairing script, no repo reader. Same gains, headline and single guard failure, and complete pairing on seeds 95 and 108. The box code equals v5b bedc22e. The e256 and e512 pins match. A 40-match replay reproduces the confirm and fresh rows from e256 (40 of 40; e512 15 and 11 of 40). The data's 90 opponent names hold no D4 cell, and the chipzen rows are all new (src 2).

### 14.47 G0: GUARD FAIL on sticky_overbettor; the gate lifts small_ball to +16.1 but misreads an unseen bot (2026-11-26)

Pre-registered in roadmap "### G0" (3fd709c, post-G0 note f6227ed). Driver `tools/g0_drive.sh` (holdem-x2r `g0` 44759f4,
holdem-rl `g0-rl` bad56dd, root `g0-root` 0e3b521) on gb10-d, 2026-11-26 08:32 to 10:51 UTC, every step rc 0: rows 14
min, classifier 2, chipzen line 6, screens 8, confirm 82, departure 26. Seeds 94, 95, 112 and 113 registered G0 read.

* **Classifier:** 141 epochs, held-out loss 0.2890, held-out accuracy 89.4% (206,403 rows held out by pair). By hand
  bucket: 1-10 80.6% (bp100 43.7%, small_ball 60.0%, chipzen 18.6%), 11-20 88.7%, 21-40 94.1%, 40+ 97.7% (chipzen
  85.3%). Calibration error per class 0.003 to 0.006.
* **Misfire table (14.37 logs, seed 102):** share of hands off the default. G80: bp100 56.4%, small_ball 35.0%,
  chipzen 25.6%, sticky_overbettor 4.1%, every other bot 3.6% or less. G50: bp100 71.4%, small_ball 56.3%, chipzen
  49.2%, sticky_overbettor 24.4% (22.2% to the small_ball expert), small_ball_b 14.3%, the rest 6.5% or less.
* **Chipzen line (2b):** `br_chipzen` against the seeded `chipzen`, 2,000 on seed 95: +10.2 [+7.9, +12.5]; line +5.10.
* **Choice:** screen scores G80 0.7326, G50 0.7597, both through the 78.0% filter (lowest arch:5 83.0% and 81.5%, 23 of
  23 at 80%): **G50**. The screen already showed the cost: sticky_overbettor G80 80.8%, G50 75.4%.
* **Read, G50, seed 95, paired against fb2-900 on (seed, hero seat):**

| cell | weight | n | gain | 95% interval |
|---|---|---|---|---|
| bp100 | 0.70 | 4000 | +15.2 | [+13.7, +16.8] |
| tight_sticky (D4) | 0.10 | 2000 | -0.1 | [-0.4, +0.1] |
| sticky_overbettor (D4) | 0.09 | 2000 | **-5.9** | **[-7.2, -4.6]** |
| small_ball_b (D4) | 0.08 | 2000 | +1.4 | [+0.1, +2.7] |
| ext:autodidact (D4) | 0.03 | 1000 | +0.2 | [-0.9, +1.3] |
| small_ball | 0 | 2000 | **+16.1** | [+14.2, +17.9] |
| chipzen | 0 | 2000 | +2.6 | [+0.6, +4.7] |
| never_fold_pre (D4) | 0 | 2000 | -0.1 | [-0.7, +0.4] |
| raise_station (D4) | 0 | 2000 | -0.2 | [-0.5, +0.1] |
| loose_passive (D4) | 0 | 2000 | -0.2 | [-0.6, +0.2] |
| ext:ashwing (D4) | 0 | 1000 | -0.6 | [-2.0, +0.8] |
| ext:ashwing_search (D4) | 0 | 1000 | -1.0 | [-2.4, +0.4] |
| ext:ashwing_hive (D4) | 0 | 1000 | -0.4 | [-1.0, +0.2] |
| ext:wolf (D4) | 0 | 1000 | +0.0 | [-0.5, +0.5] |

* Headline +10.23 [+9.13, +11.33]. Guard: one failure, sticky_overbettor. Fresh seed 113, sticky_overbettor 2,000:
  -6.4 [-7.8, -5.0] (G50 74.4% wins, fb2-900 80.8%), so the fresh check fails too. **Verdict: branch 2, GUARD FAIL**;
  the misfire rate on that bot is 24.4% (over 10%), so the rule names the classifier. Also short: chipzen +2.6 under
  its +5.10 line. bp100 and small_ball clear theirs (+13.7 over +10.0, +14.2 over +11.0).
* **Departure by hand bucket (200 matches each, G50):** sticky_overbettor leaves the default on 5.6% of decisions in
  hands 1-10, 32.0% in 11-20, 61.6% in 21-40 and 92.4% past 40 (79.1% to the small_ball expert there): the classifier
  grows more certain of the wrong class as the match goes on. small_ball 10.9%, 53.6%, 92.0%, 98.9%; bp100 16.7%, 72.4%,
  90.8%, 99.1%; chipzen 12.6%, 50.9%, 77.6%, 91.3% with 9.9% of all decisions to the bp100 expert.
* **Decision time:** G50 mean 0.029 ms, p95 0.033 ms, max 0.158 ms per move; fb2-900 0.013 ms.
* **Described, not decided:** on the opponents it was trained to name, the gate does what pooling could not: small_ball
  +16.1 against V5b's +7.3 (14.46) and bp100 level with V5b, and every other held-out cell sits within 1 point of level,
  closer than V5b's. The failure is open-set: sticky_overbettor is in no class's rows, its features sit nearest
  small_ball's, and a closed four-way softmax has no way to say "none of these", so the posterior climbs with evidence
  toward the wrong expert. The arm with the higher threshold left that bot alone (4.1%) but lost on the screen score.
* **Outcome verifier: CONFIRMED** (fresh context, own script from the raw jsonl, no read module imported): every cell,
  the headline, the chipzen line, the fresh cell, the choice (difference 0.027 over the 0.005 margin), the pins
  (G50 8b1a4cc0..., clf d068ea0d..., all four teachers) and the registry lines (94, 95, 112, 113 only) as stated.

### 14.48 G80 read post hoc (G0b prerequisite P0): guards hold, gains just short; its own play drifts too (2026-11-26)

A measurement, not a verdict (G80 lost G0's choice, 14.47). `tools/g0_posthoc_g80.sh` (holdem-x2r `g0` 77f0c00), run on
gb10-d 10:59 to 12:23 UTC from `~/d0-run/x2r-g0`, file `~/g0-run/students/g80.npz` verified against its pins; same
seeds, counts and fb2-900 arms as G0's read; rows `~/poker-ai-lab-x2r/logs/g0/posthoc_g80`. Numbers from my own
recompute of the raw rows (paired on (seed, hero seat), n-1 variance, the 14.47 verifier's method).

| cell | n | gain | 95% interval |
|---|---|---|---|
| bp100 | 4000 | +11.4 | [+9.9, +12.8] |
| small_ball | 2000 | +11.1 | [+9.4, +12.8] |
| chipzen | 2000 | +1.4 | [-0.1, +2.8] |
| sticky_overbettor (D4) | 2000 | -0.4 | [-1.0, +0.2] |
| small_ball_b (D4) | 2000 | +0.1 | [-0.8, +0.9] |
| other D4 cells | 1000-2000 | -0.7 to +0.1 | lowest lower bound -1.5 (ext:ashwing) |
| fresh sticky_overbettor, seed 113 | 2000 | -1.4 | [-2.0, -0.8] |

* Headline +7.93 [+6.91, +8.96]. No D4 guard failure; the fresh lower bound -1.985 is just above -2.0. Under G0's
  rule G80 would read GAINS SHORT: bp100 +9.9 and `small_ball` +9.4 lower bounds under +10.0 and +11.0; `chipzen`
  under its +5.10 line.
* **Departure in its own play (200 matches, seed 95), share of decisions off the default by hand bucket:**
  `sticky_overbettor` 0.3%, 4.3%, 14.4%, 43.7% (all to the `small_ball` expert; G0's misfire table on fb2-900's logs
  gave 4.1% overall); `small_ball` 1.4%, 27.2%, 70.6%, 90.2%; `chipzen` 1.2%, 17.0%, 36.7%, 53.4%; `small_ball_b`
  0%, 2.1%, 10.4%, 4.3%.
* **Described, not decided:** the higher threshold trades identification speed for safety: it gives up about 4 to 5
  points on bp100 and `small_ball` against G50 (14.47) and holds the guard. The drift of 14.47 is present at t = 0.80
  as well (4% offline, 44% past hand 40 in its own play): the gate's own expert moves the counts it reads. G0b reads
  every gate figure on rows from both actors for this reason. G80 is the reference arm of G0b's steps 19 and 20.

### 14.49 G0b steps A to C: the size terms separate the open set; S1 and S2 PASS (2026-11-26)

Run on gb10-d 12:48 to 14:36 UTC from holdem-rl `g0b-rl` (4a4a5f1, stopped twice and resumed at b9031b1 and e87a5f5;
roadmap G0b build record), `~/g0b-run`: 13,600 fitting matches (6,824 fit, 3,352 cal, 3,424 test by match label) and
2,200 evaluation matches per actor (fb2-900 and G50), seed 114. Gate GS fitted on the fit pairs: T 0.5, the size
ablation's T 0.6. Output `~/g0b-run/stepc.json`, table `~/g0b-run/logs/stepc.out`. Offline only: nothing here plays.

**S1 PASS** (`sticky_overbettor`, G50-actor rows, share of hands routed to any expert by hand bucket 1-10, 11-20,
21-40, over 40; line at most 10% in every bucket):

| arm | 1-10 | 11-20 | 21-40 | over 40 |
|---|---|---|---|---|
| GS50 | 4.8% | 3.7% | 0.1% | 0.0% |
| GS80 | 0.0% | 0.0% | 0.0% | 0.0% |
| GS50 without the size terms | 11.4% | 41.7% | 34.9% | 10.2% |
| G80 (reference, same rows) | 0.2% | 4.7% | 26.7% | 65.3% |

**S2 PASS** (true bp100 and `small_ball`, test pairs, hands 11 and later, share routed to the cell's own expert by
GS80, line at least 0.8 of G80's share): bp100 93.2 to 97.3% (G80 37.0 to 93.4%); `small_ball` 91.2 to 100% (G80
27.6 to 92.9%). The closest cell is `small_ball`, G50 actor, over 40: GS80 91.9% against a need of 74.3%.

* **What carries it:** the six size terms. Without them the gate sends `sticky_overbettor` and `small_ball_b` to the
  `small_ball` expert on up to 49.4% and 33.8% of hands (as G0 did, 14.47); with them both are routed anywhere on at
  most 4.9% of hands under GS50 and 0% under GS80. The support test changes almost nothing at these thresholds (every `nosupport` column within
  0.53 points of the full gate): it is inert here, not harmful.
* **Item 15 (reported, no stop):** four misses, all GS50 in hands 1 to 10, all to the bp100 expert:
  `ext:ashwing_hive` 17.7% (fb2 actor) and 19.0% (G50), `ext:autodidact` 12.4% and 12.3%. GS80 routes them 3.4%
  and 2.9%. Every other D4 cell is at most 8.4% under GS50 and 0.7% under GS80. Named again in step 20's read.
* **Own-play drift check:** the two actors agree within a few points in every GS cell (e.g. `sticky_overbettor` GS50
  4.7% and 4.8% in 1-10), unlike G80, whose G50-actor rows reach 65% past hand 40 against 32% on fb2-900's.
  Step 20 measures drift in each arm's own play.
* **Described, not decided:** offline, GS80 routes bp100 and `small_ball` better than G80 in all but one S2 cell
  (`small_ball`, G50 actor, over 40: 91.9% against 92.9%; `chipzen` is not in S2) and leaves the unknown ones alone.
  Whether that turns into match wins without a guard failure is step D's question (launched 14:38 UTC).
* **Outcome verifier: CONFIRMED** (2026-11-26): an independent recompute from the raw match files (own split hash,
  size parser, Beta-binomial, support test and weights; the refit equals gate.npz exactly) reproduces every figure,
  S1 and S2; the counts, labels and seeds match the spec; the two resumes left every cell whole and on additive-only
  code changes. Four wording fixes applied (33.8%, 0.53, the S2 exception, item 11's actor).

### 14.50 G0b step D: GS50 chosen, VERDICT PASS (2026-11-26)

Run on gb10-d 14:38 to 16:44 UTC from holdem-x2r `g0b` aaa17ad (`~/g0b-run/x2r`, `tools/g0b_drive.sh`) and
`g0b-root` 27773b0 (`~/d0-run/x2r-g0b`); registry 115 to 117 G0B read; rows `~/poker-ai-lab-x2r/logs/g0b/{screen,valid,read}`,
`chosen.json`, `g0b_result.json`; read `~/g0b-run/logs/drive_read.out`. Twenty new styles `~/g0b-run/styles_g0b.json`
(seed 115). Outcome verifier CONFIRMED (16:55 UTC; own script on the raw rows: counts, seeds, pairing, every
gain, the choice and the arm file's `gs_t` 0.50 recomputed).

**Screen and choice (item 19):**

| arm | B1 screen score | league lowest (200 per opponent) | pooled validation gain [lower] | worst validation style | eligible |
|---|---|---|---|---|---|
| GS80 | 78.55 | 83.5%, 23 of 23 at 80% | +0.1 [-0.0] | +0.0 | yes |
| G80 | 73.26 | 83.0%, 23 of 23 | +0.1 [-0.2] | -0.5 | yes |
| GS50 | 79.36 | 84.0%, 23 of 23 | -0.3 [-0.8] | -3.0 | yes |

GS50 is 0.81 above GS80, outside the 0.005 tie band: chosen GS50.

**Read (item 20), GS50 against fb2-900, paired gain in points:**

| cell | n | gain [95%] |
|---|---|---|
| bp100 | 4000 | +18.4 [+16.7, +20.1] |
| `small_ball` | 2000 | +18.8 [+16.9, +20.7] |
| `chipzen` | 2000 | +7.0 [+4.7, +9.2] (lower bound under its +5.10 line; reported, does not decide) |
| `sticky_overbettor` seed 113 | 2000 | -0.2 [-0.7, +0.3] |
| `sticky_overbettor` seed 95 | 2000 | +0.4 [+0.0, +0.9] |
| other D4 and B1 cells | 1000 to 2000 | -0.4 to +0.7, every interval spans or sits above zero |
| test styles `gen2:10` to `gen2:19`, pooled | 3000 | -0.1 [-0.5, +0.3]; worst `gen2:10` -1.0 [-2.5, +0.5] |

* **Rule 21:** no guard fails, both gain lines clear (bp100 lower +16.7 against +10.0, `small_ball` +16.9 against +11.0):
  **PASS**. G0's +15.2 and +16.1 are kept and beaten, and G0's `sticky_overbettor` loss (-5.9) is gone.
* **Own-play departure** (share of decisions with any expert weight): `sticky_overbettor` 4.0%, 3.7%, 0.0%, 0.0% by
  bucket against 4.8%, 3.7%, 0.1%, 0.0% offline (no drift flag); bp100 75 to 96%, `small_ball` 61 to 96%, `chipzen`
  35 to 88%. Item 15's misses show in play too: `ext:ashwing_hive` 18.2% and `ext:autodidact` 11.1% in hands 1 to 10,
  at no measurable cost (+0.1 [-1.5, +1.7], -0.4 [-2.1, +1.3]).
* **What it is not:** a candidate. 200 matches per league opponent is the screen; the upload gate needs 400 per
  opponent and a head-to-head win over the heuristic bot, and the bot as entered also carries the all-in answer.
  Next is the candidate slice (spec item 3), written by the roadmap agent.

### 14.51 C1v5: v5 (GS50 shipped as is) passes the full upload gate (2026-11-27)

Run on gb10-d 2026-11-26 23:03 to 2026-11-27 01:50 UTC (gating steps) from holdem-x2r `c1v5` 4767f28 (`~/c1v5-run/code-x2r-4`,
`tools/c1v5_drive.sh`) and `c1v5-root` b14b176 (`~/c1v5-run/code-root-2`); registry 118 to 120; rows
`~/poker-ai-lab-x2r/logs/c1v5/{step2,styles}`, result `c1v5_result.json`, `item9.out`, `gate.out`; league
`~/poker-ai-lab-league/out/c1v5/verify-rl-v5`. Twenty new styles `~/c1v5-run/styles_c1v5.json` (seed 120). Package
`~/build-rl/holdem-v5-c1v5.tar.gz` sha256 3758ca7f...0840, weights sha256 f7d22324...91e6 (= `rl/models/gs50.npz`).
Outcome verifier CONFIRMED (2026-11-27, own script on the raw rows: seeds, pairing, every gain and bound, league and head
to head counts and Wilson bounds, all 35 counter records and the package and weights hashes).

**Item 9, seed 118, v5 against fb2-900, paired match-win gain in points:**

| cell | weight | n | gain [95%] |
|---|---|---|---|
| bp100 | 0.70 | 4000 | +18.9 [+17.2, +20.6] |
| `small_ball` | 0.00 | 2000 | +20.1 [+18.1, +22.1] |
| `chipzen` | 0.00 | 2000 | +5.9 [+3.7, +8.1] (lower bound under its +5.10 line; reported, does not decide) |
| `tight_sticky`, `sticky_overbettor`, `small_ball_b` | 0.10, 0.09, 0.08 | 2000 each | -0.1, -0.1, +0.0, every interval spans zero |
| `never_fold_pre`, `raise_station`, `loose_passive` | 0.00 | 2000 each | +0.3, +0.1, +0.1 |
| `ext:ashwing`, `ext:ashwing_search`, `ext:ashwing_hive`, `ext:autodidact`, `ext:wolf` | 0 to 0.03 | 1000 each | +0.6, +0.3, -1.0 [-2.5, +0.5], +0.0, +0.1 |
| styles `gen3:0` to `gen3:19` (seed 119), pooled | | 4000 | -0.2 [-0.8, +0.3]; lowest `gen3:11` and `gen3:16` -2.5 |

Headline +13.21 [+12.00, +14.41]. Every item 9 line holds: no guard failure, bp100 lower +17.2 against +10, `small_ball`
+18.1 against +11, pooled styles lower -0.8 against -2, no style under -5. Counters clean over 34 runs.

**Step 3, E1 league pairs 200 to 399 (400 matches per opponent) and the head to head:** 23 of 23 opponents at 80% or
more; lowest `arch:5` 83.25% (Wilson lower 79.3%), then `arch:2` 86.0%, `bot:PoetAndCoder` 86.25%, `base:random` 86.5%,
`base:maniac` 87.75%; the rest 89% to 98.25%. No illegal action, no exception, no capped match. Paired differences against
fb2-900 per opponent within -1.5 to +0.5 points. Head to head against `cand:chipzen-102b05e`: 305 of 400, 76.25%, Wilson
lower 71.8% (fb2-900 +6.0 points behind it). Item 12: bp100's +18.9 beside the `bot:Blueprint` clone's -0.2 [-3.9, +3.4],
no flag. **VERDICT PASS** over 35 counter records.

* **What it means:** v5 is the first candidate to clear the whole upload gate (80% against each of the 23 league
  opponents over 400 matches, head to head win over the heuristic bot, verifier CONFIRMED). Its gains sit where the gate
  arm routes (bp100, `small_ball`, `chipzen`); everywhere else it plays as fb2-900 does, inside a point.
* **Season 16:** the swap window closed with registration (Mon 23 Nov 23:59 UTC); the season page shows no Change bot
  while matches run, so `poker-ai-lab-v4` stays the entry. Wayne said on 2026-11-27 to wrap up and upload; v5 is packaged
  for the account and for Hugging Face (private while the season runs).

### 14.52 R3 and R5 item 5: where v5's gate sends live names (reported; feeds the R4R5 rule)

Tools: holdem-x2r `e2` ddd487a `tools/e2_r3.py` (R3, C1v5's 330 replays) and `r45` 973550f `tools/r5_arena.py route`
(item 5, A0's snapshot of `~/chipzen-replays`: 20,421 files, 16,099 poker matches, all accepted by C1v5's conformance
filter; parity with r3.json on the 330 shared matches held). Root c1v5-root b14b176, hashes checked before and after.
Outputs on gb10-d: `~/e2-run/r3.out`, `~/r45-run/item5/run/r5_route.json`, printed table in `~/r45-run/drive.out`.
Both build verifiers CONFIRMED.

Entrant-faced share and v5's routing (default, T1, C1, br_chipzen), item 5:

| name | faced | default | T1 | C1 | br_chipzen |
|---|---|---|---|---|---|
| Blueprint | 15.4% | 59.6% | 38.5% | 0.1% | 1.8% |
| fermat6 | 6.8% | 84.5% | 14.6% | 0.2% | 0.6% |
| NashForge | 6.1% | 78.2% | 21.2% | 0.2% | 0.4% |
| hoops | 5.8% | 99.8% | 0.1% | 0.1% | 0.0% |
| mr_hide | 5.7% | 90.8% | 9.1% | 0.0% | 0.1% |
| r0ckGarden | 5.3% | 98.3% | 1.5% | 0.1% | 0.0% |
| PluriBot | 3.8% | 82.3% | 10.6% | 0.1% | 7.0% |
| slopBot | 2.7% | 89.2% | 10.6% | 0.1% | 0.0% |
| WSmithSimLab | 2.3% | 90.8% | 8.9% | 0.0% | 0.2% |
| AutodidactInnovations | 1.5% | 98.5% | 1.4% | 0.0% | 0.1% |
| MonteCarlo | 1.3% | 55.2% | 41.0% | 0.1% | 3.7% |
| Shuck1e1 | 0.9% | 63.8% | 35.9% | 0.1% | 0.2% |
| Chatterbox | 0.5% | 67.7% | 32.0% | 0.0% | 0.2% |

* 81 names reach a T1 share of 25% or more (in item 5 or R3); Blueprint is the only one above 2% of entrant-faced
  seats. In R3's 330 replays (public matches between other bots, experiments section 1; not v4's matches, corrected
  2026-11-27 after the V6 build verifier found no v4 seat in them) Blueprint was 5.0% of seats and 60.0% T1; Chatterbox 5.3%
  and 30.0%; the Ashwing and autodidact names together about 3.6%.
* Reading: v5 plays T1 on more than a third of its hands against the largest live name without any measurement that
  T1 gains there. The R4R5 rule decides it; under rule C (no evidence) Blueprint, above 2%, is treated as A.

### 14.53 R4: v5 against fb2-900 on the ten `bot:` clones; only Blueprint routes to T1, and its gain spans zero

Tool: holdem-x2r `r45` 973550f `tools/r4_clones.py` (paired reader on C1v5's E1 rows, pairs 200 to 399, 400 keys per
clone; v5 replayed with a `gs_route` recorder, every replayed row equal to E1; root b14b176 hashes checked before and
after). Output `~/r45-run/r4` on gb10-d, table in `~/r45-run/drive-r4.out`. 0 void clones.

| clone | v5 minus fb2-900 | 95% interval | T1 share of hands | usable (T1 above 25%) |
|---|---|---|---|---|
| Blueprint | -0.25 | [-3.89, +3.39] | 45.7% | yes, across zero |
| DeepStack | -0.75 | [-2.38, +0.88] | 17.7% | no |
| mr_hide | -1.25 | [-2.87, +0.37] | 5.4% | no |
| InfernalMonarch | +0.00 | [-1.39, +1.39] | 3.7% | no |
| SolvencyCheck | -0.50 | [-1.70, +0.70] | 1.7% | no |
| MercuryRetrograde | -0.25 | [-1.10, +0.60] | 1.2% | no |
| AutodidactInnovations | +0.00 | [-1.39, +1.39] | 0.9% | no |
| PoetAndCoder | +0.00 | [-0.69, +0.69] | 0.8% | no |
| Kimiko | +0.00 | [+0.00, +0.00] | 0.3% | no |
| qwentom-leap | +0.50 | [-0.19, +1.19] | 0.3% | no |

* No clone is usable with an interval that excludes zero, so the validity check counts 0 clones (5 needed) and fails;
  R5's style pooling does not run and gives no A, B or D. Seed 127 stays unregistered.
* Reading: against the Blueprint clone v5 routes T1 on 45.7% of hands and wins the same as fb2-900 within about 3.6
  points either way. Clones overstate (14.25), so this neither supports nor condemns T1 there.

### 14.54 R4R5 rule table: Blueprint and NashForge go to v5.1 (no evidence, above 2% of seats)

Tool: holdem-x2r `r45` 973550f `tools/r45_rules.py table` over item 5 (14.52), R3 and R4 (14.53); output
`~/r45-run/table/table.json` on gb10-d, printed in `~/r45-run/drive-table.out`. Validity check FAIL (0 counted
clones), so R5 contributed nothing and every target name is C.

* 81 target names (T1 share 25% or more in item 5 or R3): all C. Two are above 2% of entrant-faced seats and so take
  rule A's action: **Blueprint** (15.4% of seats, T1 38.5% in item 5 and 60.0% in R3; R4 clone -0.25 [-3.89, +3.39])
  and **NashForge** (6.1%, T1 21.2% in item 5 and 28.0% in R3). The other 79 are kept; 210 other names not judged.
* Action, as pre-registered: v5.1, the gate refit with Blueprint's and NashForge's real archive counts in the
  population class, through C1v5's steps before it replaces v5.
* What this does not show: that T1 loses to Blueprint. It shows nothing measures T1 there, and the rule puts the
  largest live names on the default until something does.

### 14.55 E2 Stage 1: the teachers' gain matrix; both families get a class (CONTINUE both)

Tool: holdem-x2r `e2` ddd487a `tools/e2_drive.sh` on gb10-d (03:18 to 04:44 UTC), root b14b176, seed 121, 500 matches
per cell, 24 cells, 0 voids; `~/poker-ai-lab-x2r/logs/e2/stage1_table.txt` and `stage1_classes.json`. Build verifier
CONFIRMED.

| name | br_ashwing minus fb2-900 | br_autofast minus fb2-900 | class |
|---|---|---|---|
| ext:ashwing | +14.2 [+10.2, +18.2] | -2.8 [-7.3, +1.7] | ashwing |
| ext:ashwing_search | +13.6 [+9.6, +17.6] | -2.0 [-6.5, +2.5] | ashwing |
| ext:ashwing_hive | +5.8 [+2.3, +9.3] | -6.6 [-10.5, -2.7] | held out (population) |
| ext:ashwing_v2 | +5.8 [+2.3, +9.3] | -6.6 [-10.5, -2.7] | population |
| ext:ashwing_adaptive | +5.8 [+2.3, +9.3] | -6.6 [-10.5, -2.7] | population |
| ext:ashwing_value | +0.8 [-2.0, +3.6] | +2.2 [-0.8, +5.2] | population |
| ext:autodidact | +1.2 [-2.9, +5.3] | +14.2 [+10.3, +18.1] | autodidact |
| ext:autodidact_fast | +2.2 [-2.2, +6.6] | +13.2 [+9.3, +17.1] | autodidact |

* Verdict CONTINUE both: ashwing family {ext:ashwing, ext:ashwing_search}, autodidact family {ext:autodidact,
  ext:autodidact_fast}. The teachers are specific: each loses or ties against the other family.
* `ext:ashwing_hive`, `ext:ashwing_v2` and `ext:ashwing_adaptive` give identical rows on every key apart from the
  opponent label (checked by hashing the rows without it). In our harness the V2 and Adaptive classes play exactly as
  Hive Mind, so their river logic never changes an action. The engine does send `seats` with `is_self`; why the river
  path is inert is unverified. It changes no class here (all three are population), but `ext:ashwing_v2` is not an
  independent cell, and the live Ashwing_v2 may play differently on the river than our copy.

### 14.56 V6 stage A: STOP_V6; on the gate's 14 terms Blueprint cannot be told from bp100

Tool: holdem-x2r `v6` e23e5a9 `tools/v6_drive.sh` (stage a), fitter holdem-rl `v6-rl` 79dc09a, runtime `v6-root`
562cb58, root c1v5-root b14b176; gb10-d `~/v6-run` (06:21 UTC; output `~/v6-run/drive.out`, gates `~/v6-run/a/`).
Seed 127 registered `127 V6 draw`. Draw: Blueprint 1,918 candidates, NashForge 560 (324 Blueprint-against-NashForge
matches dropped); bands Blueprint 250 calibration, 250 held out, 500 fit; NashForge 140, 140, 280. check-v5 reproduced
gs50 exactly. Shadow replay: 400 `bot:Blueprint` keys, 13,212 hands, 0 rows differing from E1. r3 parity 0. Build
verifiers 1 and 2 REFUTED (cap), fixed first-hand (roadmap V6 review record).

Hands routed to any expert (the line bar is 10% in every bucket):

| attempt | line | name | hands 1-10 | 11-40 | 41+ |
|---|---|---|---|---|---|
| 1, solver_live (T 0.40) | (a) archive held out | Blueprint | 30.3% | 35.1% | 16.3% |
| 1 | (a) | NashForge | 11.6% | 3.2% | 0.0% |
| 1 | (b) own-hero shadow | Blueprint | 36.4% | 32.3% | 3.5% |
| 2, two classes (T 0.45) | (a) | Blueprint | 35.6% | 38.0% | 17.5% |
| 2 | (a) | NashForge | 15.1% | 3.7% | 0.1% |
| 2 | (b) | Blueprint | 41.3% | 37.9% | 4.9% |

Line (c) held both times (T1 share on bp100 at hands 11 and later: fb2-900 94.84% under v5, 93.00% and 93.90% under the
two refits; G50 96.69%, 95.75% and 96.37%). Nearly all routed hands go to T1. Reported (item 6), v5 then attempt 1:
Blueprint any-expert 60.9% to 33.9%, Chatterbox 32.3% to 17.3%, MonteCarlo 44.8% to 16.6%, PluriBot 17.7% to 8.0%,
fermat6 15.5% to 2.7%.

* Outcome STOP_V6, as pre-registered; returned to the roadmap agent.
* Reading: a class fitted on Blueprint's own archive counts halves T1 routing on Blueprint but leaves about a third of
  its hands on T1, while bp100 keeps 93% or more. On these 14 terms Blueprint and bp100 overlap: the gate sees
  Blueprint as bp100 for long stretches. A gate on these terms cannot keep T1 for bp100 and keep it off Blueprint.


### 14.57 GP0 Stage 0: BASE-FLAT; the sturdier base (S2 it1800) does not win more against the aggressor styles

Tool: holdem-x2r `gp0` e1424cd `tools/gp0_drive.sh 0` on gb10-d (12:38 to 12:41 UTC 2026-11-27), from `~/gp0-run/code`
(`code.commit`); rows, records and result in `~/gp0-run/stage0/` (`result.json`, `runs.jsonl`, `capacity_*.json`).
Seed 128 (`128 GP0 read`, registered with 129 to 132 by the driver, pre-copy `~/gp0-run/seed_registry.pre-gp0`).
S2 it1800 `~/poker-ai-lab-rl/ckpt/s2/it001800.npz` (sha256 prefix 4989481c5e7d5d8b, asserted) against fb2-900, plain
`rl.eval_arena`, 2,000 matches per cell, paired on (seed, hero seat). Capacity at the run: 19.0 GiB available, swap 11.9
GiB, 16 workers (shared device; timings are from a shared box).

| cell | it1800 minus fb2-900 (points) | 95% interval |
|---|---|---|
| `small_ball` | -0.90 | [-2.91, +1.11] |
| `small_ball_b` | -2.45 | [-4.44, -0.46] |
| `sticky_overbettor` | -1.30 | [-2.76, +0.16] |
| `loose_passive` | -0.35 | [-1.70, +1.00] |
| pooled (equal weight) | -1.25 | [-2.12, -0.38] |

* Verdict **BASE-FLAT** (the `small_ball` upper bound +1.11 is under +4.0): E3 stays a reported number and the base
  stays last in the order; no base slice is specified beside GP1.
* Reading: S2's exploiter league made the policy harder to exploit (E3 96.5% to 78.7%, 14.10, 14.15) but it does not
  convert into wins against the styles that take fb2-900's over-fold; if anything it gives up about a point. The leak
  those styles take is one the decision procedure has to answer online, which is what Stages A and B measure.
* Outcome verifier CONFIRMED (2026-11-27): every gain, SE and interval recomputed from the raw rows with its own script
  (2,000 distinct shared keys per cell and arm, won consistent with stacks, pool = mean of the four gains with SE
  sqrt(sum SE^2)/4); a 40-match replay per arm on small_ball and loose_passive matched its own arm's rows 40 of 40 and the
  other arm's 13 or 14 of 40, so each arm used its pinned model; registry diff exactly 128 to 132 `GP0 read`.
