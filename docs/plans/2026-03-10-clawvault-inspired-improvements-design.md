---
status: active
last_reviewed: 2026-04-23
---

# ClawVault 着想による Claude Code 設定改善 — 設計書

**日付**: 2026-03-10
**ステータス**: approved
**参照**: https://github.com/Versatly/clawvault (★406, TypeScript, AI agent memory system)

---

## 背景

ClawVault の構造化メモリシステムを調査し、既存の AutoEvolve / hook 設計に取り入れるべき3つの改善領域を特定した。既存の hook ベース設計哲学（非破壊的、軽量、独立性）を維持しつつ、段階的にレイヤーを追加する。

## スコープ

| レイヤー | 改善領域                                  | ClawVault の着想元                       |
| -------- | ----------------------------------------- | ---------------------------------------- |
| Layer 1  | セッション耐障害性 (Checkpoint)           | `wake`/`sleep`/`checkpoint`/`recover`    |
| Layer 2  | 学習データの質的向上 (Importance Scoring) | Observer の `c=0.9\|i=0.85` スコアリング |
| Layer 3  | コンテキスト取得の賢さ (Context Profiles) | `--profile planning\|incident\|handoff`  |

## 設計方針

- **アプローチ 1: 段階的レイヤー追加** を採用
- 各レイヤーは独立して動作し、単体でテスト可能
- 既存 18 hook + AutoEvolve を壊さない
- ClawVault のコンセプトのみ移植（OpenClaw/qmd 依存は取り込まない）

---

## Layer 1: Checkpoint System

### 目的

セッション中の作業状態を中間保存し、context death や crash から回復可能にする。

### 新規ファイル

| ファイル                        | 種類               | 役割                           |
| ------------------------------- | ------------------ | ------------------------------ |
| `scripts/checkpoint-manager.py` | PostToolUse hook   | 自動 checkpoint 判定・実行     |
| `commands/checkpoint.md`        | スラッシュコマンド | 手動 `/checkpoint`             |
| `scripts/checkpoint-recover.py` | SessionStart hook  | 前回 checkpoint からの復元提案 |

### データ構造

保存先: `~/.claude/session-state/checkpoints/`

```json
{
  "timestamp": "ISO8601",
  "trigger": "auto:edit_threshold | auto:context_threshold | auto:time_threshold | manual",
  "working_on": "auth rollout",
  "focus": ["src/lib/auth.ts", "tests/auth.test.ts"],
  "branch": "feat/auth",
  "git_status": "M src/lib/auth.ts\nA tests/auth.test.ts",
  "staged_diff_summary": "auth モジュールにトークンリフレッシュ追加",
  "edit_count": 12,
  "context_usage_pct": 45,
  "active_profile": "debugging",
  "profile_source": "auto:keyword_match",
  "session_events_snapshot": []
}
```

最新ポインタ: `~/.claude/session-state/last-checkpoint.json`

### 自動 checkpoint トリガー条件

PostToolUse (Edit|Write) で `checkpoint-manager.py` が発火:

- `edit_count >= 15` — 15回以上の編集
- `context_pct >= 60` — コンテキスト使用率 60% 超
- `elapsed_minutes >= 30` — 前回 checkpoint から 30分経過
- いずれか1つを満たし、かつ前回 checkpoint から最低 5分経過で発火

### 復元フロー

SessionStart で `checkpoint-recover.py` が発火:

1. `last-checkpoint.json` を読む
2. 前回セッションが正常終了 → 何もしない
3. 異常終了（checkpoint はあるが session-save がない）→ 復元情報を注入

### 保持ポリシー

最新 5 件の checkpoint を保持。古いものは自動削除。

---

## Layer 2: Importance Scoring

### 目的

learnings JSONL の全エントリに重要度 (importance) と確信度 (confidence) を付与。書き込み時はルールベース、分析時は LLM で再評価。

### 変更ファイル

| ファイル                      | 変更内容                                         |
| ----------------------------- | ------------------------------------------------ |
| `scripts/session_events.py`   | `emit_event()` に importance/confidence 自動付与 |
| `scripts/session-learner.py`  | flush 時にスコア付きで書き出し                   |
| `agents/autolearn.md`         | LLM 再スコアリング + 昇格判定ロジック追加        |
| `references/scoring-rules.md` | スコアリングルール定義（新規）                   |

### JSONL フォーマット拡張

既存フィールドに追加:

| フィールド         | 型        | 説明                                                        |
| ------------------ | --------- | ----------------------------------------------------------- |
| `importance`       | `0.0-1.0` | 重要度。高いほど昇格対象                                    |
| `confidence`       | `0.0-1.0` | スコアの確信度                                              |
| `type`             | `string`  | `error` / `quality` / `pattern` / `correction` / `decision` |
| `scored_by`        | `string`  | `"rule"` or `"llm"`                                         |
| `promotion_status` | `string`  | `"pending"` / `"promoted"` / `"archived"`                   |

### ルールベーススコアリング

