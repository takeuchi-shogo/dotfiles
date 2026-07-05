---
title: 複利ループ
topics: [agent, harness]
sources: [2026-04-08-asi-evolve-autoevolve-integration-analysis.md, 2026-04-08-coral-autonomous-multi-agent-evolution-analysis.md, 2026-04-08-environment-driven-rl-analysis.md, 2026-04-09-great-convergence-analysis.md, 2026-04-19-autogenesis-absorb-analysis.md, 2026-04-29-yamadashy-routines-perf-tuning-absorb-analysis.md, 2026-06-02-hermes-60-days-6-lessons-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 9
confidence: established
---

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
5. **複数リソースの同時進化が単一軸を上回る**: prompt と solution strategy を同時に進化させる co-evolution は、どちらか一方だけを繰り返し改善するより効果が高い（Autogenesis, AFlow/ADAS で裏付け）
6. **受理条件の段階化**: 改善案の採否を単一の A/B 判定に頼らず、synthetic check → holdout → delayed real-use outcome の3段ゲートに分けると、複利ループの品質保証が効く（ASI-Evolve の AutoEvolve 統合分析）
7. **間接協調も複利を生む**: 複数エージェントが直接通信せず共有メモリ経由で知識を再利用する stigmergy 型協調でも、知識アーティファクトを介した複利効果が確認されている（CORAL: 除去で性能18.6%低下、他エージェント成果の再利用が36%）
8. **測定基盤の違いに注意**: deterministic な性能指標（CPU時間等）向けの「+2%で改善採用」という閾値は、LLM出力品質のような分散が大きく評価者ブレのある指標にはそのまま適用できない。品質評価では holdout・回帰ゼロ・Goodhart検出を組み合わせた多条件が必要（yamadashy Routines perf tuning 分析）
9. **フィードバックループは echo chamber を招きうる**: 「出力→誤り指摘→修正→permanent rule化→反復」という複利ループは、放置すると出力が既存の判断や保有物に偏って収束する自己強化リスクを内包する（Hermes 60日運用記事、著者も未解決と明言）

## 関連

- [自己改善エージェント](self-improving-agents.md)
- [軌跡学習](trajectory-learning.md)
- [ワークフロー最適化](workflow-optimization.md)

## 出典

- Dorsey & Botha "From Hierarchy to Intelligence" (2026-04-01)
- Single Grain 実装体験記: 4ヶ月の複利効果の実証データ
- [ASI-Evolve: AI Accelerates AI](../../research/2026-04-08-asi-evolve-autoevolve-integration-analysis.md) — AI自己進化ループを分析、Analyzer/DB連携など5項目を段階採用
- [CORAL: Towards Autonomous Multi-Agent Evolution](../../research/2026-04-08-coral-autonomous-multi-agent-evolution-analysis.md) — 自律マルチエージェント進化を分析、heartbeat機構を優先採用
- [Environment-Driven Reinforcement Learning](../../research/2026-04-08-environment-driven-rl-analysis.md) — 環境駆動RL記事を分析、RL基盤をAutoEvolveへ接続採用
- [The Great Convergence](../../research/2026-04-09-great-convergence-analysis.md) — 汎用ハーネス収束論を分析、存在≠機能の検証課題を抽出
- [Autogenesis: A Self-Evolving Agent Protocol](../../research/2026-04-19-autogenesis-absorb-analysis.md) — 自己進化エージェント論文を分析、一部の強化案のみ採用し統一リソース層は棄却
- [Claude Code Routines性能チューニング absorb分析](../../research/2026-04-29-yamadashy-routines-perf-tuning-absorb-analysis.md) — Routines性能チューニング記事を分析、AutoEvolveへ6タスク採用
- [How To Fix AI Slop (Using Hermes)](../../research/2026-05-31-hermes-ai-slop-eval-loop-absorb-analysis.md) — Hermesのeval loop提案を分析、既存基盤が上回り自動closeループ不採用
- [How To Fix AI Slop (Using Hermes) — full-workflow 再分析](../../research/2026-05-31-hermes-eval-loop-absorb-analysis.md) — 同種Hermes eval loop記事を再分析、全Already/意図的retireで採用0
- [6 Workflows, 6 Lessons, 60 Days with Hermes Analyst](../../research/2026-06-02-hermes-60-days-6-lessons-absorb-analysis.md) — Hermes運用60日記事を分析、echo chamber対策を昇格ループ設計ノートに追記採用
