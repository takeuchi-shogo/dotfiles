---
source: https://nyosegawa.com/posts/coding-agent-workflow-2026/
analysis: docs/research/2026-03-25-coding-agent-workflow-2026-analysis.md
codex-review: Codex risk review 2026-03-25. Critical→0, High→2, Medium→7
status: task3.3-complete
created: 2026-03-25
revised: 2026-03-26
---

# 統合プラン: Coding Agent Workflow 2026 (v2 — Codex レビュー反映)

全14項目を3フェーズに分割。Codex リスクレビューで High 2件・Medium 7件を検出し、以下を修正:
- Task 2.2: AGENTS.md 60行制限を削除（現状108行で不整合）。doc-garden-check.py との統合設計
- Task 2.3: ハードコードリスト→.mcp.json から動的取得に変更
- Task 2.1: 既存 harness-rationale.md 4分類からの移行計画を追加
- Task 3.1: session-state isolation を文書ルールから実装レベルに昇格
- Task 3.3: heartbeat + フォールバック通知を追加
- 全 Phase 2+: テスト計画を各タスクに追記

## Phase 1: ドキュメント強化 (S規模 × 7, 同一セッションで実行可能)

### Task 1.1: FM-020 Probabilistic Cascade 追加 [S]
- **ファイル**: `references/failure-taxonomy.md`
- **変更**: FM-020 追加。定義: 各ステップの成功確率 p が連鎖すると p^n で減衰。対策: タスク分割粒度を「1ステップ5分以内」に保つ
- **依存**: なし

### Task 1.2: 共有ファイル直列化ルール追加 [S]
- **ファイル**: `references/subagent-delegation-guide.md`
- **変更**: Task Parallelizability Gate に「Shared File Detection」ルール追加:
  - 同一ファイルを複数エージェントが編集する場合は直列化 or API境界での分割を強制
  - **[Codex H2 対応]** session-state 共有ファイル (`~/.claude/session-state`, `progress.log`, `checkpoint/`) を Shared File リストに明示。worktree 起動時は per-worktree コピー or 無効化を要求
- **依存**: なし

### Task 1.3: Vercel 実証データ追記 [S]
- **ファイル**: `references/compact-instructions.md`
- **変更**: Progressive Disclosure の根拠として Vercel Next.js 16 実証データ追記 (8KB AGENTS.md = 100% パス率、Skills リトリーバル 53% を 47pt 上回る)
- **依存**: なし

### Task 1.4: Agent-Native コード設計ガイド新規作成 [M]
- **ファイル**: `references/agent-native-code-design.md` (新規)
- **変更**: 記事の5原則を統合:
  1. Grep-able命名 (named export強制、一貫したエラー型)
  2. Collocated Tests (ソース隣接 `__tests__/`, 一貫した命名)
  3. 機能単位モジュール化 (水平→垂直スライス)
  4. テスト=報酬信号 (テストなしコードパス=品質保証不能)
  5. API境界明確化 (型定義・API契約を先に合意)
- **依存**: なし

### Task 1.5: モデル切替提案の明示化 [S]
- **ファイル**: `references/cross-model-insights.md`
- **変更**: 「Model Musical Chairs」パターンを明文化。stagnation-detector.py の同種エラー反復検出後に、error-to-codex.py による自動切替に加え、Gemini への切替も選択肢として記述
- **依存**: なし

### Task 1.6: Context Rot 1M 対応注記 [S]
- **ファイル**: `references/resource-bounds.md`
- **変更**: Context Pressure Levels に「1M コンテキスト利用時の調整値」を注記。Opus 4.6 の MRCR v2 78.3% を根拠に、200K 前提の閾値と 1M 利用時の推奨値を併記
- **依存**: なし

### Task 1.7: Linear Walkthrough ルール追加 [S]
- **ファイル**: `references/comprehension-debt-policy.md`
- **変更**: M/L 規模で AI 生成コードの Linear Walkthrough 生成を推奨に追加。「What/Why/Risk」3点に加え、処理フローの step-by-step 説明を含む Walkthrough セクションを Design Rationale に追加
- **依存**: なし

## Phase 2: ツール強化 (M規模 × 4)

### Task 2.1: Factory.ai lint カテゴリ統合ドキュメント [M]
- **ファイル**: `references/lint-category-map.md` (新規)
- **変更**:
  - **[Codex M4 対応]** `harness-rationale.md` の既存4分類を起点に、Factory.ai 7カテゴリ (Grep-ability, Glob-ability, Architectural Boundaries, Security & Privacy, Testability, Observability, Documentation) への移行マッピングを作成
  - 既存 lint ルール (biome, oxlint, ruff, gofmt) を7カテゴリで再分類
  - `harness-rationale.md` の旧分類セクションに deprecation notice + 新ドキュメントへの参照を追記
