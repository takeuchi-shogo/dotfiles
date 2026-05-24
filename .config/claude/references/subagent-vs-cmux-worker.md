---
status: reference
last_reviewed: 2026-05-25
---

# サブエージェント vs cmux Worker 比較

## 特性比較

| 観点 | サブエージェント (Agent tool) | cmux Worker (ペイン起動) |
|------|------|------|
| **可視性** | ブラックボックス。結果のみ返る | リアルタイムで全 I/O が見える。介入可能 |
| **起動コスト** | 低い。同一プロセス内で即起動 | 高い。ペイン作成 → Claude Code 起動 → Trust確認 → プロンプト送信 |
| **コンテキスト共有** | 親のコンテキスト（CLAUDE.md、メモリ等）を自動継承 | 独立セッション。コンテキストは渡し直す必要がある |
| **結果受け渡し** | 構造化された返り値。親が直接利用可能 | `read-screen` でテキスト読み取り。パース必要 |
| **並列数** | 実質 3-5 程度（コンテキスト制約） | ワークスペース分離で 10+ も可能 |
| **モデル多様性** | Claude のみ（model パラメータで sonnet/opus 切替） | Claude Code / Codex / Gemini / 任意 CLI を混在可能 |
| **タスク時間** | 短時間向き（分単位）。長引くと親がブロック | 長時間OK。非同期で放置してポーリング回収 |
| **障害分離** | サブエージェントのクラッシュ = 結果ロスト | ペインが残るので scrollback から回収可能 |
| **デバッグ** | 困難。途中経過が見えない | 容易。画面で何が起きているか追える |
| **ファイルシステム** | worktree 指定可能だが、デフォルトは共有 | worktree 必須（cmux-team の設計原則） |
| **コスト（トークン）** | 親コンテキスト共有で効率的 | 各セッションが独立にコンテキスト消費。合計トークンは増える |
| **iPhone 監視** | 不可 | cmux-remote で可能 |

## 使い分けの判断基準

| こんなとき | サブエージェント | cmux Worker |
|-----------|:---:|:---:|
| 5分以内に終わる調査・検索 | **◎** | △ |
| 単一ファイルの分析・レビュー | **◎** | △ |
| 30分以上かかる実装 | △ | **◎** |
| Codex / Gemini を使いたい | ✗ | **◎** |
| 途中で人間が介入したい | ✗ | **◎** |
| 複数タスクを 5+ 並列で回したい | △ | **◎** |
| 結果を構造化データで受け取りたい | **◎** | △ |
| トークンコストを抑えたい | **◎** | △ |

## 設計指針

- **デフォルトはサブエージェント**。起動コスト・コンテキスト共有・結果受け渡しで優位
- **cmux Worker に昇格する条件**: 長時間タスク、マルチモデル、高並列、人間介入が必要な場合
- 両者は排他ではなく**併用**。タスクの性質で自動振り分けする

## Agent View / Agent Teams との境界

cmux Worker は **process-level / multi-model** orchestration、Agent View / Agent Teams は **Claude session-level / single-model** orchestration。**別レイヤーであり、cmux が上位互換ではない**。

| 用途 | 機構 | 補足 |
|------|------|------|
| Codex / Gemini 並列、長時間、実機監視 | **cmux Worker** | terminal-observable / multi-model / process-level |
| Claude session の background 管理 (peek/attach) | **Agent View** | `claude agents` dashboard、`claude --bg` / `claude attach`、Claude-only |
| shared task list + peer messaging | **Agent Teams** | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (`settings.json:4` で設定済)、`TeamCreate` / `TaskCreate` / `TaskUpdate` / `TaskList` / `SendMessage` tools、Claude-only peer coordination |

peer coordination が必要なら Agent Teams、Codex/Gemini・長時間・実機監視なら cmux Worker。両者は排他ではなく、用途別に併存する。

> 出典: 2026-05-25 /absorb (Agent Team 7 steps listicle) → Codex 批評で「cmux で上位互換」判定の Confirmation bias を指摘 (`docs/research/2026-05-25-claude-agent-teams-7steps-absorb-analysis.md`)。
