"""Helpers for reading/writing skills-lock.json with provenance metadata.

Schema (version 2):

    {
      "version": 2,
      "skills": {
        "<name>": {
          "source": "<owner>/<repo>",
          "sourceType": "github",
          "computedHash": "<sha256>",
          "provenance": {
            "source":      "github.com/<owner>/<repo>",
            "ref":         "HEAD" | "<branch>" | "<tag>",
            "commit_sha":  "<sha>" | null,
            "tree_sha":    "<sha>" | null,
            "resolved_at": "<ISO-8601 UTC>" | null
          }
        }
      }
    }

Backward compatibility: version 1 entries without `provenance` are accepted.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

LOCKFILE_VERSION = 2


class Provenance(TypedDict):
    source: str | None
    ref: str
    commit_sha: str | None
    tree_sha: str | None
    resolved_at: str | None


SkillEntry = dict[str, object]
Lockfile = dict[str, object]


class LockfileError(RuntimeError):
    """Raised when the lockfile is missing or malformed."""


def load(path: Path) -> Lockfile:
    if not path.is_file():
        raise LockfileError(f"lockfile not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LockfileError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict) or "skills" not in data:
        raise LockfileError(f"missing 'skills' key in {path}")
    return data


def save(path: Path, data: Lockfile) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()


def _resolve_via_gh(source: str, ref: str) -> tuple[str | None, str | None]:
    """Return (commit_sha, tree_sha). None on failure."""
    try:
        out = subprocess.run(
            ["gh", "api", f"repos/{source}/commits/{ref}"],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        return None, None
    try:
        payload = json.loads(out.stdout)
    except json.JSONDecodeError:
        return None, None
    commit_sha = payload.get("sha")
    tree_sha = (payload.get("commit") or {}).get("tree", {}).get("sha")
    return commit_sha, tree_sha


def _resolve_via_ls_remote(source: str, ref: str) -> str | None:
    """Fallback: return commit_sha via `git ls-remote`."""
    url = f"https://github.com/{source}.git"
    try:
        out = subprocess.run(
            ["git", "ls-remote", url, ref],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        return None
    line = out.stdout.strip().split("\n", 1)[0]
    return line.split("\t", 1)[0] if line else None


def resolve_provenance(source: str, source_type: str, ref: str = "HEAD") -> Lockfile:
    """Return a provenance dict. Fields may be null if resolution fails."""
    entry: Lockfile = {
        "source": f"{source_type}.com/{source}" if source_type == "github" else source,
        "ref": ref,
        "commit_sha": None,
        "tree_sha": None,
        "resolved_at": None,
    }
    if source_type != "github":
        return entry
    commit_sha, tree_sha = _resolve_via_gh(source, ref)
    if commit_sha is None:
        commit_sha = _resolve_via_ls_remote(source, ref)
    entry["commit_sha"] = commit_sha
    entry["tree_sha"] = tree_sha
    if commit_sha is not None:
        entry["resolved_at"] = _utc_now_iso()
    return entry


def ensure_provenance(entry: Lockfile, *, ref: str = "HEAD") -> bool:
    """Add `provenance` to an entry if missing. Returns True if mutated."""
    if "provenance" in entry:
        return False
    source = entry.get("source")
    source_type = entry.get("sourceType", "github")
    if not source:
        entry["provenance"] = {
            "source": None,
            "ref": ref,
            "commit_sha": None,
            "tree_sha": None,
            "resolved_at": None,
        }
        return True
    entry["provenance"] = resolve_provenance(source, source_type, ref=ref)
    return True
