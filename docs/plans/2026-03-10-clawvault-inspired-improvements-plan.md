---
status: active
last_reviewed: 2026-04-23
---

# ClawVault 着想による Claude Code 設定改善 — 実装計画

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** セッション耐障害性 (Checkpoint)、学習データ品質 (Importance Scoring)、コンテキスト取得の賢さ (Context Profiles) の3レイヤーを既存 hook 設計に非破壊的に追加する。

**Architecture:** 既存の `session_events.py` / `session-save.js` / `agent-router.py` を拡張し、3つの独立レイヤーとして追加。各レイヤーは単独でも動作し、段階的にテスト可能。

**Tech Stack:** Python 3 (hooks), Node.js (hooks), JSON/JSONL (data), Claude Code hook protocol (stdin/stdout JSON)

**設計書:** `docs/plans/2026-03-10-clawvault-inspired-improvements-design.md`

---

## Task 1: Importance Scoring — `session_events.py` 拡張

Layer 2 を最初に実装する。後続の Checkpoint と Context Profiles がスコアを利用するため。

**Files:**

- Create: `.config/claude/references/scoring-rules.md`
- Modify: `.config/claude/scripts/session_events.py`
- Test: `.config/claude/scripts/tests/test_session_events.py`

**Step 1: スコアリングルール reference を作成**

```markdown
# Importance Scoring Rules

## スコアリングモデル

全ての learnings エントリに付与するフィールド:

| フィールド         | 型        | 説明                                      |
| ------------------ | --------- | ----------------------------------------- |
| `importance`       | `0.0-1.0` | 重要度                                    |
| `confidence`       | `0.0-1.0` | スコアの確信度                            |
| `type`             | `string`  | イベント種別                              |
| `scored_by`        | `string`  | `"rule"` or `"llm"`                       |
| `promotion_status` | `string`  | `"pending"` / `"promoted"` / `"archived"` |

## ルールベーススコアリング

### 高重要度 (0.8-1.0)

- `EACCES|Permission denied` → 0.9
- `segfault|SIGSEGV|OOM` → 1.0
- `GP-001|GP-002|GP-003|GP-004|GP-005` → 0.8
- `security|vulnerability|injection` → 0.9

### 中重要度 (0.4-0.7)

- `Cannot find module|ModuleNotFoundError` → 0.5
- `TypeError|ReferenceError` → 0.5
- `timeout|ETIMEDOUT` → 0.6

### 低重要度 (0.0-0.3)

- `warning:|WARN` → 0.2
- `deprecated` → 0.3

### カテゴリベーススコア（ルール未マッチ時）

- `error` → 0.5
- `quality` → 0.6
- `pattern` → 0.4
- `correction` → 0.7

### confidence

- ルールマッチ時: 0.8
- カテゴリベース時: 0.5

## 昇格ルール

| 条件                                    | アクション       |
| --------------------------------------- | ---------------- |
| `importance >= 0.8` + 1回出現           | 自動昇格候補     |
| `0.4 <= importance < 0.8` + 3回以上出現 | 昇格候補         |
| `importance < 0.4`                      | 90日後アーカイブ |
```

**Step 2: テストファイルを作成**

```python
#!/usr/bin/env python3
"""Tests for session_events.py importance scoring."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from session_events import compute_importance, emit_event, flush_session


class TestComputeImportance(unittest.TestCase):
    """Test importance scoring rules."""

    def test_high_importance_permission_denied(self):
        score, conf = compute_importance("error", {"message": "EACCES: Permission denied"})
        self.assertGreaterEqual(score, 0.8)
        self.assertEqual(conf, 0.8)

    def test_high_importance_segfault(self):
        score, conf = compute_importance("error", {"message": "segfault at 0x0"})
        self.assertEqual(score, 1.0)

    def test_high_importance_golden_principle(self):
        score, conf = compute_importance("quality", {"rule": "GP-003", "detail": "..."})
        self.assertGreaterEqual(score, 0.8)

    def test_medium_importance_module_not_found(self):
        score, conf = compute_importance("error", {"message": "Cannot find module 'foo'"})
        self.assertAlmostEqual(score, 0.5)

    def test_low_importance_warning(self):
        score, conf = compute_importance("error", {"message": "warning: unused variable"})
        self.assertLessEqual(score, 0.3)

    def test_base_importance_no_rule_match(self):
        score, conf = compute_importance("error", {"message": "something unknown"})
        self.assertAlmostEqual(score, 0.5)  # error base
        self.assertAlmostEqual(conf, 0.5)

    def test_quality_base_importance(self):
        score, conf = compute_importance("quality", {"rule": "UNKNOWN"})
        self.assertAlmostEqual(score, 0.6)  # quality base

    def test_pattern_base_importance(self):
        score, conf = compute_importance("pattern", {"name": "test"})
        self.assertAlmostEqual(score, 0.4)  # pattern base

    def test_correction_base_importance(self):
        score, conf = compute_importance("correction", {"detail": "auto-fixed"})
        self.assertAlmostEqual(score, 0.7)  # correction base


class TestEmitEventWithScoring(unittest.TestCase):
    """Test that emit_event writes scored entries."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        os.environ.pop("AUTOEVOLVE_DATA_DIR", None)

    def test_emit_includes_importance(self):
        emit_event("error", {"message": "Permission denied", "command": "npm test"})
        events = flush_session()
        self.assertEqual(len(events), 1)
        self.assertIn("importance", events[0])
        self.assertIn("confidence", events[0])
        self.assertEqual(events[0]["scored_by"], "rule")
        self.assertEqual(events[0]["promotion_status"], "pending")

    def test_emit_preserves_existing_data(self):
        emit_event("error", {"message": "foo", "command": "bar"})
        events = flush_session()
        self.assertEqual(events[0]["message"], "foo")
        self.assertEqual(events[0]["command"], "bar")
        self.assertEqual(events[0]["category"], "error")


if __name__ == "__main__":
    unittest.main()
```

