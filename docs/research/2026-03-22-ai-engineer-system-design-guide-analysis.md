---
status: active
last_reviewed: 2026-04-23
---

# AI Engineer System Design Interview Guide 分析

**書籍**: The AI Engineer's System Design Interview Guide (Volume 1)
**著者**: Lamhot Siagian (AI Engineering Insider)
**版**: 2026 edition
**入手範囲**: プレビュー版（16ページ / 全90ページ）— 目次全章 + Ch1-2 の実コンテンツ
**ソース**: `~/Downloads/AI Engineer System Design.pdf`

## 書籍概要

RAG・LLMシステム設計のインタビュー準備ガイド。各章は「Core Concepts（概念整理）」+「Tough Questions（面接質問と模範解答）」の2部構成。2026 edition では各章に「なぜ本番環境で重要か」の解説を追加。

## 全13章 + ボーナスセクション

| # | テーマ | 本セットアップへの活用度 |
|---|--------|----------------------|
| 1 | RAG Fundamentals | 中 — RAG vs Fine-tuning 判断基準、6つの RAG 失敗モード |
| 2 | Advanced Retrieval Design | 中 — Hybrid Retrieval (BM25+Vector), Re-ranking, Multi-hop |
| 3 | RAG Architecture (Production) | **高** — Planner-Executor-Verifier, Stateful RAG, Tool Calling |
| 4 | Evaluation & Metrics | **高** — RAGAS, Retrieval vs Generation 分離評価 |
| 5 | Hallucination & Reliability | **高** — Grounded Generation, Confidence Scoring, Refusal 設計 |
| 6 | Performance & Scaling | 中 — ANN (HNSW/IVF), TTFT 最適化, Caching vs Recomputation |
| 7 | Data Pipeline & Ingestion | 中 — Document Parsing, Incremental Updates, Data Freshness |
| 8 | Security & Enterprise RAG | **高** — Access Control, Multi-tenant Isolation, PII Filtering |
| 9 | Agentic RAG | **最高** — Planner-Executor-Verifier, LangGraph, CrewAI, Tool Orchestration |
| 10 | Prompt Engineering for RAG | **高** — Context Injection Patterns, Structured Outputs, Context Overflow 防止 |
| 11 | Observability & Monitoring | **最高** — What to Log, Tracing, Drift Detection, Feedback Loops |
| 12 | Deployment & LLMOps | 中 — CI/CD for RAG, Model Versioning, A/B Testing, Canary |
| 13 | LLM Inference Optimization | 中 — KV Cache, Paged Attention, Continuous Batching |
| Bonus | 20 Top System Design Q&A | **高** — Production RAG 設計の集大成（28問） |
| Bonus | RAG & AI Systems Challenge Trends | **高** — 未解決課題の体系化（7カテゴリ） |

## Ch1-2 から抽出した具体的パターン（実コンテンツあり）

### RAG 失敗モード分類（Ch1.2.1）
1. **Retrieval fails** — 正しいチャンクが返らない
2. **Chunk size mismatch** — 回答が複数チャンクにまたがる
3. **Semantic gap** — クエリとドキュメントの語彙ギャップ
4. **Multi-hop reasoning** — 複数文書の事実を組み合わせる必要
5. **Temporal** — インデックスが古い
6. **LLM ignores context** — パラメトリック知識を優先

**Fix strategy**: Retrieval と Generation を分離評価。Recall@K が低ければ chunking/embedding を修正、Faithfulness が低ければプロンプトを修正。

### Hybrid Retrieval 設計パターン（Ch2.2.1）
- **Indexing**: Recursive splitter (512 tokens, 64 overlap) + BGE-large-en (1024 dims) + BM25
- **Query time**: LLM Query Rewrite → Dense top-20 + Sparse top-20 → RRF (0.3/0.7) → Cross-encoder Re-rank → top-5
- **Quality controls**: Cosine similarity < 0.65 をドロップ、重複除去

### Query Rewriting テクニック（Ch2.1.2）
- **Multi-query**: 3-5 reformulations → union
- **HyDE**: 仮想回答を生成 → embed（ドキュメント分布に近い）
- **Step-back**: 抽象化した質問で基礎コンテキストを取得

### Vector DB 選択マトリクス（Ch1.1.4）
| DB | 強み | 用途 |
|---|---|---|
| FAISS | In-memory, 最速 | Research, single node |
| Pinecone | Managed, serverless | SaaS, low ops |
| Chroma | Easy local dev | Prototypes |
| Weaviate | Hybrid search native | Production enterprise |
| Qdrant | Fast, Rust-native | High throughput |
| pgvector | PostgreSQL extension | 既存PGユーザー |

### Embedding モデル選定（Ch1.2.2）
- Dimensionality: 高次元 (1536) = 表現力↑ / コスト↑
- Domain-specific approach: text-embedding-3-large → MTEB eval → fine-tune on domain triplets → MRL embeddings

## 既存セットアップとのシナジー分析

### 1. Agentic RAG (Ch9) → agent-router.py / completion-gate.py
- **Planner-Executor-Verifier** パターンは本セットアップの agent delegation + review pipeline に直接対応
- 「infinite loop 回避」→ stagnation-detector.py と相補的
- 「agent performance 評価」→ AutoEvolve evaluator 改善に活用

### 2. Evaluation (Ch4) → evaluator-calibration-guide.md
- RAGAS メトリクス (Faithfulness, Answer Relevancy, Context Precision) → 定量評価指標の追加
- Retrieval vs Generation 分離評価 → precision/recall を段階別に測定する発想

### 3. Observability (Ch11) → OTel AI Agent Observability
- What to Log / Tracing / Drift Detection → 3階層 Span 設計との直接シナジー
- Feedback Loop 設計 → AutoEvolve 4層ループの改善

### 4. Hallucination & Reliability (Ch5) → overconfidence-prevention.md
- Grounded Generation / Citation Enforcement → エージェント出力の根拠づけ
- Confidence Scoring & Refusal → 「分からないときは正直に言う」の定量化

### 5. Security (Ch8) → agency-safety-framework.md
- Access Control / PII Filtering / RAG Audit → OWASP MCP Top 10 との統合

### 6. Prompt Engineering for RAG (Ch10) → skill 設計
- Context Injection Patterns → Progressive Disclosure と整合
- Context Overflow 防止 → compact-instructions.md との相互参照

### 7. Challenge Trends → 未解決課題の共有認識
- Retrieval Quality, Context & Memory, Data Freshness, Faithfulness, Observability, Security, Architecture — 7カテゴリの未解決課題を体系的に把握

## 統合方針

プレビュー版のため、**目次ベースの知見抽出**を中心に実施:

1. **references/ai-system-design-checklist.md** — 60+ Tough Questions をデザインチェックリストとして整理
2. Ch1-2 の具体的パターンを既存 references と統合（重複なしで補完）
3. MEMORY.md にエントリを追加

フルブック入手時は `/absorb` で章ごとの詳細統合を実施する。
