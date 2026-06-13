---
status: active
last_reviewed: 2026-04-23
---

# モデル別ルーティング

主エージェント (メインセッションのモデル、現在: Fable 5) は判断・計画・統合・ユーザー対話に集中。実作業はデフォルトで委譲する (委譲手段は「実装委譲の判断表」で規模に応じて選ぶ)。

## モデル階層 (Tier) — source of truth

メインが全部自前でやるのが最大のトークン浪費。タスクは既定で下位 Tier に落とし、上の Tier は「下では品質が落ちる」と判断できるときだけ使う。品質の要は協調プロトコル (Scaffolding > Model) であり、モデル格上げは最後の手段。

| Tier | モデル | 担当 (これ以外は下の Tier へ落とす) | 起動方法 |
|------|--------|--------------------------------------|----------|
| 0 | **メインセッション** (現在: Fable 5) | ユーザー対話、統合判断、最終 verify/マージ判断、新規アーキテクチャ判断、仕様の曖昧さ解消などの最深推論 | (本体) |
| 1 | **Opus** (現行 4.8) | Plan 草案、設計分析、根本原因デバッグ、レビュー統合、edge case 分析 — 推論は要るが Tier 0 級ではないサブタスク | `Agent(model: "opus")` |
| 2 | **Sonnet** | コード実装、ファイル探索、テスト作成、定型レビュー、doc 整備 | `Agent(model: "sonnet")`、複数ファイル+verify は `Workflow({name:'delegate-implementation'})` |
| 3 | **Haiku** | WebFetch 生取得 (要約は呼び出し側責務)、ファイル内容の抽出、フォーマット変換、非権威の cheap grader/prefilter (境界は後述「Model Safety Boundary」) | `Agent(model: "haiku")` |

運用ルール:

