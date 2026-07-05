---
title: コンテキストエンジニアリング
topics: [claude-code, memory]
sources: [2026-03-24-ace-agentic-context-engineering-analysis.md, 2026-03-19-important-if-conditional-tags-analysis.md, 2026-03-25-context-and-impact-analysis.md, 2026-03-18-evaluating-agentsmd-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 33
confidence: established
---

# コンテキストエンジニアリング

## 概要

コンテキストエンジニアリングとは、LLM に渡す情報（system prompt・指示・メモリ）の構造・配置・更新手法を設計する技術領域である。ACE 論文（ICLR 2026）は、コンテキストをモノリシックなテキストとして一括書き換えするアプローチが「Context Collapse」（18,282 tokens が 122 tokens に崩壊してベースラインを下回る）を引き起こすことを示した。一方、AGENTS.md の実証評価（ETH Zurich）は、LLM が生成したコンテキストファイルは性能を -0.5〜-2% 低下させるのに対し、人間が記述した指示は +4% の改善をもたらすことを明らかにしており、コンテキストの質と構造が定量的な性能差を生む。

## 主要な知見

- **Brevity Bias の危険性**: コンテキスト最適化手法がドメイン固有の戦略やエッジケースを「簡潔さ」のために削ぎ落とす問題。ACE はインクリメンタルデルタ更新でこれを回避する
- **Incremental Delta Updates**: コンテキストを bullet 単位で管理し、helpfulness/harmfulness カウンタ付きの一意IDで追跡。全体リライトではなく差分更新で Context Collapse を防ぐ
- **`<important if>` 条件タグ**: 条件が現在のタスクにマッチする場合のみ Claude がそのセクションを重視するタグ。ファイルが長くなるほど個別セクションが「任意」扱いされる問題への対処
- **指示バジェット**: 約 150〜200 指示で遵守率が均一に劣化する。system prompt で既に約 50 消費済みのため実質的な余裕は限られる
- **hooks は deterministic、CLAUDE.md は advisory**: 確実に実行すべきルールは hook 化すべきであり、CLAUDE.md は判断ガイダンスとして機能する
- **5層コンテキスト収集**: L0（永続メモリ）→ L1（Grep/Glob）→ L2a（コールグラフ）→ L2b（Wikiliink グラフ）→ L3（セマンティック検索）の段階的収集が盲目的コード変更を防ぐ
- **Temporal Decay**: `exp(-0.1 × days)` でコンテキストの鮮度を自動管理（7日で 49.7%、30日で 5% に減衰）
- **コードベース概要は無効**: AGENTS.md にファイルツリーを含めても関連ファイルへの到達ステップ数に有意差がない（ETH Zurich 実証）
- **既存ドキュメントとの冗長排除**: docs が存在する場合、LLM 生成 CLAUDE.md は開発者記述を -2.7% 下回る。Documentation = Infrastructure 原則が重要
- **Task-Scoped Context Injection**: コンテキストを常時全量注入するのではなく、タスクのスコープに応じて必要な範囲だけを注入する原則。過剰注入によるノイズと指示バジェットの浪費を防ぐ
- **Filesystem as Context Engineering**: スキルはプロンプト本文に情報を詰め込む代わりに、ファイルシステム自体（scripts/config/logs）をコンテキスト管理の基盤として使える。プロンプトは「何をするか」、ファイルシステムは「状態と詳細」を担う分離
- **Reasoning Sandwich**: 推論ステージごとに配分を変える（plan=high、build=reduced、verify=high）方が全ステージ max より高精度になる。LangChain Terminal Bench 2.0 実測で 66.5%（Sandwich）対 53.9%（全段 max）
- **WebFetch 内部要約による Silent Truncation**: WebFetch は取得コンテンツを内部で Haiku が要約してからモデルに渡すため、信頼済みドメイン以外では表示上の受信バイト数と実際にモデルが読む内容が乖離しうる。取得できた=読めた、ではない
- **出力フォーマットの Re-ingest Tax**: HTML など高密度フォーマットへの最適化は、後続エージェントが再度読み込む際のトークンコストを 1.3〜1.8 倍に増やす。version control diff・grep・memory 索引を重視する用途では markdown が既定であるべき

## 実践的な適用

dotfiles の CLAUDE.md は `<important if>` 条件タグを 6 セクションに適用し、関連タスクのときのみ該当指示が活性化する設計になっている。Progressive Disclosure（CLAUDE.md → references/ → rules/）でコンテキスト密度を制御し、詳細は分離ファイルに委譲する。hook 体系（completion-gate、golden-check など）が deterministic なルールを担い、CLAUDE.md は advisory な指示のみを持つ明確な役割分担がある。ACE の Incremental Delta Updates に相当する実装として、メモリファイルを bullet 単位で管理し、MEMORY.md を要約＋パス参照のみに保つ方針を採っている。Temporal Decay は現在 Gap として認識されており、手動での「古い→削除」からスコアベースの自動減衰への移行が課題である。

## 関連概念

- [agent-memory](agent-memory.md) — エージェントのメモリ層とコンテキストの永続化
- [context-management](context-management.md) — コンテキスト圧縮とウィンドウ管理
- [claude-code-architecture](claude-code-architecture.md) — Claude Code のシステム構造とコンテキストフロー

## ソース

- [ACE: Agentic Context Engineering Analysis](../../research/2026-03-24-ace-agentic-context-engineering-analysis.md) — ICLR 2026 採録。Brevity Bias・Context Collapse の定義とインクリメンタルデルタ更新手法
- [Important-If Conditional Tags Analysis](../../research/2026-03-19-important-if-conditional-tags-analysis.md) — `<important if>` タグによる指示遵守率向上と指示バジェットの制約
- [Context and Impact Analysis](../../research/2026-03-25-context-and-impact-analysis.md) — 5層コンテキスト収集・Temporal Decay・Ensemble Quality Gate を含む包括的パイプライン
- [Evaluating AGENTS.md Analysis](../../research/2026-03-18-evaluating-agentsmd-analysis.md) — ETH Zurich による大規模実証。LLM 生成 vs 人間記述のコンテキストファイル性能比較
- [Harnesses Are Everything (2026-04)](../../research/2026-04-19-harness-everything-absorb-analysis.md) — **instruction budget の真の総量** = CLAUDE.md 本文 + hook 注入 + description + MCP tool 定義。Stanford "Lost in the Middle" 研究が裏付け: 2000 トークン超で指示遵守率 20-30% 低下。**Progressive Disclosure** (lean .md → references → rules) で常時露出を最小化し、dumb zone を回避する。
- [Claude Code Harness Blueprint (leaked CC internals)](../../research/2026-04-08-cc-harness-blueprint-analysis.md) — CC内部4層設計を分析、7項目をharnessに統合済み
- [Single-Agent vs Multi-Agent Thinking Budget (Stanford, arXiv:2604.02460)](../../research/2026-04-08-sas-vs-mas-thinking-budget-analysis.md) — SAS対MAS論文を分析、委譲判断基準にDPI根拠明文化を提案
- [12 Claude Patterns You've Never Tried (@sharbel)](../../research/2026-04-09-12-claude-patterns-analysis.md) — Claude活用12パターンを分析、全項目を既存スキル強化に統合
- [30 Claude Prompts, Workflows & Automations (@eng_khairallah1)](../../research/2026-04-09-30-claude-prompts-analysis.md) — 実務プロンプト30選を分析、決定ジャーナルなど9タスク採用
- [PostHog『The golden rules of agent-first product engineering』(Jina Yoon) 分析](../../research/2026-04-11-posthog-agent-first-rules-analysis.md) — PostHog記事、wrapper境界文書化とfriction→evalループを採用
- [Skills for Claude Code: The Ultimate Guide (Anthropic Engineer, Medium) 分析](../../research/2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md) — Anthropicエンジニア記事、config.json標準とGotchas監査を追加実装
- [Claude Codeセッション管理と1Mコンテキスト記事 (Anthropic Applied AI) 分析](../../research/2026-04-17-claude-code-session-mgmt-analysis.md) — Claude Code公式1Mコンテキスト記事分析、Rewind等6項目を全採用
- [コンテキストデザイン組織活用記事 (久保星哉) 分析](../../research/2026-04-17-context-design-absorb-analysis.md) — コンテキストデザイン記事分析、MCP分散とTelemetry品質を最優先Gapと特定
- [Obsidian × Claude Code — .claude ディレクトリ設計パターン (@akira_papa_AI)](../../research/2026-04-21-obsidian-claudecode-absorb-analysis.md) — Obsidianのcommands/skills設計を分析、Inbox連携等5タスクを採用
- [A good AGENTS.md is a model upgrade (Slava Zhenylenko, Augment)](../../research/2026-04-23-agents-md-patterns-absorb-analysis.md) — AGENTS.md記事分析、sprawl監査等7タスク採用(module化棄却)
- [claudecode-harness — Team Claude Code Harness Template (anothervibecoder-s)](../../research/2026-04-23-team-harness-template-analysis.md) — チームharnessテンプレ記事を分析、team-project雛形一式を新設
- [A Closer Look at Harness Engineering from Top AI Companies (AlphaSignal)](../../research/2026-04-24-harness-engineering-absorb-analysis.md) — Harness Engineering記事分析、reasoning budget表等3タスクを追記
- [graphify (知識グラフ変換ツール) absorb分析](../../research/2026-04-27-graphify-absorb-analysis.md) — 知識グラフツールgraphifyを分析、本体棄却し3件軽量採用
- [Subagent Context Fork absorb分析 (aitmpl系記事)](../../research/2026-04-27-subagent-context-fork-absorb-analysis.md) — Subagent context fork記事を分析、fork機能非採用・観測3件採用
- [What to Learn, Build, and Skip in AI Agents (2026) absorb分析](../../research/2026-04-30-learn-build-skip-2026-absorb-analysis.md) — AIエージェント要点記事を分析、機会費用フィルター1件のみ採用
- [Claude Code Overhead 9 Patterns absorb分析](../../research/2026-05-04-claude-code-overhead-9patterns-absorb-analysis.md) — Claude Codeオーバーヘッド9パターンを分析、skill tax削減等5件採用
- [SessionStart Hook監査レポート (absorb 9patterns T2)](../../research/2026-05-04-sessionstart-audit.md) — SessionStartフック6個を実測監査、latency 71%削減実施
- [WebFetch内部Haiku要約問題 absorb分析 (著者: sherry)](../../research/2026-05-06-webfetch-haiku-summary-absorb-analysis.md) — WebFetch内部Haiku要約の盲点を分析、decision table等8件全採用
- [The Unreasonable Effectiveness of HTML absorb分析 (Thariq Shihipar)](../../research/2026-05-09-html-effectiveness-absorb-analysis.md) — HTML出力最大化論を分析、全面採用棄却し決定表2件採用
- [SocratiCode codebase intelligence MCP](../../research/2026-05-17-socraticode-absorb-analysis.md) — codebase intelligence MCPを比較検証、循環依存記録のみ採用
- [Codex Research Agent Workflow (中国語記事、10分構築)](../../research/2026-05-28-codex-research-agent-workflow-absorb-analysis.md) — 朝ブリーフ記事、注釈欄と週次差分提案など3件採用
- [Claude Code Harness (Chachamaru127、契約駆動デリバリ)](../../research/2026-05-30-claude-code-harness-absorb-analysis.md) — 契約駆動ハーネス記事と比較、退役概念追跡等4件採用
- [Hermes Harness Architecture (NousResearch)](../../research/2026-05-30-hermes-harness-architecture-absorb-analysis.md) — Hermesハーネス記事、cwd設定ファイルのinjection対策のみ採用
- [The Claude Opus 4.8 Setup Guide (zodchixquant)](../../research/2026-05-30-opus48-setup-guide-absorb-analysis.md) — Opus4.8設定ガイド記事、Fast Mode指針採用・誤情報2件検出
- [32 Claude Code hacks (movez.substack)](../../research/2026-05-31-32-claude-code-hacks-absorb-analysis.md) — 32個のCC hacks記事、ultracode表記追記のみ採用
- [agents-best-practices (provider-neutral Agent Skill) (DenisSergeevitch)](../../research/2026-06-02-agents-best-practices-absorb-analysis.md) — provider-neutral harness skillを分析、8原則は全Already、reference扱いで不採用
- [movez「Claudeの14ステップ活用法」](../../research/2026-06-02-how-to-actually-use-claude-14-steps-absorb-analysis.md) — Claude活用14ステップ記事、既存判断で全手法カバー済み・採用0件
- [MUSE-Autoskill: Self-Evolving Agents via Skill Lifecycle](../../research/2026-06-05-muse-autoskill-self-evolving-agents-absorb-analysis.md) — MUSE論文のスキル生涯管理を分析、per-skill memoryなど新規性ゼロ採用0件
