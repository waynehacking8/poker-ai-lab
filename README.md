# Poker AI Lab

> A self-study prototype exploring **Counterfactual Regret Minimization (CFR)**
> for imperfect-information games and **machine-learning-based collusion
> detection** for online card-game platforms.

The repo prioritizes **correctness, readability, and honest
scope** over scale or novelty.

---

## What this is

- A working implementation of **vanilla CFR** on Kuhn Poker (3-card toy
  game) and Leduc Hold'em.
- Variants: **MCCFR (External Sampling)** and **CFR+** on both games.
- An **exploitability** evaluator for tabular policies (info-set-aware
  two-pass best response, with brute-force enumeration retained as a
  Kuhn oracle).
- A pipeline that generates **synthetic colluding-game data** (CFR
  policies + soft-play colluder pairs) and trains a **LightGBM
  pair-level detector**; reaches AUC ≥ 0.85 on stacked 4-player Kuhn
  sessions.
- Convergence plots committed under `results/`.
- A **FlashCFR Phase 1 design document** (`docs/flashcfr-phase1-design
  .md`) defining the CUDA kernel signatures, struct-of-arrays memory
  layout, and kernel-by-kernel work order — paused for review before
  implementation.
- End-to-end runnable on a laptop CPU — no GPU required for any of the
  above (FlashCFR kernels themselves are gated on CUDA hardware).

## What this is NOT

- **Not novel research.** All algorithms follow published papers
  (Zinkevich 2007, Lanctot 2009, Tammelin 2014, etc.).
- **Not production-ready.** No real-world poker data; collusion
  behaviors are simulated and likely simpler than what real platforms see.
- **Not benchmarked on No-Limit Hold'em.** Toy games only — the
  techniques are correct, the scale is not.
- **CUDA path is design-only.** `docs/flashcfr-phase1-design.md`
  defines the kernels; no `.cu` files exist yet (the spec explicitly
  pauses for review at this point).

---

## Project layout

```
poker-ai-lab/
├── cfr/                       # Phase 1: CFR family on toy poker games
│   ├── games/                 # Kuhn Poker, Leduc Hold'em
│   ├── algorithms/            # vanilla_cfr, mccfr, cfr_plus, _state
│   └── evaluate/              # exploitability (two-pass BR + brute force)
├── collusion/                 # Phase 2: synthetic data + detector
│   ├── simulator/             # honest_player, colluding_pair, game_runner
│   ├── features/              # pairwise behavioral features
│   └── models/                # lgbm_classifier
├── scripts/                   # Smoke tests + convergence plot scripts
├── results/                   # PNG convergence plots committed to repo
├── tests/                     # pytest suite — every phase has tests pinned
└── docs/
    ├── cfr-notes.md                # Reading notes on CFR papers
    ├── design-decisions.md         # Why this scope, why these choices
    ├── roadmap.md                  # Status of each module
    ├── references.md               # Papers + recommended reading order
    ├── specifications-phase2.md    # Per-module contracts for Phase 2
    ├── flashcfr-spec.md            # GPU CFR library spec (Phase 4)
    └── flashcfr-phase1-design.md   # Kernel + memory design (paused for review)
```

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/waynehacking8/poker-ai-lab.git
cd poker-ai-lab

