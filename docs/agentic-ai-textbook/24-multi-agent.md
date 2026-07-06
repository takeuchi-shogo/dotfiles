# 第24章 Multi-Agent Systems（協調層 — 複数エージェントを1システムとして設計する）

> **一文サマリ:** 単一の generalist より、狭い小問に特化した専門エージェントのチームの方が、複雑な多面的タスクで上回る — 人間の専門家チームが1人の万能選手に勝つように。本章は複数エージェントのトポロジー・協調・役割設計・デバッグ。リサーチエージェントの「収集/選別/要約」分業の本命。
> **PDF参照:** §24, p.439-458

## 24.1 なぜ複数エージェントか

モノリシックなエージェントから **agent society** への移行を駆動する4つの動機: ①**Specialization**(小問ごとに別の能力・プロンプト戦略・基盤モデルが効く。1エージェントに全部を強いるのは非効率かつしばしば不可能)②**Parallelism**(独立subtaskを同時実行、文献調査+データ解析+執筆を並列で wall-clock 短縮)③**Robustness**(単一エージェントは SPOF。2つ目が検証・批評・独立再導出。adversarial agentが信頼前に弱点を探る)④**Emergent Capabilities**(議論・交渉・反復精緻化で、どの個体も持たない解に到達)。問いは「複数を使うか」でなく「**どう組織化するか**」。

> dotfiles の "Scaffolding > Model(協調プロトコル選択が品質差異の44%、モデル選択は~14%)" がまさにこれ。トポロジーと協調の設計がモデル選択より効く。

## 24.2 マルチエージェント・アーキテクチャ

トポロジー(エージェントの繋がり方と権限の流れ)が**最も影響の大きい設計判断**。4つの正準パターン。

### Centralized（Supervisor / Manager）— まずこれ
**これは何か** — 1つの orchestrator(supervisor/manager/planner)がグローバル状態を持ち、タスクを分解し、subtaskを worker に委譲し、結果を集約する。トポロジーは **hub-and-spoke**(全通信が中央を通る)。managerの責務: task routing(どのworkerが適任か)/ context管理(各workerに関連部分集合を渡す)/ result aggregation(出力を統合)/ error handling(失敗検出と再ルーティング)。
**いつ使う / なぜ要る** — **マルチエージェントの出発点**。制御フローが単純・説明責任が明確・デバッグ容易(全判断が1箇所)。
**最小実装（LangGraph supervisor、Listing 簡約）**
```python
def supervisor_node(state):                          # 中央: 次にどのエージェントを呼ぶか決める
    response = llm.invoke([{"role":"system","content":SUPERVISOR_PROMPT},
                           {"role":"user","content":
                            f"Task:{state['task']} Plan:{state.get('plan','')} "
                            "次にどのエージェント? planner/coder/tester/reviewer/FINISH"}])
    return {**state, "next_agent": response.content.strip()}

def route(state):                                    # FINISH なら終了、それ以外は該当エージェントへ
    return state["next_agent"] if state["next_agent"] != "FINISH" else END

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", route)
for agent in ["planner","coder","tester","reviewer"]:
    builder.add_edge(agent, "supervisor")            # worker は常に supervisor に戻る
```
**リサーチエージェントでの使いどころ** — manager が「収集役」「選別役」「要約役」を順に呼ぶ。dotfiles の improve/debate/absorb の **hub-and-spoke conductor パターン**(複数モデルを spoke に並列起動 → メイン=conductor が統合)がこれ。
**落とし穴** — ①**SPOF**(managerが幻覚・混乱すると全体崩壊)②高負荷でmanagerがボトルネック ③managerのcontext窓にグローバル状態が乗るのでスケール限界。
**PDF参照** — §24.2.1, p.440-441

**他の3トポロジー:**

