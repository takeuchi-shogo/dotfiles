# AutoEvolve Step 1: Data Collection Foundation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** セッション中のイベント（エラー、品質指摘、ファイル変更）を自動収集し、jsonl に蓄積するデータ基盤を構築する

**Architecture:** 既存の PostToolUse hooks にイベント発火を追加し、Stop/SessionEnd hook で jsonl にフラッシュする。共有モジュール `session_events.py` で書式と I/O を統一。

**Tech Stack:** Python 3, jsonl, 既存 hook インフラ (settings.json)

---

## 前提知識

- hook スクリプトは `dotfiles/.config/claude/scripts/` に置く（symlink で `~/.claude/scripts/` に配置される）
- データは `~/.claude/agent-memory/learnings/` に保存（git 管理外）
- hook の I/O プロトコル:
  - **Stop/SessionEnd**: stdin でデータ受信 → 処理 → stdout にパススルー
  - **PostToolUse**: stdin で JSON `{tool_name, tool_input, tool_output}` → stdout で JSON
- 既存 hook からの import は `Path(__file__).resolve().parent` で解決

---

### Task 1: セッションイベント共有モジュール

**Files:**

- Create: `.config/claude/scripts/session_events.py`
- Test: `tests/scripts/test_session_events.py`

**Step 1: テストファイルのディレクトリを作成**

Run: `mkdir -p tests/scripts`

**Step 2: failing test を書く**

```python
# tests/scripts/test_session_events.py
import json
import tempfile
import os
import sys
from pathlib import Path

# scripts/ をインポートパスに追加
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / ".config" / "claude" / "scripts"))


class TestSessionEvents:
    """session_events モジュールのユニットテスト"""

    def setup_method(self):
        """各テストで一時ディレクトリを使用"""
        self.tmpdir = tempfile.mkdtemp()
        self.original_env = os.environ.get("AUTOEVOLVE_DATA_DIR")
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir

    def teardown_method(self):
        """環境変数を復元"""
        if self.original_env is None:
            os.environ.pop("AUTOEVOLVE_DATA_DIR", None)
        else:
            os.environ["AUTOEVOLVE_DATA_DIR"] = self.original_env

    def test_emit_event_creates_temp_file(self):
        from session_events import emit_event
        emit_event("error", {"message": "TypeError: x is not a function"})
        temp_path = Path(self.tmpdir) / "current-session.jsonl"
        assert temp_path.exists()
        line = temp_path.read_text().strip()
        data = json.loads(line)
        assert data["category"] == "error"
        assert "timestamp" in data

    def test_emit_multiple_events(self):
        from session_events import emit_event
        emit_event("error", {"message": "err1"})
        emit_event("quality", {"rule": "GP-004"})
        temp_path = Path(self.tmpdir) / "current-session.jsonl"
        lines = temp_path.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_flush_session_returns_events_and_cleans_up(self):
        from session_events import emit_event, flush_session
        emit_event("error", {"message": "err1"})
        emit_event("quality", {"rule": "GP-004"})
        events = flush_session()
        assert len(events) == 2
        assert events[0]["category"] == "error"
        temp_path = Path(self.tmpdir) / "current-session.jsonl"
        assert not temp_path.exists()

    def test_flush_empty_session(self):
        from session_events import flush_session
        events = flush_session()
        assert events == []

    def test_append_to_learnings(self):
        from session_events import append_to_learnings
        append_to_learnings("errors", {"message": "test error", "command": "npm run build"})
        learnings_path = Path(self.tmpdir) / "learnings" / "errors.jsonl"
        assert learnings_path.exists()
        data = json.loads(learnings_path.read_text().strip())
        assert data["message"] == "test error"
        assert "timestamp" in data

    def test_append_to_metrics(self):
        from session_events import append_to_metrics
        append_to_metrics({
            "project": "dotfiles",
            "errors_count": 2,
            "quality_issues": 1,
            "files_changed": 3,
        })
        metrics_path = Path(self.tmpdir) / "metrics" / "session-metrics.jsonl"
        assert metrics_path.exists()
        data = json.loads(metrics_path.read_text().strip())
        assert data["project"] == "dotfiles"
        assert "timestamp" in data
```

**Step 3: テストが失敗することを確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest tests/scripts/test_session_events.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'session_events'"

**Step 4: session_events.py を実装**

