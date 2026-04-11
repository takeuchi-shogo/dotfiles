---
source: Derrick Choi (@derrickcchoi) "Where do plugins fit in Codex?"
date: 2026-03-31
status: analyzed
---

## Source Summary

Codex の4層スタック解説。Skills(ワークフローロジック) → MCP(ツール/コンテキストアクセス) → Apps(認証統合) → Plugins(パッケージ化)。プラグインは `.codex-plugin/plugin.json` マニフェスト中心で skills/ + .app.json + .mcp.json をバンドル。個人(`~/.agents/plugins/`)とリポジトリ(`.agents/plugins/`)の2スコープ。Built by OpenAI プラグイン（GitHub, Build Web Apps, Google Drive, Figma, Gmail, Slack, Calendar, Linear）と plugin-creator によるカスタム作成が可能。非エンジニアリングワークフローにも対応。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 4層アーキテクチャ（Skills→MCP→Apps→Plugins） | Partial | Claude Code 側は skills/MCP/agents の3層。Codex 側はプラグイン構造なし |
| 2 | プラグイン構造（.codex-plugin/plugin.json） | Gap | `.codex-plugin/` 不在。`.codex/` に AGENTS.md + agents/*.toml + rules |
| 3 | 2スコープ管理（個人 vs リポジトリ） | Partial | Claude Code は global/project 分離済み。Codex は `.codex/` のみ |
| 4 | plugin-creator | Gap | カスタムプラグイン作成の仕組みなし |
| 5 | marketplace.json | Gap | 未使用 |
| 6 | Built-in プラグイン | N/A | Claude Code は MCP 経由で統合済み |
| 7 | 非エンジニアリングワークフロー | N/A | Claude Code 側で対応済み |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す構造 | 判定 |
|---|-------------|---------------|------|
| 1 | codex-plugin-cc (03-31統合済み) | プラグインは skills+MCP+apps をバンドル | Already (強化不要) |
| 2 | .codex/AGENTS.md + agents/*.toml | plugin.json 中心の構造 | Already (強化可能) — ポータビリティ向上余地あり |

## Integration Decisions

- **スキップ（全項目）**: 現状の `.codex/AGENTS.md` + `codex-plugin-cc` で十分機能している
- **理由**: Codex は Claude Code の補助用途（レビュー・リスク分析・レスキュー）。プラグイン化の ROI が低い。エコシステム成熟時に再検討
- **再検討トリガー**: Codex プラグインエコシステムの GA / marketplace の安定 / 複数リポジトリでの Codex 利用拡大
