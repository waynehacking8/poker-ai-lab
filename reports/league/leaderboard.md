# League leaderboard

Rank is the match-win rate against the field population (archetype win rates weighted by archetype share in rated matches), 95% bootstrap CI over duplicate pairs; ties broken by mean hands per won match (fewer is better).  Win rate is percent of matches, a tied hand cap counts half.

| # | entrant | gate | field win % [95% CI] | hands/win | bot-clone win % [95% CI] | baseline win % [95% CI] | field matches | decide ms mean/max | errors |
|---|---|---|---|---|---|---|---|---|---|
| 1 | cand:rl-distill1 | PASS 23/23 | 91.5 [90.4, 92.7] | 25.7 | 91.3 [90.4, 92.1] | 94.5 [93.6, 95.3] | 2400 | 2.1/20 | 0 |
| 2 | cand:rl-fb2-900 | PASS 23/23 | 91.2 [90.0, 92.4] | 26.2 | 91.8 [90.9, 92.6] | 94.0 [93.1, 94.8] | 2400 | 1.9/17 | 0 |
| 3 | cand:rl-fb1-900 | PASS 23/23 | 89.8 [88.5, 91.0] | 25.4 | 91.5 [90.6, 92.4] | 94.2 [93.2, 95.0] | 2400 | 1.9/16 | 0 |
| 4 | cand:rl-17cf03f | FAIL 22/23 | 89.4 [88.2, 90.7] | 27.2 | 89.0 [88.0, 89.9] | 92.5 [91.5, 93.4] | 2400 | 1.4/25 | 0 |
| 5 | cand:adapt-v2 | PASS 23/23 | 89.4 [88.1, 90.7] | 33.3 | 90.6 [89.7, 91.5] | 93.5 [92.5, 94.4] | 2400 | 7.5/73 | 0 |
| 6 | cand:rl-h4-900 | FAIL 22/23 | 88.9 [87.6, 90.2] | 27.3 | 89.7 [88.7, 90.6] | 94.2 [93.2, 95.0] | 2400 | 1.8/65 | 0 |
| 7 | cand:rl-h4-300 | PASS 23/23 | 88.8 [87.6, 90.1] | 25.0 | 89.4 [88.4, 90.3] | 93.8 [92.9, 94.7] | 2400 | 2.1/20 | 0 |
| 8 | cand:adapt-v1 | FAIL 22/23 | 86.0 [84.5, 87.4] | 20.5 | 87.7 [86.7, 88.7] | 87.8 [86.5, 88.9] | 2400 | 10.3/42 | 0 |
| 9 | cand:chipzen-102b05e | FAIL 8/23 | 76.0 [74.3, 77.7] | 31.8 | 77.5 [76.2, 78.7] | 79.1 [77.6, 80.6] | 2400 | 8.1/177 | 0 |
| 10 | base:lag | n/a (under 400 matches) 0/22 | 65.1 [60.2, 69.6] | 36.4 | 69.2 [65.4, 72.7] | 70.3 [65.4, 74.8] | 360 | -/0 | 0 |
| 11 | base:station_raiser | n/a (under 400 matches) 0/22 | 63.4 [58.4, 68.2] | 24.8 | 65.8 [61.9, 69.5] | 61.1 [56.0, 66.0] | 360 | -/0 | 0 |
| 12 | base:maniac | n/a (under 400 matches) 0/22 | 47.6 [43.0, 52.0] | 5.5 | 44.5 [40.6, 48.5] | 47.8 [42.7, 52.9] | 360 | -/0 | 0 |
| 13 | base:nit | n/a (under 400 matches) 0/22 | 43.7 [38.6, 48.9] | 74.4 | 53.0 [49.0, 57.0] | 64.2 [59.1, 68.9] | 360 | -/0 | 0 |
| 14 | base:random | n/a (under 400 matches) 0/22 | 37.1 [32.5, 41.7] | 8.1 | 39.7 [35.8, 43.6] | 46.7 [41.6, 51.8] | 360 | -/0 | 0 |
| 15 | base:reference | n/a (under 400 matches) 0/22 | 27.3 [23.2, 31.4] | 72.3 | 36.2 [32.4, 40.1] | 48.9 [43.8, 54.0] | 360 | -/0 | 0 |
| 16 | base:station | n/a (under 400 matches) 0/22 | 13.8 [10.9, 17.0] | 71.4 | 11.5 [9.2, 14.3] | 24.4 [20.3, 29.1] | 360 | -/0 | 0 |

## Gate: at least 80% over at least 400 matches, per opponent

An entrant passes an opponent when its win rate against that opponent alone is at least 80% over at least 400 matches (200 duplicate pairs); it passes the gate only if it passes every baseline, every archetype clone and every per-bot clone. The 95% Wilson lower bound over matches is shown next to the point estimate. Baseline entrants play fewer matches, so their rows read n/a. An entrant never plays itself.

### cand:rl-distill1

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 96.5 | 94.2 | 400 | PASS |
| baseline maniac | 86.0 | 82.3 | 400 | PASS |
| baseline nit | 99.8 | 98.6 | 400 | PASS |
| baseline random | 87.0 | 83.3 | 400 | PASS |
| baseline reference | 97.8 | 95.8 | 400 | PASS |
| baseline station | 97.0 | 94.8 | 400 | PASS |
| baseline station_raiser | 97.5 | 95.5 | 400 | PASS |
| archetype A0-limper-calm | 92.0 | 88.9 | 400 | PASS |
| archetype A1-station | 95.8 | 93.3 | 400 | PASS |
| archetype A2-opener-aggro-shover | 90.5 | 87.2 | 400 | PASS |
| archetype A3-opener-aggro-shover | 91.2 | 88.1 | 400 | PASS |
| archetype A4-bb-folder-calm | 92.5 | 89.5 | 400 | PASS |
| archetype A5-opener-calm | 88.0 | 84.4 | 400 | PASS |
| bot clone Blueprint | 88.5 | 85.0 | 400 | PASS |
| bot clone Kimiko | 96.2 | 93.9 | 400 | PASS |
| bot clone AutodidactInnovations | 86.8 | 83.1 | 400 | PASS |
| bot clone SolvencyCheck | 94.5 | 91.8 | 400 | PASS |
| bot clone DeepStack | 98.2 | 96.4 | 400 | PASS |
| bot clone mr_hide | 92.8 | 89.8 | 400 | PASS |
| bot clone MercuryRetrograde | 94.2 | 91.5 | 400 | PASS |
| bot clone qwentom-leap | 85.0 | 81.2 | 400 | PASS |
| bot clone InfernalMonarch | 89.0 | 85.6 | 400 | PASS |
| bot clone PoetAndCoder | 87.5 | 83.9 | 400 | PASS |

