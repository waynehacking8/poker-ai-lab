# Roadmap

Living document tracking what's done, what's in progress, and what's planned.
Updated as the prototype evolves.

---

## Phase 1 — CFR family on toy games

### 1.1 Kuhn Poker environment
- [x] Game tree, terminal utilities, info-set keys (`cfr/games/kuhn.py`)
- [x] Deal enumeration (3 cards × 2 hole cards = 6 deals)

### 1.2 Vanilla CFR
- [x] Recursive traversal with reach probabilities
- [x] Regret matching + average strategy tracking
- [x] Smoke-test script (`scripts/smoke_test_kuhn.py`)
- [x] Convergence verified — at 200k iterations exploitability = 0.004,
      game value = -0.052 ≈ Kuhn's analytical value of -1/18.

### 1.3 Exploitability evaluator
- [x] Brute-force enumeration of pure best-response strategies (kept as
      `best_response_value_brute_force` and used as a test oracle on
      Kuhn — its `|A|^|I|` cost is infeasible past ~12 info sets).
- [x] Two-pass information-set-aware BR algorithm (`best_response_value`,
      `cfr/evaluate/exploitability.py`). Pass 1 enumerates opponent
      cf-reaches per BR-player info set; pass 2 decides BR actions
      bottom-up. Exact match with brute force on Kuhn within 1e-9.
- [x] Two-player summed exploitability.
- [ ] Per-iteration exploitability logging (for convergence plots).

### 1.4 MCCFR (External Sampling)
- [x] Sample opponent action + chance, traverse all of acting player's actions
- [x] Per Lanctot 2009 §4.2 — External Sampling needs no IS correction (the
      sampling distribution equals the cf-reach probability, so the
      estimator is naturally unbiased)
- [x] Convergence verified on Kuhn — at 50k iterations exploitability ≈ 0.02,
      P2 bluff rate J:p ≈ 1/3 (theoretical) within sampling noise

### 1.5 CFR+
- [x] Regret matching+ (regrets floored at 0 after each update)
- [x] Linear iteration weighting in strategy averaging (`Σ̄ += t · σ^t`)
- [x] Alternating updates — each iteration does two passes (P0 then P1) so
      the second pass responds to P0's just-updated strategy
- [x] Convergence verified on Kuhn — at 8k iterations exploitability ≈ 0.02,
      faster per-iteration than vanilla CFR (matches Tammelin 2014 ordering;
      the 10x speedup reported in the paper is on Leduc / Limit Hold'em
      where info-set count is large enough for RM+'s warm-start advantage
      to dominate — on 12-info-set Kuhn the gap is modest)

### 1.6 Leduc Hold'em
- [x] Game tree per Southey 2005: 6-card deck (J/Q/K × 2 suits), 2
      betting rounds (`/` separator in history), bet 2 / raise 4 chip
      structure, cap 2 raises per round (`cfr/games/leduc.py`).
- [x] Showdown logic — pair-with-community beats non-pair, then high
      hole card; genuine ties split.
- [x] Variable-action support added to `CFRState` (2 actions when no bet
      is pending, 3 with raise legal, 2 again at the cap) — see
      `cfr/algorithms/_state.py`.
- [x] Vanilla CFR converges on Leduc — at 30k iterations exploitability
      ≈ 0.10, game value ≈ -0.084 matching Lanctot 2013's published
      Nash value of -0.0856. (`tests/test_leduc_cfr.py`,
      `scripts/smoke_test_leduc.py`)
- [x] Fixed a sign-flip bug surfaced by Leduc: the recursive CFR
      negation assumed strict player alternation. Leduc's round
      separator lets the same player act on both sides of a round
      boundary (e.g., the `cr` → `crc/` transition leaves P0 to act).
      Replaced `len(history) % 2` with `game.current_player(...)` in
      `_terminal_util_current` and made the recursive negation
      conditional on whether the next node's player actually differs.
- [x] MCCFR (External Sampling) on Leduc — 200k iter, expl ≈ 0.47
      (`tests/test_leduc_mccfr.py`). MCCFR per-iteration variance is
      higher than vanilla CFR; the test sets a loose 0.6 threshold.
- [x] CFR+ on Leduc — 20k iter / 40k traversals, expl ≈ 0.15
      (`tests/test_leduc_cfr_plus.py`). Each iteration runs two passes
      (alternating traversers) so the work budget is `2 × N`.

### 1.7 Convergence visualization
- [x] `scripts/plot_convergence_kuhn.py` — log-log exploitability curve
      for vanilla / MCCFR / CFR+ on Kuhn → `results/convergence_kuhn.png`.
- [x] `scripts/plot_convergence_leduc.py` — same three algorithms on
      Leduc → `results/convergence_leduc.png`.
