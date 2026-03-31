---
source: "What comes after human code review" (Warp CEO, 2026-04)
date: 2026-04-01
status: integrated
---

## Source Summary

### 主張
コードレビューはエージェント時代の最大ボトルネック。"Spec & Verify" パラダイムに移行すべき — コードではなく仕様をレビューし、検証はエージェントに任せる。

### 手法
1. **Dual Spec**: Product Spec（ユーザー行動ベース）+ Tech Spec（アーキテクチャレベル）をマークダウンで作成
2. **Spec チームレビュー**: NL ベースの仕様レビュー（コードレビューの代替）
3. **Agent 実装**: Spec が十分なら one-shot 可能
4. **Agent Code Review**: セキュリティ・スタイル・仕様準拠の自動検証
5. **Self-improving verification loops**: 人間フィードバック → プロンプト自動改善
6. **Behavior verification**: computer use, screenshot, integration test
7. **Production monitoring**: anomaly detection, fraud/abuse patterns

### 根拠
- Warp チームでレビューが #1 ボトルネック（書くより review cycle が遅い）
- エンタープライズ顧客でエージェントが人間より多くセキュリティ問題を検出
- 人間は大量コードを素早くレビューするため見落とすが、エージェントはデフォルトで thorough

### 前提条件
- エージェントが十分に高品質なコードを生成できる環境
- チームに spec 作成能力がある
- Intelligence infrastructure（Skills, specs の "trade memory"）が構築済み

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Dual Spec 分離（Product + Tech） | Partial | `/spec` は一体型 PRD。行動ベース Product Spec とアーキテクチャ Tech Spec が構造的に未分離 |
| 2 | Behavior Verification のワークフロー統合 | Partial | `webapp-testing` / `ui-observer` / Playwright MCP は存在するが `/review` ワークフローに未統合 |
| 3 | Production Monitoring エージェント | N/A | dotfiles リポジトリはインフラ設定。プロダクト開発時に別途検討 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点/機会 | 強化案 |
|---|-------------|-------------------|--------|
| A | Spec/Plan Gate (`codex-plan-reviewer`) | 記事は Spec レビューを人間の主要投資先と位置づけ。現状は機械レビューのみで人間向けハイライトなし | 出力に「Human Decision Points」セクション追加 |
| B | Agent Code Review (`/review` + Codex Review Gate) | Warp は個別レビューコメントへの人間フィードバック → Skill 自動改善。現状は session trace ベースで間接的 | comment-level feedback → `review-feedback.jsonl` → AutoEvolve 入力 |
| C | Self-improving loops (AutoEvolve 32 rules) | 記事は review 特化の改善ループ。AutoEvolve は汎用的だが個別コメントレベルのフィードバック弱い | improve-policy に `review-comments` カテゴリ追加 |
| D | Intelligence infrastructure (Skills + refs + memory) | "trade memory" と同等。現セットアップの方がはるかに洗練 | 強化不要 |

## Integration Decisions

全項目を取り込み:
1. [Partial] Dual Spec → `/spec` SKILL.md に Product/Tech Spec セクション追加
2. [Partial] Behavior Verification → `/review` に UI 変更時の behavior check 推奨追加
3. [強化] Review Comment Feedback Loop → `/review` Step 7 + improve-policy 新カテゴリ
4. [強化] Human Decision Points → `codex-plan-reviewer` 出力フォーマット拡張
- [N/A] Production Monitoring → dotfiles 対象外、スキップ

## Plan

| # | タスク | 対象ファイル | 規模 |
|---|--------|-------------|------|
| 1 | `/spec` に Dual Spec 構造追加 | `skills/spec/SKILL.md` | S |
| 2 | `/review` に Behavior Verification 推奨追加 | `skills/review/SKILL.md` | S |
| 3 | Review Comment Feedback Loop | `skills/review/SKILL.md` + `references/improve-policy.md` | S |
| 4 | Human Decision Points | `agents/codex-plan-reviewer.md` | S |
