# Failure Taxonomy

LLM エージェントの失敗モードを体系的に定義する。
各失敗モードは binary (pass/fail) で判定可能な単一の基準を持つ。
各失敗モードは「定義」（avoid: やってはいけないこと）と「不変条件」（enforce: 守るべき推論原則）の対で構成される（MemCollab 対比蒸留パラダイム）。

hooks (`session_events.py`) と review agents が共通で参照する。

---

## 失敗モード一覧

### FM-001: Null Safety Violation

- **定義**: nullable 値の未チェックアクセスによるクラッシュ
- **検出パターン**: `TypeError: Cannot read properties`, `nil pointer dereference`, `panic:.*nil`
- **関連 GP**: —
- **判定**: nullable フィールドへのアクセス前にガードがあるか (pass/fail)
- **不変条件**: nullable 値へのアクセスは必ずガードの後に行う
- **レビューアー**: `code-reviewer`, `nil-path-reviewer`
- **autoFixable**: true
- **suggestedFix**: "nullable ガードの自動挿入（lint --fix）"

### FM-002: Error Suppression

- **定義**: catch/except ブロックでエラーを黙殺し、上位に伝播しない
- **検出パターン**: `catch\s*\(.*\)\s*\{\s*\}`, `except.*:\s*pass`
- **関連 GP**: GP-004
- **判定**: catch/except 内でエラーが記録または再 throw されるか (pass/fail)
- **不変条件**: catch/except 内では必ずエラーを記録または再送出する
- **レビューアー**: `silent-failure-hunter`
- **autoFixable**: false
- **suggestedFix**: "エラーハンドリングパターンの手動レビュー"

### FM-003: Dependency Drift

- **定義**: 既存の安定したライブラリがあるのに新しい依存を追加
- **検出パターン**: `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt` への追加行
- **関連 GP**: GP-003
- **判定**: 追加された依存に既存代替があるか (pass/fail)
- **不変条件**: 新依存追加前に既存の代替を検索する
- **レビューアー**: `code-reviewer`
- **autoFixable**: true
- **suggestedFix**: "既存依存の検索を促すプロンプト注入"

### FM-004: Type Safety Violation

- **定義**: any/interface{} 等の unsafe 型の使用で型安全性が失われる
- **検出パターン**: `: any`, `as any`, `interface{}`
- **関連 GP**: GP-005
- **判定**: 具体的な型で代替可能か (pass/fail)
- **不変条件**: 具体的な型で表現可能な場合は any/interface{} を使わない
- **レビューアー**: `type-design-analyzer`
- **autoFixable**: true
- **suggestedFix**: "any/interface{} の具体型への自動変換（lint --fix）"

### FM-005: Boundary Validation Miss

- **定義**: 外部入力（API, CLI, ファイル）をバリデーションなしで使用
- **検出パターン**: `req.body`, `req.query`, `sys.argv`, `os.Args` のバリデーションなし使用
- **関連 GP**: GP-002
- **判定**: 入力に対するバリデーション/サニタイズがあるか (pass/fail)
- **不変条件**: 外部入力は使用前に必ずバリデーション/サニタイズする
- **レビューアー**: `security-reviewer`
- **autoFixable**: false
- **suggestedFix**: "入力バリデーションの手動設計"

### FM-006: Permission/Access Error

- **定義**: ファイル/ネットワークのパーミッションエラー
- **検出パターン**: `EACCES`, `Permission denied`
- **関連 GP**: —
- **判定**: 権限チェックまたはエラーハンドリングがあるか (pass/fail)
- **不変条件**: ファイル/ネットワーク操作は権限チェックまたはエラーハンドリングで保護する
- **レビューアー**: `code-reviewer`
- **autoFixable**: false
- **suggestedFix**: "権限モデルの手動レビュー"

### FM-007: Module Resolution Failure

- **定義**: モジュール/パッケージのインポート解決失敗
- **検出パターン**: `Cannot find module`, `ModuleNotFoundError`, `no required module`
- **関連 GP**: —
- **判定**: インポートパスが正しく、依存が宣言されているか (pass/fail)
- **不変条件**: インポートパスと依存宣言の一致を確認してからコミットする
- **レビューアー**: `code-reviewer`
- **autoFixable**: true
- **suggestedFix**: "import パスの自動補完（LSP）"

