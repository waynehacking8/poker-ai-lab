#!/usr/bin/env bash
# Uncontaminated archetype prior: refit without matches of the 10 per-bot test bots, validate it,
# and append the comparison to the validation report. Run from ~/poker-ai-lab-league (2 workers).
# Does not touch out/league.
set -euo pipefail
export PYTHONPATH=.
PY=.venv/bin/python
$PY -m league.fit_prior --base league/data/clones.npz --out league/data/clones_prior.npz
$PY -m league.fit_prior --base out/clones_train.npz --holdout 0.3 --out out/clones_prior_train.npz > /dev/null
$PY -m league.validate --model out/clones_prior_train.npz --sims 600 --bot-sims 0 --workers 2 \
    --out out/validation_prior.json
$PY -m league.validation_md out/validation.json out/clone_validation.md > /dev/null
$PY -m league.compare_clones --a league/data/clones.npz --b league/data/clones_prior.npz \
    --sims 400 --workers 2 --md-append out/clone_validation.md \
    --val-a out/validation.json --val-b out/validation_prior.json
cp league/data/clones_prior.npz data/clones_prior.npz
