---
title: RLHFアライメント
topics: [ml-rl]
sources: [2026-03-18-policy-gradients-rlhf-analysis.md, 2026-03-20-rlhf-book-ch4-ch5-analysis.md, 2026-04-02-verbalized-sampling-analysis.md, 2026-04-04-overconfidence-circuits-analysis.md]
updated: 2026-04-04
---

# RLHFアライメント

## 概要

RLHF（Reinforcement Learning from Human Feedback）は、人間のフィードバックを報酬シグナルとしてLLMを最適化するアライメント技術である。Policy Gradient手法（REINFORCE/PPO/GRPOなど）によってモデルの出力分布を望ましい方向へ誘導するが、その過程でTypicality Bias（典型的な回答を過度に優遇するバイアス）やMode Collapseが副作用として発生する。dotfilesハーネスはこの理論を直接のニューラル学習ではなく、エージェント設定の離散最適化（AutoEvolve）に応用している。

## 主要な知見

- **アルゴリズム選択より入力データ品質が決定要因** — PPO/GRPOの差よりも報酬シグナルの質が最終性能を左右する
- **Bradley-Terryモデル** — P(i>j) = sigmoid(r_i - r_j)。スコアの絶対値ではなく差分のみが有意
- **PRM vs ORM** — Process Reward Model（ステップ単位）とOutcome Reward Model（結果単位）の使い分けがタスク種別に依存する
- **Trust Region制約** — 更新幅の上限（PPOのclipping）が安定学習に不可欠。dotfilesでは`max 3 files/cycle`が対応
- **Typicality Bias** — RLHFはα≈0.57-0.65の強さで典型回答を好む。創作・合成データ生成タスクで多様性が失われる根本原因
- **Verbalized Sampling** — プロンプトだけでTypicality Biasを克服し、創作で1.6-2.1倍の多様性向上が可能
- **生成型RM（LLM-as-Judge）** — 温度=0でロバスト性向上。dotfilesの`evaluator-calibration-guide.md`でTPR/TNR補正済み
- **Verbalized Confidence Inflation** — RLHF はモデルの信頼度言語化回路 (CMC) を増幅し、言語化された信頼度を体系的に膨張させる（Zhao et al. 2026, arXiv:2604.01457）。Typicality Bias（多様性の問題）とは直交する calibration の問題
- **Instruction Tuning原則** — 応答部分のみ損失計算（Prompt Masking）、低学習率での保守的更新
- **Advantage推定** — A/Bデルタ（改善前後の差分+2pp閾値）がharness側のAdvantage相当

## 実践的な適用

dotfilesハーネスはRLHF理論を「プロンプト空間の離散最適化」として再解釈している。

| RLの概念 | harness上の対応 |
|---------|---------------|
| Policy π_θ | CLAUDE.md + skills + agents + hooks の設定全体 |
| Reward R | importance score / skill health score / review結果 |
| Advantage A | A/Bデルタ（改善前後+2pp閾値） |
| Trust Region | max 3 files/cycle + 3連続reject停止 |
| Episode | セッション |

Typicality Biasへの対処として`references/verbalized-sampling-guide.md`を整備し、レビュー・創作タスクでVS（Standard/CoT/Multi）プロンプト技法を適用できる。また`cross-model-insights.md`にTypicality Biasセクションを追記してサブエージェント選択時のバイアス認知を強化している。

## 関連概念

- [メタ進化](meta-evolution.md) — AutoEvolveループとRLHFサイクルの対応関係
- [エージェント評価](agent-evaluation.md) — LLM-as-JudgeとRMの実装パターン

## ソース

- [Policy Gradients for RLHF](../../research/2026-03-18-policy-gradients-rlhf-analysis.md) — REINFORCE/PPO/GRPOの数学的定式化とharness概念へのマッピング
- [RLHF Book Ch4/Ch5](../../research/2026-03-20-rlhf-book-ch4-ch5-analysis.md) — Instruction TuningとReward Modelingの実装詳細、Gap分析
- [Verbalized Sampling](../../research/2026-04-02-verbalized-sampling-analysis.md) — Typicality Biasの定量的証明とプロンプトのみによる多様性回復手法
- [Overconfidence Circuits](../../research/2026-04-04-overconfidence-circuits-analysis.md) — 信頼度言語化回路(CMC)の機械的分析とRLHFによる過剰自信増幅