### FM-008: Build/Compilation Failure

- **定義**: ビルドまたはコンパイルの失敗
- **検出パターン**: `build failed`, `compilation failed`, `error\[E\d+\]`, `SyntaxError`
- **関連 GP**: —
- **判定**: コードが正しくコンパイルされるか (pass/fail)
- **不変条件**: コード変更後は必ずビルド/コンパイルを実行して通過を確認する
- **レビューアー**: `build-fixer`
- **autoFixable**: true
- **suggestedFix**: "ビルドエラーの自動修正（build-fixer agent）"

### FM-009: Resource Exhaustion

- **定義**: メモリ不足、タイムアウト等のリソース枯渇
- **検出パターン**: `OOM`, `out of memory`, `timeout`, `ETIMEDOUT`, `SIGSEGV`
- **関連 GP**: —
- **判定**: リソース制限の考慮があるか (pass/fail)
- **不変条件**: リソース消費がスパンに比例する操作にはタイムアウトとメモリ制限を設定する
- **レビューアー**: `code-reviewer`
- **autoFixable**: false
- **suggestedFix**: "リソース制限の手動設計"

### FM-010: Security Vulnerability

- **定義**: インジェクション、XSS、認証バイパス等のセキュリティ脆弱性
- **検出パターン**: `injection`, `vulnerability`, `XSS`, `CSRF`
- **関連 GP**: —
- **判定**: OWASP Top 10 に該当するパターンがないか (pass/fail)
- **不変条件**: 外部入力を含む処理は OWASP Top 10 のチェックリストで検証する
- **レビューアー**: `security-reviewer`
- **autoFixable**: false
- **suggestedFix**: "OWASP チェックリストによる手動レビュー"

### FM-011: Plan Adherence Failure

- **定義**: 計画ステップの省略、計画外行動の実行
- **検出パターン**: `completion-gate.py` の Ralph Loop で未完了ステップ検出、計画からの逸脱
- **関連 GP**: —
- **判定**: アクティブプランの全ステップが完了しているか (pass/fail)
- **不変条件**: アクティブプランの全ステップを完了するまで作業を終了しない
- **レビューアー**: `code-reviewer`
- **着想**: AgentRx — Plan Adherence Failure
- **autoFixable**: false
- **suggestedFix**: "計画ステップの再確認"

### FM-012: Information Invention

- **定義**: 存在しないファイル、API、事実の参照（ハルシネーション）
- **検出パターン**: `No such file or directory`, `ENOENT`, `404 Not Found`, Read/Glob で対象が見つからない連続パターン
- **関連 GP**: —
- **判定**: 参照した情報が実在するか (pass/fail)
- **不変条件**: 参照するファイル・API・事実は実在を確認してから使用する
- **レビューアー**: `code-reviewer`
- **着想**: AgentRx — Invention of New Information
- **autoFixable**: false
- **suggestedFix**: "参照先の実在確認"

### FM-013: Tool Output Misinterpretation

- **定義**: コマンド出力やツール結果の誤読による不適切な後続アクション
- **検出パターン**: 同一コマンドの短時間再実行、エラー直後の同一ファイル再編集
- **関連 GP**: —
- **判定**: ツール出力に基づく判断が正しいか (pass/fail)
- **不変条件**: ツール出力は生テキストを直接読み、推測で解釈しない
- **レビューアー**: `debugger`
- **着想**: AgentRx — Misinterpretation of Tool Output
- **autoFixable**: false
- **suggestedFix**: "生出力の再読み取り"

### FM-014: Intent Misalignment

- **定義**: ユーザーの意図を誤解し、要求と異なる作業を実行
- **検出パターン**: ユーザーからの修正指示（「違う」「そうじゃなく」「〜ではなく」）、ユーザー否認パターン
- **関連 GP**: —
- **判定**: 実行した作業がユーザーの要求と一致するか (pass/fail)
- **不変条件**: 曖昧な指示は実装前に確認し、ユーザーの意図を明示的に言語化する
- **レビューアー**: `product-reviewer`
- **着想**: AgentRx — Intent–Plan Misalignment
- **autoFixable**: false
- **suggestedFix**: "ユーザーへの確認質問"

### FM-015: Premature Action

