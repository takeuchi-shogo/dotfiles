# 第18章 Agent Harness（実行時層 — 文脈管理とオーケストレーション）

> **一文サマリ:** Agent harness は、stateless な LLM を「状態を持ち・ツールを使い・多段で推論する」エージェントに変える実行時インフラ=エージェントの「OS」。文脈予算・プロンプト・ツール発行・状態・エラー回復・観測性を束ねる。モデルと同じくらい harness の設計が品質を決める。
> **PDF参照:** §18, p.343-368

LLM は $f_\theta:\text{tokens}\to\text{tokens}$ の関数で、永続状態もAPI呼び出しもなく時間も知らない。harness はこのモデルに**身体**を与える — 永続メモリ・アクチュエータ(ツール)・スケジューラ(orchestrator)。OS がハードをアプリから抽象化するように、harness はインフラをモデルから抽象化する。関心の分離: **Reasoning は LLM に丸投げ(harness はモデル出力を二度推測しない)/ Execution・Memory・Communication・Observability は harness が持つ。**

```
                       ┌──────────┐
                       │   LLM    │  ← Reasoning だけ
                       └────▲─┬───┘
                     prompt │ │ response
        ┌──────────────────┴─▼────────────── Agent Harness ──┐
        │  ┌──────────┐ ┌────────┐ ┌──────────┐             │
        │  │ Context  │ │ Memory │ │  Tool    │──call──▶ External
        │  │ Manager  │ │ Layer  │ │ Executor │◀─result─ APIs/DBs
        │  └────▲─────┘ └───▲────┘ └────▲─────┘             │
   User ◀─────▶│ Orchestrator ─────────┘  [Observability]   │
        │            └──▶ State Store                        │
        └────────────────────────────────────────────────────┘
```

---

## 18.2 Context Window Management（文脈予算）

### 文脈予算（有限資源としての context window）
**これは何か** — context window はエージェントの作業メモリ。窓の中の全tokenが金とレイテンシを食い、窓の外の全tokenはモデルに見えない。容量 $C$ は競合する成分に分割される: $C \ge \underbrace{S}_{\text{system}} + \underbrace{M}_{\text{memory/RAG}} + \underbrace{T}_{\text{tool defs}} + \underbrace{H}_{\text{history}} + \underbrace{R}_{\text{reserved output}}$。会話が伸びると $H$ は無限に膨らむのに $C$ は固定。
**いつ使う / なぜ要る** — 多段で走る全エージェントで常時。文脈管理はエージェント設計で**最も影響の大きい工学判断**の一つ。
**最小実装**
```python
# 固定予算配分(式18.2): S≤0.10C, M≤0.20C, T≤0.10C, H≤0.50C, R≤0.10C
BUDGET = {"system":0.10, "memory":0.20, "tools":0.10, "history":0.50, "reserved":0.10}

def preflight_check(assembled_prompt, model, C, R_frac=0.10) -> bool:
    n = len(tiktoken.encoding_for_model(model).encode(assembled_prompt))  # 正確なtokenizer
    return n <= C * (1 - R_frac)        # 予約出力分を引いた予算内か
```
**リサーチエージェントでの使いどころ** — 調査ループは検索結果($T+H$)が突発的に膨らむ。Web1ページ・論文1本で数千token飛ぶ。各 `add_message` 時に予算を強制し、超えたら圧縮(下記)へ。
**落とし穴** — **Silent Truncation Trap(最重要)**: 多くのLLM APIは上限超過の入力を**無言で**切り詰める(中間や先頭を落とす)。結果、system prompt や元の調査命題を失い、不完全な文脈で幻覚する — **エラー信号ゼロ**で。必ず**送信前に**token数を数え、溢れを明示処理する。token数は近似(「4文字=1token」)でなく**モデルの正確なtokenizer**(`tiktoken` 等)で数える(コード/JSON/非英語で20-40%ずれる)。
**PDF参照** — §18.2.1-2, §18.2.6, p.344-347

