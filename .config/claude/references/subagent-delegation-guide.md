# エージェント委譲ガイド

サブエージェントの目的は **コンテキスト圧縮**。並列性は副次的な利点。
サブエージェントが8ファイル読んで15回ツール呼び出しをしても、親は750トークンの要約だけ受け取る。

---

## 最上位原則: コンテキスト境界で分割する

> "Design around context boundaries, not around roles or org charts."

タスク分割は**ロール**（planner, implementer, tester）ではなく**コンテキスト**で決める。

| 判断基準 | 分割する | 同一エージェントに留める |
|---|---|---|
| **情報の重複** | 2つのサブタスクが完全に独立した情報で動作 | 深く重複する情報が必要（例: 実装者がテストも書く） |
| **ハンドオフコスト** | インターフェースが明確（diff を渡すだけ等） | 暗黙の前提が多く、伝達で劣化する |
| **発見の影響** | 一方の発見が他方の作業を変えない | 一方の発見で他方のアプローチが変わる |

**原則**: 単一エージェントで押して、限界が見えたところで分割する。最初から多エージェントにしない。

---

## Task Parallelizability Gate

サブエージェントに分割する**前**に、タスク特性を判定する。
Google Research (2025) の実証: 逐次推論タスクにマルチエージェントを適用すると **-39〜70% 劣化**。

```
タスクは embarrassingly parallel?  → 並列化の恩恵あり（+81% の事例あり）
タスクに逐次推論が必要?           → シングルエージェントを維持（並列は劣化リスク）
迷ったら?                         → シングルで始めて、ボトルネックが見えたら分割
```

| タスク特性 | 例 | 推奨戦略 |
|---|---|---|
| **並列可能** | 独立ファイルのレビュー、複数ソースのリサーチ、独立テスト実行 | Parallelization / Orchestrator-Worker |
| **逐次推論** | デバッグ（原因→仮説→検証の連鎖）、段階的リファクタリング、依存のある設計判断 | Prompt Chaining / シングルエージェント |
| **混合** | API設計（並列調査）→ 実装（逐次） | フェーズごとに戦略を切り替え |

> **出典**: Google Research "Towards a Science of Scaling Agent Systems" — Finance-Agent (並列可能) で +81%、PlanCraft (逐次推論) で -70%。

---

## Decision Framework

```
結果が次のステップに必要?        → Sync（Agent ツール）
独立タスク、ブロック不要?        → Async（claude -p / background agent）
将来の特定時刻に実行?            → Scheduled（CronCreate / cron）
迷ったら?                        → Async がデフォルト（親のコンテキストを守る）
```

---

## Context Inheritance Policy (fork_context)

> 出典: Pan et al. 2026 "Natural-Language Agent Harnesses" — IHR の fork_context=true/false で子エージェントのコンテキスト継承を制御

子エージェントを起動する際、**親の会話コンテキストを引き継ぐか否か**を意識的に選択する。

| モード | 説明 | いつ使う |
|--------|------|---------|
| **Inherit** (fork_context=true) | 親の蓄積コンテキストを子が引き継ぐ | 親の発見・判断に依存する作業（レビュー結果を踏まえた修正等） |
| **Clean** (fork_context=false) | 子は最小限のタスクパケットだけ受け取る | 独立した調査・実装（親のバイアスを避けたい場合） |

### Claude Code での実現

| モード | 実装方法 |
|--------|---------|
| **Inherit** | Agent ツール（デフォルト）— プロンプトに十分なコンテキストを含める |
| **Clean** | `claude -p` でヘッドレス起動、または worktree + 最小プロンプト |

### 判断基準

```
子の作業に親の発見が必要?     → Inherit
子の独立した視点が欲しい?     → Clean（セカンドオピニオン、リスク分析）
迷ったら?                     → Clean がデフォルト（コンテキスト汚染を防ぐ）
```

### Clean モードの最小入力セット

fork_context=false（Clean）で起動する場合、子エージェントには **3 項目のみ** を渡す:

| # | 項目 | 内容 |
|---|------|------|
| 1 | **Task** | 具体的なタスク指示（ファイルパス・行番号・型情報を含む自己完結的な記述） |
| 2 | **Path** | 作業ディレクトリまたは worktree パス + ブランチ名 |
| 3 | **Awareness Summary** | 並列実行時のみ。他のエージェントが何をしているかの 1-2 行サマリ |

コンテキストが狭いほどエージェントの出力品質は上がる。「念のため」で追加情報を渡さない。

> 出典: Mex Emini "Parallel Agent Orchestrator" — "Narrower context per agent produces better output. Agents with too much context second-guess themselves."

---

## Awareness Summary（並列実行時の相互認識）

並列でサブエージェントを起動する場合、各エージェントに **他のエージェントが何をしているか** を伝える。
目的は衝突回避であり、協調ではない。エージェント間の直接通信は不要。

### テンプレート

```
## Awareness Summary
他のエージェントが並行して以下の作業をしています:
- Agent A: {タスク概要}（{対象ファイル/ディレクトリ}）
- Agent B: {タスク概要}（{対象ファイル/ディレクトリ}）

あなたの担当外のファイルには触れないでください。
共有ファイルの変更が必要な場合は、変更せずにその旨を報告してください。
```

### ルール