### cand:rl-fb2-900

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 95.2 | 92.7 | 400 | PASS |
| baseline maniac | 85.5 | 81.7 | 400 | PASS |
| baseline nit | 99.0 | 97.5 | 400 | PASS |
| baseline random | 88.0 | 84.4 | 400 | PASS |
| baseline reference | 97.5 | 95.5 | 400 | PASS |
| baseline station | 96.8 | 94.5 | 400 | PASS |
| baseline station_raiser | 96.0 | 93.6 | 400 | PASS |
| archetype A0-limper-calm | 93.5 | 90.6 | 400 | PASS |
| archetype A1-station | 97.8 | 95.8 | 400 | PASS |
| archetype A2-opener-aggro-shover | 85.0 | 81.2 | 400 | PASS |
| archetype A3-opener-aggro-shover | 91.8 | 88.6 | 400 | PASS |
| archetype A4-bb-folder-calm | 92.0 | 88.9 | 400 | PASS |
| archetype A5-opener-calm | 84.5 | 80.6 | 400 | PASS |
| bot clone Blueprint | 86.0 | 82.3 | 400 | PASS |
| bot clone Kimiko | 97.8 | 95.8 | 400 | PASS |
| bot clone AutodidactInnovations | 88.8 | 85.3 | 400 | PASS |
| bot clone SolvencyCheck | 92.8 | 89.8 | 400 | PASS |
| bot clone DeepStack | 97.8 | 95.8 | 400 | PASS |
| bot clone mr_hide | 93.0 | 90.1 | 400 | PASS |
| bot clone MercuryRetrograde | 95.2 | 92.7 | 400 | PASS |
| bot clone qwentom-leap | 91.2 | 88.1 | 400 | PASS |
| bot clone InfernalMonarch | 90.2 | 86.9 | 400 | PASS |
| bot clone PoetAndCoder | 85.2 | 81.4 | 400 | PASS |

### cand:rl-fb1-900

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 95.8 | 93.3 | 400 | PASS |
| baseline maniac | 87.0 | 83.3 | 400 | PASS |
| baseline nit | 99.2 | 97.8 | 400 | PASS |
| baseline random | 85.5 | 81.7 | 400 | PASS |
| baseline reference | 98.0 | 96.1 | 400 | PASS |
| baseline station | 96.8 | 94.5 | 400 | PASS |
| baseline station_raiser | 97.0 | 94.8 | 400 | PASS |
| archetype A0-limper-calm | 91.0 | 87.8 | 400 | PASS |
| archetype A1-station | 97.0 | 94.8 | 400 | PASS |
| archetype A2-opener-aggro-shover | 86.2 | 82.5 | 400 | PASS |
| archetype A3-opener-aggro-shover | 88.8 | 85.3 | 400 | PASS |
| archetype A4-bb-folder-calm | 92.0 | 88.9 | 400 | PASS |
| archetype A5-opener-calm | 83.8 | 79.8 | 400 | PASS |
| bot clone Blueprint | 86.2 | 82.5 | 400 | PASS |
| bot clone Kimiko | 97.0 | 94.8 | 400 | PASS |
| bot clone AutodidactInnovations | 89.2 | 85.8 | 400 | PASS |
| bot clone SolvencyCheck | 92.5 | 89.5 | 400 | PASS |
| bot clone DeepStack | 96.2 | 93.9 | 400 | PASS |
| bot clone mr_hide | 91.5 | 88.4 | 400 | PASS |
| bot clone MercuryRetrograde | 95.0 | 92.4 | 400 | PASS |
| bot clone qwentom-leap | 89.0 | 85.6 | 400 | PASS |
| bot clone InfernalMonarch | 92.2 | 89.2 | 400 | PASS |
| bot clone PoetAndCoder | 86.5 | 82.8 | 400 | PASS |

### cand:rl-17cf03f

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 95.2 | 92.7 | 400 | PASS |
| baseline maniac | 82.0 | 77.9 | 400 | PASS |
| baseline nit | 99.8 | 98.6 | 400 | PASS |
| baseline random | 82.8 | 78.7 | 400 | PASS |
| baseline reference | 97.8 | 95.8 | 400 | PASS |
| baseline station | 96.5 | 94.2 | 400 | PASS |
| baseline station_raiser | 93.5 | 90.6 | 400 | PASS |
| archetype A0-limper-calm | 90.8 | 87.5 | 400 | PASS |
| archetype A1-station | 95.8 | 93.3 | 400 | PASS |
| archetype A2-opener-aggro-shover | 88.5 | 85.0 | 400 | PASS |
| archetype A3-opener-aggro-shover | 86.0 | 82.3 | 400 | PASS |
| archetype A4-bb-folder-calm | 89.5 | 86.1 | 400 | PASS |
| archetype A5-opener-calm | 86.5 | 82.8 | 400 | PASS |
| bot clone Blueprint | 81.5 | 77.4 | 400 | PASS |
| bot clone Kimiko | 97.2 | 95.1 | 400 | PASS |
| bot clone AutodidactInnovations | 86.0 | 82.3 | 400 | PASS |
| bot clone SolvencyCheck | 90.0 | 86.7 | 400 | PASS |
| bot clone DeepStack | 98.0 | 96.1 | 400 | PASS |
| bot clone mr_hide | 88.0 | 84.4 | 400 | PASS |
| bot clone MercuryRetrograde | 89.5 | 86.1 | 400 | PASS |
| bot clone qwentom-leap | 89.0 | 85.6 | 400 | PASS |
| bot clone InfernalMonarch | 91.0 | 87.8 | 400 | PASS |
| bot clone PoetAndCoder | 79.5 | 75.3 | 400 | FAIL |

