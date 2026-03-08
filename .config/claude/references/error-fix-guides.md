# Error Fix Guides

error-to-codex.py が参照するエラーパターン → 修正手順マッピング。
エラー検出時に具体的な修正指示を additionalContext に注入する。

---

## JavaScript/TypeScript

### TypeError: Cannot read properties of undefined

- **原因**: null/undefined チェックの欠落
- **修正**: optional chaining (`?.`) または事前ガードを追加
- **例**: `obj?.prop` or `if (!obj) return`

### ReferenceError: X is not defined

- **原因**: import 漏れまたはスコープ外参照
- **修正**: import 文を確認、変数スコープを確認

### SyntaxError

- **原因**: 構文ミス（括弧閉じ忘れ、セミコロン等）
- **修正**: エラー行の前後を確認、括弧の対応をチェック

### npm ERR! ERESOLVE

- **原因**: 依存関係の競合
- **修正**: `npm ls` で競合パッケージ特定 → `--legacy-peer-deps` または手動解決

### cannot find module

- **原因**: パッケージ未インストールまたはパス誤り
- **修正**: `npm install` 実行、import パスの typo 確認

## Go

### panic:

- **原因**: nil ポインタ参照、index out of range 等
- **修正**: nil チェック追加、bounds check 追加

### FAIL (go test)

- **原因**: テスト期待値の不一致
- **修正**: `go test -v` で詳細出力確認、expected/actual 比較

## Python

### Traceback (most recent call last)

- **原因**: 未処理例外
- **修正**: スタックトレースの最下行で実際のエラーを確認

## Rust

### error[E...]

- **原因**: コンパイルエラー（型不一致、借用チェック等）
- **修正**: エラーコードの公式ドキュメント `rustc --explain EXXXX` を参照

## General

### build failed / compilation failed

- **原因**: ビルド設定またはコード構文の問題
- **修正**: build-fixer エージェントに委譲を推奨

### segmentation fault

- **原因**: メモリ不正アクセス
- **修正**: debugger エージェントで根本原因分析を推奨

### fatal error

- **原因**: 回復不能なランタイムエラー
- **修正**: スタックトレース全体を確認し、codex-debugger で分析