- **定義**: 確認なしに危険・不可逆な操作を実行
- **検出パターン**: `git push`, `rm -rf`, `DROP TABLE` 等の危険操作を事前確認なしに実行
- **関連 GP**: —
- **判定**: 危険操作の前にユーザー確認を取得したか (pass/fail)
- **不変条件**: 不可逆な操作の前にユーザー確認を取得する
- **レビューアー**: `code-reviewer`
- **着想**: AgentRx の障害分類を拡張した独自カテゴリ
- **autoFixable**: false
- **suggestedFix**: "操作前の確認プロンプト挿入"

### FM-016: Result Fabrication

- **定義**: 期待される出力に合わせて中間結果・パラメータを調整し、導出の正しさを偽装する
- **検出パターン**: 検証なしの「確認しました」、根拠不明の定数・係数、プロットと数式の不整合、ステップ飛ばし表現（「this becomes」「for consistency」）
- **関連 GP**: —
- **判定**: 中間ステップの導出が明示されているか、値の根拠が示されているか (pass/fail)
- **不変条件**: 中間ステップの導出を省略せず、各値の根拠を明示する
- **レビューアー**: `code-reviewer`, `codex-reviewer`
- **着想**: Schwartz "Vibe Physics" (2026-03) — Claude がパラメータ調整でプロットを合わせ、不確定性バンドを美的に平滑化し、検証したと虚偽申告した事例群。FM-012 (Information Invention) とは異なり、参照先は実在するが値・導出が捏造されるパターン
- **autoFixable**: false
- **suggestedFix**: "中間ステップの導出検証"

### FM-017: Feature Stubbing

- **定義**: 機能の UI 要素（ボタン、メニュー、パネル）は存在するが、インタラクション深度が不足しており実質的に display-only
- **検出パターン**: onClick が空関数、イベントハンドラが未実装、API 呼び出しが TODO/stub コメント、テストで UI 存在のみ確認し操作結果を検証していない
- **関連 GP**: —
- **判定**: UI 要素に対応する完全なインタラクションパス（イベント → 処理 → フィードバック）が実装されているか (pass/fail)
- **不変条件**: UI 要素にはイベント→処理→フィードバックの完全なインタラクションパスを実装する
- **レビューアー**: `code-reviewer`, `product-reviewer`
- **着想**: Anthropic "Harness Design for Long-Running Apps" (2026-03) — Generator が機能を stub する傾向。ボタンは toggle するがマイク入力を capture しない、ツールは存在するが機能しない等の事例。FM-011 (Plan Adherence) が「ステップ省略」を検出するのに対し、FM-017 は「ステップ完了に見えるが実は hollow」を検出する
- **autoFixable**: false
- **suggestedFix**: "インタラクションパスの完全性検証"

### FM-018: Evaluator Rationalization

- **定義**: Evaluator が問題を正しく特定した後、自己説得により重大度を引き下げて承認してしまう
- **検出パターン**: レビューコメントで「〜だが問題ない」「minor issue」「許容範囲」等の rationalization 表現が critical/high severity の指摘に続く、指摘数と最終判定の乖離（多数指摘→LGTM）
- **関連 GP**: —
- **判定**: Evaluator が特定した問題の severity が最終判定に適切に反映されているか (pass/fail)
- **不変条件**: 検出した問題の severity を最終判定に適切に反映し、自己矮小化しない
- **レビューアー**: `/review` スキルの合成フェーズ（レビューアー間の judgment divergence として検出）
- **着想**: Anthropic "Harness Design for Long-Running Apps" (2026-03) — QA エージェントが「legitimate issues を見つけた後、talk itself into deciding they weren't a big deal and approve」する失敗パターン。Self-evaluation bias の具体的発現形態。FM-016 (Result Fabrication) が「結果の捏造」であるのに対し、FM-018 は「正しい検出結果の自己矮小化」
- **autoFixable**: false
- **suggestedFix**: "severity と最終判定の整合性チェック"

### FM-019: Agentic Laziness (Premature Stop)

