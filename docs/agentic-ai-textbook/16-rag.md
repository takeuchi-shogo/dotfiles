# 第16章 RAG（Retrieval-Augmented Generation）

> **一文サマリ:** RAG は、クエリ時に外部文書を検索してLLMの文脈に注入し、学習済みパラメータに無い知識で回答を接地（grounding）させる手法。リサーチエージェントの「知識層」そのもの。
> **PDF参照:** §16, p.295-319

この章から6フィールド型。ただし RAG は派生手法が異常に多いので、**幹となる概念は6フィールドで厚く、派生の山(Self-RAG, CRAG, RAG-Fusion 等)は比較表で軽く**捌く。リサーチエージェントにとっての本命は §16.7 Agentic RAG。

---

## 16.1 なぜRAGが要るか

LLMは知識を**パラメトリック**（重みに圧縮）に持つ。これが3つの限界を生む: ①Hallucination（知識境界の外で自信満々に間違える）②Knowledge Staleness（学習カットオフ以降を知らない）③Domain Specificity（専有データを知らない)。RAG はこれを**非パラメトリック**な外部知識で補う。

形式的には、検索分布 $P_{ret}(d|q)$ で検索した文書 $d$ について周辺化する: $P_{RAG}(a|q,\mathcal{D}) = \sum_{d} P_{\mathcal{M}}(a|q,d)\,P_{ret}(d|q)$。要は「記憶から推測する学者」に「図書館の利用カード」を渡す話。

**よくある誤解:** RAG は fine-tuning の代替ではない。**FT は "どう推論・応答するか" を教え、RAG は "何について" を与える**。両者は補完的。

**RAG / FT / Long Context の使い分け(Table 16.1):**

| 条件 | RAG | Fine-Tuning | Long Context |
|---|:---:|:---:|:---:|
| 知識が頻繁に更新される | ✓ | ✗ | ✗ |
| 引用・接地が要る | ✓ | ✗ | ✓ |
| 専有の大規模コーパス | ✓ | ✗ | ✗ |
| スタイル/書式を適応 | ✗ | ✓ | ✗ |
| 新しい推論スキルを教える | ✗ | ✓ | ✗ |
| コーパスが文脈窓に収まる | ✗ | ✗ | ✓ |
| 低レイテンシ必須 | ✗ | ✓ | ✗ |

→ リサーチエージェントは「日々増える記事・論文を引用付きで参照」なので RAG が中核。スタイル適応が要る箇所だけ後で FT を足す（§16.10）。

---

## 16.2 基本パイプライン

### RAGパイプライン（offline索引 + online検索生成）
**これは何か** — RAG は2フェーズ。**オフライン索引**: 文書をロード→チャンク分割→embedding→Vector DBへ。**オンライン検索生成**: クエリをembedding→類似検索（top-k）→（任意でre-rank）→プロンプトに注入→生成。
**いつ使う / なぜ要る** — 外部知識に接地した回答が要る全ての場面。これが土台で、§16.3以降は各ステップの差し替え部品。
**最小実装**
```python
# オンライン側のプロンプト組み立て（Listing 16.1 を簡約）
SYSTEM = """提供された文脈だけで回答せよ。情報が無ければ「無い」と明言し、
出典を [Doc N] 形式で引用せよ。"""

def build_rag_prompt(query: str, chunks: list[dict]) -> str:
    ctx = "\n".join(
        f"[Doc {i+1}] (出典: {c['source']}, p.{c.get('page','N/A')})\n{c['text']}"
        for i, c in enumerate(chunks)
    )
    return f"{SYSTEM}\n\nContext:\n{ctx}\n\nQuestion: {query}\nAnswer:"
```
検索は cos類似度 $\mathrm{sim}(\mathbf{q},\mathbf{e}_i)=\frac{\mathbf{q}\cdot\mathbf{e}_i}{\|\mathbf{q}\|\|\mathbf{e}_i\|}$ で top-k を返すだけ。
**リサーチエージェントでの使いどころ** — 収集済み記事コーパスへの問い合わせの基本形。`source`・`page`・`timestamp` をメタデータに必ず残す（後の引用とフィルタに効く）。
**落とし穴** — ①「文脈だけで答えよ・無ければ無いと言え」をプロンプトに明示しないと、検索結果を無視してパラメトリック記憶で捏造する（§16.8.4 Hallucination Despite Retrieval）②メタデータを索引時に捨てると引用も日付フィルタも後付け不能。
**PDF参照** — §16.2, p.296-297

