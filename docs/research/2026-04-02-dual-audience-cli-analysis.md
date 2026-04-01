---
source: "Build a CLI for AI agents & humans in less than 10 mins" (ghchinoy, Saboo_Shubham_, Zack Akil)
date: 2026-04-02
status: integrated
---

## Source Summary

**主張**: CLIはデータとプレゼンテーションを分離し、人間とAIエージェントの両方に対応すべき。同じコマンドが人間にはTUI、エージェントにはJSON/NDJSONを返す「デュアルオーディエンス」設計。

**手法**:
1. Structured discoverability — Short/Long/Example 3フィールド、AGENTS.md + skills/
2. Agent-first interoperability — `--json`、NO_COLOR、非対話フォールバック、コンテキストウィンドウ保護
3. Configuration and context — XDG準拠、Named environments
4. Error guidance — Hint行、fail fast、決定的exit code (0/1/2/3)
5. Flag consistency — 短縮形統一、positional vs optional
6. Semantic color tokens — 7トークン（Accent/Command/Pass/Warn/Fail/Muted/ID）
7. Versioning & lifecycle — SIGINT graceful handling、Actor tracking

**根拠**: YouTube CLI の実例、clig.dev コミュニティ、beads UI philosophy

**前提条件**: CLIツールを開発しているプロジェクト。特にAIエージェントから呼び出される可能性があるCLI。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Structured discoverability | Partial | `osa` は cobra で Short/Long あり。Example は未整備 |
| 2 | Agent-first interoperability (`--json`) | Partial | `codex-janitor` のみ JSON 出力。他ツールになし |
| 3 | XDG 準拠 | Already (強化不要) | dotfiles 全体が `~/.config/` ベース |
| 4 | Error guidance | Gap | Hint 行なし。exit code は 0/1 のみ |
| 5 | Flag consistency | Partial | cobra ツールは一貫。shell スクリプトはフラグ体系なし |
| 6 | Semantic color tokens | N/A | hook は非対話。Claude が stdout を解析するため色は不要 |
| 7 | Versioning & lifecycle | Partial | shell/Python スクリプトに SIGINT trap なし |
| 8 | Named environments | N/A | dotfiles は単一環境 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|------------|--------------|--------|
| 3 | XDG 準拠 | — | 強化不要 |
| AGENTS.md | Codex 向けに存在 | CLI discoverability が不足 | CLI Tools セクション追加 |

## Integration Decisions

全4項目を取り込み:
1. **[Gap] Error guidance** — osa に Hint 行追加、リファレンスに exit code 標準定義
2. **[Partial] `--json` 出力** — osa の analyze/list に `--json` グローバルフラグ追加
3. **[Partial] リファレンス** — `references/dual-audience-cli-guide.md` として7原則を保存
4. **[強化] AGENTS.md** — CLI Tools セクション（Short/Long/Example 形式）を追加

スキップ: Semantic color tokens (N/A)、Named environments (N/A)

## Plan

| # | タスク | ファイル | 状態 |
|---|--------|---------|------|
| 1 | リファレンス作成 | `references/dual-audience-cli-guide.md` | done |
| 2 | osa `--json` フラグ | `cmd/root.go`, `cmd/analyze.go`, `cmd/list.go`, `internal/discovery/discovery.go` | done |
| 3 | AGENTS.md CLI Tools セクション | `AGENTS.md` | done |
| 4 | 分析レポート + MEMORY.md | この文書 + MEMORY.md | done |
