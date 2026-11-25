# Report Reading Guide

The three English reports (`phase1-convergence.md`, `mccfr-scaling.md`,
`phase2-collusion-detection.md`) record the experimental results in a rigorous
format. This guide is the narrator for **how to read those reports**: it gives you
three speeds to get into them, explains why the shape of each chart is reasonable,
which details a reviewer will catch, and which limitations should be flagged
honestly.

---

## Who this is for

- **You yourself**: coming back after a few weeks, without re-climbing all the reports every time
- **Reviewers and incoming readers**: a quick way to navigate the value of the three reports
- **Incoming AIs and engineers**: know the purpose and structure of each report and how to cite it

The English reports cover "**what this is**"; this guide covers "**how to read it, why it is reasonable, and how to defend against challenges**".

---

## Map of the reports/ directory

| File | Topic | Purpose |
|---|---|---|
| [`phase1-convergence.md`](phase1-convergence.md) | The three CFR families converging on Kuhn / Leduc | Phase 1 results report |
| [`mccfr-scaling.md`](mccfr-scaling.md) | The crossover where MCCFR beats enum on large games | Phase 1 supplementary experiment (answers "is MCCFR useless?") |
| [`phase2-collusion-detection.md`](phase2-collusion-detection.md) | LightGBM collusion detection | Phase 2 results report |
| `phase2-metrics-*.json` | Phase 2 machine-readable data | Ground truth the report cites |
| `phase2-roc-*.png` | Phase 2 ROC curves | Report figures |
| `mccfr-scaling.png` | MCCFR crossover two-line chart | Report figure |
| `mccfr-scaling.json` | MCCFR sweep raw data | Ground truth the report cites |
| `phase2-metrics.json` | Phase 2 combined data | Cited by the report |
| [`../results/convergence_kuhn.png`](../results/convergence_kuhn.png) | Phase 1 Kuhn convergence chart | Report figure |
| [`../results/convergence_leduc.png`](../results/convergence_leduc.png) | Phase 1 Leduc convergence chart | Report figure |

---

## Report 1: Phase 1, the CFR convergence report

### What it says

The implementations of the three canonical CFR algorithms on two toy games (Kuhn,
12 info sets; Leduc, 528 info sets) are complete, converge correctly, and agree
with the literature.

### 30 seconds with one chart

Open [`../results/convergence_leduc.png`](../results/convergence_leduc.png):

- 🟧 The **orange CFR+ enum** line is lowest (strongest) → expl 0.001 at 1000 iter
- 🔵 The **blue vanilla CFR enum** line is in the middle → expl 0.033 at 1000 iter
- 🟢 The **green MCCFR** line is up in the sky → expl 0.46 at 200,000 iter

One-sentence conclusion: **CFR+ is 35× faster than vanilla, matching Tammelin 2014.
MCCFR is slow on small games, matching Lanctot 2009.**

### 3 minutes: scan these 4 places

| Section | What to look at |
|---|---|
| §1 What's measured | The exploitability formula + the table of published Nash values |
| §3.1 Kuhn convergence table | CFR+ reaches expl 0.00018 at 1k iter, 75× faster than vanilla |
| §4.1 Leduc convergence table + advantage table | How the 35× advantage slowly grows out of 1.6× |
| §6 Bug fix history | The discovery of the RM+ inline floor bug, a demonstration of methodology |

### Deep read: where every number comes from

Each cell corresponds to one deterministic seed run (enum has no RNG); MCCFR uses 5
seeds (Kuhn) or 3 seeds (Leduc) and takes mean ± std. **Reproducibility is in
§8**: paste the commands into a terminal and your machine gets the same numbers.

Comparison with the accepted Nash values:

| Game | Accepted Nash value | Our best game value | Gap |
|---|---|---|---|
| Kuhn | -1/18 ≈ -0.0556 (Kuhn 1950, analytic) | -0.0555 at 5000 enum iter | < 0.001 ✓ |
| Leduc | -0.0856 (Lanctot 2013 published) | -0.0779 at 1000 CFR+ enum iter | 0.008 ✓ |

The gaps are within finite-iteration error, which **shows the implementation is correct** (if the implementation were wrong, the game value would drift 0.02+ from the published one).

### Red-flag checklist (use it to judge whether similar reports by others are real)

| Red flag | Meaning |
|---|---|
| ❌ The convergence curve bounces back somewhere | A bug in the strategy_sum update (overwritten instead of accumulated) |
| ❌ CFR+ is slower than vanilla | Usually an inline RM+ floor bug, which our early version had |
| ❌ Game value deviates from the published one by more than 0.02 | Wrong utility computation, or wrong sign convention |
| ❌ MCCFR is faster than enum CFR+ on Kuhn | Violates the Lanctot 2009 prediction; go back and look for a bug |
| ✓ All our charts pass the checks above | |