```python
# .config/claude/scripts/session_events.py
"""AutoEvolve session event collector.

セッション中のイベントを一時ファイルに蓄積し、
セッション終了時に jsonl にフラッシュする共有モジュール。

Usage (from other hooks):
    from session_events import emit_event
    emit_event("error", {"message": "TypeError", "command": "npm test"})
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

# データディレクトリ（テスト時は環境変数で上書き可能）
_DATA_DIR = Path(os.environ.get(
    "AUTOEVOLVE_DATA_DIR",
    os.path.join(os.environ.get("HOME", ""), ".claude", "agent-memory"),
))


def _temp_path() -> Path:
    return _DATA_DIR / "current-session.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit_event(category: str, data: dict) -> None:
    """セッション中のイベントを一時ファイルに追記する。

    Args:
        category: イベント種別 ("error", "quality", "pattern", "correction")
        data: イベント固有のデータ
    """
    path = _temp_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": _now_iso(), "category": category, **data}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def flush_session() -> list[dict]:
    """一時ファイルのイベントを全て読み出し、ファイルを削除する。

    Returns:
        セッション中に蓄積されたイベントのリスト
    """
    path = _temp_path()
    if not path.exists():
        return []
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    path.unlink(missing_ok=True)
    return events


def append_to_learnings(filename: str, data: dict) -> None:
    """learnings/ ディレクトリに jsonl エントリを追記する。

    Args:
        filename: ファイル名（拡張子なし）。例: "errors", "patterns"
        data: 記録するデータ
    """
    path = _DATA_DIR / "learnings" / f"{filename}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": _now_iso(), **data}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def append_to_metrics(data: dict) -> None:
    """metrics/ ディレクトリにセッションメトリクスを追記する。

    Args:
        data: セッションの統計データ
    """
    path = _DATA_DIR / "metrics" / "session-metrics.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": _now_iso(), **data}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

**Step 5: テストを実行して全件パスを確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest tests/scripts/test_session_events.py -v`
Expected: 6 passed

**Step 6: コミット**

```bash
git add .config/claude/scripts/session_events.py tests/scripts/test_session_events.py
git commit -m "✨ feat: add session event collector module for AutoEvolve"
```

---

### Task 2: session-learner.py（Stop/SessionEnd hook）

**Files:**

- Create: `.config/claude/scripts/session-learner.py`
- Test: `tests/scripts/test_session_learner.py`

**Step 1: failing test を書く**

```python
# tests/scripts/test_session_learner.py
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / ".config" / "claude" / "scripts"))


class TestSessionLearner:
    """session-learner.py の処理ロジックのテスト"""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir

    def teardown_method(self):
        os.environ.pop("AUTOEVOLVE_DATA_DIR", None)

    def test_build_session_summary_with_events(self):
        # セッション中にイベントを蓄積
        from session_events import emit_event
        emit_event("error", {"message": "TypeError", "command": "npm test"})
        emit_event("error", {"message": "ReferenceError", "command": "node app.js"})
        emit_event("quality", {"rule": "GP-004", "file": "src/app.ts"})

        from session_learner import build_session_summary
        summary = build_session_summary(cwd="/tmp/test-project")

        assert summary["errors_count"] == 2
        assert summary["quality_issues"] == 1
        assert summary["project"] == "test-project"

    def test_build_session_summary_empty(self):
        from session_learner import build_session_summary
        summary = build_session_summary(cwd="/tmp/test-project")
        assert summary["errors_count"] == 0
        assert summary["quality_issues"] == 0
        assert summary["total_events"] == 0

    def test_process_flushes_events_to_learnings(self):
        from session_events import emit_event
        emit_event("error", {"message": "TypeError", "command": "npm test"})

        from session_learner import process_session
        process_session(cwd="/tmp/test-project")

        errors_path = Path(self.tmpdir) / "learnings" / "errors.jsonl"
        assert errors_path.exists()

        metrics_path = Path(self.tmpdir) / "metrics" / "session-metrics.jsonl"
        assert metrics_path.exists()

    def test_process_skips_when_no_events(self):
        from session_learner import process_session
        process_session(cwd="/tmp/test-project")

        # メトリクスは空セッションでも記録しない
        metrics_path = Path(self.tmpdir) / "metrics" / "session-metrics.jsonl"
        assert not metrics_path.exists()
```

**Step 2: テストが失敗することを確認**

