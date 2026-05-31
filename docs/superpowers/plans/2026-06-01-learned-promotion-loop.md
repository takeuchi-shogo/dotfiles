# learned 昇格ループ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** patterns.jsonl の `type:learned`(124件、以降増える)pending を durable artifact へ昇格させる、死蔵しない軽量ループを構築し、断線した旧パイプラインを退役する。

**Architecture:** 純粋ロジックのコア1本(patterns.jsonl 読取 → generalized_detail の SHA1 で ledger 照合 → 未処理候補を JSON 出力)に、薄い入口3つ(オンデマンド skill / 週次 nudge / improve 統合)を載せる。状態は追記専用の promoted-ledger.jsonl で管理。

**Tech Stack:** Python 3.14(stdlib のみ: json/hashlib/pathlib)、pytest、bash、launchd、既存 lib `session_events.append_to_learnings`。

**Spec:** `docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md`

---

## File Structure

| ファイル | 責務 | 新規/変更 |
|---|---|---|
| `.config/claude/scripts/learner/extract-promotion-candidates.py` | コア。learned 未処理候補を抽出し JSON 出力(副作用なし) | 新規 |
| `tests/scripts/test_extract_promotion_candidates.py` | コアのユニットテスト | 新規 |
| `.config/claude/skills/promote-learnings/SKILL.md` | 入口1。候補提示→対話採否→ledger 追記 | 新規 |
| `.config/claude/scripts/runtime/nightly/learned-nudge.sh` | 入口2。件数だけ通知(レポート本体は作らない) | 新規 |
| `~/Library/LaunchAgents/com.user.nightly.friction-aggregate.plist` | nudge を指すよう ProgramArguments 差替 | 変更 |
| `.config/claude/settings.json` | Stop hook から failure-clusterer を除去 | 変更 |
| `.config/claude/scripts/runtime/friction-weekly-digest.sh` | 退役(無効化マーク) | 変更 |
| 既存 `/improve` skill の SKILL.md | チェック項目に pending 件数を1行追加 | 変更 |
| `MEMORY.md` / `memory/project_friction_detection_loop.md` | 実態に合わせ更新 | 変更 |
| `docs/decommission-log.md` | 退役措置の日付記録(30日評価用) | 新規 or 追記 |

---

## Task 1: コア extract-promotion-candidates.py

**Files:**
- Create: `.config/claude/scripts/learner/extract-promotion-candidates.py`
- Test: `tests/scripts/test_extract_promotion_candidates.py`

- [ ] **Step 1: 失敗するテストを書く**

```python
# tests/scripts/test_extract_promotion_candidates.py
import json
import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "epc",
    Path(__file__).resolve().parents[2]
    / ".config/claude/scripts/learner/extract-promotion-candidates.py",
)
epc = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(epc)


def _write(path, records):
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")


def test_extracts_only_learned(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    _write(patterns, [
        {"type": "learned", "scope": "cc-bash", "generalized_detail": "A"},
        {"type": "doom_loop", "target": "x"},
        {"type": "learned", "scope": "review-gate", "generalized_detail": "B"},
    ])
    ledger.write_text("", encoding="utf-8")
    out = epc.extract(patterns, ledger)
    assert {c["scope"] for c in out} == {"cc-bash", "review-gate"}


def test_dedup_by_generalized_detail(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    _write(patterns, [
        {"type": "learned", "scope": "s", "generalized_detail": "same insight"},
        {"type": "learned", "scope": "s", "generalized_detail": "same insight"},
    ])
    ledger.write_text("", encoding="utf-8")
    out = epc.extract(patterns, ledger)
    assert len(out) == 1


def test_skips_keys_in_ledger(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    _write(patterns, [{"type": "learned", "scope": "s", "generalized_detail": "done"}])
    key = epc.candidate_key({"generalized_detail": "done"})
    ledger.write_text(json.dumps({"key": key, "decision": "adopted"}) + "\n", encoding="utf-8")
    out = epc.extract(patterns, ledger)
    assert out == []


def test_tolerant_parse_skips_broken_lines(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    patterns.write_text(
        '{"type":"learned","scope":"s","generalized_detail":"ok"}\n'
        "{ this is broken json\n",
        encoding="utf-8",
    )
    ledger.write_text("", encoding="utf-8")
    out = epc.extract(patterns, ledger)
    assert len(out) == 1


def test_missing_patterns_file_returns_empty(tmp_path):
    out = epc.extract(tmp_path / "nope.jsonl", tmp_path / "nope2.jsonl")
    assert out == []


def test_falls_back_to_detail_when_no_generalized(tmp_path):
    patterns = tmp_path / "patterns.jsonl"
    ledger = tmp_path / "promoted-ledger.jsonl"
    _write(patterns, [{"type": "learned", "scope": "s", "detail": "only detail"}])
    ledger.write_text("", encoding="utf-8")
    out = epc.extract(patterns, ledger)
    assert out[0]["detail"] == "only detail"
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest tests/scripts/test_extract_promotion_candidates.py -v`
Expected: FAIL(モジュールが存在しない / `extract` 未定義)

