# 第25章 Agent Development Frameworks（実装層 — プロトタイプを本番システムにする）

> **一文サマリ:** Jupyter で動くエージェントを作るのは簡単。本番で動くエージェント(エッジケース処理・障害復旧・負荷スケール・継続改善)を作るのは根本的に別の工学規律。本章は LangGraph/AutoGen/CrewAI/OpenAI SDK/DSPy/Semantic Kernel の選び方と、テスト・観測・デプロイ。リサーチエージェントを「本番品質」に引き上げる章。
> **PDF参照:** §25, p.459-489

## 25.1 The Engineering Gap（プロトタイプと本番の溝）

研究プロトタイプは協調的環境を仮定する: 整った入力・利用可能なツール・応答するAPI・失敗したら再起動してくれる忍耐強い人間。本番エージェントにはどれもない。溝は5次元:

| 次元 | 本番で要求されること |
|---|---|
| **Reliability** | ツール障害を優雅に処理、部分的状態破損から復旧、無限ループ/暴走API呼び出しを回避。**エラー処理は ad hoc でなく systematic** |
| **Observability** | 誤答時に**なぜ**そうしたか分かる。全LLM呼び出し・ツール実行・状態遷移の構造化ログ(最終出力だけでなく) |
| **Testability** | 非決定的でcontext依存 → unit test では不十分。eval harness・golden trajectory比較・behavioral test suite |
| **Deployment** | 分〜時間に及ぶstateful長時間プロセス。async実行・checkpoint・障害後の再開・マルチテナント隔離 |
| **Iteration** | 世界が変わればエージェントは劣化。systematic failure分析・prompt versioning・fine-tuningパイプライン |

> **成熟度モデル(stage 2→3 の溝を過小評価しがち):** Prototype(単一スクリプト・ハードコード)→ Alpha(モジュール化・基本エラー処理)→ **Beta(framework化・自動テスト・staging)**→ Production(完全観測・CI/CD・auto-scaling・SLA)→ Mature(継続学習・A/B test・自己改善ループ)。あなたのリサーチエージェントは「Mature」を目指すが、まず Beta を通す。

## 25.2 開発ライフサイクル

`Design → Implement → Test → Deploy → Iterate`、各段に feedback loop(失敗は前段に戻す)。

- **Design**: capability envelope を先に決める(コード前に)。capability matrix(扱うタスク/拒否すべきedge case/スコープ外の挙動)= eval基準の土台。tool selection は**過剰ツールが最大の失敗**(too many tools → 選択混乱+レイテンシ)。constraint(最大ツール呼び出し数・許可ドメイン・出力形式)は system prompt に書く**かつ**プログラムで強制。
- **Implement**: prompt engineering(system prompt は version管理する living document)+ tool integration(typed interface・冪等性)+ orchestration(エージェントループ; framework選択がここを最も左右する)。
- **Iterate**: 全失敗を full context でログ → 失敗を型分類 → prompt変更は regression suite に通してからデプロイ → 限界で fine-tuning → A/B test。

> dotfiles の workflow guide(S/M/L 規模 → Plan→Implement→Test→Review→Verify)が Design→Iterate の具体化。capability matrix = `/spec`、constraint のプログラム強制 = hook。

## 25.3 主要フレームワーク

