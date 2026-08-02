"""dispatch-log.sh の worker 単位ビュー (pending / filter) のテスト。

セッション ID は "日時-$$" でプロセスごとに振られるため、launch と collect を
別コマンドで実行すると 1 つの worker のログが 2 ファイルに分かれる。
worker 単位のサブコマンドが最新 1 ファイルしか読まないと、
「起動済みで未回収の worker」を誰も検出できなくなる。

分析レポート: docs/research/2026-08-03-intent-cli-wake-sources-absorb-analysis.md
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

_SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "runtime" / "dispatch-log.sh"
)

# セッション A: 2 worker を起動しただけ (launch 側プロセスのログ)
_SESSION_LAUNCH = """\
{"ts":"2026-08-03T10:00:00Z","from":"master","to":"w-1-codex","type":"dispatch","model":"codex","task":"レビューして"}
{"ts":"2026-08-03T10:00:01Z","from":"w-1-codex","to":"master","type":"state_change","old_state":"launching","new_state":"running"}
{"ts":"2026-08-03T10:00:02Z","from":"master","to":"w-2-claude","type":"dispatch","model":"claude","task":"実装して"}
{"ts":"2026-08-03T10:00:03Z","from":"w-2-claude","to":"master","type":"state_change","old_state":"launching","new_state":"running"}
"""

# セッション B: 別プロセスで w-1 だけ回収した (collect 側プロセスのログ)
_SESSION_COLLECT = """\
{"ts":"2026-08-03T10:05:00Z","from":"w-1-codex","to":"master","type":"result","status":"completed"}
{"ts":"2026-08-03T10:05:01Z","from":"w-1-codex","to":"master","type":"state_change","old_state":"running","new_state":"completed"}
"""


def _run(subcommand: list[str], log_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(_SCRIPT), *subcommand],
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin", "DISPATCH_LOG_DIR": str(log_dir)},
    )


@pytest.fixture
def log_dir(tmp_path: Path) -> Path:
    (tmp_path / "20260803-100000-111.jsonl").write_text(_SESSION_LAUNCH)
    (tmp_path / "20260803-100500-222.jsonl").write_text(_SESSION_COLLECT)
    return tmp_path


def test_pending_reports_only_uncollected_worker(log_dir: Path) -> None:
    """result が別セッションに書かれていても回収済みと判定する。"""
    result = _run(["pending"], log_dir)
    assert result.returncode == 0, result.stderr
    assert "w-2-claude" in result.stdout
    assert "w-1-codex" not in result.stdout
    assert "未回収 1 件" in result.stdout


def test_pending_is_empty_when_all_collected(tmp_path: Path) -> None:
    (tmp_path / "20260803-100500-222.jsonl").write_text(_SESSION_COLLECT)
    result = _run(["pending"], tmp_path)
    assert result.returncode == 0, result.stderr
    assert "未回収の worker はありません" in result.stdout


def test_pending_fails_without_logs(tmp_path: Path) -> None:
    result = _run(["pending"], tmp_path)
    assert result.returncode == 1
    assert "No log files found" in result.stderr


def test_filter_spans_sessions(log_dir: Path) -> None:
    """launch 側と collect 側に分かれた同一 worker のログを両方拾う。"""
    result = _run(["filter", "--worker", "w-1-codex"], log_dir)
    assert result.returncode == 0, result.stderr
    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    assert len(lines) == 4, result.stdout
    assert any("dispatch" in ln for ln in lines)
    assert any("result" in ln for ln in lines)