**Step 3: テストを実行して失敗を確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_session_events.py -v`
Expected: FAIL — `compute_importance` が存在しない

**Step 4: `session_events.py` に `compute_importance` を追加し、`emit_event` を拡張**

`session_events.py` に以下を追加（既存コードの後、`emit_event` を修正）:

```python
import re

# --- Importance Scoring ---

IMPORTANCE_RULES: list[tuple[str, re.Pattern, float]] = [
    # High importance (0.8-1.0)
    ("high", re.compile(r"EACCES|Permission denied", re.I), 0.9),
    ("high", re.compile(r"segfault|SIGSEGV|OOM|out of memory", re.I), 1.0),
    ("high", re.compile(r"GP-00[1-5]"), 0.8),
    ("high", re.compile(r"security|vulnerability|injection", re.I), 0.9),
    # Medium importance (0.4-0.7)
    ("medium", re.compile(r"Cannot find module|ModuleNotFoundError", re.I), 0.5),
    ("medium", re.compile(r"TypeError|ReferenceError", re.I), 0.5),
    ("medium", re.compile(r"timeout|ETIMEDOUT", re.I), 0.6),
    # Low importance (0.0-0.3)
    ("low", re.compile(r"(?<!\w)warning(?:s)?(?:\s*:|\s)", re.I), 0.2),
    ("low", re.compile(r"deprecated", re.I), 0.3),
]

BASE_IMPORTANCE: dict[str, float] = {
    "error": 0.5,
    "quality": 0.6,
    "pattern": 0.4,
    "correction": 0.7,
}

RULE_CONFIDENCE = 0.8
BASE_CONFIDENCE = 0.5


def compute_importance(category: str, data: dict) -> tuple[float, float]:
    """ルールベースで importance と confidence を計算する。"""
    searchable = " ".join(str(v) for v in data.values())

    for _level, pattern, score in IMPORTANCE_RULES:
        if pattern.search(searchable):
            return score, RULE_CONFIDENCE

    base = BASE_IMPORTANCE.get(category, 0.5)
    return base, BASE_CONFIDENCE
```

`emit_event` を修正:

```python
def emit_event(category: str, data: dict) -> None:
    """セッション中のイベントを一時ファイルに追記する（スコア付き）。"""
    logger = _setup_logger()
    try:
        importance, confidence = compute_importance(category, data)
        path = _temp_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": _now_iso(),
            "category": category,
            **data,
            "importance": round(importance, 2),
            "confidence": round(confidence, 2),
            "scored_by": "rule",
            "promotion_status": "pending",
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        brief = str(data.get("message", data.get("rule", "")))[:80]
        logger.debug("emit: %s [i=%.1f] - %s", category, importance, brief)
    except Exception as exc:
        try:
            logger.error("emit failed: %s", exc)
        except Exception:
            pass
```

**Step 5: テストを実行して全て PASS を確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_session_events.py -v`
Expected: All tests PASS

**Step 6: コミット**

```
✨ feat: add importance scoring to session events

emit_event() にルールベースの重要度スコアリングを追加。
高重要度(セキュリティ,OOM,GP違反)→0.8-1.0、中→0.4-0.7、低→0.0-0.3。
```

---

## Task 2: Importance Scoring — `session-learner.py` 拡張

**Files:**

- Modify: `.config/claude/scripts/session-learner.py`
- Test: `.config/claude/scripts/tests/test_session_learner.py`

**Step 1: テストファイルを作成**

```python
#!/usr/bin/env python3
"""Tests for session-learner.py scored output."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestSessionLearnerScoring(unittest.TestCase):
    """Test that session-learner preserves importance scores in learnings."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        os.environ.pop("AUTOEVOLVE_DATA_DIR", None)

    def test_learnings_include_scores(self):
        from session_events import emit_event
        from importlib import import_module
        learner = import_module("session-learner")

        emit_event("error", {"message": "Permission denied", "command": "npm test"})
        learner.process_session(cwd=self.tmpdir)

        errors_path = Path(self.tmpdir) / "learnings" / "errors.jsonl"
        self.assertTrue(errors_path.exists())

        with open(errors_path) as f:
            entry = json.loads(f.readline())

        self.assertIn("importance", entry)
        self.assertIn("confidence", entry)
        self.assertIn("scored_by", entry)
        self.assertIn("promotion_status", entry)
        self.assertGreaterEqual(entry["importance"], 0.8)  # Permission denied = high

    def test_metrics_include_score_summary(self):
        from session_events import emit_event
        from importlib import import_module
        learner = import_module("session-learner")

        emit_event("error", {"message": "OOM", "command": "build"})
        emit_event("quality", {"rule": "GP-001", "file": "x.ts", "detail": "..."})
        emit_event("error", {"message": "warning: unused", "command": "lint"})
        learner.process_session(cwd=self.tmpdir)

        metrics_path = Path(self.tmpdir) / "metrics" / "session-metrics.jsonl"
        with open(metrics_path) as f:
            entry = json.loads(f.readline())

        self.assertIn("high_importance_count", entry)
        self.assertIn("avg_importance", entry)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: テストを実行して失敗を確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_session_learner.py -v`
Expected: FAIL — `high_importance_count` がメトリクスにない

**Step 3: `session-learner.py` を修正**

`process_session` 関数の learnings 書き出し部分を修正。既存の `{k: v for k, v in error.items() if k != "category"}` は既にスコアフィールドを保持するため変更不要。

`build_session_summary` にスコアサマリーを追加:

