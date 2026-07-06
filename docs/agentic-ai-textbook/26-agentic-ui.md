# 第26章 Agentic UI Frameworks（対話層 — 人間が信頼して使えるインタフェース）

> **一文サマリ:** チャットの吹き出しは**結果**を伝える。Agentic UI は**プロセス**(推論・呼んだツール・下した判断・人間の判断が要る点)を伝える。これが見えないと、ユーザはエージェントを信頼も訂正も学習もできない。本章は UI パラダイム・ストリーミング・承認ゲート・信頼UX。コードは TypeScript。
> **PDF参照:** §26, p.490-511

## 26.1 なぜ専用UIが要るか

20ステップの調査タスク(Web閲覧→コード実行→レポート統合)を走るエージェントに、ユーザは単純なテキスト応答では答えられない問いを持つ:
- **今エージェントは何をしている?**(長時間タスクで沈黙は不信を生む)
- **なぜこの判断をした?**(推論の透明性が早期のエラー検出を可能に)
- **どのツールをどの入力で使った?**(事実検証と挙動監査に必須)
- **どこで介入すべき?**(全マイクロ判断で人を煩わせずに判断点を surface)
- **これは取り消せる?**(メール送信・ファイル変更・コード実行など不可逆操作は明示確認とロールバック経路が要る)

> **Automation Bias のリスク(最重要):** 研究は一貫して、ユーザが自動システムを**過信**することを示す — 特に出力が自信ありげで不確実性シグナルがないとき。**Agentic UI は automation bias に能動的に抗わねばならない**: 不確実性を surface し、推論を見せ、判断を疑う/上書きするのを容易にする。これは dotfiles の「Claude=Sycophancy バイアス」への UI 側の対策。

5つの設計目標: ①Transparency(内部状態を可読に)②Control(常時監視なしの意味ある介入点)③Trust Calibration(能力と限界の正確なメンタルモデルを育てる)④Efficiency(認知負荷を最小化、正しい情報を正しいタイミングで)⑤Recoverability(ミスを安く検出・取り消し可能に)。

## 26.2 UI パラダイム

### パラダイム選択（タスク特性で選ぶ）
**これは何か** — 万能パラダイムはない。タスク持続時間・必要な人間関与・出力型・ユーザ熟練度で選ぶ。スペクトラムは「完全会話型チャット」から「最小介入の完全自律ダッシュボード」まで。
**いつ使う / なぜ要る** — UI 設計の最初の分岐。間違えると、並列プロセスを線形チャットに押し込めて実行グラフを誤表現する(チャットの構造的限界)。
**6パラダイム比較**

| パラダイム | 形 | 向き |
|---|---|---|
| **Chat** | 吹き出し+入力+履歴。streaming/inline tool indicator/typing status で拡張 | 低学習コスト・短文脈。**並列プロセスを直列化してしまう** |
| **Canvas/Artifact** | split-pane(左=会話、右=生成物をライブ編集) | co-creation(執筆/コード/データ分析)。Claude Artifacts 型 |
| **Workflow Viz** | 実行グラフを DAG/フローチャート、node の色で進捗 | 構造化プラン実行。LangGraph Studio 型 |
| **Dashboard** | 稼働状況・リソース・キュー・アラートの運用ビュー | 長時間/本番エージェント。**運用者**向け(エンドユーザでなく) |
| **Collaborative** | エージェントを共有ワークスペースの peer(presence/diff/提案) | Cursor/Notion AI 型 |
| **Autonomous + Checkpoints** | 大部分自律実行、事前定義 checkpoint でのみ承認を求める | computer-use / scheduled agent |

**リサーチエージェントでの使いどころ** — あなたの自己進化型リサーチエージェントは **Autonomous + Checkpoints** が中核。nightly に自律で走り(scheduled agent)、結果を非同期報告し、後続アクション(「この23記事を採用していい?」)を承認ゲートで surface。dotfiles の nightly codex batch + morning-briefing がまさにこの paradigm。会話で対話するときだけ Chat を重ねる。
**落とし穴** — ①チャット一択にすると並列ツール実行が見えない ②ダッシュボードはエンドユーザ向けでない(運用ビュー)③paradigm を混在させるのが本番の常(無理に1つに統一しない)。
**PDF参照** — §26.2, p.491-493

