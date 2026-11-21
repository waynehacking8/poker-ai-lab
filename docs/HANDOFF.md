# HANDOFF: Chipzen Season 16 hold'em bot

Updated 2026-11-21 15:03 UTC.

## Goal and gate
- Heads-up NLHE bot for Chipzen.ai Season 16. Registration closes Mon 23 Nov 23:59 UTC.
- Ship gate (Wayne): at least 80% match wins against every one of the 23 league opponents,
  each separately, over at least 400 matches (point estimate; report the Wilson lower bound).
  No upload or registration before a candidate passes and a fresh verifier confirms it.
- Design rule (Wayne): adaptation comes from a decision model (online opponent model plus a
  procedure that maximizes match-win probability plus a safety blend), not switched fixed strategies.

## State (league on the corrected engine, `reports/league/leaderboard.md` on holdem-league 955a021)
| entrant | branch / commit | passed | field | weakest |
|---|---|---|---|---|
| rl-17cf03f | holdem-rl 17cf03f | 22/23 | 89.4 | PoetAndCoder clone 79.5 |
| adapt-v1 | holdem-adapt | 22/23 | 86.0 | maniac 74.5 |
| chipzen-102b05e | holdem-chipzen 102b05e | 8/23 | 76.0 | A5 64.0 |
- Maniac best response confirmed: 87.55% [86.0, 88.9] over 2000 matches (holdem-br, `br/bot.py` ManiacBR).
- Blueprint (holdem-blueprint 06b654d): 1/23 alone; safety anchor and range model only.
- Research log: branch `research`, `docs/research/` (pushed, 8e83c3a).

## Branches and worktrees (Desktop)
poker-ai-lab (holdem-chipzen), -league, -rl, -adapt, -br, -blueprint, -search, -research.

## Open work
1. Archetype clones refit without the 10 held-out bots -> `league/data/clones_prior.npz` (league track).
2. RL retrain on the clean clones plus ManiacBR distillation; the long run is launched by the
   orchestrator on gb10-d (`~/poker-ai-lab-rl`), the agent only runs short chunks.
3. adapt-v2: full-hand search horizon for the maniac.
4. Best-response values and arena checks for lag and station_raiser (holdem-br).
5. On a pass: fresh confirmation run with new seeds, verifier, amd64 image build on gb10-d,
   upload through ego-browser, register.

## Traps
- `tools/league_add.sh`: never edit it while a run of it is active (bash reads scripts lazily).
- RL weights are `*.npz` and gitignored: commit with `git add -f`, or the league export has no model.
- numba is not deployable (pure Python plus numpy only on the host).
- chipzen.ai: one fetcher, stop on the first 429 (900 s IP block).
- gb10-d clock is UTC+8.
