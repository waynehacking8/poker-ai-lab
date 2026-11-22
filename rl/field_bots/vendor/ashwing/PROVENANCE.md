# ashwing

- Repo: https://github.com/Shaurya-S0603/PokerBots (folder `ashwing_sdk/`)
- Commit: dc87080d1030ebf6df900eab2d8938acaf830878
- License: none (no LICENSE file in the repo; vendored for local evaluation only, not for redistribution)
- Fetched: 2026-11-22 (`git clone --depth 1`, outside any repo; every vendored file read in full before use)
- Live on Chipzen as "Ashwing_v2" (README link) = `AshwingV2Bot` in `chipzen_entry.py`, our `ext:ashwing_v2`.

Files taken (from `ashwing_sdk/`): `pokerbots_sdk/{model,river_calls,hive_policy,adaptive_policy,betting_line,equity_policy,strategies,ashwing_policy,search_policy}.py`,
`fast_rank.py`, `equity.py`, `baseline_v4.py`, lines 2-3 and 36-209 of `pokerroom.py` (card constants, `rules`, `highest_hand`;
the game manager is not taken), the bot classes of `chipzen_entry.py` -> `entry.py`, and the JSON in
`training/{competition-policy,streamlit-river-gate,ashwing-blind-blueprint}.json` embedded as `data.py`.
Not taken: `champion_policy.py` and the other training JSON (not used by any registered bot), the Streamlit app, tests.

Patches (applied by `tools/vendor_build.py`):
1. Imports of top-level modules (`equity`, `fast_rank`, `baseline_v4`, `pokerroom`, `poker_engine`) and `pokerbots_sdk.*` became package relative imports.
2. `strategies.py`: `json`/`pathlib` removed; the competition profile comes from `data.COMPETITION_PROFILE` instead of reading the JSON file.
3. `search_policy.py`: `json`/`pathlib`/`lru_cache` removed; the blind blueprint comes from `data.BLIND_RAISE_BB`.
4. `entry.py`: only the bot classes (`CompetitionBot`, `AshwingV2Bot`, `AshwingAdaptiveBot`, `AshwingSearchBot`, `AshwingBot`); the river-gate profile comes from `data.RIVER_GATE`; `argparse`, `asyncio`, `logging`, `os`, `pathlib`, `run_external_bot`, `load_strategy` (importlib) and the network `main` are gone.
5. `pokerroom.py` is cut to the card constants and the hand rules (drops `random`).

Registry names: `ashwing_v2` (AshwingV2Bot), `ashwing_hive` (Hive Mind), `ashwing_value` (Value profile), `ashwing_adaptive`, `ashwing_search`, `ashwing` (AshwingBot, the "Ashwing" policy).