| トポロジー | 仕組み | Pros / Cons |
|---|---|---|
| **Decentralized (P2P/mesh)** | 中央なし、任意のエージェントが相互通信、局所相互作用から協調が創発(negotiation/stigmergy/gossip/local consensus) | 個体障害に強い・自然にスケール / デバッグ困難・状態不整合・$O(n^2)$ overhead |
| **Hierarchical (tree)** | centralized を木に一般化。top orchestrator → ドメイン sub-manager → worker。委譲は下へ、結果は上へ、escalation path あり | スケールしつつ説明責任維持・ドメイン隔離で各層の認知負荷減。**本番で最も使われる** |
| **Swarm (handoffs)** | 多数の疎結合エージェントが単純な局所ルールで動く。Routines(手順)+ Handoffs(制御+context を別エージェントに渡す)。グローバル状態なし | 軽量・orchestration overhead なし / customer service triage 等の handoff 連鎖向き |

### 選び方（24.10 の結論）
| 状況 | アーキ |
|---|---|
| 独立subtask | 並列(division of labor / ensemble) |
| 明確な逐次依存 | pipeline |
| 耐障害性が要る | centralized を避け、hierarchical/decentralized |
| デバッグ性が要る | centralized / pipeline(全判断が追跡可能) |
| **<5エージェント** | **centralized が最単純** |
| >20エージェント | hierarchical / swarm |

> **実務の既定: hierarchical**(top supervisor → ドメイン sub-supervisor → 小チーム)。だが**まず centralized supervisor で始め、限界を測ってから**複雑化する(KISS)。

## 24.3 協調メカニズム

トポロジーと同じくらい「どう情報共有・分担・衝突解決するか」が重要。6つ。

### Blackboard（共有状態）と Task DAG（分解）
**これは何か** — **Blackboard**: 全エージェントが読み書きする共有データ構造(辞書/DB/文書)。conflict は confidence で解決(高い方が勝つ)、購読で変更通知。**Task DAG**: managerが高レベルタスクを依存付きDAGに分解し、各nodeをworkerに割り当て、依存解決済みのものを並列実行(HTN planning の多エージェント版)。
**いつ使う / なぜ要る** — Blackboard=解の道筋が事前に不明で各エージェントが異なる段階で貢献するとき(stigmergy 的)。DAG=タスクが依存付きsubtaskに明確に分解できるとき。
**最小実装（Task DAG）**
```python
class TaskDAG:
    def ready_tasks(self):                           # 依存が全て done のタスク
        return [t for t in self.tasks.values() if t.status == "pending"
                and all(self.tasks[d].status == "done" for d in t.dependencies)]
    async def execute(self, agent_pool):
        while any(t.status != "done" for t in self.tasks.values()):
            ready = self.ready_tasks()
            if not ready: await asyncio.sleep(0.1); continue
            await asyncio.gather(*[self._run(t, agent_pool[t.assigned_to]) for t in ready])
```
**リサーチエージェントでの使いどころ** — 調査命題を Task DAG に分解(「検索」→「読む」→「比較表」→「執筆」、Ch19 の planning DAG と同じ)。収集役が blackboard に発見を投稿し、要約役が読んで統合する stigmergy 型も。
**落とし穴** — ①blackboard の並行書き込みは lock + conflict解決(confidence)②DAG に循環があると停止しない ③blackboard が肥大(古いエントリのGC)。
**PDF参照** — §24.3.1, §24.3.3, p.444-446

**残り4つ(軽め):** Message passing(構造化/自然言語/hybrid、direct/broadcast/pub-sub)/ Voting・Consensus(majority / weighted $o^*=\arg\max_o\sum w_i\mathbf{1}[o_i=o]$ / debate / Delphi)/ Market-based(Contract Net の入札、API コスト最小化に有効)/ **Stigmergy**(明示通信せず共有環境を変更して間接協調 — 共有文書・コードリポ・タスクキュー。アリのフェロモン)。

## 24.4 通信プロトコル

メッセージは構造化(信頼できるparse/routing)。**Performative types**(FIPA-ACL由来): `inform`(共有)/ `request`(行動依頼)/ `propose`(提案)/ `accept`/`reject`/ `query`(質問)/ `confirm`(完了確認)/ `failure`(エラー報告)。