```python
def build_session_summary(cwd: str | None = None) -> dict:
    """セッションイベントを集約してサマリーを構築する。"""
    events = flush_session()

    errors = [e for e in events if e.get("category") == "error"]
    quality = [e for e in events if e.get("category") == "quality"]
    patterns = [e for e in events if e.get("category") == "pattern"]
    corrections = [e for e in events if e.get("category") == "correction"]

    project = Path(cwd).name if cwd else "unknown"

    # Score summary
    all_importance = [e.get("importance", 0.5) for e in events]
    high_count = sum(1 for i in all_importance if i >= 0.8)
    avg_importance = sum(all_importance) / len(all_importance) if all_importance else 0.0

    return {
        "project": project,
        "cwd": cwd or os.getcwd(),
        "total_events": len(events),
        "errors_count": len(errors),
        "quality_issues": len(quality),
        "patterns_found": len(patterns),
        "corrections": len(corrections),
        "high_importance_count": high_count,
        "avg_importance": round(avg_importance, 2),
        "_errors": errors,
        "_quality": quality,
        "_patterns": patterns,
        "_corrections": corrections,
    }
```

`process_session` の metrics dict にも追加:

```python
    metrics = {
        "project": summary["project"],
        "cwd": summary["cwd"],
        "total_events": summary["total_events"],
        "errors_count": summary["errors_count"],
        "quality_issues": summary["quality_issues"],
        "patterns_found": summary["patterns_found"],
        "corrections": summary["corrections"],
        "high_importance_count": summary["high_importance_count"],
        "avg_importance": summary["avg_importance"],
    }
```

**Step 4: テストを実行して全て PASS を確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_session_learner.py -v`
Expected: All tests PASS

**Step 5: コミット**

```
✨ feat: propagate importance scores through session-learner