### cand:adapt-v2

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 93.5 | 90.6 | 400 | PASS |
| baseline maniac | 81.2 | 77.1 | 400 | PASS |
| baseline nit | 100.0 | 99.0 | 400 | PASS |
| baseline random | 87.0 | 83.3 | 400 | PASS |
| baseline reference | 99.8 | 98.6 | 400 | PASS |
| baseline station | 99.0 | 97.5 | 400 | PASS |
| baseline station_raiser | 94.0 | 91.2 | 400 | PASS |
| archetype A0-limper-calm | 91.5 | 88.4 | 400 | PASS |
| archetype A1-station | 95.2 | 92.7 | 400 | PASS |
| archetype A2-opener-aggro-shover | 88.2 | 84.7 | 400 | PASS |
| archetype A3-opener-aggro-shover | 84.2 | 80.4 | 400 | PASS |
| archetype A4-bb-folder-calm | 87.0 | 83.3 | 400 | PASS |
| archetype A5-opener-calm | 88.8 | 85.3 | 400 | PASS |
| bot clone Blueprint | 87.2 | 83.6 | 400 | PASS |
| bot clone Kimiko | 95.2 | 92.7 | 400 | PASS |
| bot clone AutodidactInnovations | 89.8 | 86.4 | 400 | PASS |
| bot clone SolvencyCheck | 80.8 | 76.6 | 400 | PASS |
| bot clone DeepStack | 95.8 | 93.3 | 400 | PASS |
| bot clone mr_hide | 91.8 | 88.6 | 400 | PASS |
| bot clone MercuryRetrograde | 94.8 | 92.1 | 400 | PASS |
| bot clone qwentom-leap | 94.2 | 91.5 | 400 | PASS |
| bot clone InfernalMonarch | 93.2 | 90.4 | 400 | PASS |
| bot clone PoetAndCoder | 83.5 | 79.5 | 400 | PASS |

### cand:rl-h4-900

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 95.5 | 93.0 | 400 | PASS |
| baseline maniac | 86.5 | 82.8 | 400 | PASS |
| baseline nit | 99.2 | 97.8 | 400 | PASS |
| baseline random | 86.0 | 82.3 | 400 | PASS |
| baseline reference | 99.0 | 97.5 | 400 | PASS |
| baseline station | 98.2 | 96.4 | 400 | PASS |
| baseline station_raiser | 94.8 | 92.1 | 400 | PASS |
| archetype A0-limper-calm | 90.0 | 86.7 | 400 | PASS |
| archetype A1-station | 96.8 | 94.5 | 400 | PASS |
| archetype A2-opener-aggro-shover | 84.8 | 80.9 | 400 | PASS |
| archetype A3-opener-aggro-shover | 90.2 | 86.9 | 400 | PASS |
| archetype A4-bb-folder-calm | 93.2 | 90.4 | 400 | PASS |
| archetype A5-opener-calm | 79.8 | 75.5 | 400 | FAIL |
| bot clone Blueprint | 80.2 | 76.1 | 400 | PASS |
| bot clone Kimiko | 96.8 | 94.5 | 400 | PASS |
| bot clone AutodidactInnovations | 86.5 | 82.8 | 400 | PASS |
| bot clone SolvencyCheck | 93.8 | 90.9 | 400 | PASS |
| bot clone DeepStack | 95.8 | 93.3 | 400 | PASS |
| bot clone mr_hide | 91.2 | 88.1 | 400 | PASS |
| bot clone MercuryRetrograde | 91.2 | 88.1 | 400 | PASS |
| bot clone qwentom-leap | 86.5 | 82.8 | 400 | PASS |
| bot clone InfernalMonarch | 89.2 | 85.8 | 400 | PASS |
| bot clone PoetAndCoder | 86.0 | 82.3 | 400 | PASS |

### cand:rl-h4-300

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 96.2 | 93.9 | 400 | PASS |
| baseline maniac | 87.2 | 83.6 | 400 | PASS |
| baseline nit | 99.2 | 97.8 | 400 | PASS |
| baseline random | 86.5 | 82.8 | 400 | PASS |
| baseline reference | 97.8 | 95.8 | 400 | PASS |
| baseline station | 97.2 | 95.1 | 400 | PASS |
| baseline station_raiser | 92.5 | 89.5 | 400 | PASS |
| archetype A0-limper-calm | 90.2 | 86.9 | 400 | PASS |
| archetype A1-station | 96.0 | 93.6 | 400 | PASS |
| archetype A2-opener-aggro-shover | 85.5 | 81.7 | 400 | PASS |
| archetype A3-opener-aggro-shover | 87.8 | 84.2 | 400 | PASS |
| archetype A4-bb-folder-calm | 89.5 | 86.1 | 400 | PASS |
| archetype A5-opener-calm | 83.2 | 79.3 | 400 | PASS |
| bot clone Blueprint | 85.2 | 81.4 | 400 | PASS |
| bot clone Kimiko | 95.8 | 93.3 | 400 | PASS |
| bot clone AutodidactInnovations | 85.8 | 82.0 | 400 | PASS |
| bot clone SolvencyCheck | 90.5 | 87.2 | 400 | PASS |
| bot clone DeepStack | 95.0 | 92.4 | 400 | PASS |
| bot clone mr_hide | 90.2 | 86.9 | 400 | PASS |
| bot clone MercuryRetrograde | 91.8 | 88.6 | 400 | PASS |
| bot clone qwentom-leap | 86.5 | 82.8 | 400 | PASS |
| bot clone InfernalMonarch | 86.2 | 82.5 | 400 | PASS |
| bot clone PoetAndCoder | 87.2 | 83.6 | 400 | PASS |

