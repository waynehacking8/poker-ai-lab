# Handoff: read this first

State of the repo on branch `holdem-chipzen` (nothing pushed). The FlashCFR documents in
`docs/` are kept as they were; this file describes what is actually built and what is open.

## What exists

1. CFR family on toy games (Kuhn, Leduc): `cfr/`, tests in `tests/test_*cfr*.py`. Unchanged.
2. Collusion detector scaffolds: `collusion/`. Unchanged.
3. Heads-up No-Limit Hold'em bot for Chipzen.ai, built on this branch:
   * `chipzen_bot/` deployment folder (entry `bot.py`, strategy package `nlhe/`, Dockerfile,
     requirements, README). `chipzen-sdk validate ./chipzen_bot/ --check-connectivity`
     passes (output in `results/holdem/validate.txt`). The Docker image has not been built.
   * `holdem/` local arena: engine on the real `chipzen.models` objects, seven baseline
     opponents, match runner (`arena.py`), per hand EV runner (`cash.py`).
   * `scripts/`: `build_preflop_equity.py` and `solve_pushfold.py` generate the two data
     files in `chipzen_bot/nlhe/data/`; `pushfold_compare.py` checks them against published
     HU Nash numbers; `holdem_remote.sh` syncs the tree to gb10-d and runs a command there;
     `holdem_diag.py` buckets where chips go; `holdem_latency.py` measures decide().
   * `reports/holdem-iterations.md`: what lost, what changed, before and after numbers.
   * `tools/`: the Chipzen replay fetch and analysis scripts, `match_ceiling.py` and
     `replay_conformance.py` (see `tools/README.md`, including the 900 s rate limit). The
     replays themselves are in `.cache/` and are gitignored. To run the conformance test on
     gb10-d, copy `.cache/chipzen-replays` to `~/poker-ai-lab-sim/.cache/` once
     (`holdem_remote.sh` does not sync `.cache`); the pytest skips without it.
   * Engine fidelity (2026-11-21): all 10,516 real NLHE hands replay exactly through
     `holdem/engine.py`. Blind levels past 600 (800 from hand 121, 1000 from hand 141) are
     inferred from OFC replays; nothing past hand 146 is observed. Earlier win rates in other
     tracks were measured on the old engine (no 800 and 1000 levels, small blind prompted
     against a tiny all-in big blind) and should be re-run for comparison.

## Numbers (gb10-d, 400 seat-swapped matches per opponent, real format)

Real format: 10,000 stacks, blinds 50/100 rising every 20 hands to 600, then 800 and 1000
from hands 121 and 141 (inferred), play to bust. Re-measured after the engine fidelity fixes.
Command: `scripts/holdem_remote.sh python -m holdem.arena --opp all --matches 400 --seed 1 --workers 4`
(raw lines in `results/holdem/arena_seed1.jsonl` and `arena_seed2.jsonl`, seed 2 was never
used for tuning).

| opponent | win rate seed 1 | 95% CI | seed 2 | mean hands per won match |
|---|---|---|---|---|
| station | 96.0% | 93.6 to 97.5 | 95.5% | 27 |
| reference | 90.2% | 86.9 to 92.8 | 90.0% | 88 |
| nit | 88.2% | 84.7 to 91.0 | 86.0% | 86 |
| random | 83.0% | 79.0 to 86.4 | 79.0% | 24 |
| lag | 71.5% | 66.9 to 75.7 | 69.2% | 44 |
| maniac | 71.8% | 67.1 to 75.9 | 72.8% | 9 |
| station_raiser | 69.8% | 65.1 to 74.0 | 72.0% | 32 |

The 80 percent bar is NOT met for lag, maniac and station_raiser (random is at the line).
See the iteration log for the diagnosis. Short version: against maniac and random the chips
are won (positive EV per hand) but the match is decided by one or two all-ins, and a
fixed-threshold "shove the top 7%" probe reaches the same 73.5% against the maniac, so the
equity based method has plateaued there; lag and station_raiser still lose chips by being
stacked off in medium pots and by not folding enough to re-raises.

Decision latency on gb10-d pinned to one core (`taskset -c 0 python scripts/holdem_latency.py`):
p50 5.3 ms, p99 19 ms, max 40 ms (CPU time max 21 ms). Estimate for 0.5 vCPU x86 at 3x
slower than one gb10-d core: about 16 ms p50, 60 ms p99, 120 ms max. Well under 5 s.

## Open work, in order

1. Close the gap to 80 percent on lag, maniac and station_raiser. Ideas not yet tried:
   a solved postflop abstraction at 25 to 50 BB for the stack-off spots, a match level value
   function fitted from simulation (win probability by chip share and blind level) used for
   all-in decisions, modelling the opponent's whole-hand strategy rather than per-action
   frequencies.
2. Replace the toy baselines by clones of the real field once the replay-cloned opponents are
   available (another agent builds them in `~/poker-ai-lab-league` on gb10-d).
3. Build the Docker image on gb10-d (`docker buildx build --platform linux/amd64 chipzen_bot`)
   and upload.

## Setup

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pytest chipzen-bot==0.7.0
pytest -m "not slow"           # 100 tests; the Hold'em tests need chipzen-bot installed
pytest                         # everything (about 3 minutes)
```

Simulation and test runs for this work were done on gb10-d under `~/poker-ai-lab-sim/`
(venv with chipzen-bot, pytest, numpy). Use at most 6 worker processes there.

## Traps

* `chipzen.models.GameState` is a slotted dataclass: use `dataclasses.replace`, not `__dict__`.
* The wire has no `all_in`: a shove is `raise` with `amount == max_raise`; `min_raise` can be
  larger than `max_raise`.
* Blinds change every 20 hands in the real format: read them from `post_*` history entries.
* The pytest path includes `chipzen_bot` (see `pyproject.toml`), so `import nlhe` and
  `import bot` work in tests; `holdem/__init__.py` does the same for scripts.
* Windows checkout: files are LF in the repo; check `git diff --stat` before committing.

## Hard constraints (unchanged)

* No emoji in any file.
* Do not virtualize the author's experience: Wei Cheng (Wayne) Chiu, NTUST CS Master's
  (April 2026), LLM and multi-agent systems background, self-study in game theory and poker AI.
* Do not delete or rewrite the existing CPU CFR code; it validates any future GPU path.
* Follow `AGENTS.md` for conventions.

## FlashCFR (paused)

`docs/flashcfr-spec.md` and `docs/flashcfr-phase1-design.md` describe the GPU CFR work order.
It has not been started beyond the design documents.

## When in doubt

1. `reports/holdem-iterations.md` for the Hold'em decisions.
2. `docs/flashcfr-spec.md` for the GPU work order.
3. `docs/specifications-phase2.md` for the collusion modules.
4. `docs/cfr-notes.md`, `docs/design-decisions.md`, `AGENTS.md`.
5. Add a new `D{n}` entry rather than silently contradicting an existing decision.
