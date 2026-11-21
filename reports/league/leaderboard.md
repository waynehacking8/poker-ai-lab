# League leaderboard

Rank is the match-win rate against the field population (archetype win rates weighted by archetype share in rated matches), 95% bootstrap CI over duplicate pairs; ties broken by mean hands per won match (fewer is better).  Win rate is percent of matches, a tied hand cap counts half.

| # | entrant | gate (point) | gate (lower bound) | field win % [95% CI] | hands/win | bot-clone win % [95% CI] | baseline win % [95% CI] | field matches | decide ms mean/max | errors |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | cand:chipzen-tip | FAIL 9/23 | FAIL 4/23 | 77.8 [75.1, 80.6] | 32.0 | 74.7 [71.0, 78.0] | 79.9 [77.0, 82.5] | 800 | 6.0/30 | 0 |
| 2 | base:lag | FAIL 3/22 | FAIL 1/22 | 68.5 [65.6, 71.3] | 37.5 | 68.5 [64.7, 72.1] | 70.3 [66.8, 73.5] | 800 | -/0 | 0 |
| 3 | base:station_raiser | FAIL 4/22 | FAIL 2/22 | 62.0 [59.2, 65.2] | 27.7 | 65.5 [61.6, 69.2] | 58.9 [55.3, 62.4] | 800 | -/0 | 0 |
| 4 | base:maniac | FAIL 0/22 | FAIL 0/22 | 47.5 [44.9, 50.3] | 4.4 | 45.7 [41.7, 49.7] | 46.2 [42.6, 49.9] | 800 | -/0 | 0 |
| 5 | base:nit | FAIL 5/22 | FAIL 1/22 | 42.1 [39.2, 45.0] | 71.8 | 52.2 [48.2, 56.1] | 63.3 [59.8, 66.8] | 800 | -/0 | 0 |
| 6 | base:random | FAIL 0/22 | FAIL 0/22 | 41.6 [38.5, 44.7] | 7.2 | 38.3 [34.5, 42.3] | 43.9 [40.3, 47.5] | 800 | -/0 | 0 |
| 7 | base:reference | FAIL 2/22 | FAIL 2/22 | 30.6 [28.2, 33.1] | 69.9 | 38.2 [34.4, 42.1] | 49.9 [46.2, 53.5] | 800 | -/0 | 0 |
| 8 | base:station | FAIL 0/22 | FAIL 0/22 | 10.7 [9.0, 12.5] | 83.2 | 8.5 [6.5, 11.0] | 22.5 [19.6, 25.7] | 800 | -/0 | 0 |

## Gate: at least 80% of matches against each opponent separately

An entrant passes only if its win rate is at least 80% against every baseline, every archetype clone and every per-bot clone on its own; the field-weighted average does not count. The point estimate is the plain match win rate; the lower bound is the 95% Wilson lower bound over matches. An entrant never plays itself.

### cand:chipzen-tip

