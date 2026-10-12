#!/usr/bin/env python3
"""cccc complexity gate — cognitive / cyclomatic thresholds on changed files.

Uses moznion/cccc (https://github.com/moznion/cccc) when available.
Inspired by https://x.com/andrestaltz/status/2107716212071485875

Triggered by: hooks.Stop
Output:
  - missing binary / no changed sources → silent skip (fail-open)
  - threshold exceeded → {"decision":"block","reason":...}
  - otherwise → empty / no stdout

Advisory crash handling: fail_closed=False (unexpected errors must not
freeze Stop). Intentional threshold failures block via JSON decision.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import get_emitter, run_hook

emit = get_emitter()

# Staltz tweet defaults; overridden by repo-root cccc.toml when present.
DEFAULT_MAX_COGNITIVE = 40
DEFAULT_MAX_CYCLOMATIC = 40

# Extensions cccc routes today (keep in sync with moznion/cccc README).
SUPPORTED_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mts", ".cts", ".mjs", ".cjs",
    ".rs", ".go", ".php", ".rb",
    ".scm", ".ss", ".sld", ".rkt", ".rktl", ".rktd",
    ".lisp", ".lsp", ".cl", ".el", ".clj", ".cljs", ".cljc",
    ".kt", ".kts", ".py", ".pyi", ".zig",
    ".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx", ".h++",
    ".tpp", ".ipp", ".pl", ".pm", ".t", ".swift", ".java", ".dart",
    ".scala", ".sc", ".cs", ".csx", ".vb",
}

_SKIP_DIRS = {
    "node_modules", "vendor", ".git", "dist", "build", "__pycache__",
    ".next", "target", ".venv", "venv",
}

_TEST_MARKERS = (
    "_test.go", ".test.", ".spec.", "test_", "_test.py",
    "/tests/", "/__tests__/", "/testdata/",
)

_MAX_COG_RE = re.compile(r"^\s*max-cognitive\s*=\s*(\d+)\s*$", re.M)
_MAX_CYC_RE = re.compile(r"^\s*max-cyclomatic\s*=\s*(\d+)\s*$", re.M)


def _find_cccc() -> str | None:
    """Resolve cccc binary; allow CCCC_BIN override for tests / custom installs."""
    override = os.environ.get("CCCC_BIN", "").strip()
    if override:
        ok = os.path.isfile(override) and os.access(override, os.X_OK)
        return override if ok else None
    return shutil.which("cccc")


def _repo_root() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _get_changed_files() -> list[str]:
    """Working-tree + staged + untracked paths relative to repo root."""
    files: set[str] = set()
    commands = (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--name-only", "--cached"],
        # New files agents create are often still untracked.
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    for args in commands:
        try:
            out = subprocess.check_output(
                args, stderr=subprocess.DEVNULL, text=True, timeout=5,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            continue
        files.update(line for line in out.strip().splitlines() if line)
    return sorted(files)


def _is_skippable(path: str) -> bool:
    parts = Path(path).parts
    if any(d in _SKIP_DIRS for d in parts):
        return True
    lowered = path.replace("\\", "/")
    if any(m in lowered for m in _TEST_MARKERS):
        return True
    return Path(path).suffix.lower() not in SUPPORTED_EXTENSIONS


def _resolve_thresholds(repo_root: str) -> tuple[int, int, list[str]]:
    """Return (max_cognitive, max_cyclomatic, cccc CLI config args)."""
    for name in ("cccc.toml", ".cccc.toml"):
        cfg = os.path.join(repo_root, name)
        if not os.path.isfile(cfg):
            continue
        text = Path(cfg).read_text(encoding="utf-8")
        cog = DEFAULT_MAX_COGNITIVE
        cyc = DEFAULT_MAX_CYCLOMATIC
        m = _MAX_COG_RE.search(text)
        if m:
            cog = int(m.group(1))
        m = _MAX_CYC_RE.search(text)
        if m:
            cyc = int(m.group(1))
        return cog, cyc, ["--config", cfg]
    return (
        DEFAULT_MAX_COGNITIVE,
        DEFAULT_MAX_CYCLOMATIC,
        [
            "--no-config",
            f"--max-cognitive={DEFAULT_MAX_COGNITIVE}",
            f"--max-cyclomatic={DEFAULT_MAX_CYCLOMATIC}",
        ],
    )


def _collect_offenders(
    report: dict, max_cog: int, max_cyc: int,
) -> list[str]:
    """Human-readable lines for functions over threshold."""
    lines: list[str] = []
    for file_entry in report.get("files") or []:
        path = file_entry.get("path", "?")
        for fn in file_entry.get("functions") or []:
            cog = int(fn.get("cognitive") or 0)
            cyc = int(fn.get("cyclomatic") or 0)
            if cog <= max_cog and cyc <= max_cyc:
                continue
            name = fn.get("name") or "<anonymous>"
            line = fn.get("line") or "?"
            lines.append(
                f"  - {path}:{line} {name}  "
                f"cognitive={cog} cyclomatic={cyc}"
            )
    return lines


def _run_cccc(
    cccc_bin: str, repo_root: str, config_args: list[str], paths: list[str],
) -> tuple[int, dict | None, str]:
    """Run cccc on paths. Returns (exit_code, parsed_json_or_None, stderr)."""
    cmd = [cccc_bin, *config_args, *paths]
    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 124, None, "cccc timed out after 45s"
    except OSError as exc:
        return 127, None, f"cccc exec failed: {exc}"

    report: dict | None = None
    stdout = (proc.stdout or "").strip()
    if stdout:
        try:
            report = json.loads(stdout)
        except json.JSONDecodeError:
            report = None
    return proc.returncode, report, (proc.stderr or "").strip()


def _emit_block(
    targets: list[str],
    code: int,
    offenders: list[str],
    max_cog: int,
    max_cyc: int,
) -> None:
    emit(
        "cccc_complexity",
        {
            "status": "block",
            "exit_code": code,
            "offender_count": len(offenders),
            "files": targets[:20],
        },
    )
    reason_lines = [
        "[cccc complexity gate] 変更ファイルの複雑度が閾値を超えています",
        f"閾値: max-cognitive={max_cog} / max-cyclomatic={max_cyc}",
        "対象: 今回の git diff 上のソース（テスト・vendor 除外）",
        "",
        "超過関数:",
        *offenders[:20],
    ]
    if len(offenders) > 20:
        reason_lines.append(f"  ... 他 {len(offenders) - 20} 件")
    reason_lines.extend(
        [
            "",
            "FIX: 関数を分割・早期 return・条件の平坦化で複雑度を下げてから完了してください。",
            "手動確認: cccc <changed-files>  （設定は repo 直下 cccc.toml）",
            "無効化 (緊急時のみ): CCCC_GATE_DISABLE=1",
        ]
    )
    json.dump({"decision": "block", "reason": "\n".join(reason_lines)}, sys.stdout)


def _analyze_targets(
    cccc_bin: str, repo_root: str, targets: list[str],
) -> None:
    max_cog, max_cyc, config_args = _resolve_thresholds(repo_root)
    code, report, err = _run_cccc(cccc_bin, repo_root, config_args, targets)

    if code == 0:
        emit("cccc_complexity", {"status": "pass", "files": len(targets)})
        return

    if report is None:
        print(
            f"[cccc-complexity-gate] soft-fail: exit={code} err={err or 'no json'}",
            file=sys.stderr,
        )
        emit(
            "cccc_complexity",
            {"status": "soft_fail", "exit_code": code, "error": err},
        )
        return

    offenders = _collect_offenders(report, max_cog, max_cyc)
    if not offenders:
        summary = report.get("summary") or {}
        cog = (summary.get("cognitive") or {}).get("max", "?")
        cyc = (summary.get("cyclomatic") or {}).get("max", "?")
        offenders = [
            f"  - (summary) cognitive_max={cog} cyclomatic_max={cyc}"
        ]
    _emit_block(targets, code, offenders, max_cog, max_cyc)


def main() -> None:
    if os.environ.get("CCCC_GATE_DISABLE") == "1":
        return

    cccc_bin = _find_cccc()
    if not cccc_bin:
        print(
            "[cccc-complexity-gate] skip: cccc not found "
            "(install: https://github.com/moznion/cccc#install--build)",
            file=sys.stderr,
        )
        return

    repo_root = _repo_root()
    if not repo_root:
        return

    changed = [f for f in _get_changed_files() if not _is_skippable(f)]
    existing = [
        f for f in changed if os.path.isfile(os.path.join(repo_root, f))
    ]
    if not existing:
        return

    _analyze_targets(cccc_bin, repo_root, existing[:80])


if __name__ == "__main__":
    run_hook("cccc-complexity-gate", main, fail_closed=False)
