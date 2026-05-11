---
status: active
last_reviewed: 2026-04-23
---

# Integration Plan: Stripe Minions Patterns

## Overview

| Field | Value |
|-------|-------|
| Source | https://blog.bytebytego.com/p/how-stripes-minions-ship-1300-prs |
| Analysis | `docs/research/2026-03-19-stripe-minions-analysis.md` |
| Total Tasks | 5 |
| Estimated Size | L |

## Design Philosophy

Stripe の Minions から学ぶ核心: **「エージェントの成功は基盤インフラで決まる」**。
個々のパターンをプロダクト横断で使えるスキル・リファレンス・スクリプトとして構築する。
dotfiles で試験し、任意のプロジェクトに持ち込める形にする。

## Tasks

### Task 1: Blueprint Pattern — タスク型別ワークフロー DAG

| Field | Value |
|-------|-------|
| Files | `references/blueprint-pattern.md`, skill metadata convention |
| Dependencies | なし（他タスクの基盤） |
| Size | M |

**概要:**
Stripe の Blueprint = 「決定論ノード（lint, push, test）とエージェントループ（実装, CI修正）を組み合わせた DAG」。
現在のスキルは手順を自然言語で記述するが、どのステップが決定論的でどのステップがエージェント裁量かが曖昧。

**Changes:**
- `references/blueprint-pattern.md` を作成: Blueprint の概念、設計ガイド、実例
- Blueprint の構造定義:
  ```yaml
  blueprint:
    name: "bug-fix"
    nodes:
      - { id: analyze, type: agentic, tools: [Read, Grep, Glob] }
      - { id: implement, type: agentic, tools: [Edit, Write] }
      - { id: lint, type: deterministic, command: "task lint" }
      - { id: test, type: deterministic, command: "task test" }
      - { id: fix-failures, type: agentic, max_iterations: 2 }
      - { id: pr, type: deterministic, command: "gh pr create" }
    edges:
      - [analyze, implement]
      - [implement, lint]
      - [lint, test]
      - [test, fix-failures, { condition: "test.failed" }]
      - [fix-failures, lint]
      - [test, pr, { condition: "test.passed" }]
  ```
- 3つの標準 blueprint を定義: `bug-fix`, `feature`, `refactor`
- `/autonomous` スキルが blueprint を参照してセッション実行する接続点を設計

**設計判断:**
- Blueprint は YAML/frontmatter で宣言的に記述（手続き的なスクリプトではない）
- スキルの `metadata` セクションに `blueprint` フィールドを追加するか、独立した `blueprints/` ディレクトリにするか → 独立ディレクトリ推奨（スキルと1:1ではないため）
- 実行エンジンは Phase 1 では不要。まずは「設計ドキュメント + 人間/エージェントが参照する仕様」として機能させる

---

### Task 2: Task-scoped Tool Subsets — Blueprint 連動ツール制限

| Field | Value |
|-------|-------|
| Files | `references/tool-scoping-guide.md`, `scripts/policy/tool-scope-enforcer.py` (new), `mcp-audit.py` (enhance) |
| Dependencies | Task 1 (Blueprint 定義) |
| Size | M |

**概要:**
Stripe は 500 ツールから「タスクに必要な最小限」を選択。全ツールを渡すと認知負荷とトークンが爆発する。
現在の `mcp-audit.py` はブランケットポリシー。Blueprint のノードごとにツールセットを制限する。

**Changes:**
- `references/tool-scoping-guide.md`: ツールスコーピングの設計ガイド
  - なぜ制限するか（トークン節約、安全性、再現性）
  - スコープの粒度（blueprint レベル / ノードレベル / スキルレベル）
  - 実装パターン: `allowed-tools` in skill metadata → `run-session.sh` の `--allowedTools` に反映
- `scripts/policy/tool-scope-enforcer.py` (PreToolUse hook):
  - 現在のスキル/blueprint コンテキストを検出
  - `allowed-tools` を超えるツール使用時に警告（block ではなく warn）
  - `/autonomous` のヘッドレスセッションでは `--allowedTools` で物理的に制限
- `mcp-audit.py` 拡張: スキル metadata の `mcp-tools` フィールドを参照

**設計判断:**
- Interactive セッションでは warn のみ（block するとUXが悪い）
- Unattended セッション（`claude -p`）では `--allowedTools` で物理的に制限（Stripe と同等）
- スキルの既存 `allowed-tools` フィールドを活用（新しい概念を増やさない）

---

### Task 3: Graduated Completion — 部分完成ハンドバック

| Field | Value |
|-------|-------|
| Files | `scripts/policy/completion-gate.py` (enhance), `references/graduated-completion.md` |
| Dependencies | なし（独立） |
| Size | M |

**概要:**
Stripe: 「部分的に正しい PR でも価値がある」。現在の completion-gate は MAX_RETRIES 到達で「停止を許可」するだけ。
「何ができて何ができなかったか」を構造化して人間にハンドバックする仕組みが必要。

**Changes:**
- `references/graduated-completion.md`: Graduated Completion の設計ガイド
  - 3段階: Full（全テスト通過）→ Partial（一部成功 + 失敗レポート）→ Blocked（着手不能）
  - ハンドバックレポートのフォーマット
  - いつ Partial を許容するか（unattended agent / blueprint 定義で制御）
- `completion-gate.py` 拡張:
  - MAX_RETRIES 到達時、「停止を許可」ではなく **ハンドバックレポートを生成**
  - レポート内容: 完了タスク、失敗テスト、推定原因、推奨アクション
  - `additionalContext` にレポートを注入 → エージェントが PR description に含める
  - 新環境変数 `COMPLETION_MODE`: `strict`（従来）/ `graduated`（部分完成許可）