| opponent | win % | 95% lower bound | matches | pass (point) | pass (lower bound) |
|---|---|---|---|---|---|
| baseline lag | 67.5 | 58.7 | 120 | FAIL | FAIL |
| baseline maniac | 75.0 | 66.6 | 120 | FAIL | FAIL |
| baseline nit | 82.5 | 74.7 | 120 | PASS | FAIL |
| baseline random | 80.8 | 72.9 | 120 | PASS | FAIL |
| baseline reference | 88.3 | 81.4 | 120 | PASS | PASS |
| baseline station | 95.0 | 89.5 | 120 | PASS | PASS |
| baseline station_raiser | 70.0 | 61.3 | 120 | FAIL | FAIL |
| archetype A0-limper-calm | 81.2 | 75.4 | 208 | PASS | FAIL |
| archetype A1-station | 90.2 | 83.9 | 132 | PASS | PASS |
| archetype A2-opener-aggro-shover | 77.3 | 63.0 | 44 | FAIL | FAIL |
| archetype A3-opener-aggro-shover | 73.1 | 65.8 | 160 | FAIL | FAIL |
| archetype A4-bb-folder-calm | 76.2 | 65.9 | 80 | FAIL | FAIL |
| archetype A5-opener-calm | 69.9 | 62.7 | 176 | FAIL | FAIL |
| bot clone Blueprint | 63.3 | 50.7 | 60 | FAIL | FAIL |
| bot clone Kimiko | 91.7 | 81.9 | 60 | PASS | PASS |
| bot clone AutodidactInnovations | 61.7 | 49.0 | 60 | FAIL | FAIL |
| bot clone SolvencyCheck | 70.0 | 57.5 | 60 | FAIL | FAIL |
| bot clone DeepStack | 90.0 | 79.9 | 60 | PASS | FAIL |
| bot clone mr_hide | 71.7 | 59.2 | 60 | FAIL | FAIL |
| bot clone MercuryRetrograde | 85.0 | 73.9 | 60 | PASS | FAIL |
| bot clone qwentom-leap | 76.7 | 64.6 | 60 | FAIL | FAIL |
| bot clone InfernalMonarch | 70.0 | 57.5 | 60 | FAIL | FAIL |
| bot clone PoetAndCoder | 66.7 | 54.1 | 60 | FAIL | FAIL |

### base:lag

| opponent | win % | 95% lower bound | matches | pass (point) | pass (lower bound) |
|---|---|---|---|---|---|
| baseline maniac | 48.3 | 39.6 | 120 | FAIL | FAIL |
| baseline nit | 95.0 | 89.5 | 120 | PASS | PASS |
| baseline random | 75.8 | 67.4 | 120 | FAIL | FAIL |
| baseline reference | 80.0 | 72.0 | 120 | PASS | FAIL |
| baseline station | 85.0 | 77.5 | 120 | PASS | FAIL |
| baseline station_raiser | 37.5 | 29.4 | 120 | FAIL | FAIL |
| archetype A0-limper-calm | 71.6 | 65.2 | 208 | FAIL | FAIL |
| archetype A1-station | 74.2 | 66.2 | 132 | FAIL | FAIL |
| archetype A2-opener-aggro-shover | 59.1 | 44.4 | 44 | FAIL | FAIL |
| archetype A3-opener-aggro-shover | 63.7 | 56.1 | 160 | FAIL | FAIL |
| archetype A4-bb-folder-calm | 66.2 | 55.4 | 80 | FAIL | FAIL |
| archetype A5-opener-calm | 68.2 | 61.0 | 176 | FAIL | FAIL |
| bot clone Blueprint | 53.3 | 40.9 | 60 | FAIL | FAIL |
| bot clone Kimiko | 78.3 | 66.4 | 60 | FAIL | FAIL |
| bot clone AutodidactInnovations | 68.3 | 55.8 | 60 | FAIL | FAIL |
| bot clone SolvencyCheck | 73.3 | 61.0 | 60 | FAIL | FAIL |
| bot clone DeepStack | 73.3 | 61.0 | 60 | FAIL | FAIL |
| bot clone mr_hide | 63.3 | 50.7 | 60 | FAIL | FAIL |
| bot clone MercuryRetrograde | 71.7 | 59.2 | 60 | FAIL | FAIL |
| bot clone qwentom-leap | 73.3 | 61.0 | 60 | FAIL | FAIL |
| bot clone InfernalMonarch | 66.7 | 54.1 | 60 | FAIL | FAIL |
| bot clone PoetAndCoder | 63.3 | 50.7 | 60 | FAIL | FAIL |

### base:station_raiser

