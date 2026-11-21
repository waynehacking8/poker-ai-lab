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

Replaced the postflop if-then thresholds by one rule: value every option (fold, check, call,
bet or raise at several sizes, shove) as `f * pot + (1 - f) * (equity_when_called * (pot +
2 risk) - risk)` where `f` is his learned fold probability for that size and the equity when
called is taken against the strongest part of his range that does not fold. Value bets, thin
value, semi-bluffs and pure bluffs now fall out of the same formula.

lag 60% -> 67.5% (first measurement, more below).