> **Context Sharing の経験則:** full history(<10ターン)/ summary(中程度)/ **retrieval-augmented excerpt(長時間agent session)**。常に直近 $k$ メッセージは逐語で残す。Ch18・Ch23 と同じ — 各エージェントに必要な分だけ渡す。

## 24.5 役割設計と専門化

| 役割 | 主能力 | 典型ツール |
|---|---|---|
| Researcher | 情報収集・統合 | Web検索, RAG, DB |
| Planner | タスク分解・スケジュール | なし(推論のみ) |
| Coder | コード生成・デバッグ | code interpreter, linter |
| Reviewer | 品質評価・批評 | なし(推論のみ) |
| Critic | adversarial 評価 | なし(推論のみ) |
| Writer | 散文生成・編集 | grammar checker |
| Orchestrator | 協調・委譲 | 全エージェントI/F |

**Role-based**(事前定義ラベルで割当、単純・予測可能)vs **Capability-based**(タスク要件への動的評価で割当、柔軟だがregistry要)。長時間系は dynamic reassignment(負荷・実績・要件変化・障害補填)。

### Persona Design for Diversity of Thought（思考の多様性）
**これは何か** — 同一の "assistant" を5体でなく、**異なるpersona**を与える: optimist(機会を強調)/ skeptic(前提を疑う)/ pragmatist(実装に集中)/ visionary(長期)/ devil's advocate(逆の立場)。Six Thinking Hats 由来。groupthink を減らし頑健な集団推論を生む。
**いつ使う / なぜ要る** — 設計判断・評価・批評で多角的視点が要るとき。同質なエージェントは同じ誤りを共有する。
**リサーチエージェントでの使いどころ** — ソース評価で「楽観派(価値を見る)」と「懐疑派(信頼性を疑う)」を当てて統合。dotfiles の **複数モデル(Codex/Gemini)を spoke に並列起動して conductor が統合**するのがこれ — 単一モデルの萎縮/Sycophancy バイアスを多様性で相殺。
**落とし穴** — persona を演じさせるとタスク精度が落ちる場合がある(評価/批評に限定し、実装には素のエージェントを)。
**PDF参照** — §24.5.4, p.449

> **Role Conflict は明示解決:** 責務が重なると衝突する。priority rule で「このタスク型はこの役割優先」を定義、または衝突調停専用の meta-agent。**役割衝突を暗黙に残すと矛盾出力・無限ループになる。**

## 24.6 マルチエージェント・パターン

Ch19 の単一エージェントパターンを補完する協働パターン:

| パターン | 仕組み | 向き |
|---|---|---|
| **Debate** | 複数エージェントが異なる立場で論じ、judge が裁定。事実精度↑・幻覚↓ | 検証・真偽判定 |
| **Reflection** | generator が出力、critic が批評、generator が改訂(generate-critique-revise) | 品質改善(Ch19 Evaluator-Optimizer の2エージェント版) |
| **Division of Labor** | 独立subtaskを並列、synthesis agent が集約 | embarrassingly parallel |
| **Pipeline** | 逐次処理連鎖(research→outline→draft→edit→format) | 明確な逐次依存 |
| **Ensemble** | 同問題を独立に複数解き、選択(best-of-N)or 集約 $o^*=\arg\max\,\text{score}(o)$ | 信頼性 > 計算コスト |
| **Teacher-Student** | 有能なteacherが劣るstudentを誘導(推論時蒸留、studentのFTにも) | 知識蒸留 |
| **Red Team** | adversarial agent が他の出力の欠陥・安全違反を最大限批判的に探す | 安全クリティカル |

> リサーチエージェントに効くのは **Debate**(矛盾するソースの真偽)+ **Reflection**(要約の品質ループ)+ **Red Team**(収集結果の捏造・バイアス検出)。dotfiles の Codex Review Gate / security-reviewer の Blind-first + adversarial framing がこれ。

## 24.7 マルチエージェントのRL学習（軽め）

