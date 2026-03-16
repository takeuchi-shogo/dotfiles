# Failure Taxonomy

LLM エージェントの失敗モードを体系的に定義する。
各失敗モードは binary (pass/fail) で判定可能な単一の基準を持つ。

hooks (`session_events.py`) と review agents が共通で参照する。

---

## 失敗モード一覧

### FM-001: Null Safety Violation

- **定義**: nullable 値の未チェックアクセスによるクラッシュ
- **検出パターン**: `TypeError: Cannot read properties`, `nil pointer dereference`, `panic:.*nil`
- **関連 GP**: —
- **判定**: nullable フィールドへのアクセス前にガードがあるか (pass/fail)
- **レビューアー**: `code-reviewer`, `nil-path-reviewer`

### FM-002: Error Suppression

- **定義**: catch/except ブロックでエラーを黙殺し、上位に伝播しない
- **検出パターン**: `catch\s*\(.*\)\s*\{\s*\}`, `except.*:\s*pass`
- **関連 GP**: GP-004
- **判定**: catch/except 内でエラーが記録または再 throw されるか (pass/fail)
- **レビューアー**: `silent-failure-hunter`

### FM-003: Dependency Drift

- **定義**: 既存の安定したライブラリがあるのに新しい依存を追加
- **検出パターン**: `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt` への追加行
- **関連 GP**: GP-003
- **判定**: 追加された依存に既存代替があるか (pass/fail)
- **レビューアー**: `code-reviewer`

### FM-004: Type Safety Violation

- **定義**: any/interface{} 等の unsafe 型の使用で型安全性が失われる
- **検出パターン**: `: any`, `as any`, `interface{}`
- **関連 GP**: GP-005
- **判定**: 具体的な型で代替可能か (pass/fail)
- **レビューアー**: `type-design-analyzer`

### FM-005: Boundary Validation Miss

- **定義**: 外部入力（API, CLI, ファイル）をバリデーションなしで使用
- **検出パターン**: `req.body`, `req.query`, `sys.argv`, `os.Args` のバリデーションなし使用
- **関連 GP**: GP-002
- **判定**: 入力に対するバリデーション/サニタイズがあるか (pass/fail)
- **レビューアー**: `security-reviewer`

### FM-006: Permission/Access Error

- **定義**: ファイル/ネットワークのパーミッションエラー
- **検出パターン**: `EACCES`, `Permission denied`
- **関連 GP**: —
- **判定**: 権限チェックまたはエラーハンドリングがあるか (pass/fail)
- **レビューアー**: `code-reviewer`

### FM-007: Module Resolution Failure

- **定義**: モジュール/パッケージのインポート解決失敗
- **検出パターン**: `Cannot find module`, `ModuleNotFoundError`, `no required module`
- **関連 GP**: —
- **判定**: インポートパスが正しく、依存が宣言されているか (pass/fail)
- **レビューアー**: `code-reviewer`

### FM-008: Build/Compilation Failure

- **定義**: ビルドまたはコンパイルの失敗
- **検出パターン**: `build failed`, `compilation failed`, `error\[E\d+\]`, `SyntaxError`
- **関連 GP**: —
- **判定**: コードが正しくコンパイルされるか (pass/fail)
- **レビューアー**: `build-fixer`

### FM-009: Resource Exhaustion

- **定義**: メモリ不足、タイムアウト等のリソース枯渇
- **検出パターン**: `OOM`, `out of memory`, `timeout`, `ETIMEDOUT`, `SIGSEGV`
- **関連 GP**: —
- **判定**: リソース制限の考慮があるか (pass/fail)
- **レビューアー**: `code-reviewer`

### FM-010: Security Vulnerability

- **定義**: インジェクション、XSS、認証バイパス等のセキュリティ脆弱性
- **検出パターン**: `injection`, `vulnerability`, `XSS`, `CSRF`
- **関連 GP**: —
- **判定**: OWASP Top 10 に該当するパターンがないか (pass/fail)
- **レビューアー**: `security-reviewer`

### FM-011: Plan Adherence Failure

- **定義**: 計画ステップの省略、計画外行動の実行
- **検出パターン**: `completion-gate.py` の Ralph Loop で未完了ステップ検出、計画からの逸脱
- **関連 GP**: —
- **判定**: アクティブプランの全ステップが完了しているか (pass/fail)
- **レビューアー**: `code-reviewer`
- **着想**: AgentRx — Plan Adherence Failure

