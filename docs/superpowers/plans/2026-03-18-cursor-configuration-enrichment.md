# Cursor Configuration Enrichment Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cursor IDE の設定を充実させ、MSR '26 論文が警告する品質劣化を防ぐ QA 基盤を構築する

**Architecture:** Claude Code の Progressive Disclosure 設計を Cursor ネイティブ機能（Rules/Skills/Subagents/Commands/Hooks）に適応。Always Apply（品質ゲート）→ Auto Attached（言語別）→ Agent Decides（状況判断）の3層で品質を担保する。

**Tech Stack:** Cursor MDC format, SKILL.md (Agent Skills standard), Markdown, Bash, symlink

**Spec:** `docs/superpowers/specs/2026-03-18-cursor-configuration-enrichment-design.md`

---

## File Map

### New Files (25)
| Path | Responsibility |
|------|---------------|
| `.cursor/rules/global.mdc` | 共通原則（Always Apply）— **既存ファイルの改修** |
| `.cursor/rules/quality-guard.mdc` | 品質ゲート（Always Apply）— 論文対策の核心 |
| `.cursor/rules/typescript.mdc` | TypeScript 規約（Auto Attached: `**/*.ts, **/*.tsx`） |
| `.cursor/rules/react.mdc` | React 規約（Auto Attached: `**/*.tsx, **/*.jsx`） |
| `.cursor/rules/python.mdc` | Python 規約（Auto Attached: `**/*.py`） |
| `.cursor/rules/go.mdc` | Go 規約（Auto Attached: `**/*.go`） |
| `.cursor/rules/rust.mdc` | Rust 規約（Auto Attached: `**/*.rs`） |
| `.cursor/rules/security.mdc` | セキュリティルール（Agent Decides） |
| `.cursor/rules/error-handling.mdc` | エラーハンドリング（Agent Decides） |
| `.cursor/rules/testing.mdc` | テスト規約（Agent Decides） |
| `.cursor/skills/review/SKILL.md` | コードレビュースキル |
| `.cursor/skills/commit/SKILL.md` | コミットスキル |
| `.cursor/skills/create-pr/SKILL.md` | PR 作成スキル |
| `.cursor/skills/spec/SKILL.md` | 仕様書生成スキル |
| `.cursor/skills/test-fix/SKILL.md` | テスト修正ループスキル |
| `.cursor/skills/refactor/SKILL.md` | リファクタリングスキル |
| `.cursor/skills/quality-report/SKILL.md` | 品質レポートスキル |
| `.cursor/agents/verifier.md` | 実装検証サブエージェント |
| `.cursor/agents/reviewer.md` | コードレビューサブエージェント |
| `.cursor/agents/security-checker.md` | セキュリティチェックサブエージェント |
| `.cursor/commands/review-code.md` | レビューコマンド |
| `.cursor/commands/run-tests.md` | テスト実行コマンド |
| `.cursor/commands/fix-lint.md` | lint 修正コマンド |
| `.cursor/hooks/quality-gate.sh` | 品質ゲートフックスクリプト |
| `.cursor/hooks.json` | フック設定 |

### Modified Files (1)
| Path | Change |
|------|--------|
| `.bin/symlink.sh` | Cursor symlink 対象に skills/agents/commands/hooks/hooks.json を追加 |

## Task Dependency Graph

```
Task 1 (Always Apply Rules) ──┐
Task 2 (Language Rules TS/React) ──┤
Task 3 (Language Rules Py/Go/Rust) ──┤── 全て独立、並列実行可能
Task 4 (Agent Decides Rules) ──┤
Task 5 (Skills - Core) ──┤
Task 6 (Skills - Quality) ──┤
Task 7 (Subagents) ──┤
Task 8 (Commands) ──┤
Task 9 (Hooks) ──┘
                    │
                    ▼
            Task 10 (symlink.sh + Verification) ── Task 1-9 の全完了後
```

---

## Task 1: Always Apply Rules（global.mdc 改修 + quality-guard.mdc 新規）

**Files:**
- Modify: `.cursor/rules/global.mdc`
- Create: `.cursor/rules/quality-guard.mdc`
- Reference: `.config/claude/rules/common/code-quality.md`, `.config/claude/rules/common/overconfidence-prevention.md`, `.config/claude/rules/config.md`

- [ ] **Step 1: global.mdc を改修**

既存の 42 行から ~60 行に拡充。過信防止と設定ファイルのベストプラクティスを統合。

```markdown
---
description: Global rules for all projects
globs:
alwaysApply: true
---

# Global Rules

## Role

あなたはプロダクション品質のコードを書くシニアソフトウェアエンジニア。

## IMPORTANT ルール

- 日本語で応答する
- 実装前に既存コード・設定・ドキュメントを確認する
- 曖昧なタスクは Plan Mode（Shift+Tab）で計画を立ててから編集する
- 完了を宣言する前に、変更範囲に最も近い build/test/lint を実行する
- 疑わしければ質問する。「たぶん」「おそらく」で実装に入らない

## Harness Rules

- リンター設定ファイル（.eslintrc*, biome.json, .prettierrc* 等）は変更禁止。lint 違反はコードで修正する
- `git commit --no-verify` 禁止
- タスク完了前にテスト・lint を実行して通過を確認する

## コミット規則

- conventional commit + 絵文字プレフィックス（例: ✨ feat:, 🐛 fix:, 📝 docs:, ♻️ refactor:, 🔧 chore:）

## Core Principles

- **シンプリシティ ファースト (KISS)**: 変更はできる限りシンプルに。「動作させるために最もシンプルな方法は何か」を常に問う
- **YAGNI**: 今必要なコードのみ書く。「将来使うかも」で汎用化しない
- **DRY**: 同じロジックを複数箇所に書かない。ただし文脈が異なるコードの無理な共通化は避ける
- **最小インパクト**: 必要な箇所だけ触る。無関係な差分を広げない
- **検索してから実装**: 既存の解決策がないか確認してからコードを書く

## Editing Defaults

- 変更は既存の命名規則・構成・formatter に従う
- パッケージ追加や新規 utility の前に、既存のツール・ライブラリを確認する

## Config Best Practices

- 設定値にはスキーマ検証を使う（JSON Schema / YAML schema）
- 秘密情報は絶対にファイルに含めない（環境変数 / secret manager を使う）
- 全ての値に安全なデフォルトを設ける
```

