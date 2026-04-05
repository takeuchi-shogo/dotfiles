---
title: トラジェクトリ学習
topics: [memory, ml-rl]
sources: [2026-03-14-trajectory-informed-memory.md, 2026-04-02-glean-trace-learning-analysis.md, 2026-03-26-memcollab-contrastive-trajectory-distillation-analysis.md, 2026-04-05-continual-learning-ai-agents-analysis.md]
updated: 2026-04-05
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

**未検証トレースからの学習（SSD の知見）**

Apple の SSD 研究 (arXiv:2604.01193) は、成功/失敗ラベルなしの生サンプルでの SFT だけで +12.9pt の改善を達成した。ハーネス層への示唆:
- contrastive-trace-analyzer は現在、成功/失敗の対比を前提とするが、**ラベルなしトレースからのパターン抽出**も検討に値する
- 特に難易度の高いタスクでは、失敗トレースにも有用なパターン（部分的に正しいアプローチ、問題の分解方法）が含まれる
- session-learner.py の入力として、明確な成功/失敗判定がないセッションも対象に含めることで、学習機会を拡大できる可能性がある

SSD の知見は「タスク難易度に応じて探索度を調整する」というハーネス層の戦略にも示唆を与える。難問では多様な候補生成（高探索度）のリターンが大きく、容易な問題では精度重視（低探索度）が効率的。situation-strategy-map に難易度→探索度の軸を追加することで、best-of-n の N 値や VS バリアントの選択を自動化できる可能性がある。

## 3層継続学習フレームワーク（Chase 2026）

Harrison Chase は AI エージェントの継続的学習が3層で起きることを整理した:

| 層 | 対象 | 学習手法 | 当セットアップでの対応 |
|---|------|---------|---------------------|
| **Model** | モデル重み | SFT, RL (GRPO) | 外部（Anthropic/OpenAI が提供） |
| **Harness** | エージェントコード + 常時付随する指示・ツール | Meta-Harness: トレース→評価→コード改善提案 | AutoEvolve `/improve` + `session-learner.py` |
| **Context** | 設定可能な指示・スキル・メモリ | offline "dreaming" / hot-path 実行中更新 | offline: AutoEvolve bg loop / hot-path: `/eureka`, memory hooks |

**トレースが全層の学習を駆動する統一基盤**である点が重要。モデル学習（SFT データ）、ハーネス改善（Meta-Harness の FS ベース履歴）、コンテキスト更新（dreaming のトレース分析）のいずれもトレースを入力とする。当セットアップでは `session-trace-store.py` → `contrastive-trace-analyzer.py` → `findings-to-autoevolve.py` のパイプラインがこの統一基盤に相当する。

コンテキスト層の学習には2つの軸がある:
- **粒度**: agent-level（全ユーザー共通）vs tenant-level（user/org/team 固有）
- **明示性**: ユーザー主導（"remember this"）vs エージェント自律（ハーネス指示に基づく自動記憶）

## 関連概念

- [agent-memory](agent-memory.md) — セッション横断のメモリアーキテクチャと3スコープ設計
- [self-improving-agents](self-improving-agents.md) — AutoEvolve ループとエージェントの自律改善
- [meta-evolution](meta-evolution.md) — ハーネス自体の自動最適化と Meta-Harness

## ソース

- [トラジェクトリ情報メモリ生成（IBM Research）](../../research/2026-03-14-trajectory-informed-memory.md) — 3種 Tips の自動抽出と AppWorld ベンチマーク結果
- [Glean トレース学習分析](../../research/2026-04-02-glean-trace-learning-analysis.md) — Teacher-Student 比較とワークフローレベルのツール戦略学習
- [MemCollab 対比軌跡蒸留分析](../../research/2026-03-26-memcollab-contrastive-trajectory-distillation-analysis.md) — クロスエージェント対比蒸留と規範的制約フォーマット
- [Continual Learning for AI Agents](../../research/2026-04-05-continual-learning-ai-agents-analysis.md) — Model/Harness/Context 3層の継続学習フレームワークとトレース中心アーキテクチャ
