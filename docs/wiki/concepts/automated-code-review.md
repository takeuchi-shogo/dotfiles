---
title: 自動コードレビュー
topics: [coding, evaluation]
sources: [2026-03-26-findy-code-review-readability-analysis.md, 2026-03-26-harness-engineering-human-review-analysis.md, 2026-03-30-code-review-graph-analysis.md, 2026-04-01-spec-and-verify-analysis.md]
updated: 2026-04-04
---

# 自動コードレビュー

## 概要

自動コードレビューは、AI エージェントとハーネスを組み合わせて、コード品質・可読性・仕様準拠を自動検証するプロセスである。意思決定を伴わない品質チェックは人間のレビューが不要であり、AI に完全委譲できる。一方で「Spec & Verify」パラダイムへの移行により、人間は仕様レビューに集中し、コード検証はエージェントが担うという役割分担が生まれつつある。

## 主要な知見

- **コードレビュー指摘の 42.2% は可読性に関するもの**: Linter でカバーできるのは 30% 未満であり、AI レビューが補完すべき領域が明確に存在する
- **3 層可読性モデル**: Legibility（表記）/ Readability（構造）/ Understandability（意味・意図）の 3 層で体系化することで、レビューの観点を網羅できる
- **Atoms of Confusion**: 誤読の最小単位（15 パターン）を定義することで、AI レビューの検出精度を向上させられる
- **5 ステップレビューループ**: Review → Triage → Fix → Validate → Commit のサイクルを max 6 回繰り返し、ゼロ指摘を終了条件とする
- **オシレーション検出**: commit diff から A→B→A パターン（振り子修正）を検出し、directive pinning で固定することで収束を促す
- **Blast radius 分析によるトークン削減**: Tree-sitter AST で構造グラフを構築し、変更の影響範囲（blast radius）のみを読ませることで平均 8.2x のトークン削減を実現
- **Spec & Verify パラダイム**: コードではなく仕様をレビューし、実装検証はエージェントに委譲する。Dual Spec（Product Spec + Tech Spec）の分離が効果的
- **バンドエイド修正検出**: 別セッションでの検証フェーズで「根本原因修正 vs 一時しのぎ」を明示的に判定する
- **AI 可読性の限界**: 全体抽象化の失敗・論理表現の誤認識の 3 パターンは AI レビューが苦手な領域であり、人間による補完が必要

## 実践的な適用

dotfiles リポジトリでは `/review` スキルが Codex Review Gate（codex-reviewer + code-reviewer 並列）を自動起動する。`cross-file-reviewer` が Grep ベースの blast radius 分析を行い、`review-dimensions.md` が評価軸（maintainability 0.20 等）を定義している。`code-review-graph` MCP サーバーが構造グラフベースの影響分析（`get_impact_radius`）を提供し、Grep ベースでは見落とす間接依存（depth=2+）を補完する。`review-consensus-policy.md` §3.1 でコード振り子検出を定義している。

## 関連概念

- [quality-gates](quality-gates.md) — レビューを品質ゲートとして組み込む仕組み
- [agent-evaluation](agent-evaluation.md) — エージェント自身の出力評価の方法論
- [spec-driven-development](spec-driven-development.md) — Spec & Verify パラダイムの前提となる仕様駆動開発

## ソース

- [コードレビューに効く読みやすさの処方箋](../../research/2026-03-26-findy-code-review-readability-analysis.md) — 3 層可読性モデル・Linguistic Anti-patterns・Atoms of Confusion の学術的体系化
- [意思決定を伴わないレビューの AI 完全委譲](../../research/2026-03-26-harness-engineering-human-review-analysis.md) — 5 ステップループ・オシレーション検出・ハーネス 4 役割（Constrain/Inform/Verify/Correct）
- [code-review-graph](../../research/2026-03-30-code-review-graph-analysis.md) — Tree-sitter AST グラフによる blast radius 分析と 8.2x トークン削減
- [Spec & Verify: What comes after human code review](../../research/2026-04-01-spec-and-verify-analysis.md) — Dual Spec パラダイム・Behavior Verification・Self-improving verification loops