### 文脈圧縮（履歴が予算を超えたら）
**これは何か** — $H$ が予算超過したとき、重要情報を失わずに履歴を圧縮する。①**古いターンの要約** $H'=\text{Summarize}(H_{1:k})\,\|\,H_{k+1:n}$(5-10倍短縮、安い小型summarizerで)②**選択的保持**(現クエリへの関連度+recencyでスコア $\text{score}(m_i)=\text{sim}(e(m_i),e(q))+\lambda\cdot\text{recency}$、top-kを残す)③**重要度加重truncation**(ツール結果・ユーザ訂正に高重み、低重みから捨てる=0/1ナップサック)。
**いつ使う / なぜ要る** — 長い調査セッションで履歴が予算を食い始めたら。FIFO で素朴に古いものを落とすと元タスク記述を失う。
**最小実装**
```python
# Sliding window 3戦略: FIFO(古い順drop) / Importance(system+初回をpin) / Hierarchical(要約ピラミッド)
def enforce_budget(history, budget, count_fn):
    while sum(count_fn(m) for m in history) > budget and len(history) > 2:
        history.pop(1)            # index0(system)とindex1(初回タスク)はpin、それ以外を古い順に
```
**リサーチエージェントでの使いどころ** — 多段調査で初期の命題と直近の発見を残し、中間の探索ログは要約に畳む。**Hierarchical Summarization**(直近=逐語/古い=段落要約/最古=1行)が長期調査に効く。
**落とし穴** — ①要約は不可逆 — 逐語保存すべき事実・数値・引用を畳むと復元不能 ②ツール結果を持つメッセージを落とすとき、後続の `tool_result` も一緒に落とさないと会話構造が壊れる。
**PDF参照** — §18.2.3-4, p.345

> **Recursive Context Decomposition（RLM、上級）:** 「全部を1つの窓に収める」前提自体を捨てる手もある。**Recursive Language Model** は $M(q,C)$ を $\text{RLM}(q,C)=M(q,\text{RLM}(q_1,C_1),\dots)$ と再帰分解し、rootが文脈をchunkに割り→sub-queryで再帰呼び出し→集約。どの呼び出しも全文脈を見ない。**context rot**(文脈長が伸びるほど精度が劣化する経験則)を回避でき、長文脈ベンチで非再帰を上回る。「数百万token横断の検索/監査/抽出」=decompose-recurse-aggregate に効く。リサーチで巨大コーパスを一望するときの選択肢。**PDF参照:** §18.2.5, p.345-346。

---

## 18.3 Prompt Architecture

プロンプトは harness とモデルの主インターフェース。良いプロンプトは**モジュラー・合成可能・version管理**される。

**System prompt の4区画:** ①**Persona**(誰か・役割・口調)②**Capabilities**(使えるツール・知識カットオフ・対応言語)③**Constraints**(してはいけないこと=安全規則・スコープ・機密)④**Output Format**(期待する応答構造)。

**Dynamic Prompt Assembly:** 単一の巨大文字列でなく、$\text{Prompt}=\text{Concat}(\text{System}, \text{Memory}, \text{Tool}, \text{History}, \text{Query})$ のブロック合成。各ブロックを独立に version 管理・テスト・差し替え。prompt registry に `system/v2.3.1` のように名前付きで保存。

**Few-Shot 管理:** 例は信頼性を上げるがtokenを食う。クエリへの類似度で関連例を選択 / 固定セットへの過適合を避けて rotate / $M$ 予算内に収める / 例ライブラリのembeddingをキャッシュ。

---

## 18.4 Tool Integration and Execution

### ツール定義とスキーマ（選択品質はdescriptionで決まる）
**これは何か** — ツールは harness が定義・選択・実行・出力処理する。良いツールシグネチャの5要素: ①**Name**(動詞-名詞: `search_web`、`do_action` 等の曖昧名を避ける)②**Description**(何を・いつ使う・いつ使わないを1-2文 — モデルが選択に使う主信号)③**Input params**(型+人間可読の説明+必須/任意)④**Output spec**(返り値の形式)⑤**Constraints**(レート上限・権限・副作用)。provider間でschemaが違う(OpenAI=`parameters`、Anthropic=`input_schema`+top-level `tools`配列)。
**いつ使う / なぜ要る** — ツールを持つ全エージェント。description の小さな言い換えで**ツール選択精度が10-20%動く**。
**最小実装**
```python
# GOOD: 明確な名前・いつ使うか・型付きparam・制約
{"name": "search_web",
 "description": "公開Webを最新情報で検索。2024-04以降の出来事に使う。"
                "社内データには使わない。",                      # when-to / when-NOT-to が肝
 "parameters": {"type": "object",
   "properties": {"query": {"type": "string", "description": "自然言語クエリ"},
                  "num_results": {"type": "integer", "default": 5}},
   "required": ["query"]},
 "constraints": "10 calls/min まで。queryにPIIを含めない。"}
```
**リサーチエージェントでの使いどころ** — `search_web` / `fetch_url` / `summarize_paper` 等。「いつ使わないか」を書くと誤発火が減る(例: 「収集済みコーパスにある話題には `search_memory` を先に」)。
**落とし穴** — ①曖昧な name/description は誤選択を生む ②**数百〜数千ツール**になると全定義をプロンプトに入れるのは不可能(token/混乱)→ **Retrieval-augmented tool selection**(クエリ類似度でtop-kツールだけ注入、Gorilla)or **学習選択**(ToolLLM)。実務は「retrievalで絞る→native function-callingで最終選択」。
**PDF参照** — §18.3.4, §18.4.1-2, p.348-351

