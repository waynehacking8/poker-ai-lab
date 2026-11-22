"""AST gate for third-party code under rl/field_bots/vendor/ (run before any of it executes). JavaScript files get a token and import scan.

    python tools/check_vendor.py [dir ...]

Fails on any import outside the safe set and on any use of the banned modules and builtins. Relative imports
inside the vendored package are allowed. It parses only; it never imports the files.
"""

from __future__ import annotations

import ast
import os
import sys

SAFE = {"math", "random", "itertools", "functools", "collections", "dataclasses", "typing", "enum", "time",
        "bisect", "heapq", "statistics", "json", "re", "copy", "numpy", "chipzen", "__future__"}
BANNED_NAMES = {"os", "sys", "subprocess", "socket", "urllib", "http", "requests", "pickle", "marshal", "ctypes",
                "importlib", "open", "eval", "exec", "compile", "__import__"}


def check_file(path):
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), path)
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in SAFE:
                    bad.append((node.lineno, f"import {a.name}"))
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and (node.module or "").split(".")[0] not in SAFE:
                bad.append((node.lineno, f"from {node.module} import"))
        elif isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            bad.append((node.lineno, f"use of {node.id}"))
        elif isinstance(node, ast.Attribute) and node.attr in BANNED_NAMES and isinstance(node.value, ast.Name) \
                and node.value.id in BANNED_NAMES:
            bad.append((node.lineno, f"use of {node.value.id}.{node.attr}"))
    return bad


JS_BANNED = ("require(", "child_process", "node:fs", "node:net", "node:http", "node:https", "node:dgram", "node:dns",
             "node:worker_threads", "node:vm", "from 'fs'", "from 'net'", "eval(", "new Function", "import(", "XMLHttpRequest", "fetch(")


def check_js(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    bad = [(0, f"banned token {t}") for t in JS_BANNED if t in text]
    for line in text.splitlines():
        if line.lstrip().startswith("import ") and " from '" in line:
            mod = line.split(" from '")[1].split("'")[0]
            if not (mod.startswith("./") or mod == "node:readline"):
                bad.append((0, f"import {mod}"))
    return bad


def main(argv):
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rl", "field_bots", "vendor")
    dirs = argv or [root]
    failures = 0
    n = 0
    for d in dirs:
        for base, _, files in os.walk(d):
            for name in sorted(files):
                if name.endswith((".py", ".js", ".mjs")):
                    n += 1
                    p = os.path.join(base, name)
                    for line, msg in (check_file(p) if name.endswith(".py") else check_js(p)):
                        failures += 1
                        print(f"{p}:{line}: {msg}")
    print(f"check_vendor: {n} files, {failures} violations")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
