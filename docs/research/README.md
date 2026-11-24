# Research log: heads-up no-limit hold'em for Chipzen.ai

This folder holds the research behind the hold'em bot I am building for the
Chipzen.ai Season 16 heads-up arena (November 2026). It has two kinds of
records: literature studies, and the results of my own experiments. The plan
that ties them together is [roadmap.md](roadmap.md): it opens with where the work
stands and what comes next.

## Literature studies

Each study has one `report.md` (the synthesis, every claim cited with a URL)
and a `notes/` folder with the per-topic research notes the report was built
from. Sources were fetched on the study date. Anything a note could not
confirm is marked as unverified there.

| date | study | question | short answer |
|---|---|---|---|
| 2026-11-21 | [HUNL algorithms frontier](2026-11-21-hunl-algorithms-frontier/report.md) | What is newer than abstracted MCCFR, safe subgame solving and safe exploitation for HUNL in 2024-2026, and what fits 0.5 vCPU, 256 MB and pure Python? | Nothing new beats the classic stack within those limits. The levers are the match-win objective, the push/fold layer and a simulated opponent field built from real replays. |
| 2026-11-21 | [Adaptive agent training](2026-11-21-adaptive-agent-training/report.md) | Which training methods suit an agent that adapts to each opponent within a 30 to 44 hand match: self-play RL, league and PSRO training, fast opponent adaptation, LLM and hybrid agents? | No frontier method is tested at that horizon. The best fit is a size-aware opponent model with a population prior, best responses scored by match-win value, and a safety blend; PPO is useful as a best-response oracle and to amortize the search. |
| 2026-11-22 | [Generalization on Hugging Face](2026-11-22-hf-generalization/notes.md) | Which generalization methods and poker data on Hugging Face fit a policy that generalizes inside its opponent family but not outside it? | Train on the generated opponents the policy loses to (adversarial selection), add families that are not ours (real bots, human hand histories), and keep a test family never trained or selected on. From the HF API and abstracts only. |

Notes per study:

* HUNL algorithms frontier: [equilibrium and search](2026-11-21-hunl-algorithms-frontier/notes/equilibrium_and_search.md), [opponent modeling and exploitation](2026-11-21-hunl-algorithms-frontier/notes/opponent_modeling_exploitation.md), [open-source landscape](2026-11-21-hunl-algorithms-frontier/notes/open_source_landscape.md), [short matches and competitions](2026-11-21-hunl-algorithms-frontier/notes/short_match_and_competitions.md).
* Adaptive agent training: [self-play RL for hold'em](2026-11-21-adaptive-agent-training/notes/self_play_rl_holdem.md), [league and PSRO training](2026-11-21-adaptive-agent-training/notes/league_and_psro.md), [fast opponent adaptation](2026-11-21-adaptive-agent-training/notes/fast_opponent_adaptation.md), [LLM and hybrid agents](2026-11-21-adaptive-agent-training/notes/llm_and_hybrid_agents.md).

## Experiments

[experiments.md](experiments.md) records what I measured myself: the real
match format and field tendencies from Chipzen replays, simulator conformance
with the server, win rates against baselines and replay clones, and the probes
that decided the design. It is updated as new results land.

## How the studies were made

Each study split its question into independent topics. One researcher per
topic searched primary sources (arXiv, conference proceedings, GitHub through
its API for stars, license and last push) and wrote a note. A separate writer
read all notes and wrote the report, preferring the newer notes where they
disagreed and rechecking computed numbers.