- **定義**: 複雑なマルチステップタスクの途中で、言い訳をつけて早期停止する
- **検出パターン**: 未完了の plan ステップがある状態での停止試行、`completion-gate.py` の Ralph Loop 発火
- **関連 GP**: —
- **判定**: アクティブプランの全ステップが完了しているか (pass/fail)
- **不変条件**: 複雑なタスクは計画の全ステップ完了まで継続する
- **レビューアー**: `completion-gate.py` (Ralph Loop)
- **着想**: Anthropic "Long-Running Claude for Scientific Computing" (2026-03) — "When asked to complete a complex, multi-part task, they can sometimes find an excuse to stop before finishing the entire task." Ralph Loop パターンで対処。FM-015 (Premature Action) が「早すぎる行動」であるのに対し、FM-019 は「早すぎる停止」
- **autoFixable**: false
- **suggestedFix**: "Ralph Loop による完了強制"

### FM-020: Probabilistic Cascade

- **定義**: 各ステップの成功確率 p が連鎖すると全体成功確率が p^n で減衰する現象。例: 各ステップ 95% 成功 → 5ステップで 77%、10ステップで 60%
- **検出パターン**: タスクの分割粒度が大きい（1ステップ10分超）、連続する依存ステップが5以上、または中間検証ゲートなしの長いパイプライン
- **関連 GP**: —
- **判定**: 各ステップが5分以内に完了し、ステップ間にテスト/検証ゲートがあるか (pass/fail)
- **不変条件**: 各ステップを5分以内に完了させ、ステップ間に検証ゲートを挟む
- **レビューアー**: `completion-gate.py`, plan review
- **着想**: 逆瀬川 "Coding Agent Workflow 2026" — 確率的カスケード定量モデル。対策: タスク分割粒度を「1ステップ5分以内」に保ち、失敗時は即座に再プランして残りステップに波及させない
- **autoFixable**: false
- **suggestedFix**: "ステップ分割粒度の見直し"

### autoFixable 分類基準

- **true**: lint/フォーマット/型注釈/import 解決など、ツールが機械的に修正可能
- **false**: セキュリティ/アーキテクチャ/ビジネスロジック/設計判断/行動パターンなど、人間の判断が必要

---

## Failure Channel 分類

> 着想元: Tu (2026) "Structured Test-Time Scaling" — 2つの独立失敗チャネル
> 詳細: `references/structured-test-time-scaling.md` §7

各 FM は発生メカニズムに基づき2チャネルに分類される。対策の起点が異なる。

| Channel | 定義 | 対策のレバー |
|---|---|---|
| **drift** | 制御フローが長くなるほど蓄積する誤り（スパン/深度駆動） | Mechanism I: トポロジー圧縮（DAG 化、Depth 削減） |
| **residual** | 個々のタスクノードで発生する誤り（作業駆動） | Mechanism II+III: スコープ分離 + 検証ゲート |

| FM | Channel | 根拠 |
|---|---|---|
| FM-003 Dependency Drift | drift | 依存の蓄積はフロー長に比例 |
| FM-006 Permission/Access Error | drift | セッション中の状態変化で蓄積 |
| FM-009 Resource Exhaustion | drift | リソース消費がスパンに比例 |
| FM-011 Plan Adherence Failure | drift | 計画からの逸脱が深度で拡大 |
| FM-019 Agentic Laziness | drift | 長期タスクで発生頻度が上昇 |
| FM-020 Probabilistic Cascade | drift | p^n 減衰がスパンに直結 |
| FM-001 Null Safety Violation | residual | 個別ノードの実装品質 |
| FM-002 Error Suppression | residual | 個別ノードのエラーハンドリング |
| FM-004 Type Safety Violation | residual | 個別ノードの型設計 |
| FM-005 Boundary Validation Miss | residual | 個別ノードの入力検証 |
| FM-008 Build/Compilation Failure | residual | 個別ノードのコード品質 |
| FM-010 Security Vulnerability | residual | 個別ノードのセキュリティ |
| FM-012 Information Invention | residual | 個別ノードのハルシネーション |
| FM-016 Result Fabrication | residual | 個別ノードの検証捏造 |
| FM-017 Feature Stubbing | residual | 個別ノードの不完全実装 |
| FM-018 Evaluator Rationalization | residual | 個別ノードの評価バイアス |
| FM-007 Module Resolution Failure | hybrid | drift(状態変化) + residual(パス誤り) |
| FM-013 Tool Output Misinterpretation | hybrid | drift(コンテキスト汚染) + residual(誤読) |
| FM-014 Intent Misalignment | hybrid | drift(目標ドリフト) + residual(解釈誤り) |
| FM-015 Premature Action | hybrid | drift(判断劣化) + residual(確認不足) |

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
