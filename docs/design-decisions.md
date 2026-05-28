# Design Decisions

A record of non-obvious choices made while building this prototype, with
the reasoning behind each. Intended to be defensible under technical
interview scrutiny — every choice should have a "why this, why not that".

---

## D1. Why two phases (CFR + collusion) instead of one deep one?

**Decision:** Build vanilla CFR on toy games, then a synthetic collusion
detector — two clearly separated phases.

**Why:** The target job posting lists three responsibilities:
1. CFR / Game Theory algorithms
2. Adversarial AI / opponent modeling
3. Collusion / cheating detection

A prototype that touches **two of three** is a stronger signal than one
that doubles down on a single area. Phase 1 demonstrates algorithmic
fluency; Phase 2 demonstrates the systems-engineering side that
distinguishes someone who could be hired into the role versus someone
who only read the papers.

**Why not deep on one:** A "from-scratch No-Limit Hold'em solver" is
indefensible in interview-prep timeframes — it would either be incomplete
or a thin wrapper on OpenSpiel. A "production collusion system" would
require real game logs we don't have. The two-phase scope is the largest
honest deliverable.

---

## D2. Why toy games (Kuhn, Leduc) instead of Texas Hold'em?

**Decision:** Kuhn Poker (12 info sets) and Leduc Hold'em (~3000 info
sets) only.

**Why:**
- Kuhn has an analytical Nash equilibrium — any implementation bug is
  immediately visible as exploitability not converging to zero.
- Leduc is the standard research benchmark for CFR variants in the
  2007–2015 era — directly comparable to literature numbers.
- Texas Hold'em (No-Limit, even Heads-Up) requires action abstraction,
  card abstraction, multi-week compute, and engineering tricks that are
  the work of multi-person research teams over years.

**Why not Texas Hold'em:** The interview-prep prototype's purpose is to
show I **understand and can implement the algorithms**, not to claim I
re-solved a domain that took CMU teams a decade. Honesty about scope is
a stronger interview signal than fake ambition.

---

## D3. Why pure Python, no OpenSpiel?

**Decision:** Implement game trees and CFR variants from scratch in pure
Python + NumPy.

**Why:**
- A from-scratch implementation forces engagement with every detail —
  reach probabilities, sign conventions, average-vs-current strategy —
  that a wrapper would hide.
- Reviewers can read 200 lines of Kuhn + CFR code and verify correctness
  in 5 minutes. They cannot do that with an OpenSpiel call.
- Toy games are small enough that no library is needed for performance.

**Why not OpenSpiel:** Using OpenSpiel would invite the interview
question "what did you actually write?" with no defensible answer. The
moment the prototype lives or dies on OpenSpiel internals, the
demonstration value collapses.

**Caveat:** OpenSpiel is the right choice for serious research. This
prototype is a learning artifact, not research.

---

## D4. Why CPU only, no GPU?

**Decision:** Phase 1 and Phase 2 run on a laptop CPU.

**Why:**
- Tabular CFR on Kuhn converges in seconds; on Leduc in minutes. GPU
  adds zero value at this scale.
- LightGBM is CPU-optimal — gradient boosting was designed for CPU
  cache locality.
- A reviewer cloning the repo should be able to reproduce results
  without GPU access. Lowering the barrier increases the chance the
  reviewer actually runs the code.

**Why not GPU:** Adding CUDA would only matter for Deep CFR or a GNN
collusion detector — both are listed as **stretch goals** in the
roadmap, not the core deliverable. Including them in the core would
risk an unfinished GPU module dominating the repo's first impression.

---

## D5. Why LightGBM (not XGBoost / Random Forest / Neural Net)?

**Decision:** LightGBM for the collusion detector baseline.

**Why:**
- **Sparse pairwise behavioral features** (fold-against-partner rate,
  simultaneous fold rate, etc.) are tabular — gradient boosting is the
  empirically dominant family for tabular learning.
- **Interpretability** matters in fraud detection — `lgbm.plot_importance`
  is a one-liner that tells reviewers which features actually drove
  detection. Neural nets require SHAP / LIME on top.
