# wolf (JavaScript)

- Repo: https://github.com/mimaima699-ux/Chipzen-Poker-Bot
- Commit: e3c107335d344aa0ee894d2d877c5955001aa30d
- License: MIT
- Fetched: 2026-11-22 (`git clone --depth 1`, outside any repo; every vendored file read in full before use)
- Chipzen name: "Wolf Bot" (Season 7 entry per `bot.js`); `src/engine/aiPlayer.js` is the current engine, `aiPlayerV5.js`, `V2`, `V1` older ones.

Files taken: `src/engine/{deck,handEvaluator,equity,aiPlayer,aiPlayerV1,aiPlayerV2,aiPlayerV5}.js`, `src/{rng,tracker,adapter}.js`. Not taken: `bot.js` (imports `@chipzen-ai/bot`, runs the websocket), tests, scripts, Dockerfile.
Hand review: no `require`, `fs`, `net`, `child_process`, `http(s)`, `eval` or `Function` anywhere; the only imports are sibling files and `node:readline` in our shim.

Patches (applied by `tools/vendor_build.py`):
1. `tracker.js`: removed a `console.log` of raw turn results (stdout is the shim protocol channel).
2. `adapter.js`: the `@chipzen-ai/bot` import is replaced by a local plain-object `Action`; `decide` is now a parameter of `decideAction`; the Monte Carlo wall-clock budget is a parameter (`budgetMs`; upstream constant is 300).
3. New (ours, not upstream): `shim.mjs` (JSON lines over stdin/stdout, selects the engine by argv) and `package.json` (`"type": "module"`).

Runs only inside `rl/field_bots/wolf.py`'s container: `docker run --network none --read-only --cap-drop ALL --memory 256m --cpus 1`, folder mounted read-only. The hooks `on_turn_result` and `on_phase_change` do not exist in the local engine, so the tracker profiles opponents from the action history channel (upstream's own documented fallback).

Registry names: `wolf`, `wolf_v5`, `wolf_v2`, `wolf_v1`.