- [ ] **Step 3: コアを実装**

```python
#!/usr/bin/env python3
"""learned pending を昇格候補として抽出する純粋ロジック。

入力: learnings/patterns.jsonl (type==learned) + learnings/promoted-ledger.jsonl
出力: stdout に JSON {"count": N, "candidates": [...]}
副作用なし(読み取り専用)。冪等キーは generalized_detail(無ければ detail)の SHA1。
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# scope → 推奨昇格先(初期推奨。最終配置は skill 内で Claude が提案しユーザーが承認)
SCOPE_ARTIFACT_MAP = {
    "cc-bash": "CLAUDE.md rule / references",
    "cc": "CLAUDE.md rule / references",
    "review-gate": "agents/code-reviewer.md",
    "zero-width": "policy script / security-reviewer",
    "absorb": "skills/absorb / references",
    "triage": "skills/absorb / references",
    "skills": "該当 skill",
    "skill-creation": "skills/skill-creator",
}


def candidate_key(rec: dict) -> str:
    basis = rec.get("generalized_detail") or rec.get("detail") or ""
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()


def recommend_target(scope: str | None) -> str:
    return SCOPE_ARTIFACT_MAP.get(scope or "", "(手動判断: Claude が候補内容を読んで提案)")


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # tolerant parse: 壊れた行はスキップ
    return out


def extract(patterns_path: Path, ledger_path: Path) -> list[dict]:
    processed = {e.get("key") for e in _read_jsonl(ledger_path) if e.get("key")}
    seen: set[str] = set()
    candidates: list[dict] = []
    for rec in _read_jsonl(patterns_path):
        if rec.get("type") != "learned":
            continue
        key = candidate_key(rec)
        if key in processed or key in seen:
            continue
        seen.add(key)
        candidates.append({
            "key": key,
            "scope": rec.get("scope"),
            "detail": rec.get("generalized_detail") or rec.get("detail") or "",
            "recommended_target": recommend_target(rec.get("scope")),
            "importance": rec.get("importance", 0.5),
        })
    candidates.sort(key=lambda c: -(c.get("importance") or 0.0))
    return candidates


def main() -> int:
    learnings = Path.home() / ".claude" / "agent-memory" / "learnings"
    cands = extract(learnings / "patterns.jsonl", learnings / "promoted-ledger.jsonl")
    print(json.dumps({"count": len(cands), "candidates": cands}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: テストが通ることを確認**

Run: `cd /Users/takeuchishougo/dotfiles && python3 -m pytest tests/scripts/test_extract_promotion_candidates.py -v`
Expected: PASS(6 passed)

- [ ] **Step 5: 実データでスモーク実行**

Run: `python3 .config/claude/scripts/learner/extract-promotion-candidates.py | python3 -c "import json,sys; d=json.load(sys.stdin); print('count:', d['count']); print('top scope:', d['candidates'][0]['scope'] if d['candidates'] else 'none')"`
Expected: `count:` が概ね 124 前後(ledger 空なので全 learned が候補)

- [ ] **Step 6: Commit**

```bash
git add .config/claude/scripts/learner/extract-promotion-candidates.py tests/scripts/test_extract_promotion_candidates.py
git commit -m "✨ feat(learning-loop): learned 昇格候補抽出コア + テスト"
```

---

## Task 2: skill /promote-learnings(入口1・本体)

**Files:**
- Create: `.config/claude/skills/promote-learnings/SKILL.md`

- [ ] **Step 1: SKILL.md を作成**

```markdown
---
name: promote-learnings
description: patterns.jsonl の learned (運用ログから自動抽出された知見) を durable artifact (skill/reference/CLAUDE.md rule/policy) へ昇格させる。候補を提示し対話的に採否を決め、promoted-ledger.jsonl に記録して重複を防ぐ。Triggers: '昇格', 'learned 昇格', 'promote learnings', '学びを反映', '知見を取り込む'. Do NOT use for: 外部記事の取り込み (use /absorb)、コードレビュー (use /review)。
---