### cand:adapt-v1

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 82.5 | 78.5 | 400 | PASS |
| baseline maniac | 74.5 | 70.0 | 400 | FAIL |
| baseline nit | 99.5 | 98.2 | 400 | PASS |
| baseline random | 80.2 | 76.1 | 400 | PASS |
| baseline reference | 98.5 | 96.8 | 400 | PASS |
| baseline station | 93.8 | 90.9 | 400 | PASS |
| baseline station_raiser | 85.2 | 81.4 | 400 | PASS |
| archetype A0-limper-calm | 85.2 | 81.4 | 400 | PASS |
| archetype A1-station | 92.2 | 89.2 | 400 | PASS |
| archetype A2-opener-aggro-shover | 84.2 | 80.4 | 400 | PASS |
| archetype A3-opener-aggro-shover | 86.2 | 82.5 | 400 | PASS |
| archetype A4-bb-folder-calm | 87.2 | 83.6 | 400 | PASS |
| archetype A5-opener-calm | 81.8 | 77.7 | 400 | PASS |
| bot clone Blueprint | 81.5 | 77.4 | 400 | PASS |
| bot clone Kimiko | 93.0 | 90.1 | 400 | PASS |
| bot clone AutodidactInnovations | 84.2 | 80.4 | 400 | PASS |
| bot clone SolvencyCheck | 88.2 | 84.7 | 400 | PASS |
| bot clone DeepStack | 94.0 | 91.2 | 400 | PASS |
| bot clone mr_hide | 88.0 | 84.4 | 400 | PASS |
| bot clone MercuryRetrograde | 88.5 | 85.0 | 400 | PASS |
| bot clone qwentom-leap | 88.8 | 85.3 | 400 | PASS |
| bot clone InfernalMonarch | 85.5 | 81.7 | 400 | PASS |
| bot clone PoetAndCoder | 85.5 | 81.7 | 400 | PASS |

### cand:chipzen-102b05e

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 67.2 | 62.5 | 400 | FAIL |
| baseline maniac | 74.0 | 69.5 | 400 | FAIL |
| baseline nit | 85.5 | 81.7 | 400 | PASS |
| baseline random | 79.2 | 75.0 | 400 | FAIL |
| baseline reference | 86.2 | 82.5 | 400 | PASS |
| baseline station | 95.5 | 93.0 | 400 | PASS |
| baseline station_raiser | 66.0 | 61.2 | 400 | FAIL |
| archetype A0-limper-calm | 81.0 | 76.9 | 400 | PASS |
| archetype A1-station | 90.5 | 87.2 | 400 | PASS |
| archetype A2-opener-aggro-shover | 67.5 | 62.8 | 400 | FAIL |
| archetype A3-opener-aggro-shover | 74.2 | 69.7 | 400 | FAIL |
| archetype A4-bb-folder-calm | 74.2 | 69.7 | 400 | FAIL |
| archetype A5-opener-calm | 64.0 | 59.2 | 400 | FAIL |
| bot clone Blueprint | 64.5 | 59.7 | 400 | FAIL |
| bot clone Kimiko | 92.8 | 89.8 | 400 | PASS |
| bot clone AutodidactInnovations | 69.8 | 65.1 | 400 | FAIL |
| bot clone SolvencyCheck | 74.2 | 69.7 | 400 | FAIL |
| bot clone DeepStack | 90.8 | 87.5 | 400 | PASS |
| bot clone mr_hide | 78.8 | 74.5 | 400 | FAIL |
| bot clone MercuryRetrograde | 77.5 | 73.2 | 400 | FAIL |
| bot clone qwentom-leap | 80.0 | 75.8 | 400 | PASS |
| bot clone InfernalMonarch | 74.0 | 69.5 | 400 | FAIL |
| bot clone PoetAndCoder | 72.5 | 67.9 | 400 | FAIL |

### base:lag

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline maniac | 51.7 | 39.3 | 60 | n/a |
| baseline nit | 93.3 | 84.1 | 60 | n/a |
| baseline random | 76.7 | 64.6 | 60 | n/a |
| baseline reference | 85.0 | 73.9 | 60 | n/a |
| baseline station | 80.0 | 68.2 | 60 | n/a |
| baseline station_raiser | 35.0 | 24.2 | 60 | n/a |
| archetype A0-limper-calm | 70.0 | 57.5 | 60 | n/a |
| archetype A1-station | 76.7 | 64.6 | 60 | n/a |
| archetype A2-opener-aggro-shover | 58.3 | 45.7 | 60 | n/a |
| archetype A3-opener-aggro-shover | 63.3 | 50.7 | 60 | n/a |
| archetype A4-bb-folder-calm | 63.3 | 50.7 | 60 | n/a |
| archetype A5-opener-calm | 55.0 | 42.5 | 60 | n/a |
| bot clone Blueprint | 60.0 | 47.4 | 60 | n/a |
| bot clone Kimiko | 80.0 | 68.2 | 60 | n/a |
| bot clone AutodidactInnovations | 68.3 | 55.8 | 60 | n/a |
| bot clone SolvencyCheck | 75.0 | 62.8 | 60 | n/a |
| bot clone DeepStack | 73.3 | 61.0 | 60 | n/a |
| bot clone mr_hide | 76.7 | 64.6 | 60 | n/a |
| bot clone MercuryRetrograde | 65.0 | 52.4 | 60 | n/a |
| bot clone qwentom-leap | 68.3 | 55.8 | 60 | n/a |
| bot clone InfernalMonarch | 65.0 | 52.4 | 60 | n/a |
| bot clone PoetAndCoder | 60.0 | 47.4 | 60 | n/a |