マルチエージェントRLは**non-stationary**(各エージェントの環境に他の学習エージェントが含まれ、Markov仮定が崩れる)。形式は **Markov Game** $\mathcal{G}=\langle\mathcal{N},\mathcal{S},\{\mathcal{A}^i\},\mathcal{T},\{R^i\},\gamma\rangle$。手法: **Independent Learning**(各自が他を環境の一部扱い、単純だが non-stationarity で不安定)/ **CTDE**(Centralized Training, Decentralized Execution — 学習時は中央 critic が全結合状態を見、実行時は各自局所観測で行動。協調MARLの現行best practice)/ communication learning / self-play(競争で自動curriculum)/ PBT(多様な集団、劣者を優者の変異で置換)/ social welfare vs Nash(協調=全報酬和最大化、競争=Nash均衡、実世界は mixed-motive)。

> リサーチエージェント v1 はRL不要(プロンプト協調で十分)。学習させるなら Ch12 へ。

## 24.8 課題と解法

### When NOT to Communicate（協調オーバーヘッド）
全エージェント間メッセージが token = 時間 = 金を食う。**通信しない条件:** 情報が既に blackboard にある / 受信側が現タスクに不要 / 既送信の重複 / 単一エージェントで足りるほど単純。**ルール: 情報の期待価値がメッセージのコストを超えるときだけ通信**($\Delta v > c\cdot\text{cost\_per\_token}$)。

**他の課題:** Redundancy(重複検出/result caching/task locking)/ **Attribution**(counterfactual credit $\text{credit}^i=J(\pi)-J(\pi^i_{default})$ で各エージェントの貢献を見積もる、RL報酬割当・デバッグ・信頼較正に)/ Scalability($O(n^2)$ → hierarchical/pub-sub/sparse graph/async)/ **Emergent Behavior & Safety**。

> **マルチエージェントの安全懸念(最重要):** ①**Prompt injection cascade**(1エージェントへの悪意入力がシステム全体に伝播)②reward hacking ③collusion(競争設定で暗黙の結託)④amplification(1エージェントの誤り/バイアスを下流が増幅)。**常に safety monitor agent を置き、全エージェント間通信を観測して不安全挙動を検出したら停止**。リサーチエージェントが外部コンテンツを飲む以上、cascade は現実的リスク。

## 24.9 実例: Research Team（あなたの題材）

学術協働を模したリサーチチーム agent society:
- **Literature Reviewer**: 既存研究を検索・統合
- **Hypothesis Generator**: 新しい研究方向を提案
- **Experimentalist**: 実験を設計・実行(コード実行経由)
- **Statistician**: 結果を解析し有意性を評価
- **Writer**: 発見を一貫したレポートに統合

これがあなたの自己進化型リサーチエージェントの multi-agent 形。ただし**個人用なら全役割を立てず、まず収集役/要約役の2-3体で centralized から**(Software Dev Team の Architect→Coder→Tester→Reviewer ループと同じ構造を、Researcher→Summarizer→Critic に置換)。他の実例: Software Dev Team / Customer Service(Router→専門家→Escalation)/ Creative Team(Brainstormer→Drafter→Editor→Critic)。

## この章のまとめ

- **トポロジーが最重要判断**: centralized(SPOF だが単純、**出発点**)/ decentralized(レジリエントだがデバッグ難)/ hierarchical(**本番既定**)/ swarm(handoff連鎖)。**<5体は centralized、まず単純から。**
- 協調は blackboard / DAG分解 / voting / market / **stigmergy**(共有環境経由)。**通信は期待価値 > コストのときだけ**。
- 役割を専門化し、**persona 多様性**で groupthink を防ぐ(dotfiles のマルチモデル spoke = これ)。役割衝突は明示解決。
- パターン: Debate(真偽)/ Reflection(品質)/ Red Team(安全) がリサーチに効く。
- RLは non-stationary、CTDE が現行best(v1は不要)。
- **安全はマルチエージェントで第一級**: prompt injection cascade / amplification を safety monitor で。
- 例題: Research Team(Reviewer/Hypothesis/Experimentalist/Statistician/Writer)だが、まず2-3役の centralized から。

**次章 → Ch25 Frameworks（実装層）。** ここまでの概念を実装するツールキット(LangGraph/CrewAI/AutoGen 等)の選び方に進む。