- **Orchestrator のみが Awareness Summary を生成する**。Subagent は他 Subagent に直接通信しない
- **対象ファイル/ディレクトリを明示する**。「Agent B がフロントエンドをやっている」ではなく「Agent B が `src/components/Auth.tsx` を変更中」
- **Awareness Summary は読み取り専用情報**。Subagent はこの情報で自分の作業を制限するが、他 Subagent の作業を変更する判断はしない
- **Agent Teams では不要**。Teams は `SendMessage` でピア間通信できるため、静的な Awareness Summary より優れている

> **注意**: Inherit モードでは親のコンテキスト長が子のプロンプトトークンに加算される。長いセッションでは Clean モードの方がトークン効率が高い。

---

## Worktree = 隔離されたランタイム環境

Git worktree はファイルシステムの隔離だけでなく、**ランタイム環境全体の隔離** として設計する。

| レイヤー | 何を隔離するか | 例 |
|----------|---------------|-----|
| **ファイル** | ソースコード、設定ファイル | `git worktree add` で自動 |
| **環境変数** | `.env`、ポート、ドメイン | worktree ごとに `.env` をパッチ |
| **プロセス** | 開発サーバー、DB | worktree ごとに別ポートで起動 |
| **アクセス** | ブラウザ URL | worktree ごとに固有ドメイン/ポート |

**dotfiles リポジトリでは**: ファイル隔離のみで十分（サーバー不要）。
**Web アプリプロジェクトでは**: `.env` パッチ + サーバー自動起動 + 固有ドメインまで自動化すると、コンテキストスイッチがゼロになる。

> 出典: Mex Emini "Parallel Agent Orchestrator" — "branches aren't states to switch between, they're environments to run in parallel"

---

## 3パターン

### Pattern 1: Sync — 「やって待つ」

親が Agent ツールでサブエージェントを起動し、結果が返るまでブロック。

**使い所**: 結果がないと次に進めないタスク
- コードレビュー → 指摘を受けて修正
- テスト作成 → テスト結果を確認
- 分析・調査 → 結果を統合して報告

**dotfiles での実装**:
- Agent ツール（`subagent_type` でエージェント指定）
- `/review`: 変更規模に応じて 2-4 エージェント並列起動 → 結果統合
- デバッグ: `debugger`, `codex-debugger` に委譲 → 根本原因を受け取る

**フレーミング**: 親が結果を統合するため、サブエージェントは **簡潔に** 返す。
```
あなたはサブエージェントです。結果は親エージェントに返され、統合されます。
要点を簡潔にまとめてください。詳細な説明より、発見事項と推奨アクションを優先してください。
```

**トレードオフ**: 結果が親のコンテキストに入る。ただし完全な軌跡ではなく要約なので 90%+ 削減。

---

### Pattern 2: Async — 「やっておいて、終わったら教えて」

親がタスクを発火して即座に会話を継続。サブエージェントは独立して完了し、結果をユーザーに直接報告。

**使い所**: 長時間の独立タスク
- 並列リサーチ（`/research` で 3-8 サブタスク並列）
- 自律実行（`/autonomous` でセッション跨ぎ）
- バックグラウンド分析

**dotfiles での実装**:
- `claude -p`（`/research`, `/autonomous`）
- Agent ツール + `run_in_background: true`
- worktree 隔離（`/autonomous` の並列タスク）

**フレーミング**: ユーザーへの最終報告になるため、**詳細かつ自己完結的に** 返す。
```
あなたは非同期サブエージェントです。結果はユーザーに直接報告されます。
背景・分析・結論を含む自己完結的なレポートを作成してください。
ソースや根拠を明記してください。
```

**トレードオフ**: 親は結果を統合できない。複数 async を横断した分析は別途必要。

---

### Pattern 3: Scheduled — 「あとでやって」

将来の特定時刻にサブエージェントを実行。単なるリマインダーではなく、実行時のライブデータで分析する。

**使い所**: 定期チェック、フォローアップ、時間差分析
- デプロイメトリクスの翌朝分析
- AutoEvolve の日次改善サイクル
- 定期的な依存更新チェック

**dotfiles での実装**:
- `autoevolve-runner.sh`（cron: `0 3 * * *`）→ `/improve` を自動実行
- `/daily-report`（手動 or cron）
- CronCreate ツール（セッション内から動的にスケジュール）

**静的 cron vs 動的 CronCreate の使い分け**:

| 方式 | 適用 | 例 |
|---|---|---|
| **cron**（autoevolve-runner.sh） | 固定スケジュール、長期運用 | 日次 AutoEvolve、週次依存チェック |
| **CronCreate** | セッション中に動的に決定 | 「明日の朝にデプロイ結果を確認」「1時間後にテスト結果をチェック」 |

**核心的な違い**: Scheduled はただのリマインダーではない。「明日デプロイ結果を確認して」は通知ではなく、**明日の時点でライブデータを取得し分析するエージェント** が走る。タスク記述は固定だが、実行時のデータは新鮮。

**dotfiles での活用パターン**:

```
# 固定スケジュール（cron）— 既に運用中
autoevolve-runner.sh → 毎朝3時に /improve を実行

# 動的スケジュール（CronCreate）— セッション内から
「1時間後にテストの flaky 率を確認して」
「明日の朝にこの PR の CI 結果をまとめて」
「今週金曜にこのリファクタリングの影響を分析して」

# ポーリング（/loop スキル）— 繰り返し確認
「5分ごとに deploy の status を確認して」
```

