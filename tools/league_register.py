"""Register an exported candidate in candidates.json on gb10-d and smoke test that it loads.

Run on the box from ~/poker-ai-lab-league:
    python tools/league_register.py <name> <module> <class>
The module file is looked up under candidates/<name>/ (shallowest match, tests excluded); the
directory that contains it becomes the candidate's ``root``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))


def find_root(base: Path, module: str) -> Path:
    rel = Path(*module.split("."))
    hits = [p for pat in (f"{rel}.py", f"{rel}/__init__.py") for p in base.rglob(pat)
            if "tests" not in p.parts and ".git" not in p.parts]
    if not hits:
        raise SystemExit(f"module {module} not found under {base}")
    hit = min(hits, key=lambda p: len(p.parts))
    root = hit
    for _ in range(len(rel.parts) + (1 if hit.name == "__init__.py" else 0)):
        root = root.parent
    return root


def main(name: str, module: str, cls: str) -> None:
    base = HERE / "candidates" / name
    root = find_root(base, module)
    cfg_path = HERE / "candidates.json"
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    cfg[name] = {"root": str(root.relative_to(HERE)), "module": module, "class": cls}
    from league.hosting import RemoteBot  # smoke test: the child must import and construct it

    bot = RemoteBot(root, module, cls, decision_timeout=10)
    try:
        bot.new_match(1)
    finally:
        bot.close()
    cfg_path.write_text(json.dumps(cfg, indent=1) + "\n")
    print(f"registered {name}: root {cfg[name]['root']} module {module} class {cls}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
