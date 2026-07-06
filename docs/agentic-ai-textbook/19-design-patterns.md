# 第19章 Agent Design Patterns（アーキ層 — パターンの選び方）

> **一文サマリ:** エージェントのアーキテクチャ(オーケストレーション・タスク分解・制御フロー)が信頼性・デバッグ性・コストを決める。本章は本番(Anthropic/OpenAI/Google)で確立した正準パターンと、**「いつどれを選ぶか」**の判断軸。仕組みの詳細は Ch18、ここは選択。
> **PDF参照:** §19, p.369-374

## 19.0 まず: Agents か Workflows か

全タスクに自律エージェントは要らない。決定的な区別:

- **Workflows** — 事前定義された制御フロー。特定ステップでLLMを呼ぶ。**予測可能・テスト可能・安い**。タスク構造が既知なら使う。
- **Agents** — LLMが次の一手を動的に決める。柔軟・新規状況に対応。**適応的な意思決定が要るときだけ**使う。

> **Workflows から始めよ。** 動的ルーティングや開放的探索が本当に要るときだけ Agents へ昇格する。これは dotfiles の "KISS / 3回繰り返すまで抽象化しない / 最小インパクト" と完全に同型。リサーチエージェントも、固定手順で済む部分は workflow、探索が要る収集ループだけ agent。

---

## 19.1 Workflow Patterns（制御フローは「システム」が決める）

Anthropic の agentic building blocks 分類。LLMを**事前定義**の制御フロー内で使う。

| パターン | 仕組み | いつ使う |
|---|---|---|
| **Prompt Chaining** | 複雑タスクを固定の LLM 呼び出し列に分解、結果を次へ流す。間に quality gate | 自然に逐次なタスク(content生成・データ変換・多段分析)。各stepで別prompt/model/temperature、中間結果が検査可能 |
| **Routing** | classifier(LLM or 従来型)が入力を分類し専門handlerへ振る | 別々の最適prompt/tool/modelを要する異種タスク。サポートtriage・マルチモーダル入力 |
| **Parallelization** | 複数LLM呼び出しを並列、プログラムで結果を統合 | **Sectioning**(独立chunkに分割: security/perf/style検査を同時)/ **Voting**(同prompt N回→多数決/reward/judge)。レイテンシ=max(各)であって Σ ではない |
| **Orchestrator-Workers** | orchestratorモデルが**分解の仕方を生成**しworkerに配り統合 | subtaskの数と性質が設計時に列挙できない開放問題(「このコードベースをrefactor」=依存グラフを理解してから決める) |
| **Evaluator-Optimizer** | generatorが候補生成、別のevaluatorが採点、閾値未満なら批評を文脈に足して反復 | 明確な品質基準があるタスク(テストを通すコード・意味を保つ翻訳・スタイル遵守) |

Parallelization は **Sectioning(独立分割)** と **Voting(冗長性)** の2系統。Orchestrator-Workers が Parallelization と違うのは、**分解ロジックがモデル生成(ハードコードでない)**点。

### Evaluator-Optimizer（学習なしの反復改善)
**これは何か** — generator(候補生成)と evaluator(批評+採点)の2モデルのフィードバックループ。スコアが閾値未満なら evaluator の批評を generator の文脈に足して反復、品質バーに達するかretry予算切れまで回す。重みは更新しない。
**いつ使う / なぜ要る** — **明確な品質基準があり、初回で当たらない**タスク。批評を成果物として回す(プロジェクトの "批評を成果物にする" と同型)。
**最小実装**
```python
def evaluator_optimizer(task, gen, evaluator, threshold=0.8, max_iters=5):
    draft = gen(task)
    for _ in range(max_iters):
        score, critique = evaluator(task, draft)        # 採点 + 批評
        if score >= threshold: return draft
        draft = gen(task, feedback=critique)            # 批評を文脈に足して再生成
    return draft
```
**リサーチエージェントでの使いどころ** — 収集した要約の品質ゲート。evaluator が「引用が原典に忠実か(Ch16 Faithfulness)・網羅的か」を採点し、不足なら再収集・再要約。Codex Review Gate と同じ構造。
**落とし穴** — ①evaluator自体のバイアス(Ch14 LLM-as-judge)②閾値到達せず無限ループ(retry予算で打ち切り)③generatorとevaluatorが同モデルだと批評が甘い(別視点を持たせる)。
**PDF参照** — §19.1.5, p.370