**トレードオフ**: タスク記述はスケジュール時に固定される。キャンセル・変更が難しい。`task-registry.jsonl` でタスク ID・ステータス・成果物パスを追跡可能（`references/task-registry-schema.md` 参照）。

---

## サブエージェント vs Agent Teams

2つのマルチエージェントパラダイムは異なる問題を解決する。

### 判断基準

```
作業は embarrassingly parallel?      → サブエージェント（fire-and-forget）
エージェント間で発見の共有が必要?    → Agent Teams（ongoing coordination）
迷ったら?                            → サブエージェントから始める
```

| 観点 | サブエージェント | Agent Teams |
|---|---|---|
| **ライフサイクル** | 短命。タスク完了で消滅 | 長命。チーム解散まで持続 |
| **通信** | 親にのみ報告。ピア間通信なし | ピア間で直接通信（SendMessage） |
| **状態共有** | なし。各自が独立コンテキスト | 共有タスクリスト + ピアメッセージ |
| **依存管理** | 親が手動で順序制御 | `blockedBy` で宣言的に表現 |
| **コンテキスト** | 親は要約のみ受け取る（圧縮） | 各 teammate が自分のコンテキストを蓄積 |
| **適用例** | レビュー、リサーチ、分析 | 複数コンポーネント同時開発、EPD フロー |

### Agent Teams 適性フィルター（Green/Yellow/Red）

Teams を使う前に、タスクが本当に Teams を必要としているか判定する。

| 適性 | ユースケース | 理由 |
|------|-------------|------|
| **Green（推奨）** | 並列コードレビュー（security/performance/coverage 分離）| **Bias isolation**: 単一エージェントの最初の発見がアンカリングバイアスで後続レビュー全体を歪める。分離で各レビューアーが clean な視点を保つ |
| **Green（推奨）** | 競合仮説デバッグ（仮説ごとにエージェント分離 + 相互反証） | **Context bias 防止**: 1つの証拠で他の仮説の調査が弱まる。分離で各仮説が公平に検証される |
| **Green（推奨）** | クロスレイヤー機能（Frontend/Backend/Tests 並走） | 各エージェントが自分のドメインに留まり、相互通知で API 契約変更を即時共有 |
| **Green（推奨）** | 大規模 read-only 探索（調査・リサーチ・コンテキスト収集） | ファイル衝突ゼロ。Teams 入門に最適 |
| **Yellow（条件付き）** | ドメイン分離が明確なマルチファイルリファクタ | ファイル重複がないことを保証できる場合のみ |
| **Red（非推奨）** | 逐次依存のタスク | サブエージェントまたは単一セッションで十分 |
| **Red（非推奨）** | 同一ファイル編集 | マージコンフリクト確定。例外なし |
| **Red（非推奨）** | 単一セッションで完了可能なタスク | 3-4x のトークンオーバーヘッドが見合わない |
| **Red（非推奨）** | トークンコスト重視のワークフロー | teammate 1人 = 1 フルコンテキストウィンドウ |

### Agent Teams が有効なシナリオ

| シナリオ | なぜサブエージェントでは不十分か | Teams の利点 |
|---|---|---|
| Frontend + Backend 同時開発 | API 契約の変更を後からマージで発見 | Backend が API を変えたら Frontend に即通知 |
| 大規模リファクタ（依存あり） | task_list.md の静的依存では中間発見を反映不可 | 先行タスクの発見が後続の approach を動的に変更 |
| EPD フロー | Spec → Build → Review の逐次実行はボトルネック | Product/Engineering/Design が並走し即フィードバック |
| **競合仮説デバッグ** | 単一エージェントが1つの仮説に偏り、他を十分に検証しない | 仮説ごとにエージェントを分離し「相互反証」を指示。生き残った仮説が根本原因の可能性が高い |

### Teams の Lead 運用ガイド

**Delegate Mode を有効にする**: Shift+Tab で delegate mode をトグル。Lead がコード実装を始めてしまうのは最も多い失敗パターン。delegate mode ON で Lead は計画・委譲・統合に専念する。

**Teammate あたり 5-6 タスクが上限**: 20 個一括で渡さない。自己完結したユニットに分解し、1つずつキックオフしてから次を渡す。実際のエンジニアのマネジメントと同じ。

**Active monitoring**: set-and-forget しない。cmux / tmux の split-pane で全 teammate を監視する。Lead が自分で実装し始めたら即座に「Wait for your teammates to complete their tasks before proceeding.」と指示する。

### Teammate Briefing テンプレート

Teammates は親の会話履歴を**一切継承しない**。CLAUDE.md、MCP サーバー、spawn prompt のみがコンテキスト。spawn prompt には以下を明示的に含める:

```
## Briefing チェックリスト（spawn prompt に含める）
- [ ] プロジェクト構造（関連ディレクトリ・ファイル）
- [ ] コーディング規約・スタイルガイド
- [ ] 具体的なゴール（何を達成すべきか）
- [ ] 担当ドメインの境界（何を触って良いか / 触ってはいけないか）
- [ ] 成果物の形式（diff、レポート、テスト結果等）
```

spawn prompt が薄いと結果が凡庸になる。「1時間かけて蓄積したコンテキストはゼロから渡し直す」ことを常に意識する。

