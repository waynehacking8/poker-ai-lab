# Hold'em bot: algorithm iteration log

Format of every number: 200 seat-swapped matches (100 duplicate pairs, fixed seed 1) in the
real season format (10,000 stacks, blinds 50/100 rising every 20 hands to 600, play to bust),
produced by `python -m holdem.arena --opp NAME --matches 200 --seed 1`.

## Iteration 0: first complete bot

Rule-based hybrid: CFR+ push/fold priors, EV jam/call by equity against a range narrowed
by his actions, postflop Monte Carlo equity with if-then bet/bluff thresholds.

| opponent | win rate |
|---|---|
| station | 94.0% |
| reference | 94.0% |
| nit | 85.0% |
| random | 76.5% |
| maniac | 73.5% |
| station_raiser | 71.0% |
| lag | 60.0% |

Diagnosis (`/tmp`-style leak script, bucketing every hand by how it ended): against `lag`
the chips were lost by *folding after investing* (flop/turn/river "hero folded" buckets,
about -2.7, -4.1, -6.7 big blinds per occurrence, thousands of occurrences) and by never
exploiting that it folds to pressure. The if-then bluff rules needed 4 observations plus a
fold rate above 0.6 plus a coin flip, so they almost never fired in a 50-hand match.

## Things tried that did NOT help (kept for the record)

* Faster learning (smaller prior weight on bet frequency): lag 60% -> 55.5%, maniac unchanged.
* Win-probability utility (gambler's ruin) instead of chip EV for calls and jams, with the
  drift prior swept over 0.05 / 0.25 / 0.6 / 1.2 bb per hand. More risk aversion was worse
  (maniac 73% -> 64.5%), risk seeking was worse too (57%). Chip EV is close to optimal here.
  The utility code is kept with a near-linear prior.

## Iteration 1: expected-value action selection with a fold-equity model (postflop)

What lost: the if-then bluff and bet rules (see iteration 0). What changed: one rule values
every option (fold, check, call, bet or raise at several sizes, shove) as
`f * pot + r * (value after he raises) + (1 - f - r) * (equity when called * (pot + 2 risk)
- risk)`, where `f` is his learned fold probability for that size, `r` his raise-over-bet
rate, and the equity when called is taken against the strongest part of his range that does
not fold (two extra Monte Carlo runs against the top 50 percent and top 20 percent). Value
bets, thin value, semi-bluffs and pure bluffs now come from the same formula.

Before / after on 200 matches: lag 60% -> 67.5%, with the raise response added 68%;
reference fell 94% -> 85% when bluffs ignored his raises and recovered to 88% once the
raise branch existed. Maniac 73.5% -> 65% -> 71% after bets were valued in win probability
units (next item).

## Iteration 2: utility of a stack instead of chips (kept, near linear)

Hypothesis: winner-take-all makes chip EV the wrong objective, a coin flip for the whole
stack should be refused by the favourite. Implemented gambler's ruin utility, drift from
observed results with a prior, and swept the prior 0.05 / 0.1 / 0.25 / 0.4 / 0.6 / 1.2 bb per
hand. Result: more risk aversion was worse (maniac 73% -> 64.5%), less was no better. Probe
that explains it: a bot that only shoves or calls with the top X percent of hands and
otherwise folds, against the maniac, over 200 matches:

| top X percent | 30 | 15 | 7 | 3 | 1.5 |
|---|---|---|---|---|---|
| win rate | 61% | 67.5% | 73.5% | 59.5% | 35.5% |

Waiting for premium hands is paid for by blind escalation, so the maximum of that family
is the same 73% the full bot gets. Reaching 80% against a bot that shoves 25% of its
actions would need chips won without all-ins, which this bot already tries (it wins about
+8 bb per hand at 100 BB against the maniac).

## Iteration 3: small blind completes, re-raise fold rates, call-shove prior

Diagnosis with `scripts/holdem_diag.py` at 15 BB against station_raiser: the button folded
67 percent of hands (-0.5 bb each, about -1000 bb over 3000 hands) because the learned
call range made every marginal shove negative. Changes: (a) the small blind may complete
(limp) when that has positive utility against his big blind raise rate, (b) the fold rate
against a 3-bet or jam now starts from how often he folds to an ordinary raise, which has
far more data than the fold-to-3-bet counter, (c) the call-shove prior moves a third of the
way from the Nash table towards a looser field default.

Before / after on 400 matches (seed 1): station_raiser 67.5% -> 71.5% (69.5% in the final
configuration, within noise of 71.5), random 80% -> 83%, nit 84.5% -> 88.8%.

## Final numbers (400 matches each, `python -m holdem.arena --opp all --matches 400`)

| opponent | seed 1 | CI 95% | seed 2 (not tuned on) |
|---|---|---|---|
| station | 96.0% | 93.6 to 97.5 | 95.5% |
| reference | 90.8% | 87.5 to 93.2 | 90.3% |
| nit | 88.8% | 85.3 to 91.5 | 86.5% |
| random | 83.0% | 79.0 to 86.4 | 79.0% |
| lag | 71.5% | 66.9 to 75.7 | 69.3% |
| maniac | 72.3% | 67.7 to 76.4 | 72.3% |
| station_raiser | 69.5% | 64.8 to 73.8 | 72.3% |

## Status against the 80 percent bar

Not met for lag, maniac and station_raiser; random is on the line, its lower CI bound is
79.0%. More Monte Carlo samples (500 -> 1500 per decision) changed nothing beyond noise, so
equity precision is not the limit. Remaining chip leaks by bucket: against lag and
station_raiser the bot is stacked off at 25 to 50 BB in medium-strength pots and folds to
re-raises after investing; against maniac and random the deficit is match variance, not
chips. Next candidates are listed in HANDOFF.md.
