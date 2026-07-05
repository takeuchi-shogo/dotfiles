---
title: スキルチェイニング
topics: [skill]
sources: [2026-04-02-skill-chaining-actions-analysis.md, 2026-04-03-skill-loop-wiring-analysis.md, 2026-03-23-minimax-skills-analysis.md, 2026-04-10-atomic-skills-coding-agents-analysis.md, 2026-04-23-skill-graphs-2.0-absorb-analysis.md, 2026-04-24-google-skills-adk2-absorb-analysis.md, 2026-04-29-mattpocock-skills-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 7
confidence: established
---

# スキルチェイニング

## 主要な知見

- **Knowledge Overhang**: モデルが知っているが自発的に使わない知識をスキルで引き出す。OOD 知識を in-distribution 行動に変換するのがスキルの役割
- **スキルをエピソードメモリとして扱う**: スコープ付きコンテキストで活性化し、完了後にクリーンアップ。セッションスタックとして機能する
- **Rules vs Skills の Progressive Disclosure**: ルール＝強制ロード（常時コンテキスト汚染）、スキル＝遅延ロード（必要時のみ）。`<important if>` タグが境界を定義する
- **Orchestration Skills**: スキルが他のスキルをシーケンスするメタスキル。`/epd`（Spec→Spike→Validate）や `/dev-cycle` がその例
- **テンプレートではなくループとして配線**: 1回で止まるテンプレートより、回るたびに精度が上がる Scheduling→Memory→Feedback のループ
- **5つのスキルタイプ**: Writing/Research/Review/Memory/Ops。それぞれ異なる配線パターンを持つ
- **Decision Table パターン**: 技術選択肢を表形式で整理し「When」列で判断基準を明示。スキルの品質を構造化する
- **Mandatory Workflow**: Step 0〜N の強制手順でスキル発火後の行動を規定し、再現性を担保する
- **3層合成モデル (atoms/molecules/compounds)**: atoms=単一目的で他スキルを呼ばないプリミティブ、molecules=2-10 atomsの明示的chaining、compounds=moleculesを束ねるplaybookで人間がdriver。2025-2026業界標準（Mastra/LangGraph 2.0/Anthropic Skillsで収束）
- **Reliability Ceiling**: compoundが8-10 molecules超になると信頼性が$0.9^n$で指数減衰（n=8→43%, n=10→35%）。composition_depth計測とPLANS.mdのCompound Ceiling（≤8 molecules推奨）で観測
- **原子スキル分解の3原則**: 最小性・自己完結性・独立評価可能性。Joint RL（GRPO）による訓練で異質スキル間の負の干渉なしに転移することが実証されている（原子スキル論文, GLM-4.5-Air）
- **5-skill daily chain の実例**: grill-me → to-prd → to-issues → tdd → improve-codebase-architecture（mattpocock/skills, 28K stars）。各ステップは narrow scope の process encoding として設計され、`disable-model-invocation`で自律発火とユーザー手動起動を構造的に分離。チェインの各Issueには HITL/AFK マーカーを付与し実行モードを明示する

## 概要

スキルを静的プロンプトではなく、スコープを持つ動的アクション（contextual behaviors）として連結する設計パターン。単一スキルの呼び出しに留まらず、スキルが他のスキルを参照・シーケンスする Orchestration Skills と、Scheduling→Memory→Feedback の閉ループで自律進化するループ配線が核心。

## 実践的な適用

dotfiles の `/epd`・`/dev-cycle`・`/review` は Orchestration Skill の実装例。`<important if>` 条件タグが Rules vs Skills の境界を実装し、CLAUDE.md へのコンテキスト汚染を防ぐ。AutoEvolve の Diff-Distill ループがスキルの自律進化を担い、`continuous-learning` hook がリアクティブに変化を検知する。MiniMax パターン（Decision Table・Anti-Patterns テーブル・Mandatory Workflow）はスキル構造の標準テンプレートとして採用済み。

## 関連概念

- [skill-design](skill-design.md) — 個別スキルの設計原則と構造
- [workflow-optimization](workflow-optimization.md) — スキルチェインによるワークフロー自動化
- [self-improving-agents](self-improving-agents.md) — フィードバックループによるスキルの自律進化

## ソース

- [スキルチェイニング・アクション分析](../../research/2026-04-02-skill-chaining-actions-analysis.md) — Knowledge Overhang とエピソードメモリとしてのスキル設計
- [スキルループ配線分析](../../research/2026-04-03-skill-loop-wiring-analysis.md) — Three Rings of a Loop と 5スキルタイプの配線パターン
- [MiniMax スキル分析](../../research/2026-03-23-minimax-skills-analysis.md) — Decision Table・Anti-Patterns・Mandatory Workflow の構造化パターン
- [Scaling Coding Agents via Atomic Skills (arXiv)](../../research/2026-04-10-atomic-skills-coding-agents-analysis.md) — 原子スキル分解論文を分析、独立評価可能性など4タスク採用
- [Skill Graphs 2.0](../../research/2026-04-23-skill-graphs-2.0-absorb-analysis.md) — Skill Graphs記事を分析、composition depth計測とADR追加を採用
- [google/skills + ADK 2.0 Multi-Agent Orchestration Patterns](../../research/2026-04-24-google-skills-adk2-absorb-analysis.md) — google/skills 13個全採択、ADK 2.0パターンは強化不要と判定
- [mattpocock/skills (28K stars) absorb分析](../../research/2026-04-29-mattpocock-skills-absorb-analysis.md) — mattpocock 5-skillチェーンを分析、HITL/AFKマーカー等2件統合
