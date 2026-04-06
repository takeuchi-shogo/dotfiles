# Reviewer Routing Reference

レビューアーの詳細仕様。SKILL.md の Step 3 (Dispatch) で参照する。

## コアレビューアー（常時起動候補）

### code-reviewer

- **subagent_type**: `code-reviewer`
- **観点**: コード品質、バグ検出、CLAUDE.md 準拠、設計パターン
- **起動条件**: 50行以上の変更で常に起動
- **信頼度スコア**: 80以上の指摘のみ報告

### 言語固有チェックリスト（code-reviewer に注入）

言語専門の観点は独立エージェントではなく、`code-reviewer` のプロンプトにチェックリストを注入して適用する。

| 対象拡張子                   | 参照ファイル                                 | 専門観点                                           |
| ---------------------------- | -------------------------------------------- | -------------------------------------------------- |
| `.ts`, `.tsx`, `.js`, `.jsx` | `references/review-checklists/typescript.md` | 型安全性、React パターン、Node.js サーバーサイド   |
| `.go`                        | `references/review-checklists/go.md`         | Effective Go、エラーハンドリング、並行処理パターン |
| `.py`                        | `references/review-checklists/python.md`     | 型ヒント、Pythonic イディオム、例外設計            |
| `.rs`                        | `references/review-checklists/rust.md`       | 所有権、ライフタイム、Result/Option、unsafe 最小化 |

- **注入方法**: code-reviewer のプロンプトに該当チェックリストの内容を Read して含める
- **複数言語**: 変更ファイルに複数言語が含まれる場合、該当する全チェックリストを注入

### codex-reviewer

- **subagent_type**: `codex-reviewer`
- **観点**: Codex (gpt-5.4) による深い推論ベースのセカンドオピニオン
- **起動条件**: 50行以上の変更（code-reviewer と同時起動）
- **特記**: `/codex-review` スキルとは別。こちらは Agent として並列起動される

### golang-reviewer

- **subagent_type**: `golang-reviewer`
- **観点**: Go 固有の命名規約、nil/Option 安全性、アーキテクチャ、テスト網羅性
- **起動条件**: Go ファイル（`.go`）の変更が含まれる場合
- **スタイル**: デフォルト MA（簡潔・直接的）。プロンプトで MU（建設的・教育的）に切り替え可能

### edge-case-hunter

- **subagent_type**: `edge-case-hunter`
- **観点**: 境界値、nil/null パス、空コレクション、ゼロ値、レースコンディション
- **起動条件**: 50行以上の変更で常に起動
- **信頼度スコア**: 60以上の指摘を報告

### cross-file-reviewer

- **subagent_type**: `cross-file-reviewer`
- **観点**: 関数シグネチャ変更の未追従、型不整合、export/import 破損、設定値変更の未追従
- **起動条件**: 変更ファイルが2つ以上の場合のみ起動（コンテンツシグナル: `git diff --name-only` のファイル数 ≥ 2）
- **信頼度スコア**: 60以上の指摘を報告

## スペシャリストレビューアー（コンテンツベースで追加）

### silent-failure-hunter

- **subagent_type**: `silent-failure-hunter`
- **観点**: サイレント障害、エラー握り潰し、不適切な fallback
- **トリガー**: diff に `catch`, `recover`, `fallback`, `retry`, `on.*[Ee]rror`, `try {` が含まれる
- **重要度**: CRITICAL（silent failure）, HIGH（poor messages）, MEDIUM（missing context）

### type-design-analyzer

- **subagent_type**: `type-design-analyzer`
- **観点**: 型のカプセル化、不変条件の表現、型安全性
- **トリガー**: diff の追加行に `type `, `interface `, `struct `, `enum ` が含まれる
- **評価軸**: カプセル化(1-10), 不変条件表現(1-10), 有用性(1-10), 強制力(1-10)

### pr-test-analyzer

- **subagent_type**: `pr-test-analyzer`
- **観点**: テストカバレッジの質、エッジケースの網羅性
- **トリガー**: `_test.go`, `.test.ts`, `.spec.ts`, `__tests__/` のファイルが変更されている
- **評価**: 行カバレッジではなく振る舞いカバレッジを重視

