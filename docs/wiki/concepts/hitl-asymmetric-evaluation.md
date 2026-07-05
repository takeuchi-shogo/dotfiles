---
title: HITL非対称評価
topics: [evaluation]
sources: [2026-04-07-hitl-asymmetric-evaluation-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 5
confidence: established
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
- **Outcome over Trajectory原則**: HITL評価は経路（使ったツール数・retry回数）を罰さず、最終artifact・観測可能な成果のみで判定する。経路情報はobservability目的で記録に留める
- **Negative Signal Review Rule（AI沈黙=盲点シグナル）**: AIレビューがverdict=PASSかつ指摘ゼロを返した場合こそ、logic/security/API/harnessに関わる重要変更では人間が仕様書・ADRを念入りに見直すべきという逆説運用。「AIが見たから大丈夫」という認知のショートカットに対する防御
- **ADR検証欄によるHITL負荷の前倒し**: ADRのDecisionの後にAffected paths / Invariants / Verification commandの3フィールドを設けると、Architecture層（本来AI比率0%）の一部判断がLogic/Design層（AI比率60-90%）に降りてきて、機械照合可能な範囲が広がる
- **Teach-back型の理解検証ゲート**: 作業完了後にAI自身が教師役となり、restate-first→3階層理解→AskUserQuestionクイズの順で人間側の理解度を段階的に検証する。HITLを「計測ツール」だけでなく「人間の理解保証ツール」としても機能させる
- **判断力frontierの計測ギャップ**: AIの研究方針判断が人間の判断に迫りつつある（Mythos 51%→64%）状況下では、「委譲してよい判断」と「人間が保持すべき判断」の境界を定量的に計測する仕組みが必要になる。境界を暗黙のまま運用すると非対称損失が顕在化しにくい
- **生成と検証の自己改善の非対称リスク**: 生成側（実装の自動化）だけが自己改善を続け検証側（レビュー・HITLゲート）が固定されたままだと、未レビューのdriftが非対称に蓄積する。検証側も対称的に自己改善対象に含めるべき

## 実践的な適用

このリポジトリでは `workflow-guide.md` の「非対称損失の原則」セクションに High/Medium/Low の3段階リスクカテゴリを定義し、Review セクションの「リスクカテゴリ別レビュー方針」で具体的な reviewer 構成と判定基準を規定した。`completion-gate.py` と Review Gate がこの原則に基づいて動作する。`/review` スキルの Negative Signal Review Rule が verdict=PASS かつ指摘ゼロの場合に人間の追加確認を促し、`docs/adr/template.md` の Verification セクションが ADR↔実装整合の機械照合フィールドを提供する。`/teachback` コマンドがセッション作業の理解検証ゲートを担う。将来的には `meta-analyzer` でセッションデータからHITLパターンを統計分析し、レビュー指摘の accept/reject フィードバックループで精度を校正する計画がある。

## 関連概念

- [agent-evaluation](agent-evaluation.md) — Evals フレームワークとベンチマーク体系
- [quality-gates](quality-gates.md) — 多段検証ゲートの設計
- [automated-code-review](automated-code-review.md) — 自動コードレビューの Fβ 適用先

## ソース

- [HITL非対称評価分析](../../research/2026-04-07-hitl-asymmetric-evaluation-analysis.md) — 非対称損失・カテゴリ別Fβ・HITLパターン4分類の統合分析
- [The Self-Healing Agent Harness absorb分析](../../research/2026-04-29-self-healing-harness-absorb-analysis.md) — 自己修復ハーネス記事を分析、outcome-over-trajectory等3件採用
- [コードレビュー6段階とAI/人間の境界](../../research/2026-06-02-code-review-6-stages-ai-human-boundary-absorb-analysis.md) — コードレビュー6段階記事を分析、AI沈黙シグナルとADR検証欄の2件を実装採用
- [Suzanne teach-back prompt](../../research/2026-06-02-suzanne-teachback-absorb-analysis.md) — Suzanne teach-backを分析、軽量/teachbackコマンド採用
- [When AI builds itself (Anthropic Institute) recursive self-improvement](../../research/2026-06-05-recursive-self-improvement-anthropic-absorb-analysis.md) — Anthropic再帰的自己改善論考を分析、判断計測とメタ安全層3件を採用予定
