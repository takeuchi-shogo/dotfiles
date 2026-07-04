---
title: エージェントメモリ
topics: [memory]
sources: [2026-04-02-cc-7-layer-memory-architecture-analysis.md, 2026-04-02-claude-code-memory-internals-analysis.md, 2026-03-30-agent-memory-quality-guide-analysis.md, 2026-03-30-ai-agent-memory-types-analysis.md, 2026-04-05-claude-code-3-memory-systems-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 26
confidence: established
---

# エージェントメモリ

## 概要

エージェントメモリとは、有限なコンテキストウィンドウを持つ LLM が複数セッションにわたって知識・経験・手続きを蓄積・参照するための仕組みである。Claude Code は 7 層のメモリアーキテクチャを実装しており、安価な層（Tool Result Storage・Microcompaction）が高価な層（Full Compaction・Dreaming）の発動を防ぐ「Layered Defense, Cheapest First」原則で設計されている。メモリの質については「エージェントメモリの 84% は操作テレメトリ（ノイズ）である」という実践的知見があり、品質ゲート付きの構造化管理が不可欠である。

## 主要な知見

- **7 層防衛（Claude Code 内部）**: Tool Result Storage → Microcompaction（3 種）→ Session Memory → Full Compaction → Auto Memory Extraction → Dreaming → Cross-Agent Communication の順で段階的にコストが上がる
- **4 タイプのメモリ**: Short-term（作業デスク）/ Episodic（日記・失敗記録）/ Semantic（知識ベース）/ Procedural（筋肉記憶）の認知科学的分類が有効
- **Dreaming（クロスセッション統合）**: Orient→Gather→Consolidate→Prune の 4 フェーズで複数セッションの知識を統合。PID ロックと 10 分スロットルで安全性を担保
- **ハードキャップ**: MEMORY.md は 200 行 / 25KB、メモリファイルは 200 個、セッションあたり約 26K トークン（200K の 13%）をメモリが消費する構造的制約がある
- **サイレント失敗のリスク**: Sonnet の Semantic Recall は失敗時に `return []` を返し、`ensureMemoryDirExists` は EACCES/ENOSPC をサイレントに飲む。外部監視が必要
- **5 段階 Promotion Ladder**: draft → candidate → promoted → benchmark_grounded → realworld_validated の段階的昇格で品質を保証する
- **Doctrine Synthesis**: 3 つ以上のパケットが同タグを持つと meta-doctrine として自動合成。断片的知識を体系的原則に昇格させる
- **3 層品質ティア**: Operational(LOW) / Behavioral(MEDIUM) / Cognitive(HIGH)。HIGH ティアのみが意思決定に直接影響する
- **Prompt Cache Preservation**: byte-identical prefix の維持がキャッシュヒット（$0.003）とミス（$0.60）の 200 倍コスト差を生む。メモリ変更はキャッシュ破壊コストを意識する
- **Verification Status ラベル**: メモリエントリに `verified` / `hypothesis` / `stale` / `retracted` の検証状態を付与する設計（値の欠落時は `hypothesis` 扱い）。ベンチマーク数値そのものが未検証でも、その背後にある構造的知見（分類の価値）は別軸として採用できるという「数値と概念を分離して評価する」原則を伴う
- **Usage-based メモリ重み付け**: Vector/Graph DB のフルスタック導入は個人規模では固定運用コスト（embedding 再計算・スキーマ管理）が改善幅を上回りやすく見送られやすいが、使用頻度に応じて関連度を動的更新する usage-based edge weight は軽量に実装できる高優先度の強化余地である。また Lost-in-middle 効果（長コンテキスト中央部で精度が約 30% 低下する実証データ）はメモリ retrieval 時の chunk 配置設計に影響する
- **Pruning ロジックと実データ構造の不一致リスク**: 「ファイルの前半＝古い情報」という前提で書かれた圧縮スクリプトを、実際には「前半＝コア恒久知識・後半＝肥大化する索引」という逆構造のファイルに適用すると、signal を捨てて noise を残す逆効果になり得る。原則を codify しても、それを実行する mechanism が hook 等に接続されていなければ機能しないという教訓も伴う
- **Echo Chamber リスク**: 知見を permanent rule へ昇格させるループが importance 順 + 完全一致 dedup のみで動くと、意味的に近い知見の反復昇格や特定スコープへの偏り（monoculture）を抑止できない。多様性チェックや矛盾検出を昇格ゲートに組み込む設計余地がある
- **保存済み信念との矛盾検出**: 新しい発言・決定を過去に保存した仮説・信念と照合し矛盾を検出する仕組みは、反論・盲点の提示（ディベート型の壁打ち）だけでは代替できない独立した検証軸である

## Memory-as-Harness 設計思想

Letta AI の研究は「メモリはハーネスのプラグインではなく、ハーネスのコアそのものである」という重要な転換を提唱している。

従来の設計:
- メモリ = 外部プラグイン（Vector DBなど）としてエージェント外に置く
- コンテキスト管理はモデル任せ

Memory-as-Harness の設計:
- **メモリ管理 = ハーネスの中核責任**。何をロードするか・何が圧縮を生き残るか・何を永続化するかは不可視の意思決定であり、ハーネス側が制御する
- **4分類による保存先決定**: Working（その場で捨てる）/ Procedural（スキル・手順 → 永続化）/ Episodic（失敗記録・判断ログ → 永続化）/ Semantic（知識ベース → 永続化）の区分を compaction survival priorities として明示する
- **Background memory subagents**: セッション中にリアルタイムでメモリを管理する専用サブエージェントをハーネス内に組み込む。メイン LLM とは独立してメモリ整理・退避・gardening を実行する

この設計思想は既存の「7層防衛（Cheapest Layer First）」原則と一致しており、安価な層がメモリ問題を upstream で解決することでコストを抑えるという思想の基盤を補強する。

## 3層メモリシステム（ユーザー視点）

内部の7層アーキテクチャとは別に、ユーザーが操作・管理する3層のメモリシステムが存在する:

1. **CLAUDE.md**（手動管理）— ペルソナ・ルール・プリファレンス。変更頻度は低い
2. **Auto-memory**（自動蓄積）— MEMORY.md インデックス + 個別メモリファイル（user/feedback/project/reference）。Claude が会話中に自動管理
3. **Auto-dream**（自動統合）— 24時間ごとのバックグラウンドプロセス。Orient→Gather→Consolidate→Prune の4フェーズでメモリを統合・剪定

この3層は内部の7層防衛の上位レイヤー（Auto Memory Extraction, Dreaming）に対応する。Auto-dream は `/improve`（AutoEvolve）と補完関係にあり、前者がメモリの剪定・統合、後者が設定・スキルの改善を担当する。

## 実践的な適用

dotfiles のメモリシステムは Short-term を `context-compaction-policy.md` と `/check-context`、Episodic を `lessons-learned.md` + `decision-journal.md` + `/eureka`、Semantic を `MEMORY.md` + `references/` + Knowledge Pyramid（Tier 0〜3）、Procedural をスキル体系 + AutoEvolve + `improve-policy.md` で実装している。MEMORY.md はサマリ＋パス参照のみに保ち、26K トークン上限を意識した軽量構造を採っている。`memory-archive.py` が 500 行超でアーカイブする仕組みは内部ハードキャップ（200 行）の発覚により 180 行閾値への修正が実施済み。`staleness-detector.py` が 30 日未更新メモリファイルを検出し、鮮度管理を自動化している。`references/memory-schema.md` には検証状態フィールド（verified/hypothesis/stale/retracted）が追加済みで、欠落時は hypothesis 扱いとする運用になっている。MEMORY.md は閾値超過時に signal density 原則（thinking ⊃ information の選別、30 秒再取得ルール）に基づき圧縮する運用も実施済み（223 行/48K → 154 行/16K の実例）。

## 関連概念

- [context-management](context-management.md) — コンテキストウィンドウ管理と compaction 戦略
- [context-engineering](context-engineering.md) — コンテキスト構造設計とインクリメンタル更新
- [knowledge-pipeline](knowledge-pipeline.md) — 外部知見の取り込みと内部知識化フロー
- [trajectory-learning](trajectory-learning.md) — 実行軌跡からの知識抽出と昇格ロジック

## 外部比較事例: Hermes Fleet 共有メモリ

Moshe の Hermes setup を再現した週末ブログ記事（2026-04-17 取り込み）は、自己ホスト型の共有メモリ構成を示す外部事例として参考になる。

- **構成**: Qdrant（vector DB）+ Ollama（nomic-embed-text ローカル埋め込み）+ mem0（抽象層）を Claude Code の Stop hook から毎ターン書き込み
- **定性的 gain**: "context switching without re-explanation" — 複数エージェント（Telegram bot + coder）が同一コンテキストを共有する体験
- **実運用 4 本柱**: Redactor（sk-/ghp_/Bearer マスク）・Idempotency key（session_id + turn_index）・Provider pinning（allow_fallbacks: false）・Local fallback（gemma2:9b）
- **dotfiles との差分**: 既存の Stop hook → session-learner.py パイプラインと類似するが、(a) secret redactor が hook 経路に未統合、(b) JSONL での semantic search 不可、(c) memory schema/retention 未明文化 の 3 点がギャップ
- 参照: [Hermes Fleet 共有メモリ分析](../../research/2026-04-17-hermes-fleet-shared-memory-analysis.md) / プラン: [2026-04-17-hermes-absorb-plan.md](../../plans/2026-04-17-hermes-absorb-plan.md)

## ソース

- [CC 7-Layer Memory Architecture Analysis](../../research/2026-04-02-cc-7-layer-memory-architecture-analysis.md) — Claude Code の 7 層メモリ設計と Dreaming・Circuit Breaker の実装詳細
- [Claude Code Memory Internals Analysis](../../research/2026-04-02-claude-code-memory-internals-analysis.md) — 22 ソースファイル分析。200 行キャップ・PID ロック・サイレント失敗等の構造的限界
- [Agent Memory Quality Guide Analysis](../../research/2026-03-30-agent-memory-quality-guide-analysis.md) — 84% ノイズ率・Research Packets・5 段階 Promotion Ladder・Doctrine Synthesis
- [AI Agent Memory Types Analysis](../../research/2026-03-30-ai-agent-memory-types-analysis.md) — Short-term/Episodic/Semantic/Procedural の 4 層モデルと dotfiles 対応表
- [Letta: Memory-as-Harness](../../research/2026-04-04-letta-memory-as-harness-analysis.md) — Memory-as-Harness 設計思想・4分類による compaction survival priorities・Background memory subagents パターン
- [CORAL: Towards Autonomous Multi-Agent Evolution](../../research/2026-04-08-coral-autonomous-multi-agent-evolution-analysis.md) — 自律マルチエージェント進化を分析、heartbeat機構を優先採用
- [Environment-Driven Reinforcement Learning](../../research/2026-04-08-environment-driven-rl-analysis.md) — 環境駆動RL記事を分析、RL基盤をAutoEvolveへ接続採用
- [Obsidian + Claude Code is the New Meta](../../research/2026-04-09-obsidian-claude-code-meta-analysis.md) — Obsidian統合記事を分析、Vault自動メンテナンス等採用
- [Claude Code from Source 設計原則 周辺知見補完](../../research/2026-04-10-claude-code-design-principles-analysis.md) — CC設計原則の業界動向・脆弱性をGemini調査で補完
- [Claude Code from Source 全18章リバースエンジニアリング分析](../../research/2026-04-10-claude-code-from-source-analysis.md) — CC全18章を分析、Tier1/2統合しTier3は記録のみ
- [Claude Code from Source /absorb統合実行レポート](../../research/2026-04-10-claude-code-from-source-integration-report.md) — CCソース分析の統合実行、7ファイル編集+3新規作成完了
- [Build Agents that never forget（Cognee）](../../research/2026-04-14-cognee-agent-memory-analysis.md) — Cognee記事、vector/graph DB導入は見送り、usage-based重み付け等を採用
- [Hermesパーソナルアナリスト活用体験記](../../research/2026-04-14-hermes-personal-analyst-analysis.md) — Hermesアナリスト記事分析、大半既存資産で充足、情報源拡張のみ追加
- [Hermes Fleet共有メモリ構築記事](../../research/2026-04-17-hermes-fleet-shared-memory-analysis.md) — Hermes Fleet記事分析、Qdrant/mem0導入見送り、secret監査等4件採用
- [Obsidian × Claude Code — .claude ディレクトリ設計パターン](../../research/2026-04-21-obsidian-claudecode-absorb-analysis.md) — Obsidianのcommands/skills設計を分析、Inbox連携等5タスクを採用
- [I Tried 100+ Claude Code Skills, These 6 Are Best](../../research/2026-05-06-100-skills-best6-absorb-analysis.md) — 厳選skill 6選記事を分析、Review独立再現フェーズ等5件採用
- [How to Build an Obsidian Knowledge Vault](../../research/2026-05-08-cyril-obsidian-vault-absorb-analysis.md) — Obsidian Vault構築法を分析、矛盾検出等3件のみ採用
- [Codex Research Agent Workflow](../../research/2026-05-28-codex-research-agent-workflow-absorb-analysis.md) — 朝ブリーフ記事、注釈欄と週次差分提案など3件採用
- [Turn Every Note Into Something You Actually Use](../../research/2026-05-30-cyrilxbt-notes-into-output-absorb-analysis.md) — ノート活用術記事、キャプチャ規約と意思決定フィード採用
- [@damidefi Delete 90% of Your Obsidian Notes](../../research/2026-05-31-damidefi-delete-90-vault-absorb-analysis.md) — Vault削除記事のsignal density原則を分析、MEMORY.mdを223→154行に圧縮
- [6 Workflows, 6 Lessons, 60 Days with Hermes Analyst](../../research/2026-06-02-hermes-60-days-6-lessons-absorb-analysis.md) — Hermes運用60日記事を分析、echo chamber対策を昇格ループ設計ノートに追記採用
- [MUSE-Autoskill: Self-Evolving Agents via Skill Lifecycle](../../research/2026-06-05-muse-autoskill-self-evolving-agents-absorb-analysis.md) — MUSE論文のスキル生涯管理を分析、per-skill memoryなど新規性ゼロ採用0件
- [Karpathy 24-rule CLAUDE.md（$147K記事）absorb分析](../../research/2026-06-07-karpathy-147k-claudemd-absorb-analysis.md) — Karpathy記事は全rehash、監査でNO-OPフック等15件のharness欠陥を発見修正
- [Build self-improving agent system with Fable 5 in 14 steps](../../research/2026-06-12-fable5-14steps-absorb-analysis.md) — Fable5自己改善14ステップから検証状態ラベルとモデル安全境界を採用
- [Hermes VPS 24/7 OS Complete Guide](../../research/2026-06-17-hermes-vps-24-7-os-absorb-analysis.md) — Hermes VPS OS運用ガイドは全10手法rehash、採用0確定
- [How to Make Claude's Prompt Update Itself After Every 100 User Decisions](../../research/2026-06-20-anthropic-100-decisions-self-updating-prompt-absorb-analysis.md) — プロンプト自己更新記事は全rehash、月次calibrationも見送り採用0
