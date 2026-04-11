---
source: "Three Blocks That Make Claude Get Smarter Every Session (ProductCompass)"
date: 2026-04-02
status: skipped
---

## Source Summary

**主張**: Memory without reflection is just storage。3ブロック（Knowledge Architecture / Decision Journal / Quality Gate）+ Maintenance Schedule で複利的に賢くなるシステムを構築できる。

**手法**:
1. **Knowledge Architecture**: タスク前 Active Retrieval + 3層階層（observation → hypothesis → rule）+ Promotion/Demotion cycle。1ヶ月で24の自己生成ルール蓄積
2. **Decision Journal**: 意思決定前の既存検索 + フルコンテキスト記録（決定/代替案/理由/トレードオフ）+ 置換チェーン。ADR に類似
3. **Quality Gate**: プロジェクト固有の具体的・テスト可能な評価基準 + 基準の進化（昇格/自動ゲート化/剪定）。Definition of Done に類似
4. **Maintenance Schedule**: 定期レビュー提案（stale rule 剪定、仮説昇格判断、トレードオフ検証）

**前提条件**: マルチセッション利用、CLAUDE.md ベースのセットアップ、十分なセッション量

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Active Retrieval（タスク前の既存知識強制検索） | Partial | `/check-health` + `search-first` 原則はあるが明示的 hook なし。ただし Doctrine が `rules/` や CLAUDE.md にロードされるため暗黙カバー |
| 2 | Maintenance Schedule | N/A | `/improve`(cron+オンデマンド) + `/weekly-review` + `/timekeeper` で完全カバー |

### Already 項目の強化分析

| # | 既存の仕組み | 記事の対応概念 | 判定 |
|---|-------------|---------------|------|
| 1 | Knowledge Pyramid (4層 Tier 0-3 + 昇格/降格条件 + Doctrine Synthesis) | Knowledge Architecture (3層) | Already (強化不要) — 既存が上位互換 |
| 2 | Decision Journal (状況/選択/根拠/期待/実際 + timekeeper 連携 + tier 昇降格) | Decision Journal (ADR 類似) | Already (強化不要) — 同等設計 + 追加連携あり |
| 3 | DoD Template + completion-gate.py + Codex Review Gate + improve-policy 32ルール | Quality Gate (進化する評価基準) | Already (強化不要) — 大幅に上回る |
| 4 | decision-journal → tier 昇降格、improve-policy → rules 改善 | 相互強化ループ | Already (強化不要) — 同等のループ接続済み |

## Integration Decisions

全項目スキップ。理由: 既存セットアップが記事の提案を全次元で上回っている。

- Knowledge Architecture: 記事の3層に対し4層 + スコア定量化 + Doctrine Synthesis + AutoEvolve 連携
- Decision Journal: ほぼ同一設計が実装済み + timekeeper/improve 自動連携
- Quality Gate: DoD Template + completion-gate.py + Codex Review Gate + 32ルール improve-policy + Goodhart 警告
- 唯一の Partial (Active Retrieval) は Doctrine → rules/CLAUDE.md ロードで暗黙カバー済み
