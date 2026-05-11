---
status: active
last_reviewed: 2026-04-23
---

# autocontext v2 知見の統合プラン

> Source: `docs/research/2026-03-19-autocontext-product-analysis.md`
> 前回プラン: `docs/plans/paused/2026-03-18-autocontext-integration.md`（Task 1,3,4 実装済み）
> 規模: L（8-10ファイル変更）
> Status: **completed**
> 完了日: 2026-03-19

## 概要

autocontext 製品版記事から3つの新知見を AutoEvolve エコシステムに統合する。
前回プランの未実装分（Task 2: 次元別レビュースコア）も合わせて完了させる。

## 依存関係

```
Task A (次元別レビュースコア) ← 独立
Task B (ロールバック改善ゲート) ← 独立
Task C (Tournament 型並列スパイク) ← Task A に依存（スコア比較に使用）、Task B に依存（敗者のロールバック）
```

→ Task A, B は並列実行可能。Task C は A+B 完了後。

---

## Task A: 次元別レビュースコア（前回プラン Task 2 の実装）

### 目的

code-reviewer / codex-reviewer の出力に5次元スコアを追加し、弱点の定量追跡を可能にする。

### 変更ファイル

| ファイル | 変更内容 | サイズ |
|---------|---------|--------|
| `.config/claude/agents/code-reviewer.md` | 出力フォーマットに Review Scores セクション追加 | S |
| `.config/claude/agents/codex-reviewer.md` | 同上 | S |
| `.config/claude/references/review-dimensions.md` | 新規: 5次元の定義・重み・採点基準 | S |
| `.config/claude/agents/autoevolve-core.md` | Phase 1 Analyze に次元別スコア分析を追加 | S |

### 次元定義

| 次元 | 説明 | 重み |
|------|------|------|
| correctness | ロジックの正しさ、バグの有無 | 0.30 |
| security | セキュリティ脆弱性、入力検証 | 0.25 |
| maintainability | 可読性、テスタビリティ、複雑度 | 0.20 |
| performance | 不要な計算、N+1、メモリリーク | 0.15 |
| consistency | 既存コードベースとの一貫性 | 0.10 |

### reviewer 出力フォーマット追加

```markdown
## Review Scores
correctness: 4/5
security: 5/5
maintainability: 3/5
performance: 4/5
consistency: 4/5
weakest: maintainability

## Findings
... (既存フォーマット維持)
```

### AutoEvolve 接続

autoevolve-core Phase 1 Analyze に追加:
- `review-feedback.jsonl` から次元別スコアの時系列を集計
- 継続的に弱い次元を特定 → Phase 2 の改善提案をその次元に集中

---

## Task B: ロールバック付き改善ゲート

### 目的

merged 実験が後続の品質悪化を引き起こした場合に、自動でロールバックを提案する仕組み。

### 設計方針

autocontext の「スコアが改善しなければ前世代に戻す」パターンを採用。
ただし、**自動 git revert は危険**なので、ロールバック提案 + 確認ゲートとする。

### 変更ファイル

| ファイル | 変更内容 | サイズ |
|---------|---------|--------|
| `.config/claude/scripts/experiment_tracker.py` | `check_regression()` 関数追加 | M |
| `.config/claude/references/improve-policy.md` | ロールバック条件の追記 | S |

### check_regression() 設計

```python
def check_regression(exp_id: str) -> dict:
    """merged 実験後の品質回帰を検出する。

    判定ロジック:
    1. merged 後 3 セッション以上経過していること（安定化待ち）
    2. merged 後の error_rate が merged 前より 20% 以上増加
    3. OR: merged 後に同カテゴリの discard が 2 件以上発生
    4. OR: CQS が merged 時点から -5 以上低下

    Returns:
        {"regression": True/False, "reason": str, "suggestion": "revert <exp-id>"}
    """
```

### improve-policy への追記

```markdown
## ロールバック改善ゲート

| 条件 | アクション |
|------|-----------|
| merged 後 error_rate +20% | ロールバック提案を出力 |
| 同カテゴリ discard 2件連続 | ロールバック提案を出力 |
| CQS -5 以上低下 | ロールバック提案 + 改善サイクル一時停止 |

ロールバック提案は `[ROLLBACK SUGGESTED] exp-id: reason` 形式で出力。
自動実行はしない。/improve ダッシュボードに表示し、ユーザーが判断する。
```

