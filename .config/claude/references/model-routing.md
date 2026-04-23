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
| **Haiku** | 軽量な情報取得 | WebFetch+要約、ファイル内容の抽出、フォーマット変換 | `Agent(model: "haiku")` |
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
