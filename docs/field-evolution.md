# Field Evolution: Imperfect-Information Game AI, 2017–2026

> Why this file exists: a CFR-on-toy-games prototype is easy to read as
> "I implemented an old algorithm". This document re-frames the same
> work inside the field's current paradigm map, so a reviewer can locate
> the prototype on the right axis — and so I can defend that placement
> in interview.

---

## 1. The eight-year arc, in one sentence

> CFR was the obvious answer in 2017 (Libratus / DeepStack), got absorbed
> into RL-style training loops in 2020 (ReBeL), was bypassed by pure RL
> in 2022 (AlphaHoldem) and by LLMs in 2023 (PokerGPT), unified across
> perfect/imperfect information in 2021 (Player of Games), broke through
> the common-knowledge barrier in 2025 (Obscuro), and as of 2026 is
> simultaneously being refined theoretically (Equilibrium Refinements)
> and re-validated as the right backbone underneath LLM interfaces
> (ToolPoker).

---

## 2. Timeline

| Year | System | Core idea | What it told the field |
|------|--------|-----------|------------------------|
| 2017 | **Libratus** (Brown & Sandholm) | MCCFR blueprint + nested subgame solving | CFR + search beats top humans on HUNL |
| 2017 | **DeepStack** (Moravčík et al.) | Continual re-solving with deep counterfactual value networks | NNs can stand in for CFR's leaf evaluations |
| 2019 | **Pluribus** (Brown & Sandholm) | MCCFR blueprint, limited-lookahead search, action abstraction | 6-max poker fell with **$150 of compute** |
| 2020 | **ReBeL** (Brown, Bakhtin, Lerer, Gong) | CFR-as-subgame-solver inside an AlphaZero-style RL loop over **Public Belief States (PBS)** | CFR doesn't get replaced — it gets *embedded* in self-play |
| 2021 | **Player of Games** (DeepMind) | Growing-Tree CFR + value/policy network — works on chess, Go, HUNL, Scotland Yard | One algorithm crosses the perfect / imperfect boundary |
| 2022 | **Cicero** (Meta) | piKL planner + 2.7B LM (intent-conditioned dialogue) + alignment filter, on Diplomacy | First proof that **"LLM = surface, planner = decider, filter = safety"** works |
| 2022 | **AlphaHoldem** (Zhao et al., AAAI) | Pure end-to-end deep RL on HUNL, pseudo-siamese architecture | You *can* bypass CFR — but you lose the exploitability guarantee |
| 2023 | **PokerGPT** (various) | Lightweight RLHF-tuned LLM as the poker decision-maker | First open question: can an LLM *itself* be a competent player? |
| 2025 | **Obscuro** (Zhang & Sandholm) | One-sided GT-CFR, no common-knowledge assumption — superhuman on Fog of War chess | Subgame solving extends beyond games where PBS is tractable |
| 2026 | **Equilibrium Refinements** (Kubicek, Lisy, Sandholm) | Pick sequential equilibria from gadget games — **−50% exploitability** | CFR's theoretical surface is still alive |
| 2026 | **ToolPoker** (ICLR 2026) | LLM as natural-language interface; external CFR-based solver decides | The Cicero pattern reappears in poker — pure LLM play does not work; LLM-as-interface does |

---

## 3. Three live disagreements the field has not settled

These are the questions an interviewer will actually have an opinion on.

### D1. CFR-style solvers vs. pure end-to-end RL

- **CFR camp** (Sandholm / Brown line — Libratus, ReBeL, Obscuro,
  Equilibrium Refinements): the exploitability guarantee is what makes
  the policy *defensible*. Without it you have a poker bot, not a
  solver.
- **RL camp** (AlphaHoldem and follow-ups): empirical win rate is what
  pays; 3 days on one machine beats months of compute, and modern
  self-play schemes are robust enough in practice.
- **Where the field is**: hybrid. CFR-inside-RL (ReBeL / Player of
  Games / Obscuro) is the dominant production direction; pure
  end-to-end RL has not been demonstrated beyond HUNL.

### D2. Public Belief State vs. information-set search

- **PBS camp** (DeepStack, ReBeL, Player of Games): compressing the game
  state into a public-knowledge representation is what lets neural
  networks act as value functions.
