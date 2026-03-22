# osa — OpenTelemetry Session Analyzer

Claude Code の JSONL セッションログを構造化 Span に変換し、統計分析・OTel エクスポートする CLI ツール。

## Install

```bash
cd tools/otel-session-analyzer
go install .
# → ~/.go/bin/osa
```

## Usage

### セッション統計を表示

```bash
# 直近セッションを自動検出して分析
osa analyze

# ファイル指定
osa analyze ~/.claude/projects/<project>/<session>.jsonl

# プロジェクト絞り込み + 直近3件をバッチ分析
osa analyze -p dotfiles -n 3

# 日付以降のセッションを集約
osa analyze --since 2026-03-20
```

### セッション一覧

```bash
osa list
osa list -p dotfiles
```

### エクスポート

```bash
# JSON Span 出力
osa export <session>.jsonl -o spans.json

# OTLP HTTP エクスポート (Jaeger 等)
osa export <session>.jsonl --otlp http://localhost:4318
```

## Jaeger で可視化

```bash
docker compose up -d
osa export <session>.jsonl --otlp http://localhost:4318
open http://localhost:16686
```

## Span 階層

```
session (root)
└─ turn (ユーザー1発言 → AI応答)
   └─ tool_call (Bash, Read, Agent...)
```

## ツールカテゴリ

| カテゴリ | ツール |
|----------|--------|
| file_read | Read, Glob, Grep, LSP |
| file_write | Write, Edit, NotebookEdit |
| shell | Bash |
| web | WebSearch, WebFetch |
| agent | Agent, Task, TaskOutput, TaskCreate, ... |
| system | Skill, AskUserQuestion, EnterPlanMode, ... |
| mcp | mcp__* |

## セキュリティ

Span には `input_size` / `output_size`（文字数）のみ記録し、中身は保存しない。
`internal/redactor` で API key, password, Bearer token 等を自動除去。
