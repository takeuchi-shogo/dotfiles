---
title: 長時間自律エージェント
topics: [harness, agent]
sources: [2026-03-25-long-running-claude-scientific-computing-analysis.md, 2026-03-30-openforage-long-running-agents-analysis.md, 2026-03-25-harness-design-long-running-apps-analysis.md, 2026-04-06-agent-harness-anatomy-analysis.md]
updated: 2026-04-06
---

# 長時間自律エージェント

## 概要

長時間自律エージェントとは、数時間〜数日間にわたって人間介入なしに複雑なタスクを遂行するAIエージェントのパターンを指す。単一セッションを超えた作業継続を可能にするため、Living Documentation・失敗履歴・テストオラクル・Git連携の4本柱が基盤として機能する。長期タスクの失敗原因は「怠惰（corner-cutting）」と「混乱（stupidity）」の2種類に集約され、それぞれに構造的な対策が存在する。ハーネス設計の質がモデル選択より最終品質に大きく影響する。

## 主要な知見

- **CLAUDE.md as Living Documentation**: エージェントが作業中に自身の指示を編集・更新し、状態を維持する
- **CHANGELOG.md（ラボノート）**: 失敗アプローチと理由を記録し、セッション跨ぎのdead-end再試行を防止する
- **Ralph Loop**: 成功基準文字列（"DONE"）とmax-iterationsで「怠惰な停止」を検出・防止する制御構造
- **Generator-Evaluator分離**: 生成と評価を別エージェントに委譲し（GANインスパイア）、self-evaluation biasを軽減する
- **Context Reset vs Compaction**: モデルによりContext Anxiety感受性が異なり、長時間タスクでの戦略選択が品質に影響する
- **N個プラン生成 → 別エージェント選択**: 保守性・クリーンコード基準で別エージェントが最良プランを選択する
- **Pre-Task矛盾チェック**: 着手前に不完全・矛盾情報を体系的に検出し伝播を防止する
- **早期・頻繁な計画逸脱検証**: Lタスクで3ステップ完了ごとに計画突合を行い、カスケード障害（A→A'問題）を防ぐ
- **テストオラクル**: リファレンス実装との定量比較で進捗を測定し、明確な成功基準を設定する
- **blast radiusクリーンアップ**: セッション後にfresh contextエージェントで矛盾解消・デッドコード除去・ドキュメント同期を実施する

## 実践的な適用

このリポジトリでは`completion-gate.py`がRalph Loopの役割を担い、`HANDOFF.md`テンプレートとセッション間の状態引き継ぎを実現している。`/autonomous`スキルが長時間タスクのオーケストレーションを担当し、`/checkpoint`でセッション状態を永続化する。`plan-lifecycle.py`と`golden-check.py`が計画逸脱の早期検知に使われ、`pre-compact-save.js`がコンテキスト圧縮時の状態保全を担う。`workflow-guide.md`にはLタスクの中間検証ポイントが明記されている。

## 関連概念

- [harness-engineering](harness-engineering.md) — エージェントハーネスの設計原則と実装パターン
- [quality-gates](quality-gates.md) — 品質を保証するゲート機構の設計
- [context-management](context-management.md) — セッション跨ぎのコンテキスト管理戦略

## ソース

- [Long-Running Claude for Scientific Computing](../../research/2026-03-25-long-running-claude-scientific-computing-analysis.md) — CLAUDE.md・CHANGELOG・テストオラクル・Git・Ralph Loopの4本柱を科学計算事例で実証
- [OpenForage: Long-Running Autonomous Agents](../../research/2026-03-30-openforage-long-running-agents-analysis.md) — 7つの失敗パターンと3つの構造的対策、独立オーケストレーション層の必要性
- [Harness Design for Long-Running Apps](../../research/2026-03-25-harness-design-long-running-apps-analysis.md) — Generator-Evaluator分離・コンテキスト管理・主観的品質評価の12手法を3ケーススタディで実証
- [Agent Harness Anatomy Analysis](../../research/2026-04-06-agent-harness-anatomy-analysis.md) — harness simplification audit と12コンポーネント体系化。長時間タスクのハーネス設計を構造化する7アーキテクチャ決定
