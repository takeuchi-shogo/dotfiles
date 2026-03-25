# Agent Execution Profiles

> Qoder Experts Mode の知見: Expert = 独立ハーネス。プロンプト差し替えではなくツールセット・制約・コンテキストが役割別。

各エージェントのカテゴリ別デフォルト実行パラメータを定義する。
個別の agent 定義（`agents/*.md`）で上書き可能。

---

## カテゴリ別デフォルト

| Category | Default Model | maxTurns | Reasoning | Context Injection |
|----------|--------------|----------|-----------|-------------------|
| **Analyzer** (reviewer系) | sonnet | 12 | default | diff + 変更ファイル周辺 |
| **Deep Analyzer** (codex/gemini系) | haiku (→外部CLI) | 10 | high/xhigh | diff only (blind-first) |
| **Implementer** (pro/fixer系) | sonnet | 20 | default | plan + 対象ファイル |
| **Orchestrator** (triage/meta系) | sonnet | 8 | default | タスク概要のみ |

---

## エージェント分類

### Analyzer（読み取り専用レビュー・分析）

| Agent | Model | 契約 | 備考 |
|---|---|---|---|
| code-reviewer | sonnet | Analyze-only | 汎用レビュー。チェックリスト注入で言語特化 |
| security-reviewer | opus | Analyze-only | 深度セキュリティ分析。唯一の opus |
| edge-case-hunter | sonnet | Analyze-only | 境界値・異常系特化 |
| cross-file-reviewer | sonnet | Analyze-only | モジュール間整合性 |
| silent-failure-hunter | sonnet | Analyze-only | エラーハンドリング検出 |
| type-design-analyzer | sonnet | Analyze-only | 型設計品質 |
| golang-reviewer | sonnet | Analyze-only | Go 特化レビュー |
| comment-analyzer | sonnet | Analyze-only | コメント品質 |
| test-analyzer | sonnet | Analyze-only | テスト設計品質 |
| product-reviewer | sonnet | Analyze-only | 仕様整合性 |
| design-reviewer | sonnet | Analyze-only | UI/UX 設計 |
| safe-git-inspector | haiku | Analyze-only | Git 読み取り専用 |
| db-reader | haiku | Analyze-only | DB 読み取り専用 |
| ui-observer | sonnet | Analyze-only | ブラウザ状態観察 |

### Deep Analyzer（外部 CLI 連携）

| Agent | Model | 外部 CLI | 備考 |
|---|---|---|---|
| codex-debugger | haiku | Codex CLI | エラー分析・デバッグ |
| codex-risk-reviewer | haiku | Codex CLI | 実装前リスク分析 |
| codex-reviewer | haiku | Codex CLI | 深い推論レビュー |
| gemini-explore | haiku | Gemini CLI | 1M コンテキスト分析 |

### Implementer（コード書き込み可能）

| Agent | Model | 備考 |
|---|---|---|
| backend-architect | sonnet | バックエンド設計・実装 |
| build-fixer | sonnet | ビルドエラー修正 |
| debugger | sonnet | バグ修正 |
| frontend-developer | sonnet | フロントエンド実装 |
| nextjs-architecture-expert | sonnet | Next.js 特化 |
| golden-cleanup | sonnet | コード品質改善 |
| document-factory | sonnet | ドキュメント生成 |
| doc-gardener | haiku | 軽量ドキュメント修正 |
| golang-pro | sonnet | Go 実装 |
| typescript-pro | sonnet | TypeScript 実装 |
| test-engineer | sonnet | テスト作成 |

### Orchestrator（ルーティング・管理）

| Agent | Model | 備考 |
|---|---|---|
| triage-router | haiku | 軽量タスク分類 |
| meta-analyzer | sonnet | Task/Meta 分離分析 |
| autoevolve-core | sonnet | 改善サイクル管理 |

---

## 設計原則

1. **haiku は軽量ゲートウェイ**: 外部 CLI 連携や単純ルーティングでは haiku で十分。推論は外部 CLI が担当
2. **sonnet が標準**: 汎用的な分析・実装は sonnet。コスト/品質バランスが最適
3. **opus は例外**: 深度が必要な特定ドメインのみ（現在は security-reviewer のみ）
4. **ツール制限が契約**: agent 定義の tools フィールドが Analyze-only / Implement / Orchestrate 契約を物理的に実現（詳細: `references/subagent-delegation-guide.md` Expert 実行契約）
