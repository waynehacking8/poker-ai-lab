# Chipzen Hold'em bot

Deployment folder for the heads-up No-Limit Hold'em bot of this repo. Pure Python, no
dependency beyond the SDK (`chipzen-bot==0.7.0`).

```
chipzen_bot/
  bot.py            entry point: HoldemBot(Bot) + main(), what the Dockerfile runs
  nlhe/             strategy package (evaluator, ranges, opponent model, decisions)
    data/           preflop_equity.json (169x169 class equities), pushfold.json (CFR+ Nash)
  Dockerfile        python:3.12-slim pinned by digest, non-root uid 10001, no compiled code
  requirements.txt  chipzen-bot==0.7.0
  .dockerignore
```

## How the bot plays

* Preflop, by effective stack. At 15 big blinds or less the small blind shoves or folds
  (or completes) by expected utility against a calling range that starts at the CFR+ Nash
  call table and moves towards what this opponent actually does. From 15 to 40 BB it
  compares jam, call and fold against his range narrowed by his actions. Deeper it opens
  about 70 percent of buttons, 3-bets for value, and calls by pot odds.
* Postflop, Monte Carlo equity against a range rebuilt every decision from everything the
  opponent did this hand (preflop class ranges, then board-strength weights per street,
  draws included). Fold, check, call and several bet or raise sizes are scored with one
  formula that uses his learned fold probability and what he raises with.
* Opponent model: VPIP, raise frequencies, fold to bet (preflop folds included), fold to
  re-raise, shove and call-shove rates, showdown hands. Every rate starts at a prior
  and needs real samples to move.
* Blinds are read from the `post_*` entries of every hand, never cached. Every action is
  checked against `valid_actions`; a short stack with `min_raise > max_raise` shoves
  with `raise` at `max_raise` (there is no `all_in` on the wire). At a table with more
  than two seats it aggregates the opponents instead of reading `opponent_stacks[0]`.

## Check before building

```bash
pip install chipzen-bot
chipzen-sdk validate ./chipzen_bot/ --check-connectivity
docker build -t holdem-bot:test ./chipzen_bot
```

The one validator warning (`os` import) is the same one the SDK starter produces.

## Regenerating the data tables

```bash
python scripts/build_preflop_equity.py --samples 4000 --workers 8   # class equities
python scripts/solve_pushfold.py --iters 3000                       # CFR+ push/fold
python scripts/pushfold_compare.py                                  # vs published Nash
```