- **Training time** under 30 seconds on synthetic data → fast iteration
  during prototyping.

**Why not XGBoost:** LightGBM and XGBoost are functionally
interchangeable for this scale. LightGBM was chosen for the slightly
nicer histogram-based training and built-in categorical support.

**Why not deep learning:** Tabular data + small sample sizes + need for
interpretability = boosted trees. Neural nets would be defensible but
would not improve detection materially while sacrificing interpretability.

---

## D6. Why synthetic collusion data?

**Decision:** Generate honest games (using CFR-trained policies) and
inject simulated colluding pairs, rather than using a public poker
dataset.

**Why:**
- No public dataset labels collusion at the player-pair level — it would
  be a violation of platform privacy to release.
- Synthetic data has perfect ground truth — every game knows whether
  it contained colluders, so detection ROC curves are unambiguous.
- The simulation logic itself is part of the artifact: "I understand
  poker enough to know what realistic collusion looks like" is a
  domain-knowledge signal.

**Limitations being explicit about:**
- Real-world colluders are adversarial — they will adjust to evade
  detection. Synthetic colluders here follow a fixed strategy.
- Real data has noise our simulator does not model (laggy clients,
  random disconnects, etc.).
- Feature importances learned on synthetic data may not transfer to
  production without recalibration.

---

## D7. Why bilingual docs (English README, mixed-language code comments)?

**Decision:** Public-facing README in English. Internal notes
(`docs/cfr-notes.md`) in English. Some Chinese in personal annotations.