| opponent | win % | 95% lower bound | matches | pass (point) | pass (lower bound) |
|---|---|---|---|---|---|
| baseline lag | 62.5 | 53.6 | 120 | FAIL | FAIL |
| baseline maniac | 65.0 | 56.1 | 120 | FAIL | FAIL |
| baseline nit | 35.8 | 27.8 | 120 | FAIL | FAIL |
| baseline random | 61.7 | 52.7 | 120 | FAIL | FAIL |
| baseline reference | 31.7 | 24.0 | 120 | FAIL | FAIL |
| baseline station | 96.7 | 91.7 | 120 | PASS | PASS |
| archetype A0-limper-calm | 65.4 | 58.7 | 208 | FAIL | FAIL |
| archetype A1-station | 90.2 | 83.9 | 132 | PASS | PASS |
| archetype A2-opener-aggro-shover | 47.7 | 33.8 | 44 | FAIL | FAIL |
| archetype A3-opener-aggro-shover | 56.2 | 48.5 | 160 | FAIL | FAIL |
| archetype A4-bb-folder-calm | 53.8 | 42.9 | 80 | FAIL | FAIL |
| archetype A5-opener-calm | 50.0 | 42.7 | 176 | FAIL | FAIL |
| bot clone Blueprint | 55.0 | 42.5 | 60 | FAIL | FAIL |
| bot clone Kimiko | 88.3 | 77.8 | 60 | PASS | FAIL |
| bot clone AutodidactInnovations | 50.0 | 37.7 | 60 | FAIL | FAIL |
| bot clone SolvencyCheck | 61.7 | 49.0 | 60 | FAIL | FAIL |
| bot clone DeepStack | 85.0 | 73.9 | 60 | PASS | FAIL |
| bot clone mr_hide | 63.3 | 50.7 | 60 | FAIL | FAIL |
| bot clone MercuryRetrograde | 60.0 | 47.4 | 60 | FAIL | FAIL |
| bot clone qwentom-leap | 58.3 | 45.7 | 60 | FAIL | FAIL |
| bot clone InfernalMonarch | 61.7 | 49.0 | 60 | FAIL | FAIL |
| bot clone PoetAndCoder | 71.7 | 59.2 | 60 | FAIL | FAIL |

### base:maniac

| opponent | win % | 95% lower bound | matches | pass (point) | pass (lower bound) |
|---|---|---|---|---|---|
| baseline lag | 42.5 | 34.0 | 120 | FAIL | FAIL |
| baseline nit | 33.3 | 25.5 | 120 | FAIL | FAIL |
| baseline random | 68.3 | 59.6 | 120 | FAIL | FAIL |
| baseline reference | 50.8 | 42.0 | 120 | FAIL | FAIL |
| baseline station | 50.0 | 41.2 | 120 | FAIL | FAIL |
| baseline station_raiser | 32.5 | 24.8 | 120 | FAIL | FAIL |
| archetype A0-limper-calm | 49.0 | 42.3 | 208 | FAIL | FAIL |
| archetype A1-station | 52.3 | 43.8 | 132 | FAIL | FAIL |
| archetype A2-opener-aggro-shover | 50.0 | 35.8 | 44 | FAIL | FAIL |
| archetype A3-opener-aggro-shover | 48.1 | 40.5 | 160 | FAIL | FAIL |
| archetype A4-bb-folder-calm | 31.2 | 22.2 | 80 | FAIL | FAIL |
| archetype A5-opener-calm | 48.3 | 41.0 | 176 | FAIL | FAIL |
| bot clone Blueprint | 46.7 | 34.6 | 60 | FAIL | FAIL |
| bot clone Kimiko | 46.7 | 34.6 | 60 | FAIL | FAIL |
| bot clone AutodidactInnovations | 40.0 | 28.6 | 60 | FAIL | FAIL |
| bot clone SolvencyCheck | 43.3 | 31.6 | 60 | FAIL | FAIL |
| bot clone DeepStack | 53.3 | 40.9 | 60 | FAIL | FAIL |
| bot clone mr_hide | 46.7 | 34.6 | 60 | FAIL | FAIL |
| bot clone MercuryRetrograde | 48.3 | 36.2 | 60 | FAIL | FAIL |
| bot clone qwentom-leap | 41.7 | 30.1 | 60 | FAIL | FAIL |
| bot clone InfernalMonarch | 48.3 | 36.2 | 60 | FAIL | FAIL |
| bot clone PoetAndCoder | 41.7 | 30.1 | 60 | FAIL | FAIL |