> **Checkpoint UI 実例:** 「受信箱を整理して」と頼まれたエージェントが500通を自律分類・アーカイブし、**一時停止して**サマリを提示: 「6ヶ月開いていないメーリングリストからのメール23通を発見。全部/一部/どれも購読解除しない、どれにする?」ユーザがリストを見て選択 → エージェント続行。**自律実行を人間の判断点で区切る**のが効率と制御の両立。

## 26.3 主要UIコンポーネント

パラダイムに関わらず再出するコンポーネント群:

| コンポーネント | 設計指針 |
|---|---|
| **Thought/Reasoning Display** | collapsible(「12秒思考」の要約+展開)。progressive disclosure(既定は結論のみ)。**推論(誤りを含みうる)と最終応答を視覚的に明確分離** |
| **Tool Use Viz** | 4要素を表示: tool名+アイコン / 入力引数(巨大JSON) / 出力 / レイテンシ。inline tool card・tool timeline・input/output diff・error highlighting(失敗は赤+リトライ) |
| **Progress Indicators** | step-level progress(番号付きチェックリスト、動的に増減)・ETA(「約2-5分」と不確実性込み)・subtask nesting・**Cancel ボタン**(優雅に停止しそこまでの成果を要約) |
| **Approval Gates** | 後述(§26.7)。最重要HITLコンポーネント |
| **Context Display** | memory panel(編集可)・active tools list・retrieved context(出典付き)・**token budget indicator**(新セッション開始の判断材料) |
| **Error/Recovery UI** | error card・retry control・alternative approaches(選択肢提示)・partial results(途中まで保持)・escalation path |
| **Confidence Indicators** | verbal hedging のハイライト・source quality score・「どのくらい自信ある?」ボタン・高stakesでの検証提案 |

> **dotfiles 接続:** token budget indicator = Context Constitution の context 管理。Context Display の retrieved context(出典付き)= RAG の citation。Cancel = LoopDetector の人間版。

## 26.4 ストリーミング（ベースライン)

### Token Streaming（SSE）
**これは何か** — LLM出力を完成を待たず生成ごとに逐次配信。「結果を待つ」を「エージェントが働くのを見る」に変える。2つの transport: **SSE**(Server-Sent Events、単方向HTTPストリーム、HTTP/1.1で動きブラウザが自動再接続、OpenAI/Anthropic/Google 全採用の主流)/ **WebSocket**(双方向、複雑だがストリーム中にクライアントから送信が要るとき=エージェント中断・生成中フィードバック)。
**いつ使う / なぜ要る** — エージェントUIの table-stakes。沈黙は不信を生む。
**最小実装（型付きイベントの SSE — TypeScript フロント）**
```typescript
type AgentEvent =
  | { type: 'status'; message: string }
  | { type: 'thinking'; content: string }
  | { type: 'token'; content: string }
  | { type: 'tool_call'; tool: string; input: object; tier: number }
  | { type: 'tool_result'; tool: string; output: string; duration_ms: number }
  | { type: 'approval_required'; approval_id: string; tool: string;
      tier: number; risk: string; action_summary: string; parameters: object }
  | { type: 'done'; total_tokens: number };

const es = new EventSource(`/chat/stream?session_id=${sid}&message=${encodeURIComponent(input)}`);
es.onmessage = (e) => {
  const event: AgentEvent = JSON.parse(e.data);
  if (event.type === 'token') setResponse(prev => prev + event.content);  // 逐次追記
  else if (event.type === 'done') { setIsStreaming(false); es.close(); }
  else setEvents(prev => [...prev, event]);                               // tool/approval は別レーン
};
```
**リサーチエージェントでの使いどころ** — 「検索中...」「3記事読了」をリアルタイムに。**discriminated union の event 型**(status/thinking/token/tool_call/approval)でフロントが各イベントを適切に描画。バックエンド(FastAPI)は `asyncio` generator が `data: {json}\n\n` を yield。
**落とし穴** — ①SSE は `Cache-Control: no-cache` + `X-Accel-Buffering: no`(プロキシのバッファリング無効化)を付けないと配信が固まる ②マルチエージェントで複数ストリームが同時生成 → **backpressure**(UIが描画追いつかない時、中間トークン破棄/バッチ更新/遅いストリーム一時停止)③token batching(50-100ms バッファ)で DOM 更新頻度を抑える。
**PDF参照** — §26.6, p.500-502

