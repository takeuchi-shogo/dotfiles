# 実験規律リファレンス

> 出典: Multi-Agent Autoresearch Lab (burtenshaw/multiautoresearch)
> 反復的な仮説検証・改善ループに適用する規律。ML 実験に限らず、ハーネス改善・パフォーマンスチューニング等にも汎用。

---

## 1仮説1パッチ1実行ルール

変数を1つだけ変え、計測し、判断する。複数の変更を同時に入れると因果帰属ができない。

> **変数は少ないほうが仮説検証しやすい (One change at a time)**
> 仮説検証の基本は「1回の実験で1つの変数だけ変える」こと。複数の改善を同時に入れたくなる衝動を抑え、因果を明確にする。小さな成果物（インチストーン）単位で検証することで、失敗しても学びが得られ、やり直しのコストが最小化される。

```
promoted master からリフレッシュ
  → 1つだけ変更（仮説に対応するパッチ）
  → 実行・計測
  → ベースライン比較
  → 勝利時のみ promote
```

### チェックリスト

- [ ] 変更は1つの仮説に対応しているか（複数変更を混ぜていないか）
- [ ] ベースライン（promoted master）が明確か
- [ ] 計測メトリクスが事前に定義されているか
- [ ] 実行環境は再現可能か（worktree 隔離）

---

## Promotion ゲート

品質ゲート（Review Gate）とは別の、**定量ゲート**。メトリクスがベースラインを超えた場合のみ master に反映する。

| ゲート | 判定基準 | 適用場面 |
|--------|---------|---------|
| Review Gate | コード品質・セキュリティ | 全コード変更 |
| Promotion Gate | メトリクス改善 | 反復改善ループ |

### 判定フロー

```
メトリクス ≥ ベースライン?
  → Yes: promote（master 更新 + ベースライン更新）
  → No:  reject（worktree 破棄、失敗理由を記録）
```

**重要**: promote と reject の両方で結果を記録する。失敗からの学びが次の仮説を生む。

---

## Wave ライフサイクル

複数の仮説を並列に検証するバッチ実行パターン。

```
Wave N:
  1. Plan: 仮説リスト作成（planner ロール）
  2. Filter: 既知の重複・非効率な仮説を除外（reviewer ロール）
  3. Execute: 各仮説を worktree で並列実行（worker ロール × N）
  4. Evaluate: 結果収集・ベースライン比較（reporter ロール）
  5. Promote: 勝者のみ master に反映
  6. Learn: Wave 全体の振り返り → 次の Wave の仮説生成に活用
```

### Wave 設計の原則

| 原則 | 説明 |
|------|------|
| **並列上限** | worker 数はリソース制約に合わせる（GPU、コンテキストウィンドウ等） |
| **独立性** | Wave 内の各仮説は互いに独立。依存がある場合は Wave を分ける |
| **累積改善** | Wave N の promoted master が Wave N+1 のベースラインになる |
| **収束判定** | 2 Wave 連続で改善なし → 探索方向を変える or 終了 |

---

## ロール定義（ラボ型マルチエージェント）

反復改善ループで使う4+1ロール。既存エージェントにマッピングして使う。

| ロール | 責務 | dotfiles での対応 |
|--------|------|------------------|
| **researcher** | 文献・事例探索、新しい仮説の種を見つける | `/research` スキル、gemini-explore |
| **planner** | 実験キュー管理、仮説の優先順位付け | Lead エージェント（EnterPlanMode） |
| **worker** | 1仮説を worktree で実行 | `/spike` + worktree 隔離 |
| **reporter** | 結果収集・観測性・fleet サマリー | session-trace-store + `/improve` |
| **memory-keeper** | 永続状態の管理（main checkout への書き込み） | memory システム、lessons-learned |

### 書き込み権限の分離

| ロール | main checkout | worktree |
|--------|:---:|:---:|
| memory-keeper | Write 可 | - |
| worker | **Write 禁止** | Write 可 |
| planner / reporter | Read のみ | Read のみ |

---

## dotfiles での活用例

### ハーネス改善の反復

```
仮説: "hook X のトリガー条件を変更すると false positive が減る"
  → worktree で hook を変更
  → テストスイート実行（メトリクス: false positive 率）
  → ベースライン比較
  → 改善なら promote
```

### `/improve` との連携

AutoEvolve の `/improve` は Wave の Plan フェーズに相当する。
improve が提案した改善案を1つずつ実験規律で検証することで、改善の因果帰属が可能になる。
