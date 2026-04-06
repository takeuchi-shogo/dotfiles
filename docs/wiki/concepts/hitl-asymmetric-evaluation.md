---
title: HITL非対称評価
topics: [evaluation]
sources: [2026-04-07-hitl-asymmetric-evaluation-analysis.md]
updated: 2026-04-07
---

# HITL非対称評価

## 概要

Human-in-the-Loop (HITL) 評価において、見逃し（false negative）と過検出（false positive）のコストは対称ではない。見逃しは指数的損害（本番DB破壊、セキュリティ侵害）を招き、過検出は線形コスト（不要な確認の人件費）に留まる。この非対称性を明示的にモデル化し、リスクカテゴリに応じてゲートの厳格度を調整することで、HITLを「計測ツール」から「意思決定ツール」に昇華させる。

## 主要な知見

- **非対称損失関数**: L(Δ) = α·|Δ|^γ（下振れ）vs β·|Δ|（上振れ）。α > β, γ > 1 で見逃しに指数ペナルティ
- **カテゴリ別 Fβ スコア**: 高リスク（セキュリティ等）は β≥3 で Recall 最大化、低リスク（ドキュメント等）は β=1 でバランス
- **HITL発生パターン4分類**: 集中型（Gini>0.6）、分散型（CV<1）、フロントローディング型（FLI>0.7）、ランダムバースト型（B>0.3, CV>1）
- **HITL間の相互作用**: 依存型カスケード（上流→下流波及）、競合型干渉（短時間複数HITL→判断疲労）、補完型シナジー（同一担当者の文脈理解効果）
- **タイミング非対称性**: 遅延は指数ペナルティ c_late·|Δt|^δ。早すぎる介入は線形コスト

## 実践的な適用

このリポジトリでは `workflow-guide.md` の「非対称損失の原則」セクションに High/Medium/Low の3段階リスクカテゴリを定義し、Review セクションの「リスクカテゴリ別レビュー方針」で具体的な reviewer 構成と判定基準を規定した。`completion-gate.py` と Review Gate がこの原則に基づいて動作する。将来的には `meta-analyzer` でセッションデータからHITLパターンを統計分析し、レビュー指摘の accept/reject フィードバックループで精度を校正する計画がある。

## 関連概念

- [agent-evaluation](agent-evaluation.md) — Evals フレームワークとベンチマーク体系
- [quality-gates](quality-gates.md) — 多段検証ゲートの設計
- [automated-code-review](automated-code-review.md) — 自動コードレビューの Fβ 適用先

## ソース

- [HITL非対称評価分析](../../research/2026-04-07-hitl-asymmetric-evaluation-analysis.md) — 非対称損失・カテゴリ別Fβ・HITLパターン4分類の統合分析
