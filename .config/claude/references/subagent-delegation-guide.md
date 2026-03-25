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

### Agent Teams が有効なシナリオ

| シナリオ | なぜサブエージェントでは不十分か | Teams の利点 |
|---|---|---|
| Frontend + Backend 同時開発 | API 契約の変更を後からマージで発見 | Backend が API を変えたら Frontend に即通知 |
| 大規模リファクタ（依存あり） | task_list.md の静的依存では中間発見を反映不可 | 先行タスクの発見が後続の approach を動的に変更 |
| EPD フロー | Spec → Build → Review の逐次実行はボトルネック | Product/Engineering/Design が並走し即フィードバック |

### Teams のライフサイクル

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

### Teams の Anti-patterns

| やりがち | 代わりにやるべき |
|---|---|
| 独立タスクに Teams を使う | サブエージェント（コンテキスト圧縮が効く） |
| 全員が同じファイルを編集 | インターフェースを先に合意、実装は分離 |
| Lead を経由せず teammate 同士だけで完結 | Lead が最終統合と品質判断を担う |
| Teams 内で再帰的に Teams を作る | 1レベルの Teams に留める |

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
