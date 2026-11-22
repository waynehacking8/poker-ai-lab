# Field bots: real Chipzen bots as opponents

Third-party Chipzen bots with public source, vendored and reviewed, playable as `ext:<name>` in `rl.eval_arena`,
`rl.sdk_rollout` and `rl.train --sdk-opps`. Run on gb10-d only. Match format as everywhere in the SDK arena: 10000
stacks, blinds 50/100 rising every 20 hands, heads up, winner takes all, duplicate seeds and both seats.

## Safety record

Each source is pinned to a commit and read before it ran (`rl/field_bots/vendor/<name>/PROVENANCE.md`: URL, SHA, license,
fetch date, files, every patch). `python tools/check_vendor.py` fails on any import outside the allowed set, any use of
os, sys, subprocess, socket, urllib, http, requests, pickle, marshal, ctypes, importlib, open, eval, exec, compile or
`__import__`, and scans the JavaScript for require, fs, net, child_process, http(s), eval and dynamic import. The
vendor tree is rebuilt from the clones by `python tools/vendor_build.py --src <clones> --sha ...`, each patch an exact
string replace that must match once. Nothing was sent to chipzen.ai or any network service. The JavaScript bot runs
only in `docker run --network none --read-only --cap-drop ALL --memory 256m --cpus 1` with the code mounted read-only.

## Results (400 matches, seed 3, hero win rate, Wilson 95%)

Column "h4-300 beats it": hero is `rl/models/h4_it000300.npz`. Column "heuristic bot beats it": hero is the old
`HoldemBot` (`--hero chipzen`). Smoke columns: 50 matches each against `random` and `lag` (both seats), worst case of the two.
The p99 and max for the wolf rows include the node container start inside the first decision of each match.

| bot | h4-300 beats it (400 matches) | heuristic bot beats it | smoke p99 ms | smoke max ms | exceptions | illegal |
|---|---|---|---|---|---|---|
| ext:sdkref | 98.0% [96.1, 99.0] | 89.2% [85.8, 91.9] | 0 | 0 | 0 | 0 |
| ext:ashwing_v2 | 63.0% [58.2, 67.6] | 58.2% [53.4, 63.0] | 45 | 53 | 0 | 0 |
| ext:ashwing_hive | 58.8% [53.9, 63.5] | 59.0% [54.1, 63.7] | 45 | 52 | 0 | 0 |
| ext:ashwing_value | 75.0% [70.5, 79.0] | 66.0% [61.2, 70.5] | 6 | 6 | 0 | 0 |
| ext:ashwing_adaptive | 59.8% [54.9, 64.4] | 57.8% [52.9, 62.5] | 45 | 53 | 0 | 0 |
| ext:ashwing_search | 49.2% [44.4, 54.1] | 57.0% [52.1, 61.8] | 45 | 51 | 0 | 0 |
| ext:ashwing | 55.2% [50.4, 60.0] | 58.8% [53.9, 63.5] | 45 | 88 | 0 | 0 |
| ext:autodidact | 63.7% [58.9, 68.3] | 63.7% [58.9, 68.3] | 491 | 658 | 0 | 0 |
| ext:autodidact_fast | 58.8% [53.9, 63.5] | 64.8% [59.9, 69.3] | 74 | 166 | 0 | 0 |
| ext:wolf | 84.0% [80.1, 87.3] | 68.0% [63.3, 72.4] | 279 | 315 | 0 | 0 |
| ext:wolf_v5 | 84.0% [80.1, 87.3] | 67.8% [63.0, 72.1] | 277 | 302 | 0 | 0 |
| ext:wolf_v2 | 88.0% [84.4, 90.8] | 68.5% [63.8, 72.9] | 286 | 316 | 0 | 0 |
| ext:wolf_v1 | 90.0% [86.7, 92.6] | 73.2% [68.7, 77.4] | 272 | 309 | 0 | 0 |

