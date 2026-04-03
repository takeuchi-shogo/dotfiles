---
title: スキル設計
topics: [skill]
sources: [2026-03-18-skill-lessons-analysis.md, 2026-03-24-claude-skills-2.0-article-analysis.md, 2026-03-30-cc-skills-golang-analysis.md, 2026-04-02-master-claude-skills-module2-analysis.md]
updated: 2026-04-04
---

# スキル設計

## 概要

スキルは Claude Code に対して再利用可能な知識・手順・ワークフローをパッケージ化する仕組みである。SKILL.md の metadata 精度がトリガー精度を決定し、Progressive Disclosure（段階的開示）でトークン効率を最適化する。設計の核心は「Claude がすでに知っていることは書かない」という原則にあり、スキル固有のコンテキスト（Gotchas・境界定義・スクリプト）のみを提供する。

## 主要な知見

- **9カテゴリのスキル分類**: Library & API Reference / Product Verification / Data Fetching / Business Process Automation / Code Scaffolding / Code Quality & Review / CI/CD / Runbooks / Infrastructure Operations の9種が実用的な分類軸となる
- **Gotchas セクションが最高価値**: スキル内で最も ROI が高いのは「落とし穴・例外・注意点」のセクション。一般知識ではなく、ドメイン固有の暗黙知を書く
- **description フィールドはトリガー条件を記述する**: 要約ではなく「どのような状況でこのスキルを使うべきか」を書く。`Triggers:` と `Do NOT use for:` の両方を定義して境界を明確にする
- **Lazy-loaded アーキテクチャ**: description（~100トークン）で常時ロード、SKILL.md（~2.5K トークン）はオンデマンドロード、reference/ で深掘りという3層構造が最適
- **On Demand Hooks**: スキルが active なときのみ有効なフックを定義し、通常実行への副作用を排除する
- **評価駆動の品質管理**: アサーションベースの自動評価（eval-driven）でスキルの効果を定量測定する。cc-skills-golang では 54% → 98%（+44pp）の改善を計測
- **スクリプト委譲**: 計算・ファイル処理・外部連携はスキルから分離したスクリプトに委譲し、SKILL.md は推論の指針に集中させる
- **テリトリー衝突検出**: 複数スキル間でトリガー言語が重複する場合、`/skill-audit conflict-scan` で完全一致・部分包含・排他欠落の3種の衝突を自動検出する
- **Overridable design**: プロジェクト固有のスキルが `supersedes` 宣言によって汎用スキルを上書きできるよう設計する

## 実践的な適用

dotfiles リポジトリでは 60+ スキルを `.config/claude/skills/` 以下に管理している。`skill-writing-guide.md` と `skill-writing-principles.md` がスキル作成の規範を定義し、`description-optimization.md` が eval 駆動のトリガー最適化ループを定義している。`/skill-audit` コマンドで全スキルの横断監査（Trigger conflict scan 含む）を実行でき、`skill-suggest.py` フックが実行時にスキルの推薦を行う。skills.sh 経由で 16 の外部スキルもインストール済みである。

## 関連概念

- [skill-chaining](skill-chaining.md) — スキルを連鎖させてより複雑なワークフローを構成するパターン
- [claude-code-architecture](claude-code-architecture.md) — スキルが組み込まれる Claude Code 全体のアーキテクチャ
- [context-engineering](context-engineering.md) — Progressive Disclosure とトークン効率最適化の基盤理論

## ソース

- [Lessons from Building Claude Code: How We Use Skills](../../research/2026-03-18-skill-lessons-analysis.md) — Anthropic 公式の 9 カテゴリ分類と 9 ベストプラクティス。Gotchas・On Demand Hooks・description 最適化を解説
- [How to Build Claude Skills 2.0](../../research/2026-03-24-claude-skills-2.0-article-analysis.md) — Progressive Disclosure・500行上限・負の境界定義のベストプラクティスと dotfiles への適用ギャップ分析
- [cc-skills-golang](../../research/2026-03-30-cc-skills-golang-analysis.md) — Go 開発向けスキル設計。Lazy-loaded atomic skills・eval-driven quality・Ultrathink auto-trigger のパターン
- [Master Claude Skills Module 2](../../research/2026-04-02-master-claude-skills-module2-analysis.md) — scripts/ レイヤー分離・マルチスキルオーケストレーション・リファレンス最適化のアーキテクチャガイド
