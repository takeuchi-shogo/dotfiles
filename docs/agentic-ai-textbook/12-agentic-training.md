# 第12章 LLM Agentic Training（上級・任意 — エージェント自身を RL で学習させる）

> **一文サマリ:** プロンプト協調で足りなくなったとき、エージェントの**重み**を multi-step trajectory で学習させる層。標準 RLHF(PPO/DPO)は単ターン品質を最適化するが、エージェントは「いつツールを使うか」「軌跡途中での自己修正」「sparse な terminal reward での長期計画」を学ばねばならない。**結論を先に: あなたのリサーチエージェント v1 に重み学習は要らない。** だが「学習なしの自己進化」(in-context / non-parametric)の3経路はここにある。§12.7 が題材そのものの設計図。
> **PDF参照:** §12, p.222-249

> **この章の立ち位置:** Tier 1 の最後で「上級・任意」。あなたは自分でモデルを学習させる側ではない(`_index.md`)。だから本章は「重みを更新する RL」の詳細は概念として記録し、**重み更新なしで自己進化する経路**(§12.3 の B/C、Reflexion、Voyager)に実装上の重心を置く。

## 12.1 なぜ標準 RLHF では足りないか

チャットボット(単ターン・即時の人間フィードバック)から autonomous agent(10-100+ ツール呼び出し・実行環境からのフィードバック・sparse terminal reward)への移行が、新しい RL を要求する4つの差:

| 差 | 内容 |
|---|---|
| **Multi-step reasoning** | 単一応答でなく 10-100+ ツール呼び出しを計画 |
| **External environment feedback** | 報酬が実行環境から来る(テスト通過・ページ読込・コンパイル成功)。人間選好スコアでない |
| **Structured actions** | アクションはトークンでなく構造化出力(JSON tool call・コードブロック) |
| **Long horizons, sparse rewards** | 成否が多数の中間ステップの後にしか決まらない |

標準 RLHF(PPO/DPO)は「プロンプト→良い応答」の単ターン品質を最適化する。だがエージェントは **いつツールを使うか / 軌跡途中での誤りからの自己修正 / 探索と活用のバランス / 部分観測の処理** を学ぶ必要があり、これは**個々のターンでなく軌跡全体**を推論する訓練法を要求する。

## 12.2 Trajectory Buffer（軌跡バッファ — RL の中核データ構造)