learnings JSONL にスコアフィールドを保持し、
metrics にhigh_importance_count と avg_importance を追加。
```

---

## Task 3: Checkpoint System — `checkpoint-manager.py`

**Files:**

- Create: `.config/claude/scripts/checkpoint-manager.py`
- Test: `.config/claude/scripts/tests/test_checkpoint_manager.py`

**Step 1: テストファイルを作成**

```python
#!/usr/bin/env python3
"""Tests for checkpoint-manager.py."""
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestCheckpointManager(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.state_dir = Path(self.tmpdir) / "session-state"
        self.checkpoints_dir = self.state_dir / "checkpoints"
        os.environ["CLAUDE_SESSION_STATE_DIR"] = str(self.state_dir)
        os.environ["AUTOEVOLVE_DATA_DIR"] = self.tmpdir

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        os.environ.pop("CLAUDE_SESSION_STATE_DIR", None)
        os.environ.pop("AUTOEVOLVE_DATA_DIR", None)

    def test_should_checkpoint_edit_threshold(self):
        from checkpoint_manager import should_checkpoint
        counter = {"count": 16, "lastReset": time.time() * 1000, "recentEdits": []}
        result = should_checkpoint(counter, last_checkpoint_time=0)
        self.assertTrue(result)
        self.assertEqual(result, "auto:edit_threshold")

    def test_should_not_checkpoint_below_threshold(self):
        from checkpoint_manager import should_checkpoint
        counter = {"count": 5, "lastReset": time.time() * 1000, "recentEdits": []}
        result = should_checkpoint(counter, last_checkpoint_time=time.time())
        self.assertFalse(result)

    def test_should_checkpoint_time_threshold(self):
        from checkpoint_manager import should_checkpoint
        counter = {"count": 3, "lastReset": time.time() * 1000, "recentEdits": []}
        old_time = time.time() - 1900  # 31+ minutes ago
        result = should_checkpoint(counter, last_checkpoint_time=old_time)
        self.assertTrue(result)

    def test_cooldown_prevents_checkpoint(self):
        from checkpoint_manager import should_checkpoint
        counter = {"count": 20, "lastReset": time.time() * 1000, "recentEdits": []}
        recent_time = time.time() - 60  # 1 minute ago (within 5min cooldown)
        result = should_checkpoint(counter, last_checkpoint_time=recent_time)
        self.assertFalse(result)

    def test_save_checkpoint_creates_file(self):
        from checkpoint_manager import save_checkpoint
        save_checkpoint(
            trigger="manual",
            state_dir=self.state_dir,
            edit_count=10,
            context_pct=45,
        )
        files = list(self.checkpoints_dir.glob("checkpoint-*.json"))
        self.assertEqual(len(files), 1)

        data = json.loads(files[0].read_text())
        self.assertEqual(data["trigger"], "manual")
        self.assertEqual(data["edit_count"], 10)

    def test_save_checkpoint_keeps_max_5(self):
        from checkpoint_manager import save_checkpoint
        for i in range(7):
            save_checkpoint(
                trigger="auto:edit_threshold",
                state_dir=self.state_dir,
                edit_count=i,
            )
            time.sleep(0.01)  # ensure unique timestamps

        files = list(self.checkpoints_dir.glob("checkpoint-*.json"))
        self.assertLessEqual(len(files), 5)

    def test_last_checkpoint_pointer(self):
        from checkpoint_manager import save_checkpoint
        save_checkpoint(trigger="manual", state_dir=self.state_dir)

        pointer = self.state_dir / "last-checkpoint.json"
        self.assertTrue(pointer.exists())
        data = json.loads(pointer.read_text())
        self.assertEqual(data["trigger"], "manual")


if __name__ == "__main__":
    unittest.main()
```

**Step 2: テストを実行して失敗を確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_checkpoint_manager.py -v`
Expected: FAIL — `checkpoint_manager` モジュールが存在しない

**Step 3: `checkpoint-manager.py` を実装**

```python
#!/usr/bin/env python3
from __future__ import annotations
"""Checkpoint manager — auto-saves session state during heavy work.

Triggered by: hooks.PostToolUse (Edit|Write)
Input: stdin JSON (hook protocol)
Output: stdout JSON (with optional additionalContext)
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Thresholds
EDIT_THRESHOLD = 15
CONTEXT_PCT_THRESHOLD = 60
TIME_THRESHOLD_SECONDS = 30 * 60  # 30 minutes
COOLDOWN_SECONDS = 5 * 60  # 5 minutes between checkpoints
MAX_CHECKPOINTS = 5


def _get_state_dir() -> Path:
    return Path(os.environ.get(
        "CLAUDE_SESSION_STATE_DIR",
        os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
    ))


def _get_counter_path() -> Path:
    return _get_state_dir() / "edit-counter.json"


def _get_checkpoints_dir() -> Path:
    return _get_state_dir() / "checkpoints"


def _read_counter() -> dict:
    try:
        return json.loads(_get_counter_path().read_text())
    except Exception:
        return {"count": 0, "lastReset": time.time() * 1000, "recentEdits": []}


def _last_checkpoint_time(state_dir: Path | None = None) -> float:
    """最後の checkpoint のタイムスタンプを返す。なければ 0。"""
    pointer = (state_dir or _get_state_dir()) / "last-checkpoint.json"
    try:
        data = json.loads(pointer.read_text())
        return datetime.fromisoformat(data["timestamp"]).timestamp()
    except Exception:
        return 0.0


def should_checkpoint(
    counter: dict,
    last_checkpoint_time: float,
    context_pct: int = 0,
) -> str | bool:
    """checkpoint すべきか判定する。すべき場合は trigger 文字列を返す。"""
    now = time.time()

    # Cooldown check
    if now - last_checkpoint_time < COOLDOWN_SECONDS:
        return False

    edit_count = counter.get("count", 0)

    if edit_count >= EDIT_THRESHOLD:
        return "auto:edit_threshold"

    if context_pct >= CONTEXT_PCT_THRESHOLD:
        return "auto:context_threshold"

    if last_checkpoint_time > 0 and (now - last_checkpoint_time) >= TIME_THRESHOLD_SECONDS:
        return "auto:time_threshold"

    # First session (no previous checkpoint) + time check against session start
    if last_checkpoint_time == 0:
        session_start = counter.get("lastReset", now * 1000) / 1000
        if (now - session_start) >= TIME_THRESHOLD_SECONDS:
            return "auto:time_threshold"

    return False


def save_checkpoint(
    trigger: str,
    state_dir: Path | None = None,
    edit_count: int = 0,
    context_pct: int = 0,
    focus_files: list[str] | None = None,
    active_profile: str = "default",
) -> Path:
    """checkpoint を保存し、last-checkpoint.json ポインタを更新する。"""
    sd = state_dir or _get_state_dir()
    cp_dir = sd / "checkpoints"
    cp_dir.mkdir(parents=True, exist_ok=True)

    # Gather git info
    branch = _run_git("branch --show-current")
    git_status = _run_git("status --porcelain")

    ts = datetime.now(timezone.utc)
    data = {
        "timestamp": ts.isoformat(),
        "trigger": trigger,
        "working_on": _infer_working_on(focus_files, branch),
        "focus": (focus_files or [])[:10],
        "branch": branch,
        "git_status": git_status,
        "edit_count": edit_count,
        "context_usage_pct": context_pct,
        "active_profile": active_profile,
    }

    filename = f"checkpoint-{ts.strftime('%Y%m%dT%H%M%S')}.json"
    cp_path = cp_dir / filename
    cp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    # Update pointer
    pointer = sd / "last-checkpoint.json"
    pointer.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    # Cleanup old checkpoints (keep MAX_CHECKPOINTS)
    _cleanup_old_checkpoints(cp_dir)

    return cp_path


def _cleanup_old_checkpoints(cp_dir: Path) -> None:
    files = sorted(cp_dir.glob("checkpoint-*.json"))
    while len(files) > MAX_CHECKPOINTS:
        files.pop(0).unlink(missing_ok=True)


def _run_git(args: str) -> str:
    import subprocess
    try:
        result = subprocess.run(
            ["git"] + args.split(),
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _infer_working_on(focus_files: list[str] | None, branch: str) -> str:
    if branch and branch not in ("master", "main"):
        return branch
    if focus_files:
        return Path(focus_files[0]).stem
    return ""


def _extract_focus_files(input_data: dict) -> list[str]:
    """hook の入力 JSON からフォーカスファイルを抽出。"""
    files = []
    tool_input = input_data.get("tool_input", {})
    fp = tool_input.get("file_path", "")
    if fp:
        files.append(fp)

    # Also use recent edits from counter
    counter = _read_counter()
    for edit in counter.get("recentEdits", [])[-10:]:
        f = edit.get("file", "")
        if f and f not in files:
            files.append(f)

    return files


def main() -> None:
    data = sys.stdin.read()
    try:
        input_data = json.loads(data) if data.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    try:
        counter = _read_counter()
        lct = _last_checkpoint_time()
        trigger = should_checkpoint(counter, lct)

        if trigger:
            focus = _extract_focus_files(input_data)
            save_checkpoint(
                trigger=trigger,
                edit_count=counter.get("count", 0),
                focus_files=focus,
            )
            # Inject notification via additionalContext
            json.dump({
                **input_data,
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        f"[Checkpoint] セッション状態を保存しました "
                        f"(trigger: {trigger}, edits: {counter.get('count', 0)})"
                    ),
                },
            }, sys.stdout)
            return
    except Exception:
        pass

    # Pass through
    sys.stdout.write(data)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
```

**Step 4: テストを実行して全て PASS を確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_checkpoint_manager.py -v`
Expected: All tests PASS

**Step 5: コミット**

```
✨ feat: add checkpoint-manager for session resilience

PostToolUse hook で自動 checkpoint を実行。
トリガー: 15回以上の編集、コンテキスト60%超、30分経過。
最新5件保持、5分間のクールダウン付き。
```

---

## Task 4: Checkpoint Recovery — `checkpoint-recover.py`

**Files:**

- Create: `.config/claude/scripts/checkpoint-recover.py`
- Test: `.config/claude/scripts/tests/test_checkpoint_recover.py`

**Step 1: テストファイルを作成**

```python
#!/usr/bin/env python3
"""Tests for checkpoint-recover.py."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestCheckpointRecover(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.state_dir = Path(self.tmpdir) / "session-state"
        self.state_dir.mkdir(parents=True)
        os.environ["CLAUDE_SESSION_STATE_DIR"] = str(self.state_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        os.environ.pop("CLAUDE_SESSION_STATE_DIR", None)

    def test_no_checkpoint_no_output(self):
        from checkpoint_recover import check_recovery
        result = check_recovery(self.state_dir)
        self.assertIsNone(result)

    def test_normal_exit_no_recovery(self):
        """session-save.js が last-session.json を書いていれば正常終了。"""
        from checkpoint_recover import check_recovery
        now = datetime.now(timezone.utc)
        # Checkpoint exists
        cp = {"timestamp": now.isoformat(), "trigger": "manual", "working_on": "test"}
        (self.state_dir / "last-checkpoint.json").write_text(json.dumps(cp))
        # Session save also exists (newer)
        ss = {"timestamp": (now + timedelta(seconds=10)).isoformat()}
        (self.state_dir / "last-session.json").write_text(json.dumps(ss))

        result = check_recovery(self.state_dir)
        self.assertIsNone(result)

    def test_abnormal_exit_triggers_recovery(self):
        """checkpoint はあるが session-save がない → 復元情報を返す。"""
        from checkpoint_recover import check_recovery
        now = datetime.now(timezone.utc)
        cp = {
            "timestamp": now.isoformat(),
            "trigger": "auto:edit_threshold",
            "working_on": "auth rollout",
            "focus": ["src/auth.ts"],
            "branch": "feat/auth",
            "git_status": "M src/auth.ts",
            "edit_count": 20,
        }
        (self.state_dir / "last-checkpoint.json").write_text(json.dumps(cp))
        # No last-session.json → abnormal exit

        result = check_recovery(self.state_dir)
        self.assertIsNotNone(result)
        self.assertIn("auth rollout", result)
        self.assertIn("feat/auth", result)

    def test_old_checkpoint_ignored(self):
        """24h 以上前の checkpoint は無視。"""
        from checkpoint_recover import check_recovery
        old = datetime.now(timezone.utc) - timedelta(hours=25)
        cp = {"timestamp": old.isoformat(), "trigger": "manual", "working_on": "old"}
        (self.state_dir / "last-checkpoint.json").write_text(json.dumps(cp))

        result = check_recovery(self.state_dir)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
```

**Step 2: テストを実行して失敗を確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_checkpoint_recover.py -v`
Expected: FAIL — `checkpoint_recover` が存在しない

**Step 3: `checkpoint-recover.py` を実装**

```python
#!/usr/bin/env python3
from __future__ import annotations
"""Checkpoint recovery — detects abnormal session end and injects recovery context.

Triggered by: hooks.SessionStart
Output: stdout text (SessionStart hook protocol)
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


def _get_state_dir() -> Path:
    return Path(os.environ.get(
        "CLAUDE_SESSION_STATE_DIR",
        os.path.join(os.environ.get("HOME", ""), ".claude", "session-state"),
    ))


def check_recovery(state_dir: Path | None = None) -> str | None:
    """前回セッションの異常終了を検出し、復元メッセージを返す。"""
    sd = state_dir or _get_state_dir()
    cp_path = sd / "last-checkpoint.json"

    if not cp_path.exists():
        return None

    try:
        cp = json.loads(cp_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    # Parse checkpoint timestamp
    try:
        cp_time = datetime.fromisoformat(cp["timestamp"])
    except (KeyError, ValueError):
        return None

    now = datetime.now(timezone.utc)

    # Ignore checkpoints older than 24h
    if now - cp_time > timedelta(hours=24):
        return None

    # Check if session-save exists and is newer than checkpoint
    ss_path = sd / "last-session.json"
    if ss_path.exists():
        try:
            ss = json.loads(ss_path.read_text())
            ss_time = datetime.fromisoformat(ss["timestamp"])
            if ss_time >= cp_time:
                return None  # Normal exit
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

    # Abnormal exit — build recovery message
    lines = [
        "[Checkpoint Recovery] 前回セッションが中断された可能性があります。",
        f"  最後の checkpoint: {cp.get('timestamp', 'unknown')}",
    ]
    if cp.get("working_on"):
        lines.append(f"  作業中: {cp['working_on']}")
    if cp.get("focus"):
        files = ", ".join(cp["focus"][:5])
        lines.append(f"  フォーカス: {files}")
    if cp.get("branch"):
        lines.append(f"  ブランチ: {cp['branch']}")
    if cp.get("git_status"):
        lines.append(f"  未コミット変更: {cp['git_status'][:200]}")
    if cp.get("edit_count"):
        lines.append(f"  編集回数: {cp['edit_count']}")

    return "\n".join(lines)


def main() -> None:
    try:
        msg = check_recovery()
        if msg:
            print(msg)
    except Exception:
        pass


if __name__ == "__main__":
    main()
```

**Step 4: テストを実行して全て PASS を確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_checkpoint_recover.py -v`
Expected: All tests PASS

**Step 5: コミット**

```
✨ feat: add checkpoint-recover for crash detection

SessionStart で前回の異常終了を検出し、復元情報を注入。
session-save がなく checkpoint がある場合に発動。
```

---

## Task 5: `/checkpoint` スラッシュコマンド

**Files:**

- Create: `.config/claude/commands/checkpoint.md`

**Step 1: コマンドファイルを作成**

```markdown
現在の作業状態を手動で checkpoint として保存してください。

以下の手順で実行:

1. `~/.claude/session-state/edit-counter.json` から現在の編集カウントを取得
2. `checkpoint-manager.py` の `save_checkpoint()` を trigger="manual" で呼び出し
3. 保存結果をユーザーに報告

実行コマンド:
python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/scripts')
from checkpoint_manager import save_checkpoint, \_read_counter
counter = \_read_counter()
path = save_checkpoint(trigger='manual', edit_count=counter.get('count', 0))
print(f'Checkpoint saved: {path}')
"
```

**Step 2: コミット**

```
✨ feat: add /checkpoint slash command

手動で作業状態を保存する /checkpoint コマンド。
```

---

## Task 6: Context Profiles — reference + `agent-router.py` 拡張

**Files:**

- Create: `.config/claude/references/context-profiles.md`
- Modify: `.config/claude/scripts/agent-router.py`
- Test: `.config/claude/scripts/tests/test_agent_router.py`

**Step 1: context-profiles reference を作成**

```markdown
# Context Profiles

## プロファイル定義

| プロファイル | 用途                 | learnings フィルタ                                       |
| ------------ | -------------------- | -------------------------------------------------------- |
| `default`    | 通常の開発作業       | importance >= 0.4, 上位5件                               |
| `planning`   | 設計・アーキテクチャ | type: decision/pattern 優先, 上位8件                     |
| `debugging`  | バグ修正・調査       | type: error/correction 優先, importance >= 0.3, 上位10件 |
| `incident`   | 障害対応・緊急       | 直近24h の全 learnings, 時系列優先                       |

## 自動判別キーワード

### planning

- 設計, アーキテクチャ, architecture, design, plan, 構成
- どうする, どうすべき, 方針, 戦略, strategy
- 新機能, feature, リファクタ

### debugging

- バグ, bug, エラー, error, 失敗, fail
- 動かない, 壊れ, broken, crash
- なぜ, why, 原因, cause, 調査

### incident

- 障害, incident, 緊急, urgent, 本番, production
- ダウン, down, 止まっ, 復旧

## 手動オーバーライド

プロンプトに `@planning` `@debugging` `@incident` を含めると自動判別を上書き。
```

**Step 2: テストファイルを作成**

```python
#!/usr/bin/env python3
"""Tests for agent-router.py context profile detection."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest


class TestProfileDetection(unittest.TestCase):

    def test_planning_keywords_ja(self):
        from agent_router import detect_profile
        self.assertEqual(detect_profile("このAPIの設計を考えて"), "planning")

    def test_planning_keywords_en(self):
        from agent_router import detect_profile
        self.assertEqual(detect_profile("design the architecture"), "planning")

    def test_debugging_keywords_ja(self):
        from agent_router import detect_profile
        self.assertEqual(detect_profile("このバグを直して"), "debugging")

    def test_debugging_keywords_en(self):
        from agent_router import detect_profile
        self.assertEqual(detect_profile("fix this error"), "debugging")

    def test_incident_keywords(self):
        from agent_router import detect_profile
        self.assertEqual(detect_profile("本番で障害が発生"), "incident")

    def test_default_no_match(self):
        from agent_router import detect_profile
        self.assertEqual(detect_profile("ファイルを作成して"), "default")

    def test_override_planning(self):
        from agent_router import detect_profile
        self.assertEqual(detect_profile("@planning このバグを直して"), "planning")

    def test_override_debugging(self):
        from agent_router import detect_profile
        self.assertEqual(detect_profile("@debugging 設計を考えて"), "debugging")

    def test_override_incident(self):
        from agent_router import detect_profile
        self.assertEqual(detect_profile("@incident 確認して"), "incident")


if __name__ == "__main__":
    unittest.main()
```

**Step 3: テストを実行して失敗を確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_agent_router.py -v`
Expected: FAIL — `detect_profile` が存在しない

**Step 4: `agent-router.py` を拡張**

既存の keyword 定義の後に追加:

```python
# --- Context Profiles ---

PROFILE_OVERRIDE_RE = re.compile(r"@(planning|debugging|incident|default)")

PROFILE_KEYWORDS = {
    "planning": [
        re.compile(r"設計|アーキテクチャ|architecture|design(?!ate)|plan(?!e)|構成", re.I),
        re.compile(r"どう(する|すべき)|方針|戦略|strategy", re.I),
        re.compile(r"新機能|feature|リファクタ", re.I),
    ],
    "debugging": [
        re.compile(r"バグ|bug|エラー|(?<!\w)error(?!\w)|失敗|fail", re.I),
        re.compile(r"動かない|壊れ|broken|crash", re.I),
        re.compile(r"なぜ|(?<!\w)why(?!\w)|原因|cause|調査", re.I),
    ],
    "incident": [
        re.compile(r"障害|incident|緊急|urgent|本番|production", re.I),
        re.compile(r"ダウン|(?<!\w)down(?!\w)|止まっ|復旧", re.I),
    ],
}


def detect_profile(prompt: str) -> str:
    """プロンプトからコンテキストプロファイルを判別する。"""
    # Check override first
    override = PROFILE_OVERRIDE_RE.search(prompt)
    if override:
        return override.group(1)

    # Keyword matching
    for profile, patterns in PROFILE_KEYWORDS.items():
        for pattern in patterns:
            if pattern.search(prompt):
                return profile

    return "default"
```

`main()` 関数を修正して、既存の出力にプロファイル情報を追加:

```python
def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    prompt = data.get("user_prompt", "") or data.get("content", "")
    if not prompt or len(prompt) < 3:
        json.dump(data, sys.stdout)
        return

    # Detect context profile
    profile = detect_profile(prompt)
    profile_context = ""
    if profile != "default":
        profile_context = f"[Context Profile: {profile}] "

    # Priority 1: Multimodal files → Gemini
    mm_files = detect_multimodal(prompt)
    if mm_files:
        exts = ", ".join(f".{e}" for e in mm_files)
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"{profile_context}"
                    f"[Agent Router] マルチモーダルファイル ({exts}) が検出されました。"
                    "Gemini CLI (1Mコンテキスト) での処理を推奨します。"
                    "gemini-explore エージェントまたは gemini スキルを使用してください。"
                ),
            }
        }, sys.stdout)
        return

    # Priority 2: Codex keywords
    codex_matches = match_keywords(prompt, CODEX_KEYWORDS_JA + CODEX_KEYWORDS_EN)
    if codex_matches:
        keywords = ", ".join(codex_matches[:3])
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"{profile_context}"
                    f"[Agent Router] 設計/推論キーワード ({keywords}) が検出されました。"
                    "Codex CLI での深い分析を検討してください。"
                    "codex スキル、codex-debugger エージェント、または直接 codex exec で実行できます。"
                ),
            }
        }, sys.stdout)
        return

    # Priority 3: Gemini keywords
    gemini_matches = match_keywords(prompt, GEMINI_KEYWORDS_JA + GEMINI_KEYWORDS_EN)
    if gemini_matches:
        keywords = ", ".join(gemini_matches[:3])
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"{profile_context}"
                    f"[Agent Router] リサーチ/分析キーワード ({keywords}) が検出されました。"
                    "Gemini CLI (1Mコンテキスト + Google Search) での調査を検討してください。"
                    "gemini-explore エージェントまたは gemini スキルを使用できます。"
                ),
            }
        }, sys.stdout)
        return

    # Profile-only output (no agent routing match)
    if profile != "default":
        json.dump({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    f"[Context Profile: {profile}] "
                    f"{profile} モードのコンテキストを優先して参照します。"
                ),
            }
        }, sys.stdout)
        return

    # No match — pass through
    json.dump(data, sys.stdout)