- **依存**: Task 1.4 (Grep-able 原則を参照) + `harness-rationale.md` 既存4分類の確認
- **テスト**: 旧→新の分類マッピングに欠落がないことを目視確認

### Task 2.2: Lefthook pre-commit ガード拡張 [M] ← Codex H1, M1, M2 反映で大幅修正
- **ファイル**: `lefthook.yml`, 新規スクリプト1本, `doc-garden-check.py` 拡張
- **変更**:
  1. `scripts/policy/check-claudemd-lines.sh` — **CLAUDE.md のみ 150行チェック** (Warning)
     - ~~AGENTS.md 60行~~ → 削除。現状 root AGENTS.md=108行、.codex/AGENTS.md=134行で不整合
  2. パス実在チェック → **既存 `doc-garden-check.py` を拡張** (新規スクリプトではなく)
     - `doc-garden-check.py` に CLAUDE.md/AGENTS.md のパス参照チェックモードを追加
     - 既知の誤検知パターン (`cross-model-insights.md`, `tool-scoping-guide.md` のインライン記述) をスキップリストで管理
     - pre-commit ではなく **PostToolUse (Write|Edit) で差分のみチェック** に変更（全ファイルスキャンは重すぎる）
  3. docs 鮮度チェック → **既存 `doc-garden-check.py` の 30日閾値に統合**
     - ~~5日で警告~~ → 削除。`last-validated:` = 0件、5日超 = 175件で常時警告化するため
     - 代わりに `doc-garden-check.py` の既存30日閾値を活用。pre-commit ではなく定期実行 (daily-health-check) で検出
- **依存**: なし
- **テスト**: `doc-garden-check.py` の dry-run モードで誤検知件数を確認。CLAUDE.md 行数チェックを手動実行で検証

### Task 2.3: MCP 既知サーバー動的検証 [M] ← Codex M3 反映で修正
- **ファイル**: `scripts/policy/mcp-audit.py`
- **変更**:
  - ~~ハードコードリスト~~ → `.mcp.json` + `settings.json` の `enabledMcpjsonServers` から既知リストを動的取得
  - 既存の mcp-audit.py L39, L189 の部分実装を統合・整理
  - サーバー名の正規化 (`discord` → `plugin_discord_discord` 等の mapping テーブル)
  - リスト外サーバーの初回利用時に Warning 出力
- **依存**: なし
- **テスト**: 現行 MCP サーバー (context7, alphaxiv, playwright, obsidian, brave-search, discord) すべてが既知判定されることを確認

### Task 2.4: TDD Guard hook 追加 [M] ← Codex M (hook順序) 反映で修正
- **ファイル**: `settings.json` (hook追加), `scripts/policy/tdd-guard.py` (新規)
- **変更**:
  - PreToolUse で Edit/Write を検出し、対象が実装ファイル (*.go, *.ts, *.tsx, *.py) かつ対応テストが存在しない場合に Warning
  - **[Codex 対応]** 他 hook の結果に一切依存しない独立判断設計。環境変数 `TDD_MODE=1` のときのみ有効化
  - `TDD_MODE` ライフサイクル: `superpowers:tdd` スキル発動時に自動 set、スキル完了時に unset。手動 `/tdd on|off` でも切替可能
  - **[Codex 対応]** settings.json 変更はセッション区切りで適用（compact-instructions.md §cache invalidation 準拠）
- **依存**: なし
- **テスト**: TDD_MODE=0 時に hook が発火しないこと + TDD_MODE=1 時にテストなし実装ファイル編集で Warning が出ることを確認

## Phase 3: 新機能 (L規模 × 3, 新セッション推奨)

### Task 3.1: Best-of-N 実行時自動化スクリプト [L] ← Codex H2 反映で修正
- **ファイル**: `scripts/runtime/best-of-n-runner.sh` (新規), `references/best-of-n-guide.md` (新規)
- **変更**:
  - N 個の worktree を自動生成し、同一プロンプトで並列実行→テスト結果を比較→最良を選択
  - 成功確率モデル (1-(1-p)^N) をガイドに記載
  - **[Codex H2 対応]** session-state isolation を実装レベルで保証:
    - worktree 起動時に `~/.claude/session-state` を per-worktree にコピー (copy-on-create)
    - `checkpoint_manager.py`, `stagnation-detector.py` の出力先を worktree-local に override (env: `CLAUDE_STATE_DIR`)
    - `session-load.js` が worktree 内の state を優先参照するよう分岐
  - Lock file pattern: `package.json`, `go.mod`, `Cargo.lock` 等の共有 manifest は read-only。変更が必要な場合は直列化キューに入れる
