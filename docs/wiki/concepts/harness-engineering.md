---
title: ハーネスエンジニアリング
topics: [harness]
sources:
  - 2026-03-23-harness-engineering-article-analysis.md
  - 2026-03-28-harness-engineering-comprehensive-analysis.md
  - 2026-03-31-autoharness-code-harness-synthesis-analysis.md
  - 2026-03-31-nlah-natural-language-agent-harnesses-analysis.md
  - 2026-04-02-harness-books-analysis.md
  - 2026-04-06-agent-harness-anatomy-analysis.md
updated: 2026-04-06
---

# ハーネスエンジニアリング

## 概要

ハーネスエンジニアリングとは、AIエージェントの能力を制御し信頼性の高い成果に変換するための実行環境全体を設計する工学的パラダイムである。「Prompt → Context → Harness」という3段階の進化において最新の段階に位置し、エンジニアの役割を「コードを書く人」から「エージェントが確実に正しいコードを生産する環境を設計する人」へと転換させる。核心哲学は "Humans steer. Agents execute." であり、ハーネス設計の質がモデル選択より品質差異を大きく左右する（44% vs 14%）。

## 主要な知見

- **パラダイム進化の3段階**: Prompt Engineering（単発リクエスト）→ Context Engineering（単一セッション）→ Harness Engineering（セッション横断・永続的）。ハーネスは上位概念としてContextとPromptを包含する
- **5つの構成柱**: ツールオーケストレーション、ガードレール、フィードバックループ、観測可能性、Human-in-the-Loop。同一モデルでもハーネス設計次第でスコアが 42%→78% まで変動した事例がある
- **Scaffolding > Model の定量根拠**: AutoHarness研究では Gemini-2.5-Flash+ハーネス（0.870）が GPT-5.2-High（0.844）を推論コスト $0 で上回った。ハーネス設計がモデル選択より重要
- **ハーネスのパターン分類**: Harness-as-Action-Filter（出力フィルタ）と Harness-as-Policy（コードが直接方針を出力）の2種。後者は推論時LLM呼び出し不要
- **10原則（harness-books）**: モデルは不安定部品、Query Loopが心拍、エラーパスは主パス、検証は独立させる、チーム制度は個人技巧より重要——などの設計哲学
- **NLAH（自然言語エージェントハーネス）**: ハーネスのdesign-pattern layerを自然言語で外部化し共有ランタイム（IHR）で実行可能にする。6要素（Contracts, Roles, Stages, Adapters, State semantics, Failure taxonomy）で形式化
- **Self-evolution が最高ROI**: NLAH研究では Self-evolution モジュールが最もコスト効率の高い改善（75.2→80.0点）をもたらした
- **「構造追加 ≠ 性能向上」**: モジュール追加は solved-set replacer として機能し、ローカル検証成功とベンチマーク受理が乖離するリスクがある。KISS原則と整合する
- **Build to Delete 設計**: ハーネス要素（hook, script, agent）は次世代モデルで不要になりうる過渡的技術。軽量・モジュラーに保ち削除コストを最小化する
- **1セッション1機能ルール**: セッション境界でのコンテキスト喪失を防ぐ実践的制約。セッション終了時に main マージ可能なクリーン状態を維持する

## Context Constitution と harness 10原則の統合

Letta AI の "Memory-as-Harness" 研究が提唱する **Context Constitution**（7原則）は、既存の harness 10原則（harness-books）と補完的に統合される。

10原則にコンテキスト・メモリ管理の視点を加えると:
- **「モデルは不安定部品」** → メモリ管理もモデル任せにしない。保存先決定・compaction 戦略・survival priorities はハーネスが明示的に制御する
- **「Query Loop が心拍」** → Query Loop に PreCompact flush と PostCompact verification を組み込み、コンパクション前後の状態保全をハーネスが担保する
- **「エラーパスは主パス」** → コンテキスト消失（サイレント失敗）は最も深刻なエラー。Proactive 管理（消失前退避）でエラーパスを最小化する

これにより harness 10原則は「コンテキスト管理を含む包括的な実行環境設計原則」として拡張される。`references/context-constitution.md` が Context Constitution の実装ドキュメントとして機能し、`harness-10-principles-checklist.md` と対で参照する。

