# Agent Execution Guide

This document tells an AI agent (e.g., Claude, Cursor, Codex) how to
work this repository productively. Read this **before** opening any
source file.

---

## Repository status

This repo is **partially implemented**:

- ✓ Phase 1.1 — Kuhn Poker game tree (`cfr/games/kuhn.py`)
- ✓ Phase 1.2 — Vanilla CFR (`cfr/algorithms/vanilla_cfr.py`)
- ✓ Phase 1.3 — Brute-force exploitability evaluator
  (`cfr/evaluate/exploitability.py`)

Verified: 200k iterations on Kuhn give exploitability 0.004 and game
value -0.052, matching the known analytical value −1/18.

The remaining phases live in `docs/roadmap.md` and have not been
started:

- Phase 1.4 — MCCFR (External Sampling)
- Phase 1.5 — CFR+
- Phase 1.6 — Leduc Hold'em environment
- Phase 1.7 — Convergence notebooks
- Phase 2 — Synthetic collusion detection
- Phase 3 — Stretch (Deep CFR, GNN detector, FastAPI deploy)

---

## Repository contract

- The existing Phase 1 code follows the Neller & Lanctot (2013)
  tutorial convention: `cfr()` returns the value to the player whose
  turn it is at the current history, with recursive calls negating.
  Keep this convention when extending.
- New work orders live in `docs/roadmap.md` as checkbox items.
- Concrete formulas, I/O shapes, schema, and reference benchmarks
  live in `docs/specifications-phase2.md` (Phase 2 collusion) and
  `docs/cfr-notes.md` (Phase 1).
- `docs/design-decisions.md` records the "why this and not that" for
  decisions already made.

If a TODO is ambiguous, resolve in order:

1. `docs/specifications-phase2.md` (or `docs/cfr-notes.md` for CFR).
2. `docs/design-decisions.md`.
3. Default to a minimal, defensible choice and add a new `D{n}`
   entry.

---

## Working order

Recommended next sequence:

| Phase | Acceptance gate |
|---|---|
| 1.4 MCCFR | exploitability on Kuhn ≤ 0.01 within 50k iterations |
| 1.5 CFR+ | exploitability on Kuhn ≤ 0.005 within 10k iterations |
| 1.6 Leduc Hold'em | implementable two-pass BR replaces brute-force; CFR exploitability on Leduc ≤ 0.05 within 1M iterations |
| 2.x Collusion detection | LightGBM detector AUC ≥ 0.85 on held-out synthetic data |

Do not skip phases without writing a `D{n}` entry justifying.

---

## Conventions

- **Python style**: PEP 8, `black` formatting, `ruff` linting,
  type-hinted public functions.
- **Tests**: pytest. `pytest tests/` should be green after each
  phase completion.
- **No emoji in code or docs.**
- **Commit messages**: `<type>: <short description>` (feat / fix /
  refactor / docs / test / chore). Reference the roadmap phase in
  the body.
- **Doc updates**: when you finish a phase, flip its checkboxes in
  `docs/roadmap.md` to `[x]` and add a one-line note about what
  changed since the spec.

---

## What you do NOT need to ask

The following are pre-decided and documented. Do not re-litigate:

- Pure Python end-to-end, no OpenSpiel dependency. See
  `design-decisions.md` D3.
- Kuhn and Leduc only — no Texas Hold'em. See D2.
- Synthetic data, no public dataset. See D6.
- LightGBM as the baseline detector. See D5.
- CPU only for the core; GPU stretch goals (Deep CFR, GNN detector)
  in `docs/roadmap.md` Phase 3.

If you have a strong reason to change any of these, write a new
`D{n}` entry first; do not commit code that contradicts a current
decision.

---

## Author background (for grounding tone in docs)

Wei Cheng (Wayne) Chiu — NTUST CS Master's (April 2026 graduate),
LLM / multi-agent systems background. **No prior production experience
in reinforcement learning, game theory, or poker AI.** This is a
self-study prototype, not a re-implementation of a product.

When you write docs or comments, do not claim experience the author
does not have.
