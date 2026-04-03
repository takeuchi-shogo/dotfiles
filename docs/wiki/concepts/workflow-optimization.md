---
title: ワークフロー最適化
topics: [agent, productivity]
sources: [2026-03-30-workflow-optimization-survey-analysis.md, 2026-03-25-coding-agent-workflow-2026-analysis.md, 2026-03-25-dev-cycle-analysis.md]
updated: 2026-04-04
---

# ワークフロー最適化

## 概要

ワークフロー最適化とは、LLMエージェントの実行グラフを動的に最適化し、品質・コスト・速度のトレードオフを改善する手法群を指す。IBM Research+RPIのサーベイ論文はエージェントワークフローをAgentic Computation Graph (ACG)として形式化し、77本の文献を「静的 vs 動的」「ノードレベル vs グラフレベル」の2軸で整理した。2026年の開発は「プロジェクトワークフロー/実装テクニック/インフラ」の3層で設計し、フィードバックループを決定論的に閉じることが鍵であり、人間は構造化されたポイントでのみ介入する設計が推奨される。

## 主要な知見

- **ACG形式化**: Template（再利用設計）/ Realized Graph（実行時構造）/ Execution Trace（実行ログ）の3層を区別する
- **"When static is enough" 3条件**: 制約された演算子空間・信頼できる評価・反復デプロイが同時成立する場合に静的グラフを選ぶ
- **Graph > Prompt**: 失敗原因が構造的（ノード欠落/情報パス誤り）なら、プロンプト修正では解決できない
- **Verifier配置戦略**: cheap + semantically meaningfulな箇所に戦略配置し、全ステップ配置は非効率
- **Best-of-N並列戦略**: 4並列で成功確率68%、8並列で90%に向上する
- **Skills 3段階ローディング**: L1メタデータ(100tok) / L2指示書(<5000tok) / L3リソース(無制限)で段階的に読み込む
- **Context Rot対策**: セッション短縮・Subagent活用・compact・不要ファイル回避・1Mコンテキスト活用の5戦術
- **Agent-Nativeコード設計**: Grep-able命名・collocated tests・機能単位モジュール化・テスト=報酬信号・明確なAPI境界
- **4 Workflows**: Harper Reed式 / SDD(Spec-Driven) / RPI(Research→Plan→Implement) / Superpowersを使い分ける
- **Issue起点協調サイクル**: Claude Code（実装）+ Codex（レビュー）の6ステップでPR品質を担保する

## 実践的な適用

このリポジトリでは`/dev-cycle`スキルがIssue起点のClaude Code + Codex協調サイクルを実装している。`workflow-guide.md`がS/M/Lスケール判断基準を定義し、`/rpi`・`/sdd`・`/autonomous`などのワークフロースキルが4 Workflowsパターンに対応する。`task validate-configs`と`task validate-symlinks`がVerifier配置の実例。Git Worktreeを使ったBest-of-N並列実行は`/autonomous`スキル内のガイドラインに記述されている。`CLAUDE.md`のProgressive Disclosure設計（~130行）がSkills 3段階ローディングのL1相当を担う。

## 関連概念

- [multi-agent-architecture](multi-agent-architecture.md) — 複数エージェントの協調パターン
- [quality-gates](quality-gates.md) — ワークフロー内の品質検証ポイント
- [spec-driven-development](spec-driven-development.md) — 仕様起点の開発フロー

## ソース

- [Workflow Optimization Survey](../../research/2026-03-30-workflow-optimization-survey-analysis.md) — ACG形式化・GDT×GPM分類・"Graph > Prompt"診断を77本の文献から体系化
- [Coding Agent Workflow 2026](../../research/2026-03-25-coding-agent-workflow-2026-analysis.md) — 4 Workflows・Best-of-N・Skills 3段階ローディング等20手法を体系化
- [Dev Cycle Analysis](../../research/2026-03-25-dev-cycle-analysis.md) — Issue起点のClaude Code + Codex 6ステップ協調開発サイクルの設計
