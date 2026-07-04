---
title: エージェントセキュリティ
topics: [security]
sources: [2026-03-25-3-layer-prompt-injection-defense-analysis.md, 2026-03-23-verigrey-greybox-agent-validation-analysis.md, 2026-04-02-ai-agent-traps-analysis.md, 2026-03-18-scientist-ai-bengio-analysis.md, 2026-04-04-agentwatcher-rule-based-injection-monitor-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 22
confidence: established
---

# エージェントセキュリティ

## 概要

エージェントセキュリティは、自律型 AI エージェントが外部コンテンツ（Web・MCP・外部リポジトリ）を取り込む際に生じる攻撃面（Agent Traps）への対策体系である。LLM に「気をつけて」と指示するのではなく、LLM の外側にある実行境界（Hooks）で攻撃を止める設計思想が基本となる。エージェントの機能アーキテクチャに応じた 6 カテゴリ・22 攻撃ベクトルの体系的分類が、防御設計の出発点となる。

## 主要な知見

- **3 層 Hook 防御**: UserPromptSubmit（入力検査）→ PreToolUse（実行前ブロック、主軸）→ PostToolUse（出力監視）の 3 層構造で多層防御を実現する
- **Agent Traps の 6 カテゴリ**: Content Injection（知覚）/ Semantic Manipulation（推論）/ Cognitive State（記憶）/ Behavioural Control（行動）/ Systemic（マルチエージェント）/ Human-in-the-Loop（人間監視者）の 6 層が攻撃面となる
- **コンテキストブリッジング攻撃**: 悪意あるタスクをユーザーの本来タスクに自然言語で文脈接続する攻撃が、技術的パターン検出だけでは検知できない。VeriGrey でブラックボックス比較対比 +33pp の検出率向上を実証
- **Latent Memory Poisoning**: 内部メモリへの 0.1% 未満の汚染でも 80% 超の攻撃成功率。長期メモリシステムは特に慎重な設計が必要
- **Data Exfiltration Traps**: confused deputy 攻撃による機密漏洩成功率 80% 超。機密ファイルアクセスは hook レベルで検出・ブロックする
- **Dual-mode 検査**: raw テキスト + sanitized テキスト（クォート/heredoc 除去）の両方で OR 判定することで、難読化回避を防ぐ
- **fail-closed 設計**: フック異常時もブロックを維持する。フックがサイレント失敗してもエージェントが続行しない設計が必須
- **3 段階デプロイ**: audit（ログのみ）→ warn（警告）→ block（ブロック）の段階的投入で運用リスクを最小化する
- **Task-scoped Tool Filter**: タスク文脈に応じた動的ホワイトリストが最も ITSR（侵入タスク成功率）を下げつつ UTSR（通常タスク成功率）への影響が最小の防御策
- **Specification gaming 検出**: エージェントがメトリクスをハックする問題（Goodhart's Law 増幅）は、Gaming Detector と多目的バリデーションゲートで対処する
- **ルールベース検出 (AgentWatcher)**: 10 種攻撃ルール（R1-R10: 命令ハイジャック〜システムスプーフィング）+ 4 種ベナインルール（B1-B4: 偽陽性抑制）の体系的分類により、検出の説明可能性と保守性が向上する。ルール分類: `references/injection-rule-taxonomy.md`
- **Context Attribution の原則**: 検出対象を因果的に重要なコンテキスト断片に絞ることで、長文でも精度を維持できる。API 環境では「直近コンテキスト優先」「ツール出力境界重点チェック」「長文時の分割スキャン」で代替する
- **ベナインルールの重要性**: 「何が攻撃か」だけでなく「何が正常か」を明示的に定義することで、ツール使用エージェント環境での偽陽性を抑制する
- **cwd コンテキストファイルの injection スキャン**: `CLAUDE.md`/`AGENTS.md`/`.cursorrules` 等プロジェクト root のファイルは trusted 前提で見落とされがちだが、untrusted repo に `cd` するとエージェントが自動読込する経路が残る。SessionStart 時に zero-width unicode・ANSI escape・Trojan Source (U+202E RTL override, CVE-2021-42574) 等の難読化シグナルを検出し warn-only で警告する `[EXTRACTED, conf=85]`
- **secret 監査は共有メモリ・ログ層にも及ぶ**: エージェント間で共有するメモリ・JSONL ログは `sk-`/`ghp_`/`Bearer` 等の secret が素通りしやすい。書き込み前の redactor 統合と schema/retention 方針の策定が必要 `[EXTRACTED, conf=80]`
- **要約層自体が injection 表面になる**: WebFetch 等の内部処理で LLM がコンテンツを中間要約してから上位モデルに渡す設計では、要約担当モデルが上位モデル到達前に prompt injection を受ける経路が生まれる。生取得（raw fetch）と要約は責務を分離し、要約は呼び出し側に委ねるべき `[EXTRACTED, conf=70]`
- **high-stakes agent への requires-escalation rubric**: 長時間自律実行・merge 判断・routing・completion 判定を担う agent には「MUST escalate / MAY proceed / NEVER do」を明文化した escalation セクションが必要。多くの subagent はこれが体系化されておらず、既存の "Do NOT use for:" (scope creep 防止用) と混同しやすい `[EXTRACTED, conf=75]`
- **操作の信頼ティア (read→destructive)**: ツール表面の信頼性ラダー（file/CLI > MCP > browser > screen automation）とは別に、操作そのものの信頼ティア（read > propose/draft > local write > commit > **external side-effect（送信）** > destructive）を明示する軸が必要。特に外部への送信は独立ティアとして分離すべき `[EXTRACTED, conf=75]`
- **Agent-BOM-lite と why-observability**: enterprise 向け AI-BOM（モデル来歴・supply chain 台帳）は個人 harness には過剰だが、per-session の model/skills/MCP/tools/memory surfaces/repo trust snapshot として個人版に翻訳できる。permission/decision log に `policy_reason`/`revocation_trigger` を持たせ「なぜこの判断か」を可観測にすることが、暗号的な Zero Trust 基盤より高 ROI `[INFERRED, conf=65]`
- **外部 install される skill/subagent への CRITICAL-only injection scan**: 第三者提供の skill/agent を取り込む経路には injection scan を配線すべきだが、既存スキャナーは HIGH レベルで false positive が多発しやすい（正当な `proactively` 等の文言を誤検知）。gate 化は CRITICAL のみをブロック対象にすることで、正規 install を止めずに実害だけ遮断できる `[EXTRACTED, conf=80]`
- **PUBLIC リポジトリの CI 上のエージェントは別 trust domain**: GitHub Actions 等で動くエージェントは、第三者が Issue を開くだけでトリガーされ API 消費や実行主体になりうる。job-level の author guard（`OWNER`/`MEMBER`/`COLLABORATOR` 限定）と、secret を扱う job での依存バージョン pinning（supply chain 対策）が必須 `[EXTRACTED, conf=80]`

## 実践的な適用

dotfiles では `prompt-injection-detector.py`（PreToolUse）が技術的パターン検出を担い、`mcp-audit.py` が MCP サーバーの入力監査を行う。`/security-review` スキルと `security-reviewer` エージェントが OWASP Top 10 準拠の検査を実行する。`settings.json` の deny rules で危険コマンド（curl|bash・rm -rf 等）を常時ブロックし、`/careful` スキルがオプトインで追加保護を提供する。`security-scan` スキルが AgentShield 経由でエージェント固有の脆弱性を検出する。加えて、`scan-context-files.py`（SessionStart）が cwd の CLAUDE.md/AGENTS.md 等の難読化系 injection を検出し、`skill-security-scan.py --critical-only` が外部 install スキルの CRITICAL 脅威のみを gate し、`session-bom.py` が Agent-BOM-lite を per-session に記録する。GitHub Actions 上の agent-triage.yml は job-level author guard（`OWNER`/`MEMBER`/`COLLABORATOR`）でトリガー主体を制限する。

## 関連概念

- [adversarial-evaluation](adversarial-evaluation.md) — VeriGrey 等のグレーボックスファジングによる脆弱性発見手法
- [harness-engineering](harness-engineering.md) — セキュリティ防御を実装するハーネス設計の基盤
- [quality-gates](quality-gates.md) — セキュリティチェックを品質ゲートに統合するパターン

## ソース

- [3 層プロンプトインジェクション対策](../../research/2026-03-25-3-layer-prompt-injection-defense-analysis.md) — Hook ベースの 3 層防御・Dual-mode 検査・fail-closed・3 段階デプロイの実装ガイド
- [VeriGrey: Greybox Agent Validation](../../research/2026-03-23-verigrey-greybox-agent-validation-analysis.md) — ツール呼び出しシーケンスをカバレッジ指標としたグレーボックスファジングによる間接インジェクション脆弱性発見
- [AI Agent Traps](../../research/2026-04-02-ai-agent-traps-analysis.md) — Web 環境の攻撃面を 6 カテゴリ・22 ベクトルで体系化した DeepMind 論文
- [Scientist AI](../../research/2026-03-18-scientist-ai-bengio-analysis.md) — 知能と行為主体性の分離・Specification gaming 検出・Agency 3 本柱モデルのセキュリティ原則
- [AgentWatcher](../../research/2026-04-04-agentwatcher-rule-based-injection-monitor-analysis.md) — Context Attribution + 10 種ルール分類によるスケーラブルで説明可能なインジェクション検出
- [I Want to Extend My Claude Sessions (NotebookLM統合ガイド)](../../research/2026-04-10-notebooklm-claude-extend-sessions-analysis.md) — NotebookLM連携記事を分析、DBS rubricのみ採用
- [PostHogの golden rules of agent-first product engineering (Jina Yoon)](../../research/2026-04-11-posthog-agent-first-rules-analysis.md) — wrapper境界文書化とfriction→evalループを採用
- [コンテキストデザイン組織活用記事 (久保星哉)](../../research/2026-04-17-context-design-absorb-analysis.md) — MCP分散とTelemetry品質を最優先Gapと特定
- [Hermes Fleet共有メモリ構築記事 (Weekend blog, Moshe再現)](../../research/2026-04-17-hermes-fleet-shared-memory-analysis.md) — secret監査を含む4件採用、Qdrant/mem0導入は見送り
- [GitHub CLI gh skill コマンド changelog 分析](../../research/2026-04-19-gh-skill-cli-analysis.md) — provenance追記等7項目を採用
- [claudecode-harness — Team Claude Code Harness Template](../../research/2026-04-23-team-harness-template-analysis.md) — team-project雛形一式を新設
- [google/skills + ADK 2.0 Multi-Agent Orchestration Patterns](../../research/2026-04-24-google-skills-adk2-absorb-analysis.md) — google/skills 13個を全採択
- [WebFetch内部Haiku要約問題 absorb分析 (sherry)](../../research/2026-05-06-webfetch-haiku-summary-absorb-analysis.md) — 要約層のinjection表面など8件を全採用
- [Agent Governance Layers (@techwith_ram)](../../research/2026-05-17-agent-governance-layers-absorb-analysis.md) — 5層Governanceモデルからescalation rubricのみ採用
- [7-agent Software Factory (Sai Rahul)](../../research/2026-05-27-sairahul-7agent-software-factory-absorb-analysis.md) — 前提不一致で不採用
- [Hermes Harness Architecture (NousResearch)](../../research/2026-05-30-hermes-harness-architecture-absorb-analysis.md) — cwd設定ファイルのinjection対策のみ採用
- [Cursor Auto Review 実行モード](../../research/2026-05-31-cursor-auto-review-run-mode-absorb-analysis.md) — LLM分類器は意図的不採用、監査のみ実施
- [My Agent Stack For Automating My Personal Life (Nicolas Bustamante)](../../research/2026-05-31-personal-agent-stack-absorb-analysis.md) — ツール信頼性ラダーと操作信頼ティアの2軸を採用
- [Zero Trust for AI Agents (Anthropic eBook)](../../research/2026-05-31-zero-trust-ai-agents-absorb-analysis.md) — Agent-BOM-lite等3件をL規模で全採用
- [When AI builds itself (Anthropic Institute) recursive self-improvement](../../research/2026-06-05-recursive-self-improvement-anthropic-absorb-analysis.md) — 判断計測とメタ安全層3件を採用
- [How to Build Claude Subagents Better Than 99% of People (Jey)](../../research/2026-06-20-jey-build-claude-subagents-absorb-analysis.md) — YAML検証とCRITICAL-only injectionスキャン配線の2件を採用
- [IssueOps: Automate CI/CD with GitHub Issues and Actions (GitHub Engineering)](../../research/2026-06-30-issueops-absorb-analysis.md) — author guard・バージョンpin等3件を実装
