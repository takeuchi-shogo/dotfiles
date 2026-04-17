# MCP Connector Inventory — 2026-04-17

4 ソース (.mcp.json / settings.json / .codex/config.toml / plugin native) に分散する
MCP connector の全量と、有効化状態・ロックインリスク・代替手段を一覧化する。

関連ドキュメント:
- [`telemetry-coverage.md`](telemetry-coverage.md) — telemetry 品質
- [`.config/claude/references/mcp-toolshed.md`](../../.config/claude/references/mcp-toolshed.md) — 用途別カタログ
- [`.config/claude/scripts/policy/connector-drift-check.py`](../../.config/claude/scripts/policy/connector-drift-check.py) — drift 検出 CLI

## ソース仕様

| # | ソース | パス | 形式 | 用途 |
|---|-------|------|------|------|
| 1 | `.mcp.json` | repo root | JSON `mcpServers` | Claude Code が読む MCP 定義 |
| 2 | `settings.json` | `.config/claude/settings.json` `enabledMcpjsonServers` | JSON array | Claude Code 側の enable 明示 |
| 3 | `.codex/config.toml` | `.codex/config.toml` `[mcp_servers.*]` | TOML sections | Codex CLI が読む MCP 定義 |
| 4 | plugin native | hardcoded (`mcp-audit.py` の `_NATIVE_SERVERS`) | set | Claude Code built-in / plugin 経由 |

## Connector 一覧

| name | sources | Claude enabled | Codex enabled | provider | lock-in risk | fallback | notes |
|------|---------|----------------|---------------|----------|--------------|----------|-------|
| `context7` | 1, 2, 3 | ✅ | ✅ | Upstash (`@upstash/context7-mcp`) | **low** | WebFetch + docs グレップ | 最も広く使う docs 取得 |
| `alphaxiv` | 1, 2 | ✅ | ❌ | alphaxiv (authenticated) | med | arXiv WebFetch | OAuth 認証あり |
| `code-review-graph` | 1, 2 | ✅ | ❌ | local (tree-sitter + graph) | low | Grep + 手動 trace | ローカル CLI 版もあり |
| `scite` | 1 | ❌ (drift) | ❌ | scite (authenticated) | high | Google Scholar + WebFetch | **未有効化** — 用途未確定のため `enabledMcpjsonServers` から除外 |
| `playwright` | 3 | ❌ | ✅ | Microsoft (`@playwright/mcp`) | med | agent-browser CLI (MCP 不要) | ブラウザ操作は CLI で代替可 |
| `deepwiki` | 3 | ❌ | ✅ | Anthropic (`@anthropic-ai/deepwiki-mcp`) | med | WebFetch + docs search | Codex 専用、Claude 未連携 |
| `openaiDeveloperDocs` | 3 | ❌ | ✅ | OpenAI (`https://developers.openai.com/mcp`) | low | WebFetch | URL-based MCP |
| `brave-search` | 4 (native) | ✅ | ❌ | Brave API (plugin) | low | WebSearch | Claude Code plugin に同梱 |
| `obsidian` | 4 (native) | ✅ | ❌ | local (plugin) | low | Obsidian CLI (`obsidian-cli`) | Vault 操作 |
| `plugin_discord_discord` | 4 (native) | ✅ | ❌ | Discord (plugin) | low | Webhook | チャネル通知 |

## 検出済み drift (2026-04-17 実行時点)

`connector-drift-check.py` 実行で以下 7 件の drift を確認:

### 1 件: defined_but_not_enabled
- `scite` — `.mcp.json` に定義されているが `enabledMcpjsonServers` に無い。
  意図的な未有効化 (用途未確定)。用途が決まれば enable、不要なら `.mcp.json` から削除する。

### 3 件: codex_only
Codex CLI でのみ有効な server。Claude 側にポートするかは用途次第:
- `playwright` — agent-browser CLI で代替できるため Claude 側は不要
- `deepwiki` — Claude は WebFetch + context7 で代替可能。必要性を再評価
- `openaiDeveloperDocs` — Codex ワークフロー固有

### 3 件: claude_only
Claude 側でのみ有効な server。Codex 側での需要が発生したら config.toml に追加:
- `alphaxiv`, `code-review-graph`, `scite`

## 運用ルール

1. **drift の扱い**:
   - `defined_but_not_enabled`: **要解消** (enable か削除)
   - `codex_only` / `claude_only`: **allowed** (意図的)。本表にその理由を記載する

2. **新規 connector 追加時**:
   - 本 inventory に 1 行追加
   - lock-in risk / fallback を明記
   - `mcp-audit.py` の `_NATIVE_SERVERS` は native/plugin 経由のもののみ

3. **drift check の実行**:
   ```bash
   python3 .config/claude/scripts/policy/connector-drift-check.py
   ```
   CI や SessionStart hook への組み込みは future work (T4 で検討)

## ロックインリスク定義

| level | 条件 | 対処 |
|-------|------|------|
| **low** | 代替 provider 複数 / stdlib で代替可能 / サービス停止時の影響小 | 特別対応不要 |
| **med** | 代替は存在するが、移行コスト有 / 認証/API 依存 | fallback を文書化 |
| **high** | 独自 API / 認証フロー複雑 / データ lock-in | 撤退計画を用意 |

## 変更履歴

- **2026-04-17**: 初版作成。`connector-drift-check.py` 初回実行結果に基づく
