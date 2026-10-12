#!/usr/bin/env python3
"""cccc complexity gate — thresholds on *changed* functions only.

Uses moznion/cccc (https://github.com/moznion/cccc) when available.
Source: https://x.com/andrestaltz/status/2107716212071485875
  (max-cognitive / max-cyclomatic 40; instruct agents to make cccc pass)

Triggered by: hooks.Stop  |  CLI: --check (exit 1 on block)
Behavior:
  - missing binary → skip (fail-open)
  - changed functions over threshold → JSON decision block (Stop)
    or exit 1 (--check)
  - crash / soft-fail → fail-open (fail_closed=False)
  - MAX_RETRIES=2 then allow stop (completion-gate aligned)
  - stop_hook_active + retries exhausted → allow stop

Only functions that intersect changed lines are gated. Touching one line
in a pre-existing complex file does not block untouched functions.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from hook_utils import get_emitter, run_hook

emit = get_emitter()

# Defaults from https://x.com/andrestaltz/status/2107716212071485875
# Override via repo-root cccc.toml / .cccc.toml when present.
DEFAULT_MAX_COGNITIVE = 40
DEFAULT_MAX_CYCLOMATIC = 40

# Keep subprocess under settings.json Stop hook timeout (45s).
CCCC_TIMEOUT_SEC = 30
MAX_TARGET_FILES = 80
MAX_RETRIES = 2

# Disable cccc's own exit-on-threshold; this gate decides after line filtering.
_DISABLE_CCCC_EXIT = ["--max-cognitive=1000000", "--max-cyclomatic=1000000"]

COUNTER_DIR = os.path.join(tempfile.gettempdir(), "claude-cccc-complexity-gate")
COUNTER_FILE = os.path.join(COUNTER_DIR, "retries")

# Keep in sync with Taskfile validate-cccc / moznion/cccc README.
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

_MAX_COG_RE = re.compile(r"^\s*max-cognitive\s*=\s*(\d+)\s*$", re.M)
_MAX_CYC_RE = re.compile(r"^\s*max-cyclomatic\s*=\s*(\d+)\s*$", re.M)
_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def _find_cccc() -> str | None:
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


def _git_lines(args: list[str], *, cwd: str | None = None) -> list[str]:
    try:
        out = subprocess.check_output(
            args, stderr=subprocess.DEVNULL, text=True, timeout=5, cwd=cwd,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return []
    return [line for line in out.strip().splitlines() if line]


def _get_dirty_files() -> list[str]:
    files: set[str] = set()
    for args in (
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--name-only", "--cached"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        files.update(_git_lines(args))
    return sorted(files)


def _resolve_merge_base() -> str | None:
    for ref in ("origin/master", "master", "origin/main", "main"):
        base_list = _git_lines(["git", "merge-base", "HEAD", ref])
        if base_list:
            return base_list[0]
    return None


def _get_branch_files() -> tuple[list[str], str | None]:
    """Clean-tree fallback. Returns (paths, warning_or_None)."""
    base = _resolve_merge_base()
    if base:
        return _git_lines(["git", "diff", "--name-only", f"{base}...HEAD"]), None
    # Shallow / missing upstream: last-commit fallback, else explicit skip.
    parents = _git_lines(["git", "rev-list", "--parents", "-n", "1", "HEAD"])
    if parents and len(parents[0].split()) >= 2:
        return _git_lines(["git", "diff", "--name-only", "HEAD~1...HEAD"]), (
            "merge-base unavailable; using HEAD~1...HEAD "
            "(shallow clone? fetch origin/master for full branch diff)"
        )
    return [], (
        "merge-base unavailable and no parent commit "
        "(shallow clone?); skipping complexity gate"
    )


def _is_test_path(path: str) -> bool:
    """Match test paths by basename / directory — not substring 'test_'."""
    posix = path.replace("\\", "/")
    parts = Path(posix).parts
    if any(p in {"tests", "__tests__", "testdata"} for p in parts):
        return True
    name = Path(posix).name
    if name.endswith(("_test.go", "_test.py", "_test.rs")):
        return True
    if name.startswith("test_") and name.endswith(".py"):
        return True
    if ".test." in name or ".spec." in name:
        return True
    return False


def _is_skippable(path: str) -> bool:
    if any(d in Path(path).parts for d in _SKIP_DIRS):
        return True
    if _is_test_path(path):
        return True
    return Path(path).suffix.lower() not in SUPPORTED_EXTENSIONS


def _resolve_thresholds(repo_root: str) -> tuple[int, int, list[str]]:
    for name in ("cccc.toml", ".cccc.toml"):
        cfg = os.path.join(repo_root, name)
        if not os.path.isfile(cfg):
            continue
        text = Path(cfg).read_text(encoding="utf-8")
        cog, cyc = DEFAULT_MAX_COGNITIVE, DEFAULT_MAX_CYCLOMATIC
        m = _MAX_COG_RE.search(text)
        if m:
            cog = int(m.group(1))
        m = _MAX_CYC_RE.search(text)
        if m:
            cyc = int(m.group(1))
        return cog, cyc, ["--config", cfg, *_DISABLE_CCCC_EXIT]
    return (
        DEFAULT_MAX_COGNITIVE,
        DEFAULT_MAX_CYCLOMATIC,
        ["--no-config", *_DISABLE_CCCC_EXIT],
    )


def _parse_hunk_lines(diff_text: str) -> set[int]:
    lines: set[int] = set()
    for raw in diff_text.splitlines():
        m = _HUNK_RE.match(raw)
        if not m:
            continue
        start = int(m.group(1))
        count = int(m.group(2) or "1")
        if count <= 0:
            continue
        lines.update(range(start, start + count))
    return lines


def _is_untracked(repo_root: str, path: str) -> bool:
    try:
        subprocess.check_output(
            ["git", "ls-files", "--error-unmatch", "--", path],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return False
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return True


def _changed_lines_for_path(
    repo_root: str, path: str, *, range_spec: str | None,
) -> set[int] | None:
    """Return changed new-side lines, or None for whole-file (untracked/new)."""
    if range_spec is None and _is_untracked(repo_root, path):
        return None
    chunks: list[str] = []
    if range_spec:
        specs = [["git", "diff", "-U0", range_spec, "--", path]]
    else:
        specs = [
            ["git", "diff", "-U0", "HEAD", "--", path],
            ["git", "diff", "-U0", "--cached", "--", path],
        ]
    for args in specs:
        try:
            chunks.append(
                subprocess.check_output(
                    args,
                    cwd=repo_root,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=5,
                )
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            continue
    return _parse_hunk_lines("".join(chunks))


def _changed_lines_map(
    repo_root: str, paths: list[str], *, range_spec: str | None,
) -> dict[str, set[int] | None]:
    return {
        p: _changed_lines_for_path(repo_root, p, range_spec=range_spec)
        for p in paths
    }


def _functions_touching(
    functions: list[dict], changed: set[int] | None,
) -> list[dict]:
    if changed is None:
        return list(functions)
    if not changed:
        return []
    ordered = sorted(functions, key=lambda f: int(f.get("line") or 0))
    touching: list[dict] = []
    for i, fn in enumerate(ordered):
        start = int(fn.get("line") or 0)
        if i + 1 < len(ordered):
            end = int(ordered[i + 1].get("line") or start) - 1
        else:
            end = max(changed) if changed else start
        if end < start:
            end = start
        if any(start <= ln <= end for ln in changed):
            touching.append(fn)
    return touching


def _lookup_changed(
    path: str, lines_by_path: dict[str, set[int] | None],
) -> tuple[str, set[int] | None] | None:
    """Map cccc path (possibly absolute) back to a gated relative path."""
    if path in lines_by_path:
        return path, lines_by_path[path]
    for key, val in lines_by_path.items():
        if path.endswith(key) or key.endswith(path):
            return key, val
    return None


def _collect_offenders(
    report: dict,
    max_cog: int,
    max_cyc: int,
    lines_by_path: dict[str, set[int] | None],
) -> list[str]:
    lines: list[str] = []
    for file_entry in report.get("files") or []:
        path = file_entry.get("path", "?")
        matched = _lookup_changed(path, lines_by_path)
        if matched is None:
            continue
        rel, changed = matched
        touching = _functions_touching(file_entry.get("functions") or [], changed)
        for fn in touching:
            cog = int(fn.get("cognitive") or 0)
            cyc = int(fn.get("cyclomatic") or 0)
            if cog <= max_cog and cyc <= max_cyc:
                continue
            name = fn.get("name") or "<anonymous>"
            line = fn.get("line") or "?"
            lines.append(
                f"  - {rel}:{line} {name}  "
                f"cognitive={cog} cyclomatic={cyc}"
            )
    return lines


def _run_cccc(
    cccc_bin: str, repo_root: str, config_args: list[str], paths: list[str],
) -> tuple[int, dict | None, str]:
    cmd = [cccc_bin, *config_args, *paths]
    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=CCCC_TIMEOUT_SEC,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 124, None, f"cccc timed out after {CCCC_TIMEOUT_SEC}s"
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


def _get_retry_count() -> int:
    try:
        with open(COUNTER_FILE) as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def _set_retry_count(n: int) -> None:
    os.makedirs(COUNTER_DIR, exist_ok=True)
    with open(COUNTER_FILE, "w") as f:
        f.write(str(n))


def _reset_retries() -> None:
    try:
        os.remove(COUNTER_FILE)
    except FileNotFoundError:
        return


def _emit_block(
    targets: list[str],
    offenders: list[str],
    max_cog: int,
    max_cyc: int,
    *,
    truncated: int,
    retries: int,
    cli_check: bool,
) -> int:
    emit(
        "cccc_complexity",
        {
            "status": "block",
            "offender_count": len(offenders),
            "files": targets[:20],
            "truncated": truncated,
        },
    )
    remaining = max(0, MAX_RETRIES - retries - 1)
    reason_lines = [
        "[cccc complexity gate] 変更した関数の複雑度が閾値を超えています",
        f"閾値: max-cognitive={max_cog} / max-cyclomatic={max_cyc}",
        "対象: git diff で触った関数のみ（同一ファイルの未変更関数は対象外）",
        f"リトライ残り: {remaining}回 (上限 {MAX_RETRIES})",
    ]
    if truncated:
        reason_lines.append(
            f"注意: 変更ファイルが多すぎるため先頭 {MAX_TARGET_FILES} 件のみ計測"
            f"（省略 {truncated} 件）"
        )
    reason_lines.extend(["", "超過関数:", *offenders[:20]])
    if len(offenders) > 20:
        reason_lines.append(f"  ... 他 {len(offenders) - 20} 件")
    reason_lines.extend(
        [
            "",
            "FIX: 変更した関数を分割・早期 return・条件の平坦化で下げてから完了してください。",
            "手動確認: task validate-cccc  （設定は repo 直下 cccc.toml）",
            "無効化 (緊急時のみ): CCCC_GATE_DISABLE=1",
        ]
    )
    reason = "\n".join(reason_lines)
    if cli_check:
        print(reason, file=sys.stderr)
        return 1
    json.dump({"decision": "block", "reason": reason}, sys.stdout)
    return 0


def _analyze_targets(
    cccc_bin: str,
    repo_root: str,
    targets: list[str],
    *,
    truncated: int,
    range_spec: str | None,
    retries: int,
    cli_check: bool,
) -> int:
    max_cog, max_cyc, config_args = _resolve_thresholds(repo_root)
    code, report, err = _run_cccc(cccc_bin, repo_root, config_args, targets)

    if report is None:
        print(
            f"[cccc-complexity-gate] soft-fail: exit={code} err={err or 'no json'}",
            file=sys.stderr,
        )
        emit(
            "cccc_complexity",
            {"status": "soft_fail", "exit_code": code, "error": err},
        )
        return 0

    lines_map = _changed_lines_map(repo_root, targets, range_spec=range_spec)
    offenders = _collect_offenders(report, max_cog, max_cyc, lines_map)
    if not offenders:
        emit("cccc_complexity", {"status": "pass", "files": len(targets)})
        if not cli_check:
            _reset_retries()
        return 0

    if not cli_check:
        _set_retry_count(retries + 1)
    return _emit_block(
        targets,
        offenders,
        max_cog,
        max_cyc,
        truncated=truncated,
        retries=retries,
        cli_check=cli_check,
    )


def _select_targets(repo_root: str) -> tuple[list[str], str | None, str | None]:
    """Return (paths, range_spec, warning). range_spec set for clean-tree mode."""
    dirty = [f for f in _get_dirty_files() if not _is_skippable(f)]
    dirty = [f for f in dirty if os.path.isfile(os.path.join(repo_root, f))]
    if dirty:
        return dirty, None, None
    branch, warning = _get_branch_files()
    paths = [
        f for f in branch
        if not _is_skippable(f) and os.path.isfile(os.path.join(repo_root, f))
    ]
    if not paths:
        return [], None, warning
    base = _resolve_merge_base()
    range_spec = f"{base}...HEAD" if base else "HEAD~1...HEAD"
    return paths, range_spec, warning


def _run_gate(*, cli_check: bool, hook_data: dict) -> int:
    if os.environ.get("CCCC_GATE_DISABLE") == "1":
        return 0

    cccc_bin = _find_cccc()
    if not cccc_bin:
        print(
            "[cccc-complexity-gate] skip: cccc not found "
            "(install: https://github.com/moznion/cccc#install--build)",
            file=sys.stderr,
        )
        return 0

    repo_root = _repo_root()
    if not repo_root:
        return 0

    retries = 0 if cli_check else _get_retry_count()
    stop_active = bool(hook_data.get("stop_hook_active"))
    if stop_active:
        print(
            f"[cccc-complexity-gate] stop_hook_active=true "
            f"retries={retries}/{MAX_RETRIES}",
            file=sys.stderr,
        )
    # Align with completion-gate: after MAX_RETRIES blocks, allow stop.
    if not cli_check and retries >= MAX_RETRIES:
        _reset_retries()
        print(
            f"[cccc-complexity-gate] リトライ上限 ({MAX_RETRIES}) 到達。"
            "停止を許可します。",
            file=sys.stderr,
        )
        return 0

    targets, range_spec, warning = _select_targets(repo_root)
    if warning:
        print(f"[cccc-complexity-gate] {warning}", file=sys.stderr)
    if not targets:
        return 0

    truncated = max(0, len(targets) - MAX_TARGET_FILES)
    if truncated:
        print(
            f"[cccc-complexity-gate] truncating targets to "
            f"{MAX_TARGET_FILES} (omitted {truncated})",
            file=sys.stderr,
        )
    return _analyze_targets(
        cccc_bin,
        repo_root,
        targets[:MAX_TARGET_FILES],
        truncated=truncated,
        range_spec=range_spec,
        retries=retries,
        cli_check=cli_check,
    )


def _load_hook_data() -> dict:
    """Read Stop hook JSON from stdin; empty on CLI / capture / parse errors."""
    try:
        if sys.stdin.isatty():
            return {}
        loaded = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError, OSError, TypeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def main() -> None:
    cli_check = "--check" in sys.argv[1:]
    hook_data = {} if cli_check else _load_hook_data()
    code = _run_gate(cli_check=cli_check, hook_data=hook_data)
    if cli_check:
        raise SystemExit(code)


if __name__ == "__main__":
    run_hook("cccc-complexity-gate", main, fail_closed=False)