# Promote Learnings

運用ログ(patterns.jsonl)から溜まった `learned` を、再利用可能な artifact に昇格させる。

## Workflow

1. **候補を取得**: 次を実行し、未処理の昇格候補を得る。
   ```bash
   python3 ~/.claude/scripts/learner/extract-promotion-candidates.py
   ```
   `count` が 0 なら「pending な learned はありません」と報告して終了。

2. **トリアージ提示**: importance 降順で候補を最大 10 件ずつ提示する。各候補に:
   - `detail`(知見本文)、`scope`、`recommended_target`(初期推奨先)
   - これは「絞った absorb」と同じ。ユーザーに採否を聞く。

3. **採否と配置**: 採用する候補ごとに:
   - `recommended_target` が `(手動判断...)` なら、detail を読んで適切な昇格先(skill / references / CLAUDE.md rule / policy script)を Claude が提案し、ユーザーが承認する。
   - 採用なら実際に該当 artifact へ追記/編集する(該当ファイルを Read してから Edit)。
   - **誤爆防止**: 既存 artifact に同等内容が既にある場合は採用せず `decision:"rejected"`(理由: already covered)。

4. **ledger 追記**: 各候補の採否を記録する(冪等性のため必須)。
   ```bash
   CC_KEY="<候補の key>" CC_DECISION="adopted" CC_TARGET="<昇格先 path>" \
   python3 - <<'PYEOF'
   import os, sys
   sys.path.insert(0, os.path.join(os.path.expanduser('~'), '.claude/scripts/lib'))
   from session_events import append_to_learnings
   append_to_learnings("promoted-ledger", {
       "key": os.environ["CC_KEY"],
       "decision": os.environ["CC_DECISION"],
       "target_artifact": os.environ.get("CC_TARGET", ""),
   })
   PYEOF
   ```
   `decision` は `adopted` / `rejected` / `deferred`。`deferred` は「今回保留」(次回また候補に出る — 冪等キーは記録するが skip 扱いにしない場合は ledger に書かない選択も可。原則 deferred は書かず次回再提示)。

5. **報告**: 採用 N 件 / 棄却 M 件 / 各昇格先を要約する。artifact を変更したら `/review` を案内する。

