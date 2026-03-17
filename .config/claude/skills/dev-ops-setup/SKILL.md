---
name: dev-ops-setup
description: プロジェクトの開発オペレーション設定をセットアップする。GitHub Projects カンバン、Slack 連携、GTD キャプチャラベル等をローカル設定ファイルに保存。モノレポでチームごとに異なる設定が可能。
disable-model-invocation: true
allowed-tools: Bash(gh *), Read, Write, Edit
argument-hint: "[--reset]"
metadata:
  pattern: pipeline
---

# Dev Ops Setup

プロジェクトのローカル開発オペレーション設定を対話的にセットアップする。

## 設定ファイル

- **パス**: `.claude/dev-ops.local.json`
- **git管理**: しない（`.gitignore` に追加）
- **理由**: モノレポで複数チームが異なる設定を持てるようにするため

## 前提条件チェック

1. `gh` CLI がインストール・認証済みか確認（`gh auth status`）
2. git リポジトリ内か確認
3. `$ARGUMENTS` に `--reset` が含まれる場合、既存設定を削除して再セットアップ

## 既存設定の確認

!`cat .claude/dev-ops.local.json 2>/dev/null || echo "NOT_CONFIGURED"`

上記が `NOT_CONFIGURED` でなければ、既存設定を表示して「更新しますか？」と確認する。
`--reset` 引数がある場合はスキップして再セットアップ。

## セットアップ手順

以下の情報を対話的に収集する。自動取得できるものは `gh` CLI で取得し、ユーザーに確認を求める。

### Step 1: GitHub リポジトリ情報（自動検出）

```bash
# owner/repo を自動検出
gh repo view --json owner,name
```

検出結果をユーザーに表示し、正しいか確認。

### Step 2: GitHub Projects 連携（オプション）

```bash
# リポジトリに紐づく Projects を一覧
gh project list --owner {owner} --format json --limit 20
```

- プロジェクト一覧を表示し、使用するものを選択してもらう
- 「使わない」も選択肢に含める
- 選択されたら、プロジェクトのフィールド情報を取得:

```bash
gh project field-list {project_number} --owner {owner} --format json
```

- Status フィールドの選択肢（Backlog, Ready, In Progress 等）を自動取得

### Step 3: チーム設定（モノレポ対応）

以下を質問:
- **チーム名**（例: frontend-team）— 識別用
- **チームラベル**（例: `["frontend", "team-a"]`）— Issue フィルタリング用
- **自分の GitHub ユーザー名** — assignee フィルタ用（`gh api user` で自動取得を提案）

### Step 4: Slack 連携（オプション）

- Slack Webhook URL を質問（空欄ならスキップ）
- 投稿先チャンネル名

### Step 5: GTD キャプチャ設定

- キャプチャ用ラベル名（デフォルト: `inbox`）
- 優先度ラベル体系（デフォルト: `["P0", "P1", "P2", "P3"]`）

### Step 6: 設定ファイル生成

収集した情報を以下の JSON 形式で `.claude/dev-ops.local.json` に保存:

```json
{
  "version": 1,
  "team_name": "frontend-team",
  "github": {
    "owner": "org-name",
    "repo": "monorepo",
    "my_username": "takeuchishougo"
  },
  "project": {
    "number": 5,
    "id": "PVT_xxx",
    "status_field": {
      "id": "PVTSSF_xxx",
      "options": {
        "backlog": "option-id-1",
        "ready": "option-id-2",
        "in_progress": "option-id-3",
        "in_review": "option-id-4",
        "done": "option-id-5"
      }
    }
  },
  "slack": {
    "webhook_url": "https://hooks.slack.com/...",
    "channel": "#frontend-dev"
  },
  "gtd": {
    "capture_label": "inbox",
    "priority_labels": ["P0", "P1", "P2", "P3"]
  },
  "team_labels": ["frontend"],
  "created_at": "2026-03-12T09:00:00+09:00",
  "updated_at": "2026-03-12T09:00:00+09:00"
}
```

`project` セクションは GitHub Projects を使わない場合は `null`。
`slack` セクションは Slack を使わない場合は `null`。

### Step 7: .gitignore 更新

`.gitignore` に以下が含まれていなければ追加:

```
# Dev Ops local config (team-specific, not shared)
.claude/dev-ops.local.json
```

既に `.claude/` 全体が gitignore されている場合はスキップ。

### Step 8: 完了メッセージ

セットアップ完了後、使えるようになったスキル一覧を表示:

```
セットアップ完了！以下のスキルが使えます:

/morning          - 朝の計画: 今日のタスクを提案
/capture <text>   - 思いつきを即座にキャプチャ
/kanban [action]  - カンバン操作・進捗確認
/meeting-minutes  - 議事録からIssue更新
/weekly-review    - 週次レビュー・棚卸し
/dev-insights     - 開発パターン分析

※ GitHub Projects 未設定の場合、/kanban は GitHub Issues のみで動作します
```
