# Review Loop Patterns

反復レビューループ、定期スコアリング、ラベル駆動パイプラインの実装パターン集。

出典:
- _mkazutaka "Ralph Loop からはじめるハーネスエンジニアリング" (2026-04-02)
- 加藤 (Aicon) "Issue から AI が動き、人間の役割は要件定義だけになった" (2026-04-02)

## 1. Ralph Loop — Agent + Command レビューループ

エージェントの「問題なし」誤判定を防ぐため、レビューアAgent が品質基準を満たすまで自動的にループさせるパターン。

### 仕組み

```
while (not APPROVED && iterations < max):
  1. フィードバックファイル確認 → 指摘に対応
  2. タスク実行 & 成果物保存
  3. テスト実行
  4. レビューア Agent にレビュー依頼
  5. フィードバック読み込み
  6. APPROVED → COMPLETE 出力 → 脱出
  7. 非承認 → 修正継続
```

### 実装例: Agent 定義 + Command

**レビューア Agent** (`.claude/agents/e2e-reviewer.md`):
```yaml
---
name: e2e-reviewer
description: E2Eテストのコードレビュー実行
tools: Read, Grep, Glob, Bash
model: opus
---

## レビュー基準
1. テスト実行確認 — 全テストが pass すること
2. ユーザーストーリー検証 — 主要フローが網羅されていること
3. エラーハンドリング確認 — 異常系の処理が適切であること
4. セキュリティ検査 — 認証・認可のテストが含まれること

## 出力
- APPROVED: 全基準を満たす場合
- フィードバック: .temp/review-feedback.md に指摘を書き出す
```

**Command** (`.claude/docs/commands/run-e2e-review-ralph.md`):
```
/ralph-loop:ralph-loop "
$ARGUMENTS

## 手順
1. .temp/review-feedback.md 確認と対応
2. タスク実行と成果物保存
3. テスト実行と確認
4. e2e-reviewer エージェントへレビュー依頼
5. フィードバック読み込み
6. APPROVED 表示で <promise>COMPLETE</promise> 出力
7. 非承認時は修正継続
" --completion-promise "COMPLETE" --max-iterations 100
```

### 既存ハーネスとの関係

| 仕組み | 役割 | Ralph Loop との違い |
|--------|------|-------------------|
| `completion-gate.py` | Stop 時のテスト実行ゲート | 1回きり。ループは MAX_RETRIES=2 |
| `ralph-loop` プラグイン | コマンド → Agent の反復ループ | 100回までループ可能。レビューア Agent 統合 |
| `/loop` スキル | 定期的なプロンプト反復実行 | 時間間隔ベース。品質基準での脱出ではない |

**使い分け**: 品質基準を満たすまでの反復 → `ralph-loop`。定期ポーリング → `/loop`。

## 2. 定期スコアリング & 自動リファクタ Issue 化

コードベースを定期的に AI が評価し、スコアが低い箇所を自動で Issue 化するパターン。

### 6 観点スコアリング

| 観点 | 評価内容 |
|------|---------|
| アーキテクチャ | モジュール分離、依存関係の健全性 |
| コード品質 | 可読性、命名、複雑度 |
| テスト | カバレッジ、テスト設計の質 |
| セキュリティ | OWASP Top 10、認証・認可 |
| パフォーマンス | N+1、不要な再レンダリング、メモリリーク |
| 運用性 | ログ、監視、エラーハンドリング |

### 実装パターン

```yaml
# GitHub Actions: 週次スコアリング
on:
  schedule:
    - cron: "0 2 * * 1"  # 毎週月曜 2:00 UTC
  workflow_dispatch: {}

jobs:
  scoring:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run scoring audit
        run: |
          claude -p "$(cat <<'PROMPT'
          コードベースを以下の6観点で 1-10 のスコアで評価してください:
          1. アーキテクチャ  2. コード品質  3. テスト
          4. セキュリティ   5. パフォーマンス 6. 運用性

          スコアが 5 以下の箇所について:
          - 問題の具体的な場所 (file:line)
          - 改善提案
          - 推定工数 (S/M/L)
          を JSON 形式で出力してください。
          PROMPT
          )" --output-format json > scores.json

      - name: Create issues for low scores
        run: |
          jq -c '.findings[] | select(.score <= 5)' scores.json | while read finding; do
            TITLE=$(echo "$finding" | jq -r '.title')
            BODY=$(echo "$finding" | jq -r '.body')
            LABEL=$(echo "$finding" | jq -r '.category')
            gh issue create --title "$TITLE" --body "$BODY" --label "$LABEL,auto-refactor"
          done
```

### 既存ハーネスとの接続

