# Obsidian Vault 自動蓄積パイプライン

## Summary

Claude Code のセッションデータ（memory、日報、暗黙知、手動メモ）を Obsidian Vault に自動同期するパイプライン。シェルスクリプト中心のアプローチで、hook（即時）と cron（日次）のハイブリッドトリガーで動作する。

## Motivation

- Claude Code の memory や学習データは `~/.claude/` 配下に散在しており、Obsidian から検索・リンクできない
- `/daily-report` の出力は `~/daily-reports/` に保存されるが vault と切り離されている
- セッション中の気づきを構造化してキャプチャする仕組みがない

## Architecture

```
┌─ Claude Code セッション ─────────────────────────────┐
│                                                       │
│  /note "内容"  ──→  00-Inbox/ に即時書き出し          │
│                     (note-to-vault.sh)                 │
│                                                       │
│  memory/*.md 更新 ──→ PostToolUse hook                │
│                     → sync-memory-to-vault.sh 即時実行 │
└───────────────────────────────────────────────────────┘

┌─ cron (毎日 23:00 JST) ──────────────────────────────┐
│                                                       │
│  23:00  sync-daily-report.sh                          │
│           ~/daily-reports/*.md → 07-Daily/            │
│                                                       │
│  23:05  sync-session-insights.sh                      │
│           セッション JSONL → 00-Inbox/                │
│                                                       │
│  23:10  sync-tacit-knowledge.sh                       │
│           agent-memory/learnings/ → 04-Galaxy/        │
└───────────────────────────────────────────────────────┘

共通: OBSIDIAN_VAULT_PATH 環境変数で vault の場所を解決
```

## Vault フォルダマッピング

| ソース | 出力先 | 理由 |
|--------|--------|------|
| `memory/*.md` | `08-Agent-Memory/` | エージェントの蓄積知識。日常ノートと分離 |
| `/daily-report` 出力 | `07-Daily/` | 既存フォルダ。日付ベースの日報 |
| セッション JSONL | `00-Inbox/` | 未整理の生データ。後で手動整理 |
| `agent-memory/learnings/` | `04-Galaxy/` | パーマネントノート相当の知見 |
| `/note` 手動メモ | `00-Inbox/` | 即時キャプチャ。後で整理 |

## Components

### 1. sync-memory-to-vault.sh（既存改修）

- **変更**: `DEST_DIR` を `"07-Agent-Memory"` → `"08-Agent-Memory"` に変更
- **マイグレーション**: vault 内に旧 `07-Agent-Memory/` が存在する場合、中身を `08-Agent-Memory/` に移動し旧ディレクトリを削除する（初回実行時のみ）
- **トリガー**: PostToolUse hook（memory ディレクトリ配下の Write/Edit 検知）
- **冪等性**: mtime 比較でスキップ
- **frontmatter**: `obsidian_tags: [agent-memory, {type}]`, `synced_at`

### 2. sync-daily-report.sh（新規）

- **入力**: `~/daily-reports/*.md`
- **出力**: `$VAULT/07-Daily/YYYY-MM-DD.md`
- **処理**: ファイルコピー + frontmatter 付与
- **frontmatter**: `tags: [agent/daily-report]`, `synced_at`
- **冪等性**: 同名ファイルが存在し mtime が古ければスキップ
- **トリガー**: cron 23:00

### 3. sync-session-insights.sh（新規）

- **入力**: `~/.claude/projects/*/sessions-index.json` → 各セッション JSONL
- **出力**: `$VAULT/00-Inbox/insight-YYYY-MM-DD.md`
- **処理**:
  1. 今日の日付のセッションを sessions-index.json から収集
  2. 各セッション JSONL からユーザーメッセージを抽出（先頭200文字 x 最大10件）
  3. プロジェクト名 + firstPrompt + ユーザー発言を1ファイルにまとめる
- **frontmatter**: `tags: [agent/session-insight, status/seed]`
- **冪等性**: 同日のファイルがあればスキップ
- **トリガー**: cron 23:05

### 4. sync-tacit-knowledge.sh（新規）

- **入力**: `~/.claude/agent-memory/learnings/*.jsonl`
- **出力**: `$VAULT/04-Galaxy/YYYYMMDDHHMMSS-learning-{hash}.md`
- **処理**:
  1. errors.jsonl, quality.jsonl から今日のエントリを jq で抽出
  2. 各エントリを permanent note テンプレートに変換
