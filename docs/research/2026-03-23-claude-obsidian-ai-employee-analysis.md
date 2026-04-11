---
source: "Claude + Obsidian = A true AI employee (shared article, no URL)"
date: 2026-03-23
status: partially-integrated
related: docs/research/2026-03-22-obsidian-agent-persistent-memory-analysis.md
---

## Source Summary

### Main Claim

Obsidian を構造化ナレッジベースとして使い、Claude に MCP 経由で読み書きさせることで「記憶を持つ AI 従業員」を実現できる。通話文字起こしの自動処理で Vault が日々成長し、複利的にコンテキストが充実する。

### Techniques

1. **構造化ナレッジベース**: Memory file (onboarding doc), Client Roster, Action Tracker, Frameworks Library, Templates folder をリンクグラフで接続
2. **自動メモリループ**: Fathom (通話文字起こし) -> Zapier -> Google Drive -> Claude が処理 -> Vault に書き戻し (決定事項, アクション, 要約)
3. **Obsidian MCP**: Node パッケージで Claude に Vault の直接読み書きアクセスを付与
4. **マルチツール MCP**: Google Drive + Slack + Google Calendar を Claude Cowork に接続
5. **カスタムインストラクション**: 「毎回 Vault を検索してから回答」+ 書き戻しルーティングルール
6. **Google Drive に Vault 配置**: マルチマシン同期のため
7. **複利効果**: 毎日のセッションで Vault が成長 -> AI のコンテキストが自動充実

### Rationale

著者の実体験ベース。3週間前の通話で決めた内容を AI が想起した事例を紹介。定量データなし。

### Prerequisites

- ビジネス運営者 (15人規模の agency/サービス業)
- クライアントワーク中心
- Claude Cowork (デスクトップアプリ) 利用

## Gap Analysis

| # | Technique | Status | Detail |
|---|-----------|--------|--------|
| 1 | 構造化ナレッジベース | **Already** | CLAUDE.md + MEMORY.md + Progressive Disclosure で記事を超える水準。Vault 用に `obsidian-vault-setup` で Zettelkasten + PARA ハイブリッド構成済み |
| 2 | 自動メモリループ (Fathom -> Zapier -> Drive -> Vault) | **Gap** | `/digest` は手動貼り付けのみ。文字起こし -> Drive 監視 -> 自動処理 -> Vault 書き戻しのパイプラインは未実装 |
| 3 | Obsidian MCP サーバー | **Partial** | Vault ルートで Claude Code 起動する前提のスキル群あり。MCP サーバー経由の Vault 接続は settings.json に未設定 |
| 4 | マルチツール MCP 統合 | **Partial** | Discord MCP 設定済み。Google Drive / Calendar / Slack MCP は未確認 |
| 5 | カスタムインストラクション | **Already** | Progressive Disclosure + `<important if>` タグで条件付き動作。記事の単純な 1 行指示より高度 |
| 6 | Google Drive に Vault 配置 | **N/A** | Vault 運用は dotfiles のスコープ外。iCloud / Obsidian Sync 等が代替 |
| 7 | 複利効果 | **Already** | AutoEvolve 4 層ループ + session-learner + memory system で自動蓄積済み |

### Prior Art in This Repository

- `docs/research/2026-03-22-obsidian-agent-persistent-memory-analysis.md` — ほぼ同一コンセプトの別記事を分析済み。メモリ -> Vault 同期と自動ブリーフィングを計画、未実装
- `docs/plans/2026-02-28-obsidian-second-brain-design.md` — Vault 設計の初期プラン
- `docs/plans/2026-03-16-obsidian-knowledge-pipeline-design.md` — ナレッジパイプライン設計

## Integration Decisions

4 項目すべて選択:

1. **[Gap] 通話文字起こし -> Vault 自動パイプライン** — 新規設計
2. **[Partial] Obsidian MCP サーバー設定** — settings.json に追加
3. **[Partial] 自動ブリーフィング実装** — 前回プランの実装
4. **[Partial] メモリ -> Vault 同期スクリプト** — 前回プランの実装

## Plan

### Task 1: 通話文字起こし -> Vault 自動パイプライン (M)

**概要**: 通話文字起こしファイルが Google Drive に追加されたら、Claude が自動処理して Vault に構造化情報を書き戻す。

