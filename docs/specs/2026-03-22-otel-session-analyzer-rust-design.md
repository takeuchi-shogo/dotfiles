# otel-session-analyzer Rust Rewrite Design

## Overview

Claude Code の JSONL セッションログを構造化 Span に変換し、統計分析・OTel エクスポートする CLI ツール。
Python プロトタイプからの Rust 書き直し。

## Architecture

Library + CLI 分離構成。`lib.rs` のパーサーは将来 hook からも呼び出し可能。

```
tools/otel-session-analyzer/
├── Cargo.toml
├── src/
│   ├── main.rs          # CLI (clap subcommands)
│   ├── lib.rs           # Public API
│   ├── model.rs         # SessionSpan, Turn, ToolCall
│   ├── parser.rs        # JSONL → SessionSpan
│   ├── categories.rs    # Tool category mapping
│   ├── stats.rs         # Statistics calculation & formatting
│   ├── discovery.rs     # Session file discovery
│   ├── batch.rs         # Multi-session aggregation
│   ├── redactor.rs      # Sensitive data redaction
│   └── export/
│       ├── mod.rs
│       ├── json.rs      # JSON output
│       └── otlp.rs      # OTLP HTTP export
├── tests/
│   ├── parser_test.rs
│   └── fixtures/
└── docker-compose.yml
```

## Subcommands

```
osa analyze <file>                  # Single session stats
osa analyze --project <name>        # All sessions for project
osa analyze --last N                # Last N sessions
osa analyze --since YYYY-MM-DD      # Sessions after date

osa list                            # List all sessions
osa list --project <name>           # Filter by project

osa export <file>                   # JSON span output
osa export <file> --otlp <endpoint> # OTLP HTTP export
osa export --last 1 --otlp ...      # Export latest session
```

## Data Model

```rust
struct SessionSpan {
    session_id: String,
    start_time: DateTime<Utc>,
    end_time: DateTime<Utc>,
    duration: Duration,
    tokens: TokenUsage,
    turns: Vec<Turn>,
}

struct Turn {
    index: u32,
    start_time: DateTime<Utc>,
    end_time: DateTime<Utc>,
    duration: Duration,
    tokens: TokenUsage,
    tool_calls: Vec<ToolCall>,
}

struct ToolCall {
    tool_id: String,
    name: String,
    category: ToolCategory,
    input_size: usize,
    output_size: usize,
    is_error: bool,
    start_time: DateTime<Utc>,
    end_time: Option<DateTime<Utc>>,
    duration: Option<Duration>,
}

struct TokenUsage {
    input: u64,
    output: u64,
    cache_read: u64,
    cache_creation: u64,
}

enum ToolCategory {
    FileRead, FileWrite, Shell, Web, Agent, System, Mcp, Unknown,
}
```

## Dependencies

- `clap` (derive) — CLI
- `serde` / `serde_json` — JSON
- `chrono` — timestamps
- `colored` — terminal colors
- `reqwest` (blocking, optional feature `otlp`) — OTLP export
- `uuid` — span/trace ID generation

## Features

- Colored terminal output with summary tables
- Session auto-discovery from ~/.claude/projects/
- Batch analysis across multiple sessions with trends
- OTLP HTTP export behind feature flag
- Sensitive data redaction (API keys, passwords, tokens)
- Security: only sizes recorded, never content

## Binary Name

`osa` (otel-session-analyzer の略)。`cargo install --path .` で `~/.cargo/bin/osa` に配置。

## Success Criteria

1. `osa analyze <file>` が Python 版と同等以上の統計を出力
2. `osa list` がセッション一覧を表示
3. `osa analyze --last 5` でバッチ分析
4. `osa export --otlp` で Jaeger に Span 送信
5. 実セッションログでパース成功率 100%
