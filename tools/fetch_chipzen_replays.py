"""Fetch completed Chipzen heads-up poker replays from the public API, politely.

Writes one JSON file per match, {"match": ..., "replay": ...}, the shape
tools/analyze_chipzen_replays.py reads. Skips matches already on disk, waits
DELAY seconds between requests, and stops at the first HTTP 429 (Chipzen
blocks the IP for 15 minutes after a burst, see tools/README.md).

Usage:
    python tools/fetch_chipzen_replays.py OUT_DIR [MAX_MATCHES] [DELAY]
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://chipzen.ai/api/matches"
HEADERS = {"User-Agent": "poker-ai-lab-research/0.1"}


def get(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main(out_dir: str, max_matches: int = 400, delay: float = 3.0) -> int:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    saved = skipped = 0
    page = 1
    try:
        while saved + skipped < max_matches:
            listing = get(f"{BASE}/?game_type=poker&status=completed&page={page}&page_size=50")
            time.sleep(delay)
            matches = listing.get("matches", [])
            if not matches:
                break
            for m in matches:
                if saved + skipped >= max_matches:
                    break
                # Heads-up only: two bot participants.
                if len(m.get("participants", [])) != 2:
                    continue
                path = out / f"{m['id']}.json"
                if path.exists():
                    skipped += 1
                    continue
                replay = get(f"{BASE}/{m['id']}/replay")
                time.sleep(delay)
                path.write_text(json.dumps({"match": m, "replay": replay}), encoding="utf-8")
                saved += 1
                if saved % 20 == 0:
                    print(f"saved {saved} (page {page})", flush=True)
            page += 1
    except urllib.error.HTTPError as err:
        print(f"stopped on HTTP {err.code} at page {page}: {err.read()[:200]!r}", flush=True)
        return 1 if err.code == 429 else 2
    finally:
        print(f"done: saved {saved}, already had {skipped}", flush=True)
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    sys.exit(main(args[0], int(args[1]) if len(args) > 1 else 400,
                  float(args[2]) if len(args) > 2 else 3.0))