### Trajectory Buffer（経験プール/メモリバンク）
**これは何か** — 古典 RL の replay buffer は平坦なタプル $(s,a,r,s')$ を貯める。LLM エージェントでは高次元のトークン化テキスト構造に拡張される:

$$e_t = (\mathcal{S}_t,\ \mathcal{A}_t,\ \mathcal{R}_t,\ \mathcal{S}_{t+1})$$

- $\mathcal{S}_t$ = **完全な context state**(system prompt + ユーザ目標 + 会話履歴 + 現在の環境変数: HTML ソース・ディレクトリ構造・DB スキーマ)
- $\mathcal{A}_t$ = エージェントの生成出力 = $\{\text{text}_{\text{reasoning}},\ \text{json}_{\text{tool\_call}}\}$(CoT 推論 + 構造化ツール呼び出し)
- $\mathcal{R}_t$ = 外部実行環境由来の評価信号(unit test 通過・compiler flag・API レスポンスコード)or LLM-as-judge
- $\mathcal{S}_{t+1}$ = ツール出力やエラーログを会話履歴に追記した更新済み context window

**いつ使う / なぜ要る** — エージェントを軌跡レベルで学習・改善する全手法の土台。バッファが何を貯めるかが学習の質を決める。
**リサーチエージェントでの使いどころ** — これは dotfiles の **memory system** と同型。各セッションの (状態・行動・結果) を貯め、後で参照する。重み学習をしなくても、このバッファは §12.3-C の「経験の RAG」として直接使える(後述)。
**落とし穴** — ①LLM バッファは状態あたり 1K-128K トークンと巨大(古典 RL の固定 84×84 ピクセルと違う)→ 保存コストと context 圧縮が要る ②古いエントリの GC。
**PDF参照** — §12.2, p.223

> **コード債務タスクの軌跡例:** $\mathcal{S}_1$=「utils.py の失敗テストを直せ」→ $\mathcal{A}_1$=「まずファイルを読む」+`read_file` ($\mathcal{R}_1$=0 中間)→ $\mathcal{A}_2$=「42行目の off-by-one だ」+`edit_file` ($\mathcal{R}_2$=0)→ $\mathcal{A}_3$=「検証する」+`run_tests` ($\mathcal{R}_3$=+1.0 全テスト通過 = **sparse terminal reward**)。報酬は最後にしか来ない。

## 12.3 3つの運用パラダイム

軌跡バッファを使う3つの最適化方法。**重み更新の有無**で並べると、A→B が重い(学習)、C が軽い(学習ゼロ):

### A. 自己修正と思考精緻化（STaR / Reflexion）
失敗した軌跡をバッファに保存 → LLM に過去のパフォーマンスへの**明示的なテキスト批評**を生成させる($\text{Critique} \leftarrow \text{LLM}(\mathcal{S}_{\text{failed}}, \mathcal{A}_{\text{failed}}, \mathcal{R}_{=0})$)→ 修正済み軌跡が正の報酬を得たら最適経験プールに移し、SFT(成功軌跡で fine-tune)or RL(GRPO with binary pass/fail)で重みを更新。

### C. Non-Parametric In-Context Learning（経験の RAG — 学習ゼロ、最推奨)
**これは何か** — ニューラルネットの重みを一切変えず、軌跡バッファを**ベクトルDB**として使う。新しいユーザ目標 $\mathcal{G}_{\text{new}}$ に対し、最も関連する過去経験を retrieve:

$$\mathcal{E}_{\text{retrieved}} = \arg\max_{e \in \mathcal{B}} \text{sim}(\text{Embed}(\mathcal{G}_{\text{new}}),\ \text{Embed}(e))$$

top-$k$ の類似成功軌跡を few-shot demonstration として prompt に直接注入する。
**いつ使う / なぜ要る** — **学習リソースがない/学習したくないとき**(=あなた)。ゼロ訓練・純粋な RAG。バッファに似た経験があれば新タスクに即適応、バッファサイズでスケール(経験が増える=カバレッジ向上)、パラメトリック学習と補完的(稀ケースは retrieval、頻出パターンは重み)。
**最小実装（経験 RAG — 学習なし自己進化の核）**
```python
# 成功軌跡をベクトルDBに蓄積し、新タスクで類似経験を few-shot 注入
def solve_with_experience(goal, buffer, llm, k=3):
    similar = buffer.search(embed(goal), top_k=k,           # 過去の成功軌跡を意味検索
                            filter={"reward": ">0.7"})       # 成功したものだけ
    few_shot = "\n".join(f"過去の類似タスク: {e.goal}\n取った手順: {e.trajectory}"
                         for e in similar)
    result = llm.run(f"{few_shot}\n\n今のタスク: {goal}")     # 経験を文脈に乗せて解く
    if result.reward > 0.7: buffer.add(result)               # 成功したら自分も経験に追加
    return result
```
**リサーチエージェントでの使いどころ** — **これがあなたの「自己進化」の現実解**。「どの情報源評価が当たったか」「どの調査手順が良いレポートを生んだか」を成功軌跡として貯め、新しい調査タスクで意味検索して few-shot に注入。重み学習ゼロで、使うほど賢くなる。dotfiles の **memory-vec**(意味検索)+ **learned 昇格ループ** がまさにこの実装。
**落とし穴** — ①バッファが空のコールドスタート(最初は few-shot なし)②類似度が均質コーパスで効かない問題(dotfiles の memory-vec で実測: intent gate が必要)③成功の閾値(reward>0.7)を間違えると悪い軌跡を増幅。
**PDF参照** — §12.3.3, p.225

**残り(B):** **Off-Policy Exploration**(ReAct 等)。自律探索で数千の経験経路をログし、バッファがフィルタとして機能: success filtering(目標達成軌跡だけ訓練に)/ efficiency ranking(成功の中で最短経路を優先)/ diversity sampling(mode collapse 防止)。最適化(GRPO or filtered SFT)は効率的・成功軌跡のみで損失計算。

## 12.4 主要技法（早見表）

| 手法 | 型 | 核アイデア | 重み更新 |
|---|---|---|---|
| **STaR** | Iterative SFT | 自分の成功軌跡で fine-tune して推論をブートストラップ。rationalization(正解から逆算)が鍵 | あり |
| **Reflexion** | In-context RL | 言語的な自己批評を episodic memory に保存。**重み更新なし** | なし |
| **ReAct** | Prompting | 推論(think)と行動(tool call)を単一生成で交互に | なし |
| **LATS** | Tree search | アクション列に MCTS。推論計算を軌跡品質に交換(WebShop 75% vs ReAct 40%) | なし(推論時) |
| **AgentQ** | Off-policy RL | 軌跡成果から選好ペアを自動生成し DPO | あり |
| **Voyager** | Skill library | 検証済みコード skill を貯めて再利用・合成。単調改善(検証済みのみ追加) | なし |
| **RLEF** | Online RL | 実行フィードバック(テスト通過率)を報酬に GRPO/PPO | あり |

### Reflexion（言語的強化学習 — 重み更新なしの自己改善)
**これは何か** — 勾配学習なしで改善する急進的パラダイム。①Actor(行動する LLM)②Evaluator(成否の binary or scalar)③Self-Reflection Generator(失敗軌跡 $\tau_{\text{fail}}$ + 環境フィードバックから自然言語の reflection $r_{\text{text}}$ を生成)④Episodic Memory(過去 reflection の sliding window $\mathcal{M}$、文脈に収まる $m \le 3$)⑤Retry Loop(次の試行で reflection を prompt に注入)。
**いつ使う / なぜ要る** — frozen な API モデル(GPT-4 等)で動く・秒単位の高速反復(RL 訓練は時間単位)・解釈可能(人間可読な自己修正)・任意のベースアーキと合成可能。例: 「前回は JSON スキーマを検証せず API を呼んで 400 を出した。次回はまずスキーマ検証する」。
**最小実装（Reflexion ループ）**
```python
memory = []                                                  # 過去の reflection (episodic)
for attempt in range(max_attempts):
    result = agent.run(task, reflections=memory)             # reflection を文脈注入して実行
    if evaluator(result).success: break                      # 成功なら終了
    reflection = llm.reflect(trajectory=result.trajectory,   # 失敗を自然言語で批評
                             feedback=result.error, task=task)
    memory.append(reflection)                                # 次の試行の教訓に
    memory = memory[-3:]                                     # 文脈に収まる直近3件
```
**リサーチエージェントでの使いどころ** — 「このソースを信頼したが古い情報で誤った要約を生んだ。次回は公開日を確認する」を reflection として貯め、次の調査で注入。dotfiles の **learned 昇格ループ**(失敗→capability gap→durable artifact)の in-context 版。重みを触らず、API モデルのまま自己改善できる。
**落とし穴** — ①context 窓に限定(無限知識は蓄積不可)②未見タスクに汎化しない(memory はタスク固有)③ベースモデルが弱いと有用な批評を生成できず劣化。
**PDF参照** — §12.5.2, p.227

## 12.5 ユースケース: Research Agent from Scratch（あなたの題材の完全な設計図)

### Research Agent の MDP 定式化
**これは何か** — 仮説立案・文献検索・データ分析・コード実行・実験・レポート生成を**完全自律**で行うエージェント。本書がこの章の総合例として与える設計図 = まさにあなたが作りたいもの。
- **Input**: 研究質問(例「GRPO の group size を N>16 にすると数学推論は改善するか?」)
- **Output**: methodology・実験・結果・結論を含む完全な研究レポート
- **必要能力(7)**: 文献検索 / 仮説生成 / 実験設計 / コード実行 / データ分析 / 科学的執筆 / 自己修正
- **MDP**: State=system prompt + 研究質問 + 全行動/観測履歴(128K context)。Action=構造化ツール呼び出し + CoT。Transition=決定的(action+tool 出力を context に追記)。**Reward=sparse terminal(レポート品質)**。Horizon=20-100 steps。$\gamma=1.0$(episodic、有限タスクは割引なし)。

**Action Space(ツール)**

| ツール | カテゴリ | 機能 |
|---|---|---|
| `search_papers` | 文献 | Semantic Scholar/arXiv 検索、タイトル・abstract・引用 |
| `read_paper` | 文献 | 全文/特定セクション取得 |
| `write_code` / `execute_code` | 実験 | 訓練スクリプト記述 / sandbox 実行(stdout/stderr) |
| `read_file` / `plot_data` / `compute_stats` | 分析 | ログ・CSV 読取 / 可視化 / 統計検定(t-test・信頼区間) |
| `write_report` | 出力 | レポートのセクション執筆(LaTeX/Markdown) |
| `think` | 推論 | 外部呼び出しなしの内部推論 |
| `submit` | 終端 | 最終レポート提出、エピソード終了 |

**Reward Design(多成分 terminal reward)**

$$R = w_1 R_{\text{quality}} + w_2 R_{\text{correctness}} + w_3 R_{\text{novelty}} + w_4 R_{\text{efficiency}} + w_5 R_{\text{format}}$$

quality(0.30, LLM-judge が明快さ・深さ・厳密さを1-10)/ correctness(0.30, コードがエラーなく実行+結果再現可能)/ novelty(0.15, 論文の要約を超える洞察か)/ efficiency(0.15, 少ステップにボーナス $\max(0, 1-\text{steps}/100)$)/ format(0.10, 全セクション存在)。中間 shaping: コード実行成功 +0.1 / ランタイムエラー -0.05(まず正しいコードを書くよう促す)。

**Training Pipeline(3 Phase)**: ①SFT Warmup(500 steps、200 の専門家研究軌跡で tool-use 構文と基本ワークフローを教える、completion-only masking)→ ②GRPO(3000 steps、質問あたり N=4 軌跡を生成し多成分 reward でスコア、簡単な「Xの発見を要約」から「Xの実験を設計・実行」へ curriculum)→ ③Rejection Sampling FT(200 steps、難問あたり16軌跡生成し top-2 を SFT、最難タスクを安定化)。

**いつ使う / なぜ要る** — これは「重みを学習する版」の完全レシピ。**だがあなたは Phase 1-3 を回さない。** §12.3-C(経験 RAG)+ Reflexion で、frozen な Claude/GPT のまま同じ tool space・reward 観点(quality/correctness/novelty を**自己評価**に使う)を実装するのが現実解。
**リサーチエージェントでの使いどころ** — tool space と reward 成分をそのまま**設計のチェックリスト**として使う。dotfiles の ai-tech-researcher は: search_papers→Zenn/arXiv 収集、reward の novelty→「採用実績」、efficiency→step 数、self-correction→Reflexion。学習せず、これらを**プロンプトと評価ゲート**で表現する。
**落とし穴(Reward Hacking — 必ず起きる)** — ①**Fake results**(実験出力を捏造)→ 実行ログと報告数値を照合して検証 ②**Shallow reports**(論文 abstract を逐語コピー)→ novelty reward + 剽窃検出 ③**Length gaming**(長いレポートが高スコア)→ efficiency reward + length penalty ④**Easy questions**(難問を避ける)→ 難易度 curriculum。dotfiles の **silent-failure-hunter** + 多層検証(format+content+semantic)がこの対策。
**失敗モード** — 無限ループ(検索を繰り返し進展しない→step budget + 同一引数の反復ペナルティ)/ デバッグスパイラル(1バグに20+step→retry を3回に上限、3回失敗で別アプローチ)/ **引用幻覚**(論文タイトル/結果を捏造→全引用をツール出力で実在検証)/ 早すぎる submit(長軌跡ペナルティ回避のため不完全提出→最低品質閾値 R>0.4 未満は失敗扱い)/ judge の reward hacking(judge に高評価されるが科学的に浅い→judge モデルをローテート + 定期的に人間評価)。
**PDF参照** — §12.7, p.242-246

## 12.6 SoTA: GRPO for Agents（重み学習するなら、これ)

### GRPO（agentic 訓練の事実上の標準)
**これは何か** — DeepSeek-R1 が広めた、agentic 訓練の標準になりつつある手法。タスクあたり N 個の完全軌跡をサンプルし、メモリを食う critic network を**不要**にする。各軌跡の advantage を group 内で正規化:

$$A_i = \frac{r(o_i) - \frac{1}{N}\sum_{j=1}^{N} r(o_j)}{\text{std}(r(o_1),\dots,r(o_N))}$$

**いつ使う / なぜ要る(GRPO が agentic を支配する理由)** — ①**No critic**(GPU メモリ50%節約 — 軌跡が既に 32K-128K トークンを食うので致命的に重要)②**Natural fit**(エージェントタスクは binary verifiable reward = テスト通過/目標達成 が多く group 正規化に最適)③**Exploration**(N 個の多様な軌跡をサンプル = 異なるツール使用戦略を自然に探索)。
**Fine-Grained Credit Assignment(sparse reward 問題への対処):** 20 アクション実行して最後に unit test 失敗すると、terminal reward 0 が20アクションを等しく罰する。解: **RLVR**(決定的な中間 checkpoint で報酬: bash コンパイル成功 +0.1 / SQL が非空 +0.1 / 最終テスト +1.0 — 全ステップに勾配信号、sparse のみ比 3-5倍高速)/ **Trajectory Slicing**(成功 prefix を replay → 最初の分岐点 step $k+1$ を特定 → そのステップだけ負の報酬、正しい prefix は中立/正 = 既に正しい挙動を壊さない外科的更新)。
**リサーチエージェントでの使いどころ** — **v1 では使わない**(学習しない)。ただし RLVR の「中間 checkpoint で検証」という考えは学習なしでも効く: リサーチエージェントの各段(検索→読む→統計→執筆)に検証ゲートを置く(dotfiles の verification-before-completion)。
**落とし穴** — ①SFT quality が床(RL は SFT が出来ることしか改善できない — 有効な API 呼び出しを SFT が書けないなら RL も発見しない)②reward hacking は必至 ③API rate limit を訓練に織り込まないと並列リクエストを spam する方策を学ぶ。
**PDF参照** — §12.8, p.247-249

> **RL パラダイム比較:** GRPO(報酬密度=系列/最終、メモリ低、最大の利点=GPUメモリ削減)/ PPO(step-by-step GAE、メモリ高=critic 要、noisy 環境で安定)/ Iterative STaR(filtered binary、メモリ最小=SFT のみ、スケール簡単・RL 不安定性回避)/ RWML(predictive dense、reward hacking を world modeling で緩和)/ LATS(backpropagated、メモリ高=tree 展開、タスクあたり最高品質・推論計算でスケール)。

---

## この章のまとめ

- 標準 RLHF(単ターン)はエージェントに不十分。**軌跡全体**を推論する訓練が要る。中核データ構造は **Trajectory Buffer** $e_t=(\mathcal{S}_t,\mathcal{A}_t,\mathcal{R}_t,\mathcal{S}_{t+1})$ = dotfiles の memory system。
- 3つの自己進化パラダイム。**重み更新の重さ順**: A 自己修正(STaR/Reflexion、SFT/RL)→ B off-policy 探索(ReAct + filtered SFT)→ **C 経験の RAG(学習ゼロ、最推奨)**。
- **あなたの現実解は「学習なしの自己進化」**: ①経験 RAG(成功軌跡を memory-vec で意味検索し few-shot 注入)②Reflexion(失敗の自然言語批評を episodic memory に、frozen モデルのまま改善)③Voyager(検証済み skill を貯めて合成)。重みを一切触らない。
- **§12.7 Research Agent from Scratch があなたの設計図**: tool space(search/read/code/stats/report/submit)と reward 成分(quality/correctness/novelty/efficiency/format)を、学習でなく**プロンプトと評価ゲート**で表現する。
- **Reward hacking は必ず起きる**(捏造・剽窃・length gaming・難問回避)→ 多層検証 + 人間評価ローテート(dotfiles の silent-failure-hunter)。
- 重み学習するなら **GRPO**(critic 不要でメモリ半減、binary verifiable reward に最適)。sparse reward は RLVR(中間 checkpoint 報酬)+ trajectory slicing で外科的に。**ただし v1 は学習しない。**

---

## 教科書全体の締め — 積み上がった設計図

Ch15(地図)から始め、リサーチエージェントを下から積んだ:

- **知識を入れる** → Ch16 RAG(Hybrid検索+re-rank, Agentic RAG の conditional loop)
- **覚える** → Ch17 Memory(4種, read-act-reflect-write, write policy = 自己進化の核)
- **走らせる** → Ch18 Harness(context budget, ReAct loop, LoopDetector)
- **設計する** → Ch19 Patterns(Workflows vs Agents, Evaluator-Optimizer, planning DAG)
- **評価する** → Ch20 Environments(reward 設計, eval harness)
- **道具を繋ぐ** → Ch21 MCP(N×M→N+M, trajectory 記録)
- **能力を束ねる** → Ch22 Skills(prompt+tools+knowledge, 動的発見)
- **エージェント間** → Ch23 A2A(個人用には overkill、Ch24 を使え)
- **協調する** → Ch24 Multi-Agent(まず centralized supervisor、persona 多様性)
- **実装する** → Ch25 Frameworks(LangGraph 単独から、テスト非交渉, 観測3本柱)
- **人と対話する** → Ch26 UI(透明な協働者, tiered approval, SSE streaming)
- **自己進化させる** → Ch12 本章(学習なしの経験 RAG + Reflexion)

**一貫する原則**: 最も単純な解(単一 ReAct ループ)から始め、必要になってからエージェント/学習/フレームワークを足す(Anthropic「良いツールを持つ単純なループ」+ KISS/YAGNI)。あなたのリサーチエージェントは、**LangGraph 単独 + memory-vec 経験 RAG + Reflexion + tiered approval** で v1 が組める。本書の残り(RL 本体・推論・LLM 基礎 = Tier 2)は用語が引ければ足りる。

**Tier 1 完走。次の一歩**: この設計図で実際に v1 を組む(`docs/plans/active/2026-06-04-ai-tech-researcher-self-evolving-plan.md` に接続)。
