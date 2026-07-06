# 第17章 Agentic Memory（エージェントの記憶層）

> **一文サマリ:** メモリは、有限の context window を超えてエージェントに永続性を与える層。「過去の調査を覚える / 経験から学ぶ / ユーザーを覚える」を実現し、リサーチエージェントの**自己進化**（どの情報源が当たりかを学習する）の土台になる。
> **PDF参照:** §17, p.320-341

LLMは本質的に **stateless な関数近似器**。生成時に見られるのは context window（有限のtoken列、例: $L=128\text{K}$）だけ。短い自己完結タスクなら足りるが、何日も走るエージェントには根本的なボトルネック。メモリはこの物理制約への工学的回答。

メモリ無しで起きる3つの故障: ①**Catastrophic forgetting**（窓から流れ出た情報は復元不能、1万token前の決定を参照できない）②**経験から学べない**（毎エピソードが初回、成功戦略を再利用できず失敗を繰り返す）③**パーソナライズ不能**（毎セッション冷えた状態から）。

形式的には、エージェントを $\mathcal{A}=(\pi_\theta, \mathcal{M}, \mathcal{R}, \mathcal{W})$ — policy（LLM）/ memory store / retrieval関数 / write関数 — の組と見る。各ステップで観測 $o_t$ → 関連記憶を検索 $c_t=\mathcal{R}(o_t,\mathcal{M})$ → 行動、その後 $\mathcal{M}\leftarrow\mathcal{W}(\mathcal{M},(o_t,a_t,r_t))$ で書き込む。

---

## 17.2 メモリの4分類

### 認知科学由来の4タイプ
**これは何か** — 生物のメモリ区分を借りた4分類。**neuroscienceの模倣が目的ではなく、アクセスパターン・更新頻度・検索機構が本当に異なるから**分ける。

| タイプ | 中身 | LLMでの実体 | 性質 |
|---|---|---|---|
| **Working**（作業） | いま操作中の情報 | scratchpad / CoT / 直近の会話履歴 | 高速(検索ゼロ)・揮発・容量限界($L$) |
| **Episodic**（エピソード） | 特定の過去の出来事 | 過去の対話・成功軌跡・失敗事例 | vector storeで実装、エピソード要約をembedding |
| **Semantic**（意味) | 一般的な事実・概念 | 事実知識・ドメイン概念・knowledge graph | context非依存(いつ学んだかと無関係) |
| **Procedural**（手続き) | やり方・スキル | tool-use パターン・行動列・policy(重み) | 成功軌跡でのfine-tuningは手続き記憶の固定化 |

**いつ使う / なぜ要る** — どの記憶をどう持つかの設計地図。タスクの問い方で必要な記憶が違う(factoid質問→atomic fact、文脈質問→episode要約)。
**リサーチエージェントでの使いどころ** — Episodic=「過去の調査セッションと成否」、Semantic=「収集で蓄えたドメイン事実・トピックのグラフ」、Procedural=「論文を構造化要約する手順」。Workingは現在の調査ループの作業領域。**自己進化の主戦場は Episodic（成功/失敗から学ぶ）と write policy（§17.7）**。
**落とし穴** — 4タイプを1つの vector store に混ぜると検索が濁る。アクセス頻度・更新頻度が違うので分けて持つ。
**PDF参照** — §17.2, p.321-322

---

## 17.3 メモリアーキテクチャ

実装の器は5系統。リサーチエージェントの既定は **RAG-based（vector store）+ 階層管理**。

| アーキ | 仕組み | 向き / 備考 |
|---|---|---|
| **RAG-based** | 文書集合をembeddingして top-k 検索（dense/sparse/hybrid+RRF, $k=60$） | 既定。Ch16 の検索技術がそのまま使える。出典メタデータ必須 |
| **Summarization-based** | running summary を逐次更新 $S_{t+1}=\text{LLM}(S_t+e_t)$ / 階層圧縮 $L_0\supset L_1\supset\cdots$ | サイズ $O(1)$ だが詳細を失う。逐語保存すべきは事実・コード・数値・引用、要約は物語的文脈 |
| **Graph-based** | 三つ組 $(h,r,t)$ の知識グラフ。GraphRAG は $k$-hop 近傍探索で multi-hop に強い。Temporal KG は妥当性区間 $[t_{start},t_{end}]$ を持つ | 「2023年のOpenAI CEOは誰?」の時制を混同しない。複雑な多段推論向け |
| **KV Memory Network** | key-value 対へ soft attention $\alpha_i=\text{softmax}(q^\top k_i/\sqrt{D})$ | 微分可能・end-to-end学習可。transformer attentionはこの特殊形 |
| **MemGPT / 仮想context** | hot/warm/cold の tier。LLM自身が `memory_search/insert/delete` を発行して page-in/out | メモリ管理が**学習行動**になる(§17.7 のRL対象)。OSの仮想メモリ類推 |

