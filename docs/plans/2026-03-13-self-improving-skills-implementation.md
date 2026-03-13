# Self-Improving Skills Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** スキル実行の自動追跡・劣化検知・SKILL.md 改善提案を既存 AutoEvolve パイプラインに統合する

**Architecture:** 既存の session_events.py に skill 追跡関数を追加、PostToolUse hook でスキル呼び出しを自動捕捉、autoevolve-core の Analyze/Improve フェーズにスキル分析カテゴリを追加

**Tech Stack:** Python 3, JSONL, Claude Code hooks (PostToolUse), pytest

**Design doc:** `docs/plans/2026-03-13-self-improving-skills-design.md`

---

### Task 1: session_events.py にスキル追跡関数を追加

**Files:**
- Modify: `.config/claude/scripts/lib/session_events.py`
- Test: `.config/claude/scripts/tests/test_session_events.py`

**Step 1: テスト追加 — emit_skill_event**

`.config/claude/scripts/tests/test_session_events.py` の末尾に追加:

```python
# --- skill tracking テスト ---


class TestEmitSkillEvent:
    """スキル実行イベントの記録テスト。"""

    def test_emit_skill_invocation(self, tmp_path):
        emit_skill_event("invocation", {
            "skill_name": "review",
            "session_id": "test-session-001",
        })
        session_file = tmp_path / "current-session.jsonl"
        assert session_file.exists()

        entry = json.loads(session_file.read_text().strip())
        assert entry["category"] == "skill"
        assert entry["type"] == "invocation"
        assert entry["skill_name"] == "review"

    def test_emit_skill_event_requires_skill_name(self, tmp_path):
        with pytest.raises(ValueError, match="skill_name"):
            emit_skill_event("invocation", {"session_id": "abc"})

    def test_emit_skill_outcome(self, tmp_path):
        emit_skill_event("outcome", {
            "skill_name": "search-first",
            "score": 0.35,
            "error_count": 2,
            "gp_violations": 1,
            "review_criticals": 0,
            "test_passed": False,
        })
        session_file = tmp_path / "current-session.jsonl"
        entry = json.loads(session_file.read_text().strip())
        assert entry["category"] == "skill"
        assert entry["type"] == "outcome"
        assert entry["score"] == 0.35


class TestComputeSkillScore:
    """スキルの複合スコア計算テスト。"""

    def test_perfect_session(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "review"},
        ]
        # エラーなし、テスト失敗なし → 高スコア
        score = compute_skill_score(events, "review")
        assert score == 1.0  # base(0.5) + completion(0.5), clamp

    def test_session_with_errors(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "review"},
            {"category": "error", "message": "TypeError"},
            {"category": "error", "message": "ReferenceError"},
        ]
        score = compute_skill_score(events, "review")
        assert score == pytest.approx(0.4)  # 0.5 + 0.5 - 0.3*2 = 0.4

    def test_session_with_test_failure(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "review"},
            {"category": "pattern", "message": "test_failed", "test_passed": False},
        ]
        score = compute_skill_score(events, "review")
        assert score == pytest.approx(0.5)  # 0.5 + 0.5 - 0.5 = 0.5

    def test_session_with_gp_violations(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "review"},
            {"category": "quality", "rule": "GP-001"},
            {"category": "quality", "rule": "GP-003"},
            {"category": "quality", "rule": "GP-004"},
        ]
        score = compute_skill_score(events, "review")
        assert score == pytest.approx(0.7)  # 0.5 + 0.5 - 0.1*3 = 0.7

    def test_score_clamps_to_zero(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "bad-skill"},
            {"category": "error", "message": "err1"},
            {"category": "error", "message": "err2"},
            {"category": "error", "message": "err3"},
            {"category": "pattern", "message": "test_failed", "test_passed": False},
        ]
        score = compute_skill_score(events, "bad-skill")
        assert score == 0.0  # 0.5 + 0.5 - 0.9 - 0.5 < 0 → clamp

    def test_review_criticals_penalty(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "rpi"},
            {"category": "quality", "review_severity": "critical"},
            {"category": "quality", "review_severity": "important"},
        ]
        score = compute_skill_score(events, "rpi")
        assert score == pytest.approx(0.6)  # 0.5 + 0.5 - 0.2*2 = 0.6
```

