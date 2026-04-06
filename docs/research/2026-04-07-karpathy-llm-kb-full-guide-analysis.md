---
source: "How to create your own LLM knowledge bases today (full course)"
author: "Community (Karpathy method explainer)"
date_analyzed: 2026-04-07
status: integrated
topics: [knowledge-management, wiki, obsidian]
integration_tasks: 7
---

# How to create your own LLM knowledge bases today (full course) — 分析レポート

## Source Summary

**著者**: 不明（Karpathy の手法を解説したコミュニティ記事）
**主張**: LLM のコンテキスト制限を超えるナレッジを、3層アーキテクチャ（raw → wiki → schema）+ 4運用サイクル（Ingest/Compile/Query/Lint）+ Filing loop で管理し、複利的に知識を蓄積するシステム。

**手法**:
1. Three-layer architecture (raw/wiki/schema) — 3層, raw sources, compiled wiki
2. Ingest cycle — source summary, concept pages, entity pages
3. Compile cycle — wiki compile, cross-links, index update
4. Query cycle with filing loop — filing loop, compounding, query re-injection
5. Lint cycle — health check, contradictions, orphan pages, stale content
6. Master index pattern — wiki index, AI navigation, TOC
7. Activity log — append-only, operation log, changelog
8. CLAUDE.md as schema — AI schema, conventions, operations definition
9. Page creation threshold — 2+ sources, stub page, wikilink integrity
10. Two-model validation — cross-validation, hallucination prevention
11. YAML frontmatter conventions — metadata, confidence, source_count
12. Kebab-case naming — filename convention, URL-friendly
13. Incremental compilation — diff update, git-based, append-only
14. Web Clipper integration — browser extension, one-click collection
15. Automation levels (5段階) — CLI, slash commands, scheduled, GitHub Actions, Agent Skills
16. QMD local search — semantic search, keyword search, AI reranking
17. Synthetic data generation — wiki→QA pairs, fine-tuning

**根拠**:
- Karpathy の実運用実績（RAG なしで ~400K words の Q&A が機能）
- Filing loop による複利効果
- Plain text (markdown) = ベンダーロックインなし

**前提条件**:
- ナレッジ量がコンテキストウィンドウを超える規模（100+ pages）
- 週1回以上の更新頻度
- Obsidian + LLM subscription が利用可能

## Gap Analysis

### 判定サマリ

| 判定 | 件数 |
|------|------|
| Already | 12 |
| Partial | 3 |
| Gap | 1 |
| N/A | 1 |

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| NEW | Wiki → Schema 昇格パス | Gap | wiki 知見を CLAUDE.md/references/ に昇格させる明示的ゲートが未文書化 |
| 9 | 定期自動コンパイル | Partial | auto-morning-briefing.sh 存在、wiki 自動コンパイル未接続 |
| 15 | Wiki → 学習データ生成 | Partial | eval-generator.py は session traces → eval data。wiki → QA フロー未実装 |
| 16 | QMD / ローカル検索 | N/A | /compile-wiki query が機能的等価物。Pages ≤500 では Wiki Pattern が最適 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 4 | Filing Loop (/compile-wiki query Step 5) | log.md に query エントリがゼロ = 未使用 | デフォルトで再投入提案に変更 |
| 3 | /compile-wiki lint (read-only) | auto-fix + stub 生成 + 研究質問提案 | --fix オプション追加 |
| 5 | INDEX.md (概念名+1行サマリ) | source count + 概念間関連度が不明 | source_count, related_concepts 追加 |
| 11 | YAML frontmatter | confidence + 検証日時なし | confidence + last_validated + 自動降格提案 |

## セカンドオピニオン統合 (Phase 2.5)

### Codex 批評からの修正

- #10 Web Clipper: Partial → Already (強化不要) に変更。/absorb URL が本質をカバー
- Filing Loop (#4): 分析テーブルに「Already (強化可能)」として追加。log.md に query エントリがゼロ = 未使用
- Wiki → Schema 昇格パス: Gap として新規追加
- INDEX 強化案を拡大: related_concepts フィールド追加
- frontmatter 強化案を拡大: last_validated フィールド追加

### Gemini 周辺知識からの補足

- **Hallucination 累積リスク**: Filing loop の Gen v3+ で 35-45% リスク。Two-model validation を query 再投入時にも検討
- **メンテナンスコスト**: 大規模で月 150+ 分、自動化で 30-40% 削減
- **現在規模は最適範囲内**: Pages ≤500, Queries ≤100/月 では Wiki Pattern が最適

## Integration Decisions

**取り込み（全部）**: Gap/Partial 3項目 + Already 強化 4項目 = 計7項目

## Plan

| 優先 | Task | 内容 | 規模 | 変更ファイル |
|------|------|------|------|------------|
| 1 | T1: Filing Loop 実効化 | query Step 5 を「デフォルトで再投入提案」に変更 | S | compile-wiki/SKILL.md |
| 1 | T2: Frontmatter 強化 | confidence + last_validated 追加、Check 4 自動降格 | S | compile-wiki/SKILL.md |
| 2 | T3: INDEX 強化 | source_count, related_concepts 追加 | S | compile-wiki/SKILL.md |
| 2 | T4: Lint auto-fix | lint --fix サブコマンド追加 | M | compile-wiki/SKILL.md |
| 3 | T5: Wiki → Schema 昇格 | promote サブコマンド追加 | M | compile-wiki/SKILL.md |
| 3 | T6: 定期自動コンパイル | morning briefing に wiki update 接続 | S | auto-morning-briefing.sh |
| 4 | T7: Wiki → QA 生成 | generate-data サブコマンド追加 | M | compile-wiki/SKILL.md |

**全体規模**: M-L（~150行追加/変更）