### base:nit

| opponent | win % | 95% lower bound | matches | pass (point) | pass (lower bound) |
|---|---|---|---|---|---|
| baseline lag | 10.8 | 6.4 | 120 | FAIL | FAIL |
| baseline maniac | 71.7 | 63.0 | 120 | FAIL | FAIL |
| baseline random | 54.2 | 45.3 | 120 | FAIL | FAIL |
| baseline reference | 85.8 | 78.5 | 120 | PASS | FAIL |
| baseline station | 95.8 | 90.6 | 120 | PASS | PASS |
| baseline station_raiser | 61.7 | 52.7 | 120 | FAIL | FAIL |
| archetype A0-limper-calm | 54.3 | 47.5 | 208 | FAIL | FAIL |
| archetype A1-station | 84.1 | 76.9 | 132 | PASS | FAIL |
| archetype A2-opener-aggro-shover | 18.2 | 9.5 | 44 | FAIL | FAIL |
| archetype A3-opener-aggro-shover | 28.7 | 22.3 | 160 | FAIL | FAIL |
| archetype A4-bb-folder-calm | 50.0 | 39.3 | 80 | FAIL | FAIL |
| archetype A5-opener-calm | 11.4 | 7.5 | 176 | FAIL | FAIL |
| bot clone Blueprint | 11.7 | 5.8 | 60 | FAIL | FAIL |
| bot clone Kimiko | 88.3 | 77.8 | 60 | PASS | FAIL |
| bot clone AutodidactInnovations | 38.3 | 27.1 | 60 | FAIL | FAIL |
| bot clone SolvencyCheck | 41.7 | 30.1 | 60 | FAIL | FAIL |
| bot clone DeepStack | 88.3 | 77.8 | 60 | PASS | FAIL |
| bot clone mr_hide | 50.0 | 37.7 | 60 | FAIL | FAIL |
| bot clone MercuryRetrograde | 50.0 | 37.7 | 60 | FAIL | FAIL |
| bot clone qwentom-leap | 60.0 | 47.4 | 60 | FAIL | FAIL |
| bot clone InfernalMonarch | 55.0 | 42.5 | 60 | FAIL | FAIL |
| bot clone PoetAndCoder | 38.3 | 27.1 | 60 | FAIL | FAIL |

### base:random

| opponent | win % | 95% lower bound | matches | pass (point) | pass (lower bound) |
|---|---|---|---|---|---|
| baseline lag | 24.2 | 17.4 | 120 | FAIL | FAIL |
| baseline maniac | 29.2 | 21.8 | 120 | FAIL | FAIL |
| baseline nit | 52.5 | 43.6 | 120 | FAIL | FAIL |
| baseline reference | 64.2 | 55.3 | 120 | FAIL | FAIL |
| baseline station | 52.5 | 43.6 | 120 | FAIL | FAIL |
| baseline station_raiser | 40.8 | 32.5 | 120 | FAIL | FAIL |
| archetype A0-limper-calm | 45.2 | 38.6 | 208 | FAIL | FAIL |
| archetype A1-station | 46.2 | 37.9 | 132 | FAIL | FAIL |
| archetype A2-opener-aggro-shover | 34.1 | 21.9 | 44 | FAIL | FAIL |
| archetype A3-opener-aggro-shover | 38.1 | 31.0 | 160 | FAIL | FAIL |
| archetype A4-bb-folder-calm | 32.5 | 23.2 | 80 | FAIL | FAIL |
| archetype A5-opener-calm | 43.2 | 36.1 | 176 | FAIL | FAIL |
| bot clone Blueprint | 36.7 | 25.6 | 60 | FAIL | FAIL |
| bot clone Kimiko | 48.3 | 36.2 | 60 | FAIL | FAIL |
| bot clone AutodidactInnovations | 36.7 | 25.6 | 60 | FAIL | FAIL |
| bot clone SolvencyCheck | 21.7 | 13.1 | 60 | FAIL | FAIL |
| bot clone DeepStack | 40.0 | 28.6 | 60 | FAIL | FAIL |
| bot clone mr_hide | 43.3 | 31.6 | 60 | FAIL | FAIL |
| bot clone MercuryRetrograde | 38.3 | 27.1 | 60 | FAIL | FAIL |
| bot clone qwentom-leap | 35.0 | 24.2 | 60 | FAIL | FAIL |
| bot clone InfernalMonarch | 53.3 | 40.9 | 60 | FAIL | FAIL |
| bot clone PoetAndCoder | 30.0 | 19.9 | 60 | FAIL | FAIL |