```

**注意**: `agent-router.py` は `-` 付きファイル名なので、テストでは `import agent_router` ではなく `importlib` を使う。テストの import を修正:

```python
from importlib import import_module
agent_router = import_module("agent-router")
detect_profile = agent_router.detect_profile
```

**Step 5: テストを実行して全て PASS を確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_agent_router.py -v`
Expected: All tests PASS

**Step 6: コミット**

```
✨ feat: add context profile detection to agent-router

@planning/@debugging/@incident オーバーライド対応。
キーワードベースの自動プロファイル判別で additionalContext に注入。
```

---

## Task 7: Context Profiles — `session-load.js` 拡張

**Files:**

- Modify: `.config/claude/scripts/session-load.js`

**Step 1: `session-load.js` にプロファイル別 learnings 読み込みを追加**

`loadState()` 関数の後に追加:

```javascript
function loadLearningsForProfile(profile) {
  const dataDir = path.join(
    process.env.AUTOEVOLVE_DATA_DIR ||
      path.join(process.env.HOME, ".claude", "agent-memory"),
  );
  const learningsDir = path.join(dataDir, "learnings");

  if (!fs.existsSync(learningsDir)) return;

  const allEntries = [];
  for (const file of fs.readdirSync(learningsDir)) {
    if (!file.endsWith(".jsonl")) continue;
    try {
      const lines = fs
        .readFileSync(path.join(learningsDir, file), "utf8")
        .split("\n");
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          allEntries.push(JSON.parse(line));
        } catch {
          /* skip corrupt lines */
        }
      }
    } catch {
      /* skip unreadable files */
    }
  }

  if (allEntries.length === 0) return;

  let filtered;
  const now = Date.now();
  const oneDayMs = 86400000;

  switch (profile) {
    case "planning":
      filtered = allEntries
        .filter((e) => ["decision", "pattern"].includes(e.type || e.category))
        .filter((e) => (e.importance ?? 0.5) >= 0.4)
        .sort((a, b) => (b.importance ?? 0.5) - (a.importance ?? 0.5))
        .slice(0, 8);
      break;

    case "debugging":
      filtered = allEntries
        .filter((e) => ["error", "correction"].includes(e.type || e.category))
        .filter((e) => (e.importance ?? 0.5) >= 0.3)
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, 10);
      break;

    case "incident":
      filtered = allEntries
        .filter((e) => new Date(e.timestamp).getTime() > now - oneDayMs)
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      break;

    default: // 'default'
      filtered = allEntries
        .filter((e) => (e.importance ?? 0.5) >= 0.4)
        .sort((a, b) => (b.importance ?? 0.5) - (a.importance ?? 0.5))
        .slice(0, 5);
      break;
  }

  if (filtered.length === 0) return;

  const lines = [
    `[Learnings: ${profile}] 関連する過去の学び (${filtered.length}件):`,
  ];
  for (const e of filtered) {
    const msg = e.message || e.rule || e.detail || e.name || "";
    const imp = e.importance != null ? ` [i=${e.importance}]` : "";
    lines.push(
      `  - ${e.type || e.category || "?"}${imp}: ${msg.slice(0, 120)}`,
    );
  }

  process.stderr.write(lines.join("\n") + "\n");
}
```

