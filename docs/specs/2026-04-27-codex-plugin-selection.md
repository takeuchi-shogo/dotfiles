# Spec: Codex Plugin Selection

**Date**: 2026-04-27
**Source**: [absorb analysis](../research/2026-04-27-codex-claude-parity-absorb-analysis.md) — G8
**Status**: deferred
**Workflow**: spec → user interview → /spike (別セッション)

## Context

Codex CLI には 116 plugin が cached (`~/.codex/.tmp/plugins/plugins/`) されているが、enabled は `github@openai-curated` のみ。`config.toml` の `[plugins]` で個別有効化できる。

候補 plugin (cached 116 から実利用が見込まれるもの):

### High value (user の workflow に直結)
- `linear@openai-curated` — issue/project 管理
- `notion@openai-curated` — docs / knowledge
- `slack@openai-curated` — communication
- `gmail@openai-curated` — メール
- `google-calendar@openai-curated` — schedule
- `vercel@openai-curated` — deploy
- `cloudflare@openai-curated` — infra
- `figma@openai-curated` — design (frontend skill 連携)
- `stripe@openai-curated` — payment (multi-currency project 関連)

### Medium value
- `sentry@openai-curated` — error tracking
- `circleci@openai-curated` — CI
- `expo@openai-curated` — mobile
- `temporal@openai-curated` — workflow
- `motherduck@openai-curated` — analytics

### 不明 (user 判断要)
- `granola`, `outlook-*`, `pipedrive`, `monday-com`, `clickup` 等

## Required Decisions

User へのインタビュー項目:
1. 日常的に使う SaaS/サービスは何か?
2. 既存の Claude MCP 設定 (~/.mcp.json) と被るものは Codex plugin で重複させるか?
3. Authentication が必要な plugin (linear, notion, slack 等) で OAuth セットアップを許容するか?

## Acceptance Criteria

1. user 判断で実利用 plugin を 5-8 件選定
2. `config.toml [plugins."<name>@openai-curated"] enabled = true` で有効化
3. 各 plugin の認証完了確認
4. 不要な plugin は明示的に `enabled = false` で記録 (黙認しない)

## Risks

- Plugin 過剰有効化で context 圧迫 → top 5-8 に絞る
- Authentication 漏れで plugin が silent fail → 各 plugin の auth 状態を `codex plugin list` で確認 (要 v0.124.0+ 動作確認)

## Implementation Sketch

```toml
# config.toml
[plugins."linear@openai-curated"]
enabled = true

[plugins."notion@openai-curated"]
enabled = true

# ... user 選定したもの
```

## Recommendation

**別セッションで `/interview` skill** → user の利用状況を 4-5 質問で抽出 → `/spike` で 1-2 plugin 試験有効化 → 動作確認 → 段階的に拡大。