### Teams のライフサイクル

> **⚠️ Session ephemeral**: Agent Teams はセッションと生死を共にする。/resume は存在しない。セッション死亡 = チーム消滅。長時間タスクでは `/checkpoint` で中間成果を保全し、中断に備える。

```
Team Lead (Claude):
└── spawnTeam("feature-x")
    Phase 1 — 設計合意:
    └── spawn("architect", prompt="API 設計", plan_mode_required=true)
    Phase 2 — 並列実装:
    └── spawn("backend", prompt="API 実装")
    └── spawn("frontend", prompt="UI 実装")
    └── spawn("test-writer", prompt="統合テスト", blockedBy=["backend"])
    Phase 3 — 統合:
    └── Lead が全 teammate の成果物をマージ・検証
```

### Worktree エージェントの書き込み制約

> 出典: Multi-Agent Autoresearch Lab — memory-keeper のみが main checkout に書き込み、worker は worktree 内のみ code mutation

worktree で隔離されたエージェント（worker）は **main checkout への Write/Edit を禁止** する。
永続状態（memory, lessons-learned, promoted master）への書き込みは main checkout 側のエージェント（memory-keeper ロール）が担当する。

| ロール | main checkout | worktree |
|--------|:---:|:---:|
| **memory-keeper**（親 or Lead） | Write 可 | - |
| **worker**（worktree 内） | **Write 禁止** | Write 可 |

**理由**: worker が main checkout に書き込むと、並列実行時に状態の競合が発生する。永続状態の更新は単一のゲートキーパーに集約する。

### ハンドオフフォーマット

エージェント間でタスクを引き継ぐ際、以下の情報を明示的に渡す:

```markdown
## Handoff Packet
- **Goal**: 何を達成すべきか（1文）
- **Context**: 前工程で判明した事実・制約（箇条書き）
- **Artifacts**: 参照すべきファイルパス・diff・ログ
- **Acceptance Criteria**: 完了の判定基準
- **Not in Scope**: 明示的にやらないこと
```

spawn prompt や SendMessage でハンドオフする際は、このフォーマットに沿って情報を構造化する。暗黙の前提に依存しない。

### ラボ型ロール定義

反復改善ループ（仮説検証・パフォーマンスチューニング等）での4+1ロール。
詳細は `references/experiment-discipline.md` を参照。

| ロール | 責務 | dotfiles での対応 |
|--------|------|------------------|
| researcher | 文献・事例探索 | `/research`, gemini-explore |
| planner | 実験キュー・優先順位 | Lead（EnterPlanMode） |
| worker | 1仮説を worktree で実行 | `/spike` + worktree |
| reporter | 結果収集・観測性 | session-trace-store, `/improve` |
| memory-keeper | 永続状態管理 | memory システム |

### Teams の Anti-patterns

| やりがち | 代わりにやるべき |
|---|---|
| 独立タスクに Teams を使う | サブエージェント（コンテキスト圧縮が効く） |
| 全員が同じファイルを編集 | インターフェースを先に合意、実装は分離 |
| Lead を経由せず teammate 同士だけで完結 | Lead が最終統合と品質判断を担う |
| Teams 内で再帰的に Teams を作る | 1レベルの Teams に留める |
| **Lead が自分で実装を始める** | **delegate mode ON を維持。Lead は計画・委譲・統合に専念** |
| **spawn prompt を省略する** | **Briefing テンプレートに従い、構造・規約・ゴール・境界を明示** |
| **teammate に 10+ タスクを一括投入** | **5-6 タスク/teammate。完了を確認してから次を渡す** |

### 競合仮説デバッグパターン

Agent Teams の固有パターン。単一エージェントでは Context bias により最初に見つけた証拠に引きずられるため、仮説ごとにエージェントを分離する。

```
仮説が N 個ある場合:
  N 個の teammate を spawn（各 teammate = 1 仮説）
  各 teammate のプロンプトに含める:
    1. 自分の仮説の詳細
    2. 「この仮説を証明するだけでなく、反証する証拠も積極的に探せ」
    3. 「他の teammate の仮説を意識し、自分の仮説がなぜ正しいかを論証せよ」
  Lead が全 teammate の結果を統合:
    - 反証に生き残った仮説 = 根本原因の可能性が高い
    - 複数の仮説が生き残った場合は組み合わせを検討
```

**Key insight**: 「相互反証を指示する」ことが重要。指示がないとエージェントは自分の仮説を確認して終わる。falsification を明示的に要求することで、生き残った仮説の信頼性が大幅に向上する。

**実用上限**: 3-5 仮説（= 3-5 teammates）。それ以上は Lead の統合コストが利益を上回る。

---

## 5つのオーケストレーションパターン

サブエージェント / Teams のどちらでも適用できる基本パターン。

| パターン | 構造 | 使い所 | dotfiles での実装 |
|---|---|---|---|
| **Prompt Chaining** | A → B → C（逐次、前の出力が次の入力） | 依存するステップ | Plan → Implement → Test → Review |
| **Routing** | 分類器 → 専門ハンドラ | 入力で処理を振り分け | `triage-router`, `agent-router.py` |
| **Parallelization** | A, B, C を同時実行 → 統合 | 独立サブタスク | `/review` 並列起動, `/research` |
| **Orchestrator-Worker** | 親が分解 → 子に委譲 → 統合 | 動的な作業分割 | `/autonomous`, `/review` |
| **Evaluator-Optimizer** | 生成 → 評価 → フィードバック → 再生成 | 品質が速度より重要な場合 | `completion-gate.py`, TDD ループ |