---

## 16.3 検索方式 — Hybrid を既定にする

検索方式は sparse（語彙一致）/ dense（意味）/ hybrid（両取り）の3系統。**実務の既定は Hybrid（BM25 + dense を RRF で融合）**。これだけ6フィールドで、残りは表で捌く。

### Hybrid Retrieval + Reciprocal Rank Fusion (RRF)
**これは何か** — sparse（BM25: 正確な語彙一致）と dense（embedding: 意味的近さ）の検索結果を**順位**で融合する。スコアは系統間で比較不能なので、スコアでなく rank を使う: $\mathrm{RRF}(d)=\sum_{r}\frac{1}{k+\mathrm{rank}_r(d)}$（$k=60$ が定番）。
**いつ使う / なぜ要る** — ほぼ常時。固有名詞・専門用語（dense が取りこぼす）と言い換え（sparse が取りこぼす）の両方をカバーできる。プロダクションRAGの強い既定値。
**最小実装**
```python
def rrf(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    for ranked in ranked_lists:          # 例: [bm25順, dense順]
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)
```
**リサーチエージェントでの使いどころ** — 論文・記事検索では用語（"GRPO" 等の固有語）とテーマ（"RLの効率化"）が混在する。Hybrid なら両方拾える。
**落とし穴** — ①$k$ を小さくすると上位文書の影響が過剰になる（$k=60$ から動かさない）②sparse索引（転置index）と dense索引（ANN）の二重持ちで運用コストが上がる — まず dense 単独で動かし、取りこぼしが出たら Hybrid 化する順が安全。
**PDF参照** — §16.3.3, p.298

**検索方式の比較(Table 16.2):**

| 方式 | レイテンシ | 精度 | 索引サイズ | GPU | 向き |
|---|---|---|---|:---:|---|
| TF-IDF / BM25 | 極低 | 低〜中 | 小 | 不要 | キーワード・固有名詞・希少語 |
| DPR（bi-encoder） | 低 | 高 | 大 | 要 | 意味的類似 |
| SPLADE（learned sparse） | 低 | 高 | 中 | 要(索引時) | 意味検索をGPUなしで・転置index活用 |
| ColBERT（late interaction） | 中 | 極高 | 極大 | 要 | 高精度検索 |
| Cross-encoder | 高 | 最高 | — | 要 | top-k の re-rank 専用 |
| **Hybrid (RRF)** | 低 | 極高 | 大 | 要 | **プロダクション既定** |

> 補足: **SPLADE/v2** は MLM ヘッドで語彙拡張した sparse ベクトルを作り、転置indexでGPUなし検索＋解釈可能性を得る。**ColBERT** はトークン単位embeddingの MaxSim で bi-encoder より表現力が高い。どちらも「first-stage は SPLADE/dense → top-k を cross-encoder で re-rank」が定石。詳細はPDF §16.3.4-5。

---

## 16.4 チャンキング — 最重要の設計判断

### チャンク分割戦略
**これは何か** — 長文書を「embedding窓に収まり(典型512token)・意味的にまとまり・単独で意味が通る」断片に割る。**RAG設計で最も効くノブ**。固定長(+overlap) / semantic(隣接文の類似度で境界検出) / 構造認識(Markdown見出し・コード関数で割る) / parent-child(小chunkで検索→大chunkで生成) の4系統。
**いつ使う / なぜ要る** — 索引前に必ず通る。chunk が悪いと後段の検索・生成が全部劣化する。「良いchunkの素朴RAG」が「悪いchunkの高度RAG」に勝つ。
**最小実装**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512, chunk_overlap=64,      # 10-15%のoverlapで境界の情報欠落を防ぐ
    separators=["\n\n", "\n", ". ", " ", ""],  # 大きい境界から優先的に割る
)
chunks = splitter.split_documents(documents)
```
**リサーチエージェントでの使いどころ** — 論文/記事は**構造認識チャンキング**が効く（Markdown `##`・セクション単位）。要約タスク主体なので chunk は大きめ(512-1024token)。引用元を辿るなら **parent-child**（128tokenで精密検索 → 512tokenで文脈豊かに生成）。
**落とし穴** — ①overlap ゼロだと境界をまたぐ情報が消える ②表を行の途中で割ると壊れる（表は丸ごと1chunk）③chunk size はタスク依存（下表）。一律設定で済ませない。
**PDF参照** — §16.4, p.301-303