## Notes
- ledger (`~/.claude/agent-memory/learnings/promoted-ledger.jsonl`) は追記専用。
- 一度 `adopted`/`rejected` した key は二度と候補に出ない(コアが照合)。
```

- [ ] **Step 2: 手動シナリオ検証(候補取得→ledger 往復)**

Run(候補取得が動くか):
```bash
python3 ~/.claude/scripts/learner/extract-promotion-candidates.py | head -30
```
Run(ledger 追記が動くか・テスト key で):
```bash
CC_KEY="__smoke_test__" CC_DECISION="rejected" CC_TARGET="" python3 - <<'PYEOF'
import os, sys
sys.path.insert(0, os.path.join(os.path.expanduser('~'), '.claude/scripts/lib'))
from session_events import append_to_learnings
append_to_learnings("promoted-ledger", {"key": os.environ["CC_KEY"], "decision": os.environ["CC_DECISION"]})
print("ledger append ok")
PYEOF
tail -1 ~/.claude/agent-memory/learnings/promoted-ledger.jsonl
```
Expected: `ledger append ok` + 追記行に `"key":"__smoke_test__"`。確認後この行は手動で消すか放置(コアは learned 側に同 key が無いので無害)。

- [ ] **Step 3: Commit**

```bash
git add .config/claude/skills/promote-learnings/SKILL.md
git commit -m "✨ feat(learning-loop): /promote-learnings skill (対話採否→ledger)"
```

---

## Task 3: 週次 nudge スクリプト + launchd 差し替え(入口2)

**Files:**
- Create: `.config/claude/scripts/runtime/nightly/learned-nudge.sh`
- Modify: `~/Library/LaunchAgents/com.user.nightly.friction-aggregate.plist`

- [ ] **Step 1: nudge スクリプトを作成(件数通知のみ、レポート本体は作らない)**

```bash
#!/usr/bin/env bash
# learned 昇格 pending の件数だけを通知する。レポート本体は作らない(死蔵防止)。
set -euo pipefail
LOG=/tmp/learned-nudge.log
CORE="$HOME/.claude/scripts/learner/extract-promotion-candidates.py"

if [[ ! -f "$CORE" ]]; then
  echo "[$(date -Iseconds)] core missing: $CORE" >> "$LOG"
  exit 0
fi

SUMMARY="$(python3 "$CORE" 2>>"$LOG" | python3 -c '
import json, sys
d = json.load(sys.stdin)
n = d["count"]
if n == 0:
    print("")  # 0件なら通知しない(ノイズ防止)
else:
    scopes = {}
    for c in d["candidates"][:50]:
        s = c.get("scope") or "?"
        scopes[s] = scopes.get(s, 0) + 1
    top = ", ".join(f"{k}({v})" for k, v in sorted(scopes.items(), key=lambda x: -x[1])[:3])
    print(f"learned 昇格 pending {n} 件。top scope: {top}。/promote-learnings で処理を。")
')"

if [[ -n "$SUMMARY" ]]; then
  echo "[$(date -Iseconds)] $SUMMARY" >> "$LOG"
  # macOS 通知(失敗は無視・best-effort)
  osascript -e "display notification \"$SUMMARY\" with title \"learned 昇格\"" 2>/dev/null || true