### base:reference

| opponent | win % | 95% lower bound | matches | pass (point) | pass (lower bound) |
|---|---|---|---|---|---|
| baseline lag | 24.2 | 17.4 | 120 | FAIL | FAIL |
| baseline maniac | 54.2 | 45.3 | 120 | FAIL | FAIL |
| baseline nit | 14.2 | 9.0 | 120 | FAIL | FAIL |
| baseline random | 42.5 | 34.0 | 120 | FAIL | FAIL |
| baseline station | 94.2 | 88.4 | 120 | PASS | PASS |
| baseline station_raiser | 70.0 | 61.3 | 120 | FAIL | FAIL |
| archetype A0-limper-calm | 36.1 | 29.8 | 208 | FAIL | FAIL |
| archetype A1-station | 75.0 | 67.0 | 132 | FAIL | FAIL |
| archetype A2-opener-aggro-shover | 18.2 | 9.5 | 44 | FAIL | FAIL |
| archetype A3-opener-aggro-shover | 13.1 | 8.7 | 160 | FAIL | FAIL |
| archetype A4-bb-folder-calm | 38.8 | 28.8 | 80 | FAIL | FAIL |
| archetype A5-opener-calm | 6.8 | 3.9 | 176 | FAIL | FAIL |
| bot clone Blueprint | 8.3 | 3.6 | 60 | FAIL | FAIL |
| bot clone Kimiko | 91.7 | 81.9 | 60 | PASS | PASS |
| bot clone AutodidactInnovations | 26.7 | 17.1 | 60 | FAIL | FAIL |
| bot clone SolvencyCheck | 31.7 | 21.3 | 60 | FAIL | FAIL |
| bot clone DeepStack | 70.0 | 57.5 | 60 | FAIL | FAIL |
| bot clone mr_hide | 31.7 | 21.3 | 60 | FAIL | FAIL |
| bot clone MercuryRetrograde | 46.7 | 34.6 | 60 | FAIL | FAIL |
| bot clone qwentom-leap | 35.0 | 24.2 | 60 | FAIL | FAIL |
| bot clone InfernalMonarch | 30.0 | 19.9 | 60 | FAIL | FAIL |
| bot clone PoetAndCoder | 10.0 | 4.7 | 60 | FAIL | FAIL |

### base:station