# 2. Install deps (CPU only)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Run the Kuhn Poker CFR smoke test
python -m scripts.smoke_test_kuhn 5000
```

Expected output: learned strategy approaching Kuhn's known Nash equilibrium
(P1 bets J with probability `α ∈ [0, 1/3]`, bets K with `3α`).

---

## Phase 1 — CFR family

### Why Kuhn Poker first?

Kuhn Poker is the smallest non-trivial imperfect-information game (12
information sets total). It serves as a unit-test for any CFR
implementation: a correct algorithm reaches near-zero exploitability in
seconds. If exploitability stays high, the bug is in the algorithm, not in
scale.

### Why Leduc Hold'em next?

Leduc Hold'em (6 cards, 2 betting rounds, 1 community card) is the standard
research benchmark just above Kuhn — 528 information sets across both
players (264 each). Still tractable for vanilla CFR. Used by every CFR
paper from 2007–2015 as the canonical small benchmark.

### Algorithms implemented (canonical forms)

| Algorithm | Year | Key idea | Leduc convergence |
|---|---|---|---|
| Vanilla CFR (full enum) | 2007 | Regret matching + counterfactual reach | expl 0.033 @ 1k iter |
| MCCFR (External Sampling) | 2009 | Sample opponent + chance, traverse self | expl 0.47 @ 200k iter |
| **CFR+ (full enum)** | 2014 | RM+ + linear averaging + alternating updates | **expl 0.001 @ 1k iter** |
| Deep CFR | 2019 | Neural network for regret storage | stretch, requires GPU |

On a small game like Leduc the **canonical ordering** is
`CFR+ enum < Vanilla CFR enum < MCCFR` — matching Tammelin 2014 and
Lanctot 2009. MCCFR's advantage is asymptotic; sampling pays off on
games too large for full enumeration. Chance-sampling variants of
vanilla CFR / CFR+ are also available (`vanilla_cfr.train`,
`cfr_plus.train`) but are alternatives, not canonical algorithms.

### Evaluation

`cfr/evaluate/exploitability.py` computes the standard exploitability
metric — sum of best-response values for both players. At a Nash
equilibrium this equals 0 (in zero-sum games).

### Convergence plots

Generated by `scripts/plot_convergence_{kuhn,leduc}.py`:

| Game | Final expl (vanilla enum / CFR+ enum / MCCFR ES) |
|---|---|
| Kuhn (5k enum iter, 50k MCCFR iter) | 0.0047 / **0.000055** / 0.014 |
| Leduc (1k enum iter, 200k MCCFR iter) | 0.033 / **0.0010** / 0.46 |

CFR+ enum dominates on both games — at 1k iter on Leduc, ~35× better
than vanilla CFR enum. This is the **canonical** Tammelin 2014 result.

---

## Phase 2 — Collusion detection

Online poker platforms must detect three main fraud types:

| Type | Behavior | Detection signal |
|---|---|---|
| **Collusion (夥牌)** | Players share hole-card info; soft-play partners | Pairwise fold-against-partner rate, simultaneous folds, chip flow |
| **Bots** | Automated decisions, no human fatigue | Decision latency distribution, mouse trajectory, 24-hour activity |
| **Multi-accounting** | Same person on multiple accounts | Device fingerprint, IP, behavior similarity |

This phase simulates honest games (using CFR-trained Kuhn policies from
Phase 1) and injects colluding pairs that share hole cards and apply
soft-play / chip-dump rules. Six pairwise behavioral features are
computed per `(i, j)`: co-table frequency, mutual fold rates,
simultaneous fold rate, chip flow, decision-time correlation. A
LightGBM classifier with player-disjoint train/test split reaches
**AUC ≥ 0.85** on stacked 4-player Kuhn sessions
(`tests/test_collusion_features.py::test_lgbm_auc_threshold`). A GNN
variant is listed as a stretch goal.

Run the end-to-end pipeline:

```bash
pytest tests/test_collusion_features.py::test_lgbm_auc_threshold -m slow -v
```

---

## Field context (why this matters in 2026)

Vanilla CFR is the **same algorithmic family** that powers modern
imperfect-information AI all the way to 2026 SOTA:

- **2017–2019** Libratus / DeepStack / Pluribus — CFR + nested subgame
  solving beats human pros on HUNL and 6-max.
- **2020 ReBeL** — CFR becomes the subgame solver inside an
  AlphaZero-style RL loop over Public Belief States.
- **2021 Player of Games (DeepMind)** — Growing-Tree CFR generalizes
  across perfect and imperfect information (chess / Go / poker /
  Scotland Yard).
- **2022 Cicero (Meta, Diplomacy)** — first deployment of
  "LLM-as-interface + planner-as-decider + alignment filter"; the
  architecture later re-derived in poker by ToolPoker.
- **2025 Obscuro** — *one-sided* GT-CFR breaks the common-knowledge
  ceiling that PBS-based systems hit; superhuman on Fog of War chess.
- **2026 Equilibrium Refinements** — picks sequential equilibria from
  subgame gadget games, reducing exploitability by >50%. CFR's
  theoretical surface is still active.
- **2026 ToolPoker (ICLR)** — refutes pure-LLM poker bots; same
  Cicero-style hybrid wins.

This prototype implements the **unit test** for that whole lineage —
correct vanilla CFR + MCCFR + exploitability on Kuhn / Leduc. See
[`docs/field-evolution.md`](docs/field-evolution.md) for the full
narrative, the three live disagreements in the field, and the
"GPT-moment" question.

---

## References

See [`docs/references.md`](docs/references.md) for the full reading list
(now including the 2022–2026 lineage above). Core foundational papers:

1. Zinkevich et al. 2007 — *Regret Minimization in Games with Incomplete
   Information*
2. Lanctot et al. 2009 — *Monte Carlo Sampling for Regret Minimization in
   Extensive Games*
3. Tammelin 2014 — *Solving Heads-Up Limit Hold'em Poker* (CFR+)
4. Brown & Sandholm 2017–2019 — Libratus / Pluribus
5. Heinrich & Silver 2016 — *Deep RL from Self-Play in Imperfect-Information
   Games* (NFSP)
6. Brown et al. 2019 — *Deep CFR*
7. Brown, Bakhtin, Lerer, Gong 2020 — *ReBeL* (CFR ↔ RL bridge)
8. Bakhtin et al. 2022 — *Cicero* (LLM + planner + filter on Diplomacy)
9. Zhang & Sandholm 2025 — *Obscuro* (one-sided GT-CFR, FoW chess)
10. Kubicek, Lisy, Sandholm 2026 — *Equilibrium Refinements*

---

## Author

Wei Cheng (Wayne) Chiu · [GitHub](https://github.com/waynehacking8) ·
M.S. in Computer Science, NTUST (April 2026 graduation).