> RAGがメモリのhallucinationを消すわけではない — **悪化させうる**。古い/誤った/表層的に似ただけの文書を自信満々に取り込む。出典・timestamp・confidenceのprovenanceを必ず持ち、faithfulness検証(Ch16)を挟む。

---

## 17.4 メモリ操作（Write / Read / Update / Reflect）

4操作のうち、**Write（何を覚えるか）**と**Reflect（メタ認知)**がエージェントの賢さを決める。この2つを6フィールドで。

### Write — 記憶へのコミット（フィルタ問題）
**これは何か** — 全観測を保存しない。$\text{Write}(e)=\mathbf{1}[\text{importance}(e)>\tau]$ の閾値フィルタ。importance の見積もりは ①**Surprise**($-\log p_\theta(e|\text{context})$、予想外ほど情報的) ②**Reward signal**(|報酬|が大きい出来事) ③**LLM self-assessment**(1-10で自己採点)。書く前に既存記憶との矛盾検出 $\text{Conflict}(f_{new},\mathcal{M})$ も。
**いつ使う / なぜ要る** — 全保存はノイズと storage 爆発を招き、検索を濁らせる。「何を残すか」が記憶品質の上流。
**最小実装**
```python
def should_write(event, llm) -> bool:
    importance = llm(f"次の出来事の重要度を1-10で: {event}")  # LLM self-assessment
    return int(importance) > 6                                 # τ=6

# 粒度の選択(Table 17.1): 細かいほど後で粗くできる。逆は不可能
# atomic fact「ユーザはPythonを好む」/ structured note(A-MEM) /
# summarized episode(MemGPT) / verbatim transcript
```
**リサーチエージェントでの使いどころ** — 「この情報源は良質/低質だった」「このトピックは既出」を episodic に書く判断。**Surprise ベースが効く**(既知の焼き直し記事は importance 低、新規性ある論文は高)。**最も細かい粒度で保存し、上に粗いビューを作る**（atomic factは要約できるが、要約からatomは復元不能）。
**落とし穴** — ①書きすぎ→ノイズ、書かなすぎ→欠落。write selectivity を監視 ②provenance（出典リンク）を毎エントリに付けないと検証も監査も不能 ③矛盾検出を怠ると古い事実と新しい事実が共存して検索が壊れる。
**PDF参照** — §17.4.1, p.324-325

### Reflect — メタ認知（経験を洞察に変える）
**これは何か** — エージェントが**自分の記憶を読んで洞察を生成**する高次操作。$\text{Reflect}(\mathcal{M})\to\{i_1,i_2,\dots\}\subset\mathcal{M}_{semantic}$。Episodic（具体的過去）から**読み**、Semantic（一般化された洞察）へ**書く**。計算自体は working memory で行う。これが Reflexion（言語的強化学習）の中核。
**いつ使う / なぜ要る** — 失敗を繰り返さないため。3回同じ失敗→「入力リストが空のケースを毎回忘れる」という洞察を生成→semanticに保存→次回はそれを検索して明示チェック。生物が睡眠中にepisodicをsemanticへ固定するのと同じ。
**最小実装**
```python
def reflect(memory, llm, k=10) -> list[str]:
    recent = memory.retrieve("recent important events", k=k)
    prompt = f"これらの記憶から2-3個の高次の洞察を抽出:\n" + \
             "\n".join(f"- {m.content}" for m in recent)
    insights = llm(prompt).split("\n")
    for line in insights:
        if len(line) > 20:
            memory.write(f"[INSIGHT] {line}", importance=0.9)  # semanticへ高重要度で
    return insights
```
**リサーチエージェントでの使いどころ** — 「情報源Xは毎回低質だった」「このトピックは過去3回調べたが進展なし」という洞察を生成して情報源の取捨選択を進化させる。**これが "自己進化型" の実体**。dotfiles の nightly routine で定期 reflect を回すのが自然(§17.11 Sleep-Time)。
**落とし穴** — ①材料が薄い(エピソード<3)と generic な洞察を hallucinate する(早すぎる reflect を抑止)②洞察を semantic に書きっぱなしで矛盾が溜まる→定期 consolidation 必須。
**PDF参照** — §17.4.4, p.326