### comment-analyzer

- **subagent_type**: `comment-analyzer`
- **観点**: コメント・ドキュメントの正確性、完全性、長期保守性
- **トリガー**: `/** */`, `///`, `# ` 等のコメントブロックが10行以上追加されている
- **検出対象**: コメント腐敗、WHY の欠落、不正確な記述

### nil-path-reviewer

- **subagent_type**: `general-purpose`（専用エージェントではなく汎用エージェントに専用プロンプトを渡す）
- **観点**: nil/zero パスの安全性、ポインタ dereference の防御、暗黙の前提の検出
- **トリガー**: diff の追加/変更行に以下が含まれる場合:
  - Go: ポインタ型フィールド (`*`), `nil`, `.Get()`, `option.Option`, `option.Some`, `option.None`
  - TypeScript: `undefined`, `null`, optional chaining (`?.`), non-null assertion (`!.`)
- **プロンプト**: 以下を含めること:

  ```
  コード変更に含まれるポインタ型・Option 型・nullable フィールドについて、
  以下の観点でレビューしてください:

  1. nil/undefined になりうるフィールドが dereference される箇所に防御があるか
  2. 下流の関数に nil が渡された場合に panic/crash しないか（データフロー追跡）
  3. 「呼び出し側が nil を渡さないはず」という暗黙の前提がないか
  4. Option 型の .Get() が ok チェックなしで使われていないか
  5. テストで nil/zero ケースがカバーされているか

  重要度の高い指摘のみ報告してください。
  ```

- **重要度**: CRITICAL（nil dereference で panic 可能）, HIGH（暗黙の前提に依存）, MEDIUM（テスト欠落）

### longevity-reviewer

- **subagent_type**: `general-purpose`（汎用エージェントに専用プロンプトを渡す）
- **観点**: 長期メンテナビリティ、regression リスク、暗黙の依存関係の破壊
- **トリガー**: 200行以上の変更（L規模）、または API 境界ファイル（`handler`, `controller`, `api`, `endpoint`, `route`, `server`）の変更
- **背景**: SWE-CI ベンチマーク (arXiv:2603.03823) で、技術的負債の累積がイテレーション4-6で臨界点に到達することが判明
- **プロンプト**:

  ```
  このコード変更を「6ヶ月後の保守者」の視点でレビューしてください:

  1. この変更が暗黙に前提としている不変条件は何か？その不変条件は文書化されているか？
  2. この変更が壊れるのはどのような状況か？（依存ライブラリの更新、OS変更、データ量増加等）
  3. この変更に伴い、今は壊れていないが将来壊れる可能性のあるコードはどこか？
  4. テストが「この変更が正しいこと」だけでなく「他を壊していないこと」も確認しているか？
  5. 同様の変更を次回行う場合に踏むべき手順が明確か？

  重要度の高い指摘のみ報告してください。
  各指摘には confidence score (0-100) を付与してください。
  60未満の指摘は報告不要です。
  ```

- **重要度**: CRITICAL（暗黙の不変条件が壊れる）, HIGH（将来の regression リスク）, MEDIUM（文書化の欠落）

## リスクカテゴリ別ルーティング

変更対象のリスクカテゴリ（workflow-guide.md「非対称損失の原則」参照）に応じて
レビューアー構成と Verdict 判定基準を調整する。

### リスクカテゴリ自動判定

diff の変更ファイルパスと内容から最高リスクカテゴリを判定する:

| カテゴリ | ファイルパスシグナル | 内容シグナル |
|---------|--------------------|-----------  |
| **High** | `**/migration/**`, `**/auth/**`, `**/security/**`, `**/.env*`, `**/secrets/**`, `**/deploy/**` | `DROP`, `ALTER TABLE`, `password`, `secret`, `token`, `credential`, `chmod`, `sudo` |
| **Medium** | `**/api/**`, `**/handler/**`, `**/controller/**`, `**/hooks/**`, `**/agents/**`, `**/scripts/**` | `endpoint`, `route`, `middleware`, `PreToolUse`, `PostToolUse` |
| **Low** | `**/*.md`, `**/test*/**`, `**/*_test.*`, `**/*.test.*`, `**/docs/**` | （デフォルト） |