- **Information-set camp** (Obscuro 2025): in games like Fog of War
  chess, common-knowledge sets blow up to ~10¹⁸ and PBS becomes
  unusable; one-sided GT-CFR expands only one player's information-set
  tree.
- **Where the field is**: live frontier. Obscuro is the first system to
  break the common-knowledge barrier; whether the technique generalizes
  is the open question.

### D3. LLM as decision-maker vs. as interface

- **Decision-maker camp** (PokerGPT line): a sufficiently large LM,
  fine-tuned with RLHF, can simply *play* the game.
- **Interface camp** (Cicero 2022, ToolPoker 2026): the LM does
  natural-language reasoning and tool use; a symbolic solver
  (CFR-style) decides the action; a filter aligns the two.
- **Where the field is**: as of ICLR 2026, the interface camp is
  empirically ahead. The pattern that Cicero used in Diplomacy was
  re-derived four years later in poker by ToolPoker. This is **the
  single most important "GPT-moment" datapoint** for this field.

---

## 4. Where this prototype sits

This repository implements **vanilla CFR + MCCFR** on **Kuhn Poker**
(12 information sets) and is scoped toward **Leduc Hold'em** (~3000
information sets). Concretely:

- The **regret-matching + counterfactual reach** machinery in `cfr/`
  is the same machinery that lives inside ReBeL's subgame solver and
  Obscuro's one-sided GT-CFR. The data structures are smaller; the
  invariants are identical.
- The **exploitability evaluator** is the same metric that drives the
  Equilibrium Refinements (2026) paper's main result.
- The **separation between current and average strategy** — a common
  bug source for new implementers — is precisely what Tammelin (2014)'s
  CFR+ refines, and what every modern variant carries forward.

The prototype is **not** a Libratus / Pluribus reproduction; it is the
**unit test** for the family those systems are built on. The honest
interview framing: "I implemented the canonical algorithm correctly on
its canonical benchmark, so I can read the modern papers without
hand-waving over the math."

---

## 5. Has this field had its "GPT moment"?

> My answer: no, but Cicero (2022) is its InstructGPT moment.

**Why not GPT yet**:
1. **No scale → emergence axis.** Each new poker / FoW-chess milestone
   wins on a cleverer algorithm, not on raw compute scaling.
2. **No transformer-equivalent substrate.** The mathematical core is
   still 1990s-style CFR; everything since is a patch over it.
3. **No public deployment.** Libratus exists only as a Science paper;
   no one downloads it the way they download ChatGPT.

**Why Cicero is the InstructGPT-equivalent**:
- It is the first system to demonstrate that "LLM + game-theoretic
  planner + alignment filter" works in a non-trivial multi-agent game.
- It generalizes a recipe — the same architecture, four years later,
  works on poker as ToolPoker.
- It hasn't been a *product* (no public Diplomacy bot you can ping),
  which is exactly why it's the precursor and not the moment itself.

**What the GPT moment will probably look like** (best guess, defensible
in interview):
- A general **strategic foundation model** trained on game logs,
  negotiation transcripts, auction data, etc.
- LLM as the natural-language interface; specialized solvers (CFR,
  MCTS, market-clearing, optimization) as tools the LLM calls.
- First commercial deployment likely in **adversarial negotiation /
  auctions / pricing** rather than games per se — the value-per-unit-
  compute is higher.

---

## 6. How this maps to interview talking points

If a reviewer asks "what does this prototype demonstrate":

1. **Algorithmic literacy.** Vanilla CFR + MCCFR + exploitability is the
   reading-comprehension floor for any paper from 2007 to 2026.
2. **Distinguishing knowledge from understanding.** Phase 2 (collusion
   detection) sits in a different paradigm (supervised learning on
   pairwise behavioral features) — showing the difference is part of
   what the prototype demonstrates.
3. **Field awareness.** This file is the artifact that proves it. The
   prototype is the unit; the lineage is the context.

If a reviewer asks "why these papers and not the obvious 2017–2019
trio":

- Implementing the trio is enough for a *correct prototype*. Knowing
  the 2022–2026 papers is what separates "I read your roadmap" from "I
  understand the trajectory your roadmap sits on".

---

## 7. Further reading

- `docs/references.md` — the full paper list with reading order.
- `docs/cfr-notes.md` — reading notes on the foundational CFR papers
  (Zinkevich 2007, Lanctot 2009, Tammelin 2014).
- `docs/design-decisions.md` — why this scope, why these choices.
