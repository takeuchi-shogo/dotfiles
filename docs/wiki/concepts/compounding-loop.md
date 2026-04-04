# 複利ループ (Compounding Loop)

フィードバックループによりエージェントシステムの品質が時間とともに加速度的に改善するパターン。

## 概要

エージェントの出力結果を追跡し、成功/失敗パターンをシステムに還元することで、次回の出力品質を改善する。データの蓄積自体が競争優位の堀（moat）となる。

## 当セットアップでの実現

```
feature-tracker pass → learning 抽出 → learnings/*.jsonl
                                            ↓
/improve Phase 1 Step 3 → 成果追跡 → Phase 2 分析入力
                                            ↓
Phase 3 提案 → Phase 5 Outcome Validation → improve-history.jsonl
                                            ↓
次回 /improve → POSITIVE パターン優先 / NEGATIVE パターン回避
```

## 核心原理

1. **ループを閉じる**: 推奨→実行→結果の因果チェーンを必ず完結させる
2. **データ蓄積 = 堀**: 3ヶ月以上のデータ蓄積は後発者が追いつけない
3. **初期は苦痛**: Month 1-2 はシステム構築コストが成果を上回る。Month 3 からフライホイールが回る
4. **ループの質 > ツールの質**: 何を使うかより、学習ループが閉じているかが重要

## 関連

- [自己改善エージェント](self-improving-agents.md)
- [軌跡学習](trajectory-learning.md)
- [ワークフロー最適化](workflow-optimization.md)

## 出典

- Dorsey & Botha "From Hierarchy to Intelligence" (2026-04-01)
- Single Grain 実装体験記: 4ヶ月の複利効果の実証データ