**用途別チャンクサイズ(Table 16.3):** factoid QA=128-256 / 要約・統合=512-1024 / コード=関数丸ごと / 法務=段落単位 / 会話=256-512token。

---

## 16.5 高度なRAGパターン — Re-ranking 以外は表で

派生パターンは多いが、**費用対効果が最も高いのは Re-ranking**。これだけ6フィールド、残りは表。

### Re-Ranking（cross-encoder 再ランク）
**これは何か** — first-stage で top-k（20-100件）を粗く取り、**cross-encoder**（クエリと文書を同時に見るモデル）で精密に再スコアリングして上位を絞る。$s_{cross}(q,d)=\mathrm{CrossEncoder}([q;d])$。
**いつ使う / なぜ要る** — 検索精度を一段上げたいとき、最も低コストで効く（top-20候補にre-rankerを足すだけ）。cross-encoderは事前embeddingを持てないので first-stage には使えない（再ランク専用）。
**最小実装**
```python
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("BAAI/bge-reranker-large")

def rerank(query: str, docs: list[str], top_n: int = 5) -> list[str]:
    scores = reranker.predict([(query, d) for d in docs])
    return [d for _, d in sorted(zip(scores, docs), reverse=True)[:top_n]]
```
**リサーチエージェントでの使いどころ** — Hybridで20件拾い、re-rankerで本当に関連する5件に絞ってから要約に渡す。Lost-in-the-Middle（後述）対策にもなる。
**落とし穴** — ①レイテンシが上がる（候補をtop-20-100に制限）②low-latency要件(<100ms)とは両立しない — バッチ/非同期用途向け。
**PDF参照** — §16.5.2, p.304

**高度パターンの早見表:**

| パターン | 一言 | 効くクエリ |
|---|---|---|
| Query Transformation (HyDE/Step-Back/Multi-Query) | クエリを書き換え/分解してから検索 | 曖昧・短い・語彙ギャップ |
| Re-Ranking | top-k を cross-encoder で精密化 | プロダクションQA全般（高ROI） |
| Contextual Compression | 検索chunkからLLMで関連部分だけ抽出 | 無関係文が多いchunk |
| Self-RAG | 検索要否・関連性・出典整合を特殊tokenで自己判定 | 選択的検索 |
| CRAG (Corrective) | 検索結果をCorrect/Ambiguous/Incorrectで採点→不良ならWeb検索にfallback | 信頼できないコーパス |
| Adaptive RAG | クエリ複雑度で「検索なし/単段/多段」を振り分け | 複雑度が混在 |
| Graph RAG | コーパスから知識グラフ構築→コミュニティ要約 | 全体俯瞰("主要テーマは?") |
| RAG-Fusion | 複数クエリ生成→各検索→RRF融合 | 多様なクエリ型 |

> リサーチエージェントに効くのは **Multi-Query**（1つの調査命題を複数角度に分解）と **CRAG**（コーパスに無ければWeb検索へ自動fallback）と **Graph RAG**（「この分野の主要テーマは?」型の俯瞰）。

---

## 16.6 REFRAG（効率的デコード）

検索文書は長いのに関連は疎で、attentionが block-diagonal（cross-passageはほぼゼロ）になる。REFRAG は **Compress→Sense→Expand** の3段で、圧縮表現に軽量attentionして関連blockだけ復元する。LLaMAで TTFT 最大30.85倍、実効文脈長16倍。Agentic RAG は1クエリで複数回検索するのでレイテンシが累積する → こういう効率デコードが「反復ループを実用化する基盤」になる。今は「そういう最適化層がある」と認識すれば十分。**PDF参照:** §16.6, p.306。