> **Generative UI(フロンティア、参考):** モデルのツール呼び出しが**テキストでなくUIコンポーネントを生成**する(天気ウィジェット・株価チャート・予約フォーム)。Vercel AI SDK RSC が最成熟。ただし**完全モデル駆動UIは不整合・アクセシビリティ欠陥・セキュリティ脆弱性のリスク** → 実務では「curated な事前ビルド済コンポーネントライブラリから選ばせる」のが安全。リサーチエージェントなら「表データ→ソート可能テーブル、時系列→ズーム可能チャート」程度に留める(YAGNI)。

## 26.5 Human-in-the-Loop 設計（承認ゲート — 本章の核)

### Tiered Approval（段階的承認 — alert fatigue を防ぐ)
**これは何か** — 承認ゲートは HITL 制御の主機構。だが**頻繁すぎると alert fatigue**(ユーザが中身を読まず反射的に承認 → 監視の意味が消える)。解は3層モデル:

| Tier | 対象 | UI挙動 |
|---|---|---|
| **Tier 1 (Auto-approve)** | 低リスク・可逆・routine(Web検索、ファイル読取、read-only API) | 中断せず続行、監査ログのみ |
| **Tier 2 (Notify)** | 中リスク(下書きメールをDraftsに保存) | 非ブロッキング通知 + 短い猶予窓(30秒)でキャンセル可 |
| **Tier 3 (Require approval)** | 高リスク・不可逆・高コスト(メール送信、購入、削除) | **ブロッキング承認ゲート** + 明示的に承認/拒否/修正 |

**いつ使う / なぜ要る** — フラットな承認方針(全部承認 or 全部素通り)は本番で破綻する。tier の閾値はユーザ設定可(「メール送信前は必ず確認」)or 挙動から学習(常に承認するなら次から auto)。
**判断軸(いつ中断するか):** Reversibility(不可逆は常に承認)/ Scope(外部システム・他者に影響するものは厳しく)/ Confidence(意図解釈の自信が低ければ続行でなく確認)/ Cost(高コスト操作)/ Novelty(その文脈で初めての操作)。
**最小実装（承認ゲート — TypeScript コンポーネント簡約）**
```typescript
function ApprovalGate({ event, onDecision }: {
  event: AgentEvent & { type: 'approval_required' };
  onDecision: (approved: boolean, params?: object) => void;
}) {
  const riskColor = { reversible: '#22c55e', 'hard-to-undo': '#f59e0b',
                      irreversible: '#ef4444' }[event.risk] ?? '#6b7280';
  return (
    <div style={{ border: `2px solid ${riskColor}`, padding: 16 }}>
      <div style={{ fontWeight: 700, color: riskColor }}>承認が必要: {event.tool}</div>
      <div>{event.action_summary}</div>                        {/* 平易な言葉での行動説明 */}
      <div>リスク: <span style={{ color: riskColor }}>{event.risk}</span></div>
      <button onClick={() => onDecision(true, event.parameters)}>承認</button>
      <button onClick={() => onDecision(false)}>拒否</button>
      {/* 「修正」は parameters エディタを開いてから承認(本番) */}
    </div>
  );
}
```
バックエンドは `asyncio.Event` でストリームを一時停止し、フロントの承認 POST(`/chat/approve`)を待つ。タイムアウト(5分)時は**続行でなくスキップ**(timeout behavior は「応答なし=安全側=停止」)。
**リサーチエージェントでの使いどころ** — 「ソースを採用してメモリに書き込む/PR を出す」は Tier 3(memory/repo を変える不可逆操作)、「Web検索・記事取得」は Tier 1。dotfiles の `git commit --no-verify` 禁止や settings.json deny ルールは、まさに Tier 3 を**プログラムで**強制した形(UI でなく hook で)。
**落とし穴** — ①Tier 3 を乱発すると alert fatigue で形骸化 ②risk indicator(緑=易/黄=難/赤=不可逆)を出さないとユーザが判断できない ③timeout を「続行」にすると無人時に不可逆操作が通る(必ず停止側)。
**PDF参照** — §26.7, p.494, 502

