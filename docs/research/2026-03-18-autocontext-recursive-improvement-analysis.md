---
source: "autocontext: The Recursive Self-Improving Loop (greyhaven-ai/autocontext)"
date: 2026-03-18
status: analyzed
---

## Source Summary

### 主張

エージェントは実行ごとにコールドスタートし、学習が蓄積しない。autocontext は「実行→評価→学習→永続化→再実行」のクローズドループで、世代を跨いだ知識蓄積と自己改善を実現する。

### 手法

1. **Multi-agent evaluation pipeline**: Competitor → Translator → Analyst → Coach → Architect → Curator の6役 + Orchestrator
2. **Playbook abstraction**: 世代を跨いで成長する「生きたドキュメント」— 成功戦略、失敗モード、ティア別ルールを蓄積
3. **Elo-based progression gating**: 改善しない戦略はロールバック。検証済みの知識のみ永続化
4. **Multi-dimensional rubric judging**: 複数次元（accuracy, clarity, actionability等）で独立評価。最弱次元を狙い撃ち改善
5. **Parse resilience (4-tier fallback)**: JSON → raw JSON → regex → structured retry
6. **Frontier-to-local distillation**: フロンティアモデルで発見 → MLX ローカルモデルに蒸留
7. **Domain-agnostic scenario system**: ゲーム（客観Eloスコア）+ エージェントタスク（LLMジャッジ+ルブリック）
8. **MCP server integration**: `autoctx mcp-serve` で外部エージェントから操作

### 根拠

Grid CTF で2世代で33個のレッスン蓄積、5,870文字の actionable playbook を自動生成。populated playbook でコールドスタートを大幅に上回る。

### 前提条件

繰り返し実行可能なタスク・評価基準の定義が必要。1回限りのタスクには不向き。

## Gap Analysis

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Multi-agent pipeline (6役) | **Partial** | AutoEvolve 3フェーズ + 並列レビューあり。役割の粒度が粗い |
| 2 | Playbook abstraction | **Already** | session-learner.py → playbooks/{project}.md。100行上限、recovery-tips あり |
| 3 | Elo-based progression gating | **Gap** | A/B delta > +2pp のみ。累積的品質指標なし |
| 4 | Multi-dimensional rubric | **Partial** | 複数レビューアー並列だが「次元別スコア」の構造化なし |
| 5 | Parse resilience | **N/A** | ツールベース構造化出力のため不要 |
| 6 | Frontier-to-local distillation | **Partial** | ドキュメント蒸留パスあり。モデル蒸留は対象外 |
| 7 | Scenario-based benchmarking | **Gap** | 個別スキル A/B はあるが包括的シナリオ基盤なし |
| 8 | MCP server integration | **N/A** | MCP クライアント側。サーバー公開は不要 |

## Integration Decisions

全5項目を取り込む:

1. **[Gap → 取込] 競争的評価メカニズム** — experiment_tracker に累積品質スコア追加
2. **[Partial → 強化] 次元別レビュールブリック** — レビューアー出力に次元別スコア追加
3. **[Gap → 取込] セットアップ統合ベンチマーク** — シナリオベースのベンチマーク基盤
4. **[Partial → 強化] 知識蒸留パスの標準化** — 蒸留ルールの明文化
5. **[Partial → 強化] 改善パイプラインの役割分離** — autoevolve-core のサブロール定義

スキップ: Parse resilience (N/A), MCP server (N/A)

## Plan

→ `docs/plans/active/2026-03-18-autocontext-integration.md` に詳細プランを保存