---

## Report 2: the MCCFR scaling supplement

### What it says

The Phase 1 report left readers with the impression that "MCCFR is useless". This
supplement uses a **controlled experiment** to show that **MCCFR wins once the game
is large enough**, exactly as the asymptotic-advantage prediction in Lanctot 2009
says.

### 30 seconds with one chart

Open [`mccfr-scaling.png`](mccfr-scaling.png):

- 🔵 The blue **enum CFR+** line slopes from lower left (strong) to upper right (weak), the N² cost blow-up
- 🟧 The orange **MCCFR** line is almost horizontal, since per-iter cost does not depend on N
- The two lines **cross at N ≈ 250-300**

One-sentence conclusion: **enum wins for N < 250, MCCFR wins for N ≥ 300. The
crossover is a real physical phenomenon.**

### 3 minutes: scan these 3 places

| Section | What to look at |
|---|---|
| §2 Results table | Head-to-head results at 8 values of N, from enum winning by 350× at N=3 to MCCFR winning by 5× at N=400 |
| §3 What the chart shows | Why each of the two lines looks the way it does: enum's N² cost vs MCCFR's constant cost |
| §4 Meaning for industry | Why Cepheus used CFR+ while Libratus / Pluribus used MCCFR |

### Deep read: why this experiment design is clean

| Design choice | Why |
|---|---|
| N-card Kuhn instead of Big Leduc | The Kuhn tree is simple, so **growing N only adds chance branching, a single variable** |
| N=3 sanity check | Matches standard Kuhn to 1e-9, showing the parameterized implementation is correct |
| 20-second wall-time budget | Who learns better under a fixed time, a **fair head-to-head** |
| 1 deterministic seed for enum + a fixed seed for MCCFR | Fully reproducible |

### Red-flag checklist

| Red flag | Meaning |
|---|---|
| ❌ MCCFR beats enum at N=3 | Violates Lanctot; there is a bug |
| ❌ The two lines never cross | The controlled setup failed |
| ❌ Enum still runs 1000 iter at N=400 | Wall-time accounting is wrong |
| ✓ Our curves cross cleanly at N=250-300 | |

### How this maps to real Texas Hold'em

Report §5 honestly states that **this experiment is not an NLHE benchmark**. No
matter how many cards you add, N-card Kuhn still has a linear O(N) number of info
sets, innumerable orders of magnitude from NLHE's 10¹⁷ info sets.

But the phenomenon "**enum per-iter cost explodes → MCCFR turns the tables**" at
N=300 is **the same mechanism** as in NLHE. So this toy experiment **actually runs
out, in front of you,** the causal story of "why Libratus uses MCCFR".

---

## Report 3: Phase 2, synthetic collusion detection

### What it says

The Phase 1 CFR strategies serve as the "honest players", synthetic colluders are
injected, and a LightGBM detector is trained. **The headline AUC of 0.9995 is too
pretty**, so I also report the **adversarial baseline AUC of 0.8245** (the version
with the strong signal turned off).

### 30 seconds with one chart

Open [`phase2-roc-comparison.png`](phase2-roc-comparison.png):

- The upper **blue ROC** hugs the top-left corner → AUC 0.9995 (with the shared-latency signal)
- The lower **red ROC** sits in the upper-middle region → AUC 0.8245 (without the shared-latency signal)
- The grey dashed line is the random baseline (AUC 0.5)

One-sentence conclusion: **perfect with the strong signal, still useful without
it**. The detector does not rest on a single feature.

### 3 minutes: scan these 4 places

| Section | What to look at |
|---|---|
| §1 Pipeline | The ASCII flow chart, the whole chain CFR → simulator → features → LightGBM |
| §2 Behavioural model | The 4 collusion rules + the hidden shared-latency signal |
| §4 Results two-column table | AUC, P@R50 and feature importance for the two settings side by side |
| §5 Finding #1 | decision_time_corr dominating alone vs after removal, when fold-rate takes over |

### Deep read: why stacked sessions (D10)

Spec §6 says "4-player Kuhn, 10k hands, AUC ≥ 0.85". But N=4 gives only
C(4,2)=6 pairs, and the classifier cannot be trained. I used **40 independent
4-player sessions × 2k hands** to stack 240 pairs, with namespacing to avoid
collisions. This deviation from the spec is recorded in the D10 entry of
[`../docs/design-decisions.md`](../docs/design-decisions.md).

