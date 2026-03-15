# Lint Rule Guides

auto-format.js が lint エラー検出時に WHY/FIX コンテキストを注入するための
ルール別ガイド。OpenAI の "Error Messages as Fix Instructions" パターンに基づく。

Ref: Harness Engineering Best Practices 2026

---

## TypeScript/JavaScript (Oxlint)

### no-explicit-any
- **WHY**: 型安全性の喪失 → GP-005 違反。コンパイル時の型チェックが無効化される
- **FIX**: `unknown` + type guard、ジェネリクス `<T>`、または具体型を使用

### no-unused-vars
- **WHY**: デッドコードは可読性を下げ、バンドルサイズを増加させる
- **FIX**: 使用していない変数・import を削除。意図的なら `_` プレフィックス

### no-console
- **WHY**: プロダクションコードに console.log を残すと情報漏洩リスク
- **FIX**: logger ライブラリを使用、またはデバッグ完了後に削除

### eqeqeq
- **WHY**: `==` は暗黙の型変換で予期しない真偽値を返す
- **FIX**: `===` (厳密等価) を使用

### no-var
- **WHY**: `var` はスコープが関数単位で意図しないホイスティングを起こす
- **FIX**: `const` (再代入なし) または `let` (再代入あり) に変更

## Python (Ruff)

### E501
- **WHY**: 長すぎる行は可読性を著しく下げる
- **FIX**: 変数抽出、改行、文字列の分割

### F401
- **WHY**: 未使用の import はモジュールロード時間とメモリを浪費する
- **FIX**: import 行を削除

### F841
- **WHY**: 未使用変数はデッドコードの兆候
- **FIX**: 変数を使用するか、`_` プレフィックスで明示的に破棄

### E711
- **WHY**: `== None` より `is None` が Python のイディオム（オブジェクト同一性テスト）
- **FIX**: `is None` / `is not None` を使用

### S101 (assert)
- **WHY**: プロダクションコードの assert は -O フラグで無効化される
- **FIX**: `if not condition: raise ValueError(...)` に変更

## Go (golangci-lint)

### errcheck
- **WHY**: Go のエラーは戻り値。無視すると silent failure — GP-004 違反
- **FIX**: `if err != nil { return fmt.Errorf("...: %w", err) }`

### govet
- **WHY**: コンパイラが検出しない論理的問題（printf フォーマット不一致等）
- **FIX**: govet の指摘に従い、フォーマット文字列と引数を一致させる

### staticcheck (SA)
- **WHY**: 静的解析による潜在バグ検出。誤検出率が非常に低い
- **FIX**: 各 SA コードに対応する修正を適用

### gosec (G)
- **WHY**: セキュリティ脆弱性の自動検出
- **FIX**: 指摘に従いセキュアな代替手段を使用（ADR-0004 参照）
