---
source: "The Ultimate Guide for a Working Agent Memory (article, 2026)"
date: 2026-03-30
status: integrated
---

## Source Summary

**主張**: エージェントメモリの84%は操作テレメトリ（ノイズ）。品質ゲート付きの構造化メモリ + 人間可読な Obsidian Vault がこれを解決する。

**手法**:
1. 3層品質ティア: Operational(LOW) / Behavioral(MEDIUM) / Cognitive(HIGH)
2. Research Packets: Claim/Mechanism/Boundary/Contradiction の4フィールド構造化知識ユニット
3. 5段階 Promotion Ladder: draft → candidate → promoted → benchmark_grounded → realworld_validated
4. Doctrine Synthesis: 3+ packets が同タグ → meta-doctrine 合成
5. Lessons Learned: 1行 gotcha ファイル（最重要ファイルとされる）
6. Decision Journal: 決定 + 根拠パケット + 期待/実際結果の追跡
7. Memory Dashboard: 週次パケット統計・カバレッジ・ギャップ
8. UCB1 Multi-Armed Bandit: パケット選択最適化フィードバック
9. 品質ゲートテスト: "Would a human find this useful next time?"

**根拠**: 著者の長期実験。定量データは84%ノイズ率のみ。実践的知見に基づく。

**前提条件**: 継続的に同一プロジェクトで作業するエージェント。メモリの量が増えてノイズ問題が顕在化している環境。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Research Packets (Claim/Mechanism/Boundary/Contradiction) | Gap | docs/research/ は分析レポート形式。原子的構造化ユニットなし |
| 2 | Lessons Learned (1行 gotcha) | Gap | feedback メモリは個別ファイル、learnings は JSONL。集約なし |
| 3 | Decision Journal | Partial | docs/adr/ に ADR あるが日常決定ログなし |
| 4 | Doctrine Synthesis | Partial | contradiction-mapping.md で矛盾検出のみ、合成メカニズムなし |
| 5 | Memory Dashboard | Gap | メモリ専用の統計ダッシュボードなし |
| 6 | UCB1 Bandit | N/A | AutoEvolve scoring + Garden で同等機能を実現済み |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| A | knowledge-pyramid.md (4層昇格) | 5段階で validated を分離 | 強化不要 — Tier 3 条件が実質 validated |
| B | メモリ type 分類 + "What NOT to save" | 84%ノイズ問題 | 強化 — Garden フェーズにノイズ判定基準追加 |
| C | 品質ゲート (昇格条件) | 1行テスト | 強化不要 — 既存条件の方が具体的 |

## Integration Decisions

**取り込み**: #1(Packets構造→lessons-learnedに統合), #2(Lessons Learned), #3(Decision Journal), #4(Doctrine Synthesis), #5(Dashboard), #B(ノイズ判定基準)
**スキップ**: #6(UCB1 — 過剰複雑化), #A(4層で十分), #C(既存条件で十分)

## Plan (実行済み)

| タスク | 対象ファイル | 状態 |
|--------|-------------|------|
| Lessons Learned 1行 gotcha ファイル | `references/lessons-learned.md` | done |
| Decision Journal | `references/decision-journal.md` | done |
| ノイズ判定基準 | `references/improve-policy.md` | done |
| Doctrine Synthesis 手順 | `references/knowledge-pyramid.md` | done |
| Memory Dashboard | `skills/memory-status/SKILL.md` | done |