- [ ] **Step 2: quality-guard.mdc を作成**

論文対策の核心。全セッションで強制適用。

```markdown
---
description: Quality guard enforcing code complexity limits, static analysis, and review requirements. Prevents the velocity-quality degradation cycle identified in MSR'26 research.
globs:
alwaysApply: true
---

# Quality Guard

> Based on MSR '26 "Speed at the Cost of Quality" (arxiv:2511.04427):
> Cursor adoption leads to +41.6% code complexity and +30.3% static analysis warnings.
> These quality issues create a self-reinforcing cycle that reduces future velocity by up to 64.5%.

## Complexity Limits

- **関数**: 50行以内、ネスト4段以内
- **ファイル**: 400行目安、800行上限。超過時は分割を検討
- **認知的複雑度**: 新規関数は低複雑度を維持。条件分岐のネストより早期リターンを使う

## Static Analysis

- 変更後は必ず lint / type チェックを実行し、全パスを確認してから完了を宣言する
- 新しい警告を導入しない。既存の警告を増やす変更は許可しない
- auto-fix 可能な問題は自動修正する

## Code Duplication

- DRY 原則を厳守。同一ロジックの重複を見つけたら共通化する
- ただし、似ているだけで文脈が異なるコードの無理な共通化は避ける

## Review & Planning

- 3ファイル以上の変更は Plan Mode（Shift+Tab）で計画を立ててから実装する
- レビューなしのマージ禁止
- 大規模変更は段階的に行い、各段階でテストを通過させる

## Before Completion Checklist

1. [ ] lint / type チェックがパスする
2. [ ] 関連テストがパスする
3. [ ] 新しい警告が導入されていない
4. [ ] 関数が50行・ネスト4段以内である
5. [ ] ファイルが800行以内である
```

- [ ] **Step 3: 検証**

Run: `wc -l .cursor/rules/global.mdc .cursor/rules/quality-guard.mdc`
Expected: 各ファイル 500行以内

- [ ] **Step 4: コミット**

```bash
git add .cursor/rules/global.mdc .cursor/rules/quality-guard.mdc
git commit -m "✨ feat(cursor): add Always Apply rules — global + quality-guard

Quality guard implements defenses against MSR'26 paper findings:
complexity limits, static analysis requirements, review gates."
```

---

## Task 2: Language Rules — TypeScript + React

**Files:**
- Create: `.cursor/rules/typescript.mdc`
- Create: `.cursor/rules/react.mdc`
- Reference: `.config/claude/rules/typescript.md` (259行), `.config/claude/rules/react.md` (100行)

- [ ] **Step 1: typescript.mdc を作成**

Claude Code の `rules/typescript.md` (259行) を Cursor MDC 形式に適応。500行以内に収める。

```markdown
---
description: TypeScript coding standards — strict typing, structural patterns, Effective TypeScript 2nd Ed. principles. Applied when editing TypeScript files.
globs: "**/*.ts, **/*.tsx"
alwaysApply: false
---

# TypeScript Rules

## Type System Fundamentals

- 構造的型付け（duck typing）を理解して活用する
- 型は集合: `never`（空集合）→ リテラル → ユニオン → `unknown`（全体集合）
- `any` 禁止。`unknown` + 型ガードを使う
- `String`, `Number` 等のオブジェクトラッパー型禁止。`string`, `number` を使う
- 型アサーション (`as`) は最小限に。`satisfies` を優先

## tsconfig 必須設定

```json
{
  "strict": true,
  "noUncheckedIndexedAccess": true,
  "exactOptionalPropertyTypes": true,
  "verbatimModuleSyntax": true,
  "isolatedModules": true,
  "noUnusedLocals": true,
  "noUnusedParameters": true
}
```

## Type Inference

- コンパイラの推論に任せる（ローカル変数の型注釈は不要）
- 公開 API の戻り値型は明示する
- `import type` で型のみのインポートを使う

## Type Design

- 判別共用体（Discriminated Union）を優先。タグで分岐
- `satisfies` 演算子で型安全な初期化
- null は境界に押し出す（内部ロジックでは non-null を維持）
- 入力は寛容に、出力は厳格に
- オプショナルプロパティは限定的に使う

## Utility Types

- `Pick`, `Omit`, `Partial`, `Required`, `Record`, `Readonly` を活用
- `as const` でリテラル型を維持
- Branded Types で newtype パターン: `type UserId = string & { readonly __brand: unique symbol }`

## Nullish Handling

- `??`（nullish coalescing）、`?.`（optional chaining）を使う
- `exactOptionalPropertyTypes` で `undefined` と「未定義」を区別

## Error Handling

- Zod でランタイム検証。外部データの境界で使用
- Result パターンで型安全なエラー処理

## Documentation

- TSDoc コメント（`/** */`）を公開 API に付ける
- 型情報をコメントで繰り返さない
```

- [ ] **Step 2: react.mdc を作成**

```markdown
---
description: React and Next.js component patterns — hooks rules, Server Components, composition, memoization. Applied when editing React component files.
globs: "**/*.tsx, **/*.jsx"
alwaysApply: false
---

# React Rules

## Hooks

- 条件分岐・ループ・ネスト関数内で呼ばない
- `useRef` はリレンダー不要な値の保持に使う
- カスタムフックは `use` プレフィックス必須

## useEffect の制限

- `useEffect` は原則禁止。以下の代替手段を使う:
  1. インライン計算（派生状態）
  2. データフェッチライブラリ（useQuery / useSWR）
  3. イベントハンドラ
  4. マウント時の外部同期のみ許可（useMountEffect）
  5. key でリセット

## Composition

- children / render props でコンポーネント合成
- Container + Presentational に分離
- Context は限定的に使う（テーマ、認証、ロケールのみ）
- 状態はコロケーション（使う場所の近くに配置）

## Server Components (Next.js)

- デフォルトは Server Component
- `"use client"` はインタラクションが必要な場合のみ
- クライアント境界はできるだけ下（leaf に近く）に置く
- サーバーでデータフェッチし、シリアライズ可能な props で渡す

## Memoization

- `useMemo` / `useCallback` はデフォルトで使わない。計測してから
- React Compiler (React 19+) が利用可能なら有効化
- `React.memo()` は頻繁にリレンダーされるコンポーネントのみ

## Keys & Lists

- 動的リストに配列インデックスを key にしない
- 安定した識別子（id / slug）を使う
- key は作成時に生成、レンダー時ではない
```

