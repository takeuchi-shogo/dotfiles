---
source: "Matt Pocock — 5 Agent Skills I Use Every Day"
date: 2026-04-04
status: integrated
---

## Source Summary

AIエージェントは「記憶のない中堅エンジニア」であり、厳密なスキルでプロセスをエンコードすることでコード品質が劇的に向上するという主張。5つのスキルを日常的に使用:

1. **grill-me**: Design Tree（Brooks）の全分岐を走破する執拗なインタビュー。たった3文だが高インパクト
2. **write-a-prd**: インタビュー → PRD 生成 → GitHub Issue 投稿の一気通貫
3. **prd-to-issues**: PRD を垂直スライス（Tracer Bullet）に分解。blocking 関係付きの独立 Issue 群
4. **tdd**: Red-Green-Refactor ループ。Deep Modules 哲学込み
5. **improve-codebase-architecture**: 浅いモジュール → 深いモジュールへの週次改善。エージェントフレンドリーなコード構造

**根拠**: Design Tree (Frederick P. Brooks), Tracer Bullet（垂直スライス）, Deep Modules, TDD ループ構造とエージェントの相性

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | prd-to-issues | Gap | `/spec` で PRD 生成、`/create-issue` で単発 Issue は可能。PRD → 垂直スライス分解 → blocking 関係付き複数 Issue という一連のフローがない |
| 2 | improve-codebase-architecture | Partial | `references/agent-native-code-design.md` に5原則があるが、能動的にコードベースを探索して改善候補を提案するスキルがない |

### Already 項目の強化分析

| # | 既存の仕組み | 記事の知見 | 強化判定 |
|---|-------------|-----------|---------|
| 1 | `/grill-interview` (origin: mattpocock/skills/grill-me) | 3文のインタビュースキル | 強化不要 — 既に AI 推奨回答付きで拡張済み |
| 2 | `/spec` + `/interview` + `/create-issue` | write-a-prd（インタビュー→PRD→Issue投稿） | 強化不要 — 3スキル連携で同等以上 |
| 3 | `superpowers:test-driven-development` + `tdd-guard.py` | TDD (Red-Green-Refactor + Deep Modules) | 強化不要 — superpowers スキル + policy hook で強制力あり |

## Integration Decisions

- **採用**: prd-to-issues, improve-codebase-architecture の両方
- **スキップ**: grill-me, write-a-prd, tdd（既に同等以上の仕組みが存在）

## Plan

1. `/prd-to-issues` スキル新規作成 — `.config/claude/skills/prd-to-issues/SKILL.md`
2. `/improve-codebase-architecture` スキル新規作成 — `.config/claude/skills/improve-codebase-architecture/SKILL.md`
3. 分析レポート保存（本ファイル）