`process.stdin.on('end', ...)` のコールバックを修正:

```javascript
process.stdin.on("end", () => {
  loadState();

  // Load profile from last checkpoint or default
  let profile = "default";
  try {
    const cpPath = path.join(
      process.env.HOME,
      ".claude",
      "session-state",
      "last-checkpoint.json",
    );
    if (fs.existsSync(cpPath)) {
      const cp = JSON.parse(fs.readFileSync(cpPath, "utf8"));
      profile = cp.active_profile || "default";
    }
  } catch {
    /* ignore */
  }

  loadLearningsForProfile(profile);
  process.stdout.write(data);
});
```

**Step 2: コミット**

```
✨ feat: add profile-aware learnings injection to session-load

SessionStart 時にプロファイルに応じた learnings を注入。
planning=decision/pattern優先、debugging=error/correction優先、
incident=直近24h全件、default=importance>=0.4上位5件。
```

---

## Task 8: Hook 登録 — `settings.json` 更新

**Files:**

- Modify: `.config/claude/settings.json`

**Step 1: SessionStart に checkpoint-recover を追加**

`settings.json` の `SessionStart` 配列に追加:

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "python3 $HOME/.claude/scripts/checkpoint-recover.py 2>/dev/null || true"
    }
  ]
}
```

**Step 2: PostToolUse Edit|Write に checkpoint-manager を追加**

既存の `Edit|Write` matcher の hooks 配列の末尾に追加:

```json
{
  "type": "command",
  "command": "python3 $HOME/.claude/scripts/checkpoint-manager.py"
}
```

**Step 3: コミット**

```
🔧 chore: register checkpoint hooks in settings.json

