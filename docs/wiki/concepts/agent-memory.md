---
title: エージェントメモリ
topics: [memory]
sources: [2026-04-02-cc-7-layer-memory-architecture-analysis.md, 2026-04-02-claude-code-memory-internals-analysis.md, 2026-03-30-agent-memory-quality-guide-analysis.md, 2026-03-30-ai-agent-memory-types-analysis.md]
updated: 2026-04-04
---

# エージェントメモリ

## 概要

エージェントメモリとは、有限なコンテキストウィンドウを持つ LLM が複数セッションにわたって知識・経験・手続きを蓄積・参照するための仕組みである。Claude Code は 7 層のメモリアーキテクチャを実装しており、安価な層（Tool Result Storage・Microcompaction）が高価な層（Full Compaction・Dreaming）の発動を防ぐ「Layered Defense, Cheapest First」原則で設計されている。メモリの質については「エージェントメモリの 84% は操作テレメトリ（ノイズ）である」という実践的知見があり、品質ゲート付きの構造化管理が不可欠である。

## 主要な知見

- **7 層防衛（Claude Code 内部）**: Tool Result Storage → Microcompaction（3 種）→ Session Memory → Full Compaction → Auto Memory Extraction → Dreaming → Cross-Agent Communication の順で段階的にコストが上がる
- **4 タイプのメモリ**: Short-term（作業デスク）/ Episodic（日記・失敗記録）/ Semantic（知識ベース）/ Procedural（筋肉記憶）の認知科学的分類が有効
- **Dreaming（クロスセッション統合）**: Orient→Gather→Consolidate→Prune の 4 フェーズで複数セッションの知識を統合。PID ロックと 10 分スロットルで安全性を担保
- **ハードキャップ**: MEMORY.md は 200 行 / 25KB、メモリファイルは 200 個、セッションあたり約 26K トークン（200K の 13%）をメモリが消費する構造的制約がある
- **サイレント失敗のリスク**: Sonnet の Semantic Recall は失敗時に `return []` を返し、`ensureMemoryDirExists` は EACCES/ENOSPC をサイレントに飲む。外部監視が必要
- **5 段階 Promotion Ladder**: draft → candidate → promoted → benchmark_grounded → realworld_validated の段階的昇格で品質を保証する
- **Doctrine Synthesis**: 3 つ以上のパケットが同タグを持つと meta-doctrine として自動合成。断片的知識を体系的原則に昇格させる
- **3 層品質ティア**: Operational(LOW) / Behavioral(MEDIUM) / Cognitive(HIGH)。HIGH ティアのみが意思決定に直接影響する
- **Prompt Cache Preservation**: byte-identical prefix の維持がキャッシュヒット（$0.003）とミス（$0.60）の 200 倍コスト差を生む。メモリ変更はキャッシュ破壊コストを意識する

## 実践的な適用

dotfiles のメモリシステムは Short-term を `context-compaction-policy.md` と `/check-context`、Episodic を `lessons-learned.md` + `decision-journal.md` + `/eureka`、Semantic を `MEMORY.md` + `references/` + Knowledge Pyramid（Tier 0〜3）、Procedural をスキル体系 + AutoEvolve + `improve-policy.md` で実装している。MEMORY.md はサマリ＋パス参照のみに保ち、26K トークン上限を意識した軽量構造を採っている。`memory-archive.py` が 500 行超でアーカイブする仕組みは内部ハードキャップ（200 行）の発覚により 180 行閾値への修正が実施済み。`staleness-detector.py` が 30 日未更新メモリファイルを検出し、鮮度管理を自動化している。

## 関連概念

- [context-management](context-management.md) — コンテキストウィンドウ管理と compaction 戦略
- [context-engineering](context-engineering.md) — コンテキスト構造設計とインクリメンタル更新
- [knowledge-pipeline](knowledge-pipeline.md) — 外部知見の取り込みと内部知識化フロー
- [trajectory-learning](trajectory-learning.md) — 実行軌跡からの知識抽出と昇格ロジック

## ソース

- [CC 7-Layer Memory Architecture Analysis](../../research/2026-04-02-cc-7-layer-memory-architecture-analysis.md) — Claude Code の 7 層メモリ設計と Dreaming・Circuit Breaker の実装詳細
- [Claude Code Memory Internals Analysis](../../research/2026-04-02-claude-code-memory-internals-analysis.md) — 22 ソースファイル分析。200 行キャップ・PID ロック・サイレント失敗等の構造的限界
- [Agent Memory Quality Guide Analysis](../../research/2026-03-30-agent-memory-quality-guide-analysis.md) — 84% ノイズ率・Research Packets・5 段階 Promotion Ladder・Doctrine Synthesis
- [AI Agent Memory Types Analysis](../../research/2026-03-30-ai-agent-memory-types-analysis.md) — Short-term/Episodic/Semantic/Procedural の 4 層モデルと dotfiles 対応表