**Step 2: テスト実行 — 失敗を確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_session_events.py::TestEmitSkillEvent -v`
Expected: FAIL (emit_skill_event, compute_skill_score が未定義)

**Step 3: session_events.py に実装追加**

`.config/claude/scripts/lib/session_events.py` の末尾（`append_to_metrics` の後）に追加:

```python
def emit_skill_event(event_type: str, data: dict) -> None:
    """スキルライフサイクルイベントを記録する。

    event_type: "invocation" | "outcome"
    data には skill_name を必須で含む。
    """
    if "skill_name" not in data:
        raise ValueError("skill_name is required in data")
    logger = _setup_logger()
    try:
        path = _temp_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": _now_iso(),
            "category": "skill",
            "type": event_type,
            **data,
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logger.debug("skill_event: %s %s", event_type, data.get("skill_name"))
    except ValueError:
        raise
    except Exception as exc:
        try:
            logger.error("emit_skill_event failed: %s", exc)
        except Exception:
            pass


def compute_skill_score(session_events: list[dict], skill_name: str) -> float:
    """セッション中のイベントからスキルの複合スコアを計算する。

    スコア計算:
      base = 0.5
      + 0.5 (タスク正常完了 = デフォルト想定)
      - 0.3/件 (エラー発生)
      - 0.5 (テスト失敗)
      - 0.2/件 (レビュー Critical/Important)
      - 0.1/件 (GP違反)
    → clamp(0.0, 1.0)
    """
    score = 1.0  # base(0.5) + completion(0.5)

    # スキル呼び出し後のイベントのみ集計
    errors = [e for e in session_events if e.get("category") == "error"]
    score -= 0.3 * len(errors)

    # テスト失敗
    test_failures = [
        e for e in session_events
        if e.get("test_passed") is False
    ]
    if test_failures:
        score -= 0.5

    # GP 違反
    gp_violations = [
        e for e in session_events
        if e.get("category") == "quality"
        and e.get("rule", "").startswith("GP-")
    ]
    score -= 0.1 * len(gp_violations)

    # レビュー Critical/Important
    review_criticals = [
        e for e in session_events
        if e.get("category") == "quality"
        and e.get("review_severity") in ("critical", "important")
    ]
    score -= 0.2 * len(review_criticals)

    return max(0.0, min(1.0, round(score, 2)))
```

**Step 4: テスト実行 — パスを確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_session_events.py::TestEmitSkillEvent .config/claude/scripts/tests/test_session_events.py::TestComputeSkillScore -v`
Expected: ALL PASS