Run: `python3 -m pytest tests/scripts/test_session_learner.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'session_learner'"

**Step 3: session-learner.py を実装**

```python
# .config/claude/scripts/session-learner.py
#!/usr/bin/env python3
"""AutoEvolve session learner — flushes session events to persistent storage.

Triggered by: hooks.Stop / hooks.SessionEnd
Input: stdin passthrough (same as session-save.js)
Output: stdout passthrough

セッション中に蓄積されたイベントを集約し、
learnings/*.jsonl と metrics/session-metrics.jsonl に書き出す。
"""
import json
import os
import sys
from pathlib import Path

# 同じディレクトリの session_events をインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from session_events import append_to_learnings, append_to_metrics, flush_session


def build_session_summary(cwd: str | None = None) -> dict:
    """セッションイベントを集約してサマリーを構築する。"""
    events = flush_session()

    errors = [e for e in events if e.get("category") == "error"]
    quality = [e for e in events if e.get("category") == "quality"]
    patterns = [e for e in events if e.get("category") == "pattern"]
    corrections = [e for e in events if e.get("category") == "correction"]

    project = Path(cwd).name if cwd else "unknown"

    return {
        "project": project,
        "cwd": cwd or os.getcwd(),
        "total_events": len(events),
        "errors_count": len(errors),
        "quality_issues": len(quality),
        "patterns_found": len(patterns),
        "corrections": len(corrections),
        "_errors": errors,
        "_quality": quality,
        "_patterns": patterns,
        "_corrections": corrections,
    }


def process_session(cwd: str | None = None) -> None:
    """セッションデータを処理し、永続ストレージに書き出す。"""
    summary = build_session_summary(cwd=cwd)

    # イベントがなければスキップ
    if summary["total_events"] == 0:
        return

    # エラーイベントを learnings/errors.jsonl に記録
    for error in summary["_errors"]:
        entry = {k: v for k, v in error.items() if k != "category"}
        append_to_learnings("errors", entry)

    # 品質指摘を learnings/quality.jsonl に記録
    for issue in summary["_quality"]:
        entry = {k: v for k, v in issue.items() if k != "category"}
        append_to_learnings("quality", entry)

    # パターンを learnings/patterns.jsonl に記録
    for pattern in summary["_patterns"]:
        entry = {k: v for k, v in pattern.items() if k != "category"}
        append_to_learnings("patterns", entry)

    # セッションメトリクスを記録
    metrics = {
        "project": summary["project"],
        "cwd": summary["cwd"],
        "total_events": summary["total_events"],
        "errors_count": summary["errors_count"],
        "quality_issues": summary["quality_issues"],
        "patterns_found": summary["patterns_found"],
        "corrections": summary["corrections"],
    }
    append_to_metrics(metrics)


def main() -> None:
    # stdin を読んでパススルー（hook プロトコル準拠）
    data = sys.stdin.read()
    try:
        process_session(cwd=os.getcwd())
    except Exception as e:
        print(f"[session-learner] error: {e}", file=sys.stderr)
    sys.stdout.write(data)


if __name__ == "__main__":
    main()
```

**Step 4: テストを実行して全件パスを確認**

Run: `python3 -m pytest tests/scripts/test_session_learner.py -v`
Expected: 4 passed

**Step 5: コミット**

```bash
git add .config/claude/scripts/session-learner.py tests/scripts/test_session_learner.py
git commit -m "✨ feat: add session learner hook for AutoEvolve data collection"
```

---

### Task 3: 既存 hook にイベント発火を追加

**Files:**

- Modify: `.config/claude/scripts/error-to-codex.py` — エラー検出時に `emit_event("error", ...)` を追加
- Modify: `.config/claude/scripts/golden-check.py` — 品質違反時に `emit_event("quality", ...)` を追加

**Step 1: error-to-codex.py にイベント発火を追加**

変更箇所: `main()` 関数内、エラー検出後のブロック。
import に `session_events` を追加し、`emit_event` を呼ぶ。

```python
# error-to-codex.py の先頭に追加（既存 import の後）
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from session_events import emit_event as _emit
except ImportError:
    def _emit(*_a, **_kw): pass  # フォールバック: 無視
```

```python
# main() 内、error_match が見つかった後（context_parts の構築前）に追加:
        _emit("error", {
            "message": error_match,
            "command": command[:200],
        })
```

**Step 2: golden-check.py にイベント発火を追加**

golden-check.py を読んで、品質違反検出箇所に同様の `emit_event` を追加する。

```python
# golden-check.py の先頭に追加
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from session_events import emit_event as _emit
except ImportError:
    def _emit(*_a, **_kw): pass
