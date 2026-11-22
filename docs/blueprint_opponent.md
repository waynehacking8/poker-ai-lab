# Blueprint opponent (poker-solver 100 bb) in the SDK arena

Why: the Chipzen Season 16 field has a CFR style bot ("Blueprint"). Our shipped
policy `rl-h4-300` had only met rule based bots. The author of that bot publishes an older
100 bb blueprint, so I run it as an arena opponent and measure our policies against it in
the real match format (10000 stacks, blinds 50/100 rising every 20 hands, heads up,
winner takes all).

## Provenance

| Item | Value |
|---|---|
| Code | https://github.com/matteo-psnt/poker-solver, MIT, pinned to tag v0.1.0 = commit `4ee3132b6e802c0efc74d469ec190b9c47727d7b` |
| Blueprint | release v0.1.0 asset `blueprint-100bb.tar`, 1947260928 bytes |
| tar sha256 | `3406d6c95ce344b79f840c4bf967d5a64edbf2dfb6983a726b7d28f8fa75325b` (equals the published `.sha256` file, checked with `sha256sum -c` on the box before extracting) |
| Run played | `run-pcs-production_opens-to12k-d100-145201-6584`, checkpoint `static-65000` (the only one in the tar) |
| Our hero files | `rl/models/h4_it000300.npz` sha256 `92fe8194...67db` (shipped), `h4_it000900.npz` sha256 `6c332638...aad` (copied from the training box, not tracked in git) |

Everything third party was downloaded on gb10-d directly from GitHub. Nothing of it ever
touched the Windows PC.

## Setup

Scripts live in `bpopp/scripts/` and run on gb10-d.

1. `fetch.sh` downloads the pinned code and the tar, verifies the sha256, extracts to
   `~/bp-data`. A single release connection ran at about 30 KB/s that day, so the script
   fetches 16 byte ranges in parallel.
2. `build.sh` builds `bpopp:v010` from `bpopp/Dockerfile`: python 3.13 slim, `uv sync
   --frozen --no-dev` from their lockfile (aarch64 wheels all resolve, eval7 builds from
   source in the build stage), their `src/` and `config/`, plus our `bpopp/server.py`.
   The build uses the network. The final image runs as uid 10001.