SessionStart に checkpoint-recover、
PostToolUse(Edit|Write) に checkpoint-manager を追加。
```

---

## Task 9: `autolearn.md` エージェント拡張

**Files:**

- Modify: `.config/claude/agents/autolearn.md`

**Step 1: LLM 再スコアリングと昇格判定のセクションを追加**

`## 分析タスク` セクションの後に追加:

```markdown
### 5. LLM 再スコアリング

`scored_by: "rule"` かつ `confidence < 0.7` のエントリを抽出し、LLM で再評価:

1. learnings/\*.jsonl から対象エントリを抽出
2. 類似エントリをグループ化（同じ message/rule）
3. 出現頻度を計算
4. 重要度を再評価して `scored_by: "llm"` に更新

### 6. 昇格判定

scoring-rules.md の昇格ルールに従い:

- `importance >= 0.8` + 1回出現 → 自動昇格候補
- `0.4 <= importance < 0.8` + 3回以上出現 → 昇格候補
- `importance < 0.4` → 昇格なし

昇格候補は insights/analysis-YYYY-MM-DD.md の「昇格提案」セクションに記載。
```

`## 出力フォーマット` の insights テンプレートに追加:

```markdown
## 昇格提案

### 自動昇格候補 (importance >= 0.8)

| エントリ | importance | 出現回数 | 昇格先 |
| -------- | ---------- | -------- | ------ |
| ...      | ...        | ...      | ...    |

### 昇格候補 (3回以上出現)

| エントリ | importance | 出現回数 | 昇格先 |
| -------- | ---------- | -------- | ------ |
| ...      | ...        | ...      | ...    |
```