---

## 19.2 Autonomous Agent Patterns（制御フローを「LLM」が握る）

**ReAct** — 基礎パターン(think→act→observeのループ)。仕組みは Ch18.5.1 で詳説済み。実装の要点だけ: Thoughtはscratchpad(非表示)/ harnessがtool callをparse / **max iterations 必須(典型10-25)**/ 終了は `final_answer` か tool call 無し。

**Planning Agents** — 実行前に明示的な計画を生成し、途中で改訂する。再計画戦略で4段階:

| 戦略 | 再計画 | 特徴 |
|---|---|---|
| Plan-then-Execute | しない | 単純・予期せぬ結果に脆い |
| **Adaptive** | 失敗時 | step失敗時だけ再計画・中コスト |
| Continuous | 毎step | 各観察後に全再評価・高コストだが頑健 |
| Hierarchical | sub-plan完了時 | 高レベル計画は固定、sub-planを動的生成 |

> **リサーチレポート生成の planning(PDFの実例、あなたの例題そのもの):** ユーザ要求「transformer系の時系列予測アーキを比較する2ページレポートを書け」→ Step1: 計画生成(1 LLM呼び出し)で依存付きDAGを作る:
> ```python
> plan = [
>   {"id":1, "task":"2023-2025の最新transformer時系列モデルを検索", "tool":"search_web", "deps":[]},
>   {"id":2, "task":"上位5論文を読み手法を抽出", "tool":"read_papers", "deps":[1]},
>   {"id":3, "task":"比較表(アーキ/データ/指標)を構築", "tool":"none", "deps":[2]},
>   {"id":4, "task":"序論+方法論を執筆", "tool":"none", "deps":[2]},
>   {"id":5, "task":"結果+結論を執筆", "tool":"none", "deps":[3,4]},
>   {"id":6, "task":"最終レポートをレビュー・推敲", "tool":"none", "deps":[5]},
> ]
> ```
> Step2: 依存順に実行。**Adaptive replanning** — step1の検索が3本しか返さなかったら、隣接ドメインへ広げるsub-stepを足して計画を改訂(PatchTST, iTransformer等)。**計画は living document**: 構造を与えつつ観察に適応し、harnessが依存をDAGで追い前提が揃ったstepだけ実行する。これがリサーチエージェントの調査フローの背骨。

### Reflection / Self-Critique（失敗から学ぶ)
**これは何か** — エージェントが自分の軌跡を評価して軌道修正する。①output validation(「正しいか? 抜けは?」)②trajectory review(直近k stepの誤り・非効率を点検)③strategy revision(「そもそも正しい問題を解いているか?」)。**Reflexion** は永続的な "reflection memory" を持ち、失敗ごとに自然言語の反省(「edge caseをチェックし忘れた」)を書き、次の試行でそれをプロンプトに含める — **重み更新なしの経験学習**。
**いつ使う / なぜ要る** — 初回で失敗しがちなタスク。Ch17 の Reflect 操作の制御パターン版。
**最小実装**
```python
reflections = []                                  # 永続 reflection memory
for attempt in range(max_attempts):
    result = agent(task, hints=reflections)       # 過去の反省を文脈に含めて試行
    if evaluate(result).ok: return result
    reflections.append(llm(f"なぜ失敗したか1文で: {result}"))  # 反省を書き足す
```
**リサーチエージェントでの使いどころ** — 「この情報源は毎回低質だった」「このクエリ表現では良い結果が出ない」を reflection に蓄積し、次の調査で回避。Ch17 の self-evolving と同じ核。
**落とし穴** — ①+50%のオーバーヘッド(毎回反省を生成)②反省が generic だと効かない(具体的失敗に紐づける)③reflection memory が無限増殖(Ch17 の consolidation/forgetting で剪定)。
**PDF参照** — §19.2.3, p.372

**Tool-Use Patterns(Table 19.2):**

| パターン | 説明 | 例 |
|---|---|---|
| Single-turn | 1 LLM応答に1ツール呼び出し(LLM呼出は2回: 選択+統合) | 検索付き単純Q&A |
| Multi-tool (Parallel) | 1応答で複数の**独立**ツールを並列(互いの出力に依存しない) | 検索+計算+カレンダー同時 |
| Sequential (Pipeline) | ツール出力が次の入力へ。次手はモデルが結果で判断 | `search→fetch_page→extract→analyze` |
| Nested (Agent-as-Tool) | ツール呼び出しが別エージェントを起動(専門化) | リサーチagentがコード実行をサブagentへ委譲 |
| Fallback | 優先ツール失敗時に代替へ(harnessが透過的に処理) | API→scrape→cache |