> **フィードバック機構(自己進化への接続):** 承認の先に、エージェントを改善するフィードバック: thumbs up/down(RLHF/選好学習へ)・inline correction(原文と訂正の delta が訓練信号)・preference selection(複数案からの選択)・**explicit instruction**(「次からXするなYを優先」= 挙動方針を更新)・rating with rationale。これがリサーチエージェントの「採用実績で情報源を進化させる」ループの UI 側入口(Ch17 の write policy / Ch12 へ)。

## 26.6 アクセシビリティと信頼

> **信頼は機能でなく創発特性:** 一貫して期待通りに振る舞い、自己を明快に説明し、失敗から優雅に復旧するシステムから創発する。

- **判断の説明**: chain-of-thought を見せる以上に — decision rationale(何を決めたかでなく**なぜ**: 考慮した要素・却下した代替・置いた仮定)・source attribution(主張をソースにリンク)・counterfactual(「XでなくYと言っていたらZした」で判断境界を示す)。
- **信頼度の表示**: verbal(「かなり自信がある」は数値確率より大半のユーザに解釈しやすい)・visual(緑/黄/赤)・**per-claim**(複数主張の応答は主張ごとの信頼度=inline footnote)。
- **Undo/Rollback**: action log with undo・snapshot rollback・**dry-run mode**(実行前にプランをシミュレートし予測される状態変化を見せ、承認/修正させる)・graceful degradation(取り消し不能時=メール送信済 はそれを明示し最善の代替=フォローアップ送信 を提示)。
- **Audit Trail**: immutable action log(timestamp+identity+全パラメータ)・exportable(JSON/CSV/PDF)・diff view・session replay。
- **期待管理**: capability disclosure・limitation acknowledgment(能力外は黙って失敗せず明言)・consistent persona。

> dry-run mode は dotfiles の Plan → 撤退条件(reversible-decisions.md)の UI 版。audit trail の session replay は Ch25 の LangSmith replay と同じ。

> **透明性で信頼を築く(ケーススタディ):** フライト予約で、低信頼UIは「予約しました。確認番号 AA1234」。高信頼UIは ①使った検索条件 ②検討した代替と選定理由 ③取った正確なアクション(API呼び出し)④確認詳細+予約へのリンク ⑤24時間有効な取消オプション ⑥できないことの注記(「変更は航空会社に直接」)を出す。**後者は画面を食うが、エージェントが正しく動いた確信と、検証・復旧に要る情報を与える。**

## この章のまとめ

- **パラダイム選択が効く**(chat/canvas/workflow/dashboard/collaborative/autonomous)。タスク構造で選び、本番は複数を組み合わせる。**リサーチエージェントは autonomous+checkpoint が中核**(nightly 自律実行+承認ゲート)。
- **透明性は非交渉**: 思考表示・ツール可視化・context panel は飾りでなく信頼の土台。automation bias に能動的に抗う。
- **ストリーミングがベースライン**: SSE で token/tool/approval を型付きイベント配信。沈黙は不信。
- **承認ゲートは段階化必須**: Tier 1 auto / Tier 2 notify / Tier 3 block。フラット方針は alert fatigue で破綻。timeout は停止側。
- **Generative UI はフロンティア**だが完全モデル駆動は危険 → curated コンポーネントから選ばせる。
- **信頼は一貫性と復旧可能性から**: undo・dry-run・audit trail・calibrated confidence は raw な能力と同じくらい重要。
- 北極星 = **透明な協働者**(Transparent Collaborator): 行動が常に見え、推論に常にアクセスでき、ミスが常に取り消せ、能力と限界が常に明快。全UI判断をこの基準で評価する。

**Part V 完了。** Ch15(地図)→ 知識(16)→ 永続(17)→ 実行時(18)→ アーキ(19)→ 評価(20)→ ツール(21)→ 能力(22)→ エージェント間(23)→ 協調(24)→ 実装(25)→ 対話(26) で、リサーチエージェントを下から上まで積み上げた。**最終章 → Ch12 LLM Agentic Training（上級・任意）。** プロンプト協調で足りなくなったとき、エージェント自身を RL で学習させる層に進む。