### Deep read: why chip_flow gain = 0

Textbooks all say chip dumping is the classic collusion signal. But we set
`chip_dump_prob=0.1` (10% of the time, "should fold" becomes "call"), and each pair
of players shares only 333 hands, so the noise of ordinary wins and losses drowns
the chip-dump signal. **I did not tune parameters to make it look good**: I kept
the spec defaults and flagged the finding honestly.

### Red-flag checklist

| Red flag | Meaning |
|---|---|
| ❌ The AUC crosses the random diagonal | The classifier has a bug |
| ❌ AUC goes up after removing latency | The logic does not hold |
| ❌ No caveat is stated, leaving people thinking 0.9995 is production-ready | Dishonest |
| ✓ We state the caveat clearly in §5 Finding #1 | |

---

## The overall story of the three reports

```
        ┌──────────────────────────────────────┐
        │  Phase 1: CFR algorithm foundations  │
        │  "Do you know the CFR family?"       │
        └────────────────┬─────────────────────┘
                         │ cites
                         ▼
        ┌──────────────────────────────────────┐
        │  MCCFR scaling supplement            │
        │  "Do you understand why industry     │
        │   picked MCCFR?"                     │
        └──────────────────────────────────────┘

        ┌──────────────────────────────────────┐
        │  Phase 2: collusion detection        │
        │  pipeline                            │
        │  "Can you integrate CFR into a       │
        │   product?"                          │
        └──────────────────────────────────────┘
```

- Phase 1 is the answer to "**do you know CFR**"
- MCCFR scaling is the answer to "**do you understand why industry picks MCCFR over enum**"
- Phase 2 is the answer to "**can you integrate CFR into a real detection system**"

The three reports stand on their own, and together they tell one story: **"the full chain from understanding the algorithm to systems engineering"**.

---

## What we proved: concepts mapped to concrete experiments

| Concept I know | Where the evidence is |
|---|---|
| CFR algorithm mechanics (cf_reach, sign convention) | Phase 1 §1, [`cfr/algorithms/vanilla_cfr.py:84`](../cfr/algorithms/vanilla_cfr.py) |
| RM+ + linear averaging | Phase 1 §6 bug fix history |
| Strategy averaging vs last-iterate | Phase 1 §5 |
| Exploitability metric + two-pass BR | Phase 1 §1 + [`tests/test_exploitability.py`](../tests/test_exploitability.py) |
| MCCFR External Sampling | Phase 1 §4.2 + [`cfr/algorithms/mccfr.py`](../cfr/algorithms/mccfr.py) |
| MCCFR asymptotic advantage | mccfr-scaling.md (the whole report) |
| Sampling vs enumeration trade-off | Phase 1 §6 + mccfr-scaling §3 |
| A real collusion detection pipeline | Phase 2 (the whole report) |
| An honest adversarial baseline for synthetic data | Phase 2 §4 two-column table |
| Player-disjoint train/test to avoid leakage | Phase 2 §3 + [`collusion/models/lgbm_classifier.py`](../collusion/models/lgbm_classifier.py) |
| Bug-finding methodology | Phase 1 §6 + commit `d5c42dd` |
| Grounded in the literature (Tammelin / Lanctot / Bowling) | All sources in the three reports |

---

## What we did not prove: flagged honestly

| Concept | Why it was not done |
|---|---|
| Card abstraction (EHS / OCHS / KMeans bucketing) | Never built a bucketing pipeline |
| Action abstraction (required for NLHE) | Not touched |
| Deep CFR / function approximation | Tabular only |
| Subgame solving / nested resolving | Only listed in references.md |
| Public Belief States (ReBeL) | Same as above |
| GPU / CUDA implementation | Only a design doc, no `.cu` written |
| Real Texas Hold'em scale | Excluded by the D2 design |
| Real production data | Excluded by the D6 design |
| Self-play / NFSP | Same as above |
| Multi-player (3+ seat table) CFR | HU only |

When asked about any of the above, **answer honestly "I did the design but did not implement it" or "I read the papers but have not hit the pitfalls"**. That beats bragging.

---

## A cheat sheet: eight numbers to remember + the matching conclusions