- **frontmatter**: `tags: [type/permanent, agent/tacit-knowledge, status/seed]`
- **冪等性**: 同一 hash のファイルがあればスキップ
- **トリガー**: cron 23:10

### 5. note-to-vault.sh + /note スキル（新規）

- **トリガー**: `/note 残したい内容` コマンド
- **処理**: 引数テキストを `$VAULT/00-Inbox/note-YYYYMMDDHHMMSS.md` に書き出す
- **frontmatter**: `tags: [status/seed]`, `created: YYYY-MM-DD`
- **スキル定義**: 薄いラッパー。引数を受け取り shell script を Bash で実行

## Environment & Configuration

### 環境変数

`.zshenv` に追加:
```bash
export OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault"
```

### Hook 設定

`settings.json` に PostToolUse hook を追加。Claude Code の hook スキーマには `pattern` フィールドが存在しないため、ファイルパスフィルタは `command` 側で stdin から `tool_input.file_path` を読んで判定する:

```json
{
  "type": "command",
  "event": "PostToolUse",
  "matcher": "Write|Edit",
  "command": "bash -c 'f=$(cat | jq -r \".tool_input.file_path // empty\"); [[ \"$f\" =~ memory/.*\\.md$ ]] && ~/.config/claude/scripts/runtime/sync-memory-to-vault.sh || true'"
}
```

### Cron 設定

cron は `.zshenv` を読まないため、各エントリに `OBSIDIAN_VAULT_PATH` を明示する:

```crontab
OBSIDIAN_VAULT_PATH=/Users/takeuchishougo/Documents/Obsidian Vault
0 23 * * * OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault" ~/.config/claude/scripts/runtime/sync-daily-report.sh
5 23 * * * OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault" ~/.config/claude/scripts/runtime/sync-session-insights.sh
10 23 * * * OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault" ~/.config/claude/scripts/runtime/sync-tacit-knowledge.sh
```

**注意**: vault パスにスペースが含まれるため、スクリプト内では必ず `"$VAULT_PATH"` とクォートする。

### 実装前確認事項

以下のパスは実装前に実在を確認すること（存在しない場合はスクリプトが空振りするため graceful skip する）:
- `~/.claude/projects/*/sessions-index.json` — セッション JSONL の探索元
- `~/.claude/agent-memory/learnings/*.jsonl` — 暗黙知の入力元
- 日付判定は JST (UTC+9) 基準とする（`TZ=Asia/Tokyo date` を使用）

### Vault CLAUDE.md カスタマイズ

- 名前: takeuchishougo
- 役割: ソフトウェアエンジニア
- 関心分野: AI エージェント設計、Claude Code ハーネスエンジニアリング、Go、開発者生産性
- トーン: MIXED
- 言語: ja
- Vault Architecture テーブルに `08-Agent-Memory` を追加

## File Inventory

```
dotfiles/
├── .config/claude/
│   ├── scripts/runtime/
│   │   ├── sync-memory-to-vault.sh    (既存改修)
│   │   ├── sync-daily-report.sh       (新規)
│   │   ├── sync-session-insights.sh   (新規)
│   │   ├── sync-tacit-knowledge.sh    (新規)
│   │   └── note-to-vault.sh           (新規)
│   ├── skills/note/
│   │   └── SKILL.md                   (新規)
│   └── settings.json                  (hook 追加)
├── .zshenv                            (環境変数追加)
└── templates/obsidian-vault/
    └── CLAUDE.md                      (カスタマイズ)
```

## Acceptance Criteria

- [ ] `OBSIDIAN_VAULT_PATH` が設定され、全スクリプトが vault にアクセスできる
- [ ] memory 更新時に `08-Agent-Memory/` にファイルが同期される
- [ ] `/daily-report` 出力が `07-Daily/` に同期される
- [ ] セッション JSONL から `00-Inbox/insight-*.md` が生成される
- [ ] tacit knowledge から `04-Galaxy/` にパーマネントノートが生成される
- [ ] `/note テスト` で `00-Inbox/note-*.md` が即座に作成される
- [ ] 全スクリプトが冪等（2回実行しても重複しない）
- [ ] vault の CLAUDE.md がカスタマイズされている
- [ ] cron が正しく登録されている
