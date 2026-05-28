# Agent Execution Guide

This document tells an AI agent (e.g., Claude, Cursor, Codex) how to
work this repository productively. Read this **before** opening any
source file.

---

## Repository status

This repo is **partially implemented**. Phase 1 (CFR family on toy
games) is largely complete; Phase 2 (collusion detection) and Phase 4
(FlashCFR) are unstarted.

- [x] Phase 1.1 — Kuhn Poker game tree (`cfr/games/kuhn.py`)
- [x] Phase 1.2 — Vanilla CFR (`cfr/algorithms/vanilla_cfr.py`)
- [x] Phase 1.3 — Exploitability evaluator
  (`cfr/evaluate/exploitability.py`): info-set-aware two-pass best
  response (`best_response_value`) is the production path; brute-force
  enumeration is retained as `best_response_value_brute_force` for the
  Kuhn oracle test.
- [x] Phase 1.4 — MCCFR External Sampling (`cfr/algorithms/mccfr.py`)
- [x] Phase 1.5 — CFR+ with RM+, linear averaging, alternating
  two-pass updates (`cfr/algorithms/cfr_plus.py`)
- [~] Phase 1.6 — Leduc Hold'em: game module, two-pass BR, vanilla
  CFR convergence test landed (`cfr/games/leduc.py`,
  `tests/test_leduc_*.py`). MCCFR / CFR+ thresholds for Leduc still
  need calibrating — next sub-task in 1.6.
- [ ] Phase 1.7 — Convergence notebooks
- [ ] Phase 2 — Synthetic collusion detection
  (`docs/specifications-phase2.md` has the per-module contracts)
- [ ] Phase 4 — FlashCFR (CUDA library; see `docs/flashcfr-spec.md`
  and `HANDOFF.md` — this is the primary GPU work order)
- [ ] Phase 5 — Other GPU stretches (Deep CFR, GNN detector,
  FastAPI deploy)

Verified Kuhn (Phase 1.2): 200k iterations give exploitability 0.004
and game value -0.052, matching −1/18.

Verified Leduc (Phase 1.6 part 1): 30k iterations of vanilla CFR give
exploitability ≈ 0.10 and game value ≈ −0.084, matching Lanctot 2013's
published Nash value of −0.0856.

---

## Repository contract

- The existing Phase 1 code follows the Neller & Lanctot (2013)
  tutorial convention: `cfr()` returns the value to the player whose
  turn it is at the current history. **Recursive calls do not blindly
  negate** — they consult `game.current_player(next_history)` and
  negate only when the next player differs from the current one. This
  matters because Leduc's `'/'` round-separator lets the same player
  act on both sides of a round boundary (e.g., `cr` → `crc/` keeps
  P0 on the clock). Keep this convention when extending; do not
  revert to `len(history) % 2` arithmetic.
- The game-module protocol every algorithm depends on:
  ``ACTIONS``, ``all_deals()``, ``is_terminal(history)``,
  ``current_player(history)``, ``legal_actions(history)``,
  ``next_history(history, action)``,
  ``terminal_utility(history, cards)``,
  ``info_set_key(player, cards, history)``.
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

Recommended next sequence (1.4 / 1.5 / 1.6 part 1 are already met):

| Phase | Acceptance gate | Status |
|---|---|---|
| 1.4 MCCFR | exploitability on Kuhn ≤ 0.02 within 50k iters | met (`tests/test_mccfr.py`) |
| 1.5 CFR+ | exploitability on Kuhn ≤ 0.02 within 8k iters (two passes per iter) | met (`tests/test_cfr_plus.py`) |
| 1.6 Leduc Hold'em (CFR) | vanilla CFR exploitability ≤ 0.15 within 30k iters; game value within 0.02 of −0.0856 | met (`tests/test_leduc_cfr.py`) |
| 1.6 Leduc Hold'em (MCCFR + CFR+) | tune iteration budgets and add per-algorithm tests on Leduc | open |
| 2.x Collusion detection | LightGBM detector AUC ≥ 0.85 on held-out synthetic data | open |
| 4.x FlashCFR | see `docs/flashcfr-spec.md` for per-phase gates | open |

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
- CPU only for the core; GPU work lives under Phase 4 (FlashCFR — the
  primary GPU work order, see `docs/flashcfr-spec.md`) and Phase 5
  (Deep CFR / GNN detector / FastAPI deploy as smaller stretches).
- **GPU experiments must stay within currently-free VRAM and never
  push another process to OOM.** Check `nvidia-smi` before launching
  any training run; prefer explicit batch sizing over allocator
  tricks. **Every experiment produces both a chart and a Markdown
  report** under `reports/` (or the phase's own results dir) — a run
  without artifacts has zero shelf life.

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