### FM-012: Information Invention

- **定義**: 存在しないファイル、API、事実の参照（ハルシネーション）
- **検出パターン**: `No such file or directory`, `ENOENT`, `404 Not Found`, Read/Glob で対象が見つからない連続パターン
- **関連 GP**: —
- **判定**: 参照した情報が実在するか (pass/fail)
- **レビューアー**: `code-reviewer`
- **着想**: AgentRx — Invention of New Information

### FM-013: Tool Output Misinterpretation

- **定義**: コマンド出力やツール結果の誤読による不適切な後続アクション
- **検出パターン**: 同一コマンドの短時間再実行、エラー直後の同一ファイル再編集
- **関連 GP**: —
- **判定**: ツール出力に基づく判断が正しいか (pass/fail)
- **レビューアー**: `debugger`
- **着想**: AgentRx — Misinterpretation of Tool Output

### FM-014: Intent Misalignment

- **定義**: ユーザーの意図を誤解し、要求と異なる作業を実行
- **検出パターン**: ユーザーからの修正指示（「違う」「そうじゃなく」「〜ではなく」）、ユーザー否認パターン
- **関連 GP**: —
- **判定**: 実行した作業がユーザーの要求と一致するか (pass/fail)
- **レビューアー**: `product-reviewer`
- **着想**: AgentRx — Intent–Plan Misalignment

### FM-015: Premature Action

- **定義**: 確認なしに危険・不可逆な操作を実行
- **検出パターン**: `git push`, `rm -rf`, `DROP TABLE` 等の危険操作を事前確認なしに実行
- **関連 GP**: —
- **判定**: 危険操作の前にユーザー確認を取得したか (pass/fail)
- **レビューアー**: `code-reviewer`
- **着想**: AgentRx の障害分類を拡張した独自カテゴリ

---

## Failure Type 分類

各失敗モードの発生は、さらに2種類に分類される:

| Failure Type | 定義 | アクション |
|---|---|---|
| **specification** | エージェントへの指示（プロンプト/ルール）が曖昧または不完全 | プロンプト・ルールを改善 |
| **generalization** | 指示は明確だが、エージェントが正しく実行できなかった | Evaluator を強化 |

### 自動分類ヒューリスティック

```
1. 同じ FM が複数プロジェクトで発生 → generalization（LLM の能力限界）
2. 同じ FM が特定のプロンプト系統でのみ発生 → specification（指示の問題）
3. レビュー指摘を ignore した理由が「指摘が的外れ」→ specification
4. レビュー指摘を accept した → generalization（検出できたが防げなかった）
5. デフォルト → generalization（保守的判定）
```

---

## 運用

- **hooks**: `session_events.py` が `IMPORTANCE_RULES` のパターンマッチ時に `failure_mode` を付与
- **review**: 各レビューアーが指摘に `failure_mode` (FM-XXX) を付与
- **autoevolve-core**: `failure-taxonomy.md` を参照し、Axial Coding で taxonomy を更新提案
- **拡張**: 50件以上の learnings 蓄積後に autoevolve-core が新しい FM 候補を提案（理論的飽和まで）

---

## 帰納的検証プロセス（Error Analysis 記事ベース）

FM-001〜FM-010 はトップダウンで設計された初期分類である。
運用データの蓄積に伴い、以下のプロセスで帰納的に検証・更新する。

> 着想元: "Error Analysis: The Highest-ROI Activity in AI Engineering" — Shankar & Husain

### Open Coding → Axial Coding サイクル

1. `/improve` の Step 0 で人間が直近トレースを読み、驚き・パターンをメモ（Open Coding）
2. autoevolve-core の Task 9（Axial Coding）が未分類トレースをクラスタリング
3. 新しい FM 候補を `insights/failure-taxonomy-proposals.md` に出力
4. 人間が FM の追加・統合・削除を判断

### 理論的飽和の判定

- 直近 3 回の `/improve` 実行で新しい FM 候補がゼロ → **飽和**
- 飽和後は既存 FM の precision/recall 改善にフォーカス
- 飽和状態は `insights/taxonomy-saturation.md` に記録

### 合成トレース（将来拡張）

プロダクションデータが不足する場合、以下の次元で合成シナリオを生成:
- 言語 × エラー種別 × コンテキストサイズ
- hook が正しく検出するか検証
- 未検出パターンを FM に追加