### Evaluator-Optimizer の適用ガイド

生成と評価を分離し、フィードバックループで品質を収束させるパターン。

```
Generator Agent → 成果物 → Evaluator Agent → 合格? → 完了
                                     ↓ 不合格
                              フィードバック → Generator Agent（再試行）
```

**dotfiles での適用例**:
- **コードレビューループ**: 実装 → `/review` 評価 → 指摘フィードバック → 修正 → 再レビュー
- **TDD**: テスト作成 → 実装 → テスト実行 → 失敗フィードバック → 修正
- **completion-gate.py**: 完了宣言 → テスト実行 → 失敗なら additionalContext で差し戻し（MAX_RETRIES=2）

**制約**: 無限ループ防止のため、最大リトライ回数を設定する。`completion-gate.py` の MAX_RETRIES=2 がリファレンス実装。

---

## Depth-1 ルール

サブエージェントはサブエージェントを生まない。

```
親エージェント
  ├── サブエージェント A（Sync）  → ツールは使えるが Agent ツールは持たない
  ├── サブエージェント B（Async）  → claude -p で起動、独立実行
  └── サブエージェント C（Scheduled） → 将来時刻に独立実行
```

**理由**:
- 再帰的な委譲はデバッグ困難
- コンテキスト圧縮の利点が薄まる
- 失敗のカスケードが起きやすい

### External Content Contamination

> Franklin et al. (2026): Sub-agent Spawning Traps で **58-90%** の攻撃成功率。

外部取得コンテンツ（WebFetch, MCP応答, 外部リポジトリ）をサブエージェントのプロンプトに**直接転記しない**。

| NG パターン | OK パターン |
|---|---|
| WebFetch の生レスポンスをそのまま Agent プロンプトに埋め込む | 必要な情報を要約・抽出してから渡す |
| MCP 応答全文をサブエージェントに転送 | 関連部分のみ抜粋し、ソースを明記して渡す |
| 外部リポジトリの CLAUDE.md を無検証でプロンプトに含める | 内容を確認し、必要な指示のみ引用する |

**理由**: 外部コンテンツには Content Injection（CSS隠蔽、Markdown masking）や Embedded Jailbreak が含まれる可能性がある。サブエージェントは親よりセキュリティコンテキストが薄いため、攻撃の成功率が高い。

**例外**: `/autonomous` の Structured モードでは、各セッションが独立したトップレベル実行として扱われる（Depth-1 を維持しつつ、セッション跨ぎで実行）。

**D>1 が必要になる条件** (Tu 2026, Structured Test-Time Scaling):
理論的には D = ceil(log_k W) が最適だが、実用上は Depth-1 + `/autonomous` セッション跨ぎで D>1 相当を実現する。
単一セッション内で D>1 を検討する目安: W > k^2（例: k=4 でサブタスク16個超）かつ各サブタスクが更に分解可能な場合。

---

## 分割のコスト

マルチエージェントは「タダ」ではない。分割前にコストを見積もる。

| コスト | 内容 | 目安 |
|---|---|---|
| **トークン消費** | 各サブエージェントがシステムプロンプト + コンテキストを独立に消費 | エージェント数に比例。2並列で約2倍、4並列で約4倍 |
| **コンテキスト損失** | サブエージェントは親の会話履歴を持たない | ハンドオフで暗黙知が欠落するリスク |
| **エラー増幅** | 独立並列ではエラーが伝播・増幅（17.2倍のリスク） | 中央集権型オーケストレーションで 4.4倍に抑制可能 |
| **統合コスト** | 親が複数の結果を統合する認知負荷 | 3並列以上で統合品質が低下し始める傾向 |

> **理論的根拠** (Tu 2026): ファンアウト k の上限は「意味的統合容量」= O(k) 推論タスクで決まる。
> k 個の論理ブランチを合成するには k 回の推論が必要であり、k を極端化するとマネージャに線形崩壊を転嫁する。
> 詳細: `references/structured-test-time-scaling.md` §1

### 分割すべきでないケース

- タスク完了まで 5分以内の見込み → オーバーヘッドが本体を上回る
- サブタスク間で「発見の共有」が頻繁に必要 → ハンドオフコストが支配的
- 逐次推論チェーンの途中 → 分割すると推論の一貫性が崩れる

> **判断原則**: 「分割で得られるコンテキスト圧縮 > 分割で失うコンテキスト共有」の場合のみ分割する。

---

## Generic vs Specialized の判断基準

デフォルトは **Generic**。特化は以下の条件を満たす場合のみ:

| 特化する条件 | 例 |
|---|---|
| **異なるモデルが必要** | Codex（深い推論）、Gemini（1M コンテキスト） |
| **セキュリティ境界** | `db-reader`（SELECT のみ）、`safe-git-inspector`（読み取り専用） |
| **証明されたパフォーマンス差** | eval で汎用より特化が勝つ場合 |

**dotfiles のアプローチ**: review-checklists/ に言語固有知識を外部化し、汎用 `code-reviewer` にプロンプト注入。エージェント数を増やさずに特化知識を活用。

