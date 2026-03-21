---
source: "My AI agent woke up blank every session. One config change fixed it permanently (shared article, no URL)"
date: 2026-03-22
status: analyzed
---

## Source Summary

### Main Claim
Obsidian を AI エージェントの永続メモリ＋自動化ハブとして統合し、セッション跨ぎのコンテキスト喪失を解消する。エージェントとナレッジベースは別ツールではなく統合インフラとして運用すべき。

### Techniques
1. 単一コンテキストファイル（user.md）を Vault root に配置 → 毎セッション自動読み込み
2. エージェントのメモリストレージ先を Obsidian Vault に直接変更
3. プラグイン（Data files editor, HTML plugin）でエージェント生成物を可視化
4. 24/7 アーキテクチャ: Mac Mini/VPS + Sync で常時稼働
5. Telegram/Discord ボットでモバイルコマンド
6. 自動ブリーフィング（朝/夕）＋習慣トラッキング
7. Smart Connections で知識グラフ自動構築
8. セキュリティ: サンドボックスモード、権限最小化、デフォルトスキル削除

### Rationale
- セッション毎にコンテキストを再説明するコストの排除
- 認知機能（記憶＋注意ルーティング）のオフロード
- エージェントを「鋭いジュニア社員」として位置づけ、ルーチンワークを委譲

### Prerequisites
- Obsidian を日常的に使っている
- 常時稼働マシンがある（24/7 の場合）
- エージェントの設定ファイルを直接編集できる

## Gap Analysis

| # | Technique | Status | Detail |
|---|-----------|--------|--------|
| 1 | Single context file (user.md) | **Already** | CLAUDE.md + MEMORY.md + memory/user_*.md で実装済み。Progressive Disclosure + conditional important tags でより高度 |
| 2 | Memory storage → Vault | **Partial** | Claude Code メモリは ~/.claude/ に書き込み。Vault とは別ディレクトリ。双方向同期なし |
| 3 | Plugin visualization | **Partial** | /obsidian-vault-setup に plugin-recommendations.md あり。Data files editor / HTML plugin の統合未実装 |
| 4 | 24/7 architecture | **Gap** | ローカル Mac 上の Claude Code セッションのみ。VPS/Mac Mini 常時稼働なし |
| 5 | Telegram/Discord mobile command | **Gap** | モバイルからのエージェント操作手段なし |
| 6 | Auto briefing (morning/evening) | **Partial** | /morning（手動）, /timekeeper（対話式）あり。自動配信なし |
| 7 | Knowledge graph (Smart Connections) | **Partial** | /obsidian-knowledge でリンク候補・MOC 生成可能。バックグラウンド自動構築ではない |
| 8 | Security (sandbox, minimal permissions) | **Already** | harness hooks, deny rules, gaming-detector 等で記事を大幅に超える水準 |

## Integration Decisions

- **Selected**: #2 メモリ → Vault 同期, #6 自動ブリーフィング配信
- **Skipped**: #4 24/7 (現時点で常時稼働マシン不要), #5 Telegram Bot (セキュリティリスク), #3 プラグイン可視化 (優先度低), #7 自動知識グラフ (手動で十分)

## Plan

### Task 1: メモリ → Vault 同期スクリプト (S)

Claude Code のメモリファイル（~/.claude/projects/*/memory/*.md）を Obsidian Vault の指定ディレクトリに同期するスクリプトを作成。

- **成果物**: `scripts/runtime/sync-memory-to-vault.sh`
- **仕組み**: rsync ベースで memory/*.md → Vault/07-Agent-Memory/ にコピー。frontmatter を Obsidian 互換に変換
- **起動**: session-learner.py の PostSession hook から呼び出し、またはcron で定期実行
- **注意**: 一方向同期（Claude → Vault）。Vault 側の編集は Claude メモリには反映しない（意図的）

### Task 2: 自動ブリーフィング配信 (S)

cron + `claude -p` で朝のブリーフィングを自動生成し、cmux notify + Obsidian Daily Note に書き込み。

- **成果物**: `scripts/runtime/auto-morning-briefing.sh`
- **仕組み**: cron で毎朝 8:30 に `claude -p "..." --output-format text` を実行。結果を Obsidian Daily Note にappend + cmux notify で通知
- **入力**: GitHub Issues, 進行中タスク, 前日の /timekeeper review
- **注意**: Vault パスは環境変数 `OBSIDIAN_VAULT_PATH` で設定。未設定時はスキップ