- [ ] **Step 3: 検証**

Run: `wc -l .cursor/rules/typescript.mdc .cursor/rules/react.mdc`
Expected: 各ファイル 500行以内

- [ ] **Step 4: コミット**

```bash
git add .cursor/rules/typescript.mdc .cursor/rules/react.mdc
git commit -m "✨ feat(cursor): add TypeScript + React auto-attached rules

Adapted from Claude Code rules with Cursor-native MDC format.
TypeScript: strict typing, structural patterns, Effective TS 2nd Ed.
React: hooks rules, Server Components, composition patterns."
```

---

## Task 3: Language Rules — Python + Go + Rust

**Files:**
- Create: `.cursor/rules/python.mdc`
- Create: `.cursor/rules/go.mdc`
- Create: `.cursor/rules/rust.mdc`
- Reference: `.config/claude/rules/python.md` (144行), `.config/claude/rules/go.md` (232行), `.config/claude/rules/rust.md` (176行)

- [ ] **Step 1: python.mdc を作成**

Claude Code の `rules/python.md` を Cursor MDC 形式に適応。

```markdown
---
description: Python coding standards — type hints, uv package management, pytest, Pythonic idioms. Applied when editing Python files.
globs: "**/*.py"
alwaysApply: false
---

# Python Rules

## Project Structure

- src レイアウト + `pyproject.toml` + `uv.lock`
- ML/DS: `configs/`, `scripts/`, `src/` を分離
- パッケージ管理: `uv` を使用。`requirements.txt` / `setup.py` は非推奨

## Type Hints

- 公開関数には型ヒント必須
- `T | None` を使う（`Optional[T]` より推奨）
- `TypedDict` / `@dataclass` を dict より優先
- データモデル: `@dataclass(frozen=True)` or Pydantic `BaseModel`

## Error Handling

- 素の `except:` 禁止。具体的な例外を指定
- ログ出力 + reraise パターン
- `with` 文でリソース管理

## Pythonic Idioms

- リスト/辞書/集合内包表記を活用
- `enumerate`, `zip`, `any`, `all` を使う
- EAFP（許可より謝罪）パターン
- `from module import *` 禁止
- ミュータブルなデフォルト引数禁止

## Security

- `eval` / `exec` 禁止
- 信頼されないデータに `pickle` 禁止
- `shell=True` 禁止。ORM を使う

## Testing

- pytest + `@pytest.mark.parametrize`
- fixture / conftest.py でセットアップ共有
- 具体的なアサーション（`assert x == 42`、`assert x` ではない）
```

- [ ] **Step 2: go.mdc を作成**

```markdown
---
description: Go coding standards — error handling, naming conventions, concurrency patterns, table-driven tests. Applied when editing Go files.
globs: "**/*.go"
alwaysApply: false
---

# Go Rules

## Error Handling

- `err != nil` を必ずチェック。コンテキスト付きでラップ: `fmt.Errorf("doing X: %w", err)`
- `errors.Is()` / `errors.As()` で判定。型スイッチではなくエラーチェーンを使う
- センチネルエラーはパッケージレベルで定義: `var ErrNotFound = errors.New("not found")`
- エラーメッセージ: 小文字、句読点なし

## Naming

- MixedCaps のみ（アンダースコア不可）
- パッケージ名: 短く（user, http）、汎用禁止（util, common）
- パッケージ名との冗長排除: `user.New()` not `user.NewUser()`
- 頭字語は全大文字: ID, URL, API, HTTP
- レシーバー: 1-2文字の略称（s for Server）、一貫して使う
- Getter: `Owner()` not `GetOwner()`

## context.Context

- 第一引数に配置。全関数で伝播
- `WithTimeout` + `defer cancel()`
- 構造体に保持しない

## Concurrency

- 明確な終了パスを設計する
- `errgroup` でエラー伝播
- 通信にはチャネル、状態保護には Mutex
- 同期関数を先に書き、非同期は後から

## Function Design

- Early Return パターン
- CQS（コマンド・クエリ分離）
- ポインタはサイズではなく意味で使い分ける

## Testing

- テーブル駆動テスト + `t.Run()`
- `t.Helper()` でヘルパー関数をマーク
- `t.Parallel()` で並列実行
- アサーションメッセージに十分な情報を含める

## Modern Go (1.21+)

- 標準ライブラリの `slices` / `maps` パッケージ
- ループ変数のスコーピング修正を活用
- `log/slog` で構造化ログ
```

- [ ] **Step 3: rust.mdc を作成**

```markdown
---
description: Rust coding standards — ownership, error handling, type system, concurrency. Applied when editing Rust files.
globs: "**/*.rs"
alwaysApply: false
---

# Rust Rules

## Ownership & Borrowing

- clone より borrow を優先
- 関数引数は `&str`（`String` ではなく）
- `Rc` / `Arc` は必要な場合のみ
- `Cow<'_, str>` で所有/借用の柔軟性

## Error Handling

- ライブラリ: `Result<T, E>` + `thiserror` でドメインエラー
- アプリケーション: `anyhow::Result` + `.context()` でコンテキスト追加
- `?` 演算子で伝播

## Pattern Matching

- `if let` チェーンより `match` を優先
- `_` は控えめに使う
- `if let` / `let else` は単一バリアント判定に

## Type System

- Newtype パターンで型安全性
- bool フラグより enum
- `From` / `Into`, `TryFrom` / `TryInto` を実装
- 3+ オプショナルには Builder パターン

## Standard Traits

- `Debug`: 全型に実装
- `Clone`: 全フィールドが Clone なら
- `Copy`: 小さい型のみ
- `PartialEq` + `Eq`, `Hash`（キーに使う場合）
- `Default`, `serde::Serialize/Deserialize`

## Concurrency

- tokio チャネル > Mutex + 共有状態
- async 内で blocking しない
- spawn にはエラーハンドリングを含める

## Visibility

