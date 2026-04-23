---
status: reference
last_reviewed: 2026-04-23
---

# Blueprint パターン

Stripe の Minions システムに着想を得た、タスク種別ごとのワークフロー DAG 定義。
決定論的ノード（lint, test, git）とエージェントループ（実装、修正）を明示的に分離する。

関連: `references/blueprints/` — 具体例 (bug-fix, feature, refactor)

---

## 概要

Blueprint は「このタスク種別では何を決定論的に、何をエージェントに任せるか」を宣言する設定ファイル。
手動で3回以上繰り返したワークフローを DAG として記述し、`/autonomous` スキルの実行エンジンに渡す。

**核心的な問い**: 「このステップは LLM が必要か、それともシェルコマンドで十分か？」

---

## ノード種別

### `deterministic` — 決定論的ノード

| 属性 | 値 |
|------|----|
| 実行内容 | シェルコマンド（lint, test, git, gh） |
| LLM 使用 | なし（トークンコスト: ゼロ） |
| 再現性 | 100% |
| 用途 | lint, test, commit, push, PR 作成, スナップショット取得 |

```yaml
- id: lint
  type: deterministic
  command: "${LINT_CMD:-true}"
  on_failure: retry
```

### `agentic` — エージェントノード

| 属性 | 値 |
|------|----|
| 実行内容 | LLM 駆動の創造的作業 |
| LLM 使用 | あり（トークンコスト: 可変） |
| 再現性 | 可変 |
| 用途 | 調査, 実装, デバッグ, コードレビュー, 計画 |

```yaml
- id: implement
  type: agentic
  tools: [Read, Edit, Write, Grep, Glob]
  max_iterations: 5
  on_failure: handback
```

**必須属性**: `tools`（ツールスコープ）と `max_iterations`（無限ループ防止）は省略不可。

---

## スキーマ

```yaml
blueprint:
  name: string           # kebab-case 識別子
  description: string    # 1行の目的説明
  trigger: string        # いつこの blueprint を使うか
  completion: strict | graduated   # 完了ポリシー
  nodes:
    - id: string
      type: deterministic | agentic
      # deterministic のみ
      command: string
      # agentic のみ
      tools: string[]
      max_iterations: number    # default: 3
      # 共通
      on_failure: retry | skip | abort | handback
  edges:
    - [from, to]
    - [from, to, { condition: "node.passed | node.failed" }]
```

### `completion` ポリシー

| 値 | 動作 |
|----|------|
| `strict` | 全ノードが成功しないと完了扱いにしない (`completion-gate.py` が enforce) |
| `graduated` | 部分完了でも価値を届ける。PR 作成まで到達すれば成功とみなす |

### `on_failure` アクション

| 値 | 動作 |
|----|------|
| `retry` | 同ノードを再実行（deterministic に適する） |
| `skip` | このノードをスキップして次へ（オプショナルなステップ） |
| `abort` | ワークフロー全体を停止。前提条件が欠けている場合 |
| `handback` | エージェントが人間にコントロールを返す。自動修正できない場合 |

---

## 設計原則

### 1. 「デフォルト決定論的、必要な時だけエージェント」

エージェントノードはトークンを消費し、結果が非決定的。
lint や test 実行は LLM を介在させず、シェルで直接実行する。

Bad:
```yaml
- id: run-tests
  type: agentic          # LLM を使って「テストを実行する」
  tools: [Bash]
```

Good:
```yaml
- id: run-tests
  type: deterministic    # シェルが直接実行
  command: "${TEST_CMD}"
```

### 2. トークン経済

決定論的ノードのコストはゼロ。ループ構造（lint → fix → lint）でも追加コストが発生しない。
エージェントノードは `max_iterations` で上限を設ける。

### 3. ツールスコープ

各エージェントノードは必要最小限のツールのみ宣言する。
調査ノードに `Write` は不要。`run-session.sh` の `--allowedTools` に自動マッピングされる。

| ノードの目的 | 適切なツール |
|------------|------------|
| 調査・分析 | `Read, Grep, Glob` |
| 実装・修正 | `Read, Edit, Write, Grep, Glob` |
| デバッグ | `Read, Edit, Grep, Bash` |
| 計画 | `Read, Grep, Glob` |

### 4. フェイルセーフ設計

- エージェントノードには必ず `handback` または `abort` を設定する
- `max_iterations` を超えた場合は自動的に `on_failure` アクションを実行する
- `retry` は決定論的ノードにのみ使用する（エージェントの retry は `max_iterations` で管理）

---

## エッジとフロー制御

### 条件なしエッジ（逐次実行）

```yaml
edges:
  - [investigate, implement-fix]   # investigate 完了後に implement-fix へ
```

### 条件付きエッジ（分岐）

```yaml
edges:
  - [lint, test,            { condition: "lint.passed" }]
  - [lint, fix-lint-errors, { condition: "lint.failed" }]
```

### ループ（修正 → 再検証）

```yaml
edges:
  - [fix-lint-errors, lint]        # 修正後に lint へ戻る
  - [fix-test-failures, lint]      # テスト修正後も lint から再検証
```

---

## 統合ポイント

| コンポーネント | Blueprint の使い方 |
|-------------|-----------------|
| `/autonomous` スキル | blueprint ファイルを引数に渡してセッション実行を制御 |
| `completion-gate.py` | `completion: strict` の場合、Stop フック時に全ノード成功を検証 |
| `run-session.sh` | エージェントノードの `tools` から `--allowedTools` を自動生成 |

---

## Blueprint の作り方

1. **トリガー特定**: 手動で3回以上繰り返したタスクパターンを選ぶ
2. **ステップ列挙**: 実際に行うステップを箇条書きにする
3. **種別分類**: 各ステップを `deterministic` / `agentic` に分類する
4. **エッジ定義**: 成功時・失敗時の遷移を DAG として表現する
5. **ツールスコープ**: エージェントノードに最小限のツールを割り当てる
6. **失敗ポリシー**: 各ノードの `on_failure` を決める

### 種別分類の判断基準

```
このステップを毎回同じシェルコマンドで実行できるか？
  YES → deterministic
  NO  → agentic
```

---

## 関連ドキュメント

- `references/blueprints/bug-fix.yaml` — バグ修正フロー
- `references/blueprints/feature.yaml` — 機能実装フロー
- `references/blueprints/refactor.yaml` — リファクタリングフロー
- `references/workflow-guide.md` — 全体ワークフロー設計
- `references/resource-bounds.md` — トークン予算管理
- `skills/autonomous/SKILL.md` — `/autonomous` 実行エンジン