### LangGraph（明示的フロー制御 — リサーチエージェントの既定)
**これは何か** — エージェント実行を**有向グラフ**としてモデル化。node=計算ステップ(状態を受けて状態更新を返すPython関数)、edge=遷移(無条件 or 状態依存のconditional)。`TypedDict`/Pydantic の State が node 間を流れる契約。**Checkpointing**(全node実行後に状態を永続化 → pause/resume・human-in-the-loop・time travel デバッグ)と subgraph(合成可能)。
**いつ使う / なぜ要る** — エージェントフローを明示的に制御・テスト・デバッグしたいとき。multi-step挙動を推論しやすい。**リサーチエージェントの第一選択**(Ch16 の Agentic RAG conditional loop、Ch19 の planning DAG がそのまま node/edge になる)。
**最小実装（research agent の中核; Listing 25.3-25.4 簡約）**
```python
class ResearchState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]   # reducer で蓄積
    research_topic: str
    iteration: int
    status: str                                            # researching|drafting|done|error

def research_node(state):                                  # LLM が次の検索 or 完了を決める
    llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)
    response = llm.invoke(state["messages"])
    return {"messages": [response], "iteration": state["iteration"] + 1}

def should_continue(state):                                # conditional edge: ツール呼び出し→実行 / なし→統合
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls: return "tools"
    if state["iteration"] >= 10: return "error"            # 暴走ガード
    return "synthesize"

builder.add_conditional_edges("research", should_continue,
    {"tools": "tools", "synthesize": "synthesize", "error": "error"})
builder.add_edge("tools", "research")                      # ツール実行後ループバック
with SqliteSaver.from_conn_string(":memory:") as cp:       # checkpoint で会話メモリ
    graph = builder.compile(checkpointer=cp)
```
**リサーチエージェントでの使いどころ** — まさにこれが土台。`research → (tools → research)* → synthesize` のループ。checkpoint で長時間調査を中断・再開、human_review node で「このソース採用していい?」と人間に確認(§25.9 の production 版は PostgresSaver + FastAPI + retry)。
**落とし穴** — ①conditional edge の戻り値とdict keyが一致しないと黙って分岐ミス ②iteration上限を入れ忘れると無限ループ ③State の reducer(`add_messages`)を付け忘れるとメッセージが上書きされ履歴消失。
**PDF参照** — §25.3.1, p.461-464

### CrewAI（役割ベース — チーム設計に最も近い)
**これは何か** — 組織管理に着想した role-based パラダイム。Agent を `role`/`goal`/`backstory`/`tools` で定義(LLMの「人間組織の理解」を活用)。Task(`description`/`expected_output`/担当agent)、Crew(agent+task の集合と `process`)、Process(`sequential`=順次 / `hierarchical`=manager agent が委譲)。
**いつ使う / なぜ要る** — 最小のboilerplateで役割分担チームを組みたいとき。Ch24 の Research Team(Researcher/Writer/...)を宣言的に書ける。
**最小実装（Listing 25.6 簡約）**
```python
researcher = Agent(role="Senior Research Analyst",
    goal="最先端の発展を発掘し正確な要約を提供",
    backstory="15年の技術リサーチ経験。難解な情報を実用的洞察に変える",
    tools=[search_tool, web_tool], allow_delegation=False)
research_task = Task(description="{topic} を包括調査...",
    expected_output="要約(200語)+主要発見(5-7点)+詳細分析+出典", agent=researcher)
crew = Crew(agents=[researcher, writer], tasks=[research_task, writing_task],
    process=Process.sequential)                            # hierarchical なら manager 自動生成
result = crew.kickoff(inputs={"topic": "Reinforcement Learning for LLMs"})
```
**リサーチエージェントでの使いどころ** — Ch24 で「まず2-3役の centralized」と言った、その実装が CrewAI の sequential process。`hierarchical` にすると manager agent が役割と能力を見て自動委譲(Ch24 の supervisor)。
**落とし穴** — ①役割の backstory に頼りすぎると挙動が読めない(persona 演技で精度劣化、Ch24 §24.5)②sequential は依存が直線のときだけ、複雑な依存は LangGraph の DAG に。
**PDF参照** — §25.3.3, p.466-467

**残り4フレームワーク(要点):**

| FW | パラダイム | 核 | 向き |
|---|---|---|---|
| **AutoGen** (MS) | conversable agents | 構造化メッセージで会話する複数agent、`GroupChat`+`GroupChatManager` が発話順を制御(round-robin/LLM選択)。**code execution agent** が際立つ(要 Docker 隔離) | multi-agent協働+コード実行 |
| **OpenAI Agents SDK** (旧Swarm) | handoffs | 軽量。`handoff` で別agentに制御+context を渡す。`InputGuardrail` で安全チェック、tripwire で停止 | swarm/triage routing |
| **DSPy** | declarative self-improving | promptを手で書かず、Signature(入出力契約)から optimizer(MIPRO)が最適prompt+few-shotを**コンパイル**。モデル差し替えに強い | 明確なeval指標+50+例があるとき |
| **Semantic Kernel** (MS) | plugin architecture | 既存業務ロジックを `@kernel_function` で AI呼び出し可能に。OpenAPI plugin 自動生成。.NET/Azure統合 | エンタープライズ.NET環境 |

