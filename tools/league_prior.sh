#!/usr/bin/env bash
# Uncontaminated archetype priors (seat variant = league/data/clones_prior.npz, strict variant =
# clones_prior_strict.npz): refit without the 10 per-bot test bots, validate both on the 70/30
# split, and rebuild the validation report with the comparison. Run from ~/poker-ai-lab-league
# (2 workers). Does not touch out/league.
set -euo pipefail
export PYTHONPATH=.
PY=.venv/bin/python
$PY -m league.fit_prior --mode seat --out league/data/clones_prior.npz > /dev/null
$PY -m league.fit_prior --mode match --out league/data/clones_prior_strict.npz > /dev/null
$PY -m league.fit_prior --mode seat --base out/clones_train.npz --holdout 0.3 \
    --out out/clones_prior_train.npz > /dev/null
$PY -m league.fit_prior --mode match --base out/clones_train.npz --holdout 0.3 \
    --out out/clones_prior_strict_train.npz > /dev/null
$PY -m league.validate --model out/clones_prior_train.npz --sims 600 --bot-sims 0 --workers 2 \
    --out out/validation_prior.json
$PY -m league.validate --model out/clones_prior_strict_train.npz --sims 600 --bot-sims 0 \
    --workers 2 --out out/validation_prior_strict.json
$PY -m league.validation_md out/validation.json out/clone_validation.md > /dev/null
$PY -m league.compare_clones --a league/data/clones.npz --b league/data/clones_prior.npz \
    --c league/data/clones_prior_strict.npz --sims 400 --workers 2 \
    --md-append out/clone_validation.md --val-a out/validation.json \
    --val-b out/validation_prior.json --val-c out/validation_prior_strict.json
cp league/data/clones_prior.npz league/data/clones_prior_strict.npz data/
