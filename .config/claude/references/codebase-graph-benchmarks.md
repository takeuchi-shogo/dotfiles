---
status: reference
last_reviewed: 2026-04-27
related: skills/code-review-graph-guide.md (CRG MCP)
origin: graphify absorb (2026-04-27) — 将来の codebase→graph 再評価のための参照条件
---

# Codebase → Graph: Benchmark 比較と判断基準

「コードベース → 知識グラフ」分野の benchmark 数値を一括記録する。
将来この分野を再評価する際、各ツールの主張条件と再現性を検証可能にするための reference。

## 主要ツール比較

| ツール | benchmark | コーパス条件 | 再現性 | 採用判断 (2026-04-27) |
|--------|-----------|-------------|--------|---------------------|
| **code-review-graph (CRG)** | 8.2x token 削減 | 6 リポジトリ・13 コミット (express 含む) | 中 (express で削減せず) | **採用済み** (`.config/claude/settings.json` MCP 登録) |
| **graphify** | 71.5x token 削減 | Karpathy 52 files (repos+5 papers+4 images) | 低 (混合コーパス特化) | **棄却** (CRG と機能 70% 重複) |
| **Aider repomap** | ~3x token 削減 (推定) | 一般コードベース | 高 (heuristic caching) | 評価対象外 (Claude Code 統合未検証) |
| **MCP Code Indexer** (Anthropic 公式) | 構築中 | 標準化見込み | 未確定 | **GA 待ち** (2026-Q3 目標) |
| **Sourcegraph Cody + GraphRAG** | hallucination -30% | エンタープライズ向け | 中 | エンタープライズスコープ外 |
| **GraphRAG (Microsoft)** | 検索精度 +25-40% | RAG タスク全般 | 高 | 知識グラフ抽出パターンの参考 (provenance タグの源流) |

## 71.5x benchmark の前提条件 (graphify)

graphify の Karpathy benchmark を再現する場合の条件:

- **コーパス**: micrograd, nanoGPT, llm.c (Karpathy 系) + 5 papers + 4 images
- **比較対象**: 全ファイル直読み vs graphify の BFS query 出力
- **計測方式**: tokens read by Claude in (raw_files) / tokens (graph_query_result)
- **既知の偏り**:
  - Karpathy リポジトリは関数間の参照グラフが密で、グラフ化の利得が出やすい
  - 混合コーパス (code + papers + images) の token 比は、コードのみより大幅に有利
  - 一般コードベース (Express, FastAPI 等) では 5-15x 程度に収束

→ **71.5x は「混合コーパス + 高密度参照グラフ」の特化値**。一般コードベースに外挿してはいけない。

## CRG 8.2x benchmark の前提条件

- **コーパス**: 6 リポジトリ (Python/JS 混在)・13 コミット
- **比較対象**: コミット影響範囲を grep で全検索 vs `get_impact_radius_tool`
- **既知の偏り**:
  - express では削減効果が出ず (テスト構造が浅い)
  - 関数粒度の依存が明確なリポジトリで効果大
- **再現性**: 中 (リポジトリ依存が大きい)

## 再評価トリガー

以下のいずれかが発生したら、コードベース→グラフ分野を再評価する:

1. **MCP Code Indexer GA** (Anthropic 公式) — 標準化されたら CRG からの移行を検討
2. **dotfiles 自身が 100k+ LOC** に成長 — incremental update の限界が見えたら再設計
3. **マルチメディア取り込みニーズ** — 動画/音声/画像を knowledge graph に統合する必要が出たら graphify を再評価
4. **CRG の保守停止** — 上流が 6 ヶ月以上更新停止したら代替を検討

## 判断ルール (将来の自分への申し送り)

- benchmark 数値は **コーパス条件込みで** 評価する。"71.5x" だけ取り出さない
- CRG が解決済みの問題に新ツールを乗せない (Pruning-First / Build to Delete)
- マルチメディア統合は dotfiles 単独では ROI 低 (Obsidian 側で digest により処理済み)
- vis.js などのレガシー依存ツールは採用しない (cosmograph.app 等の現代代替を優先)

## Sources

- graphify: https://github.com/safishamsi/graphify (MIT, Python 3.10+, 2026)
- code-review-graph: https://github.com/tirth8205/code-review-graph (Python 3.10+, 2026)
- graphify absorb 分析: `docs/research/2026-04-27-graphify-absorb-analysis.md`
- code-review-graph absorb 分析: `docs/research/2026-03-30-code-review-graph-analysis.md`
- GraphRAG: Microsoft Research, 2024
- Aider repomap: https://aider.chat/docs/repomap.html