> リサーチエージェントの収集ループは典型的に **Sequential pipeline**(`search→fetch→extract→analyze`)。harnessが膨らむ文脈を追い、中間を要約して予算内に保つ(Ch18.2)。

---

## 19.3 設計原則（全パターン共通)

Anthropic の "Building Effective Agents" 蒸留。dotfiles の `<core_principles>` とほぼ一致する:

1. **シンプルに保て** — 動く最小アーキを使い、必要が実証されたときだけ複雑さを足す。「動く prompt chain」は「動くかもしれない multi-agent」に常に勝る。(=KISS/YAGNI)
2. **賢さより透明性** — 全stepを検査可能に。隠れ状態・暗黙推論を避ける。失敗時に**なぜ**が分からないと直せない。(=観測可能にする)
3. **良いツールを与えよ** — よく文書化され型付きで明確なエラーを返すツールは force multiplier。曖昧なdescriptionは誤用される。
4. **失敗を前提に設計せよ** — 全ツール呼び出しは失敗しうる。retry/fallback/graceful degradation を harness 層に置き、モデルにインフラ障害を推論させない。(=境界でFail Fast)
5. **structured output を使え** — 制約付き生成(JSON schema / function calling)でparse失敗を防ぐ。regex parsing が要る自由文は脆い。
6. **多様な入力でテストせよ** — エージェント挙動は単発chatより分散が大きい。同じpromptが別runで別のtool-call列を生む。edge case・曖昧要求・壊れた入力で敵対的にテスト。

---

## 19.4 パターン選択ガイド（本章の結論）

選択は3因子で決まる: ①タスク構造の予測可能性 ②許容できるLLM呼び出し数(レイテンシ/コスト)③品質に反復が要るか。**上(単純)から始め、単純なパターンが実証的に失敗したときだけ下へ。**

| パターン | 複雑さ | LLM呼出 | 向き |
|---|---|---|---|
| Prompt chaining | 低 | $N$(固定) | 逐次タスク・content pipeline |
| Routing | 低 | $1+1$ | 多型入力・triage |
| Parallelization | 低 | $N$(並列) | 独立subtask・voting |
| Orchestrator-workers | 中 | 可変 | 未知の分解 |
| Evaluator-optimizer | 中 | 2-10(loop) | 品質クリティカル |
| **ReAct** | 中 | 3-25(loop) | 汎用ツール利用・**探索** |
| Planning agent | 高 | 5-50+ | 長ホライズン・多段 |
| Reflection | 高 | +50%overhead | 初回失敗しがち |
| Multi-agent | 高 | 多数 | 複雑ドメイン・専門化 |

> **パターンは合成可能:** planning agent が各stepで prompt chaining を使い、review相で evaluator-optimizer を回し、routing で subtask を専門家に振る。**芸術は "いつ層を足すのをやめるか" を知ること。**

**リサーチエージェントへの当てはめ:** 収集ループ=**ReAct**(探索) + **Planning**(調査命題をDAGに分解、adaptive replanning) + **Sequential tool pipeline**(search→fetch→extract) + **Evaluator-Optimizer**(要約の品質ゲート) + **Reflection**(情報源の良し悪しを学習)。だが**まず ReAct 単体で動かし**、足りない部分だけ層を足す。

---

## この章のまとめ

- **Workflows(構造既知)から始め、Agents(適応必要)へは必要時だけ昇格。** KISS の徹底。
- Workflow 5パターン(chaining/routing/parallelization/orchestrator-workers/evaluator-optimizer)は制御フローを**システム**が、Autonomous パターン(ReAct/planning/reflection)は**LLM**が握る。
- **選択は3因子(予測可能性・呼出予算・反復要否)。単純から始め、実証的に失敗したら下へ。**
- パターンは合成可能 — リサーチエージェントは ReAct+Planning+pipeline+evaluator+reflection の重ね。ただし最小から。
- 設計原則(simple/transparent/good tools/plan-for-failure/structured output/test-diverse)は dotfiles の core_principles とほぼ一致。

**次章 → Ch20 Environments & Benchmarks（評価層）。** 組んだエージェントの挙動を「どこで・どう測るか」に進む。