- **実装・探索は Sonnet に渡し、独立タスクは並列実行する** — 1 メッセージに複数 Agent call、複数ファイル+verify は delegate-implementation Workflow。メインが Edit/Read を連発しない
- **組み込み agent (Explore / Plan / general-purpose) は `model` を必ず明示する** — 未指定はメインモデル (Fable) を継承し、fan-out が最高単価で走る。目安: Explore→`sonnet`、Plan→`opus`、general-purpose→タスク性質で選択
- agents/*.md の frontmatter は Tier 整合済み (実装・定型レビュー系=sonnet / security-reviewer=opus / CLI driver=haiku)。深い推論が要る回だけ call-time `model: "opus"` で override する (call-time 指定が frontmatter に優先)
- **subagent への model 指定はメインの prompt cache を壊さない** (子は別コンテキスト)。後述「Model Switch / Cache Invalidation Boundary」はメインセッション自体の model 切替の話

### Tier (縦) と Worker (横) は直交

Tier はメインセッション内の Claude モデル段階。Codex / Gemini / Cursor は異視点・1M コンテキスト・マルチモデル比較のための**横の並行軸**で、Tier では代替できない。ブラッシュアップ系の cmux Worker 優先 (CLAUDE.md) は従来通り。

## 外部モデル選択 (横軸)

| モデル | 得意領域 | 委譲タスク例 | 起動方法 |
|--------|----------|-------------|----------|
| **Codex** | 異視点の深い推論 | 設計の壁打ち、リスク分析、セカンドオピニオン、コードレビュー | cmux Worker or `/dispatch` |
| **Gemini** | 1Mコンテキスト | コードベース全体分析、外部リサーチ、マルチモーダル | cmux Worker or `/dispatch` |
| **Cursor** | マルチモデル・Cloud Agent | モデル比較、非同期長時間タスク、Cursor インデックス活用 | `/cursor` skill |
| **Managed Agents** | クラウド実行・スケジュール・外部連携 | 日次ブリーフ、Event-triggered PR、Slack/Teams 応答 | `/claude-api` skill + API/CLI |

## 並行実行の選択肢

- **サブエージェント**: メインをブロックするが結果が確実に返る。軽量タスク向き
- **サブエージェント (BG)**: `run_in_background: true` で非同期。完了通知で結果を受け取る
- **cmux Worker**: 完全並行 + レート制限が別枠。実装・長時間タスク・壁打ちラリー向き。cmux 内 (`CMUX_WORKSPACE_ID` 設定済み) で使用

## 委譲判定

タスクを受けたら「自分 (Tier 0) でやるべきか？」をまず問う。以下に該当しなければ、Tier 表で Opus / Sonnet / Haiku (または外部モデル) を選んで委譲する:
- ユーザーとの対話・意思決定の支援
- 複数の情報を統合した判断
- プランの策定・修正
- 委譲先への指示が説明コストに見合わない単純作業 (1-2 回の Grep/Read 等)

## 実装委譲の判断表と運用

実作業の委譲手段は規模で決める:

| 実装の規模 | 委譲先 | 理由 |
|-----------|--------|------|
| 複数ファイル / verify 込み | `Workflow({name:'delegate-implementation'})` | 構造化委譲。各タスクは並行・直書きなので独立ファイルに分解する |
| 単一〜中規模の実装 | `Agent(model:'sonnet')` 直接 | Workflow はオーバーキル |
| 1-2 回の Grep/Read 等 | メインが自前 | handoff コストが見合わない |

### 主エージェント (現在のメインモデル) の不可譲な責務 (委譲しない)

- 計画策定・タスク分解・委譲先への指示作成
- 複数情報を統合した判断・意思決定の支援
- **実装結果の最終 verify / マージ判断** (一次評価は委譲先が担い、テンプレート品質のメタ評価と取り込み可否は主エージェントが判断する)

### delegate-implementation Workflow の自己評価ループ

`delegate-implementation` を使ったら、戻り値の `templateEval` を必ず `docs/workflows/delegate-implementation.evals.jsonl` に1行記録する (timestamp はメインが付与)。テンプレート改善は `empirical-prompt-tuning` skill の収束判定に従う: 2連続で `sonnetStruggles` 空 + `handoffClarity≥4` + `wouldReuse:true` なら安定、未達なら最頻 `suggestions` を最小 diff で適用する。詳細は `docs/workflows/delegate-implementation.evals.README.md`。

## Design Principles

### End-to-End Completion > Per-Call Efficiency

**短くても完走する pipeline > 全 stage を最適化して途中で止まる pipeline**。

委譲・並列化の設計判断では、個別 call の効率 (model 選定・コンテキストサイズ・トークン削減) より「end-to-end で commit/PR/verify までユーザーが attestable な成果物に到達するか」を優先する。

- **bad**: 各 stage に最適 model を割り当てたが、stage 間 handoff で context を失い、最後の stage で詰まって commit に至らない
- **good**: 全 stage を Sonnet で済ませても、stage 間 anchor (resume-anchor-contract / HANDOFF.md / Success Criteria) を維持して commit + PR まで完走する
- **判断ヒント**: 委譲先の選定で迷ったら、「失敗した場合に main session が修復できるか」を問う。修復できないなら model upgrade よりも anchor の強化を先にする
- **由来**: 「How I got banned from GitHub due to my harness pipeline」(2026-04) — 13-stage pipeline は per-stage 最適化されていたが attestation 喪失で BAN に至った事例の翻訳

## Stage 別 Reasoning Budget 推奨 (任意チェックリスト)

出典: LangChain Terminal Bench 2.0 (GPT-5.2-Codex, 2026-04)。
- 全段 max reasoning: **53.9%**
- Reasoning Sandwich (plan=high, build=reduced, verify=high): **66.5%** (+13.7pt)

| Stage | 推奨 reasoning effort | 理由 |
|-------|----------------------|------|
| Plan / Spec | high | 全体構造・失敗モード抽出に深い推論が要る |
| Build / Implement | medium | 決定後の生成は深い推論が過剰 (53.9% の罠) |
| Verify / Review | high | エッジケース検出・批評に深い推論が効く |

**使い方**: Codex Spec/Plan Gate は `-c reasoning_effort=high`、Review Gate は `-c reasoning_effort=high`、Implement は medium 以下で十分。強制ではなく任意の参考。自動配分 (stage-aware routing) は運用複雑性が増えるため採用しない。

**由来**: `docs/research/2026-04-24-harness-engineering-absorb-analysis.md` (AlphaSignal Harness Engineering absorb)

## WebFetch 委譲注記 (Haiku 内部要約対策)

Claude Code v2.1.126 で `WebFetch` は内部 Haiku 要約 + 100k chars truncation を観測 (`docs/research/2026-05-06-webfetch-haiku-summary-absorb-analysis.md`)。Haiku 委譲時は二重圧縮 (Haiku 内部要約 → 委譲先要約) を回避するため、**生取得段階に限定**し要約は呼び出し側で行う。経路選択は `references/web-fetch-policy.md` に従う。

## Model Switch / Cache Invalidation Boundary

> 出典: "How Anthropic Engineers Actually Save Tokens" (2026-05) + Codex review (2026-05-21) + 公式 [Claude Code prompt caching docs](https://code.claude.com/docs/en/prompt-caching)。

prompt cache は **model 固有**。プロンプトの prefix が変わる以下のイベントで cache は完全リセットされる。切替は **task boundary（独立タスクの開始時）でのみ**行い、ターン中で model を渡り歩かない。

### Cache を破壊するイベント

| イベント | 影響範囲 | 備考 |
|---------|---------|------|
| **Model switch** (Opus ↔ Sonnet ↔ Haiku) | 全 layer | 各 model が独自 cache を持つため、切替で 0 hit rate |
| **`opusplan` mode** (plan=Opus / execute=Sonnet) | 全 layer | plan↔execute の都度 model switch が発生。長時間ループでは初回 miss が累積する |
| **MCP server 接続/切断** | system layer | tool definitions が変わる |
| **Tool deny / allow 変更** | system layer | tool 集合変化 |
| **Claude Code 本体 upgrade** | system layer | base system prompt 変化 |
| **CLAUDE.md / settings.json edit** | project layer | mid-session edit は restart まで未反映 (live cache は安全)。次起動時に rebuild |

### Boundary Rule

- **opusplan は禁止しない**: plan 品質の向上 (Opus の deep reasoning) は token cost より価値が高いケースが多い。ただし「opusplan で毎ターン model 切替」を recurring loop に組み込まない
- **切替は task boundary で**: 別タスクに移るタイミングでだけ model を変える。ターン中に「ちょっと Haiku に投げて戻す」は cache miss が累積する
- **長い subagent workflow には cache 期待しない**: subagent TTL=5min なので 5 分超のループは subscription cache が効かない。`subagent-delegation-guide.md` も参照

## Model Safety Boundary (Fable classifier / Haiku grader 境界)

> 出典: Fable 5 14-steps absorb (2026-06-12)。fallback 仕様は公式 docs で確認済 (platform.claude.com/cookbook/fable-5-fallback-billing-guide)。

性質の異なる 2 つの「classifier」を混同しない:

1. **Platform 側 domain safety fallback (server-side、こちらで実装するものではない)**: Fable 5 は cyber/bio/chem/distillation 領域の要求を検出すると **server 側で Opus 4.8 に透過的に自動切替**する (billing は cache hit 扱い)。security-reviewer 系タスク・脆弱性調査・暗号 primitive のレビューは Fable 指定でも実質 Opus 4.8 で走りうる。挙動が想定とズレたらこの透過 fallback を疑い、明示的に `Agent(model: "opus")` を指定して切り分ける
2. **ローカル Bash permission classifier の outage (これは別物)**: `/model claude-fable-5` で Bash auto-mode classifier がセッション全体で死亡した実績 (2026-06-10)。trivial コマンドの成功を復帰の証拠にしない。復旧は `/model` で実績モデルへ。詳細: memory `feedback_model_fable_classifier_outage.md`

**Haiku grader 境界**: Tier 3 の Haiku は「非権威の cheap prefilter / 形式チェック grader」(`/goal` evaluator も Haiku) までに限定する。**permission/safety 判定・最終 verify・マージ判断には使わない** — LLM に Tool Use 権限を判定させる permission classifier は determinism boundary 違反 + prompt injection 耐性なしとして reject 済み (`docs/research/2026-05-31-cursor-auto-review-run-mode-absorb-analysis.md` #4)。最終評価の権威は Tier 0 の不可譲な責務 (上記「主エージェント (現在のメインモデル) の不可譲な責務」)。

## Cost-aware Fallback (2026-06-15〜 Agent SDK credit 対応)

2026-06-15 から `claude -p` / Claude Agent SDK / Claude Code GitHub Actions は subscription pool ではなく **月次 Agent SDK credit** から消費される (詳細: `references/agent-sdk-credit.md`)。Credit 枯渇時、または heavy parallel `claude -p` バッチを設計する段階で以下の順序でフォールバック判断する:

1. **Codex (cmux Worker) に委譲** — 設計判断・批評・review は元々 Codex 推奨。subscription pool 外で動く独立予算
2. **Gemini (cmux Worker) に委譲** — 大規模分析・grounding 検索は Gemini が適切。同じく独立予算
3. **Interactive Claude Code (TUI) に切替** — parallel orchestration を諦めるが subscription pool に戻る
4. **extra usage 有効化 + API rate 受け入れ** — 上記が不可な場合のみ

判断ポイント: 起動前に「subscription pool で済むか、credit 消費か」を意識する。`/research` `/autonomous` の `claude -p` 多用はヘビー枠扱い、Codex/Gemini 委譲を先に検討する。Subagent (`Agent` tool) 経由は Claude Code 内部呼び出しで subscription 扱いのため影響なし。