fi
exit 0
```

- [ ] **Step 2: 実行権限付与とスモーク実行**

Run:
```bash
chmod +x .config/claude/scripts/runtime/nightly/learned-nudge.sh
bash .config/claude/scripts/runtime/nightly/learned-nudge.sh && tail -1 /tmp/learned-nudge.log
```
Expected: pending があれば「learned 昇格 pending N 件...」がログに出る

- [ ] **Step 3: launchd plist の ProgramArguments を nudge に差し替え**

`~/Library/LaunchAgents/com.user.nightly.friction-aggregate.plist` の該当 string を編集:
```
旧: <string>/Users/takeuchishougo/dotfiles/scripts/runtime/nightly/run-friction-aggregate.sh</string>
新: <string>/Users/takeuchishougo/.claude/scripts/runtime/nightly/learned-nudge.sh</string>
```
(Label は当面据え置きで可。気になるなら別タスクでリネーム)

- [ ] **Step 4: launchd を再読込して検証**

Run:
```bash
launchctl unload ~/Library/LaunchAgents/com.user.nightly.friction-aggregate.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.user.nightly.friction-aggregate.plist
launchctl list | grep friction-aggregate
```
Expected: エントリが存在(exit 0)。即時テストは `launchctl start com.user.nightly.friction-aggregate` で `/tmp/learned-nudge.log` を確認

- [ ] **Step 5: Commit**

```bash
git add .config/claude/scripts/runtime/nightly/learned-nudge.sh
git commit -m "✨ feat(learning-loop): 週次 learned nudge (件数通知のみ)"
```
(plist は `~/Library/LaunchAgents/` で repo 外。symlink でなければ commit 対象外。管理方法は既存 dotfiles の慣習に従う)

---

## Task 4: 旧パイプライン退役(harness-stability 準拠:無効化 → 30日評価)

**Files:**
- Modify: `.config/claude/settings.json`(Stop hook から failure-clusterer 除去)
- Modify: `.config/claude/scripts/runtime/friction-weekly-digest.sh`(退役マーク)
- Create/Append: `docs/decommission-log.md`

- [ ] **Step 1: settings.json の Stop hook から failure-clusterer を除去**

該当箇所(`session-learner.py && failure-clusterer.py` の行):
```
旧: "command": "(python3 $HOME/.claude/scripts/learner/session-learner.py && python3 $HOME/.claude/scripts/learner/failure-clusterer.py) >> /tmp/claude-learner.log 2>&1 &",
新: "command": "python3 $HOME/.claude/scripts/learner/session-learner.py >> /tmp/claude-learner.log 2>&1 &",
```
session-learner は patterns/quality/metrics を書く現役なので残す。failure-clusterer のみ外す。

- [ ] **Step 2: friction-weekly-digest.sh を退役マーク**

ファイル先頭(shebang 直後)に追記:
```bash
# DECOMMISSIONED 2026-06-01: friction-events.jsonl 入力枯渇のため退役。
# 後継は learned-nudge.sh。30日評価後(2026-07-01以降)に削除可。
# 早期 exit で no-op 化する。
echo "[decommissioned] friction-weekly-digest.sh は learned-nudge.sh に置換されました" >&2
exit 0
```

- [ ] **Step 3: 退役ログを記録(30日評価の起点)**

`docs/decommission-log.md` に追記(無ければ作成):
```markdown
# Decommission Log

