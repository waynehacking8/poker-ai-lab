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
the point estimate. A rerun on the corrected engine is in progress.

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
  is 87.4% at 10000 stacks. A first 12 matches went 11 to 1; the arena
  confirmation over 2000 matches is running. Until it agrees I treat 87.4% as
  unconfirmed.

## 8. River search and safe exploitation

`search/`: vectorized CFR+ over 1326 combos with a safe re-solve gadget, and
Ganzfried-Sandholm safe exploitation.

* Exploitability at 100 iterations: 1.6 to 1.9% of the pot.
* When the solver is given a too-narrow opponent range, the opponent's gain
  from the unsafe re-solve is 21 to 28% of the pot, against 0.6 to 0.7% with
  the safe gadget.
* A river resolve costs about 0.5 s median on the x86 estimate, which just
  fits. Turn solving does not fit (3.7 s).
