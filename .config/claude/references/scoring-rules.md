# Importance Scoring Rules

## スコアリングモデル

全ての learnings エントリに付与するフィールド:

| フィールド         | 型        | 説明                     |
| ------------------ | --------- | ------------------------ |
| `importance`       | `0.0-1.0` | 重要度                   |
| `confidence`       | `0.0-1.0` | スコアの確信度           |
| `type`             | `string`  | イベント種別             |
| `scored_by`        | `string`  | `"rule"` or `"llm"`     |
| `promotion_status` | `string`  | `"pending"` / `"promoted"` / `"archived"` |

## ルールベーススコアリング

### 高重要度 (0.8-1.0)

- `EACCES|Permission denied` → 0.9
- `segfault|SIGSEGV|OOM` → 1.0
- `GP-001|GP-002|GP-003|GP-004|GP-005` → 0.8
- `security|vulnerability|injection` → 0.9

### 中重要度 (0.4-0.7)

- `Cannot find module|ModuleNotFoundError` → 0.5
- `TypeError|ReferenceError` → 0.5
- `timeout|ETIMEDOUT` → 0.6

### 低重要度 (0.0-0.3)

- `warning:|WARN` → 0.2
- `deprecated` → 0.3

### カテゴリベーススコア（ルール未マッチ時）

- `error` → 0.5
- `quality` → 0.6
- `pattern` → 0.4
- `correction` → 0.7

### confidence

- ルールマッチ時: 0.8
- カテゴリベース時: 0.5

## 昇格ルール

| 条件                                    | アクション     |
| --------------------------------------- | -------------- |
| `importance >= 0.8` + 1回出現           | 自動昇格候補   |
| `0.4 <= importance < 0.8` + 3回以上出現 | 昇格候補       |
| `importance < 0.4`                      | 90日後アーカイブ |