---

## 16.7 Agentic RAG — リサーチエージェントの心臓

### Agentic RAG（検索を逐次意思決定にする）
**これは何か** — 素のRAGは「検索→生成」固定で、①multi-hop質問 ②曖昧クエリ ③異種ソース ④反復精緻化に弱い。Agentic RAG は検索を**逐次意思決定問題(MDP)**として扱う。state=現在の文脈（クエリ+既検索文書）、action={検索, 推論, 生成, 停止}、reward=回答の正しさ。エージェントが「いつ・何を検索するか」のpolicyを持つ。
**いつ使う / なぜ要る** — 答えが1回の検索で決まらない調査タスク全般。「探す→読んで足りないと分かる→クエリを変えて再検索→十分になったらまとめる」のループ。リサーチエージェントの定義そのもの。
**最小実装（LangGraphの条件付きループ, Listing 16.10 を簡約）**
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

class AgentState(TypedDict):
    query: str
    sub_queries: list[str]
    retrieved_docs: Annotated[list[dict], operator.add]  # 各検索を蓄積
    context_sufficient: bool
    answer: str
    iterations: int
    max_iterations: int

def plan_node(s):     return {**s, "sub_queries": decompose_query(s["query"]), "iterations": 0}
def retrieve_node(s):                                  # 各sub-queryを適切なソースへ
    docs = [d for sq in s["sub_queries"] for d in retrieve_from_source(sq, route_query(sq))]
    return {**s, "retrieved_docs": docs, "iterations": s["iterations"] + 1}
def evaluate_node(s): return {**s, "context_sufficient":
                              evaluate_context_sufficiency(s["query"], s["retrieved_docs"])}
def generate_node(s): return {**s, "answer":
                              generate_with_citations(s["query"], s["retrieved_docs"])}

def should_retrieve(s) -> str:                         # 条件分岐: 十分 or 予算切れ→生成、否→再検索
    if s["context_sufficient"] or s["iterations"] >= s["max_iterations"]:
        return "generate"
    return "retrieve"

g = StateGraph(AgentState)
for name, fn in [("plan",plan_node),("retrieve",retrieve_node),
                 ("evaluate",evaluate_node),("generate",generate_node)]:
    g.add_node(name, fn)
g.set_entry_point("plan")
g.add_edge("plan", "retrieve"); g.add_edge("retrieve", "evaluate")
g.add_conditional_edges("evaluate", should_retrieve,
                        {"retrieve": "retrieve", "generate": "generate"})
g.add_edge("generate", END)
agent = g.compile()
```
**リサーチエージェントでの使いどころ** — これが収集フェーズの幹。`plan`(命題を小問に分解)→`retrieve`(各小問を適切なソースへルーティング)→`evaluate`(集めた文脈で答えられるか自己判定)→足りなければループ。`max_iterations` が無限ループの安全弁。
**落とし穴** — ①`max_iterations` 必須（評価が永遠に「不十分」を返すと止まらない）②各反復で `retrieved_docs` が膨張 → 文脈溢れ（Ch18の文脈管理 / Ch17のMemoryへ逃がす）③`evaluate_context_sufficiency` がLLM判定なので甘い/辛いに振れる（基準をプロンプトで固定）。
**PDF参照** — §16.7, p.306-310

**Multi-Source Routing（どのソースに聞くか）:** 質問型ごとに最適なバックエンドは違う。素の「単一indexから引く」では外す。ルーティングは3段階で洗練される: ①Rule-based（キーワードトリガ、速いが脆い）②Classifier-based（軽量分類器、<10ms だが学習データ要）③LLM-based（structured outputで判断、柔軟だが1呼び出し増）。

```python
from enum import Enum
from pydantic import BaseModel

class KnowledgeSource(str, Enum):
    VECTOR_DB = "vector_db"; WEB_SEARCH = "web_search"; API = "api"