**成果物**:
- `scripts/runtime/process-transcript.sh` — Drive の文字起こしファイルを Claude で処理
- `/digest` スキルの拡張 — バッチモード対応 (ファイルパス引数で自動処理)

**設計**:
```
[Fathom/Otter] -> [Zapier/手動] -> Google Drive/transcripts/
                                         |
                              cron or fswatch で監視
                                         |
                              claude -p "process-transcript"
                                         |
                              Obsidian Vault に書き戻し:
                                - 01-Projects/{client}/call-notes/
                                - Action Tracker に追記
                                - Decision Log に追記
```

**依存**: Task 2 (Obsidian MCP) があると Vault 書き込みがスムーズだが、必須ではない (直接ファイル書き込みで代替可)

**注意**:
- Fathom/Otter のサブスクリプションが必要 (ユーザー判断)
- Google Drive MCP or マウント済み Drive フォルダが前提
- Vault パスは `OBSIDIAN_VAULT_PATH` 環境変数で設定

### Task 2: Obsidian MCP サーバー設定 (S)

**概要**: `obsidian-mcp` (npm パッケージ) を settings.json に追加し、任意のディレクトリから Vault を操作可能にする。

**成果物**: `settings.json` (user) に MCP サーバー設定追加

**設計**:
```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["-y", "obsidian-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/path/to/vault"
      }
    }
  }
}
```

**注意**:
- `obsidian-mcp` パッケージの存在と API を事前に確認する必要あり
- Vault パスはユーザー固有 — 環境変数 or settings.local.json で管理

### Task 3: 自動ブリーフィング実装 (S)

**概要**: cron + `claude -p` で毎朝ブリーフィングを自動生成し、Obsidian Daily Note + cmux notify に出力。

**成果物**: `scripts/runtime/auto-morning-briefing.sh`

**設計** (前回プラン 2026-03-22 を踏襲):
```bash
#!/bin/bash
# cron: 30 8 * * 1-5 (平日 8:30)
VAULT="${OBSIDIAN_VAULT_PATH:?}"
TODAY=$(date +%Y-%m-%d)
DAILY_NOTE="$VAULT/00-Inbox/$TODAY.md"

claude -p "
GitHub Issues, 進行中タスク, 直近のコミットを確認し、
今日のブリーフィングを生成してください。
フォーマット: ## Morning Briefing $TODAY
" --output-format text >> "$DAILY_NOTE"

cmux-notify.sh "Morning briefing ready"
```

**依存**: `OBSIDIAN_VAULT_PATH` 環境変数, `cmux-notify.sh` (既存)

### Task 4: メモリ -> Vault 同期スクリプト (S)

**概要**: Claude Code のメモリファイルを Obsidian Vault にミラーリング。

**成果物**: `scripts/runtime/sync-memory-to-vault.sh`

**設計** (前回プラン 2026-03-22 を踏襲):
```bash
#!/bin/bash
VAULT="${OBSIDIAN_VAULT_PATH:?}"
MEMORY_DIR="$HOME/.claude/projects"
TARGET="$VAULT/07-Agent-Memory"

mkdir -p "$TARGET"
# 全プロジェクトの memory/*.md を同期
find "$MEMORY_DIR" -path "*/memory/*.md" -exec rsync -u {} "$TARGET/" \;
```

**依存**: `OBSIDIAN_VAULT_PATH` 環境変数
**起動方法**: session-learner.py PostSession hook or cron (毎時)

## Execution Order

1. Task 2 (MCP設定) — 他の全タスクの基盤。S規模。
2. Task 4 (メモリ同期) — 独立して実装可能。S規模。
3. Task 3 (自動ブリーフィング) — 独立して実装可能。S規模。
4. Task 1 (文字起こしパイプライン) — 最も複雑。M規模。ユーザーの文字起こしツール選定が前提。

## Notes

- この記事は `2026-03-22-obsidian-agent-persistent-memory-analysis.md` とほぼ同一のコンセプト
- 新規の知見: Fathom + Zapier パイプラインの具体的な構成
- Claude Cowork (デスクトップアプリ) の言及は Claude Code CLI ユーザーには直接関係しない
- 「毎回 Vault を検索」の単一インストラクションは既に上位互換 (Progressive Disclosure) で実装済み