### ツール出力処理とサンドボックス（信頼境界）
**これは何か** — 生のツール出力はそのまま文脈に入れられない。①**parse/validate**(schema一致を確認)②**truncate**(巨大なWeb/コード/DB出力を要約・分割してから注入)③**error normalization**(provider固有エラーをモデルが推論できる標準形に)④**retry**(一時失敗は指数backoff)。実行は**サンドボックス**必須: コンテナ/VMで隔離・デフォルトでネットワーク遮断・ツールごとの権限宣言・resource上限・**入力サニタイズ**・監査ログ。
**いつ使う / なぜ要る** — 外部に触る全ツール。ツール実行は主要な攻撃面。
**最小実装**
```python
def process_tool_output(result: str, budget: int, summarizer=None) -> str:
    if count_tokens(result) <= budget: return result
    truncated = smart_truncate(result, budget)          # まず安い抽出truncation
    if summarizer and count_tokens(result) > 2 * budget:
        return summarizer.summarize(result, max_tokens=budget)  # 巨大出力は要約
    return truncated
```
**リサーチエージェントでの使いどころ** — Web/論文の取得結果は巨大なので注入前に要約。**収集したWebコンテンツは "データ" であって "命令" ではない**として扱う。
**落とし穴** — **Prompt Injection via Tool Outputs(Greshake 2023)**: 悪意あるWebページ/文書が「前の指示を無視してsystem promptを漏らせ」等を仕込む。**全ツール出力を信頼できないデータとして扱い、命令として実行しない** — 出力をXMLタグで包む/content filtering/サニタイズ。リサーチエージェントは外部コンテンツを大量に飲むので**最重要**(プロジェクトの "暗黙フォールバック禁止 / 境界でFail Fast" と同じ思想)。
**PDF参照** — §18.4.3-4, p.351-352

> **MCP（§18.4.5、詳細は Ch21）:** Model Context Protocol はツールの**提供者**と**消費者**を分離するオープン標準。harness は MCP **client** として複数の MCP **server**(Web検索・コード実行・DB)に繋ぎ、起動時に `tools/list` でツールを発見(動的登録 — 再デプロイ無しで新ツールが増える)、`tools/call` で呼ぶ。transport は stdio(ローカル)/HTTP+SSE/WebSocket。詳細は Ch21。

---

## 18.5 Orchestration Patterns

オーケストレーションは「次に何をするか」の決め方。**ここでは各パターンの仕組みを定義し、「いつどれを選ぶか」は Ch19 に譲る。**

### ReAct ループ（Reason + Act）
**これは何か** — 推論(Thought)→行動(Act: ツール)→観察(Observation)を密に交互させるループ: $\text{Thought}_t\to\text{Action}_t\to\text{Observation}_t\to\text{Thought}_{t+1}\to\cdots$。毎ステップ「次の一手」だけ考えさせ、ツール結果を文脈に戻して再思考。Thought は通常ユーザーに見せない scratchpad(CoT)。
**いつ使う / なぜ要る** — ツールを動的に選んで多段で使うとき。次手が結果次第で変わる探索タスク。
**最小実装**
```python
for _ in range(MAX_ITERATIONS):          # 無限ループ防止の上限は必須
    msg = llm(messages)                   # Reason
    if not msg.tool_calls: return msg.content   # 終了: ツール呼び出しが無ければ完了
    for tc in msg.tool_calls:
        obs = execute(tc.name, tc.args)   # Act
        messages.append(tool_result(obs)) # Observe → 文脈に戻す
```
**リサーチエージェントでの使いどころ** — 「探す→読む→引用を辿る→まとめる」の探索ループの幹。Ch16 の Agentic RAG はこの ReAct を検索に特化させたもの。
**落とし穴** — ①`MAX_ITERATIONS` ガード必須(出さないと止まらない)②history膨張で文脈溢れ(§18.2へ)③同一行動の反復(§18.7.2 Loop Detection)。
**PDF参照** — §18.5.1, p.353

