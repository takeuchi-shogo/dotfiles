---
source: https://zenn.dev/ubie_dev/articles/claude-code-tips-findy-2026
date: 2026-03-19
status: integrated
---

# Claude Code を加速させる推しスキル・ツール・設定 — 分析レポート

## Source Summary

鹿野壮（Ubie）による Findy イベント登壇資料。16 の実務 Tips を紹介:
Raycast 連携、CleanShot X、upload-image-to-pr、statusline、複数クローン並行開発、
ghq+peco、nano-banana-2-skill、feature-dev プラグイン、/btw /fork /rewind、
Claude Code Remote Control、ni パッケージマネージャー統一、skillsmp.com、
RSS → Gemini → Obsidian パイプライン。

**主張**: ツール連携とワークフロー最適化で Claude Code の生産性を劇的に向上させる。
**前提条件**: macOS + Raycast 環境。GitHub PR ベースの開発フロー。

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Raycast ホットキー/スニペット | N/A | dotfiles スコープ外 |
| 2 | `claude 依頼内容` 即時実行 | Already | 基本機能 |
| 3 | CleanShot X | N/A | 外部ツール |
| 4 | upload-image-to-pr | **Gap** | Playwright MCP でPR画像埋め込み |
| 5 | statusline | Already | context-monitor.py |
| 6 | 複数クローン並行開発 | Already | worktree 対応済み |
| 7 | ghq + peco | Already | `^g` で ghq-fzf 導入済み |
| 8 | nano-banana-2-skill | **Gap** | 画像生成 CLI。Gemini 3.1 Flash ベース |
| 9 | feature-dev プラグイン | **Partial** | EPD 類似。「質問フェーズ」明示なし |
| 10 | /btw, /fork, /rewind | Already | 組み込み機能 |
| 11 | Remote Control | N/A | 運用Tips |
| 12 | ni | **Gap** | パッケージマネージャー自動判別 |
| 13 | skillsmp.com | **Gap** | スキルマーケットプレイス |
| 14 | RSS → Gemini → Obsidian | **Gap** | 情報追跡自動化 |

## Integration Decisions

全 6 Gap/Partial 項目を統合対象とする:

1. **nano-banana-2-skill** — 画像生成 CLI 導入 + スキルラッパー
2. **upload-image-to-pr** — PR画像埋め込みスキル新規作成
3. **ni** — パッケージマネージャー統一ツール導入
4. **feature-dev 質問フェーズ** — EPD/rpi に明示的クラリフィケーションステップ追加
5. **skillsmp.com** — 参照メモリ追加
6. **RSS → Gemini → Obsidian** — 情報追跡パイプラインスキル作成

## Plan

`docs/plans/2026-03-19-findy-tips-integration-plan.md` に詳細プランを記載。