**Step 5: 既存テスト全体の回帰確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_session_events.py -v`
Expected: ALL PASS (既存テストが壊れていないこと)

**Step 6: コミット**

```bash
git add .config/claude/scripts/lib/session_events.py .config/claude/scripts/tests/test_session_events.py
git commit -m "✨ feat: add skill execution tracking to session_events.py"
```

---

### Task 2: skill-tracker.py PostToolUse hook 作成

**Files:**
- Create: `.config/claude/scripts/policy/skill-tracker.py`
- Modify: `.config/claude/settings.json`

**Step 1: skill-tracker.py を作成**

`.config/claude/scripts/policy/skill-tracker.py`:

```python
#!/usr/bin/env python3
"""Skill execution tracker — PostToolUse hook for Skill tool.

Skill tool が呼ばれた時に skill 名を自動記録する。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hook_utils import passthrough
from session_events import emit_skill_event


def main() -> None:
    data = json.loads(sys.stdin.read())

    tool_name = data.get("tool_name", "")
    if tool_name != "Skill":
        passthrough(data)
        return

    tool_input = data.get("tool_input", {})
    skill_name = tool_input.get("skill", "")

    if skill_name:
        emit_skill_event("invocation", {
            "skill_name": skill_name,
        })

    passthrough(data)


if __name__ == "__main__":
    main()
```

**Step 2: settings.json に PostToolUse hook 登録**

`settings.json` の `PostToolUse` 配列に `Skill` matcher を追加:

```json
{
    "matcher": "Skill",
    "hooks": [
        {
            "type": "command",
            "command": "python3 $HOME/.claude/scripts/policy/skill-tracker.py",
            "timeout": 5
        }
    ]
}
```

**Step 3: hook_utils.py の passthrough を確認**

Run: `grep -n "def passthrough" /Users/takeuchishougo/dotfiles/.config/claude/scripts/lib/hook_utils.py`
Expected: 関数定義が存在すること

**Step 4: コミット**

```bash
git add .config/claude/scripts/policy/skill-tracker.py .config/claude/settings.json
git commit -m "✨ feat: add skill-tracker PostToolUse hook"
```

---

### Task 3: session-learner.py にスキル集計ロジック追加

**Files:**
- Modify: `.config/claude/scripts/learner/session-learner.py`

**Step 1: session-learner.py に skill 集計を追加**

`process_session()` 内、`append_to_metrics(metrics)` の直前に以下を追加:

```python
    # スキル実行データの集計
    skill_invocations = [
        e for e in events if e.get("category") == "skill" and e.get("type") == "invocation"
    ]
    for inv in skill_invocations:
        skill_name = inv.get("skill_name", "")
        if not skill_name:
            continue
        from session_events import compute_skill_score
        score = compute_skill_score(events, skill_name)
        error_count = len(errors)
        gp_violations = len([
            e for e in quality
            if e.get("rule", "").startswith("GP-")
        ])
        review_criticals = len([
            e for e in quality
            if e.get("review_severity") in ("critical", "important")
        ])
        test_passed = not any(
            e.get("test_passed") is False for e in events
        )
        append_to_learnings("skill-executions", {
            "skill_name": skill_name,
            "score": score,
            "error_count": error_count,
            "gp_violations": gp_violations,
            "review_criticals": review_criticals,
            "test_passed": test_passed,
            "project": project,
        })
        logger.info(
            "session-learner: skill '%s' score=%.2f",
            skill_name,
            score,
        )
```

`build_session_summary()` の events 取得後に skill イベントを除外せず保持する（既存ロジックは `category` ベースのフィルタなので、`skill` カテゴリは自然にスキップされる — 追加対応不要）。

**Step 2: テスト実行**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/ -v`
Expected: ALL PASS

**Step 3: コミット**

```bash
git add .config/claude/scripts/learner/session-learner.py
git commit -m "✨ feat: add skill score aggregation to session-learner"
```

---

### Task 4: autoevolve-core.md にスキル分析・改善ルール追加

**Files:**
- Modify: `.config/claude/agents/autoevolve-core.md`

**Step 1: Phase 1 Analyze の入力データテーブルにスキルデータを追加**

`autoevolve-core.md` の入力データテーブルに行を追加:

```markdown
| `learnings/skill-executions.jsonl` | スキル実行スコア |
| `learnings/skill-benchmarks.jsonl` | スキル A/B テスト結果 |
```

**Step 2: Phase 1 Analyze の分析タスクにスキル分析を追加**

分析タスクリストの末尾に追加:

```markdown
7. **スキル健全性分析**: `skill-executions.jsonl` + `skill-benchmarks.jsonl` を分析
   - **トレンド分析**: スキルごとに直近10回の score 平均と前10回を比較
   - **閾値判定**:
     - Healthy: 平均 score >= 0.6
     - Degraded: 平均 score 0.4-0.6、または前期比 -0.1 以上の低下
     - Failing: 平均 score < 0.4、または直近5回中4回以上が score < 0.4
   - **失敗パターン特定**: Degraded/Failing スキルの紐づくエラー・GP違反を分析
   - **クロスデータ相関**: skill-benchmarks の A/B 結果と実行スコアを突き合わせ
     - A/B retire + 実行スコア低 → 強い改善根拠
     - A/B keep + 実行スコア低 → 環境変化による劣化
     - 実行データなし → 不要スキル候補
```

**Step 3: Phase 2 Improve の改善候補テーブルにスキル改善を追加**

改善候補の優先度テーブルの後に追加:

```markdown
| **高** | スキル Failing + 実行5回以上 | SKILL.md の修正案を `autoevolve/*` ブランチに作成 |
| **中** | スキル Degraded + トレンド低下 | SKILL.md の修正案を `autoevolve/*` ブランチに作成 |
| **低** | スキル実行5回未満 | 記録のみ、データ不足 |
```

そしてスキル改善の具体的な修正パターンを追記:

```markdown
### スキル改善の修正パターン

Failing/Degraded スキルに対する修正案の生成手順:

1. 対象 SKILL.md を読む
2. insights の失敗パターン分析結果を参照
3. skill-benchmarks.jsonl の A/B データを参照
4. 失敗パターンに基づいて修正を決定:

| 失敗パターン | 修正アクション |
|-------------|---------------|
| トリガー過剰 (他のタスクで誤発火) | description の条件を絞る |
| トリガー不足 (呼ばれるべき時に呼ばれない) | description にキーワード追加 |
| instruction で失敗多発 | 該当ステップの書き換え/条件追加 |
| 環境変化 (ツール非推奨等) | ツール参照の更新 |
| ベースモデルで十分 (A/B delta < 0) | retire 提案 ([DEPRECATED] 付与) |

5. `autoevolve/YYYY-MM-DD-skill-{name}` ブランチにコミット
6. コミットメッセージに根拠データを含める

### スキル改善の安全制約

- 実行5回以上が改善提案の最低条件
- retire 提案時はまず description に `[DEPRECATED]` を付与
- 次回 audit で改善なければ削除提案にエスカレート
```

**Step 4: 出力フォーマットにスキルセクション追加**

出力フォーマットの Analyze フェーズに追加:

```markdown
- スキル健全性: Failing N 件 / Degraded N 件 / Healthy N 件
```

**Step 5: コミット**

```bash
git add .config/claude/agents/autoevolve-core.md
git commit -m "✨ feat: add skill analysis and amendment to autoevolve-core"
```

---

### Task 5: /improve スキルにスキル分析ステップを追加

**Files:**
- Modify: `.config/claude/skills/improve/SKILL.md`

**Step 1: Step 1 のデータ可用性チェックにスキルデータを追加**

Step 1 の bash スクリプト内に追加:

```bash
for f in skill-executions.jsonl skill-benchmarks.jsonl; do
  path="$HOME/.claude/agent-memory/learnings/$f"
  if [ -f "$path" ]; then
    count=$(wc -l < "$path" | tr -d ' ')
    echo "✓ learnings/$f: ${count} 件"
  else
    echo "- learnings/$f: 未作成"
  fi
done
```

**Step 2: Step 4 のカテゴリテーブルを更新**

skills カテゴリの説明を更新:

```markdown
| **skills**     | `learnings/skill-executions.jsonl` + `learnings/skill-benchmarks.jsonl` からスキル健全性分析（トレンド/閾値判定/失敗パターン/クロスデータ相関） |
```

**Step 3: コミット**

```bash
git add .config/claude/skills/improve/SKILL.md
git commit -m "✨ feat: add skill health data to /improve workflow"
```

---

### Task 6: improve-policy.md にスキル改善の制約を追加

**Files:**
- Modify: `.config/claude/references/improve-policy.md`

**Step 1: 実験カテゴリテーブルの skills 行を更新**

```markdown
| skills | `skills/*/SKILL.md` | skill-executions.jsonl の平均スコア (Failing→Healthy) |
```

**Step 2: 評価指標テーブルの skills 行を更新**

```markdown
| skills | skill-executions 平均スコアの改善 | 20%以上のスコア向上 | スコア低下 or 変化なし |
```

**Step 3: 安全ルールにスキル固有制約を追加**

安全ルールセクションの末尾に追加:

```markdown
6. **スキル改善は実行データ5回以上** — データ不足での改善は行わない
7. **retire は段階的** — まず `[DEPRECATED]` 付与、次回 audit で改善なければ削除提案
```

**Step 4: コミット**

```bash
git add .config/claude/references/improve-policy.md
git commit -m "✨ feat: add skill improvement constraints to improve-policy"
```

---

### Task 7: テスト import の更新と全体回帰テスト

**Files:**
- Modify: `.config/claude/scripts/tests/test_session_events.py`

**Step 1: テストファイルの import に新関数を追加**

```python
from session_events import (
    BASE_CONFIDENCE,
    RULE_CONFIDENCE,
    compute_importance,
    compute_skill_score,
    emit_event,
    emit_review_feedback,
    emit_review_finding,
    emit_skill_event,
    flush_session,
    read_pending_findings,
)
```

**Step 2: 全テスト実行**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest .config/claude/scripts/tests/ -v`
Expected: ALL PASS

**Step 3: symlink 検証**

Run: `cd /Users/takeuchishougo/dotfiles && task validate-symlinks 2>/dev/null || echo "validate-symlinks not available, checking manually" && ls -la ~/.claude/scripts/policy/skill-tracker.py`
Expected: symlink が正しく解決されること

**Step 4: 最終コミット**

```bash
git add .config/claude/scripts/tests/test_session_events.py
git commit -m "✅ test: add skill tracking tests and verify integration"
```

---

## 実装サマリー

| Task | ファイル | 変更種別 | 概要 |
|------|---------|---------|------|
| 1 | `session_events.py`, テスト | 拡張 | `emit_skill_event()`, `compute_skill_score()` |
| 2 | `skill-tracker.py`, `settings.json` | 新規+拡張 | PostToolUse hook でスキル呼び出し検出 |
| 3 | `session-learner.py` | 拡張 | セッション終了時にスキルスコアを永続化 |
| 4 | `autoevolve-core.md` | 拡張 | Analyze にスキル分析、Improve にスキル改善ルール |
| 5 | `improve/SKILL.md` | 拡張 | スキルデータの可用性チェックと分析カテゴリ更新 |
| 6 | `improve-policy.md` | 拡張 | スキル改善の制約・閾値 |
| 7 | テスト | 拡張 | import 更新と全体回帰テスト |
