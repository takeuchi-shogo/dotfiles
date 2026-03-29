# AI System Design Checklist

Source: "The AI Engineer's System Design Interview Guide" (Lamhot Siagian, 2026)
分析メモ: `docs/research/2026-03-22-ai-engineer-system-design-guide-analysis.md`

AI/RAG システムの設計・レビュー時に使用するセルフチェックリスト。
各質問は本番環境での設計判断を検証するためのもの。

---

## 1. RAG Fundamentals

- [ ] RAG vs Fine-tuning vs Long-context LLM の選択根拠は明確か？
- [ ] RAG の6つの失敗モードのうち、どれが最も起きやすいか特定したか？
  - Retrieval fails / Chunk size mismatch / Semantic gap / Multi-hop / Temporal / LLM ignores context
- [ ] Embedding モデルの選定基準（dimensionality, domain適合性, pooling strategy）は検討したか？
- [ ] Chunk size は適切か？（小さすぎ: 50-100 tokens → ノイズ、大きすぎ: 2000+ → 精度低下）
  - 推奨: 512 tokens + 64 overlap から開始、Context Precision@5 で評価
- [ ] Domain-specific vocabulary への対処は？（Query expansion / BM25 hybrid / Synonym injection）

## 2. Advanced Retrieval

- [ ] Hybrid Retrieval (BM25 + Vector) を検討したか？（Vector-only の failure modes: 希少語、完全一致、略語）
- [ ] Re-ranking pipeline は必要か？（Bi-encoder → Cross-encoder → LLM-based の段階選択）
- [ ] Multi-hop retrieval が必要なケースを特定したか？
- [ ] 曖昧なクエリへの対処法は？（Multi-query / HyDE / Step-back）

## 3. RAG Architecture (Production)

- [ ] End-to-End Pipeline の各コンポーネントを設計したか？
- [ ] Stateless vs Stateful RAG の判断は？
- [ ] Agentic RAG (Planner-Executor-Verifier) が必要なケースか？
- [ ] Tool Calling の設計は適切か？
- [ ] 数百万ユーザー規模の Production RAG を考慮したか？
- [ ] レイテンシ削減戦略は？
- [ ] キャッシュ戦略は？
- [ ] Retrieval/LLM 障害時のフォールバックは？
- [ ] Real-time vs Batch の使い分けは？

## 4. Evaluation & Metrics

- [ ] Retrieval Metrics (Precision@K, Recall@K, MRR, NDCG) を定義したか？
- [ ] Generation Metrics (RAGAS: Faithfulness, Answer Relevancy, Context Precision) を導入したか？
- [ ] Hallucination の測定方法は？
- [ ] Retrieval と Generation を分離して評価しているか？
- [ ] Offline evaluation pipeline は構築したか？
- [ ] Golden dataset を作成したか？

## 5. Hallucination & Reliability

- [ ] Grounded Generation を強制しているか？（検索結果のみに基づく回答）
- [ ] Citation Enforcement は？（回答にソース引用を要求）
- [ ] Confidence Scoring で低信頼度の回答を検出しているか？
- [ ] システムが回答を拒否すべきケースを定義したか？
- [ ] 取得ドキュメントが誤っている場合の対処は？

## 6. Performance & Scaling

- [ ] ANN アルゴリズム (HNSW vs IVF) の選択根拠は？
- [ ] 数十億ドキュメントへのスケーリング戦略は？
- [ ] TTFT (Time to First Token) の最適化は？
- [ ] Accuracy vs Latency のトレードオフを明示したか？
- [ ] Embedding コスト削減策は？（MRL, dimensionality reduction）
- [ ] Caching vs Recomputation の判断基準は？

## 7. Data Pipeline & Ingestion

- [ ] Document Parsing 戦略は？（PDF/DOCX/HTML の処理）
- [ ] Incremental Updates の仕組みは？
- [ ] Data Freshness の要件は？
- [ ] Real-time data updates への対応は？
- [ ] ダウンタイムなしの Re-indexing は？
- [ ] 重複ドキュメントの処理は？
- [ ] Embedding のバージョニングは？

## 8. Security & Enterprise RAG

- [ ] Access Control モデルは定義したか？
- [ ] Multi-tenant Isolation は？
- [ ] PII Filtering は実装したか？
- [ ] ユーザー間のデータリークを防ぐ方法は？
- [ ] Row-level security の実装は？
- [ ] 機密ドキュメントの取り扱いは？
- [ ] RAG 出力の監査体制は？

## 9. Agentic RAG

- [ ] Agentic RAG vs Simple RAG の判断基準は？
- [ ] Agent の infinite loop 回避策は？（max iterations, timeout, cost limits）
- [ ] Agent performance の評価方法は？
- [ ] 複数ツールのオーケストレーション設計は？
- [ ] Planner-Executor-Verifier パターンの採用は？

## 10. Prompt Engineering for RAG

- [ ] Context Injection のパターンは適切か？
- [ ] Structured Outputs を使用しているか？
- [ ] Context overflow の防止策は？
- [ ] Grounding 用プロンプトの構造は？
- [ ] 矛盾するドキュメントへの対処は？
- [ ] 出力の決定論性をどう確保するか？

## 11. Observability & Monitoring

- [ ] 何をログに記録するか定義したか？（query, retrieved chunks, scores, response, latency）
- [ ] Tracing ツールは導入したか？
- [ ] Drift Detection の仕組みは？
- [ ] Bad answer のデバッグ手順は？
- [ ] 本番環境での Hallucination 監視は？
- [ ] User Feedback Loop の設計は？

## 12. Deployment & LLMOps

- [ ] RAG 向け CI/CD パイプラインは？
- [ ] Model Versioning の仕組みは？
- [ ] A/B Testing / Canary Deployment は？
- [ ] スケールデプロイの戦略は？
- [ ] Bad model のロールバック手順は？
- [ ] リリース前テスト戦略は？
- [ ] Multi-region deployment は必要か？

## 13. LLM Inference Optimization

- [ ] KV Cache を活用しているか？
- [ ] Paged Attention (vLLM) は？
- [ ] Continuous Batching は？
- [ ] Prompt token recomputation の最適化は？
- [ ] GPU メモリ使用量の最適化は？
- [ ] Kubernetes 上のスケーラブル推論サービスは？

---

## Quick Patterns（Ch1-2 から抽出）

### RAG 失敗時の診断フロー
```
Retrieval metrics (Recall@K) が低い？
  → YES: Chunking, Embedding, Query Rewriting を修正
  → NO: Faithfulness が低い？
    → YES: プロンプトを修正（Grounding 強化）
    → NO: 回答品質は OK
```

### Hybrid Retrieval Architecture
```
Index: Recursive split (512 tok) → Dense embed (BGE-large) + BM25 index
Query: LLM rewrite → Dense top-20 + BM25 top-20 → RRF (0.3/0.7) → Cross-encoder re-rank → top-5
Guard: Drop cosine < 0.65, deduplicate, trim to context window
```

### Embedding 選定
1. `text-embedding-3-large` or `BGE-large` をベースライン
2. MTEB で domain eval
3. Recall 不足 → domain triplets で fine-tune
4. 次元柔軟性 → MRL (Matryoshka) embeddings

### Cosine vs Dot Product
- 非正規化ベクトル → cosine（長さバイアス除去）
- L2正規化済み → dot product（高速、cosine と等価）
- 実用: Index 時に L2-norm → dot product = cosine at zero cost
