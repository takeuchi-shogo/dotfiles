---
title: Claude Codeアーキテクチャ
topics: [claude-code]
sources: [2026-04-01-claude-code-internal-architecture-analysis.md, 2026-03-31-instructkr-claude-code-src-analysis.md, 2026-04-02-harness-wars-begin-analysis.md, 2026-04-04-12-claude-features-top-operators-analysis.md, 2026-04-10-claude-code-from-source-analysis.md, 2026-04-08-cc-harness-blueprint-analysis.md, 2026-04-09-claude-managed-agents-analysis.md, 2026-04-10-claude-code-design-principles-analysis.md, 2026-04-10-claude-code-from-source-integration-report.md, 2026-04-11-claude-only-stack-cyrilxbt-analysis.md, 2026-05-10-zodchixquant-15-settings-absorb-analysis.md, 2026-05-20-claude-code-large-codebase-absorb-analysis.md, 2026-05-30-opus48-setup-guide-absorb-analysis.md, 2026-05-31-32-claude-code-hacks-absorb-analysis.md, 2026-06-02-how-to-actually-use-claude-14-steps-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 14
confidence: established
---

# Claude Codeアーキテクチャ

## 概要

Claude Code（v2.1.88）は約512K行のTypeScriptで実装されたCLIエージェントで、2026年3月末のソースコード公開によりその内部アーキテクチャが参照可能になった。コアはQueryEngine（会話単位のステートフルエンジン）とTool契約システムで構成され、サブエージェント階層・スキルシステム・MCPトランスポート・プラグインマーケットプレイスが統合されている。「Harness Wars」が示すように、CLIはコモディティ化しており真の競争はドメイン固有コンテキストアーキテクチャにある。

## 主要な知見

- **QueryEngine中心設計** — `src/QueryEngine.ts`が会話単位のstateful engine。message history / permission denial / file cache / usageを保持
- **ビルトインエージェント6種** — general-purpose / Explore（Edit/Write禁止, Haiku, **one-shot 135字最適化で週3400万回呼び出し**） / Plan（4ステップ構造化設計, Inherit model） / Verification（常時背景実行, anti-avoidance prompt, read-only） / claude-code-guide（Haiku, Read+Web, SDK 除外時のみ） / statusline-setup（Sonnet, Read+Edit, ステータスライン専用）
- **AgentDefinition統一スキーマ** — `agentType / whenToUse / tools / disallowedTools / model / effort / omitClaudeMd`で定義
- **モデル選定意図** — Explore/claude-code-guide が Haiku なのは「頻度が高く軽量化効果が大きい」から。Plan/Verification が inherit なのは「親の推論水準を継承する必要がある」から。固定ではなく設計上の選択
- **Bubble permission mode** — 7パーミッションモードの最後。サブエージェントは自分の危険操作を承認できず、親ターミナルまで承認要求が bubble up する
- **read-onlyエージェント原則** — 調査系エージェントは`disallowedTools: [Edit, Write, NotebookEdit]` + `omitClaudeMd: true`で権限最小化
- **effortレベル** — `high/medium/low`でAPIコストとレスポンス品質をトレードオフ。エージェント定義に直接指定可能
- **コンパクション** — `src/services/compact/`で自動/リアクティブなセッションメモリコンパクションを実装。Context Compactionへの進化
- **プラグインシステム** — `~/.agents/plugins/`（個人）と`.agents/plugins/`（リポジトリ）の2スコープ。`plugin.json`マニフェスト中心
- **Protocol > Model原則** — 協調プロトコル選択が品質差異の44%を説明、モデル選択は~14%（Dochkina 2026, 25Kタスク）
- **False Claims警戒** — Capybara v8で29〜30%の虚偽主張率（v4: 16.7%）。`completion-gate.py`の存在意義
- **4層ハーネスフレームワーク** — Model Weights / Context / Harness / Infrastructure の4層モデル（Harness Blueprint分析）。「implementation inaccessible ≠ design principle inapplicable」— CC内部実装を触れないことと設計原則として学べないことは別の主張
- **Claude Managed Agents の3層分離** — Brain（ハーネス）/ Hands（ツール実行サンドボックス）/ Session（状態ログ）を独立インタフェースに分離。推奨構成は「脳は Managed Agents（計画・推論層）、手足は Custom Harness（コード変更・ビルド・テスト・検証層）」のハイブリッド
- **5 Bets 設計哲学** — CC本体の5つの賭け: Generator Loop over Callbacks / File-Based Memory over Databases / Self-Describing Tools over Central Orchestrators / Fork Agents for Cache Sharing / Hooks Over Plugins。Fork Agentsの90%キャッシュ割引主張は実測25-50%で環境依存が大きく最も脆弱なBet
- **2^N problem** — 動的に生成されるboundary marker（セクション区切り）が変わるたびPrompt Cacheが無効化され、N個の動的セクションで最悪2^Nのcache miss パターンが発生。スキル設計で動的セクションを避ける根拠
- **thinking effort のデフォルト変更（2026-03-04）** — Anthropicがデフォルトreasoning effortをhigh→mediumに変更（レイテンシ削減目的）。正式env var名は`CLAUDE_CODE_EFFORT_LEVEL`（`CLAUDE_CODE_DEFAULT_EFFORT`は誤称）。`CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`はOpus 4.7以降ではno-op（常時adaptive reasoning）
- **Dynamic Workflows / Workflow tool** — Opus 4.8で出荷されたplatform機能。毎セッションtool descriptionで注入され、キーワードやultracode指定でopt-in起動、最大1000 subagentまでresumable実行。`/effort ultracode`（xhigh）のreasoning tierも同時出荷

## 実践的な適用

ソースコード分析から得た知見をdotfilesハーネスに反映：

| タスク | 実施内容 |
|--------|---------|
| `omitClaudeMd` | 7つのread-onlyエージェントに`omitClaudeMd: true`追加 |
| `disallowedTools` | 7つのread-onlyエージェントにEdit/Write/NotebookEdit禁止追加 |
| effortレベル | 5エージェントにeffort指定追加（high/medium/low） |
| Context control原則 | `workflow-guide.md`に追記 |
| Synthesis guard | `dispatch/SKILL.md`に追加（コンテキスト混入防止） |
| スキル品質チェック | `skill-creator/SKILL.md`にskillify 6要素追加 |

dotfilesハーネスはClaude Codeの内部設計を参照してドメイン固有コンテキストアーキテクチャを構築している。CLI部分（hooks/scripts）はコモディティであり、差別化はMEMORY.md / Progressive Disclosure / エージェントルーティングの設計にある。

## 関連概念

- [ハーネスエンジニアリング](harness-engineering.md) — Claude Code上でのハーネス設計原則と実装パターン
- [コンテキストエンジニアリング](context-engineering.md) — CLAUDE.md階層とProgressive Disclosureの設計
- [スキル設計](skill-design.md) — スキルシステムの実装詳細とskillify品質基準

## ソース

- [Claude Code内部アーキテクチャ分析](../../research/2026-04-01-claude-code-internal-architecture-analysis.md) — ソースコード分析からの設計パターン抽出とdotfilesへの統合決定
- [instructkr/claude-code ソース分析](../../research/2026-03-31-instructkr-claude-code-src-analysis.md) — 1,902ファイル/512K LOCのアーキテクチャマップと主要サブシステム一覧
- [The Harness Wars Begin](../../research/2026-04-02-harness-wars-begin-analysis.md) — ハーネスコモディティ化の洞察とContext Graph・Audit Trail・Protocol優位性の知見
- [Claude Code Harness Blueprint](../../research/2026-04-08-cc-harness-blueprint-analysis.md) — CC内部4層設計を分析、7項目をharnessに統合済み
- [Launching Claude Managed Agents](../../research/2026-04-09-claude-managed-agents-analysis.md) — Managed Agentsを分析、Hybrid構成など5タスク採用
- [Claude Code from Source 設計原則 周辺知見補完](../../research/2026-04-10-claude-code-design-principles-analysis.md) — CC設計原則の業界動向・脆弱性をGemini調査で補完
- [Claude Code from Source 全18章リバースエンジニアリング分析](../../research/2026-04-10-claude-code-from-source-analysis.md) — CC全18章を分析、Tier1/2統合しTier3は記録のみ
- [Claude Code from Source /absorb統合実行レポート](../../research/2026-04-10-claude-code-from-source-integration-report.md) — CCソース分析の統合実行、7ファイル編集+3新規作成完了
- [How to Build a Full AI Stack Using Only Claude in 2026 再分析](../../research/2026-04-11-claude-only-stack-cyrilxbt-analysis.md) — Claude単体スタック記事を再分析、全項目既存済みで不採用
- [15 Claude Code Settings Most Developers Never Touch](../../research/2026-05-10-zodchixquant-15-settings-absorb-analysis.md) — 15設定記事を検証、xhigh設定済み確認・thinking summary運用化
- [Claude Code in Large Codebases: Best Practices](../../research/2026-05-20-claude-code-large-codebase-absorb-analysis.md) — 大規模コードベース記事は既存実装で全カバー、新規採用なし
- [The Claude Opus 4.8 Setup Guide](../../research/2026-05-30-opus48-setup-guide-absorb-analysis.md) — Opus4.8設定ガイド記事、Fast Mode指針採用・誤情報2件検出
- [32 Claude Code hacks](../../research/2026-05-31-32-claude-code-hacks-absorb-analysis.md) — 32個のCC hacks記事、ultracode表記追記のみ採用
- [「Claudeの14ステップ活用法」](../../research/2026-06-02-how-to-actually-use-claude-14-steps-absorb-analysis.md) — Claude活用14ステップ記事、既存判断で全手法カバー済み・採用0件
