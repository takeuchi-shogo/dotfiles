---
status: reference
last_reviewed: 2026-04-23
---

# Extreme Co-Design Cycle

> NVIDIA "Open Data for AI" の Extreme Co-Design パターンを、
> スキル・エージェント・リファレンスの公開・改善ワークフローに適用する。

## 原則

すべてのコンポーネントを**セットで**設計・公開・改善する。
単体で公開しても、使い方・評価方法がなければ価値が半減する。

## 3点セット

| 要素 | NVIDIA の例 | 本ハーネスでの対応 |
|------|------------|-------------------|
| **Data** | データセット | スキル定義 + references/ |
| **Method** | 学習レシピ + コード | agents/ + scripts/ |
| **Eval** | ベンチマーク + 評価基準 | benchmark-dimensions.md + eval/ |

## サイクル

```
1. Release  → スキル/エージェント/リファレンスをセットで追加
2. Stress   → 実セッションで使用、edge case を発見
3. Extend   → 新ドメイン・新プロジェクトへ適用
4. Feedback → learnings/*.jsonl + review-feedback でデータ収集
5. Improve  → /improve サイクルで反復改善
```

## 適用チェックリスト

新しいスキルやエージェントを追加するとき:

- [ ] **Data**: スキル定義 (`SKILL.md`) + 必要な references/ が揃っているか
- [ ] **Method**: 実行エージェント or コマンドが定義されているか
- [ ] **Eval**: `skill-executions.jsonl` でスコアが計測されるか、評価基準があるか
- [ ] **Feedback loop**: セッション学習でデータが蓄積される経路があるか

## アンチパターン

| NG | 理由 |
|----|------|
| スキルだけ作って評価基準なし | 品質劣化に気づけない |
| エージェントだけ作って references なし | 判断基準が暗黙知のまま |
| 評価だけ作ってフィードバックループなし | 改善が手動のまま |
