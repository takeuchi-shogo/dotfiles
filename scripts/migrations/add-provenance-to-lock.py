#!/usr/bin/env python3
"""Backfill `provenance` into every entry of skills-lock.json.

Usage:
  python3 scripts/migrations/add-provenance-to-lock.py [--dry-run] [--ref REF]

Resolution strategy:
  1. `gh api repos/<source>/commits/<ref>` -> (commit_sha, tree_sha)
  2. Fallback: `git ls-remote https://github.com/<source>.git <ref>` -> commit_sha
  3. If both fail, nullable fields stay None (resolved_at stays None).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCKFILE = REPO_ROOT / "skills-lock.json"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from lib import skills_lock  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="preview only")
    parser.add_argument(
        "--ref", default="HEAD", help="git ref to resolve (default: HEAD)"
    )
    parser.add_argument("--lockfile", type=Path, default=DEFAULT_LOCKFILE)
    args = parser.parse_args()

    try:
        data = skills_lock.load(args.lockfile)
    except skills_lock.LockfileError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1

    skills = data.get("skills") or {}
    if not isinstance(skills, dict):
        print("[error] 'skills' must be a dict", file=sys.stderr)
        return 1

    added = skipped = failed = 0
    for name, entry in skills.items():
        if not isinstance(entry, dict):
            print(f"[warn] skip (not a dict): {name}", file=sys.stderr)
            skipped += 1
            continue
        if "provenance" in entry:
            skipped += 1
            print(f"skip (provenance exists): {name}")
            continue
        skills_lock.ensure_provenance(entry, ref=args.ref)
        prov = entry["provenance"]
        if prov.get("commit_sha"):
            added += 1
            print(f"added: {name} @ {prov['commit_sha'][:12]}")
        else:
            failed += 1
            print(f"added (unresolved): {name}")

    data["version"] = skills_lock.LOCKFILE_VERSION

    summary = f"added={added}, unresolved={failed}, skipped={skipped}"
    if args.dry_run:
        print(f"\n[dry-run] would update: {summary}")
        return 0

    skills_lock.save(args.lockfile, data)
    print(f"\n[done] {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