- デフォルト private
- `pub(crate)` で内部公開
- private → public はマイナー、public → private はメジャー変更

## Testing

- `#[cfg(test)] mod tests` でユニットテスト
- doc tests + integration tests
- プロパティテスト（proptest / quickcheck）

## Tools

- `cargo fmt`, `cargo clippy`, `cargo test`
- リフレクション回避、最適化前にプロファイル
```

- [ ] **Step 4: 検証**

Run: `wc -l .cursor/rules/python.mdc .cursor/rules/go.mdc .cursor/rules/rust.mdc`
Expected: 各ファイル 500行以内

- [ ] **Step 5: コミット**

```bash
git add .cursor/rules/python.mdc .cursor/rules/go.mdc .cursor/rules/rust.mdc
git commit -m "✨ feat(cursor): add Python, Go, Rust auto-attached rules

Adapted from Claude Code language rules with Cursor MDC format.
Python: type hints, uv, pytest. Go: error handling, naming, concurrency.
Rust: ownership, thiserror/anyhow, trait design."
```

---

## Task 4: Agent Decides Rules（security + error-handling + testing）

**Files:**
- Create: `.cursor/rules/security.mdc`
- Create: `.cursor/rules/error-handling.mdc`
- Create: `.cursor/rules/testing.mdc`
- Reference: `.config/claude/rules/common/security.md` (137行), `.config/claude/rules/common/error-handling.md` (74行), `.config/claude/rules/common/testing.md` (85行), `.config/claude/rules/test.md` (66行)

- [ ] **Step 1: security.mdc を作成**

```markdown
---
description: Security rules based on OWASP Top 10. Apply when writing authentication, authorization, input validation, API endpoints, database queries, or handling secrets and sensitive data.
globs:
alwaysApply: false
---

# Security Rules

## Mandatory Checks

- 秘密情報のハードコード禁止（API キー、パスワード、トークン）
- 全ユーザー入力をバリデーション（型、範囲、長さ、フォーマット）
- SQL インジェクション防止: パラメータ化クエリのみ使用
- XSS 防止: 出力エスケープ + CSP ヘッダー
- CSRF 防止: トークンベースの保護
- エラーメッセージに内部情報を含めない

## Secret Management

- 環境変数 or シークレットマネージャーを使用
- `.env*` は `.gitignore` に含める
- `.env.example` にプレースホルダーを配置
- 短命トークンを優先

## Input Validation

- 信頼境界（外部入力、API レスポンス、ファイル読み込み）で検証
- ホワイトリスト方式を優先（許可リスト > 拒否リスト）
- 検証ライブラリを使用（Zod, joi, pydantic 等）

## Authentication & Authorization

- パスワード: bcrypt / argon2 でハッシュ化
- セッション: HTTP-only, Secure, SameSite cookie
- JWT: 短い有効期限 + リフレッシュトークン
- 最小権限の原則

## Dependencies

- 既知の脆弱性をチェック（`npm audit`, `pip audit`, `govulncheck`）
- ロックファイルをコミット
- メジャーバージョンアップは変更内容を確認

## Security Response

- セキュリティ問題を発見したら即座に報告
- 修正前に影響範囲を評価
```

- [ ] **Step 2: error-handling.mdc を作成**

```markdown
---
description: Error handling patterns — explicit handling, fail fast, structured logging, user-friendly messages. Apply when implementing error handling, logging, or recovery logic.
globs:
alwaysApply: false
---

# Error Handling Rules

## Principles

- **明示的に処理**: エラーを握りつぶさない
- **早期失敗**: 問題を検出したらすぐに報告
- **構造化ログ**: コンテキスト付きでログ出力
- **ユーザーフレンドリー**: 技術的詳細を隠し、行動可能なメッセージを表示
- **回復可能なら回復**: リトライ、フォールバック、グレースフルデグラデーション

## DO

- 型付きエラーを使う（TypeScript: Result パターン、Go: error wrapping、Rust: thiserror）
- エラーにコンテキストを付与（何をしようとしていたか）
- エラー境界を設ける（React: ErrorBoundary、Go: recover）
- 重要な操作のリトライにはバックオフを使う

## DON'T

- catch して何もしない（`catch(e) {}`）
- 機密情報をログに含める
- スタックトレースをユーザーに表示する
- 制御フローに例外を使う
- 全ての例外を同一の catch で処理する
```

- [ ] **Step 3: testing.mdc を作成**

```markdown
---
description: Testing standards — AAA pattern, naming, mock strategy, coverage targets. Apply when writing tests, designing test strategy, or reviewing test code.
globs:
alwaysApply: false
---

# Testing Rules

## Coverage Target

- 80%+ を目標
- テスト種別: Unit（高速、分離）、Integration（外部依存含む）、E2E（ユーザーフロー）

## TDD Workflow

1. RED: 失敗するテストを書く
2. GREEN: テストを通す最小限の実装
3. IMPROVE: リファクタリング（テストは通したまま）

## AAA Pattern

- **Arrange**: セットアップ（テストデータ、モック）
- **Act**: 実行（テスト対象を呼び出す）
- **Assert**: 検証（期待値と比較）

## Test Naming

テスト名に WHAT / WHEN / EXPECTED RESULT を含める:
- `test_returns_empty_list_when_no_items_found`
- `should render error message when API fails`

## Mock Strategy

- 外部依存のみモック（API、DB、ファイルシステム、時刻）
- **内部ロジックはモックしない**
- 依存性注入でテスト容易性を確保
- テスト間でモックをリセット

## Assertions

- 1テスト1論理アサーション
- 具体的な値で比較（truthiness ではなく equality）
- エラーケースとエッジケースをテスト
- スナップショットテストは UI のみ

## Test Data

- マジックナンバー / マジックストリング禁止
- ファクトリ関数 / fixture で生成
- 現実的だが決定的な値を使う
```

- [ ] **Step 4: 検証**

Run: `wc -l .cursor/rules/security.mdc .cursor/rules/error-handling.mdc .cursor/rules/testing.mdc`
Expected: 各ファイル 500行以内

- [ ] **Step 5: コミット**

```bash
git add .cursor/rules/security.mdc .cursor/rules/error-handling.mdc .cursor/rules/testing.mdc
git commit -m "✨ feat(cursor): add Agent Decides rules — security, error-handling, testing