- `/audit` スキル: 手動でスコアリング相当の監査を実行。定期実行テンプレートを追加することで自動化。
- `/schedule` スキル: remote trigger でスケジュール実行可能。

## 3. ラベル駆動 Agent バトンリレー

GitHub ラベルをトリガーに、Agent 間が自動的にバトンを渡し合うパターン。

### 設計原則

1. **細粒度分解**: 各 Agent が 1 ステップだけ確実にこなせる粒度に分割
2. **ラベル = 状態遷移**: Agent 完了時に次ステップのラベルを付与 → 次の Agent が起動
3. **GitHub で可視化**: すべてを Issue/PR 上で完結させ、進行状況を可視化

### 典型的なフロー

```
[Issue 作成]
  ↓ label: needs-requirements
[要件定義 Agent] → 質問を Issue コメントに投稿
  ↓ 人間が回答 → label: requirements-done
[設計 Agent] → 設計書を PR で作成
  ↓ label: design-done
[タスク分割 Agent] → サブ Issue を自動生成
  ↓ label: ready-to-implement
[実装 Agent] → コード実装 + PR 作成
  ↓ label: needs-review
[レビュー Agent] → 4 カテゴリレビュー
  ↓ label: review-passed
[自動マージ Agent] → CI 通過後にマージ
```

### Agent カタログ（Aicon 21体から抽出した汎用パターン）

| カテゴリ | Agent | 役割 |
|---------|-------|------|
| **設計系** | requirements-agent | 要件定義の壁打ち・質問生成 |
| | detailed-design-agent | 設計書作成・PR分割計画 |
| | task-split-agent | 実装サブタスク自動生成 |
| **実装系** | implement-agent | コード実装・テスト・PR作成 |
| | fix-ci-agent | CI失敗の自動分析・修正 |
| | fix-conflict-agent | マージコンフリクト自動解消 |
| **レビュー系** | auto-review-agent | 4カテゴリコードレビュー |
| | review-fix-agent | レビュー指摘の自動修正 |
| | impact-analysis-agent | PR変更の影響分析 |
| **運用系** | stuck-monitor-agent | パイプライン停滞の検知・回復 |
| | auto-merge-agent | CI通過後の自動マージ |
| | unused-code-agent | 週次の不要コード検知 |

### setup-background-agents との接続

`/setup-background-agents` スキルでプロジェクトに適用する際、上記カタログから必要な Agent を選択し、テンプレートを生成する。

## 4. Closed Loop Chain — ステップ間状態ファイル連鎖

個別の cron / スキル / hook を「チェーン」として接続し、各ステップが前ステップの出力を確認してから実行するパターン。

出典: "I Stopped Collecting Agent Skills. Started Wiring Them Into Loops." (2026-04)

### Three Rings（ループの3要素）

テンプレート（1回使って終わり）をループ（回るたびに改善）に変えるには3要素が必要:

| Ring | 役割 | 当ハーネスでの実装 |
|------|------|-------------------|
| **Scheduling** | タイミングの自動化 | CronCreate, `/schedule`, `/loop`, GitHub Actions cron |
| **Memory** | 結果と教訓の永続化 | session-trace-store, memory system, checkpoint |
| **Feedback** | 出力と人間編集の diff からルール更新 | continuous-learning, `/improve` (output-diff カテゴリ) |

### チェーン設計原則

1. **Status file 駆動**: 各ステップは出力を固定パスのファイルに書く。次ステップはそのファイルの存在・内容を確認してから実行する
2. **冪等性**: 同じ入力で複数回実行しても結果が変わらない。完了済みステップは再実行しない
3. **障害時の再起動**: チェーンの途中で失敗しても、次の cron トリガーで未完了ステップから再開する
4. **人間介入ポイント**: チェーン内に明示的な承認ステップを設け、完全自動化を避ける

### チェーン例: 日次改善ループ

```
[cron: 毎晩]
  session-trace-store → traces/*.jsonl (status: logged)
    ↓ 読み取り
  /improve Analyze → improvement-candidates.md (status: analyzed)
    ↓ 読み取り
  /improve Propose → autoevolve branch (status: proposed)
    ↓ 人間レビュー
  merge or revert (status: merged | reverted)
    ↓ 結果記録
  experiment_tracker → experiments.jsonl (status: measured)
```

### 既存ハーネスとの接続

| 既存の仕組み | チェーンでの役割 |
|-------------|----------------|
| `session-trace-store.py` | Step 0: raw データ生成 |
| `contrastive-trace-analyzer.py` | Step 1: diff 分析・パターン抽出 |
| `/improve` | Step 2-3: 改善提案・実装 |
| `experiment_tracker.py` | Step 4: 効果測定・記録 |
| `continuous-learning` | リアルタイム補完（バッチ処理の間を埋める） |