判定ルール: **最高リスクが採用される**（1ファイルでも High ならセット全体が High）。

### レビューアー構成オーバーライド

| カテゴリ | コアレビューアー | 追加スペシャリスト | 備考 |
|---------|----------------|-------------------|------|
| **High** | code-reviewer + codex-reviewer + edge-case-hunter | **security-reviewer 必須** + silent-failure-hunter | 全レビューアーの信頼度閾値を 60→50 に引き下げ |
| **Medium** | code-reviewer + codex-reviewer + edge-case-hunter | コンテンツベースで自動選択（既存ロジック） | 標準構成 |
| **Low** | code-reviewer のみ | なし | codex-reviewer, edge-case-hunter は省略可 |

### Verdict 判定オーバーライド

| カテゴリ | NEEDS_FIX 閾値 | BLOCK 閾値 | 特記 |
|---------|----------------|-----------|------|
| **High** | CONSIDER ≥ 1 件（通常は 3 件） | MUST ≥ 1 件（変更なし） | Watch 層の指摘もユーザーに表示 |
| **Medium** | CONSIDER ≥ 3 件（変更なし） | MUST ≥ 1 件（変更なし） | 標準 |
| **Low** | CONSIDER ≥ 5 件 | MUST ≥ 1 件（変更なし） | 軽微な指摘は PASS 扱い可 |

## Agent プロンプトテンプレート

各レビューアーへ渡すプロンプトの基本構造:

```
以下のコード変更をレビューしてください。

## 変更対象
{git diff --name-only の結果}

## 差分
{git diff の結果}

## プロジェクト規約
{CLAUDE.md の内容（存在する場合）}

重要度の高い指摘のみ報告してください。
ファイルパス:行番号 の形式で具体的な場所を示してください。
```

## 信頼度スコアリング

全レビューアーは各指摘に **confidence score (0-100)** を付与する。

### スコア基準

| スコア | 基準                                              |
| ------ | ------------------------------------------------- |
| 90-100 | 確実にバグ/セキュリティ問題。コードパスで再現可能 |
| 80-89  | 高確率で問題。エッジケースや暗黙の前提に基づく    |
| 60-79  | 中程度。パターン的に問題になりやすいが確証なし    |
| 40-59  | 低確度。スタイルや好みの範囲                      |
| 0-39   | 推測レベル。根拠が薄い                            |

### フィルタリングルール（3層分類）

| 層 | スコア | ラベル | 扱い |
|----|--------|--------|------|
| Critical | 90-100 | 修正必須 | BLOCK 判定の根拠 |
| Important | 80-89 | 検討推奨 | NEEDS_FIX 判定の根拠 |
| Watch | 60-79 | 要注意 | 表示するが判定に影響しない。フィードバック収集用 |

以下の指摘は **自動除外** する（レポートに含めない）:

1. **confidence < 60** の指摘
2. **既存コードの問題**（diff の追加行以外への指摘）
3. **linter/formatter が検出すべき問題**（インデント、セミコロン等）
4. **純粋なスタイル nitpick**（命名規則の好み等、CLAUDE.md に明記がない限り）

### プロンプトへの追記

各レビューアーへのプロンプトに以下を追加:

```
各指摘には confidence score (0-100) を付与してください。
60未満の指摘は報告不要です。
既存コード（diff の追加行以外）への指摘は除外してください。
linter/formatter が検出すべき問題は除外してください。

フォーマット例:
- [95] `file.ts:42` — NullPointerException の可能性。`user` が undefined の場合に crash
- [82] `api.go:128` — エラーが握り潰されている。`err` を返すべき
- [65] `utils.py:33` — 空リスト入力時の挙動が未定義。`if not items: return []` を検討
```