**Step 2: コミット**

```
📝 docs: extend autolearn agent with LLM re-scoring and promotion

重要度の LLM 再評価と昇格判定ロジックを分析タスクに追加。
```

---

## Task 10: `pre-compact-save.js` に checkpoint 連携を追加

**Files:**

- Modify: `.config/claude/scripts/pre-compact-save.js`

**Step 1: compact 前に checkpoint を強制実行**

`pre-compact-save.js` の末尾（`console.log` の前）に追加:

```javascript
// Force checkpoint before compaction
try {
  execSync('python3 $HOME/.claude/scripts/checkpoint-manager.py <<< "{}"', {
    encoding: "utf-8",
    timeout: 10000,
    stdio: ["pipe", "pipe", "pipe"],
  });
} catch {
  // Non-critical — checkpoint failure shouldn't block compaction
}
```

**Step 2: コミット**

```
🔧 chore: trigger checkpoint before context compaction

PreCompact で checkpoint を強制保存し、圧縮後の復元に備える。
```

---

## Task 11: テスト全体実行 + 統合確認

**Step 1: 全テスト実行**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/ -v`
Expected: All tests PASS

**Step 2: hook 動作確認（手動）**

```bash
# checkpoint-manager のスタンドアロンテスト
echo '{"tool_input":{"file_path":"/tmp/test.txt"}}' | python3 ~/.claude/scripts/checkpoint-manager.py

# checkpoint-recover のスタンドアロンテスト
python3 ~/.claude/scripts/checkpoint-recover.py

# agent-router のプロファイル検出テスト
echo '{"user_prompt":"このバグを直して"}' | python3 ~/.claude/scripts/agent-router.py
```

**Step 3: 最終コミット**

```
✅ test: verify all hooks pass integration checks
```

---

## 実装順序まとめ

```
Task 1-2: Importance Scoring (session_events.py + session-learner.py)
    ↓ スコアリング基盤ができる
Task 3-5: Checkpoint System (manager + recover + command)
    ↓ セッション耐障害性ができる
Task 6-7: Context Profiles (agent-router.py + session-load.js)
    ↓ プロファイル判別とコンテキスト注入ができる
Task 8: Hook 登録 (settings.json)
    ↓ 全 hook が有効化される
Task 9-10: Agent + PreCompact 連携
    ↓ 分析・圧縮との統合
Task 11: 統合テスト
```

各 Task は独立しており、Layer 単位でも動作する。
