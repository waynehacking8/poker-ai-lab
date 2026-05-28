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
  Imperfect-Information Games.* NeurIPS. — ReBeL.
- **DeepMind (2021)** *Player of Games.* arXiv:2112.03178. — Unified
  approach across imperfect/perfect info games.

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
