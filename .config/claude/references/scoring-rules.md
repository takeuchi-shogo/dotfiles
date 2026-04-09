# Importance Scoring Rules

## スコアリングルール

イベント記録時にルールベースで importance (0.0-1.0) と confidence (0.0-1.0) を付与する。

### 高重要度 (0.8-1.0)

| パターン | importance | 説明 |
| -------- | ---------- | ---- |
| `permission denied` | 0.9 | 権限エラー |
| `EACCES` | 0.9 | アクセス拒否 |
| `security` | 1.0 | セキュリティ関連 |
| `OOM\|out of memory` | 1.0 | メモリ枯渇 |
| `GP-\d+` (golden principle) | 0.8 | ゴールデンプリンシプル違反 |

### 中重要度 (0.4-0.7)

| パターン | importance | 説明 |
| -------- | ---------- | ---- |
| `ModuleNotFoundError` | 0.6 | モジュール不在 |
| `Cannot find module` | 0.6 | モジュール不在 (Node) |
| `TypeError` | 0.5 | 型エラー |
| `ReferenceError` | 0.5 | 参照エラー |
| `timeout\|timed out` | 0.4 | タイムアウト |

### 低重要度 (0.0-0.3)

| パターン | importance | 説明 |
| -------- | ---------- | ---- |
| `warning` | 0.2 | 警告 |
| `deprecated` | 0.3 | 非推奨 |

### カテゴリフォールバック

ルールにマッチしない場合、カテゴリに基づくデフォルト値を使用:

| カテゴリ | importance | confidence |
| -------- | ---------- | ---------- |
| error | 0.5 | 0.5 |
| quality | 0.6 | 0.5 |
| pattern | 0.4 | 0.5 |
| correction | 0.7 | 0.5 |
| その他 | 0.5 | 0.5 |

## 信頼度

- ルールマッチ: `confidence = 0.8` (`scored_by: "rule"`)
- カテゴリフォールバック: `confidence = 0.5` (`scored_by: "rule"`)
- LLM 再評価: `confidence = 0.9` (`scored_by: "llm"`)

## 昇格ルール

| 条件 | アクション |
| ---- | ---------- |
| `importance >= 0.8` + 1回以上出現 | 自動昇格候補 → insights に記載 |
| `0.4 <= importance < 0.8` + 3回以上出現 | 昇格候補 → insights に記載 |
| `importance < 0.4` | 昇格なし |

昇格先: `insights/analysis-YYYY-MM-DD.md` の「昇格提案」セクション

## タスク種別スコアリングルーティング

`step_credit()` の `step_quality` パラメータの使用を制御する。
タスク種別は session-learner が自動分類する。

| タスク種別 | step_quality | 説明 |
|-----------|-------------|------|
| `reasoning` (デバッグ, 設計, レビュー) | 各ステップの成否で重み付け | PRM 的。中間推論の正しさが重要 |
| `outcome` (生成, 変換, フォーマット) | None (従来の回数比配分) | ORM 的。最終出力のみ評価 |
| `mixed` (実装+テスト) | テスト結果で重み調整 | テスト通過=1.0, 失敗=0.2 |
| `uncontrollable` (環境障害) | プロセススコア保持 (0.8-1.0) | process_correct + outcome_failed_uncontrollable: プロセス品質を不当にペナルティしない。環境障害 (timeout, permission denied, rate limit) でアウトカム失敗時、アウトカムは `blocked` としてマーク |

A/B 比較では `margin_advantage()` で度合いを保持する。
K>=3 の variant 比較では `plackett_luce_ranking()` で順序付きランキングを使用する。

## 統合スコアリング設定

全閾値・重みは `references/scoring-config.json` に一元管理されている。
チューニング時は JSON を編集し、本ファイルの閾値表は人間向けリファレンスとして残す。