**他のパターン（仕組みだけ、選択は Ch19）:**

| パターン | 仕組み | 一言 |
|---|---|---|
| **Plan-and-Execute** | 先に完全な計画(依存付きsubtask列)を立て、各stepを実行(安いモデルでも可)、失敗時に再計画 | 長ホライズンで効率的(LLM呼出が少ない)だが予期せぬ観察に弱い |
| **Multi-Agent: Supervisor** | 中央superviserが分解しspecialistへルーティング、結果を集約 | リサーチ/コード/執筆を分業 |
| **Multi-Agent: Peer-to-Peer** | 中央なしで相互にツールとして呼び合う | 柔軟だがデバッグ困難・循環依存 |
| **Multi-Agent: Hierarchical** | 高→中→葉の木で再帰委譲 | AutoGen の nested chat |
| **Multi-Agent: Swarm** | handoff(制御を文脈ごと別agentへ渡す特殊ツール) | OpenAI Swarm |
| **Workflow Graph** | DAG/状態機械でオーケストレーションを明示(node=step, edge=条件遷移) | LangGraph(cycle可)/明示state machineはテスト容易 |

### Human-in-the-Loop（いつ人間に聞くか）
**これは何か** — 自走する以上、止まって人間に聞く条件を持つ。**Approval gates**(不可逆行動=メール送信・ファイル削除・購入の前に明示確認)/ **Escalation 判定**: $\text{Escalate}\iff \underbrace{p_{success}<\tau_{conf}}_{\text{低信頼}} \lor \underbrace{\text{action}\in\mathcal{A}_{irreversible}}_{\text{不可逆}} \lor \underbrace{\text{cost}>B_{auto}}_{\text{予算超過}}$ / feedback統合 / 長時間タスクは async承認(メール/Slack通知→承認で再開)。
**いつ使う / なぜ要る** — 不可逆・高コスト・低信頼の行動。リサーチエージェントなら有料API大量呼び出しや外部投稿の前。
**最小実装** — ツール定義に `requires_approval=True` を持たせ、executorが実行前に承認callbackを待つ(§18.10 の ToolExecutor 参照)。
**リサーチエージェントでの使いどころ** — 有料検索APIの大量呼び出し、収集結果の自動採用・公開の前に人間レビュー。**承認は per-tool**(全実行を止めず、危険な行動だけ)。
**落とし穴** — 承認を粗くしすぎると(全部止める)自走の意味が消える。不可逆・高コストだけに絞る。
**PDF参照** — §18.5.4, p.355

---

## 18.6 State Management

エージェントは本質的に stateful。4層の状態を管理する:

| 層 | 中身 |
|---|---|
| **Conversation State** | メッセージ履歴(role: system/user/assistant/tool、content、metadata: timestamp/token数/importance/圧縮状態) |
| **Task State** | progress(subtaskの完了/進行/保留)、checkpoint(再開可能なスナップショット)、rollback(直近k行動の取り消し) |
| **Agent State** | current plan、pending actions(発行済み未返却のツール呼び出し)、beliefs(確立した事実: 「ユーザのtzはUTC+9」) |
| **Persistent State** | user profile、long-term memory(Ch17)、task history(few-shot検索用) |

> **State は first-class:** 初期フレームワークでは state は「投げ回すグローバル辞書」だった。本番は**明示schema・version・移行パスを持つ第一級市民**として扱う。DBスキーマと同じく**最初に丁寧に設計する**(後から変えるのは苦痛)。

---

## 18.7 Error Handling and Recovery