### base:station_raiser

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 68.3 | 55.8 | 60 | n/a |
| baseline maniac | 63.3 | 50.7 | 60 | n/a |
| baseline nit | 45.0 | 33.1 | 60 | n/a |
| baseline random | 60.0 | 47.4 | 60 | n/a |
| baseline reference | 36.7 | 25.6 | 60 | n/a |
| baseline station | 93.3 | 84.1 | 60 | n/a |
| archetype A0-limper-calm | 73.3 | 61.0 | 60 | n/a |
| archetype A1-station | 83.3 | 72.0 | 60 | n/a |
| archetype A2-opener-aggro-shover | 53.3 | 40.9 | 60 | n/a |
| archetype A3-opener-aggro-shover | 55.0 | 42.5 | 60 | n/a |
| archetype A4-bb-folder-calm | 50.0 | 37.7 | 60 | n/a |
| archetype A5-opener-calm | 53.3 | 40.9 | 60 | n/a |
| bot clone Blueprint | 58.3 | 45.7 | 60 | n/a |
| bot clone Kimiko | 88.3 | 77.8 | 60 | n/a |
| bot clone AutodidactInnovations | 55.0 | 42.5 | 60 | n/a |
| bot clone SolvencyCheck | 56.7 | 44.1 | 60 | n/a |
| bot clone DeepStack | 88.3 | 77.8 | 60 | n/a |
| bot clone mr_hide | 73.3 | 61.0 | 60 | n/a |
| bot clone MercuryRetrograde | 51.7 | 39.3 | 60 | n/a |
| bot clone qwentom-leap | 61.7 | 49.0 | 60 | n/a |
| bot clone InfernalMonarch | 60.0 | 47.4 | 60 | n/a |
| bot clone PoetAndCoder | 65.0 | 52.4 | 60 | n/a |

### base:maniac

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 38.3 | 27.1 | 60 | n/a |
| baseline nit | 35.0 | 24.2 | 60 | n/a |
| baseline random | 70.0 | 57.5 | 60 | n/a |
| baseline reference | 58.3 | 45.7 | 60 | n/a |
| baseline station | 50.0 | 37.7 | 60 | n/a |
| baseline station_raiser | 35.0 | 24.2 | 60 | n/a |
| archetype A0-limper-calm | 43.3 | 31.6 | 60 | n/a |
| archetype A1-station | 51.7 | 39.3 | 60 | n/a |
| archetype A2-opener-aggro-shover | 53.3 | 40.9 | 60 | n/a |
| archetype A3-opener-aggro-shover | 50.0 | 37.7 | 60 | n/a |
| archetype A4-bb-folder-calm | 38.3 | 27.1 | 60 | n/a |
| archetype A5-opener-calm | 50.0 | 37.7 | 60 | n/a |
| bot clone Blueprint | 40.0 | 28.6 | 60 | n/a |
| bot clone Kimiko | 48.3 | 36.2 | 60 | n/a |
| bot clone AutodidactInnovations | 33.3 | 22.7 | 60 | n/a |
| bot clone SolvencyCheck | 38.3 | 27.1 | 60 | n/a |
| bot clone DeepStack | 50.0 | 37.7 | 60 | n/a |
| bot clone mr_hide | 43.3 | 31.6 | 60 | n/a |
| bot clone MercuryRetrograde | 45.0 | 33.1 | 60 | n/a |
| bot clone qwentom-leap | 45.0 | 33.1 | 60 | n/a |
| bot clone InfernalMonarch | 58.3 | 45.7 | 60 | n/a |
| bot clone PoetAndCoder | 43.3 | 31.6 | 60 | n/a |

### base:nit

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 13.3 | 6.9 | 60 | n/a |
| baseline maniac | 71.7 | 59.2 | 60 | n/a |
| baseline random | 53.3 | 40.9 | 60 | n/a |
| baseline reference | 93.3 | 84.1 | 60 | n/a |
| baseline station | 95.0 | 86.3 | 60 | n/a |
| baseline station_raiser | 58.3 | 45.7 | 60 | n/a |
| archetype A0-limper-calm | 53.3 | 40.9 | 60 | n/a |
| archetype A1-station | 90.0 | 79.9 | 60 | n/a |
| archetype A2-opener-aggro-shover | 15.0 | 8.1 | 60 | n/a |
| archetype A3-opener-aggro-shover | 28.3 | 18.5 | 60 | n/a |
| archetype A4-bb-folder-calm | 46.7 | 34.6 | 60 | n/a |
| archetype A5-opener-calm | 18.3 | 10.6 | 60 | n/a |
| bot clone Blueprint | 11.7 | 5.8 | 60 | n/a |
| bot clone Kimiko | 88.3 | 77.8 | 60 | n/a |
| bot clone AutodidactInnovations | 40.0 | 28.6 | 60 | n/a |
| bot clone SolvencyCheck | 51.7 | 39.3 | 60 | n/a |
| bot clone DeepStack | 86.7 | 75.8 | 60 | n/a |
| bot clone mr_hide | 46.7 | 34.6 | 60 | n/a |
| bot clone MercuryRetrograde | 51.7 | 39.3 | 60 | n/a |
| bot clone qwentom-leap | 66.7 | 54.1 | 60 | n/a |
| bot clone InfernalMonarch | 51.7 | 39.3 | 60 | n/a |
| bot clone PoetAndCoder | 35.0 | 24.2 | 60 | n/a |

### base:random

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 23.3 | 14.4 | 60 | n/a |
| baseline maniac | 35.0 | 24.2 | 60 | n/a |
| baseline nit | 53.3 | 40.9 | 60 | n/a |
| baseline reference | 68.3 | 55.8 | 60 | n/a |
| baseline station | 51.7 | 39.3 | 60 | n/a |
| baseline station_raiser | 48.3 | 36.2 | 60 | n/a |
| archetype A0-limper-calm | 45.0 | 33.1 | 60 | n/a |
| archetype A1-station | 40.0 | 28.6 | 60 | n/a |
| archetype A2-opener-aggro-shover | 26.7 | 17.1 | 60 | n/a |
| archetype A3-opener-aggro-shover | 38.3 | 27.1 | 60 | n/a |
| archetype A4-bb-folder-calm | 41.7 | 30.1 | 60 | n/a |
| archetype A5-opener-calm | 25.0 | 15.8 | 60 | n/a |
| bot clone Blueprint | 43.3 | 31.6 | 60 | n/a |
| bot clone Kimiko | 53.3 | 40.9 | 60 | n/a |
| bot clone AutodidactInnovations | 41.7 | 30.1 | 60 | n/a |
| bot clone SolvencyCheck | 20.0 | 11.8 | 60 | n/a |
| bot clone DeepStack | 40.0 | 28.6 | 60 | n/a |
| bot clone mr_hide | 48.3 | 36.2 | 60 | n/a |
| bot clone MercuryRetrograde | 40.0 | 28.6 | 60 | n/a |
| bot clone qwentom-leap | 33.3 | 22.7 | 60 | n/a |
| bot clone InfernalMonarch | 46.7 | 34.6 | 60 | n/a |
| bot clone PoetAndCoder | 30.0 | 19.9 | 60 | n/a |

