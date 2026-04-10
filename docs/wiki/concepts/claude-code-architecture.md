---
title: Claude Codeアーキテクチャ
topics: [claude-code]
sources: [2026-04-01-claude-code-internal-architecture-analysis.md, 2026-03-31-instructkr-claude-code-src-analysis.md, 2026-04-02-harness-wars-begin-analysis.md, 2026-04-04-12-claude-features-top-operators-analysis.md, 2026-04-10-claude-code-from-source-analysis.md]
updated: 2026-04-10
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
