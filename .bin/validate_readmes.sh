#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

python3 - <<'PY'
import pathlib
import re
import sys

root = pathlib.Path.cwd()
readmes = sorted(root.rglob("README.md"))
link_pattern = re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')
missing = []

for readme in readmes:
    text = readme.read_text()
    for raw_target in link_pattern.findall(text):
        target = raw_target.strip()
        if not target or target.startswith("#"):
            continue
        if "://" in target or target.startswith("mailto:"):
            continue

        clean_target = target.split("#", 1)[0].split("?", 1)[0]
        if not clean_target:
            continue

        resolved = (readme.parent / clean_target).resolve()
        if not resolved.exists():
            missing.append((readme.relative_to(root), target))

if missing:
    for readme, target in missing:
        print(f"missing  {readme} -> {target}")
    sys.exit(1)

for readme in readmes:
    print(f"ok  {readme.relative_to(root)}")
PY