- [ ] Notebook variants (skipped — `.py` chart scripts are equivalent,
      run in CI, and don't carry diff noise from cell outputs).

---

## Phase 2 — Collusion detection

### 2.1 Honest player
- [x] `collusion/simulator/honest_player.py` — wraps an average-strategy
      table as a callable agent. Deterministic given seed; falls back to
      uniform on unseen info sets.

### 2.2 Colluding pair
- [x] `collusion/simulator/colluding_pair.py` — partner-aware soft-fold,
      chip-dump, and no-bluff-vs-partner rules. Reverts to honest play
      when the partner is not at the table.

### 2.3 Game runner
- [x] `collusion/simulator/run_session` — heads-up Kuhn played pairwise
      across `num_players` seats; long-format DataFrame log with the
      §3 schema plus `opponent_id` and synthetic `latency` columns.
- [x] `run_many_sessions` — namespaced stacking of independent sessions
      (without this, a single 4-player session yields only 6 labelled
      pairs which is too few for any classifier).

### 2.4 Feature engineering
- [x] `collusion/features/pairwise.py` — `co_table_freq`,
      `mutual_fold_rate_*`, `simultaneous_fold_rate` (always 0 in HU
      Kuhn, retained for schema completeness), `chip_flow_i_to_j`,
      `decision_time_corr`.
- [x] `compute_pairwise_features_multi` — per-session feature
      extraction with offset-aware pair index.

### 2.5 Detector — LightGBM baseline
- [x] `collusion/models/lgbm_classifier.py` — binary classifier with
      player-disjoint split, early stopping on AUC, ROC curve and
      precision-at-recall-50 returned. AUC ≥ 0.85 on the stacked
      `40 × 4-player × 2k-hand` setup (`tests/test_collusion_features
      .py::test_lgbm_auc_threshold`).

### 2.6 Detector — GNN (stretch)
- [ ] Player graph: edges weighted by behavioral co-occurrence
- [ ] PyTorch Geometric GraphSAGE for pair-level classification
- [ ] Compare to LightGBM baseline

### 2.7 Notebooks
- [ ] `notebooks/data_generation.ipynb` — show the simulator at work
- [ ] `notebooks/detection_results.ipynb` — ROC, importance, error analysis

---

## Phase 4 — FlashCFR (GPU-accelerated CFR library)

The main GPU work order for this repo. Full specification lives at
[`docs/flashcfr-spec.md`](flashcfr-spec.md). Target: 20–100×
speedup over CPU CFR, modelled after Berkeley/MIT's FlashLib.

### 4.1 Phase 1 design — Kuhn on GPU
- [x] Design doc at `docs/flashcfr-phase1-design.md` covering CUDA
      kernel signatures, struct-of-arrays memory layout, and
      kernel-by-kernel work order. **PAUSED for review.**
- [ ] Implement vanilla CFR CUDA kernels for Kuhn Poker (gated on
      design-doc review and CUDA-equipped environment).
- [ ] Validation: GPU-learned strategies match CPU baseline within
      seed-noise tolerance.
- [ ] Benchmark: iterations / second ≥ 10× CPU baseline on Kuhn.

### 4.2 Phase 2 — MCCFR on Leduc Hold'em (GPU)
- [ ] External-Sampling MCCFR kernels.
- [ ] Nsight Compute profiling; optimize top 3 hottest kernels.
- [ ] Report SM occupancy, warp efficiency, memory bandwidth used
      vs theoretical peak.

### 4.3 Phase 3 — CFR+ on HU Limit Hold'em
- [ ] Hand-bucketing pipeline using FlashLib KMeans (EHS / OCHS
      features computed on GPU).
- [ ] Multi-GPU regret-table sharding.
- [ ] Benchmark vs OpenSpiel (Python and C++).

### 4.4 Phase 4 — Deep CFR (optional)
- [ ] Replace tabular regret with PyTorch advantage network.
- [ ] Compare sample efficiency vs the tabular variant.

---

## Phase 5 — Stretch goals (post-FlashCFR)

- [ ] **Opponent modeling**: cluster simulated players into TAG / LAG /
      Passive / Loose archetypes; train a best-response policy per
      archetype.
- [ ] **Subgame solving** acceleration (Libratus-style nested
      re-solving).
- [ ] **Real-time inference mode** for online bots; sub-100ms decision
      latency.
- [ ] **Distributed multi-node training** with NCCL.
- [ ] **Online deployment skeleton**: FastAPI service that wraps a
      trained policy + a collusion classifier; latency budget < 500ms
      per decision.

---

## What's *not* on the roadmap

These would be defensible features for a larger project, but are
deliberately excluded from this prototype:

- **No-Limit Texas Hold'em.** Out of scope (see `design-decisions.md` D2).
- **Real production data.** Out of scope (D6).
- **Distributed training.** No need at this scale.
- **Hyperparameter sweeps.** CFR is essentially parameter-free; the
      collusion classifier uses LightGBM defaults until baseline is solid.

---

*Last updated: 2026-05-28 — Phase 1 closed (1.6 part 2 + 1.7 chart
scripts landed; tests at `tests/test_{vanilla_cfr,mccfr,cfr_plus,
exploitability,leduc_game,leduc_cfr,leduc_mccfr,leduc_cfr_plus}.py`).
Phase 2 simulator + features + LightGBM classifier landed; AUC ≥ 0.85
on stacked 4-player sessions (`tests/test_collusion_{features,
simulator}.py`). FlashCFR Phase 1 design doc landed
(`docs/flashcfr-phase1-design.md`), paused for review before CUDA
implementation. CI + MIT LICENSE added.*
