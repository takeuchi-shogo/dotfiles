---
status: reference
last_reviewed: 2026-04-23
---

# Lint Category Map (Factory.ai 7-Category Framework)

`harness-rationale.md` の旧4分類を拡張し、Agent-Native コード品質を7カテゴリで体系化する。

## 旧4分類 → 新7分類 マッピング

| # | カテゴリ | 旧分類 | 説明 |
|---|---------|--------|------|
| 1 | **Grep-ability** | 旧1 (変更なし) | named exports, 一貫したエラー型, 明示的 DTO。エージェントが Grep で発見可能 |
| 2 | **Glob-ability** | 旧2 (変更なし) | 予測可能なファイル構造, 命名規則統一。エージェントが Glob で発見・作成可能 |
| 3 | **Architectural Boundaries** | 旧3 (変更なし) | import allowlist/denylist, 依存方向強制。変更影響を限定 |
| 4 | **Security & Privacy** | 旧4 (変更なし) | secrets ブロック, 入力バリデーション, eval 禁止 |
| 5 | **Testability** | 新設 | テスト隣接配置, テスト存在チェック, テスト=報酬信号 |
| 6 | **Observability** | 新設 | 構造化ログ, エラー報告形式, 計測可能な出力 |
| 7 | **Documentation** | 新設 | パス参照整合性, ドキュメント鮮度, Design Rationale |

## 既存 lint ツールの再分類

### Biome (TS/JS/CSS) — via PostToolUse + lefthook

| カテゴリ | 寄与するルール |
|---------|--------------|
| Grep-ability | フォーマット統一 → 一貫した検索結果 |
| Glob-ability | — |
| Architectural Boundaries | — |
| Security & Privacy | — |
| Testability | — |
| Observability | — |
| Documentation | — |

### Oxlint (TS/JS) — via PostToolUse + lefthook

| カテゴリ | 寄与するルール |
|---------|--------------|
| Grep-ability | 未使用変数・未使用 import の検出 |
| Glob-ability | — |
| Architectural Boundaries | — |
| Security & Privacy | 危険なパターン検出 (eval 等) |
| Testability | — |
| Observability | — |
| Documentation | — |

### Ruff (Python) — via PostToolUse + lefthook

| カテゴリ | 寄与するルール |
|---------|--------------|
| Grep-ability | フォーマット統一, 未使用 import (F401) |
| Glob-ability | — |
| Architectural Boundaries | — |
| Security & Privacy | S: bandit ルール (hardcoded passwords, exec 等) |
| Testability | — |
| Observability | — |
| Documentation | D: docstring 存在・形式チェック |

### gofmt (Go) — via PostToolUse + lefthook

| カテゴリ | 寄与するルール |
|---------|--------------|
| Grep-ability | フォーマット統一 → 一貫した検索結果 |
| Glob-ability | — |
| Architectural Boundaries | — |
| Security & Privacy | — |
| Testability | — |
| Observability | — |
| Documentation | — |

## Hook 層での実装マッピング

| 層 | 速度 | カテゴリ寄与 |
|---|---|---|
| **PostToolUse** (ms) | auto-format.js | 1,2 (Grep/Glob-ability) |
| **PostToolUse** (ms) | golden-check.py | 3,4 (Architecture, Security) |
| **PostToolUse** (ms) | doc-garden-check.py | 7 (Documentation) |
| **PreToolUse** (ms) | tdd-guard.py | 5 (Testability) |
| **Pre-commit** (s) | lefthook biome/oxlint/ruff/gofmt | 1,4,7 |
| **Pre-commit** (s) | check-claudemd-lines.sh | 7 (Documentation) |
| **Stop** (s) | completion-gate.py | 5 (Testability — テスト実行) |
| **Human Review** (h) | /review スキル | 1-7 全カテゴリ |

## 新カテゴリの拡張候補

### 5. Testability
- **実装済み**: `completion-gate.py` (テスト実行ゲート), `tdd-guard.py` (テスト→実装順序)
- **参照**: `agent-native-code-design.md` 原則2 (Collocated Tests), 原則4 (テスト=報酬信号)
- **候補**: collocated test 存在チェック (実装ファイルの隣にテストがあるか)

### 6. Observability
- **実装済み**: `output-offload.py` (出力量管理), `stagnation-detector.py` (停滞検出)
- **候補**: 構造化ログ形式の強制 (JSON ログ推奨), エラーメッセージの情報量チェック

### 7. Documentation
- **実装済み**: `doc-garden-check.py` (参照整合性 + 鮮度), `check-claudemd-lines.sh` (行数制限)
- **参照**: `comprehension-debt-policy.md` (Design Rationale 必須)
- **候補**: public 関数の godoc/JSDoc 存在チェック