Security: OWASP Top 10 based. Error handling: fail-fast, structured logging.
Testing: TDD workflow, AAA pattern, 80%+ coverage target."
```

---

## Task 5: Skills — Core（review + commit + create-pr）

**Files:**
- Create: `.cursor/skills/review/SKILL.md`
- Create: `.cursor/skills/commit/SKILL.md`
- Create: `.cursor/skills/create-pr/SKILL.md`

- [ ] **Step 1: ディレクトリ作成**

Run: `mkdir -p .cursor/skills/review .cursor/skills/commit .cursor/skills/create-pr`

- [ ] **Step 2: review/SKILL.md を作成**

```markdown
---
name: review
description: コード変更のレビューを実行する。品質・セキュリティ・複雑度をチェックし、severity 付きで報告する。コード変更後に使用。
---

# Code Review Skill

## When to Use

- コード変更後のレビュー
- PR 作成前の品質確認
- リファクタリング後の検証

## Workflow

1. `git diff` で変更を取得（unstaged + staged）
2. 変更規模を判定:
   - **S** (1-30行): 簡易チェック（品質のみ）
   - **M** (31-100行): 品質 + セキュリティ
   - **L** (101行+): 全軸レビュー + reviewer サブエージェントに委譲
3. 変更ファイルの元のコードを読み、差分のコンテキストを理解する
4. チェック項目:
   - **品質**: 複雑度増加、命名規約、DRY 違反、エラーハンドリング
   - **セキュリティ**: 入力検証、秘密情報、注入攻撃パターン
   - **テスト**: 変更に対応するテストの有無、カバレッジ
5. 発見事項を severity 付きで報告:
   - 🔴 **Critical**: 修正必須（セキュリティ、データ損失リスク）
   - 🟡 **Warning**: 修正推奨（品質劣化、複雑度増加）
   - 🔵 **Info**: 改善提案（命名、構造）

## Output Format

```markdown
## Review Report

### Summary
- Files changed: N
- Lines added/removed: +X/-Y
- Severity: N critical, N warning, N info

### Findings
#### 🔴 Critical
- [file:line] Description

#### 🟡 Warning
- [file:line] Description

#### 🔵 Info
- [file:line] Description
```
```

- [ ] **Step 3: commit/SKILL.md を作成**

```markdown
---
name: commit
description: 変更を分析し conventional commit + 絵文字プレフィックスでコミットする。コミット前に lint/test の通過を確認する。
---

# Commit Skill

## When to Use

- コード変更をコミットする時
- 適切なコミットメッセージを生成したい時

## Workflow

1. `git diff --staged` で staged の変更を確認。なければ `git status` で unstaged を表示
2. 変更の性質を判定:
   - `✨ feat:` — 新機能
   - `🐛 fix:` — バグ修正
   - `📝 docs:` — ドキュメント
   - `♻️ refactor:` — リファクタリング
   - `🔧 chore:` — 雑務
   - `🧪 test:` — テスト
   - `🎨 style:` — フォーマット
   - `⚡ perf:` — パフォーマンス
3. lint/test を実行して通過を確認
4. コミットメッセージを生成:
   - 1行目: `emoji type(scope): summary` (72文字以内)
   - 空行
   - 本文: なぜこの変更が必要か（what ではなく why）
5. `git commit` を実行

## Rules

- `--no-verify` 禁止
- 機密ファイル（.env, credentials 等）をコミットしない
- 1コミット = 1目的
```

- [ ] **Step 4: create-pr/SKILL.md を作成**

```markdown
---
name: create-pr
description: ブランチの全コミットを分析し、タイトル・本文・テストプランを自動生成して PR を作成する。
---

# Create PR Skill

## When to Use

- 機能実装が完了し PR を作成する時
- ブランチの変更をまとめてレビューに出す時

## Workflow

1. 状態確認:
   - `git status` で未コミットの変更がないか確認
   - `git log main..HEAD --oneline` で全コミットを把握
   - `git diff main..HEAD --stat` で変更ファイル一覧
2. PR 情報を生成:
   - **タイトル**: 70文字以内、変更の目的を簡潔に
   - **Summary**: 1-3 bullet points で主要な変更を説明
   - **Test Plan**: テスト手順のチェックリスト
3. リモートにプッシュ（必要なら）: `git push -u origin HEAD`
4. PR 作成:
   ```bash
   gh pr create --title "title" --body "$(cat <<'EOF'
   ## Summary
   - Change 1
   - Change 2

   ## Test Plan
   - [ ] Test step 1
   - [ ] Test step 2
   EOF
   )"
   ```
5. PR URL を返す
```

- [ ] **Step 5: コミット**

```bash
git add .cursor/skills/
git commit -m "✨ feat(cursor): add core skills — review, commit, create-pr

Review: size-based depth (S/M/L), severity reporting.
Commit: conventional commit + emoji, lint/test gate.
Create-PR: auto-generated title/summary/test plan."
```

---

## Task 6: Skills — Quality（spec + test-fix + refactor + quality-report）

**Files:**
- Create: `.cursor/skills/spec/SKILL.md`
- Create: `.cursor/skills/test-fix/SKILL.md`
- Create: `.cursor/skills/refactor/SKILL.md`
- Create: `.cursor/skills/quality-report/SKILL.md`

- [ ] **Step 1: ディレクトリ作成**

Run: `mkdir -p .cursor/skills/spec .cursor/skills/test-fix .cursor/skills/refactor .cursor/skills/quality-report`

- [ ] **Step 2: spec/SKILL.md を作成**

```markdown
---
name: spec
description: ユーザーのアイデアをインタビュー形式で深掘りし、構造化された仕様書（目的、要件、受け入れ基準、制約）を生成する。実装前に使用。
---

# Spec Generation Skill

## When to Use

- 新機能の実装前
- 要件が曖昧な時
- 複数の実装方法がある時

## Workflow

1. ユーザーのアイデアを確認
2. 1つずつ明確化の質問をする（多肢選択を優先）:
   - 目的: 何を達成したいか
   - ユーザー: 誰が使うか
   - 制約: 技術的・時間的制約
   - 成功基準: どうなれば完成か