- `/autonomous` のセッション終了時に graduated completion を活用:
  - 全タスク完了でなくても、完了分の PR を作成して通知

**設計判断:**
- デフォルトは `strict`（現在の動作を壊さない）
- `/autonomous` や unattended blueprint では `graduated` をデフォルト
- Partial の場合、PR の title に `[WIP]` を付加し、description に残作業を明示

---

### Task 4: Unattended Pipeline — E2E 自律実行パイプライン

| Field | Value |
|-------|-------|
| Files | `skills/autonomous/SKILL.md` (enhance), `skills/autonomous/scripts/run-session.sh` (enhance), `skills/autonomous/templates/pr-template.md` (new), `references/unattended-pipeline.md` |
| Dependencies | Task 1 (Blueprint), Task 3 (Graduated Completion) |
| Size | L |

**概要:**
`/autonomous` を Stripe Minions 級の E2E パイプラインに進化させる:
`タスク受信 → Blueprint 選択 → 隔離環境 → 実行ループ → PR 作成 → 通知`

**Changes:**
- `references/unattended-pipeline.md`: パイプライン設計ガイド
  - Stripe Minions のアーキテクチャ概要
  - 当セットアップでの実現方法
  - 将来の拡張点（Slack webhook, GitHub Actions trigger）
- `/autonomous` スキル拡張:
  - **Blueprint 参照**: タスク分析時に最適な blueprint を選択
  - **PR Delivery Step**: 全セッション完了後（または graduated completion 時）に自動 PR 作成
  - `run-session.sh` に PR 作成ステップを追加:
    ```bash
    # Session loop 完了後
    if [[ "$FINAL_STATUS" == "completed" || "$COMPLETION_MODE" == "graduated" ]]; then
      gh pr create --title "$PR_TITLE" --body-file "$PR_BODY"
    fi
    ```
  - PR テンプレート: `templates/pr-template.md` — progress.md から自動生成
- **通知**:
  - `run-session.sh` 完了時に macOS notification (`osascript`) or stdout メッセージ
  - 将来拡張: Slack webhook, GitHub Actions

**設計判断:**
- 外部トリガー（Slack bot 等）は本プランのスコープ外。パイプライン内部を先に固める
- PR 作成は `gh pr create` で統一（GitHub CLI 依存は許容）
- 通知は最小限（ターミナル出力 + macOS notification）から始める

---

### Task 5: Selective Test Running — 変更関連テストのみ実行

| Field | Value |
|-------|-------|
| Files | `scripts/policy/completion-gate.py` (enhance), `scripts/lib/test_selector.py` (new) |
| Dependencies | なし（独立） |
| Size | M |

**概要:**
Stripe は 300万+ テストから関連サブセットのみ実行。現在の completion-gate は全テスト実行。
変更ファイルから関連テストを特定し、まず関連テストのみ実行 → 通過したら全テストも実行、の2段階にする。

**Changes:**
- `scripts/lib/test_selector.py` (新規):
  - `git diff --name-only HEAD` で変更ファイルを取得
  - `_TEST_FILE_MAPPINGS`（既に completion-gate.py にある）を活用してテストファイルを特定
  - 言語別のテスト実行コマンドを生成:
    - Go: `go test ./path/to/changed/package/...`
    - Python: `pytest path/to/test_file.py`
    - Node: `jest --findRelatedTests path/to/changed.ts`
    - Rust: `cargo test --test specific_test`
  - フォールバック: テストファイル特定不能 → 全テスト実行
- `completion-gate.py` 拡張:
  - Step 1: `test_selector.py` で関連テストのみ実行（高速フィードバック）
  - Step 2: 関連テスト通過 → 全テスト実行（回帰チェック）
  - Step 1 で失敗 → 即座にフィードバック（全テスト実行をスキップ）
  - 環境変数 `SELECTIVE_TESTS`: `on`（デフォルト）/ `off`（全テスト強制）

**設計判断:**
- 関連テスト特定は「ベストエフォート」。特定不能なら全テスト実行にフォールバック
- 関連テスト通過後の全テスト実行は、プロジェクト規模が大きい場合のみ有効（小規模なら両方一瞬）
- `test_selector.py` は独立ライブラリとして `scripts/lib/` に配置（他のスクリプトからも使える）

---

## Task Dependencies

```
Task 1 (Blueprint) ─────┬──→ Task 2 (Tool Subsets)
                         └──→ Task 4 (Unattended Pipeline)
Task 3 (Graduated) ─────────→ Task 4 (Unattended Pipeline)
Task 5 (Selective Tests) ────→ (独立)
```

推奨実行順序:
1. Task 1 (Blueprint) + Task 3 (Graduated) + Task 5 (Selective Tests) — 並列可能
2. Task 2 (Tool Subsets) — Task 1 完了後
3. Task 4 (Unattended Pipeline) — Task 1 + 3 完了後

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Blueprint が過度に複雑になる | 誰も使わない設計ドキュメントになる | Phase 1 は宣言的仕様のみ。実行エンジンは作らない |
| Tool scoping が既存ワークフローを壊す | Interactive セッションの UX 劣化 | Interactive は warn のみ、block は unattended のみ |
| Graduated completion で品質低下 | 不完全な PR がマージされる | PR に [WIP] 付加 + 残作業明示。マージは人間が判断 |
| Selective tests が重要テストを漏らす | 回帰バグの見逃し | 関連テスト通過後に全テストも実行する2段階方式 |
| `/autonomous` の複雑化 | メンテナンス困難 | Blueprint 参照は optional。既存フローは壊さない |

## Execution

| Size | Approach |
|------|----------|
| L | docs/plans/ に保存 → 新セッションで段階実行 |

推奨: Task 1, 3, 5 を最初のセッションで並列実行。Task 2, 4 を次のセッションで実行。
