---
source: https://github.com/rohitg00/agentmemory
date: 2026-04-05
status: integrated
---

## Source Summary

### 主張
エージェントの built-in メモリ（CLAUDE.md 等のフラットファイル）はオーバーフローし陳腐化する。検索可能・バージョン管理された DB ベースの永続メモリで、セッション横断の記憶を高精度に提供すべき。

### 手法
1. **Triple-stream hybrid 検索** — BM25 + vector embedding + knowledge graph traversal を RRF (k=60) で融合
2. **4層統合パイプライン** — Working → Episodic → Semantic → Procedural に段階的圧縮
3. **Ebbinghaus decay** — 忘却曲線に基づく記憶の重み減衰
4. **Contradiction detection** — 矛盾するメモリの自動検出・解決
5. **Cascading staleness** — 1つの記憶が古くなると関連ノードも自動フラグ
6. **Importance-based eviction** — 10K 上限 + 重要度スコアによる淘汰
7. **Auto-observation capture** — 12 hooks でツール使用・ファイル編集・テスト・エラーを自動記録
8. **Knowledge graph** — エンティティ抽出、関係マッピング、信頼度スコア、時間バージョニング
9. **Multi-agent coordination** — リース、シグナル、P2P mesh sync

### 根拠
240 observations / 30 sessions での実測値。Recall@10: 64.1% vs 55.8%（built-in）、トークン 92% 削減、MRR 100%。

### 前提条件
TypeScript エコシステム、iii-sdk 依存、Claude Agent SDK 前提。MCP プロトコル対応環境。16K LOC / 70+ ツール。

### Karpathy アプローチとの比較

agentmemory は「Karpathy の実装」と言われることがあるが、設計哲学は根本的に異なる:

| 観点 | Karpathy | agentmemory |
|------|----------|-------------|
| 核心 | LLM = compiler（知識を能動的に構造化） | DB = retriever（observation を高精度検索） |
| 媒体 | Markdown wiki（Obsidian） | KV + vector index + knowledge graph |
| 検索 | LLM が wiki をナビゲート（RAG 不要） | RAG の進化版（triple-stream） |
| 可読性 | 人間が直接読める、git diff で追跡 | DB 内部はブラックボックス |
| 複雑度 | ミニマル | 16K LOC、106 API |
| 哲学 | "less knowledge, better cognition" | "more data, better retrieval" |

**重なる部分:** セッション横断永続メモリ、自動統合/圧縮、陳腐化検出。
**決定的な違い:** Karpathy は「構造化 Markdown を LLM がメンテする」、agentmemory は「DB にすべて入れて検索精度で勝つ」。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Triple-stream hybrid 検索 | N/A | Grep/Glob + LLM ナビゲーション。Karpathy 哲学と同じく vector DB 不使用 |
| 2 | 4層統合パイプライン | Already | knowledge-pyramid.md (4層) + 蒸留パイプライン L0-L4 |
| 3 | Ebbinghaus decay | Partial | temporal-decay-policy.md にドキュメント鮮度スコアあり。メモリ重要度加重なし |
| 4 | Contradiction detection | Already | contradiction-mapping.md に 3種分類 + 5ステップ解決フロー |
| 5 | Cascading staleness | Partial | staleness-detector.py が hook 単体検出。メモリ間伝播なし |
| 6 | Importance-based eviction | Gap | メモリ上限管理なし。MEMORY.md 手動管理 |
| 7 | Auto-observation capture | Already | session_events.py + hook テレメトリ + session-learner.py |
| 8 | Knowledge graph | N/A | code-review-graph MCP + wiki バックリンクで十分 |
| 9 | Multi-agent coordination | N/A | worktree + cmux Worker で管理。単一ユーザーにリース不要 |

### Already 項目の強化分析

| # | 既存の仕組み | agentmemory が示す弱点 | 判定 |
|---|-------------|----------------------|------|
| 2 | knowledge-pyramid (4層昇格) | 昇格が手動判定 | Already (強化不要) — /improve Garden が半自動実行 |
| 4 | contradiction-mapping | 検出が手動チェック | Already (強化可能) — /check-health に自動スキャン追加 |
| 7 | session_events + テレメトリ | 構造化度が低い | Already (強化不要) — JSONL + session-learner で十分 |

## Integration Decisions

全4項目を取り込み:
1. [Partial→強化] Ebbinghaus decay にメモリ重要度加重追加
2. [Partial→強化] Cascading staleness にメモリ間関連伝播追加
3. [Gap→新規] Importance-based eviction スクリプト
4. [Already→強化] /check-health に矛盾自動スキャン追加

## Plan

| # | タスク | 変更先 | 規模 |
|---|--------|--------|------|
| 1 | Decay メモリ適用拡張 | references/temporal-decay-policy.md | S |
| 2 | Cascading staleness 伝播 | scripts/learner/staleness-detector.py | S |
| 3 | Importance-based eviction | 新規: scripts/learner/memory-eviction.py | M |
| 4 | 矛盾自動スキャン | skills/check-health/SKILL.md + 新規: scripts/learner/contradiction-scanner.py | M |
