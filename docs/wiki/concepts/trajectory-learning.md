---
title: トラジェクトリ学習
topics: [memory, ml-rl]
sources: [2026-03-14-trajectory-informed-memory.md, 2026-04-02-glean-trace-learning-analysis.md, 2026-03-26-memcollab-contrastive-trajectory-distillation-analysis.md]
updated: 2026-04-04
---

# トラジェクトリ学習

## 概要

エージェントの実行軌跡（trajectory）から構造化された知識を自動抽出し、将来タスクに再利用するメモリ学習パターン。単なる成功事例の記録に留まらず、成功/失敗の対比蒸留によってエージェント非依存の制約として知識を一般化する。IBM Research・Glean・MemCollab の3アプローチがそれぞれ異なる角度から同一問題に取り組んでいる。

## 主要な知見

- **3種の Tips（IBM Research）**: Strategy（成功パターン）/ Recovery（失敗→回復シーケンス）/ Optimization（非効率改善）の粒度で軌跡を分類し、セマンティック検索で注入。AppWorld で SGC +14.3pp（難易度3では +28.5pp）
- **subtask-level 粒度が精度を駆動**: task-level より subtask-level の Tips が TGC を大きく改善。粒度が細かいほど転移しやすい
- **Teacher-Student 比較（Glean）**: 高推論予算 teacher + 制約付き student の複数トレース比較でベスト戦略を抽出。個別ツール呼び出しではなくツール間の組み合わせパターンを学習
- **Multi-trace 合意検証**: 複数トレースから事実主張を抽出・合意チェック。不一致解消不能時は学習しない（ノイズ混入防止）
- **対比蒸留（MemCollab）**: 同一タスクへの成功/失敗軌跡を対比し `enforce X; avoid Y` 形式の規範的制約に蒸留。生のソリューションではなく抽象的推論原則を共有
- **直接転送は逆効果**: 強いモデルのメモリを弱いモデルに直接転送すると baseline を下回るケースあり（MATH500: 50.6% vs 52.2%）。クロスエージェント対比が self-contrast を上回る
- **Spatial Pruning 効果**: エラーパターンが探索空間を刈り込み、推論ターン数を削減（2.7→2.2 turns）
- **Deployment/User 2層メモリ分離**: 共有ワークフロー戦略（ツール名・シーケンス）と個人プリファレンスを分けて管理

## 実践的な適用

dotfiles の `session-learner.py` + `findings-to-autoevolve.py` が軌跡から知見を抽出する Critic-Refiner の近似を担う。`edit-failure-tracker.py` + `lessons-learned` が失敗を記録しているが、成功/失敗の明示的対比分析はまだない。MemCollab の知見から、Claude と Codex の対比蒸留（クロスアーキテクチャ）が同族対比より有効である可能性がある。`references/situation-strategy-map.md` として「この状況ではこの戦略を優先」という意図的に狭い粒度の状況→戦略マップを整備することが次のステップ。

## 関連概念

- [agent-memory](agent-memory.md) — セッション横断のメモリアーキテクチャと3スコープ設計
- [self-improving-agents](self-improving-agents.md) — AutoEvolve ループとエージェントの自律改善
- [meta-evolution](meta-evolution.md) — ハーネス自体の自動最適化と Meta-Harness

## ソース

- [トラジェクトリ情報メモリ生成（IBM Research）](../../research/2026-03-14-trajectory-informed-memory.md) — 3種 Tips の自動抽出と AppWorld ベンチマーク結果
- [Glean トレース学習分析](../../research/2026-04-02-glean-trace-learning-analysis.md) — Teacher-Student 比較とワークフローレベルのツール戦略学習
- [MemCollab 対比軌跡蒸留分析](../../research/2026-03-26-memcollab-contrastive-trajectory-distillation-analysis.md) — クロスエージェント対比蒸留と規範的制約フォーマット
