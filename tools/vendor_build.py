"""Rebuild rl/field_bots/vendor/ from pinned third-party clones, applying the recorded patches.

    python tools/vendor_build.py --src <dir with the clones> [--out rl/field_bots/vendor]

The clones are only read as text here, never imported or run. Every patch is an exact string replace that
must match exactly once, so a changed upstream file fails loudly instead of silently diverging. The list of
patches is mirrored in each vendor/<name>/PROVENANCE.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re

HEADER = '"""Vendored from {repo} @ {sha}, patched for the offline arena (see PROVENANCE.md)."""\n\n'


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def sub(text, old, new, what, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit(f"patch '{what}': expected {count} match, found {n}")
    return text.replace(old, new)


def strip_comment_lines(text):
    return "\n".join(l for l in text.split("\n") if l.strip() and not l.lstrip().startswith("#")) + "\n"


# ---------------------------------------------------------------- sdk reference bot
def build_sdkref(src, out, sha):
    t = read(os.path.join(src, "chipzen-sdk/examples/reference-bot/bot.py"))
    head, _, _ = t.partition("# ---------------------------------------------------------------------------\n# Entry point")
    start = head.index("from __future__")
    body = head[start:]
    body = sub(body, "import asyncio\nimport logging\nimport os\nimport sys\nfrom collections import Counter",
               "from collections import Counter", "imports")
    body = sub(body, "from chipzen.client import run_bot\n", "", "client import")
    body = sub(body, 'logger = logging.getLogger("reference-bot")\n', "", "logger")
    body = sub(body, '        logger.info("match_start my_seat=%s", self._my_seat)\n', "", "log 1")
    body = re.sub(r"        logger\.info\(\n.*?\n        \)\n", "", body, flags=re.S)
    assert "logger" not in body, "logger use left"
    write(os.path.join(out, "sdkref/bot.py"), HEADER.format(repo="chipzen-ai/chipzen-sdk", sha=sha) + body.rstrip() + "\n")
    write(os.path.join(out, "sdkref/__init__.py"), "")


# ---------------------------------------------------------------- ashwing
def build_ashwing(src, out, sha):
    root = os.path.join(src, "PokerBots/ashwing_sdk")
    hdr = HEADER.format(repo="Shaurya-S0603/PokerBots (ashwing_sdk)", sha=sha)
    dst = os.path.join(out, "ashwing")

    def put(name, text):
        write(os.path.join(dst, name), hdr + text)

    for name in ("model", "river_calls", "hive_policy", "adaptive_policy"):
        put(name + ".py", read(os.path.join(root, "pokerbots_sdk", name + ".py")))
    put("fast_rank.py", read(os.path.join(root, "fast_rank.py")))
    t = read(os.path.join(root, "pokerbots_sdk/betting_line.py"))
    t = sub(t, "from equity import", "from .equity import", "equity import")
    t = sub(t, "from fast_rank import", "from .fast_rank import", "fast_rank import")
    put("betting_line.py", t)
    t = read(os.path.join(root, "equity.py"))
    t = sub(t, "from fast_rank import", "from .fast_rank import", "fast_rank import")
    t = sub(t, "from pokerroom import ranks, suits", "from .pokerroom import ranks, suits", "pokerroom import")
    put("equity.py", t)
    lines = read(os.path.join(root, "pokerroom.py")).split("\n")
    # lines 2-3 (ranks, suits) and lines 36-209 (cards_on_table, rules, highest_hand); the game manager is not taken
    sel = lines[1:3] + [""] + lines[35:209]
    assert "def highest_hand" in "\n".join(sel) and "def compare" not in "\n".join(sel)
    put("pokerroom.py", "\n".join(sel) + "\n")
    t = read(os.path.join(root, "baseline_v4.py"))
    t = sub(t, "from poker_engine import highest_hand", "from .pokerroom import highest_hand", "engine import")
    put("baseline_v4.py", t)
    t = read(os.path.join(root, "pokerbots_sdk/equity_policy.py"))
    t = sub(t, "from baseline_v4 import", "from .baseline_v4 import", "baseline import")
    t = sub(t, "from equity import", "from .equity import", "equity import")
    put("equity_policy.py", t)
    t = read(os.path.join(root, "pokerbots_sdk/strategies.py"))
    t = sub(t, "import json\nfrom pathlib import Path\n\nfrom baseline_v4 import calling_station\n",
            "from .baseline_v4 import calling_station\nfrom .data import COMPETITION_PROFILE\n", "imports")
    t = sub(t, 'DEFAULT_POLICY = Path(__file__).resolve().parents[1] / "training" / "competition-policy.json"\n'
               'VALUE_PROFILE = EquityProfile(**json.loads(DEFAULT_POLICY.read_text())["profile"])\n',
            "VALUE_PROFILE = EquityProfile(**COMPETITION_PROFILE)\n", "profile")
    put("strategies.py", t)
    t = read(os.path.join(root, "pokerbots_sdk/ashwing_policy.py"))
    t = sub(t, "from equity import", "from .equity import", "equity import")
    t = sub(t, "from fast_rank import", "from .fast_rank import", "fast_rank import")
    t = sub(t, "from pokerbots_sdk.betting_line import", "from .betting_line import", "bl import")
    t = sub(t, "from pokerbots_sdk.equity_policy import", "from .equity_policy import", "ep import")
    t = sub(t, "from pokerbots_sdk.hive_policy import", "from .hive_policy import", "hp import")
    t = sub(t, "from pokerbots_sdk.search_policy import", "from .search_policy import", "sp import")
    put("ashwing_policy.py", t)
    t = read(os.path.join(root, "pokerbots_sdk/search_policy.py"))
    t = sub(t, "from functools import lru_cache\nimport json\nfrom pathlib import Path\n",
            "from .data import BLIND_RAISE_BB\n", "imports")
    t = sub(t, 'BLIND_PATH = Path(__file__).resolve().parents[1] / "training" / "ashwing-blind-blueprint.json"\n', "", "path")
    t = sub(t, '@lru_cache(maxsize=1)\ndef blind_blueprint():\n  return json.loads(BLIND_PATH.read_text())["blind_raise_bb"]\n',
            "def blind_blueprint():\n  return BLIND_RAISE_BB\n", "blueprint")
    put("search_policy.py", t)
    data = {
        "COMPETITION_PROFILE": json.loads(read(os.path.join(root, "training/competition-policy.json")))["profile"],
        "RIVER_GATE": json.loads(read(os.path.join(root, "training/streamlit-river-gate.json"))),
        "BLIND_RAISE_BB": json.loads(read(os.path.join(root, "training/ashwing-blind-blueprint.json")))["blind_raise_bb"],
    }
    text = "".join(f"{k} = {json.dumps(v, indent=2)}\n\n" for k, v in data.items())
    put("data.py", text.rstrip() + "\n")
    # entry: the bot classes of chipzen_entry.py without the argparse / network main
    t = read(os.path.join(root, "chipzen_entry.py"))
    a = t.index("def _cards(cards):")
    b = t.index("def bot_for_strategy")
    classes = t[a:b]
    classes = sub(classes,
                  '    profile = DEFAULT_POLICY.with_name("streamlit-river-gate.json")\n'
                  '    self.profile = RiverCallProfile(**json.loads(profile.read_text()))\n',
                  "    self.profile = RiverCallProfile(**RIVER_GATE)\n", "river profile")
    entry_head = (
        "from random import Random\n\n"
        "from chipzen import Action, Bot\n\n"
        "from .adaptive_policy import ashwing_adaptive\n"
        "from .ashwing_policy import decide as ashwing_decide\n"
        "from .data import RIVER_GATE\n"
        "from .equity_policy import equity_bot\n"
        "from .hive_policy import adaptive_river_value_pressure, hive_mind\n"
        "from .model import LineAction, Observation, OpponentBet, validate_decision\n"
        "from .river_calls import RiverCallHistory, RiverCallProfile\n"
        "from .search_policy import ashwing_search\n"
        "from .strategies import value\n\n"
        'SUITS = {"h": "♥️", "d": "♦️", "c": "♣️", "s": "♠️"}\n\n\n')
    put("entry.py", entry_head + classes.rstrip() + "\n")
    write(os.path.join(dst, "__init__.py"), "")


# ---------------------------------------------------------------- autodidact
CORE_HEAD = '''import time

from . import strategy as S

# Offline stubs for everything live_agent.py did over the network or on disk. All of it was observation only
# (opponent stats cache, shadow logs); the adapter in chipzen_agent.py switched the same things off.
S22_SHADOW_ENABLED = False
S24_SHADOW_ENABLED = False
S37_SHADOW_ENABLED = False
S38_SHADOW_ENABLED = False
S22_VETO_ENABLED = True
EQ_TRIALS = 2000


def get_opponent_stats(agent_id):
    return None


def my_agent_id():
    return None


def build_reasoning(equity, pot_odds, action):
    parts = [f'ke: "{equity * 100:.0f}% eq"']
    if action in ("bet", "raise", "all-in"):
        parts.append(f'sr: "pot odds {pot_odds * 100:.0f}%, equity edge"')
    return "{" + ", ".join(parts) + "}"


def _noop(*args, **kwargs):
    return None


shadow_record_fold = shadow_record_flop_nopair = shadow_record_s38 = shadow_record_s24 = _noop
shadow_record_s37 = shadow_record_s22 = _noop


def flop_nopair_verdict(*args, **kwargs):
    return None


'''


def build_autodidact(src, out, sha):
    root = os.path.join(src, "poker-arena")
    hdr = HEADER.format(repo="autodidactinnovations-dev/poker-arena", sha=sha)
    dst = os.path.join(out, "autodidact")
    # strategy.py: drop the unread-for-code module docstring (lines 1-39) and the disk read of the s24 table
    lines = read(os.path.join(root, "strategy.py")).split("\n")
    t = "\n".join(lines[39:])
    t = sub(t, """    global _S24_TABLE
    if _S24_TABLE is None:
        import json, os
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis", "beat_rates.json")
        try:
            _S24_TABLE = json.load(open(p, encoding="utf-8"))
        except Exception:
            _S24_TABLE = {}
    return _S24_TABLE""", """    return {}""", "s24 table")
    t = sub(t, "pending_weight=0.35, trials=600, max_tries=40):",
            "pending_weight=0.35, trials=None, max_tries=40):\n    if trials is None:\n        trials = RANGED_TRIALS", "ranged trials")
    t = sub(t, "import itertools\nimport random\n", "import itertools\nimport random\n\nRANGED_TRIALS = 600\n", "const")
    write(os.path.join(dst, "strategy.py"), hdr + t)
    # live core: live_agent.py lines 277-2109 (module constants, helpers, decide_live), full-line comments removed
    la = read(os.path.join(root, "live_agent.py")).split("\n")
    core = "\n".join(la[276:2109])
    assert core.startswith("_PENDING_WEIGHT_BY_STREET") or core.lstrip().startswith("# How") is False
    core = strip_comment_lines(core)
    core = sub(core, "trials=2000) if len(hole) == 2 else 0.5", "trials=EQ_TRIALS) if len(hole) == 2 else 0.5", "eq trials")
    assert core.rstrip().endswith('"decided_by": "fallback_error_path"}}')
    write(os.path.join(dst, "live_core.py"), hdr + CORE_HEAD + core)
    # adapter
    t = read(os.path.join(root, "chipzen_adapter.py"))
    t = sub(t, "import live_agent as L\n\n# --- isolate from dev.fun -------------------------------------------------\n"
               "L.get_opponent_stats = lambda agent_id: None\nL.S22_SHADOW_ENABLED = False\nL.S24_SHADOW_ENABLED = False\nL.LIVE = False\n",
            "from . import live_core as L\n", "adapter import")
    t = sub(t, "        import strategy as S\n", "        from . import strategy as S\n", "chen import")
    t = sub(t, 'import os\nCALLDOWN = os.environ.get("CHIPZEN_CALLDOWN") == "1"\n', "CALLDOWN = False\n", "calldown")
    write(os.path.join(dst, "chipzen_adapter.py"), t)
    write(os.path.join(dst, "__init__.py"), "")


# ---------------------------------------------------------------- wolf (JavaScript)
SHIM = r"""// JSON-lines shim around the vendored Wolf engine (our code). One JSON object per stdin line, one reply line per
// "decide". No fs, net or child_process: stdin and stdout only. Runs in a --network none container (rl/field_bots/wolf.py).
import { createInterface } from 'node:readline'
import { TableTracker } from './tracker.js'
import { decideAction } from './adapter.js'
import { makeRng } from './rng.js'
import { decide as wolf } from './engine/aiPlayer.js'
import { decide as wolfV5 } from './engine/aiPlayerV5.js'
import { decide as wolfV2 } from './engine/aiPlayerV2.js'
import { decide as wolfV1 } from './engine/aiPlayerV1.js'