### base:reference

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 23.3 | 14.4 | 60 | n/a |
| baseline maniac | 51.7 | 39.3 | 60 | n/a |
| baseline nit | 16.7 | 9.3 | 60 | n/a |
| baseline random | 36.7 | 25.6 | 60 | n/a |
| baseline station | 93.3 | 84.1 | 60 | n/a |
| baseline station_raiser | 71.7 | 59.2 | 60 | n/a |
| archetype A0-limper-calm | 30.0 | 19.9 | 60 | n/a |
| archetype A1-station | 78.3 | 66.4 | 60 | n/a |
| archetype A2-opener-aggro-shover | 6.7 | 2.6 | 60 | n/a |
| archetype A3-opener-aggro-shover | 13.3 | 6.9 | 60 | n/a |
| archetype A4-bb-folder-calm | 30.0 | 19.9 | 60 | n/a |
| archetype A5-opener-calm | 3.3 | 0.9 | 60 | n/a |
| bot clone Blueprint | 1.7 | 0.3 | 60 | n/a |
| bot clone Kimiko | 90.0 | 79.9 | 60 | n/a |
| bot clone AutodidactInnovations | 25.0 | 15.8 | 60 | n/a |
| bot clone SolvencyCheck | 18.3 | 10.6 | 60 | n/a |
| bot clone DeepStack | 70.0 | 57.5 | 60 | n/a |
| bot clone mr_hide | 25.0 | 15.8 | 60 | n/a |
| bot clone MercuryRetrograde | 46.7 | 34.6 | 60 | n/a |
| bot clone qwentom-leap | 41.7 | 30.1 | 60 | n/a |
| bot clone InfernalMonarch | 28.3 | 18.5 | 60 | n/a |
| bot clone PoetAndCoder | 15.0 | 8.1 | 60 | n/a |

### base:station

| opponent | win % | 95% lower bound | matches | result |
|---|---|---|---|---|
| baseline lag | 21.7 | 13.1 | 60 | n/a |
| baseline maniac | 50.0 | 37.7 | 60 | n/a |
| baseline nit | 8.3 | 3.6 | 60 | n/a |
| baseline random | 50.0 | 37.7 | 60 | n/a |
| baseline reference | 13.3 | 6.9 | 60 | n/a |
| baseline station_raiser | 3.3 | 0.9 | 60 | n/a |
| archetype A0-limper-calm | 10.0 | 4.7 | 60 | n/a |
| archetype A1-station | 33.3 | 22.7 | 60 | n/a |
| archetype A2-opener-aggro-shover | 20.0 | 11.8 | 60 | n/a |
| archetype A3-opener-aggro-shover | 6.7 | 2.6 | 60 | n/a |
| archetype A4-bb-folder-calm | 0.0 | -0.0 | 60 | n/a |
| archetype A5-opener-calm | 15.0 | 8.1 | 60 | n/a |
| bot clone Blueprint | 25.0 | 15.8 | 60 | n/a |
| bot clone Kimiko | 35.0 | 24.2 | 60 | n/a |
| bot clone AutodidactInnovations | 1.7 | 0.3 | 60 | n/a |
| bot clone SolvencyCheck | 0.0 | -0.0 | 60 | n/a |
| bot clone DeepStack | 33.3 | 22.7 | 60 | n/a |
| bot clone mr_hide | 5.0 | 1.7 | 60 | n/a |
| bot clone MercuryRetrograde | 3.3 | 0.9 | 60 | n/a |
| bot clone qwentom-leap | 5.0 | 1.7 | 60 | n/a |
| bot clone InfernalMonarch | 3.3 | 0.9 | 60 | n/a |
| bot clone PoetAndCoder | 3.3 | 0.9 | 60 | n/a |

## Field population

Archetype shares (rated participants): A0-limper-calm 26%, A1-station 16%, A2-opener-aggro-shover 6%, A3-opener-aggro-shover 20%, A4-bb-folder-calm 10%, A5-opener-calm 22%

| entrant | A0-limper-calm | A1-station | A2-opener-aggro-shover | A3-opener-aggro-shover | A4-bb-folder-calm | A5-opener-calm |
|---|---|---|---|---|---|---|
| cand:rl-distill1 | 92.0 (n=400) | 95.8 (n=400) | 90.5 (n=400) | 91.2 (n=400) | 92.5 (n=400) | 88.0 (n=400) |
| cand:rl-fb2-900 | 93.5 (n=400) | 97.8 (n=400) | 85.0 (n=400) | 91.8 (n=400) | 92.0 (n=400) | 84.5 (n=400) |
| cand:rl-fb1-900 | 91.0 (n=400) | 97.0 (n=400) | 86.2 (n=400) | 88.8 (n=400) | 92.0 (n=400) | 83.8 (n=400) |
| cand:rl-17cf03f | 90.8 (n=400) | 95.8 (n=400) | 88.5 (n=400) | 86.0 (n=400) | 89.5 (n=400) | 86.5 (n=400) |
| cand:adapt-v2 | 91.5 (n=400) | 95.2 (n=400) | 88.2 (n=400) | 84.2 (n=400) | 87.0 (n=400) | 88.8 (n=400) |
| cand:rl-h4-900 | 90.0 (n=400) | 96.8 (n=400) | 84.8 (n=400) | 90.2 (n=400) | 93.2 (n=400) | 79.8 (n=400) |
| cand:rl-h4-300 | 90.2 (n=400) | 96.0 (n=400) | 85.5 (n=400) | 87.8 (n=400) | 89.5 (n=400) | 83.2 (n=400) |
| cand:adapt-v1 | 85.2 (n=400) | 92.2 (n=400) | 84.2 (n=400) | 86.2 (n=400) | 87.2 (n=400) | 81.8 (n=400) |
| cand:chipzen-102b05e | 81.0 (n=400) | 90.5 (n=400) | 67.5 (n=400) | 74.2 (n=400) | 74.2 (n=400) | 64.0 (n=400) |
| base:lag | 70.0 (n=60) | 76.7 (n=60) | 58.3 (n=60) | 63.3 (n=60) | 63.3 (n=60) | 55.0 (n=60) |
| base:station_raiser | 73.3 (n=60) | 83.3 (n=60) | 53.3 (n=60) | 55.0 (n=60) | 50.0 (n=60) | 53.3 (n=60) |
| base:maniac | 43.3 (n=60) | 51.7 (n=60) | 53.3 (n=60) | 50.0 (n=60) | 38.3 (n=60) | 50.0 (n=60) |
| base:nit | 53.3 (n=60) | 90.0 (n=60) | 15.0 (n=60) | 28.3 (n=60) | 46.7 (n=60) | 18.3 (n=60) |
| base:random | 45.0 (n=60) | 40.0 (n=60) | 26.7 (n=60) | 38.3 (n=60) | 41.7 (n=60) | 25.0 (n=60) |
| base:reference | 30.0 (n=60) | 78.3 (n=60) | 6.7 (n=60) | 13.3 (n=60) | 30.0 (n=60) | 3.3 (n=60) |
| base:station | 10.0 (n=60) | 33.3 (n=60) | 20.0 (n=60) | 6.7 (n=60) | 0.0 (n=60) | 15.0 (n=60) |

