---
title: Obsidian統合
topics: [tooling, memory]
sources: [2026-03-22-obsidian-agent-persistent-memory-analysis.md, 2026-03-23-claude-obsidian-ai-employee-analysis.md, 2026-03-16-notebooklm-obsidian-claude-integration.md]
updated: 2026-04-04
---

# Obsidian統合

## 概要

ObsidianはMarkdownベースのナレッジベースツールで、AIエージェントの永続メモリ基盤として活用できる。MCP経由でClaude CodeにVaultへの直接読み書きアクセスを付与することで、セッション跨ぎのコンテキスト喪失を解消し「記憶を持つAIエージェント」を実現する。dotfilesはすでにCLAUDE.md + MEMORY.md + Progressive Disclosureによる高度なメモリ構造を持ち、Obsidian統合はその可視化・同期・複利成長レイヤーとして機能する。

## 主要な知見

- **単一コンテキストファイル原則** — `user.md`をVault rootに配置し毎セッション自動読み込みする設計は、dotfilesのCLAUDE.md + MEMORY.mdパターンと等価
- **自動メモリループ** — 通話文字起こし（Fathom）→ Zapier → Vault書き戻しで複利的コンテキスト充実。手動`/digest`との対比
- **Obsidian MCPサーバー** — NodeパッケージでClaude CodeにVault直接読み書きを付与。`settings.json`への`obsidian-mcp`設定が統合点
- **Smart Connections** — バックリンクと埋め込みから知識グラフを自動構築。手動MOC生成との補完関係
- **NotebookLM APIなし問題** — Consumer版は非公開API。自動化はGemini API / Claude Codeで代替が現実的
- **ハイブリッドノートシステム** — 5ノートシステム（IPARAG + Zettelkasten）の各要素が制御するオブジェクトは異なる
- **複利効果** — 毎セッションVaultが成長 → AIコンテキストが自動充実。AutoEvolve 4層ループと同じ設計原則
- **セキュリティ原則** — サンドボックスモード・権限最小化・デフォルトスキル削除。dotfilesのhooks/deny rulesと対応

## 実践的な適用

dotfilesでの現状と計画：

| 機能 | 現状 | 方針 |
|------|------|------|
| 単一コンテキストファイル | CLAUDE.md + MEMORY.md（Already） | 強化不要 |
| メモリ→Vault同期 | 片方向のみ（Partial） | 双方向同期を計画 |
| Obsidian MCPサーバー | settings.jsonに未設定（Partial） | `obsidian-mcp`追加を計画 |
| 自動ブリーフィング | `/morning`手動のみ（Partial） | 自動配信を計画 |
| 知識グラフ | `/obsidian-knowledge`で手動生成 | バックグラウンド自動化は将来 |
| 24/7アーキテクチャ | ローカルセッションのみ（Gap） | 常時稼働マシン不要のため保留 |

`docs/plans/2026-03-16-obsidian-knowledge-pipeline-design.md`でナレッジパイプライン設計が進行中。`/obsidian-vault-setup`スキルによりZettelkasten + PARAハイブリッド構成を整備済み。

## 関連概念

- [エージェントメモリ](agent-memory.md) — 3層メモリスコープ（user/project/local）との対応
- [ナレッジパイプライン](knowledge-pipeline.md) — 外部情報のVault取り込みフロー
- [コンテキストエンジニアリング](context-engineering.md) — Progressive Disclosureとの統合点

## ソース

- [Obsidianエージェント永続メモリ](../../research/2026-03-22-obsidian-agent-persistent-memory-analysis.md) — セッション跨ぎコンテキスト保持の手法とGap分析
- [Claude + Obsidian = AI従業員](../../research/2026-03-23-claude-obsidian-ai-employee-analysis.md) — 構造化ナレッジベースと自動メモリループの設計パターン
- [NotebookLM + Obsidian + Claude統合調査](../../research/2026-03-16-notebooklm-obsidian-claude-integration.md) — ツール選択の現実解とハイブリッドノートシステムの原則
