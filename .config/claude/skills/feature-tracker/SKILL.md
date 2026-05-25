---
name: feature-tracker
description: >
  マルチセッションプロジェクトのフィーチャーリスト管理。feature_list.json で進捗を構造化追跡。init/next/pass/status サブコマンド。
  Triggers: 'feature-tracker', '次のタスク', '進捗確認', 'フィーチャー管理', 'what feature is next'.
  Do NOT use for: GitHub Issues の操作（use /kanban）、単一セッションのタスク管理（use TaskCreate）。
origin: self
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
metadata:
  pattern: executor
---

# Feature Tracker

マルチセッションプロジェクトで機能単位の進捗を `feature_list.json` で構造化管理する。

## Usage

```
/feature-tracker init          — feature_list.json を生成
/feature-tracker next          — 次の未完了機能を表示
/feature-tracker pass <id>     — 機能をテスト合格済みにマーク
/feature-tracker status        — 全体進捗サマリ
```

## JSON Schema

`feature_list.json` はプロジェクトルートに配置する:

```json
{
  "version": 2,
  "roadmap_90_day": {
    "month1": {
      "theme": "Auth & onboarding",
      "feature_ids": ["F-001", "F-002"]
    },
    "month2": {
      "theme": "Core data flow",
      "feature_ids": ["F-003"]
    },
    "month3": {
      "theme": "Bold bet: AI assistant",
      "feature_ids": ["F-004"]
    }
  },
  "features": [
    {
      "id": "F-001",
      "category": "core",
      "description": "ユーザー認証機能",
      "steps": [
        "JWT トークン生成",
        "ログインエンドポイント",
        "ミドルウェア認証チェック"
      ],
      "priority": "P0",
      "impact": "High",
      "effort": "M",
      "bold_bet": false,
      "passes": false,
      "session_completed": null
    }
  ]
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | 一意の機能ID（`F-NNN` 形式推奨） |
| `category` | string | カテゴリ（`core`, `ui`, `infra`, `test`, `docs` 等） |
| `description` | string | 機能の説明 |
| `steps` | string[] | 実装ステップ（チェックリスト用） |
| `priority` | `P0`\|`P1`\|`P2` | P0=必須 / P1=重要 / P2=あれば良い (Khairallah P19 移植) |
| `impact` | `High`\|`Med`\|`Low` | ユーザー/ビジネスインパクト評価 |
| `effort` | `S`\|`M`\|`L` | 実装労力 (S=日, M=週, L=月単位) |
| `bold_bet` | boolean | 賭けに値する一発勝負の機能か (90 日に 1 つだけ) |
| `passes` | boolean | テスト合格済みか |
| `session_completed` | string\|null | 完了セッションの日時（ISO 8601） |

### Top-level Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | int | schema バージョン (v2 = 90-day roadmap + priority/impact/effort/bold_bet 追加) |
| `roadmap_90_day` | object\|null | optional 90-day roadmap (Khairallah P19 移植)。`month1` / `month2` / `month3` の 3 ヶ月単位。各月は `theme` (string) + `feature_ids` (string[]) を持つ |

### Migration from v1

既存 `feature_list.json` (version=1) は **そのまま動作する**:
- 新フィールド (`priority`, `impact`, `effort`, `bold_bet`, `roadmap_90_day`) はすべて optional
- `feature-tracker next` / `status` は新フィールド不在でも動作 (priority による並び替えは新フィールドがある場合のみ有効化)
- `feature-tracker init` で新規生成時は version=2 を出力、新フィールドの入力を促す

## Subcommands

### `/feature-tracker init`

1. プロジェクトルートに `feature_list.json` が既に存在するか確認
2. 存在しない場合、ユーザーに機能リストをヒアリング:
   - プロジェクトの目的
   - 主要な機能（3-10個程度）
   - 各機能の実装ステップ
3. ヒアリング結果から `feature_list.json` を生成
4. 生成後、内容を表示して確認を求める

```bash
# 確認: feature_list.json がまだ存在しないこと
test ! -f feature_list.json
```

### `/feature-tracker next`

1. `feature_list.json` を読み込む
2. `passes: false` の機能を配列順に検索
3. 最初の未完了機能を表示:
   - ID、カテゴリ、説明
   - 実装ステップ一覧
   - 推定作業量（ステップ数ベース）
4. 未完了機能がない場合: 「全機能完了」と表示

### `/feature-tracker pass <id>`

1. `feature_list.json` を読み込む
2. 指定 ID の機能を検索
3. **テスト実行を確認**: 該当機能に関連するテストが通過しているか確認を促す
4. `passes: true`、`session_completed: new Date().toISOString()` に更新
5. **学習抽出**: 完了した機能から知見を抽出し、`learnings/` に記録する
   1. 実装中に得た知見を 1-3 行で要約（例: 「〇〇パターンが有効だった」「△△は想定より複雑で見積もりが甘かった」）
   2. `~/.claude/agent-memory/learnings/` に以下の形式で追記:
      ```jsonl
      {"type": "feature_completion", "feature_id": "F-001", "description": "...", "learnings": ["..."], "date": "2026-04-05", "session_id": "..."}
      ```
   3. この learning エントリは将来の振り返り (recall や手動レビュー) で参照可能。
      旧 `/improve` Phase 2 が消費していたが、/improve は 2026-05-03 に retire 済み
6. `feature_list.json` を書き戻す
7. 次の未完了機能があれば表示

### `/feature-tracker status`

1. `feature_list.json` を読み込む
2. サマリを表示:

```
Feature Tracker Status
━━━━━━━━━━━━━━━━━━━━━
Total:     8 features
Completed: 3 (37.5%)
Remaining: 5

By Category:
  core:  2/4
  ui:    1/2
  infra: 0/2

Next: F-004 — API レート制限
```

## Integration Points

- **completion-gate.py**: `feature_list.json` 存在時、未テスト機能の完了宣言を警告
- **session-load.js**: セッション開始時に次の未完了機能を表示
- **checkpoint**: checkpoint 時に progress.log へ進捗を記録

## Notes

- `feature_list.json` は **git 管理下に置く**（チーム共有・履歴追跡のため）
- S/M 規模のタスクには不要。L 規模のマルチセッションプロジェクトで使用
- 機能の追加・削除は手動で `feature_list.json` を編集するか、`init` を再実行

## Anti-Patterns

| NG | 理由 |
|----|------|
| S 規模のタスクに feature-tracker を使う | 単一セッションで完結するなら TaskCreate で十分 |
| feature_list.json を git 管理外に置く | チーム共有・履歴追跡ができなくなる |
| ステータスを更新せずに次の機能に着手する | 進捗が不正確になり、マルチセッション管理が破綻する |
