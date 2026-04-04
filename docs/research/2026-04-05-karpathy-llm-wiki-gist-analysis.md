---
source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
date: 2026-04-05
status: integrated
prior_analysis: 2026-04-03-karpathy-llm-knowledge-bases-analysis.md
---

## Source Summary

**主張**: RAG（毎回ゼロから検索・合成）ではなく、LLM が永続的な wiki を漸進的に構築・保守する。wiki は複利で蓄積される知識資産であり、ソースを追加するたびにリッチになる。人間はキュレーションと探索に集中し、LLM が要約・相互参照・整理・簿記を担当する。

**手法**:
1. **3層アーキテクチャ**: Raw Sources（不変のソースドキュメント）→ Wiki（LLM が書く構造化 markdown）→ Schema（CLAUDE.md 等の運用規約）
2. **Ingest**: ソース追加時に要約ページ作成 + 既存ページ横断更新（1ソースで10-15ページ更新）+ index/log 更新
3. **Query**: index.md → 関連ページ読み → 合成回答。良い回答は wiki に再投入して知識を蓄積
4. **Lint**: 矛盾検出、陳腐化チェック、孤立ページ、欠損リンク、新たな調査提案
5. **index.md**（内容カタログ）+ **log.md**（時系列操作ログ）の2ファイル分離
6. **qmd** 等のローカル検索エンジン（規模が大きくなったら）

**根拠**: Karpathy 本人の実践。~100ソース、~400K words で RAG 不要の Q&A が機能。Vannevar Bush の Memex (1945) の精神的後継。

**前提条件**: ファイルシステムアクセス可能な LLM エージェント、Obsidian 推奨、ある程度の規模のリサーチトピック。

**前回分析(04-03)との差分**: 前回は Twitter 投稿ベースで7ステップモデル。今回は GitHub Gist として洗練され、3層アーキテクチャの明確化、log.md の分離、Query 操作の形式化、use case の拡充が追加。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 3層アーキテクチャ | Already | `docs/research/` = Raw, `docs/wiki/` = Wiki, `CLAUDE.md` + `references/` = Schema |
| 2 | Ingest 操作 | Already | `/absorb` → `/compile-wiki` パイプライン |
| 3 | Query 操作（INDEX → ドリルダウン → 合成） | Partial | wiki は存在するが「wiki に問い合わせる」明示的ワークフローが未定義 |
| 4 | Lint 操作 | Already | `/compile-wiki` lint + `/check-health` |
| 5 | log.md（時系列操作ログ） | Gap | wiki 操作の時系列ログが存在しない |
| 6 | Query 結果の wiki 再投入 | Partial | `/eureka` がブレイクスルー記録。一般的 Q&A の wiki フィードバック未対応 |
| 7 | 検索 CLI (qmd 等) | Already | code-review-graph MCP + Obsidian MCP + Grep |
| 8 | Obsidian tips | Already | Obsidian 統合実装済み |
| 9 | Schema 層の明示化 | Already | CLAUDE.md + references/ + rules/ |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す視点 | 強化案 |
|---|-------------|---------------|--------|
| 4 | `/check-health` + compile-wiki lint | 概念ページ間の矛盾検出を明示 | 同一トピック内で相反する主張を検出するチェック追加 |

## Integration Decisions

前回(04-03)の統合で大部分は実装済み。今回は差分4項目を取り込み:
1. [Gap] log.md 導入
2. [Partial] Query ワークフロー明示化
3. [Partial] Q&A 結果の wiki 再投入強化
4. [強化] 概念間矛盾検出追加

## Plan

規模: M（4-5ファイル変更）。同一セッションで実行。

- Task 1: `docs/wiki/log.md` 作成 + `/absorb`, `/compile-wiki` に log 追記ステップ追加
- Task 2: `/compile-wiki` に `query` サブコマンド追加
- Task 3: `/compile-wiki` に Q&A 結果フィードバック手順追加
- Task 4: `/compile-wiki` lint に概念間矛盾検出追加
