---
name: setup-background-agents
description: >
  プロジェクトにバックグラウンドエージェント基盤をセットアップする。GitHub Actions ワークフロー、
  イベントルーティング、ガバナンス設定のテンプレートを生成。
  "The Self-Driving Codebase" の3本柱（Isolated Compute, Event Routing, Governance）に基づく。
  新プロジェクトでのCI/CDエージェント統合や、既存プロジェクトへの自動化追加に使用。
  Triggers: 'background agent', 'バックグラウンドエージェント', 'CI/CD agent', 'GitHub Actions agent', 'self-driving codebase', '自動化エージェント'.
  Do NOT use for: プロジェクト初期化全般（use /init-project）、既存 CI の修正（直接編集で十分）、スケジュール実行（use /schedule）。
origin: self
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
disable-model-invocation: true
metadata:
  pattern: generator
---

# Setup Background Agents

プロジェクトにバックグラウンドエージェント基盤を構築するスキル。

## 出典

- "The Self-Driving Codebase" (background-agents.com) — Ona
- Cursor Self-Driving Codebase Research (2026)

## 3本柱

1. **Isolated Compute** — エージェントごとの隔離環境（worktree / container）
2. **Event Routing** — イベント駆動のエージェント起動（PR, schedule, security advisory）
3. **Governance** — 権限制御、監査証跡、人間レビューゲート、Blast Radius 制限

## Workflow

```
1. Assess    → プロジェクトの現状分析（tech stack, CI/CD, 既存自動化）
2. Select    → ユースケース選択（ユーザーと対話）
3. Generate  → テンプレートからワークフロー・設定を生成
4. Verify    → 生成物の動作確認ガイド
```

## Step 1: Assess

プロジェクトの現状を分析:

```bash
# Tech stack
ls package.json go.mod Cargo.toml pyproject.toml requirements.txt 2>/dev/null
# CI/CD
ls -la .github/workflows/ .gitlab-ci.yml Jenkinsfile 2>/dev/null
# Existing automation
ls .github/dependabot.yml .github/renovate.json 2>/dev/null
# Branch protection
gh api repos/{owner}/{repo}/branches/main/protection 2>/dev/null || echo "No branch protection"
```

## Step 2: Select Use Cases

ユーザーに以下から選択してもらう（複数可）:

| ユースケース | トリガー | 説明 |
|---|---|---|
| **dependency-audit** | schedule (weekly) | 依存関係の監査・自動更新PR |
| **cve-remediation** | schedule (6h) | 脆弱性の自動検出・修正PR生成 |
| **test-coverage** | pull_request | カバレッジギャップの検出・テスト追加 |
| **standards-enforcement** | schedule (weekly) | コーディング標準の一括適用 |

## Step 3: Generate

選択されたユースケースごとに `templates/` からテンプレートを読み込み、プロジェクトに合わせてカスタマイズして生成。

### 生成物

1. `.github/workflows/agent-{usecase}.yml` — GitHub Actions ワークフロー
2. `.github/agent-config/{usecase}.md` — エージェントへの指示（制約含む）
3. `docs/background-agents.md` — 概要ドキュメント（初回のみ）

### テンプレート参照

```
~/.claude/skills/setup-background-agents/templates/
├── dependency-audit.yml
├── cve-remediation.yml
├── test-coverage.yml
├── standards-enforcement.yml
├── governance.md
└── agent-configs/
    ├── dependency-audit.md
    ├── cve-remediation.md
    ├── test-coverage.md
    └── standards-enforcement.md
```

### 制約の注入

`references/constraints-library.md` から該当する制約を agent-config に注入する:
- 全ユースケース: C-001, C-003, C-006, C-007, C-009
- dependency-audit: + C-002
- DB 関連: + C-004
- API 関連: + C-005
- 並列実行: + C-008

### Governance 設定

全ユースケース共通で `templates/governance.md` を参照し、以下を確認・設定:
- `.github/CODEOWNERS` — エージェント PR のレビュー必須化
- Branch protection rules の推奨設定
- エージェントコミットの識別（`agent/` ブランチプレフィックス）

## Step 4: Verify

生成後のチェックリスト:

- [ ] ワークフロー YAML の構文が正しい
- [ ] エージェント設定に適切な制約が含まれている
- [ ] CODEOWNERS でエージェント PR のレビューアーが設定されている
- [ ] シークレット（ANTHROPIC_API_KEY）が GitHub Secrets に登録されている
- [ ] Branch protection でマージ前レビューが必須になっている

## Key Principles

- **制約 > 指示**: "No partial implementations" > "finish the task fully"
- **スコープを限定**: well-scoped, reviewable, bounded work
- **PR がレビューゲート**: エージェントのコードは必ず PR 経由でマージ
- **小さな定常エラー率を許容**: 全エラーの予防より、高速な検出・修正が効率的
- **階層構造**: Planner → Worker の分離

## Anti-Patterns

- エージェントに main/master への直接 push 権限を与える
- 制約なしでエージェントを起動する
- レビューなしでエージェント PR をマージする
- 1つのエージェントに複数の異なるタスクを同時に指示する
