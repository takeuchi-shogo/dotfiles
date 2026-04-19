---
name: cursor
description: >
  Cursor Agent CLI (ヘッドレスモード) を使ったコード分析・生成・リファクタリング。
  マルチモデルアクセス（GPT-5, Sonnet-4 等）と Cloud Agent（非同期長時間タスク）が強み。
  Triggers: 'cursor', 'Cursor で', 'cursor agent', 'Cloud Agent で', 'agent -p'.
  Do NOT use for: 1Mコンテキスト分析（use /gemini）、深い推論レビュー（use /codex）、
  Claude で十分な軽量タスク（use Agent tool directly）。
origin: self
metadata:
  pattern: tool-wrapper
---

# Cursor Agent Skill Guide

## Running a Task

1. デフォルトで非対話モード (`-p`) を使用する
2. デフォルトモデルは `composer-2`。ユーザーが明示的に指定した場合はそちらを優先する
3. 用途に応じてモードとオプションを選択:
   - `--force`: ファイル変更を許可（デフォルトは read-only）
   - `--mode=plan`: 計画のみ（変更なし）
   - `--mode=ask`: Q&A（読み取り専用）
   - `--model <model>`: モデル指定（デフォルト: `composer-2`、他: `gpt-5.4-medium`, `claude-4.6-opus-high` 等）
   - `--output-format <text|json|stream-json>`: 出力形式
4. コマンドを組み立てて実行する

### Quick Reference

| Use case             | Key flags                                               |
| -------------------- | ------------------------------------------------------- |
| Read-only 分析       | `agent -p --model composer-2 --trust "Analyze: {prompt}" 2>/dev/null`              |
| 計画・設計           | `agent -p --model composer-2 --trust --mode=plan "{prompt}" 2>/dev/null`           |
| ファイル変更         | `agent -p --model composer-2 --trust --force "{prompt}" 2>/dev/null`               |
| モデル指定（Pro）    | `agent -p --model gpt-5.4-medium --trust "{prompt}" 2>/dev/null`            |
| 構造化出力           | `agent -p --model composer-2 --trust --output-format json "{prompt}" 2>/dev/null`  |
| Cloud Agent（非同期）| `agent -c "{prompt}" 2>/dev/null`                       |
| セッション再開       | `agent --continue 2>/dev/null`                          |
| セッション一覧       | `agent ls 2>/dev/null`                                  |

### Output Format

| Format        | 用途                           |
| ------------- | ------------------------------ |
| `text`        | デフォルト。クリーンなテキスト |
| `json`        | 構造化分析、スクリプト統合     |
| `stream-json` | リアルタイム進捗トラッキング   |

## When to Use Cursor Agent

- **使う**: マルチモデル比較（GPT-5 vs Sonnet-4）、Cloud Agent で非同期タスク、Cursor のコードベースインデックスを活用した分析、画像/メディアの解析
- **使わない**: 1M コンテキスト分析（→ Gemini）、深い推論/セキュリティ分析（→ Codex）、Claude 単体で十分なタスク（→ Agent tool）

## Cloud Agent

離席中も処理を継続させる場合に使用。`cursor.com/agents` から Web/モバイルで確認可能。

```bash
# Cloud Agent で非同期実行
agent -c "refactor the auth module and add comprehensive tests" 2>/dev/null

# 会話の途中でも & プレフィックスで Cloud に引き継ぎ可能
```

**注意**: Cloud Agent はユーザーに確認を仰いでから起動する。長時間タスクの委譲に最適。

## Session Management

```bash
# 過去のセッション一覧
agent ls 2>/dev/null

# 最新セッションを再開
agent --continue 2>/dev/null

# 特定セッションを再開
agent --resume="chat-id-here" 2>/dev/null
```

## Language Protocol

Cursor Agent への指示は英語で行い、結果をユーザーの言語（日本語）で報告する。

## Error Handling

- `agent --version` が失敗したら CLI 未インストールを報告
- "Authentication required" → `agent login` を案内
- "No models available" → Cursor Pro サブスクリプションの確認を案内
- タイムアウト（2分超）の場合はプロンプトを分割する

## Gotchas

- **認証**: `CURSOR_API_KEY` 環境変数 or `agent login` が必要。未認証だと全コマンド失敗
- **--force の影響**: 確認なしでファイルを直接変更する。本番コードには使用前にユーザー確認
- **Cloud Agent のコスト**: 長時間実行はトークン消費大。スコープを明確にして起動する
- **モデル可用性**: アカウントのプランによって使えるモデルが異なる。`agent --list-models` で確認
- **言語プロトコル**: 英語で指示を渡す。日本語指示だと推論品質が落ちる場合がある

## Anti-Patterns

| NG | 理由 |
|----|------|
| Claude で十分なタスクに Cursor を使う | 余分なプロセス起動のオーバーヘッド。Agent tool で委譲する方が速い |
| --force を無条件で付ける | 意図しないファイル変更のリスク。read-only がデフォルト |
| Cloud Agent を小タスクに使う | 起動・同期コストに見合わない。ヘッドレスモードで十分 |