## Per-bot clones (win %, matches)

| entrant | Blueprint | Kimiko | AutodidactInnovations | SolvencyCheck | DeepStack | mr_hide | MercuryRetrograde | qwentom-leap | InfernalMonarch | PoetAndCoder |
|---|---|---|---|---|---|---|---|---|---|---|
| cand:rl-distill1 | 88.5 (400) | 96.2 (400) | 86.8 (400) | 94.5 (400) | 98.2 (400) | 92.8 (400) | 94.2 (400) | 85.0 (400) | 89.0 (400) | 87.5 (400) |
| cand:rl-fb2-900 | 86.0 (400) | 97.8 (400) | 88.8 (400) | 92.8 (400) | 97.8 (400) | 93.0 (400) | 95.2 (400) | 91.2 (400) | 90.2 (400) | 85.2 (400) |
| cand:rl-fb1-900 | 86.2 (400) | 97.0 (400) | 89.2 (400) | 92.5 (400) | 96.2 (400) | 91.5 (400) | 95.0 (400) | 89.0 (400) | 92.2 (400) | 86.5 (400) |
| cand:rl-17cf03f | 81.5 (400) | 97.2 (400) | 86.0 (400) | 90.0 (400) | 98.0 (400) | 88.0 (400) | 89.5 (400) | 89.0 (400) | 91.0 (400) | 79.5 (400) |
| cand:adapt-v2 | 87.2 (400) | 95.2 (400) | 89.8 (400) | 80.8 (400) | 95.8 (400) | 91.8 (400) | 94.8 (400) | 94.2 (400) | 93.2 (400) | 83.5 (400) |
| cand:rl-h4-900 | 80.2 (400) | 96.8 (400) | 86.5 (400) | 93.8 (400) | 95.8 (400) | 91.2 (400) | 91.2 (400) | 86.5 (400) | 89.2 (400) | 86.0 (400) |
| cand:rl-h4-300 | 85.2 (400) | 95.8 (400) | 85.8 (400) | 90.5 (400) | 95.0 (400) | 90.2 (400) | 91.8 (400) | 86.5 (400) | 86.2 (400) | 87.2 (400) |
| cand:adapt-v1 | 81.5 (400) | 93.0 (400) | 84.2 (400) | 88.2 (400) | 94.0 (400) | 88.0 (400) | 88.5 (400) | 88.8 (400) | 85.5 (400) | 85.5 (400) |
| cand:chipzen-102b05e | 64.5 (400) | 92.8 (400) | 69.8 (400) | 74.2 (400) | 90.8 (400) | 78.8 (400) | 77.5 (400) | 80.0 (400) | 74.0 (400) | 72.5 (400) |
| base:lag | 60.0 (60) | 80.0 (60) | 68.3 (60) | 75.0 (60) | 73.3 (60) | 76.7 (60) | 65.0 (60) | 68.3 (60) | 65.0 (60) | 60.0 (60) |
| base:station_raiser | 58.3 (60) | 88.3 (60) | 55.0 (60) | 56.7 (60) | 88.3 (60) | 73.3 (60) | 51.7 (60) | 61.7 (60) | 60.0 (60) | 65.0 (60) |
| base:maniac | 40.0 (60) | 48.3 (60) | 33.3 (60) | 38.3 (60) | 50.0 (60) | 43.3 (60) | 45.0 (60) | 45.0 (60) | 58.3 (60) | 43.3 (60) |
| base:nit | 11.7 (60) | 88.3 (60) | 40.0 (60) | 51.7 (60) | 86.7 (60) | 46.7 (60) | 51.7 (60) | 66.7 (60) | 51.7 (60) | 35.0 (60) |
| base:random | 43.3 (60) | 53.3 (60) | 41.7 (60) | 20.0 (60) | 40.0 (60) | 48.3 (60) | 40.0 (60) | 33.3 (60) | 46.7 (60) | 30.0 (60) |
| base:reference | 1.7 (60) | 90.0 (60) | 25.0 (60) | 18.3 (60) | 70.0 (60) | 25.0 (60) | 46.7 (60) | 41.7 (60) | 28.3 (60) | 15.0 (60) |
| base:station | 25.0 (60) | 35.0 (60) | 1.7 (60) | 0.0 (60) | 33.3 (60) | 5.0 (60) | 3.3 (60) | 5.0 (60) | 3.3 (60) | 3.3 (60) |

## Head-to-head matrix (row's win % against column, matches)

