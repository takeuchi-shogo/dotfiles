---
source: "How To Transform Claude Code Into A Self-Evolving System [FULL GUIDE]"
date: 2026-03-30
status: integrated
---

## Source Summary

4層の自己進化システムを構築するガイド:
1. **Cognitive core** (CLAUDE.md) — decision framework + completion criteria
2. **Specialized agents** — architect (planner) + reviewer (validator)
3. **Path-scoped rules** — security/api-design/performance がファイルパスで条件発火
4. **Evolution engine** — corrections.jsonl → learned-rules.md (verify: 行付き) → CLAUDE.md への promotion ladder

核心的アイデア: "A rule without a verification check is a wish. A rule with a verification check is a guardrail. Only guardrails survive."

## Gap Analysis

### Gap / Partial

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | verify: 行付き learned-rules | Gap | lessons-learned.md に verify: なし |
| 2 | Session scoring + トレンド検出 | Gap | セッション単位メトリクス未追跡 |
| 3 | Verification sweep | Gap | SessionStart hook はあるが grep 検証なし |
| 4 | core-invariants.md (paths: **/*) | Gap | 全ファイル触発の圧縮耐性ルールなし |
| 5 | corrections.jsonl (構造化ログ) | Partial | feedback .md はあるが JSONL + count 追跡なし |
| 6 | Promotion ladder (自動昇格) | Partial | knowledge-pyramid はあるが count ベース自動昇格なし |

### Already 項目の強化分析

| # | 既存 | 強化案 |
|---|------|--------|
| A | AutoEvolve (/improve + meta-analyzer) | verify: 行統合で機械検証を追加 (強化可能) |
| B | Hook 体系 (Rust claude-hooks) | 既に十分高度 (強化不要) |
| C | Path-scoped rules (12+ ファイル) | core-invariants.md で圧縮耐性追加 (強化可能) |
| D | Memory system (MEMORY.md + 個別ファイル) | session metrics で定量化 (強化可能) |
| E | Permission allow/deny | 既に包括的 (強化不要) |
| F | Decision framework (core_principles) | 既に同等以上 (強化不要) |

### N/A

- npm/TS 固有テンプレート、基本 CLAUDE.md、2エージェント構成 — 既存が遥かに高度

## Integration Decisions

全 Gap/Partial + 強化可能 Already を統合:
1. core-invariants.md 新設 → `.config/claude/rules/common/core-invariants.md`
2. lessons-learned.md に verify: 行追加
3. improve-policy.md に verification sweep + session metrics + promotion ladder 追加

## Plan

| # | タスク | ファイル | 規模 |
|---|--------|---------|------|
| 1 | core-invariants.md 新設 | rules/common/core-invariants.md | S |
| 2 | lessons-learned.md に verify: 行追加 | references/lessons-learned.md | S |
| 3 | improve-policy 拡張 (sweep + metrics + ladder) | references/improve-policy.md | M |

スキップした記事の要素:
- corrections.jsonl / observations.jsonl / sessions.jsonl — 既存の feedback memory + learnings/*.jsonl で同等機能。並列システムの導入は複雑さ増大
- evolution/SKILL.md (自動トリガースキル) — 既存の AutoEvolve + hooks が同等機能を提供
- /boot スキル — 既存の SessionStart hook + /check-health で代替
- /evolve コマンド — 既存の /improve が同等以上の機能