| opponent | win % | 95% lower bound | matches | pass (point) | pass (lower bound) |
|---|---|---|---|---|---|
| baseline lag | 15.0 | 9.7 | 120 | FAIL | FAIL |
| baseline maniac | 50.0 | 41.2 | 120 | FAIL | FAIL |
| baseline nit | 9.2 | 5.2 | 120 | FAIL | FAIL |
| baseline random | 47.5 | 38.8 | 120 | FAIL | FAIL |
| baseline reference | 8.3 | 4.6 | 120 | FAIL | FAIL |
| baseline station_raiser | 5.0 | 2.3 | 120 | FAIL | FAIL |
| archetype A0-limper-calm | 4.3 | 2.3 | 208 | FAIL | FAIL |
| archetype A1-station | 25.0 | 18.4 | 132 | FAIL | FAIL |
| archetype A2-opener-aggro-shover | 15.9 | 7.9 | 44 | FAIL | FAIL |
| archetype A3-opener-aggro-shover | 4.4 | 2.1 | 160 | FAIL | FAIL |
| archetype A4-bb-folder-calm | 1.2 | 0.2 | 80 | FAIL | FAIL |
| archetype A5-opener-calm | 16.5 | 11.7 | 176 | FAIL | FAIL |
| bot clone Blueprint | 16.7 | 9.3 | 60 | FAIL | FAIL |
| bot clone Kimiko | 23.3 | 14.4 | 60 | FAIL | FAIL |
| bot clone AutodidactInnovations | 1.7 | 0.3 | 60 | FAIL | FAIL |
| bot clone SolvencyCheck | 1.7 | 0.3 | 60 | FAIL | FAIL |
| bot clone DeepStack | 23.3 | 14.4 | 60 | FAIL | FAIL |
| bot clone mr_hide | 3.3 | 0.9 | 60 | FAIL | FAIL |
| bot clone MercuryRetrograde | 3.3 | 0.9 | 60 | FAIL | FAIL |
| bot clone qwentom-leap | 5.0 | 1.7 | 60 | FAIL | FAIL |
| bot clone InfernalMonarch | 3.3 | 0.9 | 60 | FAIL | FAIL |
| bot clone PoetAndCoder | 3.3 | 0.9 | 60 | FAIL | FAIL |

## Field population

Archetype shares (rated participants): A0-limper-calm 26%, A1-station 16%, A2-opener-aggro-shover 6%, A3-opener-aggro-shover 20%, A4-bb-folder-calm 10%, A5-opener-calm 22%

| entrant | A0-limper-calm | A1-station | A2-opener-aggro-shover | A3-opener-aggro-shover | A4-bb-folder-calm | A5-opener-calm |
|---|---|---|---|---|---|---|
| cand:chipzen-tip | 81.2 (n=208) | 90.2 (n=132) | 77.3 (n=44) | 73.1 (n=160) | 76.2 (n=80) | 69.9 (n=176) |
| base:lag | 71.6 (n=208) | 74.2 (n=132) | 59.1 (n=44) | 63.7 (n=160) | 66.2 (n=80) | 68.2 (n=176) |
| base:station_raiser | 65.4 (n=208) | 90.2 (n=132) | 47.7 (n=44) | 56.2 (n=160) | 53.8 (n=80) | 50.0 (n=176) |
| base:maniac | 49.0 (n=208) | 52.3 (n=132) | 50.0 (n=44) | 48.1 (n=160) | 31.2 (n=80) | 48.3 (n=176) |
| base:nit | 54.3 (n=208) | 84.1 (n=132) | 18.2 (n=44) | 28.7 (n=160) | 50.0 (n=80) | 11.4 (n=176) |
| base:random | 45.2 (n=208) | 46.2 (n=132) | 34.1 (n=44) | 38.1 (n=160) | 32.5 (n=80) | 43.2 (n=176) |
| base:reference | 36.1 (n=208) | 75.0 (n=132) | 18.2 (n=44) | 13.1 (n=160) | 38.8 (n=80) | 6.8 (n=176) |
| base:station | 4.3 (n=208) | 25.0 (n=132) | 15.9 (n=44) | 4.4 (n=160) | 1.2 (n=80) | 16.5 (n=176) |

## Per-bot clones (win %, matches)