3. 2-3 のアプローチを提案（トレードオフ付き、推奨を明示）
4. 仕様書を生成:
   ```markdown
   # [Feature Name] Spec
   ## Goal
   ## Requirements
   ## Acceptance Criteria
   ## Constraints
   ## Out of Scope
   ```
5. プロジェクトの `docs/specs/` に保存
```

- [ ] **Step 3: test-fix/SKILL.md を作成**

```markdown
---
name: test-fix
description: テストを実行し、失敗を分析して修正する。修正→再実行→全パスまでループする（最大3イテレーション）。
---

# Test Fix Loop Skill

## When to Use

- テストが失敗している時
- CI が red の時
- リファクタリング後にテストを通したい時

## Workflow

1. テストフレームワークを自動検出:
   - `package.json` → jest / vitest / mocha
   - `pyproject.toml` / `pytest.ini` → pytest
   - `go.mod` → go test
   - `Cargo.toml` → cargo test
2. 全テスト実行、失敗を収集
3. 各失敗を分類:
   - **Type Error**: 型の不一致
   - **Logic Error**: 期待値と実値の不一致
   - **Runtime Error**: 例外・パニック
   - **Flaky**: 非決定的な失敗
4. 根本原因を分析し、修正を実装
5. 再実行して確認
6. 最大3イテレーション。超えたらユーザーに報告:
   - 修正できなかった失敗の一覧
   - 推定される原因
   - 推奨される次のステップ

## Rules

- テスト自体を変更して通すのは最終手段
- 実装コードを修正してテストを通す
- Flaky テストは原因を報告し、修正を提案
```

- [ ] **Step 4: refactor/SKILL.md を作成**

```markdown
---
name: refactor
description: 安全なリファクタリングを実行する。テスト通過を確認→段階的変更→各段階でテスト再実行。
---

# Safe Refactoring Skill

## When to Use

- コードの構造改善が必要な時
- 関数やファイルが大きくなりすぎた時
- 重複コードの共通化

## Workflow

1. リファクタリング対象と目標を確認:
   - 何を変えるか（ファイル分割、関数抽出、名前変更 等）
   - なぜ変えるか（複雑度、重複、テスト容易性 等）
2. 安全ネットの確認:
   - 既存テストを実行し、全パスを確認
   - テストがなければ、まずテストを追加
3. 段階的にリファクタリング:
   - 1ステップ = 1つの変換（関数抽出 OR 名前変更 OR ファイル分割）
   - 各ステップ後にテスト再実行
4. 変更前後の比較を報告:
   - 変更したファイル一覧
   - 削減した行数 / 複雑度
   - テスト結果

## Rules

- 動作を変えない（リファクタリングの定義）
- テストなしのリファクタリング禁止
- 1ステップ1コミット
```

- [ ] **Step 5: quality-report/SKILL.md を作成**

```markdown
---
name: quality-report
description: プロジェクトの品質メトリクス（静的解析警告、コード複雑度、重複密度）をレポートする。MSR'26 論文の3指標を計測。
---

# Quality Report Skill

## When to Use

- プロジェクトの品質状態を把握したい時
- 品質劣化の傾向を検出したい時
- リファクタリングの優先度を決めたい時

## Metrics (MSR '26 Paper Indicators)

1. **Static Analysis Warnings**: lint 警告数（reliability, maintainability, security）
2. **Code Complexity**: ファイル別の行数、関数の最大行数、ネスト深度
3. **Duplicate Line Density**: 重複コードブロックの割合

## Workflow

1. lint を実行し警告を集計:
   - TypeScript: `npx eslint . --format json` or `npx biome check .`
   - Python: `ruff check . --output-format json`
   - Go: `golangci-lint run --out-format json`
   - Rust: `cargo clippy --message-format json`
2. ファイル別の行数と複雑度を分析:
   - 400行以上のファイルをリストアップ
   - 50行以上の関数をリストアップ
3. 重複コードを検出（利用可能なツールがあれば）
4. レポートを生成:
   ```markdown
   # Quality Report — [Date]
   ## Summary
   - Total warnings: N (reliability: X, maintainability: Y, security: Z)
   - Files over 400 lines: N
   - Functions over 50 lines: N
   - Estimated duplicate density: X%
   ## Top Issues
   ## Trend (vs previous report)
   ```
5. プロジェクトの `docs/quality/` に保存
6. 前回レポートが存在すれば差分を表示し、劣化があれば警告
```

- [ ] **Step 6: コミット**

```bash
git add .cursor/skills/
git commit -m "✨ feat(cursor): add quality skills — spec, test-fix, refactor, quality-report

Spec: interview-driven PRD generation.
Test-fix: 3-iteration auto-fix loop.
Refactor: test-guarded incremental refactoring.
Quality-report: MSR'26 paper metrics (warnings, complexity, duplication)."
```

---

## Task 7: Subagents（verifier + reviewer + security-checker）

**Files:**
- Create: `.cursor/agents/verifier.md`
- Create: `.cursor/agents/reviewer.md`
- Create: `.cursor/agents/security-checker.md`

- [ ] **Step 1: ディレクトリ作成**

Run: `mkdir -p .cursor/agents`

- [ ] **Step 2: verifier.md を作成**

```markdown
---
name: verifier
description: 実装完了を独立検証する。テスト実行、lint チェック、要件照合を行う。タスク完了前や /review 実行時に自動委譲される。
model: inherit
readonly: false
---

# Implementation Verifier

あなたは実装の完了を独立的に検証するエージェントです。
メインエージェントが「完了」と主張していても、自分の目で確認してください。

## 検証手順

1. **変更ファイルの特定**: `git diff --name-only` で変更ファイルを把握
2. **テスト実行**: 変更に関連するテストを実行し、全パスを確認
3. **lint / type チェック**: プロジェクトの lint を実行し、新しい警告がないか確認
4. **要件照合**: メインエージェントのタスク説明と実際の変更を比較
   - 要求された機能が全て実装されているか
   - 余分な変更が含まれていないか
5. **エッジケース**: 見落とされがちなケースを指摘
   - 空入力、null、境界値
   - エラーパス
   - 並行処理の安全性

## 報告フォーマット