class RouteDecision(BaseModel):
    source: KnowledgeSource
    refined_query: str
    reasoning: str

def route_query(query: str, llm) -> RouteDecision:     # LLM-based routing
    prompt = f'クエリ "{query}" にどのソースを使うか。'\
             'vector_db=収集済みコーパス, web_search=最新情報, api=リアルタイムデータ。'\
             'source/refined_query/reasoning のJSONで返せ。'
    return llm.with_structured_output(RouteDecision).invoke(prompt)
```
> リサーチエージェントの実例: 「過去に集めた記事」→vector_db / 「昨日のリリース」→web_search / 「論文の引用数」→API。`reasoning` を必ずログに残す（デバッグと、後でClassifierを学習する教師データになる）。**ルータ自体を学習policy化**すると classification→planning の最上位形になり、これは §16.7.6 / Ch12 のRL話に繋がる。

**Search-R1（RL学習されたAgentic RAG）:** 上記はすべて**プロンプトで制御**するagentic RAG（frozen model）。Search-R1 は一歩進んで、`<search>query</search>` を**行動**としてRL（GRPO）で学習し、「いつ・何を・何回検索するか」を推論の一部として獲得する。7Bモデルが標準RAGを15-20%上回り、70B+標準RAG相当に届く。要点: **"より多く知る大モデル" より "上手く検索する小モデル" が勝つ**。実装はリサーチエージェントのv2課題。詳細は Ch12（Tier 1 末尾）で。**PDF参照:** §16.7.6, p.311。

---

## 16.8 評価 — 3層で測る

### RAG評価（RAGAs / Faithfulness）
**これは何か** — RAGの誤りはどの段でも出て累積するので、**検索品質 / 生成品質 / E2E品質**の3層で測る。中核指標は **Faithfulness**（回答の各主張が検索文脈で裏付くか = $\frac{\text{文脈で支持される主張数}}{\text{回答の全主張数}}$、LLM判定）と **Answer Relevance**（回答が質問に答えているか）。
**いつ使う / なぜ要る** — 「検索は当たってるのに生成が幻覚」「生成は良いのに検索が外れ」を切り分けるため。1層だけ最適化（例: Recall@K を大Kで上げる）すると無関係chunkで文脈が薄まり生成が劣化する。
**最小実装**
```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

ds = Dataset.from_dict({"question": questions, "answer": generated,
                        "contexts": retrieved_contexts, "ground_truth": references})
results = evaluate(ds, metrics=[faithfulness, answer_relevancy,
                                context_precision, context_recall])
