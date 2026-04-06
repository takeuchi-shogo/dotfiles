---
source: "Skills can use subagents, Subagents can use skills" (X post on Claude Code agent design)
date: 2026-04-07
status: integrated
---

## Source Summary

Skills と Subagents は相互参照可能な2つの合成パターンを持つ:

1. **Subagent preloads Skills** — `skills:` frontmatter でドメイン知識を起動時に注入。ロール定義向き
2. **Skill delegates to Subagent** — `context: fork` + `agent:` でスキルをサブエージェント内で隔離実行。タスク隔離向き
3. **使い分け基準** — ロール定義 → Agent+Skills、タスク隔離 → Skill+fork、新規 → まずエージェントを作る

前提条件: `context: fork` はタスク指示を含むスキルでのみ有効（ガイドライン系は不可）

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | `context: fork` でスキルを隔離実行 | Partial | `prompt-review` のみ使用。他スキルは Agent tool を本文内で明示呼び出し |
| 2 | Skills ↔ Subagent 使い分け基準の明文化 | Gap | CLAUDE.md に agent_delegation はあるが、合成パターンの判断基準が未文書化 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 1 | 15+ エージェントが `skills:` で知識注入 | なし | 強化不要 |

## Integration Decisions

- **#1 (Partial)**: 取り込み — `context: fork` の活用拡大は個別スキルの改善時に判断（一括変換はしない）
- **#2 (Gap)**: 取り込み — workflow-guide.md の「エージェント委譲パターン」セクションに判断基準テーブルを追加

## Plan

1. `references/workflow-guide.md` の「エージェント委譲パターン」に `#### Skill ↔ Subagent 合成パターン` サブセクションを追加
2. 判断基準テーブル + 注意事項を記載
3. `context: fork` への個別スキル移行は、各スキル改善時に都度検討（一括変換はスコープ外）
