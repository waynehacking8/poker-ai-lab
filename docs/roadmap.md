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
- [x] Brute-force enumeration of pure best-response strategies (correct
      for any zero-sum extensive-form game, tractable up to ~10 info sets
      per player).
- [x] Two-player summed exploitability.
- [ ] Two-pass information-set-aware BR algorithm (needed for Leduc — the
      brute-force version's complexity is `|A|^|I|`, which exhausts
      memory beyond ~12 info sets).
- [ ] Per-iteration exploitability logging (for convergence plots).

### 1.4 MCCFR (External Sampling)
- [ ] Sample opponent action + chance, traverse all of acting player's actions
- [ ] Importance-sampling-weighted regret updates
- [ ] Comparison: iterations-to-converge vs vanilla CFR

### 1.5 CFR+
- [ ] Floor regrets at 0 after each update
- [ ] Linear iteration weighting in strategy averaging
- [ ] Alternating updates between P1 and P2

### 1.6 Leduc Hold'em
- [ ] Game tree (6 cards, 2 betting rounds, 1 community card)
- [ ] Showdown logic (pair beats high card)
- [ ] Run all three CFR variants on Leduc

### 1.7 Notebooks
- [ ] `notebooks/convergence_kuhn.ipynb` — exploitability vs iterations
- [ ] `notebooks/strategy_comparison.ipynb` — CFR / MCCFR / CFR+
- [ ] `notebooks/leduc_results.ipynb` — Leduc Hold'em equilibrium

---

## Phase 2 — Collusion detection

### 2.1 Honest player
- [ ] Wrap a trained CFR policy as a callable agent
- [ ] Support stochastic sampling from average strategy

### 2.2 Colluding pair
- [ ] Share hole-card information between two agents
- [ ] Soft-play: increase fold rate when opponent is the partner
- [ ] Chip-dumping: deliberately lose to partner

### 2.3 Game runner
- [ ] Simulate N-player tables of Leduc (or extended Kuhn) games
- [ ] Log every (player, info_set, action) tuple to a structured format
- [ ] Configurable colluder rate per simulation

### 2.4 Feature engineering
- [ ] Pairwise stats: simultaneous fold rate, fold-against-partner rate,
      betting-pattern correlation
- [ ] Aggregate stats: per-player win rate, fold rate, aggression
- [ ] Optional graph features: co-occurrence at same table, chip flow

### 2.5 Detector — LightGBM baseline
- [ ] Binary classifier (collusion / no collusion) at the pair level
- [ ] Train / validation / test split with no overlap of players
- [ ] ROC curve, precision-recall curve, feature importance plot

### 2.6 Detector — GNN (stretch)
- [ ] Player graph: edges weighted by behavioral co-occurrence
- [ ] PyTorch Geometric GraphSAGE for pair-level classification
- [ ] Compare to LightGBM baseline

### 2.7 Notebooks
- [ ] `notebooks/data_generation.ipynb` — show the simulator at work
- [ ] `notebooks/detection_results.ipynb` — ROC, importance, error analysis

---

## Phase 3 — Stretch goals (post-interview)

- [ ] **Opponent modeling**: cluster simulated players into TAG / LAG /
      Passive / Loose archetypes; train a best-response policy per
      archetype.
- [ ] **Deep CFR**: replace tabular regret with PyTorch advantage net.
      Requires GPU; demo on Leduc.
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

*Last updated: 2026-05-28*
