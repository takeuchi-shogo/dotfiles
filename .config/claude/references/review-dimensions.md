# レビュー次元定義

> code-reviewer / codex-reviewer が出力する Review Scores の5次元を定義する。
> autoevolve-core Phase 1 Analyze がスコアの時系列分析に使用する。

## 次元

| 次元 | 説明 | 重み | 評価基準 |
|------|------|------|----------|
| correctness | ロジックの正しさ、バグの有無 | 0.30 | 5: バグなし / 4: 軽微な改善余地 / 3: ロジック懸念あり / 2: バグの可能性 / 1: 明確なバグ |
| security | セキュリティ脆弱性、入力検証 | 0.25 | 5: 脆弱性なし / 4: 軽微なリスク / 3: 要検討 / 2: 脆弱性あり / 1: 重大な脆弱性 |
| maintainability | 可読性、テスタビリティ、複雑度 | 0.20 | 5: 優れた構造 / 4: 良好 / 3: 改善余地あり / 2: 理解困難 / 1: 保守不能 |
| performance | 不要な計算、N+1、メモリリーク | 0.15 | 5: 最適 / 4: 問題なし / 3: 軽微な非効率 / 2: パフォーマンス問題 / 1: 重大なボトルネック |
| consistency | 既存コードベースとの一貫性 | 0.10 | 5: 完全に一貫 / 4: ほぼ一貫 / 3: 部分的に逸脱 / 2: 一貫性低い / 1: 全く異なるスタイル |

## 加重平均スコア

```
weighted_score = Σ(dimension_score × weight) / Σ(weight)
```

N/A の次元は計算から除外し、残りの重みで再正規化する。

## AutoEvolve での使用

- Phase 1 Analyze の Normalizer が `review-feedback.jsonl` から次元スコアを集計
- Pattern Analyst が継続的に弱い次元を特定
- Phase 2 Improve が弱い次元に集中した改善提案を生成
- weakest 次元が 3 セッション連続で同じ場合、優先改善対象としてフラグ
