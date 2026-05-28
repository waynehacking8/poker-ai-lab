# References

Curated reading list for this prototype, roughly ordered from
"required-to-read" → "background" → "advanced / stretch".

---

## Required reading

These are the papers whose algorithms are directly implemented or
referenced in the code.

### CFR family

1. **Zinkevich, Bowling, Johanson, Piccione (2007)**
   *Regret Minimization in Games with Incomplete Information.* NeurIPS.
   — The original CFR paper. Read sections 1–4; the theorem statement
   in Section 3 is the foundation.

2. **Lanctot, Waugh, Zinkevich, Bowling (2009)**
   *Monte Carlo Sampling for Regret Minimization in Extensive Games.*
   NeurIPS. — Introduces External Sampling, Outcome Sampling, Chance
   Sampling. Read sections 2–4.

3. **Tammelin (2014)**
   *Solving Heads-Up Limit Hold'em Poker.* arXiv:1407.5042. — CFR+
   algorithm. Read sections 2–3 for the three improvements.

4. **Brown & Sandholm (2017)**
   *Superhuman AI for Heads-Up No-Limit Poker: Libratus Beats Top
   Professionals.* Science. — System paper, light on math. Read for the
   "blueprint + nested subgame solving" architecture.

5. **Brown & Sandholm (2019)**
   *Superhuman AI for Multiplayer Poker.* Science (Pluribus). — Read
   for action abstraction and the surprising training-cost numbers.

### Collusion detection

6. **Smed, Knuutila, Hakonen (2007)**
   *Can We Detect Collusion in Online Poker?* — Older paper but a
   useful framing of the problem. Public PDF online.

7. **Yampolskiy & Govindaraju (2008)**
   *Strategy-Based Behavioural Biometrics: a Novel Approach to
   Automated Identification.* — Player-identity via betting patterns.

8. **Patent US7604541B2**
   *System and Method for Detecting Collusion in Online Gaming via
   Conditional Behavior.* — Industry baseline; read for what features
   matter in practice.

---

## Background reading

For readers new to the area, these provide intuition before tackling the
primary papers.

- **Int8 blog — Counterfactual Regret Minimization for Poker AI** (web).
  Best Chinese/English intro to CFR I've found; visualizes the algorithm
  on Kuhn Poker step by step.
- **Hart & Mas-Colell (2000)** *A Simple Adaptive Procedure Leading to
  Correlated Equilibrium.* — The Regret Matching paper, predates CFR.
- **Osborne & Rubinstein, *A Course in Game Theory*** — Standard
  textbook for Nash equilibrium, extensive-form games, information sets.
  Chapters 11–12 cover the relevant material.

---

## Self-play / RL (Chapter 4 of the interview note)

- **Heinrich & Silver (2016)**
  *Deep Reinforcement Learning from Self-Play in Imperfect-Information
  Games.* arXiv:1603.01121. — Neural Fictitious Self-Play (NFSP).
- **Lanctot et al. (2017)**
  *A Unified Game-Theoretic Approach to Multiagent Reinforcement
  Learning.* NeurIPS. — PSRO framework.
- **Brown, Bakhtin, Lerer, Gong (2020)**
  *Combining Deep Reinforcement Learning and Search for
  Imperfect-Information Games.* NeurIPS. — ReBeL. Reframes CFR as the
  subgame solver inside an AlphaZero-style self-play training loop over
  Public Belief States (PBS).
- **Schmid et al. / DeepMind (2021 arXiv, 2023 Science Advances)**
  *Player of Games.* arXiv:2112.03178. — A single algorithm that wins at
  chess, Go, HUNL poker, and Scotland Yard via Growing-Tree CFR (GT-CFR)
  + self-play value/policy network. The direct technical ancestor of
  Obscuro (2025).

---

## Imperfect-information AI: 2022–2026 lineage

These papers extend the canonical CFR / RL stack and are the basis of the
"field evolution" narrative in `docs/field-evolution.md`. Reading them
elevates the prototype's framing from "CFR on toy games" to "the same
algorithmic family that drives 2026 SOTA systems".

### 5.5 (insert) — Cicero (Meta, 2022)

- **Bakhtin et al. (2022)**, *Human-level play in the game of Diplomacy
  by combining language models with strategic reasoning.* Science, Nov
  2022. — First AI to reach human-level play on full-press Diplomacy.
  Architecture: **piKL planner** (policy-iterated KL-regularized regret
  minimization) + 2.7B LM (intent-conditioned dialogue) + intent /
  alignment filter. Significant beyond Diplomacy: it is the first
  successful "**LLM as surface, game-theoretic planner as decider,
  filter as alignment**" three-layer architecture — the same pattern
  later re-derived in poker by ToolPoker (ICLR 2026).

### 5.5–5.10 — Post-Pluribus systems