```markdown
## Verification Result: ✅ PASS / ❌ FAIL

### Tests
- Passed: N / Total: M

### Lint
- Warnings: N (new: X)

### Requirements
- [✅/❌] Requirement 1
- [✅/❌] Requirement 2

### Edge Cases
- [concern] Description
```
```

- [ ] **Step 3: reviewer.md を作成**

```markdown
---
name: reviewer
description: コード品質をレビューする。複雑度、命名、DRY、セキュリティを評価。コード変更後に /review スキルから委譲される。読み取り専用。
model: inherit
readonly: true
---

# Code Quality Reviewer

あなたはコード品質をレビューする読み取り専用エージェントです。
コードを変更せず、指摘のみを行います。

## MSR '26 論文の知見を反映

- コード複雑度の増加を重点的にチェック（+41.6% の傾向を防ぐ）
- 静的解析警告パターンの検出（+30.3% の傾向を防ぐ）
- 重複コードの検出

## レビュー観点

1. **複雑度**: 関数の行数、ネスト深度、条件分岐の数
2. **命名**: 変数名・関数名の明確さ、規約準拠
3. **DRY**: 重複コード、共通化の機会
4. **エラーハンドリング**: 例外処理の適切さ、エラーの握りつぶし
5. **型安全性**: 型の適切さ、any の使用、型ガード
6. **セキュリティ**: 入力検証、秘密情報、注入攻撃

## 報告フォーマット

各指摘は行番号付きで報告:

```markdown
## Review Findings

### 🔴 Critical (N)
- `file.ts:42` — Description

### 🟡 Warning (N)
- `file.ts:85` — Description

### 🔵 Info (N)
- `file.ts:120` — Description

### Complexity Summary
- Max function length: N lines (limit: 50)
- Max nesting: N levels (limit: 4)
- New warnings introduced: N
```
```

- [ ] **Step 4: security-checker.md を作成**

```markdown
---
name: security-checker
description: OWASP Top 10 に基づくセキュリティレビュー。認証、入力検証、秘密情報を監査。セキュリティ関連コード変更時に /review スキルから委譲される。読み取り専用。
model: inherit
readonly: true
---

# Security Checker

あなたは OWASP Top 10 に基づいてセキュリティレビューを行う読み取り専用エージェントです。

## チェック項目

### A01: Broken Access Control
- 認証チェックの漏れ
- 権限昇格の可能性
- CORS 設定の問題

### A02: Cryptographic Failures
- 平文での秘密情報保存
- 弱い暗号アルゴリズム
- ハードコードされたキー/パスワード

### A03: Injection
- SQL インジェクション（パラメータ化されていないクエリ）
- XSS（エスケープされていない出力）
- コマンドインジェクション（`shell=True`, `exec`, `eval`）

### A04: Insecure Design
- 入力検証の欠如
- レート制限の欠如
- 安全でないデフォルト値

### A05-A10: その他
- セキュリティ設定ミス、脆弱な依存関係、認証失敗、データ整合性、ログ・監視の不足

## 報告フォーマット

```markdown
## Security Review

### Risk Level: 🟢 Low / 🟡 Medium / 🔴 High

### Findings
- [A0X] `file:line` — Description — Severity — Recommendation
```
```

- [ ] **Step 5: コミット**

```bash
git add .cursor/agents/
git commit -m "✨ feat(cursor): add subagents — verifier, reviewer, security-checker

Verifier: independent completion verification with test/lint/requirements check.
Reviewer: readonly quality review reflecting MSR'26 paper insights.
Security-checker: readonly OWASP Top 10 audit."
```

---

## Task 8: Commands（review-code + run-tests + fix-lint）

**Files:**
- Create: `.cursor/commands/review-code.md`
- Create: `.cursor/commands/run-tests.md`
- Create: `.cursor/commands/fix-lint.md`

- [ ] **Step 1: ディレクトリ作成**

Run: `mkdir -p .cursor/commands`

- [ ] **Step 2: review-code.md を作成**

```markdown
Review the current code changes for quality and security issues.

1. Run `git diff` to see all current changes (staged and unstaged)
2. For each changed file, read the original code to understand context
3. Check for quality issues:
   - Functions exceeding 50 lines
   - Nesting deeper than 4 levels
   - Files exceeding 400 lines
   - Duplicate code patterns
   - Poor naming or unclear logic
4. Check for security issues:
   - Hardcoded secrets (API keys, passwords, tokens)
   - Unvalidated user input
   - SQL injection patterns
   - XSS vulnerabilities
5. Check test coverage:
   - Are there tests for the changed code?
   - Do existing tests still pass?
6. Report findings with severity:
   - 🔴 Critical: Must fix before commit
   - 🟡 Warning: Should fix
   - 🔵 Info: Suggestion for improvement
```

- [ ] **Step 3: run-tests.md を作成**

```markdown
Run all project tests, analyze failures, and fix them.

1. Detect the test framework:
   - Check `package.json` for jest/vitest/mocha
   - Check `pyproject.toml` or `pytest.ini` for pytest
   - Check `go.mod` for Go
   - Check `Cargo.toml` for Rust
2. Run the full test suite
3. If all tests pass, report success
4. If tests fail:
   a. Analyze each failure's root cause
   b. Classify: type error, logic error, runtime error, or flaky
   c. Fix the implementation (not the test) to make it pass
   d. Re-run tests to verify
5. Repeat up to 3 times if needed
6. Report final results with any remaining failures
```

- [ ] **Step 4: fix-lint.md を作成**

```markdown
Fix all lint warnings and errors in the project.

1. Detect the linter:
   - TypeScript: eslint, biome, or tsc
   - Python: ruff, flake8, or mypy
   - Go: golangci-lint or go vet
   - Rust: cargo clippy
2. Run the linter and collect all warnings/errors
3. Classify each issue:
   - Auto-fixable: apply `--fix` flag
   - Manual fix needed: fix one by one
4. Apply auto-fixes first:
   - `npx eslint . --fix` or `npx biome check . --write`
   - `ruff check . --fix`
   - `cargo clippy --fix`
5. Fix remaining manual issues
6. Re-run linter to confirm all clear
7. Report: total fixed, any remaining issues
```

- [ ] **Step 5: コミット**

```bash
git add .cursor/commands/
git commit -m "✨ feat(cursor): add commands — review-code, run-tests, fix-lint

