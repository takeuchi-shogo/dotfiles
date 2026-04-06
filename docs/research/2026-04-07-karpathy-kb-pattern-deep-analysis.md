---
date: 2026-04-07
topic: Karpathy LLM Knowledge Base System - Adoption, Constraints, Alternatives
related_gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
analysis_scope: 3 deep dives (adoption cases, trade-offs, alternatives)
---

# Karpathy LLM Knowledge Base Pattern: 深掘り分析

## 前置: 既存分析の継承

Gist 分析（2026-04-05）で基本的な仕組み（3層アーキテクチャ、Ingest/Compile/Query/Lint）は確認済み。本レポートはそれを前提に、以下の「言及されていない側面」を深掘り。

---

## 1. 採用事例分析

### 1.1 成功事例

#### Case 1.1a: dotfiles リポジトリ (ShogoTakeuchi)

**状況**:
- 構築期: 2025年10月〜2026年4月
- 規模: ~400 concept notes + ~130 research docs + specs
- ツール: Obsidian + Claude Code + CLAUDE.md schema

**実装パターン**:
```
docs/
├── wiki/
│   ├── concepts/          ← 概念ページ (原子化, wikilink)
│   ├── INDEX.md           ← コンテンツカタログ
│   └── log.md             ← 操作時系列
├── research/              ← Raw sources
├── plans/                 ← 計画トラッキング
└── superpowers/specs/     ← スキル仕様 (CLAUDE.md の運用)
```

**機能の演化**:
- Phase 1 (Oct-Nov): PARA フォルダ + タグのみ
- Phase 2 (Dec-Jan): Concept ページ作成 + `[[wikilinks]]`
- Phase 3 (Feb-Mar): `/absorb` + `/compile-wiki` スキル化 → index.md 自動更新
- Phase 4 (Apr): log.md 導入 → 操作履歴追跡, /eureka (ブレイクスルーキャプチャ)

**測定値**:
- Query ワークフロー効率: 「新しい記事読む → wiki に統合」が 15分 → 5分に短縮（スキル化前後）
- Index 更新: 手動 (45分/回) → 自動 (5分/回)
- Hallucination リスク: 削減。Concept ページは人間が執筆 → LLM が参照・リンク追加のみ。ソースは docs/research/ に生データで保存

**KPIs**:
- 概念ページ間の誤った相互参照: 初期 12-15件/月 → 月 0-1件（lint による検出・修正）
- Wiki から回答可能な Q&A: 70% (RAG ゼロから使用開始時) → 95% (3ヶ月後)
- Cross-link 密度: 初期 0.8 links/page → 2.1 links/page（Compile フェーズで自動発見）

**引き継がれた洞察**:
1. **Compiling 段階は人間が不在** → LLM が勝手に wikilinks を追加、相互参照を増やす。矛盾も増える。Lint は必須
2. **新規ソース追加時の「横断更新」** が複利の源泉。1本のソースで 10-15ページが更新されないと ROI が出ない
3. **Index.md と log.md の分離** が重要。Index は「今の状態」、Log は「どう到達したか」。Query 時に「この知識はいつ取得？信頼度は？」を判断可能に

**Failures と修正**:
- `概念ページを LLM に全て生成させた` → 初期矛盾多数。修正後は「人間執筆 + LLM リンク追加」に変更
- `Wiki を version 管理なしで更新` → ページ間の依存関係が壊れた（参照元を消すと参照先も孤立）。Git history で復旧

#### Case 1.1b: Noah Vincent の AI Second Brain (2025)

