---
title: ナレッジパイプライン
topics: [memory, productivity]
sources: [2026-04-03-karpathy-llm-knowledge-bases-analysis.md, 2026-04-05-karpathy-llm-wiki-gist-analysis.md, 2026-03-25-second-brain-thinking-partner-analysis.md, 2026-03-30-personal-ai-infrastructure-analysis.md]
updated: 2026-04-05
---

# ナレッジパイプライン

## 概要

LLM を使って個人の知識を収集・構造化・再利用するパイプライン設計。raw データの取り込みからインクリメンタルな wiki コンパイル、フィードバックによる知識強化まで一連のループとして捉える。単なる情報保存ではなく、セッション横断で思考を支援する「生きたシステム」として機能させることが目標。

## 主要な知見

- **Karpathy の 7ステップモデル**: Ingest → Wiki Compile → Auto Index → Wiki Linting → Output Filing → CLI Tools → Obsidian IDE。RAG なしで ~400K words の Q&A が機能する
- **情報保存 ≠ 思考実行**: 第二の脳の大半はファイリングキャビネットに過ぎず、真の思考支援には「今何が不確実か」を記録するコンテキストドキュメントが必要
- **思考プロトコルの明示化**: 自分の考えを先に述べる → 最強の反論を求める → 「何が見えていないか」で締める、の3段階
- **TELOS による深い目標理解**: MISSION/GOALS/BELIEFS/MODELS/STRATEGIES など 10 のアイデンティティファイルで個人の目標体系を構造化
- **学習シグナルの継続収集**: インタラクション毎に rating/sentiment/outcome を記録し、hot/warm/cold の3層で管理
- **セッション開始プロンプト**: CONTEXT → SESSION GOAL → MY CURRENT THINKING → WHAT I NEED FROM YOU の構造で stranger 問題を解消
- **インクリメンタル wiki コンパイル**: バッチ処理ではなくレポート追加のたびに差分更新し、横断的サマリ・バックリンク・概念記事を自動生成
- **コンテキスト圧縮閾値**: 83% で自動トリガーするなど、コンテキストウィンドウを管理する機構が不可欠
- **3層アーキテクチャ**: Raw Sources（不変）→ Wiki（LLM が保守）→ Schema（CLAUDE.md 等の運用規約）。Karpathy の "LLM Wiki" Gist で明確化
- **Query 操作の形式化**: INDEX → 関連ページドリルダウン → 合成回答 → 回答の wiki 再投入。Q&A 結果も知識資産として蓄積
- **log.md による操作追跡**: 時系列の操作ログ（ingest/compile/query/lint）で wiki の進化履歴を可視化

## 実践的な適用

dotfiles リポジトリでは Karpathy の3層を完全に実装済み: `docs/research/` = Raw Sources、`docs/wiki/` = Wiki（149レポート、26概念、12トピック）、`CLAUDE.md` + `references/` = Schema。`/absorb` → `/compile-wiki` パイプラインが Ingest を、`/compile-wiki query` が Query を、`/compile-wiki lint` が Lint をそれぞれ担当。`docs/wiki/log.md` で操作履歴を時系列追跡し、wiki の進化を可視化する。

## 関連概念

- [obsidian-integration](obsidian-integration.md) — Obsidian を IDE として wiki を閲覧・編集する統合層
- [agent-memory](agent-memory.md) — セッション横断でコンテキストを保持するメモリアーキテクチャ
- [context-engineering](context-engineering.md) — コンテキストウィンドウの効率的な利用設計

## ソース

- [Karpathy "LLM Knowledge Bases" 分析](../../research/2026-04-03-karpathy-llm-knowledge-bases-analysis.md) — 7ステップの個人 wiki パイプライン。RAG 不要の Q&A アーキテクチャ
- [Karpathy "LLM Wiki" Gist 分析](../../research/2026-04-05-karpathy-llm-wiki-gist-analysis.md) — 3層アーキテクチャ・Query操作・log.md の形式化
- [第二の脳・思考パートナー分析](../../research/2026-03-25-second-brain-thinking-partner-analysis.md) — 思考プロトコルと永続的環境の設計原則
- [Personal AI Infrastructure 分析](../../research/2026-03-30-personal-ai-infrastructure-analysis.md) — PAI フレームワーク。TELOS・学習シグナル・Scaffolding > Model 原則