| row \ col | cand:rl-distill1 | cand:rl-fb2-900 | cand:rl-fb1-900 | cand:rl-17cf03f | cand:adapt-v2 | cand:rl-h4-900 | cand:rl-h4-300 | cand:adapt-v1 | cand:chipzen-102b05e | base:lag | base:station_raiser | base:maniac | base:nit | base:random | base:reference | base:station |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cand:rl-distill1 | . | 44.8 (400) | 50.5 (400) | 48.5 (200) | 63.0 (200) | 36.5 (200) | 32.8 (400) | 65.0 (200) | 43.0 (200) | 96.5 (400) | 97.5 (400) | 86.0 (400) | 99.8 (400) | 87.0 (400) | 97.8 (400) | 97.0 (400) |
| cand:rl-fb2-900 | 55.2 (400) | . | 49.2 (400) | 55.2 (400) | 57.5 (400) | 46.0 (400) | 48.0 (400) | 62.0 (400) | 66.2 (400) | 95.2 (400) | 96.0 (400) | 85.5 (400) | 99.0 (400) | 88.0 (400) | 97.5 (400) | 96.8 (400) |
| cand:rl-fb1-900 | 49.5 (400) | 50.7 (400) | . | 60.0 (400) | 62.7 (400) | 45.0 (400) | 47.2 (400) | 59.2 (400) | 64.0 (400) | 95.8 (400) | 97.0 (400) | 87.0 (400) | 99.2 (400) | 85.5 (400) | 98.0 (400) | 96.8 (400) |
| cand:rl-17cf03f | 51.5 (200) | 44.8 (400) | 40.0 (400) | . | 53.0 (200) | 45.5 (200) | 52.8 (400) | 57.5 (200) | 48.0 (200) | 95.2 (400) | 93.5 (400) | 82.0 (400) | 99.8 (400) | 82.8 (400) | 97.8 (400) | 96.5 (400) |
| cand:adapt-v2 | 37.0 (200) | 42.5 (400) | 37.2 (400) | 47.0 (200) | . | 38.0 (200) | 37.5 (400) | 59.0 (200) | 29.5 (200) | 93.5 (400) | 94.0 (400) | 81.2 (400) | 100.0 (400) | 87.0 (400) | 99.8 (400) | 99.0 (400) |
| cand:rl-h4-900 | 63.5 (200) | 54.0 (400) | 55.0 (400) | 54.5 (200) | 62.0 (200) | . | 60.5 (200) | 59.0 (200) | 72.0 (200) | 95.5 (400) | 94.8 (400) | 86.5 (400) | 99.2 (400) | 86.0 (400) | 99.0 (400) | 98.2 (400) |
| cand:rl-h4-300 | 67.2 (400) | 52.0 (400) | 52.8 (400) | 47.2 (400) | 62.5 (400) | 39.5 (200) | . | 67.0 (400) | 69.8 (400) | 96.2 (400) | 92.5 (400) | 87.2 (400) | 99.2 (400) | 86.5 (400) | 97.8 (400) | 97.2 (400) |
| cand:adapt-v1 | 35.0 (200) | 38.0 (400) | 40.8 (400) | 42.5 (200) | 41.0 (200) | 41.0 (200) | 33.0 (400) | . | 39.0 (200) | 82.5 (400) | 85.2 (400) | 74.5 (400) | 99.5 (400) | 80.2 (400) | 98.5 (400) | 93.8 (400) |
| cand:chipzen-102b05e | 57.0 (200) | 33.8 (400) | 36.0 (400) | 52.0 (200) | 70.5 (200) | 28.0 (200) | 30.2 (400) | 61.0 (200) | . | 67.2 (400) | 66.0 (400) | 74.0 (400) | 85.5 (400) | 79.2 (400) | 86.2 (400) | 95.5 (400) |
| base:lag | 3.5 (400) | 4.8 (400) | 4.2 (400) | 4.8 (400) | 6.5 (400) | 4.5 (400) | 3.8 (400) | 17.5 (400) | 32.8 (400) | . | 33.3 (120) | 56.7 (120) | 90.0 (120) | 76.7 (120) | 80.8 (120) | 79.2 (120) |
| base:station_raiser | 2.5 (400) | 4.0 (400) | 3.0 (400) | 6.5 (400) | 6.0 (400) | 5.2 (400) | 7.5 (400) | 14.8 (400) | 34.0 (400) | 66.7 (120) | . | 64.2 (120) | 43.3 (120) | 55.8 (120) | 32.5 (120) | 95.0 (120) |
| base:maniac | 14.0 (400) | 14.5 (400) | 13.0 (400) | 18.0 (400) | 18.8 (400) | 13.5 (400) | 12.8 (400) | 25.5 (400) | 26.0 (400) | 43.3 (120) | 35.8 (120) | . | 31.7 (120) | 67.5 (120) | 53.3 (120) | 50.0 (120) |
| base:nit | 0.2 (400) | 1.0 (400) | 0.8 (400) | 0.2 (400) | 0.0 (400) | 0.8 (400) | 0.8 (400) | 0.5 (400) | 14.5 (400) | 10.0 (120) | 56.7 (120) | 68.3 (120) | . | 50.0 (120) | 88.3 (120) | 93.3 (120) |
| base:random | 13.0 (400) | 12.0 (400) | 14.5 (400) | 17.2 (400) | 13.0 (400) | 14.0 (400) | 13.5 (400) | 19.8 (400) | 20.8 (400) | 23.3 (120) | 44.2 (120) | 32.5 (120) | 50.0 (120) | . | 65.8 (120) | 50.8 (120) |
| base:reference | 2.2 (400) | 2.5 (400) | 2.0 (400) | 2.2 (400) | 0.2 (400) | 1.0 (400) | 2.2 (400) | 1.5 (400) | 13.8 (400) | 19.2 (120) | 67.5 (120) | 46.7 (120) | 11.7 (120) | 34.2 (120) | . | 90.0 (120) |
| base:station | 3.0 (400) | 3.2 (400) | 3.2 (400) | 3.5 (400) | 1.0 (400) | 1.8 (400) | 2.8 (400) | 6.2 (400) | 4.5 (400) | 20.8 (120) | 5.0 (120) | 50.0 (120) | 6.7 (120) | 49.2 (120) | 10.0 (120) | . |
