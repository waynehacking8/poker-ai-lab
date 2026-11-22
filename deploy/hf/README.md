---
license: mit
library_name: numpy
pipeline_tag: reinforcement-learning
tags:
- reinforcement-learning
- poker
- texas-holdem
- no-limit-holdem
- ppo
- game-ai
---

# poker-ai-lab HUNL policy (fb2-900)

This is the heads-up no-limit Texas hold'em bot I entered in [Chipzen.ai](https://chipzen.ai) Season 16 as
`poker-ai-lab-v3`. It is a small PPO policy network that runs on numpy alone, so it fits the arena's CPU sandbox
without a GPU or a deep learning framework.

Source and training code: [github.com/waynehacking8/poker-ai-lab](https://github.com/waynehacking8/poker-ai-lab/tree/holdem-rl)
(branch `holdem-rl`, commit `56c4419`).

## Model

* A multilayer perceptron: 56 input features, two hidden layers of 256 units with ReLU, and 6 action logits.
  81,926 float32 parameters.
* Actions: fold, check or call, raise half the pot, raise the pot, raise two pots, all in. Illegal actions are
  masked out before sampling.
* Inputs: hand strength (preflop class equity, postflop win share against a random hand, made hand category,
  draws, board texture), pot odds, both stacks in big blinds, the blind level and hands until it rises, the betting
  so far in the hand, and ten running statistics of the opponent in the current match (how often they open, fold
  to a raise, reraise, fold or raise after the flop, go to showdown, and so on).
* The opponent statistics are how it adapts. The network reads them on every decision, so its play shifts as it
  learns the opponent during a match. There is no switching between fixed strategies.
* Speed: the slowest decision across 9,600 test matches took 15 ms on one CPU core.

## Training

I trained it with PPO on a C reimplementation of the Chipzen match rules: 10,000 chip stacks, blinds starting at
50/100 and rising every 20 hands, and the match goes on until one side has all the chips. The opponents were:

* six archetype bots, seven simple baselines and behavior clones of ten bots fitted to public Chipzen replays;
* earlier snapshots of the policy itself;
* real open-source Chipzen bots run through the SDK (Ashwing v2, Ashwing value, Ashwing adaptive and a fast
  autodidact build), plus my older heuristic bot.

The real bots mattered most. The behavior clones overstated my win rate by 20 to 30 points compared with the real
bot code, and training against the real code carried over to bots I never trained against.

This checkpoint is iteration 900 of the second run against the real bots, which started from the first run's
iteration 900. A third run from here started to overfit the training bots, so I stopped it.

## Evaluation

The win rate is the share of full matches won, 400 matches per opponent.

**Test league, 23 opponents, fresh seeds** (200 seed pairs, both seats, never used to pick a checkpoint):

| group | opponents | mean | weakest |
|---|---|---|---|
| archetype bots | 6 | 90.8% | 84.8% |
| clones of Chipzen bots | 10 | 92.8% | 86.3% |
| baselines | 7 | 94.0% | 86.3% |

The mean over all 23 is 92.6%. The lowest Wilson 95% lower bound is 80.9%. Against my older heuristic bot it wins
70.3% of matches (lower bound 65.6%).

**Real open-source bots:**

| opponent | win rate | 95% interval |
|---|---|---|
| Wolf (four versions) | 96.0% to 97.0% | lower bounds 93.6% to 94.8% |
| SDK reference bot | 98.5% | 96.8% to 99.3% |
| Ashwing | 74.5% | 70.0% to 78.5% |
| Ashwing search | 72.0% | 67.4% to 76.2% |
| Ashwing hive | 85.0% | 81.2% to 88.2% |
| Ashwing v2 (a training opponent) | 85.3% | 81.4% to 88.4% |
| autodidact (full build) | 75.5% | 71.1% to 79.5% |
| Blueprint (100bb blueprint from an open-source poker solver) | 62.3% | 57.4% to 66.9% |

Only Ashwing v2 was a training opponent. The other bots in this table were held out.

How the three entries compare on the held-out real bots:

| | h4-300 (clones only) | fb1-900 | fb2-900 (this model) |
|---|---|---|---|
| Ashwing, search and hive, mean | 57.4% | 71.3% | 77.2% |
| autodidact | 63.7% | 71.8% | 75.5% |
| Blueprint | 55.5% | 59.3% | 62.3% |

## Limitations

* It plays heads-up only, and it is tuned to the Chipzen stack size and blind schedule. Other formats are out of
  distribution.
* Blueprint is the closest thing to a solver it was tested against, and it wins only 62% there. Expect a strong
  equilibrium bot to beat it.
* Play is stochastic at temperature 1. Pass `temperature=0` for the argmax action.

## Files

| path | what it is |
|---|---|
| `rl/models/weights.npz` | the weights the runtime loads |
| `model.safetensors` | the same tensors in safetensors format |
| `rl/runtime.py` | numpy inference |
| `rl/features.py` | the 56 features and the opponent tracker |
| `rl/bot.py` | the Chipzen SDK `Bot` wrapper |
| `nlhe/` | hand evaluator and preflop tables |
| `bot.py` | the Chipzen entry point |

## Usage

Run it as a Chipzen bot:

```bash
pip install -r requirements.txt     # chipzen-bot 0.7.0, numpy 2.2.6
CHIPZEN_WS_URL=<match url> CHIPZEN_TOKEN=<token> python bot.py
```

Or call the policy directly:

```python
from rl.runtime import Policy

policy = Policy("rl/models/weights.npz", temperature=0)
action = policy.act(obs, mask)  # obs: 56 floats from rl.features.build, mask: 6 legal flags
```
