---
title: 仕様駆動開発
topics: [coding]
sources: [2026-03-18-spec-is-code-analysis.md, 2026-04-01-spec-and-verify-analysis.md, 2026-03-20-comprehension-debt-analysis.md, 2026-04-02-how-to-vibe-code-analysis.md, 2026-04-04-pocock-5-agent-skills-analysis.md]
updated: 2026-04-04
---

# 仕様駆動開発

## 概要

仕様駆動開発（Spec-Driven Development）は、AI エージェントへの実装委譲前に仕様書を人間がレビューし、コードではなく意図・制約・受け入れ基準を合意するアプローチである。「仕様書は労力節約ツールではなく思考整理ツール」という認識が重要であり、精密すぎる仕様はコードに収束するという逆説（Borges の地図問題）を踏まえた適切な粒度管理が求められる。AI 支援開発で生じる「Comprehension Debt（理解の負債）」を予防する主要な手段でもある。

## 主要な知見

- **精度天井の認識**: 仕様書に擬似コード・DB スキーマ・条件分岐の網羅的記述が入ったら、コードを直接書くべきサイン。仕様書とコードが 1:1 対応になる限界点（Borges の地図問題）を意識する
- **Spec slop の回避**: AI 生成の仕様書は「形式は整っているが中身が空虚」になりやすい。急いだ仕様書は slop になるため、/spec と /interview を使って質を担保する
- **Dual Spec 分離**: Product Spec（ユーザー行動ベース）+ Tech Spec（アーキテクチャレベル）を分離することで、チームレビューとエージェント実装の役割分担が明確になる
- **Comprehension Debt（理解の負債）**: AI 生成コードが増える速度が人間の理解速度を上回ることで生じる「存在するが誰も理解していないコード」の蓄積。Anthropic の研究では AI 利用者が非利用者比で 17% 低い理解度を示した
- **速度の非対称性**: AI の生成速度 >> 人間の評価速度。この非対称性を意識せずに進めるとレビューの表面的な確認が常態化する
- **仕様レビューゲート**: M・L 規模の変更では実装前に仕様レビューを必須とすることで、理解の負債発生を構造的に防ぐ
- **Intent / Constraints / Acceptance criteria の 3 柱**: 有効な仕様書の最小構成要素。この 3 つが揃えば one-shot 実装が可能になる
- **不確実なときはプロトタイプ先行**: 仕様が曖昧な場合は仕様書を精密化しようとするより `/spike` でプロトタイプを作り、発見した知識を仕様に落とし込む
- **垂直スライス分解（Tracer Bullet）**: PRD を水平スライス（API層だけ、DB層だけ）ではなく全レイヤーを貫く薄い垂直スライスに分解する。unknown unknowns を早期に炙り出し、blocking 関係を明示することで並列エージェント実行を可能にする

## 実践的な適用

dotfiles リポジトリでは `/spec` スキルが Prompt-as-PRD を生成し、`/interview` が仕様のための深いインタビューを実施する。`/prd-to-issues` が PRD を垂直スライスの独立 Issue 群に分解し、`/autonomous` や `/rpi` による並列実行の起点となる。`overconfidence-prevention.md` が仕様なし実装への抑制ガイドラインを定義している。EPD ワークフロー（`/spec` → `/spike` → `/validate` → `/epd`）が不確実性の高いタスクの標準プロセスとなっており、`Codex Spec/Plan Gate`（M 規模以上必須）が仕様書を人間に代わって機械的にレビューする。

## 関連概念

- [automated-code-review](automated-code-review.md) — 仕様に基づいた実装検証を自動化するパターン
- [quality-gates](quality-gates.md) — 仕様レビューを品質ゲートに組み込む仕組み
- [workflow-optimization](workflow-optimization.md) — 仕様駆動を含む開発ワークフロー全体の最適化

## ソース

- [A Sufficiently Detailed Spec Is Code](../../research/2026-03-18-spec-is-code-analysis.md) — 仕様書の精度天井・Borges の地図問題・Spec slop の概念と精度管理ガイドライン
- [Spec & Verify: What comes after human code review](../../research/2026-04-01-spec-and-verify-analysis.md) — Dual Spec パラダイム・仕様チームレビューへの移行・Self-improving verification loops
- [Comprehension Debt](../../research/2026-03-20-comprehension-debt-analysis.md) — AI 生成コードによる理解の負債の定量化と仕様レビューゲートによる予防策
- [How to Vibe Code: A Developer's Playbook](../../research/2026-04-02-how-to-vibe-code-analysis.md) — Spec before prompt の 3 柱・Context engineering・Plan→Execute→Verify ループの実践ガイド
- [5 Agent Skills I Use Every Day](../../research/2026-04-04-pocock-5-agent-skills-analysis.md) — PRD→垂直スライス Issue 分解（Tracer Bullet）・Deep Modules によるエージェントフレンドリーなコードベース改善
