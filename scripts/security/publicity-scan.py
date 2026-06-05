#!/usr/bin/env python3
"""Publicity review: block high-severity credential leaks in staged commits.

Public-repo leak gate for a personal dotfiles repo. Scans the git staged ADDED
lines (new content only) for credential patterns, reusing ``PATTERNS`` from
``scan-jsonl-secrets.py`` (DRY). Blocks the commit (exit 1) if any high- or
medium-severity secret is found in to-be-committed content.

Scope note: this repo intentionally embeds absolute paths (``/Users/...``) and
the owner's username throughout (MEMORY.md, CLAUDE.md, references). Those are NOT
treated as leaks here — blocking them would be a constant-fail NO-OP. This gate
targets genuine credential leaks (private keys, cloud keys, GitHub PATs, sk-*
tokens, Bearer tokens, api_key= assignments) that must never reach a public
commit. Only low-severity matches (password= assignments — the documentation
false-positive magnet) are printed as warnings without blocking.

Known limitation: the shared PATTERNS only flag legacy GitHub PATs (``ghp_``);
fine-grained tokens (``github_pat_``/``gho_``/``ghu_``/``ghs_``) are not yet
covered. Strengthen in ``scan-jsonl-secrets.py`` (shared by other callers).

Added-lines only: legacy content is never re-scanned, so introducing this gate
does not retroactively fail on existing files (mirrors the check-new-todo hook).

Skip once: ``LEFTHOOK_EXCLUDE=publicity-review git commit ...``

Origin: /absorb of "Claude Code で自己改善ループを作った話" (sonicgarden,
2026-06-05) — the article's publicity-review gate, translated to a personal
public dotfiles repo (credential-only scope; path/username are accepted-in-repo).
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

_SCANNER = Path(__file__).with_name("scan-jsonl-secrets.py")


def load_patterns() -> list:
    """Load PATTERNS from the hyphen-named sibling scanner module (DRY reuse)."""
    spec = importlib.util.spec_from_file_location("scan_jsonl_secrets", _SCANNER)
    if spec is None or spec.loader is None:
        print(
            f"❌ publicity-review: cannot load patterns from {_SCANNER}",
            file=sys.stderr,
        )
        sys.exit(2)
    mod = importlib.util.module_from_spec(spec)
    # Register before exec so @dataclass in the loaded module can resolve its
    # own module via sys.modules (otherwise dataclasses raises AttributeError).
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return list(mod.PATTERNS)


def staged_added_lines() -> list[tuple[str, str]]:
    """Return [(path, added_line), ...] from the staged diff (added/modified)."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--diff-filter=AM", "-U0"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ publicity-review: git diff failed: {e}", file=sys.stderr)
        sys.exit(2)
    results: list[tuple[str, str]] = []
    current = "?"
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            results.append((current, line[1:]))
    return results


def main() -> int:
    patterns = load_patterns()
    # Block high + medium: medium covers real credentials too (sk-*, Bearer,
    # api_key=...), not just documentation examples — warning-only would let a
    # genuine key leak through. Only low severity (password_assignment) is
    # warn-only: it is the documentation false-positive magnet
    # ("password: changeme"). Skip a real false positive with LEFTHOOK_EXCLUDE.
    blockers = [p for p in patterns if p.severity in ("high", "medium")]
    low = [p for p in patterns if p.severity == "low"]

    blocking: list[tuple[str, str]] = []
    warnings: list[tuple[str, str]] = []
    for path, line in staged_added_lines():
        for pat in blockers:
            if pat.regex.search(line):
                blocking.append((path, pat.name))
                break
        for pat in low:
            if pat.regex.search(line):
                warnings.append((path, pat.name))
                break

    if warnings:
        print(
            "⚠️  publicity-review: low-severity match(es) "
            "in staged content (not blocking):"
        )
        for path, name in warnings[:10]:
            print(f"   {path}: {name}")
        print()

    if blocking:
        print("❌ publicity-review: credential leak in staged content:")
        for path, name in blocking[:10]:
            print(f"   {path}: {name}")
        print()
        print("   公開リポへの commit 前に credential を除去してください。")
        print("   誤検知なら: LEFTHOOK_EXCLUDE=publicity-review git commit ...")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
