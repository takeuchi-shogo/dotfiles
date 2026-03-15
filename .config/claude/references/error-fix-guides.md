# Error Fix Guides

error-to-codex.py が参照するエラーパターン → 修正手順マッピング。
エラー検出時に具体的な修正指示を additionalContext に注入する。

フォーマット: Symptom-Cause-Fix テーブル + before/after コード例（Codified Context 論文形式）

---

## JavaScript/TypeScript

| Symptom | Cause | Fix |
|---------|-------|-----|
| `TypeError: Cannot read properties of undefined` | null/undefined チェックの欠落 | optional chaining (`?.`) または事前ガード |
| `ReferenceError: X is not defined` | import 漏れまたはスコープ外参照 | import 文確認、変数スコープ確認 |
| `SyntaxError` | 構文ミス（括弧閉じ忘れ等） | エラー行の前後確認、括弧の対応チェック |
| `npm ERR! ERESOLVE` | 依存関係の競合 | `npm ls` で競合特定 → `--legacy-peer-deps` または手動解決 |
| `cannot find module` | パッケージ未インストールまたはパス誤り | `npm install` 実行、import パスの typo 確認 |

### TypeError: Cannot read properties of undefined

```typescript
// BEFORE (壊れる)
const name = user.profile.name;

// AFTER (安全)
const name = user?.profile?.name;
// または事前ガード
if (!user?.profile) return;
const name = user.profile.name;
```

**Deeper cause**: 非同期データの初期状態が undefined のまま参照されるケースが多い。API レスポンスの型定義で `| undefined` を明示し、コンパイル時に検出する。

---

## Go

| Symptom | Cause | Fix |
|---------|-------|-----|
| `panic: runtime error: invalid memory address or nil pointer dereference` | nil ポインタ参照 | nil チェック追加、Option 型の活用 |
| `panic: runtime error: index out of range` | スライスの境界外アクセス | bounds check 追加、`len()` で事前確認 |
| `FAIL` (go test) | テスト期待値の不一致 | `go test -v` で詳細出力、expected/actual 比較 |
| `go.mod: module declares its path as X` | go.mod のモジュールパス不一致 | import パスとモジュール宣言を一致させる |
| `context deadline exceeded` | context のタイムアウト | タイムアウト値の調整、処理の最適化 |

### panic: nil pointer dereference

```go
// BEFORE (壊れる)
func process(resp *http.Response) {
    body := resp.Body // resp が nil なら panic
}

// AFTER (安全)
func process(resp *http.Response) error {
    if resp == nil {
        return fmt.Errorf("response is nil")
    }
    body := resp.Body
}
```

**Deeper cause**: エラーを返す関数で `err != nil` チェック前に戻り値を使用するパターン。`if err != nil { return }` を先に書く習慣で防止。

---

## Python

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Traceback (most recent call last)` | 未処理例外 | スタックトレース最下行で実際のエラーを確認 |
| `ModuleNotFoundError` | パッケージ未インストール | `pip install` または `uv add` |
| `AttributeError: 'NoneType' has no attribute` | None チェック欠落 | `is not None` ガード追加 |
| `IndentationError` | インデントの混在（tab/space） | エディタ設定統一、`autopep8` 実行 |

### Traceback の読み方

```
Traceback (most recent call last):
  File "app.py", line 42, in handle_request  ← 呼び出し元（コンテキスト）
    result = process(data)
  File "core.py", line 15, in process       ← 実際の問題箇所
    return data["key"]                       ← ここを修正
KeyError: 'key'                              ← 根本原因
```

**読み方**: 最下行が根本原因。上に向かって呼び出しチェーンを辿り、入力データの出所を特定する。

---

## Rust

| Symptom | Cause | Fix |
|---------|-------|-----|
| `error[E0382]: borrow of moved value` | 所有権の移動後に参照 | `.clone()` または参照 `&` に変更 |
| `error[E0308]: mismatched types` | 型不一致 | 期待される型と実際の型を確認、`Into`/`From` 実装 |
| `error[E0597]: does not live long enough` | ライフタイム不足 | 変数のスコープを広げるか、所有権を移動 |

**一般原則**: `rustc --explain EXXXX` で公式ドキュメントの詳細な解説を確認。

---

## General

| Symptom | Cause | Fix |
|---------|-------|-----|
| `build failed / compilation failed` | ビルド設定またはコード構文の問題 | build-fixer エージェントに委譲 |
| `segmentation fault` | メモリ不正アクセス | debugger エージェントで根本原因分析 |
| `fatal error` | 回復不能なランタイムエラー | スタックトレース全体を確認、codex-debugger で分析 |
| `ECONNREFUSED / connection refused` | サーバー未起動またはポート不一致 | プロセス確認 (`lsof -i :PORT`)、ポート番号確認 |
| `permission denied` | ファイル/ディレクトリ権限不足 | `ls -la` で権限確認、`chmod` で修正 |
