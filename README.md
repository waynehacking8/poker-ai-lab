# Poker AI Lab

> A self-study prototype exploring **Counterfactual Regret Minimization (CFR)**
> for imperfect-information games and **machine-learning-based collusion
> detection** for online card-game platforms.

Built as preparation material for an AI Engineer interview focused on poker /
card-game AI. The repo prioritizes **correctness, readability, and honest
scope** over scale or novelty.

---

## What this is

- A working implementation of **vanilla CFR** on Kuhn Poker (3-card toy
  game) and Leduc Hold'em (planned).
- Variants: **MCCFR (External Sampling)** and **CFR+** (planned).
- An **exploitability** evaluator for tabular policies.
- A pipeline to generate **synthetic colluding-game data** and train
  detectors using behavioral features (planned).
- End-to-end runnable on a laptop CPU — no GPU required.

## What this is NOT

- **Not novel research.** All algorithms follow published papers
  (Zinkevich 2007, Lanctot 2009, Tammelin 2014, etc.).
- **Not production-ready.** No real-world poker data; collusion
  behaviors are simulated and likely simpler than what real platforms see.
- **Not benchmarked on No-Limit Hold'em.** Toy games only — the
  techniques are correct, the scale is not.
- **Not yet complete.** This is a work-in-progress prototype.

---

## Project layout

```
poker-ai-lab/
├── cfr/                       # Phase 1: CFR family on toy poker games
│   ├── games/                 # Kuhn Poker, Leduc Hold'em (planned)
│   ├── algorithms/            # vanilla_cfr, mccfr, cfr_plus
│   └── evaluate/              # exploitability
├── collusion/                 # Phase 2: synthetic data + detector (planned)
│   ├── simulator/             # honest player, colluding pair, game runner
│   ├── features/              # pairwise behavioral features, player graphs
│   └── models/                # LightGBM classifier, GNN detector (optional)
├── scripts/                   # Demo / smoke-test entry points
├── notebooks/                 # Convergence plots, detection ROC curves
├── results/                   # Figures and tables committed to repo
└── docs/
    ├── cfr-notes.md           # Reading notes on CFR papers
    ├── design-decisions.md    # Why this scope, why these choices
    ├── roadmap.md             # Status of each module
    └── references.md          # Papers + recommended reading order
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
research benchmark just above Kuhn. ~3000 information sets — still
tractable for vanilla CFR. Used by every CFR paper from 2007–2015 as the
canonical small benchmark.

### Algorithms implemented

| Algorithm | Year | Key idea | Status |
|---|---|---|---|
| Vanilla CFR | 2007 | Regret matching + counterfactual reach | written, debugging convergence |
| MCCFR (External Sampling) | 2009 | Sample opponent + chance, traverse self | planned |
| CFR+ | 2014 | Reset negative regrets to 0; linear averaging | planned |
| Deep CFR | 2019 | Neural network for regret storage | stretch, requires GPU |

### Evaluation

`cfr/evaluate/exploitability.py` computes the standard exploitability
metric — sum of best-response values for both players. At a Nash
equilibrium this equals 0 (in zero-sum games).

---

## Phase 2 — Collusion detection (planned)

Online poker platforms must detect three main fraud types:

| Type | Behavior | Detection signal |
|---|---|---|
| **Collusion (夥牌)** | Players share hole-card info; soft-play partners | Pairwise fold-against-partner rate, simultaneous folds, chip flow |
| **Bots** | Automated decisions, no human fatigue | Decision latency distribution, mouse trajectory, 24-hour activity |
| **Multi-accounting** | Same person on multiple accounts | Device fingerprint, IP, behavior similarity |

This phase will simulate honest games (using CFR-trained policies from
Phase 1) and inject colluding pairs (sharing hole cards, soft-playing).
Features are then engineered at the pairwise level, and a LightGBM
classifier is trained to flag colluders. A simple GNN variant is planned
as a stretch goal.

---

## References

See [`docs/references.md`](docs/references.md) for the full reading list.
Core papers:

1. Zinkevich et al. 2007 — *Regret Minimization in Games with Incomplete
   Information*
2. Lanctot et al. 2009 — *Monte Carlo Sampling for Regret Minimization in
   Extensive Games*
3. Tammelin 2014 — *Solving Heads-Up Limit Hold'em Poker* (CFR+)
4. Brown & Sandholm 2017–2019 — Libratus / Pluribus
5. Heinrich & Silver 2016 — *Deep RL from Self-Play in Imperfect-Information
   Games* (NFSP)
6. Brown et al. 2019 — *Deep CFR*

---

## Author

Wei Cheng (Wayne) Chiu · [GitHub](https://github.com/waynehacking8) ·
M.S. in Computer Science, NTUST (April 2026 graduation).
