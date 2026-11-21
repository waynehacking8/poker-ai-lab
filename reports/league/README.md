# League: referee for Chipzen NLHE candidates

The league plays every candidate bot against a simulated opponent field cloned from real Chipzen
replays, against the seven hand-written baselines, and against every other candidate, in the real
match format (10,000 stacks, blinds 100, 150, 200, 300, 400, 600 rising every 20 hands, play to
bust). Candidates are ranked by match-win rate against the field population.

Everything heavy runs on gb10-d in `~/poker-ai-lab-league/` (own venv). The PC only edits and runs git.

## Layout

| path | what |
|---|---|
| `league/replays.py` | NLHE replay parser (Pineapple OFC matches are skipped), checked against `stacks_after` |
| `league/fit.py` | per-bot statistics, k-means archetypes, EM action tables with hidden-card de-censoring |
| `league/clone.py` | `CloneBot("arch:2")` / `CloneBot("bot:Kimiko")`, plain engine bots |
| `league/data/clones.npz` | fitted clones (all replays), committed so the league is rerunnable |
| `league/validate.py`, `league/validation_md.py` | held-out validation of the clones |
| `league/run.py` | the league runner (parallel, resumable, deterministic) |
| `league/report.py` | leaderboard from `results.jsonl` |
| `league/bot_host.py`, `league/hosting.py` | runs one candidate in its own process |
| `tools/league_sync.sh`, `tools/league_export.sh` | copy this checkout / a candidate branch to gb10-d |
| `reports/league/` | `clone_validation.md`, `leaderboard.md`, this file |

## How a candidate plugs in

A candidate is any chipzen `Bot` subclass: `decide(state)` returning a `chipzen.Action`, optional
`on_match_start`, `on_round_start`, `on_round_result` hooks, the same objects the live platform
passes. The constructor may take `seed=` (the runner passes a per-match seed for reproducibility) or
nothing.

The runner never imports a candidate into its own process. Branches share module names (`nlhe`,
`bot`) with different contents, so each candidate runs in a child process (`bot_host.py`) behind a
pipe and the engine calls it through `RemoteBot`. Consequences:

* two candidates from different branches can meet in one match without module clashes,
* a crash, exception, illegal action or a decision slower than `--decision-timeout` (10 s) counts as
  an error for that decision and the engine plays check, or fold if facing a bet (the engine runs
  with `strict=False`); errors and decide times are listed per entrant in the leaderboard,
* candidate code is only read: `league_export.sh` uses `git archive`, nothing is checked out or
  written in the other agents' repos.

Steps to add a candidate, from the PC (Git Bash):

```
tools/league_export.sh /c/Users/WEI-CHENG/Desktop/poker-ai-lab holdem-blueprint blueprint
# on gb10-d add an entry to ~/poker-ai-lab-league/candidates.json:
#   "blueprint": {"root": "candidates/blueprint/chipzen_bot", "module": "bot", "class": "HoldemBot"}
```

`root` is the directory put on `sys.path` (the one containing the module), `module` and `class` name
the `Bot` subclass. Install any extra dependencies the candidate needs into
`~/poker-ai-lab-league/.venv` (it is the interpreter the child process uses). Then rerun (below);
only the new entrant's matches and its head-to-head matches against the others are played.

## Rerun

```
tools/league_sync.sh                       # push league code from the PC
ssh gb10-d
cd ~/poker-ai-lab-league
nohup env PYTHONPATH=. .venv/bin/python -m league.run --candidates candidates.json \
    --out out/league --field-pairs 400 --bot-pairs 30 --base-pairs 60 --h2h-pairs 100 \
    --workers 4 > logs/league.log 2>&1 &
PYTHONPATH=. .venv/bin/python -m league.report --out out/league --md out/leaderboard.md
```

`--workers 4` was the cap for the first run (6 is allowed since the search agent finished): four engine processes, each busy; a candidate's child process
sits idle while the engine waits for it (at most two children per engine process are kept alive).

Matches are keyed `entrant|opponent|pair|seat` in `out/league/results.jsonl`; a rerun skips keys that
exist, so you can raise `--field-pairs` later and only the extra pairs are played, or kill and
restart at any time. Seeds derive from the opponent key and pair index only, so every entrant faces
the same deals and the same opponent draws. A pair is one deal seed played from both seats.

To replace a candidate that changed, delete its lines from `results.jsonl` (`"a": "cand:<name>"`
and head-to-head rows that name it) or use a new name.

Refit the clones after new replays arrive (copy the JSONs to `~/poker-ai-lab-league/data/`):

```
PYTHONPATH=. .venv/bin/python -m league.fit --data data --out league/data/clones.npz
PYTHONPATH=. .venv/bin/python -m league.fit --data data --out out/clones_train.npz --holdout 0.3
PYTHONPATH=. .venv/bin/python -m league.validate --model out/clones_train.npz
PYTHONPATH=. .venv/bin/python -m league.validation_md out/validation.json out/clone_validation.md
```

Clones changed means results are no longer comparable: use a fresh `--out` directory.

## Reading the result

* Gate (coordinator's rule): an entrant passes only if it wins at least 80% of matches against each
  opponent separately: every baseline, every archetype clone and every per-bot clone. The leaderboard
  shows a per-opponent PASS or FAIL table for each entrant, once on the point estimate and once on the
  95% Wilson lower bound over matches. The field-weighted average below is a ranking aid, not the gate.
  With 60 matches per bot clone and about 50 per small archetype, the lower bound can only clear 80%
  for a near-perfect record; raise `--bot-pairs` / `--field-pairs` when a close call matters.
* Rank: stratified field win rate. Each archetype gets its win rate over duplicate pairs, weighted by
  how often that archetype appears among rated-match participants; the CI is a 2,000 draw bootstrap
  over pairs inside each archetype. Second key: mean hands per won match.
* Bot-clone and baseline columns use a plain Wilson interval over matches (pairs share a deal, so
  treat these as slightly optimistic).
* The head-to-head matrix mirrors cells, so the row's win rate against the column is read directly.
* The numbers are win rates against clones. The clones are memoryless and do not adapt, so a candidate
  with an opponent model gets no credit for modelling an opponent that has nothing to learn beyond its
  fixed frequencies. See the weaknesses in `clone_validation.md` before trusting small gaps.

## First leaderboard (2026-11-21)

* Entrants: `chipzen-tip` (branch `holdem-chipzen` at 8c7c8d1, class `HoldemBot` in `chipzen_bot/bot.py`)
  and the seven baselines. The `holdem-blueprint` and `holdem-search` branches had no playable `Bot`
  yet, so they are not entered.
* Clones: `league/data/clones.npz`, fitted on all 235 NLHE matches (7,598 hands, 56 bots, 6 archetypes).
  The validation in `clone_validation.md` uses a train/test split refit (70/30 by match id), whose
  clustering chose 4 archetypes, so its archetype names differ from the league's.
* Exact command, on gb10-d in `~/poker-ai-lab-league` (this is `tools/league_first.sh`, which also
  runs the validation; `candidates.json` as in the section above, one entry for `chipzen-tip`):

```
PYTHONPATH=. .venv/bin/python -m league.run --candidates candidates.json --out out/league \
    --field-pairs 400 --bot-pairs 30 --base-pairs 60 --h2h-pairs 100 --workers 4
PYTHONPATH=. .venv/bin/python -m league.report --out out/league --md out/leaderboard.md
```

  17,080 matches, about 40 minutes at 4 workers. Results: `leaderboard.md`.
