# Handoff — Read This First

You are an AI agent continuing development on this repository in a
new environment. This file is the single source of truth for what
to do next. Read it end-to-end before acting.

---

## What this repo is

`poker-ai-lab` is a self-study prototype exploring CFR-family
algorithms for imperfect-information games and ML-based collusion
detection for online card-game platforms.

GitHub: https://github.com/waynehacking8/poker-ai-lab

---

## Current status

- Phase 1 (CPU): **complete and verified**. Kuhn Poker + Vanilla
  CFR + brute-force exploitability. 200k iterations reach
  exploitability 0.004 and game value -0.052, matching the known
  analytical value -1/18. `pytest tests/test_kuhn_cfr.py -k "not
  slow"` is green.
- Phase 2 (collusion detection): docs and scaffolds only; no
  implementation. Spec in `docs/specifications-phase2.md`.
- Phase 3 (stretch / GPU): docs only.

---

## This environment's advantage and primary work order

You have a GPU available.

**The primary work order for this session is `docs/flashcfr-spec.md`.**

That document defines FlashCFR — a CUDA-accelerated CFR library
modelled after Berkeley/MIT's FlashLib, targeting 20–100× speedup
over CPU CFR baselines. FlashCFR is the most valuable use of GPU
time in this repo because:

1. CFR is provably correct on this repo's CPU baseline, so
   correctness validation is trivial.
2. The algorithm is highly parallel (millions of independent
   info-set updates per iteration) and is a good fit for modern
   GPU architectures.
3. There is no widely-used GPU CFR library; this is a real gap in
   the open-source ecosystem.

### Where to start

Open `docs/flashcfr-spec.md` and follow the "Starting point"
section: produce a Phase 1 design document at
`docs/flashcfr-phase1-design.md` (CUDA kernel signatures, memory
layout, kernel-by-kernel work order) BEFORE writing any kernel
code. Pause for review at that point.

The existing CPU CFR code (`cfr/`) is the ground-truth validator
for FlashCFR. Do not delete or rewrite it.

---

## Secondary work order (if FlashCFR is paused or you have spare time)

If FlashCFR is blocked or you cycle back to the CPU side:

1. **Phase 2 collusion detection** — see
   `docs/specifications-phase2.md`. Modules to implement:
   `collusion/simulator/{honest_player.py, colluding_pair.py,
   game_runner.py}`, `collusion/features/pairwise.py`,
   `collusion/models/lgbm_classifier.py`.
   - Acceptance: `pytest tests/test_collusion_features.py
     test_lgbm_auc_threshold` passes (AUC ≥ 0.85 on the easy
     setting).

2. **Phase 1.4 / 1.5 — MCCFR and CFR+ on CPU**, as a sanity check
   reference before tackling them on GPU. Acceptance criteria are
   listed in `AGENTS.md`.

3. **Phase 1.6 — Leduc Hold'em** game tree. The existing
   brute-force exploitability evaluator will not scale to Leduc's
   ~3,000 info sets per player; you will need a proper two-pass
   information-set-aware best-response algorithm. Spec stub is in
   `docs/roadmap.md` Phase 1.3.

---

## Setup

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install pytest

# Verify Phase 1 still works
pytest tests/test_kuhn_cfr.py -k "not slow"

# Quick sanity check on the CPU baseline
python -m scripts.smoke_test_kuhn 20000
```

For FlashCFR work, you will additionally need:

- CUDA Toolkit 12.x (`nvcc --version` should report 12.x).
- PyTorch matching the local CUDA version (`torch.cuda.is_available()`
  must return True).
- (Optional) FlashLib for the hand-bucketing pipeline at Phase 3 —
  add only when needed; defer initial setup.

---

## Hard constraints (do NOT violate)

- **No emoji** in any file.
- **Do not virtualize the author's experience.** Wei Cheng (Wayne)
  Chiu — NTUST CS Master's (April 2026), LLM and multi-agent
  systems background. **No prior production RL, game theory, or
  poker AI experience.** This repo is explicitly a self-study
  artifact and CUDA work would also be educational; docs and
  comments must not claim otherwise.
- **Preserve the CPU CFR conventions.** `cfr/algorithms/vanilla_cfr.py`
  follows the Neller & Lanctot 2013 convention (cfr() returns
  current-player perspective; recursive calls negate). The GPU
  implementation should use the same convention so policies are
  directly comparable across the two paths.
- **Do not delete or rewrite the existing CPU CFR code.** It is
  the ground-truth validator for the GPU path.
- **Follow `AGENTS.md`** for conventions (PEP 8, type hints,
  pytest, commit-message format).

---

## Verification gate before merging any phase

```
pytest tests/ -k "not slow"   # all phase-relevant tests green
git status                    # clean tree before commit
```

For FlashCFR specifically, additionally:

- Exploitability on Kuhn (GPU) is within 0.005 of the CPU
  baseline's exploitability at the same iteration count.
- Iterations-per-second on Kuhn ≥ 10× the CPU baseline.

Then flip the corresponding checkboxes in `docs/roadmap.md` and
commit.

---

## When in doubt

Order of resolution:

1. `docs/flashcfr-spec.md` — primary work-order details.
2. `docs/specifications-phase2.md` — collusion module contracts.
3. `docs/cfr-notes.md` — CFR algorithmic reference.
4. `docs/design-decisions.md` — "why this, not that".
5. `AGENTS.md` — conventions.
6. Add a new `D{n}` entry rather than silently contradicting
   an existing decision.
