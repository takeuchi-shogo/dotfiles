---
title: トラジェクトリ学習
topics: [memory, ml-rl]
sources: [2026-03-14-trajectory-informed-memory.md, 2026-04-02-glean-trace-learning-analysis.md, 2026-03-26-memcollab-contrastive-trajectory-distillation-analysis.md, 2026-04-05-continual-learning-ai-agents-analysis.md, 2026-04-08-environment-driven-rl-analysis.md, 2026-04-09-better-harness-eval-hill-climbing-analysis.md, 2026-04-09-skill-eval-self-improving-loop-analysis.md, 2026-04-11-pepabo-failure-learning-loop-analysis.md, 2026-04-14-cognee-agent-memory-analysis.md, 2026-05-28-codex-research-agent-workflow-absorb-analysis.md, 2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md, 2026-06-20-skillmd-trajectory-mining-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 12
confidence: established
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
- **Trace-driven eval flywheel（Better Harness Hill-Climbing）**: 本番トレース→eval 化→ハーネス改善提案→検証というフライホイールが、ハーネス自己改善の中核パターン。eval を「訓練データ」として扱い、baseline-first・single-change-at-a-time・回帰保護・人間レビューゲートを伴わせることで暴走を防ぐ [EXTRACTED, conf=80]
- **Trajectory-based skill evaluation の3指標**: 正解率・介入回数（人間の修正回数）・ツールコール数の3メトリクスで軌跡を評価し、4分類（Informational / Failed calls / Command formatting / Architectural info）の改善提案に変換する。per-skill の属性分解が壊れていると、指標を増やしても改善提案自体が無意味になるという実装上の落とし穴が報告されている [EXTRACTED, conf=75]
- **Recording proxy + trace-based reward shaping（Environment-Driven RL）**: 推論プロキシで本番トレースを記録し、サンドボックス不要でトレースから直接報酬シグナルを導出するパターン。チェックポイント/クローンによる replay mechanism と組み合わせることで、同一状況での A/B 実験的検証も可能になる [EXTRACTED, conf=75]
- **メモリ統合（consolidation）は対比蒸留の一般化（Cognee）**: 反復するトレース事例を一般知識へ昇華する consolidation は MemCollab の対比蒸留と同じ構造を持つが、Cognee はさらに使用頻度に基づくエッジ重みの動的更新（usage-based reinforcement）を加える。時間ベースの decay より使用ベースの強化の方が、エージェントの実際の記憶モデルに近いという指摘がある [INFERRED, conf=65]
- **昇格基準は経過時間より複数文脈での再発が頑健（pepabo失敗学習ループ）**: 失敗を「状況・失敗・正解」の3点セットとしてトレースから記録し、単一プロジェクトでの経過日数ではなく複数の異なる文脈（プロジェクト/セッション）での再発を昇格条件にする方が、ノイズの昇格を防ぎやすい [EXTRACTED, conf=70]
- **Objective lane / Judgement lane の分離（SkillOpt）**: トレースからの自動テキスト最適化（bounded edit budget + held-out strict validation gate + rejected-edit buffer）は「正解キーで照合可能なタスク」（抽出・分類・構造化生成）でのみ機能する。absorb/review/think のような判断タスクに適用すると false positive を量産する。SSD の「品質フィルタは最小限でよい」という知見とは適用対象が異なる点に注意（SSD は学習データの品質、SkillOpt は自動編集の受理ゲート） [EXTRACTED, conf=85]
- **トレース分割・クラスタリングの cross-domain transfer は失敗しうる（SKILL.md 自動生成論文, arXiv:2606.20363）**: GUI トレースを意味境界で分割しクラスタリングして skill library を自動抽出するパイプラインは、クラスタの可読性（purity ≥0.95）は達成するが cross-domain のポリシー転移は失敗する（一部指標は trivial frequency prior を下回る）。著者は境界検出の粗さ・順序無視の segment 表現・オフライン報酬モデルの3点を失敗主因と自己診断しており、転移の成否は分割の粒度と表現に強く依存するという既存の「subtask-level 粒度が転移を駆動する」知見を負の実証結果として裏付ける [EXTRACTED, conf=80]
- **手動 annotation + 週次 diff 提案という human-gated feedback loop**: トレース（日々のブリーフ読了ログ）末尾に3行程度の手動 annotation（useful/noise/missing）を残し、週次で集計してコンテキスト更新の「diff 提案」のみ行う（自動更新はしない）パターン。auto-update には安全上のリスクがあるという指摘がある [EXTRACTED, conf=70]

## 実践的な適用

dotfiles の `session-learner.py` + `findings-to-autoevolve.py` が軌跡から知見を抽出する Critic-Refiner の近似を担う。`edit-failure-tracker.py` + `lessons-learned` が失敗を記録しているが、成功/失敗の明示的対比分析はまだない。MemCollab の知見から、Claude と Codex の対比蒸留（クロスアーキテクチャ）が同族対比より有効である可能性がある。`references/situation-strategy-map.md` として「この状況ではこの戦略を優先」という意図的に狭い粒度の状況→戦略マップを整備することが次のステップ。

SkillOpt の知見は、`session-learner.py` や `contrastive-trace-analyzer.py` が生成する改善提案の受理範囲を再考する材料になる。routing/抽出/構造化生成のように正解を機械判定できるタスク（objective lane）にはトレース由来の自動編集・held-out 検証ゲートを適用してよいが、absorb/review/think のような判断タスク（judgement lane）では人間承認を経ずに自動反映すべきではない。この線引きが曖昧だと、旧 `/improve` が false positive を量産して retire した経緯と同じ失敗を繰り返す。

**未検証トレースからの学習（SSD の知見）**

Apple の SSD 研究 (arXiv:2604.01193) は、成功/失敗ラベルなしの生サンプルでの SFT だけで +12.9pt の改善を達成した。ハーネス層への示唆:
- contrastive-trace-analyzer は現在、成功/失敗の対比を前提とするが、**ラベルなしトレースからのパターン抽出**も検討に値する
- 特に難易度の高いタスクでは、失敗トレースにも有用なパターン（部分的に正しいアプローチ、問題の分解方法）が含まれる
- session-learner.py の入力として、明確な成功/失敗判定がないセッションも対象に含めることで、学習機会を拡大できる可能性がある

SSD の知見は「タスク難易度に応じて探索度を調整する」というハーネス層の戦略にも示唆を与える。難問では多様な候補生成（高探索度）のリターンが大きく、容易な問題では精度重視（低探索度）が効率的。situation-strategy-map に難易度→探索度の軸を追加済み。

**品質フィルタに関するガイドライン（SSD "Bad Data, Good Results" の知見）**

SSD の追加実験で、温度 2.0・truncation なしの低品質データでも Pass@1 +5.7pp, Pass@5 +10.5pp の改善を達成。これは**分布リシェイピングがサンプル品質より重要**であることを示す。ハーネス層への示唆:
- session-learner.py の入力フィルタは**最小限**でよい。明らかな構文エラー（パース不能）のみ除外し、論理的な正誤は問わない
- 失敗セッションのトレースも、部分的に正しいアプローチ・問題分解パターンを含む。特に難問（推定成功率 < 0.5）では失敗トレースの学習価値が高い
- フィルタの厳格化より、トレース数の確保を優先する。品質管理は下流の contrastive-trace-analyzer に委ねる

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
- [agent-evaluation](agent-evaluation.md) — eval を訓練データとして使う hill-climbing とトレース駆動フライホイール
- [hitl-asymmetric-evaluation](hitl-asymmetric-evaluation.md) — トレースからの自動反映と人間承認ゲートの非対称設計

## ソース

- [トラジェクトリ情報メモリ生成（IBM Research）](../../research/2026-03-14-trajectory-informed-memory.md) — 3種 Tips の自動抽出と AppWorld ベンチマーク結果
- [Glean トレース学習分析](../../research/2026-04-02-glean-trace-learning-analysis.md) — Teacher-Student 比較とワークフローレベルのツール戦略学習
- [MemCollab 対比軌跡蒸留分析](../../research/2026-03-26-memcollab-contrastive-trajectory-distillation-analysis.md) — クロスエージェント対比蒸留と規範的制約フォーマット
- [Continual Learning for AI Agents](../../research/2026-04-05-continual-learning-ai-agents-analysis.md) — Model/Harness/Context 3層の継続学習フレームワークとトレース中心アーキテクチャ
- [Environment-Driven Reinforcement Learning](../../research/2026-04-08-environment-driven-rl-analysis.md) — Recording Proxy とトレース駆動報酬シェイピングによる本番RL
- [Better Harness: Eval-Driven Hill-Climbing](../../research/2026-04-09-better-harness-eval-hill-climbing-analysis.md) — eval を訓練データとするハーネス自己改善のトレース→eval フライホイール
- [Skill Evaluation & Self-Improving Loop](../../research/2026-04-09-skill-eval-self-improving-loop-analysis.md) — 正解率・介入回数・ツールコール数によるトラジェクトリ評価と per-skill 属性分解の落とし穴
- [pepabo「Claude Code 失敗学習ループ」吸収分析](../../research/2026-04-11-pepabo-failure-learning-loop-analysis.md) — 「状況・失敗・正解」3点セット記録と複数文脈再発による昇格基準
- [Build Agents that never forget（Cognee）](../../research/2026-04-14-cognee-agent-memory-analysis.md) — メモリ統合による一般知識への昇華と使用頻度ベースのエッジ重み更新
- [Codex Research Agent ワークフロー吸収分析](../../research/2026-05-28-codex-research-agent-workflow-absorb-analysis.md) — 手動 annotation と週次 diff 提案による human-gated フィードバックループ
- [Microsoft SkillOpt 自己進化スキル吸収分析](../../research/2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md) — text-space optimizer と objective lane / judgement lane の分離
- [SKILL.md 自動生成: Interaction Trajectory Mining 吸収分析](../../research/2026-06-20-skillmd-trajectory-mining-absorb-analysis.md) — GUI トレース分割・クラスタリングの cross-domain transfer 失敗の自己診断
