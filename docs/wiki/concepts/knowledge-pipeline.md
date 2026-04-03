---
title: ナレッジパイプライン
topics: [memory, productivity]
sources: [2026-04-03-karpathy-llm-knowledge-bases-analysis.md, 2026-03-25-second-brain-thinking-partner-analysis.md, 2026-03-30-personal-ai-infrastructure-analysis.md]
updated: 2026-04-04
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

## 実践的な適用

dotfiles リポジトリでは `docs/research/` に 60+ 記事の分析レポートを蓄積しているが、横断的な wiki 構造化は手動だった。`/compile-wiki` スキルと `docs/wiki/concepts/` ディレクトリがこのギャップを埋める。MEMORY.md はポインタ索引として機能し、詳細は各メモリファイルへの参照で Progressive Disclosure を実現している。TELOS はすでに `docs/agent-memory/telos_*.md` として部分実装されており、PAI の設計思想と整合している。

## 関連概念

- [obsidian-integration](obsidian-integration.md) — Obsidian を IDE として wiki を閲覧・編集する統合層
- [agent-memory](agent-memory.md) — セッション横断でコンテキストを保持するメモリアーキテクチャ
- [context-engineering](context-engineering.md) — コンテキストウィンドウの効率的な利用設計

## ソース

- [Karpathy "LLM Knowledge Bases" 分析](../../research/2026-04-03-karpathy-llm-knowledge-bases-analysis.md) — 7ステップの個人 wiki パイプライン。RAG 不要の Q&A アーキテクチャ
- [第二の脳・思考パートナー分析](../../research/2026-03-25-second-brain-thinking-partner-analysis.md) — 思考プロトコルと永続的環境の設計原則
- [Personal AI Infrastructure 分析](../../research/2026-03-30-personal-ai-infrastructure-analysis.md) — PAI フレームワーク。TELOS・学習シグナル・Scaffolding > Model 原則