また、**Memory-as-Harness** 設計思想はハーネスの5つの構成柱（ツールオーケストレーション・ガードレール・フィードバックループ・観測可能性・Human-in-the-Loop）の観測可能性に直結する。何をロードするか・何が圧縮を生き残るか・何を永続化するかという不可視の意思決定を visible にすることが harness 設計の責務として明確化された。

## 実践的な適用

このリポジトリはハーネスエンジニアリングの参照実装として機能している。

**実装済みコンポーネント:**
- `.config/claude/scripts/` — hooks 4層（runtime/policy/lifecycle/learner）+ lib
- `.config/claude/settings.json` — Hook 自動実行ゲート（formatter/policy/completion gate/session）
- `docs/agent-harness-contract.md` — harness logic と runtime charter の境界定義
- `docs/plans/` / `tmp/plans/` — plan-lifecycle hook による計画管理
- `.config/claude/references/harness-10-principles-checklist.md` — 10原則チェックリスト
- `.config/claude/references/harness-polity-comparison.md` — Claude Code vs Codex の政体比較

**CLAUDE.md の設計原則:**
- `Scaffolding > Model` 原則に Harness-as-Policy(0.870) > GPT-5.2-High(0.844) の定量根拠を記載
- `<important if>` 条件付きタグで hook/script 変更時のみハーネス契約を表示
- `Build to Delete` 原則でハーネス要素の過剰設計を抑制

## 関連概念

- [quality-gates](quality-gates.md) — ハーネスのフィードバックループを構成する品質ゲートの詳細
- [multi-agent-architecture](multi-agent-architecture.md) — ハーネスが制御するマルチエージェント協調の設計
- [self-improving-agents](self-improving-agents.md) — Self-evolution モジュールによるハーネス自体の改善
- [autoharness](autoharness.md) — LLMがコードハーネスを自動生成するAutoHarness手法の詳細
- [context-management](context-management.md) — Context Constitution と Proactive コンテキスト管理。ハーネスのメモリ制御責務の実装
- [agent-memory](agent-memory.md) — Memory-as-Harness 設計思想とメモリ4分類の位置づけ

## ソース

- [Harness Engineering 記事分析](../../research/2026-03-23-harness-engineering-article-analysis.md) — 2エージェント構成・1セッション1機能・4層フィードバックの実践的ハーネス設計パターン
- [Harness Engineering 包括的調査](../../research/2026-03-28-harness-engineering-comprehensive-analysis.md) — 33記事横断分析。定義・起源・5つの柱・成果・批評を網羅
- [AutoHarness 分析](../../research/2026-03-31-autoharness-code-harness-synthesis-analysis.md) — Google DeepMindによるコードハーネス自動合成。小モデル+ハーネスが大モデル単体を上回ることを実証
- [NLAH 分析](../../research/2026-03-31-nlah-natural-language-agent-harnesses-analysis.md) — 自然言語ハーネスの形式化（6要素）と共有ランタイム（IHR）の設計論
- [Harness Books 分析](../../research/2026-04-02-harness-books-analysis.md) — Claude CodeとCodexのソースコードを行番号レベルで分析した10原則と政体比較フレームワーク
- [Letta: Memory-as-Harness](../../research/2026-04-04-letta-memory-as-harness-analysis.md) — Context Constitution が harness 10原則を補完する視点・Memory-as-Harness によるコンテキスト可視化責務の明確化
- [Agent Harness Anatomy Analysis](../../research/2026-04-06-agent-harness-anatomy-analysis.md) — ハーネスの12コンポーネント + 7アーキテクチャ決定の体系化。recovery type 4分類・observation masking・harness simplification audit

## Related External Insights

- **[CREAO AI-First Strategy (2026-04)](../../research/2026-04-14-creao-ai-first-analysis.md)**: harness engineering を「エージェント有効化」と再定義し、抽象原理 4 つ (観測可能化 / 判断ゲート化 / 批評を成果物に / 失敗→capability gap→durable artifact) に集約。個人 dotfiles 文脈では企業儀式を棄却し抽象原理のみ採用。
