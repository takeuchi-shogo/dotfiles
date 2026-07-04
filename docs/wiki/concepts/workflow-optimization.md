---
title: ワークフロー最適化
topics: [agent, productivity]
sources: [2026-03-30-workflow-optimization-survey-analysis.md, 2026-03-25-coding-agent-workflow-2026-analysis.md, 2026-03-25-dev-cycle-analysis.md, 2026-04-09-30-claude-prompts-analysis.md, 2026-04-09-better-harness-eval-hill-climbing-analysis.md, 2026-04-09-claude-code-automation-guide-analysis.md, 2026-04-10-claude-full-ai-stack-2026-analysis.md, 2026-04-11-caveman-genshijin-brevity-analysis.md, 2026-04-11-claude-only-stack-cyrilxbt-analysis.md, 2026-04-11-new-software-cli-skills-vertical-models-analysis.md, 2026-04-19-harness-everything-absorb-analysis.md, 2026-04-23-agents-md-patterns-absorb-analysis.md, 2026-04-26-workflow-trellis-absorb-analysis.md, 2026-05-14-claude-code-routines-absorb-analysis.md, 2026-05-30-opus48-setup-guide-absorb-analysis.md, 2026-05-30-single-threaded-300-agents-absorb-analysis.md, 2026-05-31-32-claude-code-hacks-absorb-analysis.md, 2026-05-31-4-agent-pipeline-absorb-analysis.md, 2026-06-02-how-to-actually-use-claude-14-steps-absorb-analysis.md, 2026-06-03-dynamic-workflows-absorb-analysis.md, 2026-06-12-servant-engineering-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 21
confidence: established
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
- **Instruction budget 総量計測**: 常時露出する指示の総量は本文行数だけでなく description・hook注入・MCP tool定義を含めて計測すべき。使われない reference/skill/agent の dead-weight scan も予算を圧迫する要因になる
- **Control Surface Override**: S規模のタスクでも auth 変更・不可逆操作（DB migration/削除）・harness 変更・breaking change は M 相当の Gate を強制する。Workflow Trellis の「高 Relief Pressure × 高 Control Demand」象限に対応し、規模だけでなくリスク種別でルーティングを補正する
- **Routine 設計の Bulletproof Prompt**: role/task/process/output/error/constraints の6要素 rubric で自動化 Routine のプロンプト品質を担保し、Daily PR Review・Weekly Dep Audit などの Recipe Catalog として再利用する
- **Faceted Prompting によるレビュー速度改善**: Persona/Policy/Knowledge/Instruction/Output Contract の5分割で判断基準をファイル化し、Worker(edit不可)/Judgeを分離した決定論的 FSM オーケストレーションでレビューを並列実行する。速度改善には「レビューにかかった時間」の計測基盤が前提になる
- **Eval-as-training-data**: Eval を hill-climbing の学習信号として扱い、baseline-first・single-change-at-a-time・train/holdout split で回帰を防ぎながらハーネスを継続改善する
- **Online cascade routing**: 安いモデルで試行→品質判定→昇格/停止という動的カスケードは、静的な tier ルーティングより効率が良い。モデル固有のルールは永続資産ではなく削除条件付きの「debt」として管理する

## 実践的な適用

このリポジトリでは`/dev-cycle`スキルがIssue起点のClaude Code + Codex協調サイクルを実装している。`workflow-guide.md`がS/M/Lスケール判断基準を定義し、`/rpi`・`/sdd`・`/autonomous`などのワークフロースキルが4 Workflowsパターンに対応する。`task validate-configs`と`task validate-symlinks`がVerifier配置の実例。Git Worktreeを使ったBest-of-N並列実行は`/autonomous`スキル内のガイドラインに記述されている。`CLAUDE.md`のProgressive Disclosure設計（~130行）がSkills 3段階ローディングのL1相当を担う。Control Surface Override は `references/stage-transition-rules.md` に、Routine プロンプト rubric は `references/routine-prompt-rubric.md` に、Online cascade routing は `references/cascade-routing.md` と `references/model-debt-register.md` に実装されている。

## 関連概念

- [multi-agent-architecture](multi-agent-architecture.md) — 複数エージェントの協調パターン
- [quality-gates](quality-gates.md) — ワークフロー内の品質検証ポイント
- [spec-driven-development](spec-driven-development.md) — 仕様起点の開発フロー

## ソース

- [Workflow Optimization Survey](../../research/2026-03-30-workflow-optimization-survey-analysis.md) — ACG形式化・GDT×GPM分類・"Graph > Prompt"診断を77本の文献から体系化
- [Coding Agent Workflow 2026](../../research/2026-03-25-coding-agent-workflow-2026-analysis.md) — 4 Workflows・Best-of-N・Skills 3段階ローディング等20手法を体系化
- [Dev Cycle Analysis](../../research/2026-03-25-dev-cycle-analysis.md) — Issue起点のClaude Code + Codex 6ステップ協調開発サイクルの設計
- [30 Claude Prompts, Workflows & Automations](../../research/2026-04-09-30-claude-prompts-analysis.md) — 実務プロンプト30選を分析、決定ジャーナルなど9タスク採用
- [Better Harness: Eval-Driven Hill-Climbing](../../research/2026-04-09-better-harness-eval-hill-climbing-analysis.md) — Eval駆動ハーネス改善、baseline-first・回帰保護を全採用
- [You Can Automate Anything — 7 Easy Prompts](../../research/2026-04-09-claude-code-automation-guide-analysis.md) — 日常自動化7プロンプトを分析、実現可能性ラベル等2件採用
- [How to Build a Full AI Stack Using Only Claude in 2026](../../research/2026-04-10-claude-full-ai-stack-2026-analysis.md) — Claude単体AIスタック記事、Obsidian同期hookのみ採用
- [日本語簡潔化プロンプト genshijin/caveman](../../research/2026-04-11-caveman-genshijin-brevity-analysis.md) — 日英簡潔化手法、日本語Drop Listをconcise.mdに統合
- [How to Build a Full AI Stack Using Only Claude in 2026 再分析](../../research/2026-04-11-claude-only-stack-cyrilxbt-analysis.md) — 同記事の再分析、全項目既存済みで不採用
- [The New Software: CLI, Skills & Vertical Models](../../research/2026-04-11-new-software-cli-skills-vertical-models-analysis.md) — SaaS戦略記事からcascade promotion gate・model debt registerを採用
- [Harnesses are everything](../../research/2026-04-19-harness-everything-absorb-analysis.md) — ハーネス設計記事、instruction budget計測等6項目を採用
- [A good AGENTS.md is a model upgrade](../../research/2026-04-23-agents-md-patterns-absorb-analysis.md) — AGENTS.md記事、search-result sprawl監査等7タスク採用
- [Workflow Trellis (2x2フレームワーク)](../../research/2026-04-26-workflow-trellis-absorb-analysis.md) — 2軸ワークフロー設計論、Control Surface Override等3件を統合
- [How to Set Up Claude Code Routines](../../research/2026-05-14-claude-code-routines-absorb-analysis.md) — Routines機能を検証、Bulletproof prompt rubricとRecipe Catalogを新規採用
- [The Claude Opus 4.8 Setup Guide](../../research/2026-05-30-opus48-setup-guide-absorb-analysis.md) — Opus4.8設定ガイド、Fast Mode用途指針を採用
- [You're Not Slow. You're Single-Threaded: 300 Agents](../../research/2026-05-30-single-threaded-300-agents-absorb-analysis.md) — Kimi300エージェント群記事、並列主張は既存確認済みで不採用
- [32 Claude Code hacks](../../research/2026-05-31-32-claude-code-hacks-absorb-analysis.md) — 32個のCC hacks記事、ultracode表記追記のみ採用
- [4-Agent Pipeline](../../research/2026-05-31-4-agent-pipeline-absorb-analysis.md) — Planner→Coder→Tester→Reviewer固定パイプライン、Tester境界1件のみ採用
- [movez「Claudeの14ステップ活用法」](../../research/2026-06-02-how-to-actually-use-claude-14-steps-absorb-analysis.md) — Claude活用14ステップ記事、既存判断で全手法カバー済みで不採用
- [A harness for every task: dynamic workflows](../../research/2026-06-03-dynamic-workflows-absorb-analysis.md) — Workflow tool記事、意図的不採用を維持しつつリンク切れ修正
- [nrslib サーヴァントエンジニアリング](../../research/2026-06-12-servant-engineering-absorb-analysis.md) — AIレビュー速度改善記事、計測基盤・Faceted Prompting等8件を統合プラン化