> **DSPy の自己改善が刺さる:** Signature を「ソースの信頼性を評価する」と書き、開発セット(信頼できる/できないソースのラベル付き50例)を与えると、optimizer が prompt を自動最適化。あなたの「採用実績で情報源を進化させる」構想(ai-tech-researcher)の prompt 側を機械化できる。ただし**主観的な創作タスクには不向き**(正解が定義できない)。

### OpenAPI = ゼロコード ツール定義層
既存REST APIの OpenAPI spec(JSON/YAML)を parse → 各operationを function-calling schema に自動変換(`operationId`→tool名, `summary`→description)。**spec がそのままツール定義**。Google ADK / Semantic Kernel / LangChain `OpenAPIToolkit` が対応。「APIドキュメントがある組織は追加コードゼロでAPIをagent化できる」(§25.4.3, p.474)。

## 25.4 テスト（非交渉)

```
        E2E Tests          ← 少数・遅い・高信頼
     Integration Tests     ← 中程度・分単位
    Component Tests        ← 多数・秒単位
   Unit Tests              ← 多数・高速・隔離
```
**多粒度でテスト**(個別ツール / エージェントループ全体 / E2Eユーザシナリオ)。5種:

- **Unit(ツール単体)**: happy path + error case + edge case。`test_empty_query_raises`, `test_api_failure_returns_error`, `test_rate_limit_triggers_retry`(`call_count == 2`)。
- **Integration(ループ全体)**: `MockToolSet` で `test_completes_research_task`(status=="done")・`test_uses_search_before_writing`(search_idx < write_idx)・`test_handles_tool_failure_gracefully`。
- **Regression(golden trajectory)**: 既知の良い挙動を記録し回帰検出。tool列の一致(`DeepDiff`)・**semantic similarity > 0.85**(embedding cosine、出力が意味的に近いか)・**cost regression < 1.2×**(token が基準の1.2倍を超えない)。
- **Behavioral(制約遵守)**: `test_refuses_harmful_requests`・`test_respects_max_tool_calls`(<= 5)・`test_stays_within_allowed_domains`。
- **Cost/Latency**: タスク別に `(max_cost, max_latency)` を parametrize して上限検証。

> リサーチエージェントは「search してから write する」順序(integration)・「許可ドメイン外を読まない」(behavioral)・「token が膨張しない」(regression)が要のテスト。dotfiles の verification-before-completion + golden test の考え方そのもの。

## 25.5 観測とデバッグ

> **観測可能性の3本柱:** ①**Traces**(全LLM呼び出し・ツール実行・状態遷移の完全な実行記録)②**Metrics**(cost/latency/成功率/ツール使用の集約統計)③**Logs**(デバッグと監査証跡の構造化イベント)。

ツール: LangSmith / Arize Phoenix(幻覚検出・関連性スコア)/ Braintrust / W&B Weave / **OpenTelemetry**(標準計装、span 属性に `llm.model`/`prompt_tokens`/`tool.success` を載せる)。

### Failure Categorization（失敗の分類学 — ad hoc デバッグを止める)
**これは何か** — 構造化分類なしでは症状を治して根因を見逃す。6つの失敗型を症状・自動検出・対処で分類:

| 失敗型 | 症状 | 検出 | 対処 |
|---|---|---|---|
| **Tool Error** | ツール例外・空結果 | エラー率監視 | retry・fallback ツール |
| **Reasoning Error** | 誤ツール選択・誤引数 | trajectory分析 | prompt改善・few-shot |
| **Hallucination** | 事実捏造・ツール結果の捏造 | fact-check・grounding | RAG・引用必須化 |
| **Infinite Loop** | 同じツール反復・進展なし | loop検出・max iter | hard limit・loop破壊prompt |
| **Context Overflow** | 履歴切り詰め・context喪失 | token計数 | 要約・context管理 |
| **Refusal** | 正当なタスクを拒否 | 出力分類 | prompt調整・guardrail調整 |