Simple workflow templates for common development tasks.
review-code: quality + security check.
run-tests: detect framework, run, analyze failures, fix.
fix-lint: auto-fix + manual fix loop."
```

---

## Task 9: Hooks（hooks.json + quality-gate.sh）

**Files:**
- Create: `.cursor/hooks.json`
- Create: `.cursor/hooks/quality-gate.sh`

- [ ] **Step 1: ディレクトリ作成**

Run: `mkdir -p .cursor/hooks`

- [ ] **Step 2: hooks.json を作成**

```json
{
  "version": 1,
  "hooks": {
    "stop": [
      {
        "command": "bash .cursor/hooks/quality-gate.sh"
      }
    ]
  }
}
```

- [ ] **Step 3: quality-gate.sh を作成**

```bash
#!/usr/bin/env bash
# Quality Gate Hook — runs on agent stop
# Checks for lint issues in uncommitted changes and asks agent to fix them.
# Source: Cursor blog "Best practices for coding with agents" (2026-01-09)

set -euo pipefail

# Read context from stdin (Cursor passes agent context as JSON)
CONTEXT=$(cat)

# Counter file: use project root hash to isolate per-project
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
COUNTER_FILE="/tmp/cursor-quality-gate-$(echo "$REPO_ROOT" | md5sum | cut -c1-8)"

# Check if there are uncommitted changes
if ! git diff --quiet HEAD 2>/dev/null; then
  # Detect linter
  LINT_CMD=""
  if [ -f "package.json" ]; then
    if command -v npx &>/dev/null; then
      if npx biome --version &>/dev/null 2>&1; then
        LINT_CMD="npx biome check ."
      elif npx eslint --version &>/dev/null 2>&1; then
        LINT_CMD="npx eslint ."
      fi
    fi
  elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    if command -v ruff &>/dev/null; then
      LINT_CMD="ruff check ."
    fi
  elif [ -f "go.mod" ]; then
    if command -v golangci-lint &>/dev/null; then
      LINT_CMD="golangci-lint run"
    fi
  elif [ -f "Cargo.toml" ]; then
    LINT_CMD="cargo clippy --quiet"
  fi

  if [ -n "$LINT_CMD" ]; then
    # Run lint and capture output (no eval — safe execution)
    LINT_OUTPUT=$($LINT_CMD 2>&1) || true
    LINT_EXIT=$?

    if [ $LINT_EXIT -ne 0 ]; then
      # Track iteration count via persistent counter file
      COUNT=1
      if [ -f "$COUNTER_FILE" ]; then
        COUNT=$(( $(cat "$COUNTER_FILE") + 1 ))
      fi
      echo "$COUNT" > "$COUNTER_FILE"

      if [ "$COUNT" -ge 3 ]; then
        # Max iterations reached — clean up and stop
        rm -f "$COUNTER_FILE"
        echo '{"status": "stop", "message": "Quality gate: lint failed after 3 attempts. Manual intervention needed."}'
        exit 0
      fi

      # Ask agent to fix lint issues
      cat <<EOF
{
  "followup_message": "Lint check failed. Please fix the following issues:\n\n\`\`\`\n${LINT_OUTPUT}\n\`\`\`\n\nFix all lint errors and warnings, then verify by running the linter again."
}
EOF
      exit 0
    fi
  fi
fi

# All clear — clean up counter
rm -f "$COUNTER_FILE"

echo '{"status": "ok"}'
```

- [ ] **Step 4: 実行権限を付与**

Run: `chmod +x .cursor/hooks/quality-gate.sh`

- [ ] **Step 5: コミット**

```bash
git add .cursor/hooks.json .cursor/hooks/
git commit -m "✨ feat(cursor): add quality-gate hook — auto lint on agent stop

Detects project linter, runs on agent stop, requests fix via followup_message.
Max 3 iterations before stopping. Supports JS/TS, Python, Go, Rust."
```

---

## Task 10: Infrastructure（symlink.sh 更新 + 検証）

**Files:**
- Modify: `.bin/symlink.sh`

**Depends on:** Tasks 1-9 全完了

- [ ] **Step 1: symlink.sh の Cursor セクションを確認**

Read: `.bin/symlink.sh` — `create_cursor_symlinks` 関数を特定

- [ ] **Step 2: symlink.sh を更新**

`CURSOR_SYMLINK_FILES` と `CURSOR_SYMLINK_DIRECTORIES` を拡張:

```bash
CURSOR_SYMLINK_FILES=(
  "hooks.json"
)
CURSOR_SYMLINK_DIRECTORIES=(
  "rules"
  "skills"
  "agents"
  "commands"
  "hooks"
)
```

- [ ] **Step 3: symlink を実行**

Run: `task symlink`
Expected: 全ディレクトリが `~/.cursor/` にリンクされる

- [ ] **Step 4: symlink を検証**

Run: `task validate-symlinks`
Expected: PASS

- [ ] **Step 5: ファイル数を検証**

Run: `find .cursor -type f | wc -l`
Expected: 25 (Rules 10 + Skills 7 + Subagents 3 + Commands 3 + Hooks 2)

- [ ] **Step 6: 行数を検証**

Run: `wc -l .cursor/rules/*.mdc`
Expected: 各ファイル 500行以内

- [ ] **Step 7: コミット**

```bash
git add .bin/symlink.sh
git commit -m "🔧 chore(symlink): add Cursor skills, agents, commands, hooks to symlink targets

Extends create_cursor_symlinks() to deploy full Cursor configuration:
rules, skills, agents, commands, hooks directory + hooks.json file."
```

---

## Post-Implementation Verification Checklist

Task 10 の Step 3-6 で自動検証を行った後、Cursor を起動して手動検証:

- [ ] Cursor Settings → Rules で `global` と `quality-guard` が Always Apply で表示される
- [ ] `.ts` ファイルを開き、typescript ルールが適用されることを確認
- [ ] チャットで `/` を入力し、review / commit / create-pr 等が表示される
- [ ] `/review-code` を実行し、コマンドが動作する
- [ ] 「verifier を使って検証して」と指示し、サブエージェントが委譲される
- [ ] Agent にコード変更を依頼し、停止時に quality-gate.sh が実行される