const VARIANTS = { wolf, wolf_v5: wolfV5, wolf_v2: wolfV2, wolf_v1: wolfV1 }
const engine = VARIANTS[process.argv[2]]
const budgetMs = Number(process.argv[3] || 100)
if (!engine) throw new Error('unknown variant ' + process.argv[2])
const tracker = new TableTracker()

const rl = createInterface({ input: process.stdin })
rl.on('line', (line) => {
  const m = JSON.parse(line)
  if (m.ev === 'match_start') tracker.onMatch(m.msg)
  else if (m.ev === 'round_start') tracker.newHand(m.msg)
  else if (m.ev === 'round_result') tracker.commitHand(m.msg)
  else if (m.ev === 'decide') {
    const state = m.state
    const rng = makeRng(state.roundId, state.handNumber, state.actionHistory.length)
    const { action, info } = decideAction(state, tracker, rng, engine, budgetMs)
    process.stdout.write(JSON.stringify({ action: action.action, amount: action.amount ?? null, error: info.error ?? null }) + '\n')
  }
})
"""


def build_wolf(src, out, sha):
    root = os.path.join(src, "Chipzen-Poker-Bot/src")
    hdr = "// Vendored from mimaima699-ux/Chipzen-Poker-Bot @ %s (MIT), patched for the offline arena (see PROVENANCE.md).\n" % sha
    dst = os.path.join(out, "wolf")
    for name in ("deck", "handEvaluator", "equity", "aiPlayer", "aiPlayerV1", "aiPlayerV2", "aiPlayerV5"):
        write(os.path.join(dst, "engine", name + ".js"), hdr + read(os.path.join(root, "engine", name + ".js")))
    write(os.path.join(dst, "rng.js"), hdr + read(os.path.join(root, "rng.js")))
    t = read(os.path.join(root, "tracker.js"))
    t = sub(t, """    if (this.diag.turnResults <= 5) {
      console.log(JSON.stringify({ ev: 'raw_turn_result', n: this.diag.turnResults, msg: truncate(message) }))
    }
