# HANDOFF: Chipzen Season 16 hold'em bot

Updated 2026-11-21 22:35 UTC.

## Goal and gate
- Heads-up NLHE bot for Chipzen.ai Season 16. Registration closes Mon 23 Nov 23:59 UTC.
- Ship gate (Wayne): at least 80% match wins against every one of the 23 league opponents,
  each separately, over at least 400 matches (point estimate; report the Wilson lower bound).
  Added 2026-11-21 (Wayne): the shipped bot must also beat the old heuristic bot (holdem-chipzen
  102b05e) head to head: at least 400 matches, Wilson 95% lower bound above 50%.
  No upload or registration before a candidate passes both and a fresh verifier confirms it.
- Design rule (Wayne): adaptation comes from a decision model (online opponent model plus a
  procedure that maximizes match-win probability plus a safety blend), not switched fixed strategies.

## State (league on the corrected engine, `reports/league/leaderboard.md` on holdem-league 1c74fbd)
| entrant | branch / commit | passed | field | weakest |
|---|---|---|---|---|
| rl-h4-300 (SHIPPED) | holdem-rl 5493fc6 | 23/23 | 88.8 | A5 83.2 (fresh seeds 80.2); heuristic h2h 69.8 (fresh 67.5) |
| rl-distill1 | holdem-rl 22b46de | 23/23 | 91.5 | qwentom-leap clone 85.0; heuristic h2h 43.0 |
| adapt-v2 | holdem-adapt 4a4b419 | 23/23 | 89.4 | SolvencyCheck clone 80.8; heuristic h2h 29.5 |
| rl-17cf03f | holdem-rl 17cf03f | 22/23 | 89.4 | PoetAndCoder clone 79.5 |
| adapt-v1 | holdem-adapt | 22/23 | 86.0 | maniac 74.5 |
| chipzen-102b05e | holdem-chipzen 102b05e | 8/23 | 76.0 | A5 64.0 |
- Maniac best response confirmed: 87.55% [86.0, 88.9] over 2000 matches (holdem-br, `br/bot.py` ManiacBR).
- Blueprint (holdem-blueprint 06b654d): 1/23 alone; safety anchor and range model only.
- Research log: branch `research`, `docs/research/` (pushed, 8e83c3a).

## Branches and worktrees (Desktop)
poker-ai-lab (holdem-chipzen), -league, -rl, -adapt, -br, -blueprint, -search, -research.

## Uploaded (2026-11-21 22:15 UTC)
- Chipzen bot `poker-ai-lab`, image `.cache/images/holdem-rl-h4-300.tar.gz`,
  sha256 b6f08ac739d92dd283375c82b76c3e096d5dc0eeab96f2403a6a87c5f0efff92 (weights md5 cc78a8aa...).
- Review passed (ACTIVE). Warm-ups on the real server: won all 3 (DeepStack, Kimiko, glambot), no timeouts.
- ENTERED in Season 16 at 22:32 UTC. The site allows swapping in another uploaded bot until
  registration closes (Mon 23 Nov 23:59 UTC). Fixtures are published at the close.
- Verifier (fresh seeds, pairs 200 to 399): CONFIRMED. Thin margin: A5 321/400 = 80.2% (LB 76.1).

## Open work
1. Only if a candidate beats rl-h4-300 on both gates with margin (fresh seeds): upload it and swap the entry.
2. heur4 long run on gb10-d (`ckpt/heur4`, screener `tools/heur_watch.sh`, summary in
   `logs/heur_watch/summary.jsonl`). it600 failed A5 (77.7). A5 is the weak spot as heuristic training grows.
3. Optional round 4: widen the A5 margin without losing the heuristic head to head.
4. Image builds: `deploy/build_on_box.sh <model npz> <tag>` on holdem-rl (4d50c2a fixes root-owned cleanup).

## Traps
- `tools/league_add.sh`: never edit it while a run of it is active (bash reads scripts lazily).
- RL weights are `*.npz` and gitignored: commit with `git add -f`, or the league export has no model.
- numba is not deployable (pure Python plus numpy only on the host).
- chipzen.ai: one fetcher, stop on the first 429 (900 s IP block).
- gb10-d clock is UTC+8.