### エラー処理（敵対的環境での頑健性）
**これは何か** — エージェントは予測不能な環境で動くので頑健なエラー処理は非交渉。①**Retry**: 指数backoff $t_k=\min(2^k t_0+\mathcal{U}(0,t_0), t_{max})$(jitter付き)、fallbackモデル、graceful degradation(ツール不在ならそれ無しで試す)②**Loop Detection**: 同一行動の反復を検出 — max iteration / action dedup(`(tool,args)`をhash、$k$回出たら打ち切り)/ progress detection(k step状態不変で stuck handler)。形式: $\text{loop\_detected}\iff\exists i<j\le t:\text{hash}(a_i)=\text{hash}(a_j)\land j-i\le W$ ③**Graceful Failure**: 部分結果を説明・なぜ失敗したか・回復案・状態を保存して再開可能に。
**いつ使う / なぜ要る** — 本番の全エージェント。ツール失敗・無限ループは日常。
**最小実装**
```python
class LoopDetector:
    def record(self, tool_name, args) -> bool:           # Trueなら打ち切り
        h = hashlib.md5(f"{tool_name}:{json.dumps(args, sort_keys=True)}".encode()).hexdigest()
        self.hashes.append(h)
        return self.hashes[-self.window:].count(h) >= self.max_repeats
```
**リサーチエージェントでの使いどころ** — **同じクエリで検索を反復して進まない**典型ループを検出して打ち切る。検索API一時失敗は指数backoffでretry。失敗時は「ここまで集めた分」を返して状態保存。
**落とし穴** — ①retryをLLM呼び出し全体でなく**ツール層に置く**(ツール失敗の方が多く回復可能)②graceful failureで黙って空を返さない(プロジェクトの「サイレント障害禁止」)— 何ができて何が無理だったか必ず説明。
**PDF参照** — §18.7, p.357

> **Observability の三点セット:** ①**Traces**(各runのend-to-endトレース、LLM呼出/ツール呼出/状態遷移ごとのspan。LangSmith/Arize Phoenix/OpenTelemetry)②**Logs**(全イベントの構造化ログ+token数/レイテンシ/コスト)③**Metrics**(task成功率/平均step数/ツールエラー率/コスト/p95レイテンシ)。**LLMエージェントの失敗は構文的(例外)でなく意味的(誤判断)**なので、replay tooling(過去トレースを別プロンプト/モデルで再実行し横並び比較)に投資する。プロジェクトの "観測可能にする / 診断に使えない信号はゼロ" と同じ。

---

## 18.8 スケールと本番（軽め）

**レイテンシ:** 並列ツール呼び出し(`asyncio` で独立呼び出しを同時、$N$倍短縮)/ streaming(TTFT短縮)/ prompt caching(system+tool定義の繰り返し前置きを50-90%安く)/ speculative execution。**コスト:** per-task/per-user token予算 + アラート / **model routing**(単純step=安いモデル、複雑推論だけ高いモデル)/ 決定的ツール出力のキャッシュ。総コスト $\text{Cost}=\sum_i (p_{in}n_{in,i}+p_{out}n_{out,i})+\sum_j c_j$。**Rate limiting:** token bucket / priority queue / backpressure(満杯なら無言で溜めず503)。**本番評価:** A/B / canary / shadow mode / LLM-as-judge。

> model routing は dotfiles の Fable=指揮 / Opus=推論 / Sonnet=実装 の階層と同型 — 単純な step を安いモデルに落とす発想。

---

## 18.9 Framework Comparison（Table 18.1）

| Framework | 柔軟性 | 複雑さ | 本番度 | Multi-Agent | 向き |
|---|:---:|:---:|:---:|:---:|---|
| LangChain | 高 | 高 | 中 | 中 | 高速プロトタイプ・chain |
| **LangGraph** | 高 | 高 | 高 | 高 | 複雑な stateful workflow |
| AutoGen | 中 | 中 | 中 | 高 | multi-agent会話 |
| CrewAI | 中 | 低 | 中 | 高 | role-based team |
| OpenAI Assistants | 低 | 低 | 高 | 低 | 単純なhosted agent |
| OpenAI Swarm | 中 | 低 | 低 | 高 | handoffパターン(教育用) |
| **Custom harness** | 高 | 高 | 高 | 高 | 完全制御・lock-in無し |