```python
IMPORTANCE_RULES = {
    "high": [  # 0.8-1.0
        (r"EACCES|Permission denied", 0.9),
        (r"segfault|SIGSEGV|OOM", 1.0),
        (r"GP-001|GP-002|GP-003", 0.8),
        (r"security|vulnerability|injection", 0.9),
    ],
    "medium": [  # 0.4-0.7
        (r"Cannot find module|ModuleNotFoundError", 0.5),
        (r"TypeError|ReferenceError", 0.5),
        (r"timeout|ETIMEDOUT", 0.6),
    ],
    "low": [  # 0.0-0.3
        (r"warning:|WARN", 0.2),
        (r"deprecated", 0.3),
    ],
}
BASE_IMPORTANCE = {"error": 0.5, "quality": 0.6, "pattern": 0.4, "correction": 0.7}
```

### 昇格ルール

| 条件                                    | アクション                   |
| --------------------------------------- | ---------------------------- |
| `importance >= 0.8` + 1回出現           | 自動昇格候補                 |
| `0.4 <= importance < 0.8` + 3回以上出現 | 昇格候補                     |
| `importance < 0.4`                      | 昇格なし。90日後にアーカイブ |

### 後方互換性

- スコアなしエントリは `importance ?? 0.5` でフォールバック
- 既存 JSONL を壊さない（フィールド追加のみ）

---

## Layer 3: Context Profiles

### 目的

タスク種類に応じて SessionStart で注入するコンテキストの内容・量・優先度を切り替える。

### プロファイル定義

| プロファイル | 用途                 | learnings フィルタ                               |
| ------------ | -------------------- | ------------------------------------------------ |
| `default`    | 通常の開発作業       | i>=0.4, 上位5件                                  |
| `planning`   | 設計・アーキテクチャ | `type: decision, pattern` 優先, 上位8件          |
| `debugging`  | バグ修正・調査       | `type: error, correction` 優先, i>=0.3, 上位10件 |
| `incident`   | 障害対応・緊急       | 直近24h の全 learnings, 時系列優先               |

### 自動判別

`agent-router.py` の UserPromptSubmit hook を拡張:

```python
PROFILE_KEYWORDS = {
    "planning": [r"設計|アーキテクチャ|architecture|design|plan|構成", ...],
    "debugging": [r"バグ|bug|エラー|error|失敗|fail", ...],
    "incident": [r"障害|incident|緊急|urgent|本番|production", ...],
}
```

### 手動オーバーライド

プロンプトに `@planning` `@debugging` `@incident` を含めると keyword 判別を上書き。

### 新規・変更ファイル

| ファイル                         | 変更種別 |
| -------------------------------- | -------- |
| `references/context-profiles.md` | 新規     |
| `scripts/agent-router.py`        | 拡張     |
| `scripts/session-load.js`        | 拡張     |

---

## 全体データフロー

```
セッション中                                     SessionStart
┌─────────────────────────────────────┐        ┌──────────────────────────────┐
│  PostToolUse (Edit|Write|Bash)      │        │  checkpoint-recover.py       │
│       │                              │        │    ↓                         │
│  checkpoint-manager.py              │        │  session-load.js             │
│    ├─ edit_count >= 15?             │        │    ├─ profile = auto-detect  │
│    ├─ context_pct >= 60%?           │        │    ├─ loadContextForProfile()│
│    └─ elapsed >= 30min?             │        │    └─ inject learnings       │
│       │ YES                          │        └──────────────────────────────┘
│       ▼                              │
│  checkpoint-{ts}.json               │        UserPromptSubmit
│  (working_on, focus, profile, ...)  │        ┌──────────────────────────────┐
│                                      │        │  agent-router.py             │
│  session_events.py                  │        │    ├─ @override check        │
│    ├─ emit_event("error", {...})    │        │    ├─ keyword profile match  │
│    ├─ + importance (rule-based)     │        │    └─ additionalContext 注入  │
│    └─ + confidence (rule-based)     │        └──────────────────────────────┘
└─────────────────────────────────────┘
                │
        SessionEnd/Stop → session-learner.py → learnings/*.jsonl (with scores)
                │
        分析 (on-demand/cron) → autolearn (LLM re-score) → knowledge-gardener (promote)
```

## ファイル変更サマリー

- **新規**: 5ファイル (checkpoint-manager.py, checkpoint-recover.py, checkpoint.md, scoring-rules.md, context-profiles.md)
- **変更**: 7ファイル (session_events.py, session-learner.py, agent-router.py, session-load.js, pre-compact-save.js, autolearn.md, settings.json)

## リスク軽減策

| リスク                                      | 対策                                       |
| ------------------------------------------- | ------------------------------------------ |
| checkpoint 書き込みがセッションを遅延させる | 非同期書き込み、silent fail                |
| importance ルールが不正確                   | `scored_by: "rule"` 記録、LLM で補正       |
| プロファイル誤判別                          | `@override` 手動切り替え、default fallback |
| 既存 JSONL との非互換                       | フィールド追加のみ、`?? 0.5` 後方互換      |
| checkpoint ファイル肥大化                   | 最新5件保持、自動クリーンアップ            |
