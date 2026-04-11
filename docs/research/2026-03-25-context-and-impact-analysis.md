---
source: https://github.com/ShunsukeHayashi/context-and-impact
date: 2026-03-25
status: analyzed
---

# context-and-impact リポジトリ分析

## Source Summary

**主張**: AIエージェントがコード変更する前に、5層のコンテキスト収集 → 品質ゲート → DAG計画 → ルーティング実行のパイプラインを通すべき。「盲目的なコード変更」を防ぎ、cascade failure を回避する。

**手法**:
- **5層コンテキスト収集**: L0(永続メモリ) → L1(Grep/Glob) → L2a(コールグラフ) → L2b(Wikilink グラフDB) → L3(セマンティック検索)
- **Temporal Decay**: `exp(-0.1 × days)` で古いコンテキストの重みを自動減衰（7日で49.7%、30日で5%）
- **RRF Fusion**: 複数検索レイヤーの結果を `1/(k+rank)` (k=60) で統合ランキング
- **Ensemble Quality Gate**: 3 LLM ジャッジの平均≥70 & 標準偏差≤20 で通過。stddev>20 は `collect_more`
- **Blast Radius DAG**: gitnexus でコード依存グラフ → タスクDAG自動生成
- **Multi-model Task Classifier**: 3モデル多数決でエージェントルーティング（fix→cursor, feat→copilot）
- **ARIA Audit**: 全実行を worklog に記録し cycle-ops で自己改善

**根拠**: 64ユニットテスト。タスク分類器は100%精度。RRF は単一ソースランキングより高精度。Ensemble は single-judge より分散が低い。

**前提条件**: Node.js v24+、gitnexus CLI、Obsidian Vault、複数AIエージェントの並行利用。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Temporal Decay Scoring | **Gap** | メモリに鮮度スコアがない。手動で「古い→削除」だが定量的減衰なし |
| 2 | RRF Fusion | **Gap** | Grep/Glob/Obsidian MCP を個別使用。統合ランキング機構なし |
| 3 | Blast Radius DAG | **Partial** | cross-file-reviewer が変更影響を検出するが、実装前の自動DAG生成はない |
| 4 | L2b Wikilink グラフクエリ | **N/A** | Obsidian MCP で検索・リンク探索は可能。グラフDB導入はオーバーエンジニアリング |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 5 | review-consensus-policy.md §2-3（Agreement Rate + Convergence Stall） | stddev>20 で `collect_more` にフォールバックする段階的 escalation がない。現状は Agreement Rate <70% で一括 CONVERGENCE STALL | stddev ベースの escalation rule を §3 に追加（不一致度が中程度の場合に追加レビューアーを自動起動してから stall 判定） |
| 6 | agent-router.py（キーワードベースのルーティング） | 記事の「fix→深い推論モデル、feat→広いコンテキストモデル」の分類軸が明示的でない | codex-delegation.md にタスク性質別の委譲ガイダンスを追記 |
| 7 | AutoEvolve 4層ループ + progress.log | 記事の ARIA Audit と同等以上 | Already（強化不要） |
| 8 | MEMORY.md + memory files | 記事の project_memory と同等 | Already（強化不要） |
| 9 | Grep/Glob ツール | 差分なし | Already（強化不要） |
| 10 | Obsidian MCP search_notes | SmartConnections MCP と同等 | Already（強化不要） |

## Integration Decisions

取り込み対象（ユーザー選択）:
1. **Temporal Decay Scoring** — references/ にポリシーとして追加
2. **RRF Fusion** — search-first スキルの references に統合ランキングガイドを追加
3. **Blast Radius DAG** — cross-file-reviewer に Pre-Implementation モードを追加
4. **Ensemble stddev gate** — review-consensus-policy.md §3 を拡張
5. **ルーティング分類軸** — codex-delegation.md にタスク性質別ガイダンス追加

スキップ: L2b Wikilink グラフクエリ（N/A）

## Plan

`docs/plans/2026-03-25-context-and-impact-integration.md` を参照。