**Read と Update（軽め）:** **Read** はクエリ整形（HyDE / query expansion / step-back、Ch16と同じ）+ **時間減衰** $\text{score}=\lambda\cdot\text{sim}+(1-\lambda)\cdot\exp(-(t-t_d)/\tau_{decay})$ で新しい記憶を優先。**Update** は consolidation（関連記憶をクラスタ→要約でマージ）と忘却（LRU / importance加重 / spaced repetition: 繰り返しアクセスされた記憶を長く保持）。

---

## 17.5 マルチターン会話のメモリ

永続 user model $\mathcal{U}$ に明示選好（言明した好み）・暗黙選好（行動から推論: 常にPython・簡潔好み）・専門レベル・進行中プロジェクトを蓄積し、毎交互作用後に更新。セッション開始時に $\mathcal{U}$ と直近要約を引いてパーソナライズ system prompt を注入、終了時に要約して更新。技術: adaptive verbosity / domain priming / proactive recall（「先月これを聞いてましたね」）。

> **プライバシー（必須）:** 永続 user memory は ①保存前に明示同意 ②記憶の閲覧・削除手段 ③マルチユーザでのアクセス制御 ④GDPR/CCPA 準拠 を求める。privacy-by-default で設計する。リサーチエージェントが個人用でも、収集ソースの利用規約とAPIキーの扱いはここに含まれる。

---

## 17.6 マルチエージェントの共有メモリ

複数エージェントが協働するとき、メモリは個人の知識庫でなく**協調機構**になる。共有 store $\mathcal{M}_{shared}$ + 各自の private $\mathcal{M}_i$ で、context$_i=\mathcal{R}(\mathcal{M}_i,q)\cup\mathcal{R}(\mathcal{M}_{shared},q)$。**Blackboard**（全員が読み書きする黒板 + 前提条件を満たしたエージェントを起動する controller）が古典。書き込み衝突は last-write-wins / versioned / voting / confidence加重マージ / designated authority で解決。詳細な協調は Ch24 へ。リサーチで収集役・選別役・要約役を分けるなら、収集結果を blackboard 経由で渡す。

---

## 17.7 RLでメモリを学習する（自己進化の核心）

### 何を覚えるかを学習する（write policy の学習）
**これは何か** — メモリ操作(read/write/update/reflect)を **RLのaction** として扱い、write policy $\pi_{write}(e)$ を将来のタスク性能が最大化するよう学習する。難しさ: ①記憶の価値は将来にしか現れない(遅延報酬)②書く時点で将来クエリ未知 ③記憶は相互作用する($e$を保存する価値は他の記憶に依存)。
**いつ使う / なぜ要る** — 手書きの importance ヒューリスティクスの天井を超えたいとき。ドメインに最適化された**学習された inductive bias**（コーディング agent は API シグネチャを、リサーチ agent は引用チェーンを覚えるよう学習）になる。
**最小実装（概念）**
```python
# 手法の骨子(コードでなく報酬設計が本体):
# ① Hindsight relabeling: 成功エピソード後、実際に検索された記憶を遡って
#    「重要」とラベルし、似た物を保存するよう write policy を訓練
# ② Meta-RL: タスク分布を跨いで write policy を学習(汎化する情報を覚える)
# ③ Curiosity-driven: 予測誤差(surprise)が高い観測を保存
#
# メモリ拡張 policy gradient: L(θ,φ) = E[Σ γ^t r_t] − λ·L_mem(φ)
#   θ=LLM, φ=メモリ系のパラメータ(検索モデル重み等)
r_mem = r_task + α*r_retrieve + β*r_write + γ*r_consistency  # 操作ごとの合成報酬
```
**リサーチエージェントでの使いどころ** — **これが "自己進化型情報収集" の理論的背骨**。「採用された情報の出典」を hindsight でラベルし、似た出典を優先的に覚える write policy を育てる。ただしv1はヒューリスティック(§17.4 Surprise/reward)で十分、RL化はv2。`ai-tech-researcher` プランの「採用実績で情報源を進化」がまさにこれだが、**採用実績の主指標化は評価ゲーミング**を招く点に注意(MAB探索/多様性/時間減衰で封じる、プラン側の警告通り)。
**落とし穴** — ①遅延報酬で学習が不安定 ②報酬を「覚えた量」にすると溜め込みすぎる(efficiency reward $-\lambda\cdot\mathbf{1}[\text{write}]$ で抑制)③コールドスタート(初期は実績ゼロ)。
**PDF参照** — §17.7, p.328-329