### AutoEvolve 接続

autoevolve-core Phase 3 Garden の Quality Gate に追加:
- `check_regression()` を全 merged 実験に対して実行
- regression 検出時はダッシュボードに警告表示

---

## Task C: Tournament 型並列スパイク

### 目的

複数の改善戦略を並列実行し、スコア比較で最適解を選定する。
現状の `/spike`（1戦略ずつ検証）を拡張し、K-variant 同時比較を可能にする。

### 設計方針

- 既存の worktree インフラ（`superpowers:using-git-worktrees`）を活用
- `/spike` の拡張ではなく、`/improve --tournament` オプションとして実装
- 最大 3 バリアント（コスト制御）
- 各バリアントは独立 worktree で実行 → 結果を Task A の次元スコアで比較

### 変更ファイル

| ファイル | 変更内容 | サイズ |
|---------|---------|--------|
| `.config/claude/skills/improve/instructions/tournament-mode.md` | 新規: tournament モードの手順定義 | M |
| `.config/claude/agents/autoevolve-core.md` | Phase 2 Improve に tournament オプション追加 | S |
| `.config/claude/references/improve-policy.md` | tournament ルール追記 | S |

### tournament-mode.md 設計

```markdown
# Tournament Mode

## トリガー
- `/improve --tournament` で手動起動
- AutoEvolve Phase 2 で CQS が Stagnant (0.0-2.0) のとき自動提案

## フロー

1. **戦略生成**: 改善対象に対して 2-3 の異なるアプローチを生成
   - Approach A: 保守的（既存パターンの延長）
   - Approach B: 革新的（新パターン導入）
   - Approach C: (optional) ハイブリッド

2. **並列実行**: 各アプローチを独立 worktree で実装
   - `EnterWorktree` で隔離環境を作成
   - 各 worktree で実装 → テスト → レビュースコア取得

3. **スコア比較**: Task A の5次元スコアで比較
   - 加重平均スコアが最高のバリアントを勝者とする
   - 差が 0.5 未満の場合は保守的アプローチを優先（KISS原則）

4. **勝者マージ**: 勝者の worktree を本体にマージ
   - 敗者の worktree は自動クリーンアップ

## 制約
- 最大 3 バリアント（トークンコスト制御）
- 各バリアント最大 10 ターン
- tournament は 1 改善サイクルにつき最大 1 回
```

### AutoEvolve 接続

autoevolve-core Phase 2 Improve に条件分岐追加:
```
IF CQS Stagnant (0.0-2.0) AND 前回 improve が neutral:
  → tournament mode を提案
ELSE:
  → 通常の single-variant improve
```

---

## 実行順序

```
並列 Phase:
  ├─ Task A: reviewer x2 + review-dimensions.md + autoevolve-core.md (次元スコア)
  └─ Task B: experiment_tracker.py + improve-policy.md (ロールバック)

逐次 Phase:
  └─ Task C: tournament-mode.md + autoevolve-core.md + improve-policy.md (tournament)
```

## 検証チェックリスト

- [ ] code-reviewer の出力に `## Review Scores` セクションが含まれる
- [ ] codex-reviewer の出力に `## Review Scores` セクションが含まれる
- [ ] `references/review-dimensions.md` が存在し、5次元が定義されている
- [ ] `python scripts/experiment_tracker.py check-regression <exp-id>` が動作する
- [ ] `improve-policy.md` にロールバック条件が記載されている
- [ ] `improve/instructions/tournament-mode.md` が存在する
- [ ] autoevolve-core.md に次元スコア分析 + tournament 分岐が含まれる
- [ ] 既存テスト（`uv run pytest tests/`）が pass する

## リスク

| リスク | 対策 |
|--------|------|
| reviewer がスコアを安定して出力しない | スコア未検出時はフォールバック（findings のみ使用） |
| ロールバック誤検知 | 3セッション安定化待ち + 提案のみ（自動実行しない） |
| tournament のコスト過大 | 最大3バリアント制限 + Stagnant 時のみ発動 |
| worktree 競合 | 既存 worktree インフラの排他制御を利用 |