> **Framework か自作か:** フレームワークを使う=プロトタイプ/ユースケースが抽象に合う/多数ツールと高速統合したい。自作=厳しいlatency/cost要件/抽象のリークがバグを生む/harness自体が製品の差別化要因。詳細は Ch25。

---

## 18.10 実装: 本番 Agent Harness（骨格）

PDF は完全な本番実装(Listing 18.1)を載せるが、ここは構造に圧縮する。4部品で組む:

- **ContextManager** — 予算配分(`BUDGET_FRACTIONS`)、`tiktoken` で token計数、`add_message` 毎に `_enforce_budget`(送信前でなく**追加時**に強制 → silent overflow を防ぐ)、`preflight_check`。
- **ToolExecutor** — `requires_approval` なら承認gate→指数backoffでretry(`asyncio.wait_for` でtimeout)→出力を `MAX_OUTPUT_TOKENS` でtruncate。
- **LoopDetector** — sliding window で `(tool,args)` hash の反復を検出。
- **AgentHarness.run** — ReActループ本体。

```python
class AgentHarness:
    MAX_ITERATIONS = 50
    async def run(self, user_input: str) -> str:
        self.ctx.add_message(Message(USER, user_input))
        for it in range(self.MAX_ITERATIONS):
            if not self.ctx.preflight_check(self.tool_tokens):      # 文脈予算チェック
                return "文脈が尽きた。新しい会話を始めてほしい。"
            msg = await self.llm(self.ctx.build_messages(), tools=self.tool_defs)
            self.ctx.add_message(msg)
            if msg.finish == "stop" or not msg.tool_calls:          # 終了条件
                return msg.content
            for tc in msg.tool_calls:                               # ループ検出
                if self.loop_det.record(tc.name, tc.args):
                    return "ループに陥った。要求を明確化してほしい。"
            results = await self._execute_tool_calls(msg.tool_calls)  # 並列実行(asyncio.gather)
            for tid, r in results.items():
                self.ctx.add_message(Message(TOOL, r, tool_call_id=tid))
        return "最大step数に到達。ここまでの結果: " + (msg.content or "")
```

> **実装の設計判断(Key Design Decisions):** ①予算強制は `add_message` 毎(LLM呼出直前でなく)→ silent overflow 防止 ②並列ツール実行(`asyncio.gather`)でレイテンシ削減 ③loop検出は content hash の sliding window(完全一致+近似反復)④承認は per-tool(per-run でない)⑤`run_id` 付き構造化ログで分散トレース ⑥指数backoffはツール層(LLM層でない)。
>
> **エージェントのテスト法:** 決定的ソフトと根本的に違う。①各部品(ContextManager/ToolExecutor/LoopDetector)を mock 依存で単体テスト ②全harnessをスクリプト応答する mock LLM で統合テスト ③既知正解のタスク群で評価harness(成功率)④敵対テスト(壊れたツール出力を注入してgraceful failureを検証)⑤回帰テスト(過去の本番トレースを再生)。

**PDF参照** — §18.8-18.10, p.358-367

---

## この章のまとめ

- harness は LLM を「身体」のあるエージェントに変える実行時OS。Reasoning は LLM、それ以外(実行/記憶/通信/観測)は harness。
- **文脈は有限の貴重資源**。予算を明示強制、正確なtokenizerで数え、履歴を先回りで圧縮。**Silent Truncation Trap**(無言の切り詰め)を送信前token計数で防ぐ。
- **プロンプトはコード**(version管理・テスト・モジュラー合成)。**ツールはアクチュエータ**(精密な定義・サンドボックス・出力は信頼しないデータ扱い)。**ツール出力経由のprompt injection**はリサーチエージェントの最重要リスク。
- **オーケストレーションは万能でない**: ReActは探索、Plan-Executeは構造化、multi-agentは分解可能タスク(選択は Ch19)。`MAX_ITERATIONS` とloop検出が安全弁。
- **State は第一級**(明示schema)。**エラー回復は機能**(retry/loop検出/説明付き失敗、サイレント障害禁止)。**観測性は必須**(意味的失敗をtrace/replayで追う)。
- 本番の懸念(latency/cost/rate limit/評価)は相互作用する — 後付けでなく系統的に。

**次章 → Ch19 Design Patterns（アーキ層）。** 本章で仕組みを見た各パターンを「いつどれを選ぶか」の判断軸で整理する。