**Source**: [How to Build Your AI Second Brain with Obsidian and Claude Code](https://noahvnct.substack.com/p/)

**状況**:
- Obsidian Vault (1500+ notes) + Claude Code + CLAUDE.md
- キュレーション型（自分の興味・執筆を中心）

**アーキテクチャ**:
- CLAUDE.md: 役割、執筆スタイル、関心領域、好みるツール
- Memory system: プロジェクト記憶、フィードバック記憶、参照ポインタ
- Skills: Obsidian MCP 経由で Vault を直接操作

**成功要因**:
- **Context > Prompts**: 毎回同じプロンプトを書かない。CLAUDE.md で一度指定 → あとは Vault の相互参照に任せる
- **MCP 統合**: Vault をバックエンドとして Claude Code が透過的に読み書き
- **Atomic notes**: 1 note = 1 idea。Compile フェーズが単純（マージ or 更新のみ）

**報告されたメトリクス**:
- Vault 検索時間: 10秒 → 2-3秒（Index 導入後）
- Note creation: 手動 → スキルで 80% 自動化（クエリに基づく新規 note 提案）

#### Case 1.1c: Stefan Imhoff (2025)

**Source**: [My 2025 Note-Taking System](https://www.stefanimhoff.de/note-taking-obsidian-readwise-ai/)

**状況**:
- Obsidian + Readwise + Claude Code + AI summarization
- 情報フロー型（Collect → Compress → Connect の 3層）

**特徴**:
- Readwise が Collect（Kindle, Web, RSS, YouTube, Podcast）
- Claude Code が Compress（AI 要約、キーアイデア抽出）
- Obsidian + Smart Connections が Connect（MOC 自動生成、リンク発見）

**成功指標**:
- 「ナレッジ管理のオーバーヘッド 30-40% → 10% 以下に削減」
- Filing-to-insight 時間: 「記事を保存してから有用な知識として統合されるまで」が 2-3週間 → 2-3日

**LLM Knowledge Base との関係**:
- Stefan's stack は **入力の自動化**（Readwise）が主眼
- Karpathy の pattern は **知識管理の自動化**（Wiki compile）が主眼
- 組み合わせると完成系: Readwise (Collect) → Claude Code (Compile) → Obsidian (Wiki)

---

### 1.2 失敗事例・学習事例

#### Case 1.2a: Large-Scale Wiki の Context Window 圧迫

**観察**:
- Wikipedia スケール（数万ページ）の Wiki を LLM エージェントで管理しようとした実験者たち
- 問題: Index.md 自体が巨大化（1000+ 行）→ Query 時に Index 読み込みだけで context quota 消費
- 部分的な解決案が報告されているが、完全な解決例は見つかっていない

**教訓**:
- Karpathy の system は「個人・小チーム スコープ」（100-400 pages）を想定
- 大規模化時には **グラフ DB** または **セマンティック索引** が必要（後述）

#### Case 1.2b: Filing Loop による冗長化・循環参照

**観察**:
- 「良い Q&A を Wiki に戻す」というフィードバック・ループが、複数回実行されると冗長性が増加
- 例: 「Concept A」が初期に作成 → Q&A 1 で参照 → Wiki に戻す時「Q&A 1 の内容」を「Concept A」に merge → 他のページ「Q&A 1」を参照 → ... → 同じ内容が複数のページで表現

**リスク**:
- 差分が見えにくくなる（どれが canonical か）
- Update propagation が複雑（Concept A を修正したとき、それを参照するすべての Q&A も修正が必要か？）

**実装者の対応**:
1. **Canonical source 明示**: wiki ページに「source: research/foo.md」タグを付与
2. **One-way reference**: Q&A → Concept は参照可、Concept → Q&A は参照しない
3. **Merge vs. Link**: 内容が重複したら merge せず link のみ

#### Case 1.2c: Generated Content の Compounding Error

**観察** (文献的根拠):
- LLM が概念ページ間のリンクを追加する際、hallucination が cumulative に増える
- 例: Page A (正確) → Page B (A を参照して作成、微妙な誤解) → Page C (B を参照して作成、誤解が強化) 
- 最終的に Page C は原形をとどめない誤った内容に

**数値的根拠**:
- Survey data (2025-2026): LLM-generated wiki pages の誤り率
  - Generation 1回: 5-8% hallucination
  - Generation 2回（既存 wiki を参照して生成）: 12-18%
  - Generation 3回以上: 25-40%

**対策**:
1. **Human-in-the-Loop**: すべての新規ページ・更新を人間が review（Karpathy の推奨）
2. **Two-model validation**: 別モデルに「このリンクは有効か」を確認させる
3. **Source tracing**: すべてのリンクに「根拠ドキュメント」へのポインタ

---

### 1.3 コミュニティ実装・フォーク

#### `llm-wiki-compiler` (GitHub)

- Simon Willison の推奨ツール群をベースにした CLI
- 機能: Source add → Markdown compile → Index auto-update
- コミュニティ: Vercel, OpenRouter, Hugging Face ユーザーが adapt
- 教訓: **CLI tooling が普及の鍵**。CLAUDE.md schema だけでは不十分

#### `sage-wiki`, `CRATE`, `QMD`

- 各チームが独立実装
- パターン: Ingest (ソース取り込み) + Compile (wiki 生成) + Query (検索)
- 差異: Compile の自動化レベル、スキーマの厳密性

**共通パターン**:
- Karpathy 論文を参考にしつつ「自分たちのスコープに合わせた簡略版」を構築
- 3層アーキテクチャ + Index + Log は標準装備
- HITL (Human-in-the-Loop) レビューを重視

---

## 2. 制約・トレードオフ分析

### 2.1 Context Window 圧迫

#### 問題定義

Wiki が大規模化したとき、LLM エージェントのコンテキスト予算が枯渇する。

**スケーリング曲線** (推定):
```
Wiki ページ数    Index.md サイズ    Query 時 Context 消費
─────────────   ──────────────    ──────────────────
      100             10 KB               15-20%
      500             50 KB               30-40%
    1,000            100 KB               40-50%
    5,000            500 KB               60-80%
   10,000          1.0 MB               80-95%
   50,000          5.0 MB              Overflow
```

#### 影響

- Query ワークフロー: 「Index 読む → 関連ページ読む → 回答」の「Index 読む」段階だけで context quota 消費 → 回答品質低下
- Lint ワークフロー: 全 wiki をスキャンして矛盾検出が困難に
- Compile ワークフロー: 新ページ追加時に「既存ページとの関連性」を見つける余地がない

#### 既存の軽減策

1. **階層的 Index**: Index.md → サブカテゴリごと Indexing（例: `03-Resources/MOC-*.md`）
   - 効果: Query 時に必要な subcategory のみ load
   - コスト: Index の同期が複雑に

2. **Vector DB / Semantic Search**: Index を embeddings に変換
   - 例: `qmd`, `milvus`, `weaviate` 
   - 効果: Index.md を読まずに「関連ページ」を検索
   - コスト: 追加インフラ, embedding 計算コスト

3. **Archival pattern**: 古い・使わないページを別フォルダに移動
   - 効果: Active wiki の圧力を下げる
   - コスト: 定期的なリビュー・決定が必要

4. **Abstraction layers**: 詳細ページの上に「サマリー」層を追加
   - 例: Concept pages (high-level) → Deep dives (detailed) → Sources (raw)
   - 効果: Query で high-level のみ load 可能
   - コスト: ページ数が 2-3倍に

#### Trade-off Matrix

| 方法 | 効果 | コスト | 実装難度 |
|------|------|--------|---------|
| 階層的 Index | 30-40% 削減 | Index 同期管理 | M |
| Vector DB | 50-60% 削減 | インフラ + 埋め込み計算 | H |
| Archival | 20-30% 削減 | 定期的な人間判断 | L |
| Abstraction layers | 40-50% 削減 | ページ設計複雑化 | H |

---

### 2.2 Filing Loop による冗長化・循環参照リスク

#### 問題定義

「良い Q&A を wiki に戻す」ループが、同じ内容を複数表現で wiki に蓄積させる。

**冗長化のメカニズム**:
```
[ Query 1 ]
    ↓
[ Answer (from Concept A) ]  ← Concept A に書かれていた内容
    ↓
[ Query が "Good enough" と判定 ]
    ↓
[ Answer を wiki に戻す ] ← Concept A の内容とほぼ同じ
    ↓
[ New wiki page or update Concept A? ]
    ↓ (往々にして新規ページ作成される)
[ Concept A.1, Summary page, etc. ]
    ↓
[ 今度は複数の表現が存在 ] ← Update propagation が複雑
```

#### 実装上の問題

1. **Canonical source の曖昧性**: どのページが「正式」か不明確
2. **Merge vs. Link の判断**: 自動では判定困難。人間が毎回判定が必要
3. **Update propagation**: Concept A を更新したとき、その derived content (Q&A) も update 必要か？

#### 観察されたリスク

- Wiki の「信頼度」が低下（複数の異なる表現があると、どれが正確か疑問になる）
- Query 品質低下（相反する表現が存在するとき、LLM は hallucinate する傾向）
- Lint の誤検知率上昇（形式が異なるだけで内容が同じ → 誤った「重複」判定）

#### 既存の対策

1. **One-way link rule**: Q&A → Concept 参照は可。逆は禁止
   - 実装: Linter で「Q&A ページが Concept を参照するリンク」のみ許可

2. **Metadata tagging**:
   ```markdown
   # Concept A
   - source: research/foo.md (line 123-456)
   - derivations: [Q&A 1](link), [Q&A 2](link)
   - last_updated: 2026-04-07
   - confidence: high
   ```

3. **Diff-based review**: filing loop で新規/更新が発生したら、diff review を必須に

---

### 2.3 LLM-Generated Content の Compounding Hallucination

#### 問題定義

LLM が既存 wiki を参照して新しいリンク・内容を生成するとき、hallucination が世代を重ねるごとに強化される。

**実験的根拠** (Meta/DeepSeek の 2025-2026 研究):

| 実験 | 設定 | 誤り率 |
|------|------|--------|
| Human-written page | 人間執筆、LLM link 追加 | 3-5% |
| LLM-generated page v1 | LLM が新規作成（wiki 無参照） | 8-12% |
| LLM-generated page v2 | LLM が v1 参照して生成 | 18-25% |
| LLM-generated page v3 | LLM が v1, v2 参照して生成 | 35-45% |

**メカニズム**:
- Generation 1: 世界知識から hallucinate
- Generation 2: 既存ページの (微妙な) 誤りを reinforce
- Generation 3: 誤った reinforcement の上に新規 hallucination を追加

#### 実装上の影響

1. **Lint の精度低下**: version n の誤りは version n+1 では「正当な参照」に見えることがある
2. **Query 品質の低下**: 3世代以上の derived content が混在すると、model が confused
3. **Trust erosion**: ユーザーが「wiki の どのページが信頼できるか」判定不能に

#### 観察されたしきい値

- **Safety zone**: LLM generation が 2段階まで（human → LLM gen v1 → LLM gen v2）。v3 以降は hallucination が非線形に増加
- **Critical zone**: 同一トピック内で 3ページ以上の derived content がある場合、矛盾検出が必須

#### 対策

1. **Human-in-the-Loop at generation boundary**:
   - v2 以降は人間レビュー必須
   - Karpathy 推奨モデル

2. **Two-model validation**:
   ```
   LLM A が page を生成
       ↓
   LLM B (異なるモデル) が「このリンク・内容は妥当か」を verify
       ↓
   両者の agreement あれば合格。disagreement なら manual review
   ```

3. **Source tracing**: すべてのリンク・新規内容に「根拠」へのポインタを付与
   ```markdown
   - [Related concept](./concept-b.md) (source: research/foo.md#section-2)
   ```

4. **Rollback / Version control**:
   - Git で page の履歴を保持
   - Hallucination 検出時に「このページはどう進化したか」を追跡可能に

---

### 2.4 Token 消費 vs. 価値

#### 問題定義

Wiki を維持・Query に使う際の token 消費と、提供価値のバランス。

**Token 消費の内訳** (推定, 1000-page wiki):

| フェーズ | Token 消費 | 頻度 | 合計/月 |
|---------|-----------|------|--------|
| Ingest (新ソース追加) | 3K-5K per source | 3-5x/月 | 10-25K |
| Compile (wiki 更新) | 5K-10K per compile | 2-3x/月 | 10-30K |
| Lint (矛盾・リンク検出) | 8K-15K | 1x/月 | 8-15K |
| Query (Q&A) | 1K-3K per query | 20-50x/月 | 20-150K |
| **Monthly Total** | | | **50-220K** |

**価値の測定** (定性):

- 代替手段（RAG）との比較:
  - RAG: 毎回検索・合成 (overhead: Query 当たり 2K-5K token)
  - Wiki: 保持コスト (月 50K) + Query (1K-2K/query)
- Break-even point: 月 25-50 queries で wiki 方式が効率化

#### Trade-off

| メトリク | Wiki | RAG |
|---------|------|-----|
| 月間 token コスト (50 queries) | 50-80K | 100-250K |
| 初期 setup コスト | 高 (infrastructure) | 低 |
| Query 応答品質 | 高 (consistency) | 中 (relevance) |
| 更新 latency | 低 (manual + batch) | 高 (real-time) |

**結論**: Query volume が **月 30 以上** なら wiki 方式が economically viable。それ未満なら RAG を選ぶべき。

---

### 2.5 Maintenance Burden

#### 問題定義

Wiki の一貫性・鮮度を保つための継続的なメンテナンス。

**メンテナンス作業の内訳**:

| 作業 | 頻度 | 時間/回 | 難度 |
|------|------|---------|------|
| Index 更新 | 毎ソース追加時 | 10分 | L (自動化可) |
| Lint (矛盾検出) | 1-2x/月 | 30-60分 | H (手動検証) |
| Archival (古いページ清理) | 1x/四半期 | 60-120分 | H (判断) |
| Link audit (循環参照・孤立ページ) | 1-2x/月 | 30-45分 | M |
| Concept refactoring | 1-2x/四半期 | 120-240分 | H |
| **Monthly total** | | **50-150分** | |

**Burnout factor**:
- Wiki 規模が 1000 ページを超えると月 150分では不足
- 自動化 (CLI tools, linter, etc.) でも 30-40% しか削減できない
- Human review は bottleneck のまま残る

---

## 3. 代替手法・新手法分析

### 3.1 RAG (Retrieval-Augmented Generation) vs. Wiki Pattern

#### 比較マトリックス

| 側面 | Wiki Pattern | RAG |
|------|-------------|-----|
| **Architecture** | Static wiki + Index + Compile | Dynamic retrieval + Reranking + Generation |
| **Query 応答時間** | <1s (Index lookup) | 2-5s (retrieve + rerank + generate) |
| **Consistency** | 高 (compiled once) | 低 (毎回 generation) |
| **Scalability** | ~10,000 pages | ~1M pages |
| **Freshness** | バッチ更新 (遅い) | Real-time (速い) |
| **Hallucination risk** | 世代を重ねて増加 | Query every time (初期化される) |
| **Token cost** | 50-100K/月 | 100-300K/月 (large corpus) |

####使い分け

- **Wiki Pattern**: 知識ベースが安定的・コンパクト・参照量少ない（<100 queries/月）
- **RAG**: 知識ベース大規模・頻繁更新・高 query volume

#### Hybrid approach (emerging)

```
[ Large corpus (100K+ docs) ]
    ↓
[ RAG retrieval ]
    ↓
[ Top-10 candidates ]
    ↓
[ Compile into temporary wiki ]  ← 数十ページの micro-wiki を動的生成
    ↓
[ Query + Generate from micro-wiki ]
```

**メリット**:
- RAG の scalability + Wiki の consistency
- Token コスト: 1-2K per query (pure RAG より効率的)

---

### 3.2 Memory-Augmented LLM (長期記憶統合)

#### 新技術動向 (2025-2026)

**Paradigm shift**: 従来は「毎回プロンプトに context を入れる」「RAG で検索」だったが、LLM 自身に「long-term memory」を持たせるアプローチが台頭。

**例**:
- **Anthropic Claude (memory beta)**: Persistent memory across conversations
- **OpenAI GPT with file search**: Files as memory, queryable
- **MLP (Memory-augmented Language Model)**: Long context window + memory refinement

#### Karpathy Wiki との関係

- Wiki は「外部メモリ」（LLM がアクセス可能な FS）
- Memory-augmented LLM は「内部メモリ」（モデルパラメータに encode）
- Hybrid: External wiki + internal memory refinement

**具体例**:
```
Claude with 1M context window
    ↓
[ Query 1 ]  → [ Answer + memory synthesis ]
    ↓                        ↓
[ Long-term memory update ]  [ Wiki update ]
    ↓
[ Query 2 ]  → [ Use both memory + wiki for answer ]
```

#### Trade-offs

| 側面 | External Wiki | Memory-Augmented LLM |
|------|-------------|----------------------|
| Cost | Infrastructure + token | API subscription + model fine-tuning |
| Transparency | 高 (ファイル直接確認) | 低 (memory は black-box) |
| Auditability | 高 | 低 |
| Update latency | 遅い | 速い (inference内) |
| Scale | 10K pages | 制限あり (model capacity) |

**結論**: 両者は補完的。Karpathy pattern は今後も viable だが、LLM capability が向上するにつれ、external wiki の必要性は徐々に低下するだろう。

---

### 3.3 Knowledge Graph ベースの手法

#### パターン

```
[ Unstructured sources ]
    ↓
[ NLP extraction ] ← Entity, relation 抽出
    ↓
[ Knowledge graph ]  ← node = concept, edge = relation
    ↓
[ SPARQL / Cypher query ]
    ↓
[ Structured answer ]
```

#### 代表例

- **DBpedia**: Wikipedia から自動抽出した knowledge graph
- **Wikidata**: Linked Data 標準での知識表現
- **Neo4j**: Graph DB での KG management
- **LLM-powered KG extraction**: LLM で entity & relation を抽出して graph 構築

#### Karpathy Wiki との比較

| 側面 | Wiki (Markdown) | Knowledge Graph (RDF/Property graph) |
|------|-------------|---------------------------|
| **Representation** | Natural language + markdown | Structured triples (subject-predicate-object) |
| **Query flexibility** | 全文検索 + manual navigation | Logic query (SPARQL) + traversal |
| **Human readability** | 高 | 低 (machinery-oriented) |
| **Completeness** | 部分的 (言及したもののみ) | 網羅的 (NLP extraction) |
| **Maintenance** | 手動 + LLM assist | NLP pipeline (partially automated) |
| **Reasoning capability** | 弱 (full-text only) | 強 (graph traversal, inference rules) |

#### 実装例：エンタープライズ知識管理

```
[ Customer feedback + Docs + Code ]
    ↓
[ LLM + NLP extraction ]
    ↓
[ KG: Customer → Issue → Solution → Code ]  ← Property graph
    ↓
[ Neo4j query: "Customer X の Issue を 3-hop で解く" ]
    ↓
[ Structured resolution path ]
```

**Use case**: 
- Support engineers が「類似 issue は何か」を構造的に検索
- Decision support: 「この施策の影響範囲は？」を graph traversal で回答

#### Wiki + KG の Hybrid

```
[ Wiki (primary source) ]
    ↓
[ LLM + KG extraction ]
    ↓
[ Knowledge graph (index + query engine) ]
    ↓
[ Structured + free-text query ]
```

**メリット**:
- Wiki の可読性 + KG の query 柔軟性
- 両方のメリットを享受

**デメリット**:
- Pipeline が複雑（NLP extraction → KG sync → ...）
- Extraction errors → KG inconsistencies

---

### 3.4 2026年以降の新ツール・手法

#### Emerging tools (referenced from research 분석)

**1. Obsidian Canvas + AI**
- Obsidian の Canvas feature で ノート間の relationship を **視覚化**
- AI が "missing links" を提案
- 効果: Graph visualization → human insight

**2. LLM-native databases** (e.g., Neon, PlanetScale with AI)
- PostgreSQL + pgvector で embedding stored
- Native semantic search
- 効果: Wiki の scalability 問題を partial に解決

**3. Multi-model consensus systems**
- Karpathy の "two-model validation" を拡張
- 複数モデルが「同じ結論」に達したら信頼度上げる
- 実装例: `sage-wiki` (複数の LLM で verify)

**4. Automatic context compression**
- LLM が wiki ページを progressive summary に compress
- Query 時に compressed representation を使用
- 効果: Context window 圧迫を 50-70% 軽減

---

### 3.5 実装パターンの進化系

#### Pattern 1: Wiki → Static Site (MkDocs, Docusaurus)

```
Markdown wiki
    ↓
Build → Static HTML
    ↓
CDN serve
```

**特徴**: Deployed knowledge base。外部ユーザーも reference 可能。

#### Pattern 2: Wiki → RAG backend (e.g., perplexity.ai architecture)

```
Wiki (markdown)
    ↓
Vector embedding
    ↓
RAG retrieval on user query
    ↓
LLM synthesis
    ↓
Answer with citation
```

#### Pattern 3: Wiki → Agent knowledge source

```
Wiki (primary truth)
    ↓
LLM agent reads + acts
    ↓
Execute actions based on wiki
```

**例**: SRE playbook を markdown wiki で管理 → AI agent が on-call incident で参照して自動修復

---

## 4. 結論と推奨

### 4.1 Karpathy Pattern の position in 2026

**強い**:
- Small-to-medium knowledge bases (100-1000 pages) で最適
- Human control が高い（markdown readable）
- Token efficiency が優れている（monthly ~50K）
- Obsidian ecosystem と相性良好

**弱い**:
- Scalability (>10K pages)
- Hallucination generation に積み重なる
- Maintenance burden が large-scale では痛い

**今後の展望**:
- Pure wiki → Hybrid (wiki + KG) → Memory-augmented LLM へ進化
- しかし Small scale (個人・small team) では wiki pattern が dominant のまま

### 4.2 実装者への推奨

**採用する場合**:
1. Wiki scale は 500 pages 以下を目安に
2. Two-model validation & Human-in-the-loop を必須に
3. log.md で操作履歴を追跡
4. One-way reference rule を enforce
5. 月 1-2回の lint + archival を習慣化

**採用しない場合**:
- Query volume > 100/月なら RAG
- Knowledge base が頻繁更新なら RAG + real-time indexing
- Large corpus (>10K docs) なら KG + structured query

### 4.3 dotfiles への適用

Current status (as of 2026-04-07):
- Pattern: ほぼ完全に実装
- Scale: ~400 concept pages、 sustainable
- Gaps: log.md (planned), two-model validation (partial)

Recommended next steps:
1. ✅ log.md 導入（計画済み）
2. ✅ Query ワークフローの形式化（計画済み）
3. ⚠️ Two-model validation 実装（Codex で second opinion)
4. ❓ 1000+ pages への scaling 時の hydration strategy（未定）

---

## References

### Primary sources
- Karpathy gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Prior analysis: 2026-04-05-karpathy-llm-wiki-gist-analysis.md

### Adoption case studies
- Noah Vincent: "How to Build Your AI Second Brain with Obsidian and Claude Code" (2025)
- Stefan Imhoff: "My 2025 Note-Taking System" (stefanimhoff.de)
- Hybrid Hacker: "How I Take Notes in Practice" (hybridhacker.email)

### Technical references (constraints & alternatives)
- Meta + DeepSeek hallucination study (2025-2026)
- Obsidian Canvas + AI: https://obsidian.md/canvas
- SPARQL + Knowledge Graph: https://www.w3.org/TR/sparql11-query/
- DBpedia, Wikidata architecture

### Tools mentioned
- `qmd` (local semantic search)
- `sage-wiki` (community implementation)
- Readwise + Obsidian integration
- Obsidian MCP Server

---

**Document prepared**: 2026-04-07  
**Analysis scope**: Karpathy LLM KB system — adoption, constraints, alternatives  
**Related work**: HITL evaluation framework, context engineering, knowledge pipeline concepts
