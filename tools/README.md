# tools

Scripts around the Chipzen replays. The replays themselves live in `.cache/chipzen-replays`
(gitignored), one JSON file per match, shaped `{"match": ..., "replay": ...}`.

* `python tools/fetch_chipzen_replays.py OUT_DIR [MAX_MATCHES] [DELAY]` downloads completed
  heads-up poker replays from the public API, skipping files already on disk.
* `OUT=~/chipzen-replays bash tools/fetch_chipzen_all.sh` runs that fetcher in passes until a pass saves
  nothing: the whole public archive, over days. On HTTP 429 it waits 30 minutes and resumes.
* `python tools/analyze_chipzen_replays.py .cache/chipzen-replays` prints the match format
  (blind steps, match lengths) and field tendencies.
* `python tools/match_ceiling.py [chipzen_bot/nlhe/data/preflop_equity.json]` solves the
  fold-or-shove dynamic program against the maniac and prints a lower bound on the best
  achievable match win rate.
* `python tools/replay_conformance.py [REPLAY_DIR] [--show N]` replays every real NLHE hand
  through `holdem/engine.py` and lists each hand where the engine asks something else, offers
  other actions, posts other blinds or ends with other stacks (exit code 1 on any difference).
  `tests/test_replay_conformance.py` runs the same check and skips without the replay folder.
  The replays are not synced by `scripts/holdem_remote.sh`; copy `.cache/chipzen-replays` to
  `~/poker-ai-lab-sim/.cache/` on the box once to run it there.

## Rate limit

Chipzen blocks the IP for 900 s after a burst of requests. Keep at least 3 s between
requests, stop on the first HTTP 429, and run one fetcher at a time.
