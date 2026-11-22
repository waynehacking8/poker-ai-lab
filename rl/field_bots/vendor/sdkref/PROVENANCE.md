# sdkref

- Repo: https://github.com/chipzen-ai/chipzen-sdk
- Commit: 1cfcb1f82f472c3ca7add324964b1072520ae429
- License: Apache-2.0
- Fetched: 2026-11-22 (`git clone --depth 1`, outside any repo; read in full before use)
- Taken: `examples/reference-bot/bot.py` -> `bot.py` (the module up to the "Entry point" section)

Patches (applied by `tools/vendor_build.py`):
1. Dropped the `asyncio`, `logging`, `os`, `sys` imports and `chipzen.client.run_bot`.
2. Removed the `logger` object and its `logger.info` calls.
3. Removed the entry point (`_amain`, `main`) that read `CHIPZEN_*` env vars and opened the websocket.