- **依存**: Task 1.2 (共有ファイル直列化ルール)
- **テスト**: 2-worktree での同時実行テスト。session-state が互いに干渉しないことを検証

### Task 3.2: GitHub Agentic Workflows 基盤 [L]
- **ファイル**: `.github/workflows/` (新規), `/setup-background-agents` スキル活用
- **変更**:
  - Continuous Triage (Issue自動ラベル) + Continuous Quality (CI失敗→修正PR提案) の2ワークフロー
  - **[Codex H3 対応]** `/dev-cycle` との境界: `/dev-cycle` = ローカル手動起点、GitHub Workflows = CI/CD 自動起点。重複する機能は `/dev-cycle` 側から GitHub Actions を呼び出す形で統合
- **依存**: なし (ただし /setup-background-agents スキルの活用を推奨)
- **テスト**: act (GitHub Actions ローカルランナー) で dry-run

### Task 3.3: Patrol Agent + 通知集約 [L] ← Codex M (silent failure) 反映で修正
- **ファイル**: `scripts/runtime/patrol-agent.sh` (新規), `/schedule` スキル活用
- **変更**:
  - cron で定期実行。活動中セッションの停止検出→Discord/Slack に集約通知
  - cmux-notify.sh との統合
  - **[Codex 対応]** silent failure 対策:
    - heartbeat ファイル (`~/.claude/patrol-heartbeat`) を毎実行で更新。daily-health-check.sh で heartbeat の鮮度を検証
    - 通知失敗のフォールバック: Discord 失敗時→ローカル通知 (osascript) → ログファイル。`|| true` による握り潰しを禁止
    - `last_success` タイムスタンプで連続失敗を検出
- **依存**: Task 3.2 が先にあると GitHub Actions 経由も可能
- **テスト**: 通知先を mock した dry-run + heartbeat 更新の確認

## 実行順序

```
Phase 1 (即実行可能, 並列)
├── Task 1.1 FM-020 [S]
├── Task 1.2 共有ファイル直列化 + session-state リスト [S]
├── Task 1.3 Vercel データ [S]
├── Task 1.4 Agent-Native ガイド [M]
├── Task 1.5 モデル切替 [S]
├── Task 1.6 1M 対応注記 [S]
└── Task 1.7 Linear Walkthrough [S]

Phase 2 (Phase 1 完了後)
├── Task 2.1 lint カテゴリ統合 [M] → depends: 1.4, harness-rationale.md
├── Task 2.2 Lefthook ガード (CLAUDE.md行数のみ) + doc-garden-check.py 拡張 [M]
├── Task 2.3 MCP 動的検証 [M]
└── Task 2.4 TDD Guard [M]

Phase 3 (新セッション, /rpi で実行)
├── Task 3.1 Best-of-N + session-state isolation [L] → depends: 1.2
├── Task 3.2 GitHub Workflows [L]
└── Task 3.3 Patrol Agent + heartbeat [L]
```

## Codex レビュー対応表

| Codex 指摘 | 重大度 | 対応タスク | 対応内容 |
|-----------|--------|-----------|---------|
| AGENTS.md 60行制限が現状108行で不整合 | High | 2.2 | 削除。CLAUDE.md 150行のみ |
| Best-of-N の session-state 共有が文書ルールでは防げない | High | 1.2, 3.1 | session-state isolation を実装 (CLAUDE_STATE_DIR) |
| check-docs-freshness が常時警告化 (175件) | Medium | 2.2 | doc-garden-check.py の30日閾値に統合 |
| check-broken-pointers の誤検知 | Medium | 2.2 | doc-garden-check.py 拡張 + スキップリスト |
| MCP 既知リストがハードコードで drift | Medium | 2.3 | .mcp.json + settings.json から動的取得 |
| 既存4分類との移行計画なし | Medium | 2.1 | harness-rationale.md からの移行マッピング |
| PreToolUse hook 順序保証なし | Medium | 2.4 | 独立判断設計 + TDD_MODE ライフサイクル明確化 |
| Patrol Agent silent failure | Medium | 3.3 | heartbeat + フォールバック通知 |
| Phase 2+ テスト計画欠落 | Medium | 全 Phase 2/3 | 各タスクにテスト項目を追記 |
