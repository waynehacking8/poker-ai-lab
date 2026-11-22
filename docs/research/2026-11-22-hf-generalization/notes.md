# Generalization methods and data on Hugging Face (2026-11-22)

All entries were fetched on 2026-11-22 from the Hugging Face API:
`/api/papers/search`, `/api/papers/<id>`, `/api/models?search=poker`,
`/api/datasets?search=poker`, `/api/datasets/<id>` and the dataset READMEs.
The claims about methods come from the abstracts only. I have not read the
full papers.

## Methods that map onto our problem

The problem: the policy generalizes inside our opponent family but not
outside it (`../experiments.md` sections 14 and 14.1).

* **GOAT** (arXiv 2504.15457, 2025). A pretrained generative model produces
  valid partner policies. Adversarial training then searches its latent
  space for the partners the learner does worst against, maximizing regret.
  Training on those improves generalization to new humans.
  * Our mapping: `tools/gen_clones.py` is the generative model. The clone
    parameters (archetype mix plus style tilts) are its latent space. Search
    them for the opponents the current policy loses to, then train on those.
    No code is published.
* **Metamon** (arXiv 2504.04395, 2025, github UT-Austin-RPL/metamon). Large
  real human replay data, plus sequence models that adapt to the opponent in
  context, plus offline RL, reaches human level in Pokemon. Mapping: real
  human hand histories as a broad opponent family (data below).
* **VGC-Bench** (arXiv 2506.10326, 2025). A benchmark for generalizing
  across diverse strategies, with self-play, fictitious play, double oracle
  and behavior-cloning baselines. Its framing matches ours: train on some
  team configurations, test on unseen ones.
* **QARL** (arXiv 2311.01642, 2023). An entropy-regularized adversary gives a
  quantal response equilibrium, and the curriculum raises the adversary's
  rationality from random to rational. Mapping: a curriculum of opponent
  strength.
* **NeuPL** (arXiv 2202.07415, 2022). One conditional network represents the
  whole population of best responses, with transfer across them.
* **Population-based evaluation in repeated RPS** (arXiv 2303.03196, 2023).
  Evaluation against a fixed population of held-out hand-coded bots. Our
  test family plays the same role.
* **AAArena / Adversarial Heuristic Learning** (arXiv 2610.12341, Oct 2026,
  github THU-CST-SAST/AAArena). LLM agents revise executable game programs
  from replays within fixed match budgets, over 12 games and 1,920 human
  programs. "Opus5.5 with Claude Code earns 6 gold medals", and no setup tops
  the other 6 ladders.
* **RevengeBench** (arXiv 2606.26094, Jun 2026). It rebuilds a hidden
  rule-based policy as code from behavior traces plus designed probe
  opponents. Mapping: code-space clones of the Chipzen field bots instead of
  tabular clones.

## Data

* **takara-ai/poker_hands** and **gabbler/PokerData** (CC-BY-4.0). 21,605,687
  no-limit hold'em hands from HandHQ logs, July 2009, 25NL to 1000NL, in the
  PHH format (PokerKit). These are human players. The heads-up share is
  unknown.
* **dannyobito/arena-pokerkit-hands** (CC-BY-4.0, 10K to 100K hands). 6-max
  NLHE played by 19 AI agents on the dev.fun Arena (LLMs, open-source solver
  bots, equity heuristics), May 2026.
* **RZ412/PokerBench** (Apache-2.0). About 500k postflop and preflop spots
  with solver-optimal actions (arXiv 2501.08328). This could be an
  equilibrium anchor, but the spots come from 6-max games at 100 bb.
* **Models.** Nearly all are LLM fine-tunes, for example the PokerBench SFT
  and GRPO models and Genaro-poker. None fits 0.5 vCPU and 200 ms, and none
  is an RL policy we could use as an opponent at volume.

## What I take from it

1. **Pick opponents adversarially, not uniformly (GOAT).** Inside the
   plausible generated family, train on the opponents the current policy
   loses to. This is a cheap outer loop: every round, screen many candidates
   in the C engine and keep the hardest.
2. **Add a family that is not ours.** The real Blueprint and the real Chipzen
   bots are the competent outside families. Human hand histories are the
   broad one. Fitting per-player clones from HandHQ needs a PHH parser and a
   heads-up filter, so it is a larger job.
3. **Keep a test family that is never trained on or selected on**
   (population-based evaluation, VGC-Bench).
