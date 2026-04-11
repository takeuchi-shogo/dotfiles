# Codex Gate Workflow Design

## Summary

ワークフローに Codex Gate（Spec/Plan 批評 + Review 強化）を挿入し、Claude(Opus) の「注意の幅」と Codex(gpt-5.4) の「注意の深さ」を段階別に活用する。既存の Risk Analysis は Plan Gate に統合し、Codex の呼び出しポイントを明確化する。

## Motivation

- Codex プラグイン統合により活用手段が増えたが、ワークフロー上の位置づけが曖昧
- Plan 作成は Opus、批評は Codex という役割分担を明示したい
- Codex レビュー結果がバックグラウンドで流れがちで、指摘が活かされないケースがある
- Risk Analysis が Plan Gate と別段階になっており、二重管理になっている

## Design

### 新ワークフロー全体像

```
┌─ CREATE (Opus) ─────────────────────────────────────────┐
│ Spec 作成（該当時）                                      │
│ Plan 作成                                                │
└──────────────────────────────────────────────────────────┘
          ↓
┌─ CODEX GATE: Spec/Plan 批評 ────────────────────────────┐
│ Spec の抜け漏れ・矛盾・曖昧さ                           │
│ Plan のタスク分解・順序・依存関係の妥当性                │
│ Risk Analysis 統合（セキュリティ・障害モード・競合）     │
│                                                          │
│ → Claude が指摘を精査                                    │
│   → 修正すべき: Claude が自動修正 → 報告 → 再レビュー   │
│   → 迷う: ユーザーに選択肢提示 → ユーザー判断           │
│ → ユーザー承認で次段階へ                                 │
└──────────────────────────────────────────────────────────┘
          ↓
┌─ IMPLEMENT (Claude 主体) ────────────────────────────────┐
│ Plan に沿って実装                                        │
│ [条件付き] 100行超・トークン逼迫 → Codex 委譲           │
│ [将来拡張] タスク並列分担                                │
└──────────────────────────────────────────────────────────┘
          ↓
┌─ CODEX GATE: Review 強化 ───────────────────────────────┐
│ 7 項目検査:                                              │
│   1. Correctness  2. Security  3. Error Handling         │
│   4. Naming & Readability  5. Performance  6. Tests      │
│   7. Plan 整合性（実装が Plan の意図から逸脱していないか）│
│ [セキュリティ/API/DB] adversarial-review 並列起動        │
│                                                          │
│ → Claude が指摘を精査                                    │
│   → 修正すべき: Claude が自動修正 → 報告 → 再レビュー   │
│   → 迷う: ユーザーに選択肢提示 → ユーザー判断           │
│ → ユーザー承認で次段階へ                                 │
│ → 修正差分の再レビューは最大 3 回                        │
└──────────────────────────────────────────────────────────┘
          ↓
┌─ VERIFY → COMMIT ───────────────────────────────────────┐
│ ビルド・テスト・lint 実行確認                            │
│ → /commit                                                │
└──────────────────────────────────────────────────────────┘
```

### Gate 発火条件

| タスク規模 | Spec/Plan Gate | Review Gate |
|-----------|----------------|-------------|
| S 規模    | skip           | xhigh       |
| M 規模    | xhigh          | xhigh       |
| L 規模    | xhigh          | xhigh       |

- reasoning effort は全て `xhigh` で統一。分岐は「Gate を通すか skip するか」のみ
- Codex は常に `read-only` で実行（修正は Claude が行う）

### 修正判断の責務分担

| 判断者 | 条件 | アクション |
|--------|------|-----------|
| Claude が自動修正 | 修正すべきと明確に判断できるもの（重要度問わず） | 修正 → 修正内容をユーザーに報告 → 修正箇所のみ再レビュー |
| ユーザーに判断を委ねる | トレードオフがある・方向性に複数の選択肢がある・確信が持てない | 選択肢を提示 → ユーザーが決定 |

判断基準は Codex の重要度ラベル（CRITICAL/HIGH/MEDIUM/LOW）ではなく、Claude が修正の正しさに確信を持てるかどうか。

### Codex Gate: Spec/Plan 批評の観点

**Spec 批評（Spec がある場合）:**
1. 要件の抜け漏れ・矛盾
2. 受入基準の曖昧さ・測定不能な表現
3. スコープの過大/過小

**Plan 批評:**
1. タスク分解の粒度（大きすぎ・細かすぎ）
2. 依存関係の見落とし
3. 実装順序の妥当性

**Risk Analysis（統合）:**
1. セキュリティリスク（注入、認証バイパス、データ露出）
2. 障害モード（外部サービス障害、タイムアウト）
3. 競合状態・データ整合性
4. 暗黙の前提

### Codex Gate: Review 強化の観点

**標準 7 項目:**
1. Correctness — ロジックエラー、境界値、nil参照
2. Security — 注入、認証バイパス、シークレット漏出
3. Error Handling — 例外処理の落ち、検証不足
4. Naming & Readability — 誤解を招く命名
5. Performance — N+1、不要なアロケーション
6. Tests — エッジケース見落とし、カバレッジ
7. Plan 整合性 — 実装が Plan の意図から逸脱していないか

**追加（セキュリティ/API/DB 変更時）:**
- adversarial-review 並列起動（攻撃シナリオベースの検査）

## 変更対象ファイル

### 改訂

| ファイル | 変更内容 |
|---------|---------|
| `.config/claude/references/workflow-guide.md` | ワークフロー定義改訂。Codex Gate 挿入、Risk Analysis 統合 |
| `.config/claude/rules/codex-delegation.md` | 委譲ルール改訂。Gate 発火条件・reasoning effort 統一 |
| `.config/claude/agents/codex-reviewer.md` | Review Gate 仕様に合わせてプロンプト改訂（Plan 整合性チェック追加） |
| `.config/claude/skills/codex-review/SKILL.md` | Review Gate フロー（自動修正 / ユーザー判断の分岐）を反映 |
| `.config/claude/CLAUDE.md` | ワークフローテーブルの更新 |

### 新規作成

| ファイル | 内容 |
|---------|------|
| `.config/claude/agents/codex-plan-reviewer.md` | Spec/Plan Gate 専用エージェント。Spec 批評 + Plan 批評 + Risk Analysis 統合 |

### 廃止

| ファイル | 理由 |
|---------|------|
| `.config/claude/agents/codex-risk-reviewer.md` | Risk Analysis の観点を `codex-plan-reviewer` に統合 |

### 変更しないもの

- hook — スコープ外（ドキュメント + スキル/エージェントまで）
- `codex-debugger.md` — スコープ外
- `codex-review-issue` スキル — スコープ外
- Codex プラグインスキル（`/codex:review` 等）— 既存のまま共存

## 将来拡張ポイント

### 1. 実装段階の Codex 並列分担
Plan のタスクリストから独立したタスクを識別し、Claude と Codex で並列実装。Gate 構造を壊さず Implement 段階内に委譲判断ロジックを追加する形で拡張可能。

### 2. Spec/Plan Gate の hook 自動化
Plan ファイル書き出し時に自動で Codex Gate を起動する PostToolUse hook。今回はスキル/エージェント内のフロー記述で対応。

### 3. Gate 結果の蓄積・学習
Codex Gate の指摘パターンを `lessons-learned.md` に蓄積し、繰り返し出る指摘を Spec/Plan テンプレートにフィードバック。AutoEvolve の改善サイクルに接続。