| 措置日 | 対象 | 理由 | 削除評価日 |
|---|---|---|---|
| 2026-06-01 | settings.json Stop hook の failure-clusterer.py | category==error 空振り(入力スキーマ不整合) | 2026-07-01 |
| 2026-06-01 | friction-weekly-digest.sh | friction-events 入力枯渇、learned-nudge.sh に置換 | 2026-07-01 |
| 2026-06-01 | launchd friction-aggregate(旧 run-friction-aggregate.sh 指向) | 同上 | 2026-07-01 |
| 休眠中 | autoevolve-runner.sh(cron 未登録で元から不動) | 触らず寝かせる | 2026-07-01 評価 |
```

- [ ] **Step 4: 設定検証**

Run:
```bash
cd /Users/takeuchishougo/dotfiles && task validate-configs && task validate-symlinks
```
Expected: PASS(settings.json が valid JSON、symlink 整合)

- [ ] **Step 5: Commit**

```bash
git add .config/claude/settings.json .config/claude/scripts/runtime/friction-weekly-digest.sh docs/decommission-log.md
git commit -m "🔥 chore(learning-loop): 断線した friction パイプラインを退役(無効化→30日評価)"
```

---

## Task 5: /improve への pending 件数統合(入口3)

**Files:**
- Modify: 既存 `/improve` skill の SKILL.md

- [ ] **Step 1: /improve skill の正確なパスを特定**

Run:
```bash
ls -d ~/.claude/skills/improve* .config/claude/skills/improve* 2>/dev/null
grep -rl "skill / docs / code を並列点検\|整理候補" .config/claude/skills/*/SKILL.md 2>/dev/null
```
→ 該当する SKILL.md を昇格件数チェックの統合先とする(`improve-codebase-architecture` ではなく、skill/docs/code 点検版の方)。

- [ ] **Step 2: SKILL.md の冒頭チェック項目に1行追加**

特定した SKILL.md の最初の点検フェーズに、次の1行を追加:
```markdown
- **learned 昇格 pending**: `python3 ~/.claude/scripts/learner/extract-promotion-candidates.py` の `count` を確認。多ければ(目安 10件超)`/promote-learnings` を案内する。
```

- [ ] **Step 3: Commit**

```bash
git add <特定した SKILL.md>
git commit -m "🔧 chore(learning-loop): /improve に learned 昇格 pending 件数チェックを統合"
```

---

## Task 6: ドキュメント実態反映

**Files:**
- Modify: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md`(line 67 付近)
- Modify: 同 `memory/project_friction_detection_loop.md`

- [ ] **Step 1: MEMORY.md の friction セクションを実態に更新**

旧(line 67 付近):
```
- [project_friction_detection_loop.md] — friction-events.jsonl 中心の改善ループ。telemetry 統一済み、AutoEvolve Phase 1 接続済み
```
新:
```
- [project_friction_detection_loop.md] — 旧 friction-events 中心ループは断線(5/7停止・全件 raw/pending)し退役。後継は learned 昇格ループ(patterns.jsonl→/promote-learnings)。設計: docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md
```

- [ ] **Step 2: project_friction_detection_loop.md を更新**

旧ループが断線していた事実(根因:category スキーマ不整合 / autoevolve-runner cron 未登録 / friction 入力枯渇)と、新ループ(コア+3入口、ledger 冪等管理)へ移行したことを反映する。「telemetry 統一済み・AutoEvolve Phase 1 接続済み」の誤った記述を削除。

- [ ] **Step 3: Commit**

```bash
git add ~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md ~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/project_friction_detection_loop.md
git commit -m "📝 docs(memory): friction ループの実態(断線→learned 昇格ループ移行)を反映"
```

---

## Self-Review

**1. Spec coverage:**
- コア(A データフロー/状態管理)→ Task 1 ✅
- 入口1 skill → Task 2 ✅ / 入口2 nudge → Task 3 ✅ / 入口3 improve → Task 5 ✅
- 昇格先マップ → Task 1 `SCOPE_ARTIFACT_MAP` + Task 2 手動 fallback ✅
- 退役範囲(failure-clusterer/launchd/digest/autoevolve 休眠)→ Task 4 ✅
- harness-stability 30日評価 → Task 4 Step 3 decommission-log ✅
- テスト(冪等性/tolerant parse/空入力)→ Task 1 Step 1 ✅
- ドキュメント実態反映 → Task 6 ✅

**2. Placeholder scan:** コード/コマンドは全て実体を記載。Task 5 Step 1 の「パス特定」は placeholder ではなく実行可能な特定手順(/improve の正確なパスが環境依存のため)。

**3. Type consistency:** `candidate_key` / `extract` / `recommend_target` / `SCOPE_ARTIFACT_MAP` はコア(Task 1)で定義し、Task 2/3/5 から同名で参照。ledger スキーマ `{key, decision, target_artifact}` は Task 1(照合)・Task 2(追記)・spec で一致。

**4. リスク(spec 由来):** skill 未起動で candidates 滞留 → nudge 件数で気づく。3ヶ月起動0なら本ループ退役を再評価(spec 撤退条件)。

---

## Execution Handoff

実装は3コミット相当のまとまり(コア / skill+入口 / 退役+docs)。コードは harness 変更を含むため Codex Review Gate 対象。

**推奨**: 別セッションで fresh context にて subagent-driven-development または /rpi で Task 順に実行(過去の運用パターン)。worktree 分離も検討。