---

## スケーリングテーブル

| サブタスク数 | 実行方法 | パターン |
|---|---|---|
| 1 | Agent ツール（直接実行） | Sync |
| 2-4 | Agent ツール × N（並列起動） | Sync（並列） |
| 3-8 | `claude -p` 並列 | Async |
| 9+ | 2バッチ順次実行 | Async（メモリ保護） |
| 後で | CronCreate / cron | Scheduled |

---

## フレーミング注入

サブエージェント起動時に、パターンに応じたフレーミング命令をプロンプト先頭に注入する。
テンプレートは **`references/subagent-framing.md`** に集約。

| パターン | フレーミング | 注入先 |
|---|---|---|
| Sync | 簡潔に返す（親が統合） | `/review` の Dispatch ステップ |
| Async | 自己完結的レポート（ユーザーへ直接報告） | `/research` の Execute、`/autonomous` の executor-prompt |
| Scheduled | ライブデータ優先（実行時の状態で分析） | CronCreate のプロンプト |

---

## タスクレジストリ

Async/Scheduled サブエージェントの成果物を追跡する軽量レジストリ。
スキーマは **`references/task-registry-schema.md`** を参照。

- **保存先**: `~/.claude/agent-memory/task-registry.jsonl`
- **ユーティリティ**: `scripts/lib/task_registry.py`（`register()`, `update_status()`, `get_latest()`, `list_active()`）
- **自動連携**: `/autonomous` の `run-session.sh` がセッション開始/完了時に自動登録・更新
- **環境変数**: `TASK_REGISTRY_PATH` でパスを差し替え可能（テスト用）

---

## 自動パターン推奨

`agent-router.py`（UserPromptSubmit hook）がユーザー入力のキーワードから委譲パターンを自動推奨する。

- **Scheduled キーワード**: 「あとで」「明日」「定期的」「schedule」等 → CronCreate / /loop を推奨
- **Async キーワード**: 「調べて」「リサーチ」「バックグラウンド」「並列」等 → run_in_background / /research を推奨
- **優先順位**: Scheduled > Async（両方マッチした場合は Scheduled を優先）
- **性質**: アドバイザリー（additionalContext で提案するのみ、強制しない）

---

## CC vs Codex: ハーネス政体の違い

> 出典: wquguru/harness-books — 詳細は `references/harness-polity-comparison.md`

Claude Code と Codex は秩序の配置場所が異なる。委譲先の選択に影響する。

| 政体 | 秩序の源泉 | 委譲に適するタスク |
|------|-----------|-------------------|
| **CC (運行時共和制)** | Query Loop の現場判断。動態拼装 | 現場変化が激しいタスク、長会話での軌道修正 |
| **Codex (控制面立憲制)** | 構造化 fragment + policy | 明確な境界を持つ分析・評価、深い推論 |

両者を併用する場合: CC がプラン策定・統合・現場判断を担当し、Codex が構造化された批評・レビューを担当する分業が最も効果的。

---

## Sequential Protocol (Dochkina 2026)

> 出典: Dochkina 2026 "Drop the Hierarchy and Roles" — 25,000+ タスクで実証

「**固定順序 + 役割自律**」のハイブリッドが、集中型 (+14%) と完全自律 (+44%) の両方を上回る（内生性パラドックス）。

### 原則

**事前に役割を割り当てない。ミッション・プロトコル・高能力モデルを与え、役割は自律的に決めさせる。**

### dotfiles での適用

現在の Implicit Coordinator パターンを破棄せず、以下の場面で Sequential 原則を適用する:

| 場面 | 現状 | Sequential 適用 |
|---|---|---|
| `/review` の並列起動 | 親が各レビューアーの焦点を指定 | レビューアーに変更 diff のみ渡し、焦点は自律決定させる |
| `/research` のサブタスク | 親がサブタスクを明示分解 | テーマのみ渡し、調査範囲は自律決定させる |
| EPD フロー | 各フェーズのスコープを親が指定 | フェーズ順序は固定、フェーズ内の作業分担は自律 |

### 適用しない場面

- **安全制約があるタスク**: db-reader の SELECT 制限、safe-git-inspector の読み取り専用 — 役割自律は契約違反リスク
- **弱いモデルへの委譲**: 能力閾値以下では自律性が害になる（下記参照）

---

## 能力閾値に基づく自律度調整

> 出典: 同論文 — Claude Sonnet: 自由形式 +3.5%、GLM-5: 自由形式 -9.6%

モデルの能力に応じて「構造 vs 自律」のバランスを調整する。

| モデル能力 | 自律度 | プロンプト戦略 |
|---|---|---|
| **高** (Claude Opus/Sonnet, DeepSeek, GPT-5.4) | 高い自律 | ミッション + 制約のみ。手順は指定しない |
| **中** (Claude Haiku, GPT-4.1-mini) | 中程度 | ステップ概要 + 判断余地。重要な分岐点のみガイド |
| **低** (小規模 OSS) | 低い自律 | 具体的手順 + テンプレート。判断余地を最小化 |

### 判断基準

```
委譲先モデルは Opus/Sonnet/DeepSeek/GPT-5.4 クラス?
├─ Yes → 役割自律を最大化（Sequential 原則）
└─ No → Haiku/mini クラス?
          ├─ Yes → 手順概要を与え、判断余地は残す
          └─ No → 具体的手順 + テンプレートで構造を最大化
```