| entrant | Blueprint | Kimiko | AutodidactInnovations | SolvencyCheck | DeepStack | mr_hide | MercuryRetrograde | qwentom-leap | InfernalMonarch | PoetAndCoder |
|---|---|---|---|---|---|---|---|---|---|---|
| cand:chipzen-tip | 63.3 (60) | 91.7 (60) | 61.7 (60) | 70.0 (60) | 90.0 (60) | 71.7 (60) | 85.0 (60) | 76.7 (60) | 70.0 (60) | 66.7 (60) |
| base:lag | 53.3 (60) | 78.3 (60) | 68.3 (60) | 73.3 (60) | 73.3 (60) | 63.3 (60) | 71.7 (60) | 73.3 (60) | 66.7 (60) | 63.3 (60) |
| base:station_raiser | 55.0 (60) | 88.3 (60) | 50.0 (60) | 61.7 (60) | 85.0 (60) | 63.3 (60) | 60.0 (60) | 58.3 (60) | 61.7 (60) | 71.7 (60) |
| base:maniac | 46.7 (60) | 46.7 (60) | 40.0 (60) | 43.3 (60) | 53.3 (60) | 46.7 (60) | 48.3 (60) | 41.7 (60) | 48.3 (60) | 41.7 (60) |
| base:nit | 11.7 (60) | 88.3 (60) | 38.3 (60) | 41.7 (60) | 88.3 (60) | 50.0 (60) | 50.0 (60) | 60.0 (60) | 55.0 (60) | 38.3 (60) |
| base:random | 36.7 (60) | 48.3 (60) | 36.7 (60) | 21.7 (60) | 40.0 (60) | 43.3 (60) | 38.3 (60) | 35.0 (60) | 53.3 (60) | 30.0 (60) |
| base:reference | 8.3 (60) | 91.7 (60) | 26.7 (60) | 31.7 (60) | 70.0 (60) | 31.7 (60) | 46.7 (60) | 35.0 (60) | 30.0 (60) | 10.0 (60) |
| base:station | 16.7 (60) | 23.3 (60) | 1.7 (60) | 1.7 (60) | 23.3 (60) | 3.3 (60) | 3.3 (60) | 5.0 (60) | 3.3 (60) | 3.3 (60) |

## Head-to-head matrix (row's win % against column, matches)

| row \ col | cand:chipzen-tip | base:lag | base:station_raiser | base:maniac | base:nit | base:random | base:reference | base:station |
|---|---|---|---|---|---|---|---|---|
| cand:chipzen-tip | . | 67.5 (120) | 70.0 (120) | 75.0 (120) | 82.5 (120) | 80.8 (120) | 88.3 (120) | 95.0 (120) |
| base:lag | 32.5 (120) | . | 37.5 (240) | 52.9 (240) | 92.1 (240) | 75.8 (240) | 77.9 (240) | 85.0 (240) |
| base:station_raiser | 30.0 (120) | 62.5 (240) | . | 66.2 (240) | 37.1 (240) | 60.4 (240) | 30.8 (240) | 95.8 (240) |
| base:maniac | 25.0 (120) | 47.1 (240) | 33.8 (240) | . | 30.8 (240) | 69.6 (240) | 48.3 (240) | 50.0 (240) |
| base:nit | 17.5 (120) | 7.9 (240) | 62.9 (240) | 69.2 (240) | . | 50.8 (240) | 85.8 (240) | 93.3 (240) |
| base:random | 19.2 (120) | 24.2 (240) | 39.6 (240) | 30.4 (240) | 49.2 (240) | . | 60.8 (240) | 52.5 (240) |
| base:reference | 11.7 (120) | 22.1 (240) | 69.2 (240) | 51.7 (240) | 14.2 (240) | 39.2 (240) | . | 92.9 (240) |
| base:station | 5.0 (120) | 15.0 (240) | 4.2 (240) | 50.0 (240) | 6.7 (240) | 47.5 (240) | 7.1 (240) | . |