---

## 17.8 アーキテクチャ比較(Table 17.2)

| アーキ | 容量 | 検索 | 更新コスト | 学習可 | 向き |
|---|---|---|---|---|---|
| In-context (working) | $O(L)$ token | 0ms | 無料 | FT経由 | 短タスク・能動推論 |
| Dense RAG | $O(10^7)$ doc | 10-50ms | embedのみ | encoderのみ | 意味検索・QA |
| Sparse (BM25) | $O(10^8)$ doc | 1-5ms | index | 不可 | キーワード・法務医療 |
| Hybrid RAG | $O(10^8)$ doc | 15-60ms | embedのみ | encoderのみ | 汎用(既定) |
| Summarization | 無制限 | 0ms(in-ctx) | LLM呼出 | FT経由 | 長会話・物語 |
| Knowledge Graph | $O(10^9)$ triple | 5-100ms | insert | embed層 | 構造化事実・multi-hop |
| MemGPT tiered | 無制限 | 0-100ms | 混在 | RL経由 | 長期エージェント・アシスタント |
| Graph RAG | $O(10^7)$ node | 20-200ms | insert | encoderのみ | 複雑推論・コミュニティ |

---

## 17.9 メモリの評価

質は**下流タスク性能を通じて間接的にしか現れない**ので評価が難しい(完璧な recall でも無関係 context を引けば失敗)。**LongMemEval** が長期メモリの5能力を定義: ①情報抽出(会話から要点を保存できるか)②マルチセッション推論(複数セッションを跨いで統合)③時制推論("再編前の優先度は?")④知識更新(事実変化を反映しつつ履歴保持)⑤**Abstention**(関連記憶が無ければ捏造せず「分からない」と言えるか)。

指標 — メモリ層: Recall / Precision / Latency / Token efficiency。下流: Answer accuracy / Faithfulness / Contradiction rate。運用: write selectivity / staleness / storage growth rate。

> **評価のギャップ:** 多くの研究は短いベンチ(10-50セッション)で評価するが、本番は数ヶ月・数千セッション走る。**長期ホライズンでの memory drift・矛盾蓄積・storage 肥大**こそ支配的故障モードで、未解決。ベンチスコアに加えて運用指標の縦断監視を。

---

## 17.10 実装パターン

実装は3層: **VectorMemoryStore**（embedding+メタデータ、時間減衰込みhybrid検索、重複検出、LRU evict）→ **HierarchicalMemoryManager**（hot/warm/cold tier、アクセス頻度で自動昇格降格）→ **MemoryAugmentedAgent**（read-act-reflect-write ループ）。下は最上位ループの骨格。