### dotfiles での実装

- **Codex (GPT-5.4)**: 高自律。codex-reviewer / codex-plan-reviewer は「何を評価するか」のみ指定、手順は自律
- **Gemini (1M)**: 高自律。gemini-explore は分析テーマのみ渡す
- **Claude サブエージェント**: 高自律。専門エージェントにはミッション + 制約のみ
- **将来の弱モデル委譲時**: 中〜低自律。チェックリスト注入 + 出力テンプレートで構造化

---

## 自発的自己棄却

> 出典: 同論文 — Sequential 協調で 38/60 エージェントが自己判断で不参加。Claude の自己棄却率: 8.6%

サブエージェントが「自分はこのタスクに価値を追加できない」と判断した場合、早期終了する仕組み。

### プロンプトガイドライン

並列レビュー等で複数エージェントを起動する場合、以下の指示をプロンプトに含める:

```
あなたの専門領域に関連する問題が見つからない場合は、
「該当なし — [理由]」と簡潔に報告して早期終了してください。
無理に指摘を生成する必要はありません。
```

### 適用場面

| 場面 | 効果 |
|---|---|
| `/review` の並列レビュー | 関連のないレビューアーが空の指摘を生成するのを防止 |
| `/research` の並列調査 | 情報が見つからないサブタスクが冗長なレポートを返すのを防止 |
| best-of-N | 明らかに失敗した候補が早期終了し、リソース節約 |

### 注意

- Analyze-only 契約のエージェントにのみ適用。Implement 契約では「変更不要」と「見落とし」の区別がつかないため、自己棄却は危険
- 棄却理由を必ず報告させ、親が判断材料として使えるようにする

---

## エージェント障害耐性

> 出典: 同論文 — 完全トポロジーで RI=0.959、エージェント除去から 1 反復で回復

マルチエージェント実行時の障害回復パターン。

### 障害タイプと対応

| 障害 | 症状 | 回復戦略 |
|---|---|---|
| **タイムアウト** | サブエージェントが応答しない | 結果なしとして統合。親が不足部分を補完 |
| **API エラー** | レート制限、モデル障害 | 1回リトライ → 失敗なら代替モデルにフォールバック |
| **品質障害** | 空レスポンス、無関係な出力 | 結果を破棄し、残りの結果で統合 |
| **部分障害** | N 並列中 M 個が失敗 | M/N < 0.5 → 成功分で続行。M/N >= 0.5 → 親に報告して判断を仰ぐ |

### Graceful Degradation 原則

```
全エージェント成功?     → 全結果を統合
一部失敗 (< 50%)?      → 成功分で統合 + 欠落領域を報告
過半数失敗 (>= 50%)?   → ユーザーに報告、リトライ判断を委ねる
全エージェント失敗?     → 親が直接実行にフォールバック
```

### dotfiles での適用

- `/review`: レビューアーの一部がタイムアウトしても、返ってきた結果で統合を完了する
- `/research`: サブタスクの一部が失敗しても、成功分でレポートを生成し、欠落を明示する
- best-of-N: 候補の一部が失敗しても、残りの候補で選択を行う

---

## Anti-patterns

| やりがち | 代わりにやるべき |
|---|---|
| 単純な1ファイル読みに Agent を使う | Read ツールで直接読む |
| 結果が必要なのに Async で起動 | Sync（Agent ツール）を使う |
| 全タスクを Sync で実行して親のコンテキストを圧迫 | 独立タスクは Async に |
| Depth-2 以上の再帰委譲 | Depth-1 を維持、必要なら親が再委譲 |
| 特化エージェントを大量に作る | 汎用 + チェックリスト注入 |
| ユーザー承認なしに Async / Scheduled を起動 | 必ず承認を得てから |
| 並列エージェントに同時にコードを書かせる | 調査・分析は並列可。書き込みは逐次か Teams で協調 |
| ロールでタスクを分割する（planner/implementer/tester） | コンテキスト境界で分割する（最上位原則を参照） |

### 並列コード書き込みの危険性

並列エージェントがコードを同時に書くと、**暗黙の前提が不整合** になる:

- エージェント A が「このフィールドは nullable」と仮定 → エージェント B が「non-null」で実装
- worktree 隔離は物理的衝突を防ぐが、設計上の不整合は防げない
- マージ後に初めて発覚し、デバッグコストが高い

**対策**:
1. 並列書き込みが必要な場合、**shared assumptions** を task_list.md に明記する
2. インターフェース（型定義、API 契約）を先に合意してから並列実行する
3. 可能なら Agent Teams を使い、エージェント間で直接ネゴシエーションさせる

### Shared File Detection Rule

並列エージェントが同一ファイルを編集するリスクを事前に検出・回避する。

**対処パターン:**
1. **直列化**: 該当ファイルへの書き込みを1エージェントに限定し、他は待機
2. **API境界分割**: 共有ファイルをインターフェース境界で分割し、各エージェントが独立部分のみ編集
3. **Read-only 共有**: `package.json`, `go.mod`, `Cargo.lock` 等の manifest は read-only。変更が必要なら直列化キューに入れる

**Session-state 共有ファイル（worktree 並列実行時に特に注意）:**

