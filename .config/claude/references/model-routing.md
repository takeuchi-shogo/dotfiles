---
status: active
last_reviewed: 2026-04-23
---

# モデル別ルーティング

主エージェント (Opus 等) は判断・計画・統合・ユーザー対話に集中。実作業はデフォルトで委譲する。

## モデル選択

| モデル | 得意領域 | 委譲タスク例 | 起動方法 |
|--------|----------|-------------|----------|
| **Sonnet** | 高速実装・定型作業 | ファイル探索、コード実装、テスト作成、URL取得+要約、定型レビュー | `Agent(model: "sonnet")` |
| **Haiku** | 軽量な情報取得 | WebFetch (生 markdown 取得まで、要約は呼び出し側責務)、ファイル内容の抽出、フォーマット変換 | `Agent(model: "haiku")` |
| **Codex** | 異視点の深い推論 | 設計の壁打ち、リスク分析、セカンドオピニオン、コードレビュー | cmux Worker or `/dispatch` |
| **Gemini** | 1Mコンテキスト | コードベース全体分析、外部リサーチ、マルチモーダル | cmux Worker or `/dispatch` |
| **Cursor** | マルチモデル・Cloud Agent | モデル比較、非同期長時間タスク、Cursor インデックス活用 | `/cursor` skill |
| **Managed Agents** | クラウド実行・スケジュール・外部連携 | 日次ブリーフ、Event-triggered PR、Slack/Teams 応答 | `/claude-api` skill + API/CLI |

## 並行実行の選択肢

- **サブエージェント**: Opus をブロックするが結果が確実に返る。軽量タスク向き
- **サブエージェント (BG)**: `run_in_background: true` で非同期。完了通知で結果を受け取る
- **cmux Worker**: 完全並行 + レート制限が別枠。実装・長時間タスク・壁打ちラリー向き。cmux 内 (`CMUX_WORKSPACE_ID` 設定済み) で使用

## 委譲判定

タスクを受けたら「自分 (Opus) でやるべきか？」をまず問う。以下に該当しなければ委譲する:
- ユーザーとの対話・意思決定の支援
- 複数の情報を統合した判断
- プランの策定・修正
- 委譲先への指示が説明コストに見合わない単純作業 (1-2 回の Grep/Read 等)

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

## Cost-aware Fallback (2026-06-15〜 Agent SDK credit 対応)

2026-06-15 から `claude -p` / Claude Agent SDK / Claude Code GitHub Actions は subscription pool ではなく **月次 Agent SDK credit** から消費される (詳細: `references/agent-sdk-credit.md`)。Credit 枯渇時、または heavy parallel `claude -p` バッチを設計する段階で以下の順序でフォールバック判断する:

1. **Codex (cmux Worker) に委譲** — 設計判断・批評・review は元々 Codex 推奨。subscription pool 外で動く独立予算
2. **Gemini (cmux Worker) に委譲** — 大規模分析・grounding 検索は Gemini が適切。同じく独立予算
3. **Interactive Claude Code (TUI) に切替** — parallel orchestration を諦めるが subscription pool に戻る
4. **extra usage 有効化 + API rate 受け入れ** — 上記が不可な場合のみ

判断ポイント: 起動前に「subscription pool で済むか、credit 消費か」を意識する。`/research` `/autonomous` の `claude -p` 多用はヘビー枠扱い、Codex/Gemini 委譲を先に検討する。Subagent (`Agent` tool) 経由は Claude Code 内部呼び出しで subscription 扱いのため影響なし。
