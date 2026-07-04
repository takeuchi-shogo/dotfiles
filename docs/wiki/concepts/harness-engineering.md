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
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 38
confidence: established
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
- **「存在チェック」ではなく「機能チェック」**: ハーネスの構成要素は実装の有無だけでなく実際に機能しているかで評価すべきという視点。存在するが機能していない仕組み（Self-Improving loop や Meta-Harness など）は、存在チェックだけでは見逃される
- **Hook Enforcement の3分類**: deterministic block（機械的に強制）/ semantic advisory（助言のみ）/ human judgment（人間の判断に委ねる）。「static-checkable rules は mechanism に寄せる」原則と「Hard enforcement を避ける」設計哲学の緊張関係を、この3分類で裁定する
- **stdout/stderr の役割分離**: hook の出力のうち context window（cache prefix）に流入するのは stdout のみで、stderr は UI 表示専用でキャッシュに影響しない。この区別に基づく並列化・出力削減により、SessionStart hook 群の合計 latency を 3.20 秒 → 0.92 秒（71%削減）まで圧縮できた実測例がある

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
- [Claude Code Harness Blueprint (leaked CC internals)](../../research/2026-04-08-cc-harness-blueprint-analysis.md) — CC内部4層設計を分析、7項目をharnessに統合済み
- [The Great Convergence (harness市場分析、元Cruiseエンジニア)](../../research/2026-04-09-great-convergence-analysis.md) — 汎用ハーネス収束論を分析、存在≠機能の検証課題を抽出
- [Claude Code from Source 全18章リバースエンジニアリング分析](../../research/2026-04-10-claude-code-from-source-analysis.md) — CC全18章を分析、Tier1/2統合しTier3は記録のみ
- [Claude Code from Source /absorb統合実行レポート](../../research/2026-04-10-claude-code-from-source-integration-report.md) — CCソース分析の統合実行、7ファイル編集+3新規作成完了
- [Garry Tan『Thin Harness, Fat Skills』分析](../../research/2026-04-12-tan-thin-harness-fat-skills-analysis.md) — Tan「Thin Harness Fat Skills」分析、Invocation Pattern等3件を新規実装
- [Hermesパーソナルアナリスト活用体験記分析](../../research/2026-04-14-hermes-personal-analyst-analysis.md) — Hermesアナリスト記事分析、大半既存資産で充足、情報源拡張のみ追加
- [Karpathy Skills (andrej-karpathy-skills)](../../research/2026-04-20-karpathy-skills-absorb-analysis.md) — Karpathyコーディング原則記事を分析、4原則は実装済・ADR等4タスク追加
- [claudecode-harness — Team Claude Code Harness Template](../../research/2026-04-23-team-harness-template-analysis.md) — チームharnessテンプレ記事を分析、team-project雛形一式を新設
- [A Closer Look at Harness Engineering from Top AI Companies (AlphaSignal)](../../research/2026-04-24-harness-engineering-absorb-analysis.md) — Harness Engineering記事分析、reasoning budget表等3タスクを追記
- [Codex CLI を Claude Code 並みに最適化 absorb分析](../../research/2026-04-27-codex-claude-parity-absorb-analysis.md) — Codex最適化4項目を分析、agents/MCP同期等6件採用
- [Boris の30 Tips完全版 absorb分析](../../research/2026-04-30-boris-30tips-absorb-analysis.md) — Boris 30 Tipsを分析、hook監視等4件を既存に軽量追記
- [Claude API skill 4社展開 absorb分析](../../research/2026-04-30-claude-api-skill-absorb-analysis.md) — Anthropic公式アナウンス記事を分析、採用0件で全項目Already
- [Continually Improving Cursor's Agent Harness absorb分析](../../research/2026-04-30-cursor-harness-absorb-analysis.md) — Cursorハーネス改善記事を分析、11手法全て既存カバーで採用0件
- [Claude Code Overhead 9 Patterns absorb分析](../../research/2026-05-04-claude-code-overhead-9patterns-absorb-analysis.md) — Claude Codeオーバーヘッド9パターンを分析、skill tax削減等5件採用
- [SessionStart Hook監査レポート](../../research/2026-05-04-sessionstart-audit.md) — SessionStartフック6個を実測監査、latency 71%削減実施
- [15 Claude Code Settings Most Developers Never Touch](../../research/2026-05-10-zodchixquant-15-settings-absorb-analysis.md) — 15設定記事を検証、xhigh設定済み確認・thinking summary運用化
- [Claude Code in Large Codebases: Best Practices (Anthropic公式)](../../research/2026-05-20-claude-code-large-codebase-absorb-analysis.md) — 大規模コードベース記事は既存実装で全カバー、新規採用なし
- [OpenClaw autoreview SKILL.md (Peter Steinberger)](../../research/2026-05-28-openclaw-autoreview-absorb-analysis.md) — 自動コードレビュー記事、PASS後再レビュー禁止等5件採用4件保留
- [14 Claude Code sub-agents, 4 survived](../../research/2026-05-30-14-subagents-4-survived-absorb-analysis.md) — 60日14サブエージェント実験記事、アンチパターン等軽微採用
- [Claude Code Harness (Chachamaru127、契約駆動デリバリ)](../../research/2026-05-30-claude-code-harness-absorb-analysis.md) — 契約駆動ハーネス記事と比較、退役概念追跡等4件採用
- [Hermes Harness Architecture (NousResearch)](../../research/2026-05-30-hermes-harness-architecture-absorb-analysis.md) — Hermesハーネス記事、cwd設定ファイルのinjection対策のみ採用
- [4-Agent Pipeline (zodchixquant)](../../research/2026-05-31-4-agent-pipeline-absorb-analysis.md) — 4エージェント固定パイプラインを分析、Tester境界1件のみ採用しほぼ不採用
- [How To Fix AI Slop (Using Hermes)](../../research/2026-05-31-hermes-ai-slop-eval-loop-absorb-analysis.md) — Hermesのeval loop提案を分析、既存基盤が上回り自動closeループ不採用
- [Zero Trust for AI Agents (Anthropic eBook)](../../research/2026-05-31-zero-trust-ai-agents-absorb-analysis.md) — Zero Trust eBookを分析、暗号ID等はN/A、Agent-BOM-lite等3件をL規模で全採用
- [agents-best-practices (DenisSergeevitch)](../../research/2026-06-02-agents-best-practices-absorb-analysis.md) — provider-neutral harness skillを分析、8原則は全Already、reference扱いで不採用
- [6 Workflows, 6 Lessons, 60 Days with Hermes Analyst](../../research/2026-06-02-hermes-60-days-6-lessons-absorb-analysis.md) — Hermes運用60日記事を分析、echo chamber対策を昇格ループ設計ノートに追記採用
- [私の最強のMac開発環境2026 (tyPhoon)](../../research/2026-06-02-typhoon-nix-mise-absorb-analysis.md) — Nix+mise記事を検証、mise未活用のランタイム二重管理事故を発見し統合
- [A harness for every task: dynamic workflows in Claude Code](../../research/2026-06-03-dynamic-workflows-absorb-analysis.md) — Workflow tool記事分析、意図的不採用維持・リンク切れ2件修正
- [Karpathy 24-rule CLAUDE.md ($147K記事)](../../research/2026-06-07-karpathy-147k-claudemd-absorb-analysis.md) — Karpathy記事は全rehash、監査でNO-OPフック等15件のharness欠陥を発見修正
- [Vercel eve Agent Framework absorb分析](../../research/2026-06-18-vercel-eve-agent-framework-absorb-analysis.md) — Vercel eveは機能面で採用0だが設計思想からgate数drift検出を導入
- [Anthropic knowledge-work-plugins (Cowork公式)](../../research/2026-06-20-knowledge-work-plugins-absorb-analysis.md) — Cowork職務別プラグイン集は開発ハーネスとscope不一致、採用0

## Related External Insights

- **[CREAO AI-First Strategy (2026-04)](../../research/2026-04-14-creao-ai-first-analysis.md)**: harness engineering を「エージェント有効化」と再定義し、抽象原理 4 つ (観測可能化 / 判断ゲート化 / 批評を成果物に / 失敗→capability gap→durable artifact) に集約。個人 dotfiles 文脈では企業儀式を棄却し抽象原理のみ採用。
- **[Harnesses Are Everything (2026-04)](../../research/2026-04-19-harness-everything-absorb-analysis.md)**: lean .md files + R.P.I (Research→Plan→Implement) + subagents の3サーフェス設計で品質差異を最大化。**instruction budget** 概念 — CLAUDE.md 本文行数だけでなく hook 注入・description・MCP tool 定義を含む「常時露出総量」を計測・管理する。**Progressive Disclosure** (CLAUDE.md → references → rules) で指示を段階的に開示しdumb zone（指示過多による判断能力低下）を回避。**R.P.I framework** は dotfiles の `/spec`→`/spike`→`/validate`→`/epd` フローと対応。**Reviewer Calibration** — レビューアーの TPR/TNR を JSONL で追跡し「レビューが効いているか」を定量化する。**Harness Stability** — ハーネス要素の削除は 30 日評価後（`references/harness-stability.md`）。
- **[Claude Code Harness Blueprint (2026-04-08)](../../research/2026-04-08-cc-harness-blueprint-analysis.md)**: リーク版 CC ソース（v2.1.88）を Model Weights/Context/Harness/Infrastructure の4層で捉え直す。Codex 批評「implementation inaccessible ≠ design principle inapplicable」（実装に触れられないことと設計原則として学べないことは別）が、ソースを直接読めない対象からも設計知を抽出できる根拠となった。
- **[Fat Skills, Thin Harness, Dumb Tools (2026-04-12, Garry Tan)](../../research/2026-04-12-tan-thin-harness-fat-skills-analysis.md)**: 知性は Skill に集中させ、Harness は薄く、Tool は単機能に保つ3層設計原則。5つの構成柱のうちツールオーケストレーションを具体化する。**Invert Test**（skill が反対の結論も導けるか自己検証）と **Negative Routing**（衝突時に skill を使わない条件を明示）を新規採用した。
- **[Karpathy 4原則と Hook Philosophy (2026-04-20)](../../research/2026-04-20-karpathy-skills-absorb-analysis.md)**: LLM の4大失敗パターン対策は soft instruction に留め hard enforcement を避けるべきという哲学。既存 hook の多用との緊張関係を、deterministic block / semantic advisory / human judgment の3分類 ADR で整理した。
- **[Zero Trust for AI Agents (2026-05-31, Anthropic eBook)](../../research/2026-05-31-zero-trust-ai-agents-absorb-analysis.md)**: 暗号ID/mTLS/SOAR 等のインフラ層は単一ユーザーハーネスには N/A だが、「Least Agency」原則と8-phase デプロイライフサイクルは個人ハーネス向けに翻訳可能（Agent-BOM-lite・why observability として具体化）。「技術名が N/A でも設計原則まで N/A にしない」という enterprise→個人 absorb の教訓を残した。
- **[Karpathy 24-rule CLAUDE.md 監査追跡 (2026-06-07)](../../research/2026-06-07-karpathy-147k-claudemd-absorb-analysis.md)**: 記事自体は既存の完全 rehash（採用0）だが、24原則を adversarial lens として既存ハーネスを監査すると、2ヶ月間発火しなかった NO-OP フック2件・symlink 起因のトークン過小計上・`--no-verify` bypass 経路を file:line 単位で発見できた。「記事からの採用0 ≠ 監査に価値なし」を実証した事例。