| ファイル | リスク | 対策 |
|---------|--------|------|
| `~/.claude/session-state` | 複数 worktree が同時書き込み | per-worktree にコピー (copy-on-create) |
| `progress.log` | 複数セッションのログが混在 | `CLAUDE_STATE_DIR` で出力先を worktree-local に override |
| `checkpoint/` | チェックポイントの上書き | per-worktree で独立管理 |
| `stagnation-detector` 状態 | 他セッションのカウントで誤検知 | worktree-local に隔離 |

文書ルールだけでは runner の自動並列実行を守れない。`best-of-n-runner` 等のランナーは `CLAUDE_STATE_DIR` 環境変数でパスを分離すること。

---

## Expert 実行契約

> Qoder Experts Mode の知見: 調整と実行の分離が役割切替オーバーヘッドを排除する。

エージェント起動時に「何ができるか」を明示的に契約として定義する。
各エージェントの実行パラメータは `references/agent-execution-profiles.md` を参照。

### 契約タイプ

| 契約 | 説明 | ツール制限 | 例 |
|---|---|---|---|
| **Analyze-only** | 分析・報告のみ。ファイル変更禁止 | Read, Bash, Glob, Grep のみ | code-reviewer, security-reviewer, test-analyzer |
| **Implement** | 指定スコープ内のみ変更可 | Read, Write, Edit, Bash, Glob, Grep | build-fixer, debugger, test-engineer |
| **Orchestrate** | タスク分解・委譲・統合。直接実装しない | 全ツール（Agent 含む） | triage-router, autoevolve-core |

### 契約の実現方法

dotfiles では Agent ツールの `tools` パラメータ（agent 定義の frontmatter）がそのまま契約として機能する:

- **Analyze-only**: `tools: [Read, Bash, Glob, Grep]` — Write/Edit を持たないため、物理的にファイル変更不可
- **Implement**: `tools: [Read, Write, Edit, Bash, Glob, Grep]` — Agent ツールを持たないため、再委譲不可
- **Orchestrate**: 全ツール利用可能だが、agent 定義内の指示で「直接実装しない」を明示

### 契約違反の検出

ツール制限自体が契約として機能するため、Claude Code のインフラレベルで違反が防止される。
追加の検出機構は不要（YAGNI）。ただし、Orchestrate 契約の「直接実装しない」はソフト制約であり、
agent 定義のプロンプトで遵守を求める。

---

## DAG Orchestration Pattern

> Qoder: 「すべての SWE Agent は非同期並列がデフォルト。依存は DAG で管理」

### 現状の手動 DAG

dotfiles では Unit of Work テーブル（`workflow-guide.md`）の依存列で DAG を表現し、
`/autonomous` スキルが worktree 並列で実行する。

### 自動化の閾値

| Unit 数 | 推奨 | 理由 |
|---|---|---|
| 1-2 | 直接実行 | オーケストレーションのオーバーヘッドが本体を上回る |
| 3-4 | 手動 DAG（現状） | Unit of Work テーブルで十分管理可能 |
| 5+ | 自動 DAG 検討 | 依存チェック + 自動起動が手動管理のコストを下回る |

### 将来の自動化候補

`/autonomous` スキル内で依存チェック + 自動起動を実装する案:

1. `task_list.md` の依存列をパースして DAG を構築
2. 依存が満たされた Unit を自動で worktree 起動
3. 完了通知で後続 Unit をトリガー

**即時実装は不要** — 現状の手動 DAG（3-4 Unit）で十分に機能している。
5+ Unit の L タスクが頻発したら再検討する。

---

## Graph Plasticity Mode（GPM）判定基準

ワークフロー構造をどの程度動的にするか、**最小限の plasticity** を選ぶ。

> 出典: Yue et al. 2026 "From Static Templates to Dynamic Runtime Graphs" §7.1-7.2

### 4 段階スペクトラム

| GPM | 定義 | 判断基準 | dotfiles での例 |
|-----|------|---------|----------------|
| **none** | 固定テンプレートをそのまま実行 | S 規模 + 3 条件成立（制約された演算子空間、信頼できる評価、反復デプロイ） | typo 修正: Edit → Test → Done |
| **select** | 固定スーパーグラフからサブグラフを選択 | タスクは似ているが難易度やツールが異なる | agent-router.py が規模で reviewer 数を選択 |
| **generate** | 実行前にタスク固有のグラフを生成 | タスク種類自体が異なり、異なる構造が必要 | `/autonomous` が DAG を生成し worktree 並列 |
| **edit** | 実行中にグラフ構造を変更 | 部分実行で予期せぬ情報が現れ構造変更が必要 | error-to-codex hook がエラー時にルート変更 |

### 判断フロー

```
タスク異質性は低い?
├─ Yes → 難易度だけが違う? → select（reviewer 数調整等）
│         └─ No → none（固定パイプライン）
└─ No → 実行前に構造を決定できる?
          ├─ Yes → generate（DAG 生成）
          └─ No → edit（実行時適応）
```

### コスト意識

plasticity が高いほど:
- **利点**: 表現力が増し、多様なタスクに対応可能
- **代償**: 検証負荷↑、credit assignment が困難、予算制御が複雑化
- **原則**: edit は select で不十分な場合のみ。generate は select で不十分な場合のみ