- **Zhao et al. (AAAI 2022)** *AlphaHoldem: High-Performance
  Artificial Intelligence for Heads-Up No-Limit Texas Hold'em from
  End-to-End Reinforcement Learning.* — Pure end-to-end deep RL with a
  pseudo-siamese architecture; bypasses CFR and human-engineered card
  abstraction entirely. Single PC, 3 days, 2.9 ms / decision.
  Demonstrates that the "drop CFR, train end-to-end" thesis works on
  HUNL, while sacrificing the exploitability guarantee.

- **Various authors (2023+)** *PokerGPT* family. — Lightweight
  RLHF-tuned LLM playing poker via prompt-formatted state. Claimed to
  beat Slumbot; later largely refuted by ToolPoker (ICLR 2026), which
  finds pure LLMs consistently lose to NFSP and CFR+ due to heuristic
  reasoning, factual errors, and a "knowing-doing gap".

- **Zhang & Sandholm (2025)** *General search techniques without common
  knowledge for imperfect-information games, and application to
  superhuman Fog of War chess.* arXiv:2506.01242. — **Obscuro** is the
  first superhuman AI on Fog of War (dark) chess, a game whose **common-
  knowledge set reaches ~10¹⁸**, breaking the PBS assumption that ReBeL
  / DeepStack rely on. Key innovation: **one-sided GT-CFR**, which
  expands only one player's information-set tree, dodging the
  common-knowledge explosion. Same group as Libratus (2017) — an
  unbroken eight-year research line.

- **Kubicek, Lisy, Sandholm (2026)** *Equilibrium Refinements Improve
  Subgame Solving in Imperfect-Information Games.* arXiv:2601.17131. —
  Observes that gadget games used in safe subgame solving typically
  have **infinitely many Nash equilibria** that are equivalent in the
  gadget yet behave very differently in the original game. Adopting
  **sequential equilibrium** (Kreps & Wilson 1982) as the solution
  concept reduces overall exploitability by **>50%**. Demonstrates that
  the CFR theoretical line is still live in 2026.

- **Anon (2026)** *How Far Are LLMs from Professional Poker Players?
  Revisiting Game-Theoretic Reasoning with Agentic Tool Use.* ICLR
  2026. — Introduces **ToolPoker**: an LLM that does not decide actions
  but instead calls an external CFR-based solver and translates GTO
  output to natural-language justification. Empirically refutes the
  optimistic claims of PokerGPT-class systems. Same architecture as
  Cicero (2022) — two independent research lines converge on the same
  conclusion four years apart.

### Why these papers matter for this prototype

The prototype implements **vanilla CFR + MCCFR** on toy games — exactly
the same algorithmic family that, scaled up and combined with
neural-network value functions, drives Libratus / DeepStack / ReBeL /
Player of Games / Obscuro. The 2022–2026 papers above show:

1. CFR is not obsolete — **Equilibrium Refinements (2026)** is a fresh
   theoretical improvement on the very same subgame solving used in
   Libratus (2017).
2. The pure-end-to-end-RL alternative (AlphaHoldem) sacrifices
   exploitability guarantees in exchange for speed; the trade-off is
   live, not settled.
3. The LLM-only alternative (PokerGPT) failed; the hybrid pattern
   (Cicero-style, ToolPoker-style) is what works.

Reading these in sequence — Pluribus → ReBeL → AlphaHoldem → Cicero →
Player of Games → Obscuro → Equilibrium Refinements → ToolPoker —
recapitulates the field's reasoning over the last decade. See
`docs/field-evolution.md` for the narrative version.

---

## Modern RL trends (background for the broader interview prep)

- **Schulman et al. (2017)** PPO. arXiv:1707.06347.
- **Rafailov et al. (2023)** DPO. arXiv:2305.18290.
- **DeepSeek-AI (2025)** R1 / GRPO. arXiv:2501.12948.
- **Sebastian Raschka — *The State of LLMs 2025*** (blog). Best
  high-altitude survey of the RLHF → DPO → GRPO trajectory.

---

## Tools and libraries

- **OpenSpiel (DeepMind)** — Reference implementations for benchmarking.
  Intentionally NOT used in this prototype (see `design-decisions.md` D3),
  but the right choice for serious research.
- **PokerKit (Park et al., 2023)** — Comprehensive poker simulation
  toolkit. Useful for No-Limit work.
- **LightGBM docs** — https://lightgbm.readthedocs.io/

---

## Suggested reading order

If approaching this area fresh:

1. Int8 blog (CFR intro) — get intuition.
2. Zinkevich 2007 sections 1–3 — see the algorithm formally.
3. Implement vanilla CFR on Kuhn yourself — code is the best teacher.
4. Lanctot 2009 — once vanilla CFR works.
5. Tammelin 2014 — CFR+ improvements.
6. Skim Libratus / Pluribus papers — see how the toy algorithms scale.
7. Heinrich & Silver 2016 — switch tracks to deep RL self-play.
8. Brown 2020 (ReBeL) — bridge back to CFR.

This is roughly the order I followed while building this prototype.