```
検索層は Recall@K / Precision@K / MRR / NDCG@K、生成層は Faithfulness / Answer Relevance / Context Precision・Recall。
**リサーチエージェントでの使いどころ** — 収集結果の質を自動採点する評価ゲート。特に Faithfulness は「要約が原典に忠実か（捏造引用してないか）」の検査になり、Ch17のMemoryで「この情報源は当たり/外れ」を学習する報酬信号にも使える。
**落とし穴** — ①LLM-as-judgeなので judge自体のバイアス（Ch14参照）②reference-free指標でも質問セットの代表性が無いと無意味 ③RAGAsはバージョンでAPIが変わる（v0.2+は `user_input`/`response`/`retrieved_contexts`/`reference`）。
**PDF参照** — §16.8, p.312-313

**監視すべき6つの故障モード(§16.8.4):** ①Retrieval Miss（コーパスにあるのに取れない）②Context Poisoning（誤情報混入）③**Lost-in-the-Middle**（長文脈の中央が無視される → re-rankで上位集約）④Over-Retrieval（多すぎて希釈）⑤Hallucination Despite Retrieval（文脈を無視して捏造）⑥Citation Fabrication（裏付けない引用）。

---

## 16.9 プロダクションの勘所

**Embedding modelが品質の天井(Table 16.5):** 最も効く部品選び。2026時点の選択肢 — API系: Voyage `voyage-4-large`（最高精度）/ OpenAI `text-embedding-3-large`(MTEB 64.6)/ Cohere `embed-english-v3.0`。自前ホスト系: nvidia `NV-Embed-v2`(MTEB 72.3, #1)/ `gte-Qwen2-7B`(Apache-2.0, 多言語)/ `BGE-M3`(dense+sparse+multi-vec)。選定軸: ドメイン一致(専用モデルは5-15%上回る)/ 文脈長(32Kなら無チャンクで丸ごと)/ Matryoshka(次元を後から切れる)/ 量子化対応 / 多言語。

**Vector DB(Table 16.6):** FAISS(自前/research)、Pinecone(managed/手軽)、Weaviate(GraphQL/multi-modal)、Chroma(local開発)、Qdrant(高性能)、Milvus(enterprise)、pgvector(既存Postgres)。

**レイテンシ最適化:** ①メタデータpre-filtering（日付/カテゴリで検索空間を絞る）②HNSW/IVF近似（~1%のrecall犠牲で10倍速）③embeddingキャッシュ ④非同期並列検索（`asyncio.gather`で複数ソース同時、最遅ソースのコストだけ払う）⑤生成のストリーミング ⑥量子化。

**増分索引(Listing 16.14):** コーパスは静的でない。**Upsert**（doc_id単位で旧chunk全削除→再chunk→挿入、stale断片を残さない）/ **Delete・Expire**（TTLで時限GC、ニュース等に）/ **Version tracking**（`version`+`indexed_at`でrollbackと監査）。embeddingモデルを上げると旧vectorと非互換 → モデル版ごとに別index＋背景移行、または Matryoshka互換モデル。

> リサーチエージェントは「日々記事が増え、古い情報は腐る」ので **増分索引 + TTL** が必須。`indexed_at` と `source` のメタデータが、後で「いつの情報か」「どの情報源か」のフィルタを可能にする。

---

## 16.10 RAG + Fine-Tuning（RAFT）

FTとRAGは補完的: FT単独は書式を学ぶが事実を幻覚、RAG単独は事実を持つが使い方が下手。**Combined**は「検索文脈をうまく使う(引用する/不確実を認める/無関係を無視する)」ようFTする。**RAFT** は関連文書＋distractor（おとり）文書を混ぜて学習させ、関連だけを見分けて使う力を付ける。最大性能は retriever-generator の同時学習だが複雑（index非同期更新・疎な学習信号・不安定）。リサーチエージェントv1では不要、スタイル品質が頭打ちになったら検討。**PDF参照:** §16.10, p.317-318。

---

## この章のまとめ

- RAG = クエリ時に外部文書を検索して文脈に注入し、回答を接地する知識層。FTの代替でなく補完。
- **既定の組み合わせ:** 良いチャンキング(構造認識+overlap) → Hybrid検索(BM25+dense+RRF) → cross-encoder re-rank(top-20→5) → 「文脈だけで答えよ」プロンプト。「素朴だが良いchunk」が「高度だが悪いchunk」に勝つ。
- **リサーチエージェントの心臓は Agentic RAG**: plan→retrieve→evaluate→（不足なら）loop の条件付きグラフ。`max_iterations`が安全弁。Multi-Source Routingで質問型ごとにソースを振り分け、`reasoning`をログに残す。
- 評価は検索/生成/E2Eの3層。Faithfulnessは「捏造引用してないか」の検査で、Memory(Ch17)の報酬信号にもなる。
- プロダクション: embeddingモデルが天井、増分索引+TTLでコーパスの腐敗に対処。
- RL学習版（Search-R1）は「上手く検索する小モデルが勝つ」— v2課題として Ch12 へ。

**ベストプラクティス要約:** ①まず素朴RAGを良いchunkで動かす ②検索を生成と分けて評価し、検索を先に直す ③Hybrid(BM25+dense+RRF)を既定に ④top-20にcross-encoder re-rank（高ROI）⑤embeddingは一度・頻出クエリはキャッシュ ⑥chunkは10-15%overlap ⑦リッチなメタデータ(source/date/section)でpre-filtering。

**次章 → Ch17 Agentic Memory（永続層）。** 検索した知識を「セッションをまたいで覚える」層に進む。
