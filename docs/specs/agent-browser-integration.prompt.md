---
name: agent-browser-integration
status: spike
created: 2026-03-12
acceptance_criteria:
  - agent-browser がグローバルインストールされ、基本コマンド (open, snapshot, click, close) が動作する
  - ui-observer agent が agent-browser CLI ベースに更新されている
  - webapp-testing skill が agent-browser のワークフローを記述している
  - Playwright MCP への依存が除去され、Bash + agent-browser CLI で完結する
---

# agent-browser Integration

## Background

現在 ui-observer agent と webapp-testing skill は Playwright (Python / MCP) に依存している。
vercel-labs/agent-browser は AI エージェント専用に設計されたブラウザ自動化 CLI で、
アクセシビリティツリーベースのセマンティック参照 (@e1, @e2) を使い、LLM との相性が良い。

## Requirements

1. **インストール**: `npm install -g agent-browser && agent-browser install`
2. **ui-observer agent 移行**: Playwright スクリプト → agent-browser CLI コマンド
3. **webapp-testing skill 更新**: Decision Tree と例を agent-browser ベースに書き換え
4. **後方互換**: Playwright MCP が設定されているプロジェクトでは引き続き使えるようフォールバック記述を残す

## Prompt

dotfiles の `.config/claude/agents/ui-observer.md` と `.config/claude/skills/webapp-testing/SKILL.md` を
agent-browser CLI ベースに移行してください。

- agent-browser の snapshot (アクセシビリティツリー) を主な要素発見手段とする
- セマンティック参照 (@e1) でのインタラクションを推奨する
- find コマンド (find role, find text, find label) を活用する
- state save/load で認証永続化をサポートする
- screenshot と snapshot diff を活用した観察フローを記述する