**いつ使う / なぜ要る** — 本番失敗を体系的に潰すとき。1つのユーザ可視失敗はしばしば複数型のcascade(tool error → 復旧しようとして reasoning error → 無限ループ)。
**リサーチエージェントでの使いどころ** — 外部コンテンツを飲む以上 Hallucination(出典捏造)と Tool Error(取得失敗)が頻出。**replay**(LangSmith で run ID から失敗trajectoryを再生し、prompt/model を変えて再実行)でデバッグ。dotfiles の AgentRx FM-011~015 / error_analysis_integration と同じ分類アプローチ。
**落とし穴** — 症状(無限ループ)だけ見て対処すると根因(その前の reasoning error)を見逃す。cascade を遡る。
**PDF参照** — §25.6.2, Table 25.1, p.479-480

## 25.6 本番デプロイ

- **Async実行**: 長時間agentはasyncで(API接続をブロックしない)。Celery(分散タスクキュー)で retry・worker scaling・結果永続化。`API Gateway → Task Queue → Worker N → State Store` 構成。
- **Multi-Tenant隔離**: namespace隔離(テナント毎の状態/メモリ/ツール設定)・per-tenant rate limit・resource quota・tenant ID付き監査ログ。
- **Cost最適化**: **model routing**(分類/抽出は小型 `gpt-4o-mini`、推論/コード生成は `gpt-4o`、複雑分析は `o1`)・**prompt caching**(反復system promptで最大90%削減)・result caching・batching・**early termination**(十分な情報が揃ったらループ早期終了)。`50-90%` コスト削減を品質を犠牲にせず実現。
- **Auto-scaling**: **queue-depth scaling**(CPU使用率でなくキュー深さでスケール)・predictive scaling・spot instance + checkpoint・graceful shutdown(現タスク完了後に縮退し状態破損を防ぐ)。

> `CostOptimizedRouter`(task_type → model マップ + complexity>0.8 で昇格)は dotfiles の **model-routing.md**(Fable=指揮/Opus=推論/Sonnet=実装)と同型。リサーチエージェントなら「ソース分類=mini、要約統合=4o、矛盾解決の推論=o1」。

## 25.7 フレームワーク選択（§25.8 の決定表)

| 要件 | 選ぶ |
|---|---|
| エージェントフローの明示制御 | **LangGraph** |
| コード実行を伴うmulti-agent | **AutoGen** |
| 最小boilerplateの役割ベースagent | **CrewAI** |
| OpenAIエコシステム上 | **Agents SDK** |
| prompt自動最適化 | **DSPy** |
| エンタープライズ.NET/Azure | **Semantic Kernel** |

> **あなたへの推奨: LangGraph 単独で始める。** 明示的グラフ・checkpoint・human-in-the-loop が個人リサーチエージェントの「中断/再開」「ソース採否の確認」に直結する。役割分担が要るほど育ったら CrewAI を node の中に embed、prompt最適化を機械化したくなったら DSPy を足す。**最初から全部は YAGNI。**

## 25.8 Production Checklist（§25.9）

本番投入前に検証: ①全ツールに retry+エラー処理 ②最大iteration上限を強制 ③traceに機密データを残さない ④per-tenant rate limit ⑤長時間タスクで checkpoint 有効 ⑥behavioral test 通過(有害出力なし)⑦cost/latency上限を検証 ⑧rollback手順を文書化+テスト済 ⑨on-call runbook が主要failure modeを網羅。

---

## この章のまとめ

- **フレームワーク選択は効く**: LangGraph=制御可能ワークフロー / AutoGen=multi-agent+コード実行 / CrewAI=役割ベース簡潔 / DSPy=prompt自動最適化。**リサーチエージェントは LangGraph 単独から。**
- **テストは非交渉**: 非決定的だからこそ unit/integration/behavioral/regression を多粒度で。golden trajectory(tool列一致 + semantic類似 > 0.85 + cost回帰 < 1.2×)。
- **観測がiterationを可能にする**: 3本柱(traces/metrics/logs)。**6型の失敗分類学**で根因を遡る(cascade に注意)。早期投資。
- **async がデフォルト**: 長時間プロセスは queue + checkpoint + graceful failure。
- **cost管理が肝**: model routing + caching + early termination で 50-90% 削減(品質維持)。dotfiles の model-routing と同型。
- ライフサイクルは反復的: デプロイは一度きりでない。継続監視・failure分析・改善。

**次章 → Ch26 Agentic UI（対話層）。** 本番システムを「人間が信頼して使える」インタフェースに繋ぐ層に進む。
