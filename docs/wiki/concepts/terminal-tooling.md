---
title: ターミナルツーリング
topics: [tooling]
sources: [2026-03-22-cmux-ecosystem-claude-code-analysis.md, 2026-03-22-ghostty-sand-cmux-analysis.md, 2026-04-02-dual-audience-cli-analysis.md]
updated: 2026-04-04
---

# ターミナルツーリング

## 概要

AI コーディングエージェントの長時間セッションに耐えるターミナル環境の設計と、人間・エージェント双方が使いやすい CLI の実装原則。Ghostty + cmux の組み合わせがエージェント特化ターミナルのデファクトとなりつつあり、デュアルオーディエンス設計によって同一 CLI が人間には TUI、エージェントには構造化データを返す。

## 主要な知見

- **VSCode terminal の限界**: M4 Mac でも Claude Code の長時間セッションでクラッシュする。Ghostty はネイティブ GPU レンダリングで AI スケールの出力に耐える
- **cmux のリソース階層**: `window → workspace → pane → surface`。pane（レイアウト）と surface（中身）の分離が従来マルチプレクサとの決定的な違い
- **Conductor/Worker 分離**: workspace:1 を Conductor（操作側・広いペイン）、workspace:2+ を Worker（実行側）に割り当て、詰め込みによる `read-screen` 破損を防ぐ
- **デュアルオーディエンス設計**: `--json` フラグで同一コマンドが人間には色付き TUI、エージェントには JSON/NDJSON を返す。コンテキストウィンドウ保護が前提
- **決定的 exit code**: 0/1/2/3 の標準化。エージェントは exit code でエラー種別を判断する
- **SAND mnemonic**: Split/Across/Navigate/Destroy の 4 操作にキーバインドを集約し、パネル管理を習慣化
- **OSC 通知統合**: cmux の OSC 9/99/777 シグナルを hooks に接続し、Stop/Notification イベントを統一的に処理
- **Error Hint 行**: CLI のエラーメッセージに次のアクションを示す Hint 行を添えることで、エージェントの自律回復を助ける

## 実践的な適用

dotfiles では Ghostty + cmux + aerospace の3層構成。cmux を `workspace 4` に固定し AI coding terminal と役割明記。`/dispatch` スキルが cmux Worker を起動する際は `new-workspace → send → send-key enter → read-screen --scrollback → close-surface` のパターンを踏む。tmux はリモート SSH 専用に位置づけ直し、ローカルでの多重化は cmux に統一している。`cmux-notify.sh` が Stop/Notification hook で cmux notify + claude-hook notification を担う。

## 関連概念

- [claude-code-architecture](claude-code-architecture.md) — Claude Code の内部アーキテクチャとエージェント連携
- [workflow-optimization](workflow-optimization.md) — マルチエージェント並列実行とワークフロー最適化

## ソース

- [cmux エコシステム分析](../../research/2026-03-22-cmux-ecosystem-claude-code-analysis.md) — 5コンポーネントとワークスペース分離アーキテクチャ
- [Ghostty SAND / cmux 調査](../../research/2026-03-22-ghostty-sand-cmux-analysis.md) — SAND キーバインドと cmux 通知統合
- [デュアルオーディエンス CLI 分析](../../research/2026-04-02-dual-audience-cli-analysis.md) — 人間とエージェントの双方に対応する CLI 設計原則
