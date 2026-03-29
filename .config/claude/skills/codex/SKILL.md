---
name: codex
description: >
  Use when the user asks to run Codex CLI (codex exec, codex resume) or references
  OpenAI Codex for code analysis, refactoring, or automated editing. Uses gpt-5.4 by default.
  Triggers: 'codex', 'codex exec', 'codex resume', 'Codex で', 'gpt-5.4 で分析'.
  Do NOT use for: コードレビュー（use /codex-review）、デバッグ（use debugger agent）、リサーチ（use /gemini or /research）。
metadata:
  pattern: tool-wrapper
---

# Codex Skill Guide

## Running a Task

1. Default to `gpt-5.4` model. Auto-infer reasoning effort from task type (see table below). Inform the user of the auto-selected level and allow override. User can also override model if needed (see Model Options below).

### Reasoning Effort Auto-Inference

| タスク性質 | 自動選択 | 根拠 |
|-----------|----------|------|
| セキュリティ分析、脆弱性調査 | `xhigh` | 見落としが致命的 |
| コードレビュー（~30行以上） | `xhigh` | 正確性が最重要 |
| アーキテクチャ設計、デバッグ | `high` | 深い推論が必要 |
| 実装、リファクタリング、テスト生成 | `medium` | 速度とコストのバランス |
| 簡単な修正、フォーマット | `low` | オーバーヘッド最小化 |

ユーザーが明示的に指定した場合はそちらを優先する。
2. Select the sandbox mode required for the task; default to `--sandbox read-only` unless edits or network access are necessary.
3. Assemble the command with the appropriate options:
   - `-m, --model <MODEL>`
   - `--config model_reasoning_effort="<high|medium|low>"`
   - `--sandbox <read-only|workspace-write|danger-full-access>`
   - `--full-auto`
   - `-C, --cd <DIR>`
   - `--skip-git-repo-check`
4. Always use --skip-git-repo-check.
5. When continuing a previous session, use `codex exec --skip-git-repo-check resume --last` via stdin. When resuming don't use any configuration flags unless explicitly requested by the user e.g. if he species the model or the reasoning effort when requesting to resume a session. Resume syntax: `echo "your prompt here" | codex exec --skip-git-repo-check resume --last 2>/dev/null`. All flags have to be inserted between exec and resume.
6. **IMPORTANT**: By default, append `2>/dev/null` to all `codex exec` commands to suppress thinking tokens (stderr). Only show stderr if the user explicitly requests to see thinking tokens or if debugging is needed.
7. Run the command, capture stdout/stderr (filtered as appropriate), and summarize the outcome for the user.
8. **After Codex completes**, inform the user: "You can resume this Codex session at any time by saying 'codex resume' or asking me to continue with additional analysis or changes."

### Quick Reference

| Use case                       | Sandbox mode            | Key flags                                                                                        |
| ------------------------------ | ----------------------- | ------------------------------------------------------------------------------------------------ |
| Read-only review or analysis   | `read-only`             | `--sandbox read-only 2>/dev/null`                                                                |
| Apply local edits              | `workspace-write`       | `--sandbox workspace-write --full-auto 2>/dev/null`                                              |
| Permit network or broad access | `danger-full-access`    | `--sandbox danger-full-access --full-auto 2>/dev/null`                                           |
| Resume recent session          | Inherited from original | `echo "prompt" \| codex exec --skip-git-repo-check resume --last 2>/dev/null` (no flags allowed) |
| Run from another directory     | Match task needs        | `-C <DIR>` plus other flags `2>/dev/null`                                                        |

## Model Options

| Model          | Best for                                                                  | Context window           | Key features                                      |
| -------------- | ------------------------------------------------------------------------- | ------------------------ | ------------------------------------------------- |
| `gpt-5.4` ⭐   | **Codex-optimized model**: Software engineering, agentic coding workflows | 400K input / 128K output | Codex CLI 最適化、高精度コード生成                |
| `gpt-5.2-max`  | **Max model**: Ultra-complex reasoning, deep problem analysis             | 400K input / 128K output | 76.3% SWE-bench, adaptive reasoning, $1.25/$10.00 |
| `gpt-5.2`      | **Flagship model**: General-purpose software engineering                  | 400K input / 128K output | 76.3% SWE-bench, adaptive reasoning, $1.25/$10.00 |
| `gpt-5.2-mini` | Cost-efficient coding (4x more usage allowance)                           | 400K input / 128K output | Near SOTA performance, $0.25/$2.00                |

**gpt-5.4 Advantages**: Codex CLI に最適化された最新モデル。高精度コード生成、改善されたツール使用、低遅延。セキュリティ分析や深い推論タスクに最適。

**Reasoning Effort Levels**:

- `xhigh` - Ultra-complex tasks (deep problem analysis, complex reasoning, deep understanding of the problem)
- `high` - Complex tasks (refactoring, architecture, security analysis, performance optimization)
- `medium` - Standard tasks (refactoring, code organization, feature additions, bug fixes)
- `low` - Simple tasks (quick fixes, simple changes, code formatting, documentation)

**Cached Input Discount**: 90% off ($0.125/M tokens) for repeated context, cache lasts up to 24 hours.

## Following Up

- After every `codex` command, immediately use `AskUserQuestion` to confirm next steps, collect clarifications, or decide whether to resume with `codex exec resume --last`.
- When resuming, pipe the new prompt via stdin: `echo "new prompt" | codex exec resume --last 2>/dev/null`. The resumed session automatically uses the same model, reasoning effort, and sandbox mode from the original session.
- Restate the chosen model, reasoning effort, and sandbox mode when proposing follow-up actions.

## Error Handling

- Stop and report failures whenever `codex --version` or a `codex exec` command exits non-zero; request direction before retrying.
- Before you use high-impact flags (`--full-auto`, `--sandbox danger-full-access`, `--skip-git-repo-check`) ask the user for permission using AskUserQuestion unless it was already given.
- When output includes warnings or partial results, summarize them and ask how to adjust using `AskUserQuestion`.

## CLI Version

Requires Codex CLI v0.57.0 or later. The CLI defaults to `gpt-5.4` (config.toml で設定済み). Check version: `codex --version`

Use `/model` slash command within a Codex session to switch models, or configure default in `~/.codex/config.toml`.

## Gotchas

- **model 選択ミス**: `--model` 未指定だと gpt-5.4 がデフォルト。軽量タスクには `o4-mini` を指定してコスト抑制
- **reasoning effort 過不足**: `--reasoning high` はレビュー・設計向き。実装タスクに xhigh を使うとトークン浪費。タスク種別に合わせて medium/high/xhigh を選択
- **sandbox scope**: `--full-auto` は全ファイル書き込み可能。本番コードには `--suggest` で差分確認を挟む
- **resume token 消費**: `codex resume` は前回セッションの全コンテキストを再読み込み。長いセッション後の resume はコスト大
- **日本語コメント**: Codex は英語最適化。日本語コメントのあるコードで推論精度が落ちる場合がある。指示は英語で渡す

## Skill Assets

- モデル選択ガイド: `references/model-selection.md`
- ヘルパースクリプト: `scripts/codex-helper.sh`

## Anti-Patterns

| NG | 理由 |
|----|------|
| Codex にレビューを依頼する | read-only レビューは /codex-review を使う。codex スキルは実行・編集用 |
| reasoning effort を指定しない | デフォルト high だがレビュー時は xhigh が必要。タスクに応じて調整する |
| 200K 以内のタスクに使う | Claude 単体で十分。Codex は深い推論や大規模分析に使う |