Rows are in registry order. `ext:wolf` and `ext:wolf_v5` are distinct engines (the current one adds an aggression
weighted equity); they happen to land on the same win count here.

## Dropped bots

None. Every registered bot completed 50 smoke matches against each baseline with 0 exceptions and 0 illegal or
auto-corrected actions, and every p99 is under 1 s. Slowest is `ext:autodidact` at about 300 ms mean and 491 ms p99
(2000 Monte Carlo trials per decision), which makes 400 matches cost about 37 minutes on 4 workers; it is too slow for
training, so `ext:autodidact_fast` (identical code, 200 and 150 trials) is the one to put in `--sdk-opps`.
Skipped by instruction: matteo-psnt/poker-solver, elcoosp/*, robopoker (no public strategy artifacts) and G5 (C#).

## What the numbers say

* `h4-300` is not dominant against the real code. It beats the Ashwing family only 49 to 63% (95% interval for
  `ashwing_search` includes 50%), `autodidact` 64%, while it beats `wolf` 84 to 90% and the SDK reference bot 98%.
* Against the Ashwing bots the old heuristic bot scores 57 to 59%, the same as `h4-300` within noise, so on this
  family the RL policy shows no edge over the heuristic.
* `ashwing_value` (plain Value profile) is the easiest Ashwing policy; the range inference variants (hive, adaptive,
  search, full) are harder. `ashwing_v2` is the live Chipzen entry.
* Matches are short (about 14 to 37 hands for the strong bots), so the blind schedule decides most of them.

## Chipzen name mapping

* Ashwing: the `PokerBots` README links the live bot "Ashwing_v2" on chipzen.ai; `ext:ashwing_v2` is `AshwingV2Bot`, the class
  `chipzen_entry.py` builds for that name. Confirmed from the repo, not from a leaderboard.
* Wolf: the entry is "Wolf Bot" (header of `bot.js`, Season 7). Whether it still plays in Season 16 is unknown.
* poker-arena: the Chipzen entry is `chipzen_agent.py` -> `chipzen_adapter.decide_chipzen` -> `live_agent.decide_live` +
  `strategy.py` (+ a heads-up preflop filter). The repo does not state its Chipzen bot name (the id lives in a git-ignored
  `chipzen.toml`). `analysis/shadow_report.py` is a dev.fun shadow-log reader, so "Shadow" is not this repo's bot. We only
  guess "AutodidactInnovations" from the owner name.
* sdkref is the official SDK example, not a field entrant.

## Known differences from the real bots

* Wolf: the Monte Carlo budget is 100 ms per decision (upstream 300 ms), so equity is noisier. The local engine does not
  send `turn_result` or `phase_change` hooks, so its tracker uses the action history channel (upstream documents it as
  the guaranteed one).
* autodidact: opponent model reset at each match; the equity shadow logging is off (it never changed an action).
* Randomness: bots seed from the system, so reruns with the same seed differ by sampling noise.

## Training input

`python -m rl.train ... --sdk-workers N --sdk-opps chipzen,ext:ashwing_v2,ext:autodidact_fast` hands each SDK worker the
list round robin (one opponent per seat pair, workers staggered). Without the flag the behavior is unchanged
(`chipzen`, the heuristic bot). A 3 iteration smoke on gb10-d (`tools/fb_train_smoke.sh`, scratch out dir, 2 SDK workers,
opponents chipzen, ashwing_v2, autodidact_fast, wolf) logged samples from every opponent:
`"sdk_samples": {"chipzen": 369, "ext:ashwing_v2": 391, "ext:autodidact_fast": 342, "ext:wolf": 121}`, and
per opponent match counts and win rates under `wr`.

Tools: `tools/field_smoke.py`, `tools/field_measure.sh`, `tools/field_report.py` (this table), `tools/autodidact_audit.py`
(which decision branch fired; no swallowed errors: 0 fallback decisions in 6 matches), `tools/fb_deploy.sh`.