### Read-Act-Reflect-Write ループ
**これは何か** — メモリ系をエージェントの推論ループに織り込む4相サイクル(MemGPT発・CoALAで形式化)。応答前に関連記憶を**読み**、応答を生成(**act**)、定期的に洞察を**reflect**、重要情報を**write**。LLM出力中の特殊token(`[MEMORY_SEARCH]` 等)がメモリ操作を起動し、モデルが自分の永続性を自己制御する。
**いつ使う / なぜ要る** — セッションを跨いで賢くなるエージェントの標準形。OODA ループ / 認知心理の encode-store-retrieve と同型。記憶は受動的な倉庫でなく**能動的な認知の参加者**。
**最小実装（骨格、Listing 17.3 を簡約）**
```python
class MemoryAugmentedAgent:
    def step(self, user_message: str) -> str:
        memories = self.memory.retrieve(user_message, k=5)        # 1. Read
        messages = self._build_messages(user_message, memories)
        raw = self.llm(messages)                                  # 2. Act
        clean, ops = self._parse_memory_commands(raw)             # [MEMORY_*] を抽出
        self._execute_memory_ops(ops, user_message, clean)        # search/write/reflect 実行
        self._auto_write(user_message, clean)                     # 4. Write(ヒューリスティック)
        # 定期的に self._reflect() を呼ぶ                          # 3. Reflect
        return clean
```
**リサーチエージェントでの使いどころ** — 調査ループの背骨。「過去に同じトピックを調べたか」を Read、新発見を Write、「この分野の進展パターン」を定期 Reflect。tiered manager の hot=現在の調査文脈 / warm=最近の調査 / cold=アーカイブ。
**落とし穴** — ①`_auto_write` のキーワードヒューリスティックは粗い(重要な物を取りこぼす/ノイズを書く)→ importance 判定をLLMに寄せる ②reflect を毎ターン呼ぶとコスト爆発(定期/idle時に)③hot tier の容量超過時の要約 compress を忘れると context 溢れ。
**PDF参照** — §17.10, p.331-339

---

## 17.11 最近の進展

| 手法 | 要点 | リサーチagentへの示唆 |
|---|---|---|
| **CoALA**（Cognitive Architectures for Language Agents） | 新システムでなく**設計言語**。modular memory(4分類)+構造化action空間(内部/外部)+ sense-plan-act 決定サイクルで既存agentを分析し**欠けた能力を特定** | 自分のagentを CoALA で棚卸しして穴を見つける参照アーキ |
| **Mem0**（本番スケール記憶層） | LLMに明示コマンドを出させず**自動で要点抽出**+関係グラフ+圧縮。LOCOMOで baseline比+26%、p95レイテンシ-91%、token -90% | 「自動抽出」は self-evolving 収集に直結。出力をそのまま採用候補にできる |
| **Sleep-Time Compute**（オフライン記憶処理） | クエリ時でなく**交互作用の合間(idle="睡眠")に記憶を整理・先読み計算**。推論ベンチで test-time計算 5倍削減、関連クエリ群でコスト2.5倍減 | **dotfiles の nightly routine がまさにこれ**。夜間に収集物を consolidation/reflect。offline RL(Ch12)とも繋がる |
| **A-MEM**（Zettelkasten式） | 各記憶を**構造化note**(説明+keyword+関連noteへのリンク)に。新規追加時に既存noteへ双方向リンク+既存を**更新**(memory evolution)。LLMが組織化を自己決定 | 「どう組織化するか」が「何を貯めるか」と同等に効く。Obsidian Vault的な知識ネットワーク化 |

---

## この章のまとめ

- メモリは有限 context window への工学的回答。無いと「忘却・経験から学べない・パーソナライズ不能」の3故障。
- **4分類**(working/episodic/semantic/procedural)はアクセス・更新・検索が違うから分ける。リサーチ自己進化の主戦場は **Episodic + write policy**。
- **器は5系統**(RAG/要約/グラフ/KV/MemGPT tier)。既定は RAG-based + 階層管理。
- **操作の要は Write(何を覚えるか)と Reflect(経験→洞察)**。Surprise ベースの write、失敗3回での reflect が効く。
- **RLで write policy を学習**するのが "自己進化" の理論背骨。だが採用実績の主指標化は評価ゲーミングを招くのでv1はヒューリスティック、探索/多様性/時間減衰で封じる。
- 実装は read-act-reflect-write ループ。dotfiles の nightly = **Sleep-Time Compute**(夜間 consolidation/reflect)。
- 評価は下流で間接的。長期の drift/矛盾/肥大が本番の支配的故障 → 運用指標を縦断監視。

**次章 → Ch18 Agent Harness（実行時層）。** 記憶した知識を回す「OS」=エージェントループ・文脈予算・ツール発行・エラー回復に進む。
