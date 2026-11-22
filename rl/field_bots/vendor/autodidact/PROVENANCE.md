# autodidact

- Repo: https://github.com/autodidactinnovations-dev/poker-arena
- Commit: 334e1480b7b4cc99e0ae9c5297bdbbafa5ac58bf
- License: none (no LICENSE file; vendored for local evaluation only, not for redistribution)
- Fetched: 2026-11-22 (`git clone --depth 1`, outside any repo)
- Which file the Chipzen entry uses: `chipzen_agent.py` runs `PokerArenaBot`, which calls `chipzen_adapter.decide_chipzen`, which converts the Chipzen state to the dev.fun table shape and calls `live_agent.decide_live` (using `strategy.py`), then applies a heads-up preflop filter (`hu_filter`). `live_agent.py` is 3058 lines of dev.fun polling, joins, archives and shadow logs around that one function.
- Chipzen name: not confirmed from the repo. `analysis/shadow_report.py` and the `*_shadow*` files are dev.fun shadow-log readers (a research log of counterfactual rules), not a bot name, so "Shadow" is not mapped to it. The repo plays on Chipzen under a bot id kept in a git-ignored `chipzen.toml`. We map it to the field bot "AutodidactInnovations" only by the repo owner name, which is a guess.

Files taken: `strategy.py` (lines 40 to end; the module docstring is not taken), `live_agent.py` lines 277-2109 (module constants, helpers and `decide_live`) with every full-line comment removed (the vendored file is exactly what was read), `chipzen_adapter.py`.
Not taken: all networking, credentials, archive and shadow-logging code, `main()`, the other strategy versions and tests.

Patches (applied by `tools/vendor_build.py`):
1. `live_core.py` header: stubs for `get_opponent_stats` (returns None, as the adapter did), `my_agent_id`, all `shadow_record_*`, `flop_nopair_verdict`; `S22/S24/S37/S38_SHADOW_ENABLED = False` (the adapter already set S22/S24 and LIVE off; S37/S38 only log and cost an extra 600-trial simulation, no effect on the action); `build_reasoning` copied as is; `EQ_TRIALS = 2000`.
2. `live_core.py`: `trials=2000` became `trials=EQ_TRIALS` (default unchanged).
3. `strategy.py`: `_s24_table()` returned a JSON read from disk (os, open); now `{}` (shadow only). `estimate_equity_ranged` default `trials=600` became `None` -> module constant `RANGED_TRIALS = 600` (default unchanged).
4. `chipzen_adapter.py`: `import live_agent as L` became `from . import live_core as L`; the three `L.* =` lines removed (stubbed in the core); `import strategy as S` relative; the `os.environ` read for CALLDOWN replaced by `CALLDOWN = False` (a test-only mode).
5. Glue `rl/field_bots/autodidact.py` replaces `chipzen_agent.PokerArenaBot` (file logging and websocket runner dropped) and clears the module-level opponent model at each match start (the real entry was one process per match).

Registry names: `autodidact` (unchanged, 2000-trial equity per decision) and `autodidact_fast` (same code with 200 and 150 trials, the only difference).
