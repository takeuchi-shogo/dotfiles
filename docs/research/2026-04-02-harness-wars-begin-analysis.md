---
source: "The Harness Wars Begin" (blog post, 2026-04)
date: 2026-04-02
status: integrated
---

## Source Summary

### 主張
Claude Code ソースコードのリーク（v2.1.88, ~512K行, 1,906 TS ファイル）により、ハーネスエンジニアリングの参照アーキテクチャが公開され Cambrian Explosion が始まった。しかし真の競争は CLI ではなくドメイン固有のコンテキストアーキテクチャにある。

### 手法/パターン
1. **Harness commoditization awareness** — CLI 部分はコモディティ化。差別化はドメイン固有コンテキスト
2. **"Similarity ≠ Relevance"** — RAG/VectorDB は what を返すが why を返さない。Context Graph が次世代
3. **Domain-specific harness** — compaction/false-claims/state management の意味がドメインごとに異なる
4. **Audit trail as differentiator** — "What did your system actually do?" に答えられるか
5. **Strong Primitives First** — security, auth, data storage が先
6. **False claims awareness** — Capybara v8 で 29-30%（v4: 16.7%）
7. **Fork agent parallelism limits** — 5×200K = ~1M tokens だが consistency 未解決
8. **Protocol > Model** — 協調プロトコル 44% vs モデル選択 14%（Dochkina 2026）

### 根拠
- Claude Code v2.1.88 ソース分析、instructkr/claw-code (74.7K stars)
- Capybara v4→v8 false claims rate データ
- Dochkina 2026 (25K tasks)
- HydraDB ($6.5M raise)

### 前提条件
- ハーネスを構築・改善している開発者/チーム向け
- ソフトウェア開発以外のドメインへの拡張を視野に入れた思考フレーム

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | "Similarity ≠ Relevance" / why capture | Partial | MEMORY.md はポインタ、session-trace-store.py は raw データ。decision-journal.md は計画のみ未実装 |
| 2 | Audit trail queryability | Partial | session-trace-store.py で raw 保存済みだがクエリ手段なし |
| 3 | Domain-specific harness | N/A | coding harness として設計 |
| 4 | Context graph DB (HydraDB 的) | N/A | dotfiles ハーネスのスコープ外。code-review-graph MCP が部分対応 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点/視点 | 強化案 | 判定 |
|---|-------------|---------------------|--------|------|
| 1 | Build to Delete + Scaffolding > Model | CLI 超えてドメイン拡張 | — | 強化不要 |
| 2 | Dochkina 44% vs 14% | 同データ引用 | — | 強化不要 |
| 3 | Trust Verification Policy | multi-agent blast radius 欠如 | agency-safety-framework に追加 | 強化可能 |
| 4 | derivation-honesty + completion-gate | Capybara v8: 29-30% 定量データ | resource-bounds.md に追記 | 強化可能 |
| 5 | Context rot 対策 | compaction 後 re-grounding 未明文化 | resource-bounds.md に追記 | 強化可能 |

## Integration Decisions

全5項目を取り込み:
- **#3 multi-agent blast radius** → agency-safety-framework.md に並列数×blast radius テーブル + チェックリスト追加
- **#4 false claims rate** → resource-bounds.md に Capybara v4→v8 データ + 設計含意追加
- **#5 compaction re-grounding** → resource-bounds.md に Re-grounding ルール 4項目追加
- **#1 why capture** → 既存プラン（Agent Memory Quality Guide: decision-journal.md）で対応。本分析レポートで参照
- **#2 audit trail query** → 既存プラン（Trace Learning: situation-strategy-map）で対応。本分析レポートで参照

## Skipped

- Domain-specific harness: N/A（coding harness のスコープ）
- Context graph DB: N/A（dotfiles のスコープ外。code-review-graph MCP が部分対応）
- Harness commoditization awareness: Already（Build to Delete 原則で十分カバー）