""", "", "tracker stdout log")
    write(os.path.join(dst, "tracker.js"), hdr + t)
    t = read(os.path.join(root, "adapter.js"))
    t = sub(t, "import { decide } from './engine/aiPlayer.js'\nimport { Action } from '@chipzen-ai/bot'\n",
            "const Action = {\n  raiseTo: (amount) => ({ action: 'raise', amount }),\n  call: () => ({ action: 'call' }),\n"
            "  check: () => ({ action: 'check' }),\n  fold: () => ({ action: 'fold' }),\n}\n", "sdk import")
    t = sub(t, "export function buildCtx(state, tracker, rng, info) {", "export function buildCtx(state, tracker, rng, info, budgetMs = MC_BUDGET_MS) {", "buildCtx")
    t = sub(t, "deadline: Date.now() + MC_BUDGET_MS,", "deadline: Date.now() + budgetMs,", "deadline")
    t = sub(t, "export function decideAction(state, tracker, rng) {", "export function decideAction(state, tracker, rng, decide, budgetMs) {", "decideAction sig")
    t = sub(t, "buildCtx(state, tracker, rng, (x) => Object.assign(info, x))", "buildCtx(state, tracker, rng, (x) => Object.assign(info, x), budgetMs)", "ctx call")
    write(os.path.join(dst, "adapter.js"), hdr + t)
    write(os.path.join(dst, "shim.mjs"), SHIM)
    write(os.path.join(dst, "package.json"), '{"type": "module", "private": true}\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rl/field_bots/vendor"))
    ap.add_argument("--sha", nargs=4, metavar=("SDK", "ASHWING", "AUTODIDACT", "WOLF"), required=True)
    a = ap.parse_args()
    write(os.path.join(a.out, "__init__.py"), "")
    build_sdkref(a.src, a.out, a.sha[0])
    build_ashwing(a.src, a.out, a.sha[1])
    build_autodidact(a.src, a.out, a.sha[2])
    build_wolf(a.src, a.out, a.sha[3])
    print("vendor tree written to", a.out)


if __name__ == "__main__":
    main()