```
Accepted Nash values
────────────────────────────────────────────
Kuhn:    -1/18 ≈ -0.0556      (Kuhn 1950, analytic)
Leduc:   -0.0856                (Lanctot 2013 published)

Phase 1 results (canonical enum variants)
────────────────────────────────────────────
Vanilla CFR enum  1000 iter:  expl 0.033, val -0.079
CFR+ enum         1000 iter:  expl 0.001, val -0.078    ← 35× stronger than vanilla
MCCFR Leduc       200k iter:  expl 0.47                 ← unfavorable on a small game

MCCFR scaling results (N-card Kuhn, 20-second budget)
────────────────────────────────────────────
N=3:    enum 4.4e-6  / mccfr 1.5e-3   → enum wins 350×
N=300:  enum 1.8e-2  / mccfr 7.8e-3   → MCCFR turns the tables ✓
N=400:  enum 4.4e-2  / mccfr 8.7e-3   → MCCFR wins 5×

Phase 2 results
────────────────────────────────────────────
with    shared latency:  AUC 0.9995   (decision_time_corr dominates)
without shared latency:  AUC 0.8245   (fold-rate dominates, the more honest number)
```

**Remember these 8 numbers and you can keep up with most technical discussions**. Open the files when you need details.

---

## How to answer common questions

### Q1: "Do you know CFR?"

> "Yes. I implemented vanilla, MCCFR (External Sampling) and CFR+ from scratch,
> including both the chance-sampling and enum variants. On Leduc, CFR+ enum at
> 1000 iter reaches expl 0.001, consistent with the published Tammelin 2014. I
> found two bugs along the way (inline RM+ floor + live strategy reading), both
> by comparing against the OpenSpiel reference."

### Q2: "Why does industry (Libratus, Pluribus) use MCCFR?"

> "I ran a scaling experiment on N-card Kuhn and measured MCCFR starting to beat
> enum CFR+ at around N ≈ 300. The reason is that enum's per-iter cost blows up as
> N², while MCCFR's is constant. What the implementation verified is fully
> consistent with the asymptotic-advantage claim in Lanctot 2009 §1, §6. Real NLHE
> has 10¹⁷ info sets, **far to the right of the crossover**, so MCCFR is the only
> option."

### Q3: "How did you do collusion detection?"

> "Phase 1 trained CFR strategies to serve as the honest players, and I added
> synthetic colluders (soft-fold + chip-dump + no-bluff vs partner). The pipeline
> runs end to end to a LightGBM binary classifier with a player-disjoint split. The
> AUC of 0.9995 is the version with the strong shared-latency signal; **with that
> signal turned off the AUC is still 0.8245**, and the fold-rate features take
> over as the dominant ones. I put the two settings side by side explicitly, and
> **did not hide the caveat**."

### Q4: "Why not just use OpenSpiel?"

> "OpenSpiel is the production-grade choice, but for a research prototype like
> this it would blur 'what exactly did you do'. Implementing from scratch made me
> hit every sign convention, reach probability and Leduc round-boundary edge case,
> and it is also what let me find the inline RM+ floor bug. **This design choice
> is recorded in D3**."

### Q5: "Do you know GPU CFR?"

> **Answer honestly**: "I wrote the Phase 1 design doc (`docs/flashcfr-phase1-design.md`)
> covering the kernel signatures, the SoA memory layout and the kernel-by-kernel
> work order. I did not write any `.cu`, because I had no GPU at hand and the spec
> itself required a PAUSE for review before implementation could start. If I get
> an environment, I have a complete work plan."
>
> **Do not say**: "I can write CUDA" (do not say it if it is not verified)

### Q6: "Are your experiments robust enough?"

> "The Phase 1 enum variants have no RNG and are deterministic; MCCFR uses
> multiple seeds (5 for Kuhn / 3 for Leduc) and takes mean ± std, with every std
> under 7% of the mean. Phase 2 is fully deterministic with seed=0. CI on GitHub
> Actions runs ruff + bandit + a pytest matrix (Python 3.11/3.12) on every PR."

---

## Your own "report maintenance discipline"

After you change any algorithm, **do these four things before committing**:

1. **Run the related tests**: `pytest tests/test_xxx.py`, and confirm there is no regression
2. **Re-run the experiments of the affected reports** (plot script + metrics script)
3. **Update the affected numbers in the reports** (do not let a report say something different from the code)
4. **State the number change clearly in the commit message**: "expl went from 0.033 to 0.001 because of the fix to X"

The maintenance discipline is written into [`../AGENTS.md`](../AGENTS.md): "**every experiment
produces both a chart and a Markdown report**".

---

## One-line closing

The English reports are **responsible for what it is**, and this guide is **responsible for how to read it**. Both should be honest: do not pretend to have done what you did not do, and show clearly what you did.

---

*Last updated: 2026-05-28. Corresponds to the state of reports/ and the code after commit `212877a`.*