3. `bpopp/server.py` runs inside the container. It reads one JSON line per request on
   stdin and answers on stdout. It loads the run with `RunTracker.load(run_dir, None)`
   (the run record comes from the tar's own `run.jsonl`, not from Postgres), applies the
   policy threshold 0.35 at load, and calls their `BlueprintSeat.for_match` and
   `decide_frame` with `use_resolver=False`. That is the decision path of the live seat
   (`infra/serve/chipzen-seat.service` passes `--no-resolver` and `seat.toml` sets
   threshold 0.35). `run_seat`, the SDK, websockets, Azure, Batch, Postgres, terraform
   and deploy code are never imported or called.
4. `bpopp/opponent.py` is the arena side (`BlueprintOpponent`). It starts one container per
   arena worker process on first use and reuses it for every match of that worker (the
   load takes about 10 s), sends `match_start` per match and `decide` per turn.
5. `rl/eval_arena.py` got `--opp bp100`, `--hero chipzen` (the old `bot.HoldemBot`) and
   `--hero bp100` (blueprint as hero, used for the smoke test). Nothing else changed there.
6. `bpopp/analyze_log.py` and `bpopp/hand_check.py` read the per decision logs
   (`BP_LOG=dir`); `bpopp/flat_check.py` is a mapping sanity check (below);
   `scripts/run_matches.sh` is the exact run I used.

### Isolation flags (every container)

```
docker run -i --rm --name bpopp-<pid>-<rand> \
  --network none \
  --read-only --tmpfs /tmp:rw,exec,size=2g \
  --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 256 --memory 10g --cpus 2 \
  --user 10001:10001 \
  -v ~/bp-data/data:/work/data:ro \
  -e BP_RUN=... -e BP_AT=65000 -e BP_THRESHOLD=0.35 \
  -e OMP_NUM_THREADS=1 -e NUMBA_NUM_THREADS=1 bpopp:v010
```

No secrets or other mounts, blueprint data read only, no network at match time, no
contact with chipzen.ai or poker.matteopsnt.dev. One caveat: if an arena worker is killed
instead of exiting, its container can outlive it, so the run script kills
`bpopp-*` containers after each arena. None were left after any run.

## How stack depth is handled

Only the 100 bb rung is published. In their live seat a `DepthLadder` picks the rung by
effective depth, but with one rung it always returns that rung (the snap up rule needs a
deeper rung than the table, the log nearest fallback returns the only one). So the blueprint
plays its 100 bb tree at every depth, exactly as it would on Chipzen with only this
file. Concretely:

* `reconstruct` starts every hand from the blueprint's own 100 bb stacks, not from the
  real ones. Real stacks matter only through the clamp: wire sizes are priced in table
  chips and clamped to `[min_raise, max_raise]`, and an all in is `max_raise`.
* `table_scale` is fixed at `match_start` (factor 50 for 50/100). When blinds rise, its
  bet sizes stay in units of the first level, so most opens at later levels collapse to
  min raises. This is their documented limitation (`_note_escalation`), not something I
  added, and I left it as is because the goal is the opponent as it plays in the field.
* Depth census over the h4-300 run (47,422 blueprint decisions): 56.3 percent of decisions
  at 50 to 100 bb, 27.7 percent at 25 to 50 bb, 12.0 percent at 10 to 25 bb, 4.0 percent
  at 10 bb or less. So 44 percent of its decisions are below the depth it was trained for.

## Results

Arena: `run_arena`, 400 matches per row (200 duplicate seed pairs, both seats), seed 3,
4 workers, hero is our side, opponent is the blueprint. Wilson 95 percent interval.

| Hero | Hero wins | Win rate | 95% CI | Mean hands per match |
|---|---|---|---|---|
| `h4_it000300` (shipped rl-h4-300) | 222 / 400 | 55.5% | 50.6 to 60.3 | 39.9 |
| `h4_it000900` (newer candidate) | 220 / 400 | 55.0% | 50.1 to 59.8 | 43.4 |
| `bot.HoldemBot` (old heuristic) | 200 / 400 | 50.0% | 45.1 to 54.9 | 43.7 |

Reading: the blueprint is a real opponent (it holds the old heuristic bot to exactly 50
percent), and both RL policies beat it by a small margin whose lower bound only just clears
50. The two RL policies are indistinguishable here. Matches vs the blueprint are
not seed reproducible, because the blueprint samples actions from its strategy with an
unseeded generator, so a rerun moves each row by a few points.

### Smoke test (blueprint as hero vs baselines, 20 matches, seed 3)

| Opponent | Blueprint wins | Win rate | 95% CI | Mean hands |
|---|---|---|---|---|
| random | 11 / 20 | 55% | 34 to 74 | 17.5 |
| lag | 14 / 20 | 70% | 48 to 86 | 45.5 |

No exceptions, no illegal actions. Decision time over the 2,351 smoke decisions: server side
mean 0.18 ms, p99 0.42 ms, max 1.09 ms; round trip through `docker run -i` mean 0.41 ms,
p99 1.1 ms, max 2.3 ms (the box was running a training job at load average about 15 of 20).
Over the three 400 match runs (about 140k decisions): server mean 0.21 to 0.30 ms, p99 about
0.5 ms, max 2.5 ms; round trip p99 1.3 to 3.4 ms, worst single round trip 24 ms.
There is no resolver, so decisions are table lookups and far inside any Chipzen clock.

Memory per container: about 2.2 GiB steady, up to 5.3 GiB right while loading the
checkpoint (docker stats counts file cache; limit 10 GiB). Load plus numba warm up about 10 s.

Context for the smoke numbers: the blueprint is a poor exploiter. At the same seed set
(100 matches) it scored 63 percent vs random and 61 percent vs lag, where `h4_it000300`
scored 92 and 98 percent. With flat 50/100 blinds (every hand at 100 bb, `bpopp/flat_check.py`,
40 matches) it scored 92.5 percent vs station, 62.5 vs random, 65 vs lag, 65 vs maniac
and 100 vs nit, so the weak numbers are not only the depth mismatch. Equilibrium play is not
trying to maximise against these.

## Hand level check

Read from the decision logs of the h4-300 run (47,422 decisions) and the smoke run.

* Preflop, hands 1 to 20 (50/100 level, where the tree matches): as small blind it
  raises 84.4 percent, limps about 0, folds 15.6 percent (3,129 raise, 2 limp, 577 fold).
  Facing the first raise as big blind it continues 64 percent (353 call, 98 raise, 258 fold).
  Vs the heuristic bot: raise 84.5 percent, continue 71 percent. Sane equilibrium shapes.
* Premium preflop folds (AA, KK, QQ, JJ, TT, AKs, AKo, AQs, AQo, AJs, KQs): 3 in the whole
  run, all AQo, none in the smoke run.
* Postflop folds: 4,628 in the h4-300 run, only 4 faced a price of 20 percent of the pot or
  less, and 1 of those held a pair. The 12 first listed folds with two pair or better were
  all against all in or overbet prices (for example 7s Qs on 5h Jd 7s Qd Qc folding to 11,700
  into 13,500 from an opponent that was all in).
* Narrated hand, h4-300 vs blueprint, hand 2, blueprint is seat 1 with 6c 4d on the button:
  raise to 250 preflop, 150 bet on Qh 8d 3d, 1000 on the Ad turn, 3500 on the river after
  Qc. Hand 1, seat 1 with Jd 4s checks the flop and turn, bets 100 into 200 on the river,
  calls an 800 raise. All legal and in line with a CFR line.

No sign of a broken state mapping. The conventions of our engine history (raise amount is
the raise to total, call amount is the paid increment, blind posts as synthetic entries)
match the live wire notes in their `adapter.py`.

### Problems found in their decision path (not fixed in their code, handled in ours)

1. `wire_action` clamp: `_clamp_raise` returns `max(min_raise, min(total, max_raise))`,
   which is above `max_raise` when `min_raise > max_raise` (only the shove is legal). The
   strict arena engine rejects it ("raise 6666 outside [6182, 6182]"). Fix in
   `bpopp/opponent.py`: clamp into `[min(min_raise, max_raise), max_raise]`, which is the
   shove. Frequency: 42 / 60 / 85 decisions per 400 matches. Logged as `clamped`.
2. Short all in below the min raise: `their_raise` rounds the raise to zero increment in its
   coarse chips and snaps it to CALL, so the blueprint answers as if it faced a check and
   sends `check` where the price is positive (seen in the flat blind check vs random,
   "seat 0 sent check not in [fold, call]"). The wrapper repairs an illegal answer to the
   nearest legal action (check to call, call to check). Logged as `repaired`; it did not
   fire in the three 400 match runs.
3. Replay drift: rarely the replay ends in `Illegal action CALL (to_call=0)`. Their own code
   catches it and passes (fold if facing a bet). 1 of 2,351 decisions in the smoke run (vs
   random), 0 in the 400 match runs. Logged as `fallback`.
4. Inherited, left as is: chip scale fixed at the first blind level (see depth section).
   A variant that re-derives the scale per hand would be a stronger and less faithful
   opponent. I did not build it.

## Reproduce

```
# on gb10-d, with the repo checked out under ~/poker-ai-lab-bp/src
bash bpopp/scripts/fetch.sh && bash bpopp/scripts/build.sh
bash bpopp/scripts/run_matches.sh          # smoke, then 3 x 400 matches, logs in ~/bp-logs
~/poker-ai-lab-rl/.venv/bin/python -m bpopp.analyze_log ~/bp-logs/h4_300
~/poker-ai-lab-rl/.venv/bin/python bpopp/hand_check.py ~/bp-logs/h4_300
```

Single match: `python -m rl.eval_arena --model rl/models/h4_it000300.npz --opp bp100 --matches 400 --seed 3 --workers 4`
with `BP_DATA`, `BP_RUN`, `BP_AT`, `BP_IMAGE` set as in `bpopp/scripts/env.sh`.