**Why:**
- The repo's reviewers may be Mandarin-speaking (Taiwan job market) or
  English-speaking (international collaborators on the company's team).
  English README maximizes reach.
- Code comments are English-only for portability.
- Notes that are clearly personal-study artifacts may have Chinese
  passages — they reflect the actual learning process and don't pretend
  otherwise.

---

## D8. Why "Phase 1 / Phase 2" framing instead of monolithic feature list?

**Decision:** Explicit phase decomposition in the README, with each phase
having its own deliverable and timeline.

**Why:**
- Reviewers can stop reading after Phase 1 and still get a complete
  picture — Phase 1 is self-contained.
- Sets honest expectations about what's done versus what's planned;
  prevents "the README promised X" surprises.
- Shows project-management thinking — scoping work into shippable
  increments is itself an engineering skill.

---

## D9. Why include this `design-decisions.md` file?

**Decision:** Include a public design-decisions document with no special
formatting or polish.

**Why:**
- The most common interview failure mode at this seniority is "I built
  it but can't explain why I made the choices I made". A written record
  forces clear thinking and provides reviewers a starting point.
- Reviewers who read this file before interviewing me will have better
  questions; the interview becomes more productive.
- For my own future reference — six months from now, "why did I pick
  LightGBM?" should not be a mystery.

---

## D10. Why stack many 4-player sessions instead of one 4-player session?

**Decision:** The Phase 2 LightGBM AUC test runs **40 independent
4-player sessions of 2 000 hands each** and stacks the labelled pairs
(`run_many_sessions`), rather than the single `4-player × 10 000-hand`
configuration literally stated in
`docs/specifications-phase2.md` §6.

**Why:** With four players there are only `C(4, 2) = 6` labelled pairs
per session. A binary classifier with player-disjoint train/test split
on 6 examples is curve-fitting, not learning — and the spec's own
acceptance criterion (`AUC ≥ 0.85`) cannot be evaluated honestly at
that scale. Stacking 40 sessions with namespaced player IDs (offset
`session_idx × num_players`) gives 240 labelled pairs and ~40 distinct
colluder assignments, which is the smallest setup that supports a
defensible held-out AUC.

**Why not increase `num_players` to 20+ within a single session:** A
single session has only one colluder assignment. Generalisation across
configurations needs many assignments, not many players. Twenty
players in one session would test "can the model find these specific
2 colluders" rather than "can it recognise colluders in general".

**Why not change the spec instead:** The spec's §6 figures are the
contract for the AUC test threshold. Loosening the spec would erode a
useful regression boundary. Adding a second helper
(`run_many_sessions`) preserves the spec's per-session shape and
documents the deviation in one place.

---

## D11. Why a shared-latency factor as the dominant detection signal?

**Decision:** Colluding partners' synthetic decision latencies are
drawn from a **shared per-hand base** (`Normal(1.5, 0.3)`) plus tiny
i.i.d. noise (`Normal(0, 0.05)`); honest pairs' latencies are
independent. The pair-level feature `decision_time_corr` therefore
sits near 0.97 for colluders and near 0 otherwise — and ends up
contributing ~98 % of the Phase 2 classifier's gain.

**Why:** `docs/specifications-phase2.md` §4 calls out
`decision_time_corr` as a feature with the explicit annotation
"placeholder: synthetic latencies". The simulator has to *generate*
those latencies — there is no real-world packet capture to draw from.
Modelling the partners as briefly synchronised (one player waits while
the other thinks) is the simplest realistic mechanism, and it gives
the classifier a high-signal feature to validate the rest of the
pipeline against.

**Acknowledged limitations** (documented in
`reports/phase2-collusion-detection.md` §5):

- Real adversaries deliberately uncorrelate their input cadence.
- AUC drops sharply on the spec's "subtle collusion" setting
  (`soft_fold_prob = 0.3`, no latency correlation) — this is expected
  and is the reason for the §5 caveat rather than a hidden bug.

**Why not omit the feature:** Even with the placeholder caveat, the
feature schema is a contract. Dropping a feature would diverge from
the spec; rolling our own (which we did) preserves it.

---

## D12. Why FP32 everywhere in FlashCFR Phase 1?

**Decision:** `docs/flashcfr-phase1-design.md` specifies FP32 for both
`regret_sum` and `strategy_sum`, deferring the spec's mixed-precision
recommendation to Phase 2 / Phase 3.

**Why:**
- Kuhn's regret table is 24 floats. Halving to 12 floats saves no
  meaningful memory bandwidth on a problem that fits in a single
  warp's registers.
- The CPU reference is FP32; comparing GPU FP32 to CPU FP32 is a
  straight equality test (up to seeded RNG divergence). Mixed
  precision would introduce a numerical-tolerance dimension on top of
  the algorithmic-correctness one, making bug hunting harder.
- The acceptance gate for Phase 1 is "match CPU baseline exploitability
  within 0.005". Mixed precision adds variance that uses up that
  budget for no gain at Kuhn scale.

**Why not now:** Mixed precision pays for itself on Leduc / HU Limit
where the regret table size starts to dominate bandwidth. That's
Phase 2 / Phase 3. The Phase 1 design doc records this as an open
choice to revisit there — see `flashcfr-spec.md` "Key Design Decisions
to Make Upfront" §2.

---

## D13. Why `.py` chart scripts instead of Jupyter notebooks?

**Decision:** `docs/roadmap.md` 1.7 originally called for three
notebooks (`convergence_kuhn.ipynb`, `strategy_comparison.ipynb`,
`leduc_results.ipynb`). Replaced with two `.py` scripts
(`scripts/plot_convergence_{kuhn,leduc}.py`) that write PNGs to
`results/` and a Markdown report under `reports/`.

**Why:**
- `.ipynb` JSON includes cell outputs (image bytes, stderr, run
  timestamps) that mutate on every execution and produce noisy diffs
  even when no code changed.
- The chart scripts are importable, parameterisable from the CLI
  (`--iters`, `--out`), and run unchanged in CI alongside the rest of
  the test suite.
- The "reading notes" value of a notebook is captured better by
  `reports/phase1-convergence.md` (versioned prose) and the PNGs
  (versioned charts) than by a long `.ipynb`.

**Why not both:** A notebook variant would just be a thin wrapper
around the same script. Keep the source of truth in one place.

**Caveat:** A future "experiment narrative" deliverable (showing the
strategy converging info-set by info-set with side-by-side tables)
genuinely benefits from notebook format. If that's ever wanted, add
it then — not preemptively.