```

違反検出時:

```python
        _emit("quality", {
            "rule": rule_id,  # e.g. "GP-004"
            "file": file_path,
            "detail": violation_detail[:200],
        })
```

**Step 3: 手動テスト — hook が壊れていないことを確認**

Run: `echo '{"tool_name":"Bash","tool_input":{"command":"npm test"},"tool_output":"TypeError: x is not a function"}' | python3 ~/.claude/scripts/error-to-codex.py`
Expected: JSON 出力 + stderr にエラーなし

**Step 4: コミット**

```bash
git add .config/claude/scripts/error-to-codex.py .config/claude/scripts/golden-check.py
git commit -m "✨ feat: integrate event emission into existing hooks"
```

---

### Task 4: settings.json に session-learner を登録

**Files:**

- Modify: `.config/claude/settings.json`

**Step 1: Stop と SessionEnd に session-learner.py を追加**

`settings.json` の `hooks.Stop` と `hooks.SessionEnd` 配列に、既存の `session-save.js` の **後に** 追加:

```json
{
  "type": "command",
  "command": "python3 $HOME/.claude/scripts/session-learner.py"
}
```

**Step 2: JSON の構文チェック**

Run: `python3 -c "import json; json.load(open('$HOME/.claude/settings.json'))"`
Expected: エラーなし

**Step 3: コミット**

```bash
git add .config/claude/settings.json
git commit -m "🔧 chore: register session-learner hook in settings.json"
```

---

### Task 5: ディレクトリ構造の初期化と .gitignore

**Files:**

- Create: `~/.claude/agent-memory/learnings/.gitkeep` (ローカルのみ、git 管理外)
- Create: `~/.claude/agent-memory/metrics/.gitkeep` (ローカルのみ、git 管理外)

**Step 1: ディレクトリを作成**

Run:

```bash
mkdir -p ~/.claude/agent-memory/learnings
mkdir -p ~/.claude/agent-memory/metrics
mkdir -p ~/.claude/agent-memory/insights/project-profiles
```

**Step 2: 既に .gitignore でカバーされていることを確認**

`~/.claude/agent-memory/` は dotfiles 外（symlink されていない）なので git 管理外。追加の .gitignore は不要。

**Step 3: スキップ（コミット不要 — ローカル操作のみ）**

---

### Task 6: エンドツーエンド検証

**Step 1: イベント発火テスト**

```bash
# エラーイベントを手動発火
AUTOEVOLVE_DATA_DIR=~/.claude/agent-memory python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/scripts')
from session_events import emit_event
emit_event('error', {'message': 'test error', 'command': 'echo test'})
emit_event('quality', {'rule': 'GP-004', 'file': 'test.py'})
print('Events emitted')
"
```

Expected: `~/.claude/agent-memory/current-session.jsonl` にイベントが記録される

**Step 2: フラッシュテスト**

```bash
echo "" | python3 ~/.claude/scripts/session-learner.py
```

Expected:

- `~/.claude/agent-memory/learnings/errors.jsonl` にエラーが記録
- `~/.claude/agent-memory/learnings/quality.jsonl` に品質指摘が記録
- `~/.claude/agent-memory/metrics/session-metrics.jsonl` にメトリクスが記録
- `~/.claude/agent-memory/current-session.jsonl` が削除される

**Step 3: 記録内容を確認**

```bash
cat ~/.claude/agent-memory/learnings/errors.jsonl
cat ~/.claude/agent-memory/metrics/session-metrics.jsonl
```

Expected: 正しい JSON 行が含まれる

**Step 4: 全テストを実行**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest tests/scripts/ -v`
Expected: All passed

**Step 5: コミット（最終確認用、テストのみの変更があれば）**

---

## 完了条件

- [x] `session_events.py` がイベントの emit / flush / learnings 書き出し / metrics 書き出しをサポート
- [x] `session-learner.py` が Stop/SessionEnd で自動的にデータをフラッシュ
- [x] 既存 hook (error-to-codex, golden-check) がイベントを発火
- [x] settings.json に hook 登録済み
- [x] ユニットテスト全件パス
- [x] エンドツーエンド検証完了

## 次のステップ (Step 2: 知識整理)

Step 1 の基盤が動いたら、蓄積されたデータを分析・整理する:

- `autolearn` agent: jsonl を分析してパターン抽出
- `knowledge-gardener` agent: 知識の整理・重複排除
- daily-report 拡張: 「今日の学び」セクション
