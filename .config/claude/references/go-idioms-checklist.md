---
status: reference
last_reviewed: 2026-04-23
---

# Go Idioms Checklist

権威ソース: Effective Go, Go Code Review Comments, Google Go Style Guide, Uber Go Style Guide, 100 Go Mistakes, Learn Go with Tests

`rules/go.md` の基本ルールを前提とし、ここでは実装・レビュー時の包括チェックリストを提供する。

---

## 1. コード設計 & プロジェクト構成

- [ ] 変数のシャドーイングが意図的か確認（`:=` で外側の変数を隠していないか）
- [ ] ネストは2段以内（ハッピーパスを左側に、ガード節で早期 return）
- [ ] init() を使っていない（テスト不可、実行順序不明確。ファクトリ関数を使う）
- [ ] interface は使用者側で定義（producer 側で定義しない）
- [ ] interface を返していない（具象型を返す）
- [ ] `any` は全型対応時のみ使用（過度な一般化を避ける）
- [ ] ジェネリクスは具体的な必要性がある場合のみ（`[]int` と `[]string` で同じロジックなど）
- [ ] 型埋め込みで不要なメソッドが昇格していないか
- [ ] Functional Options パターンでオプション設定（多数のオプション引数がある場合）
- [ ] パッケージはコンテキストまたはレイヤー別に整理
- [ ] `util`/`common`/`misc` パッケージを作っていない
- [ ] エクスポート要素にはドキュメントコメント（対象名で始まる完全な文）
- [ ] リンター（golangci-lint）を使用

## 2. データ型 & メモリ

- [ ] 8進数リテラルは `0o` プレフィックスで明確化
- [ ] 整数オーバーフローの可能性を考慮
- [ ] 浮動小数点比較はデルタで（`==` 禁止）
- [ ] スライスの length と capacity の違いを理解して使用
- [ ] 既知サイズのスライスはプリアロケート: `make([]T, 0, n)`
- [ ] nil スライスと空スライスの区別（`var s []T` vs `s := []T{}`）
- [ ] スライスの空チェックは `len(s) == 0`（nil/空の両方対応）
- [ ] `copy` 関数は min(dst, src) までコピーする点を理解
- [ ] `append` が元スライスのバッキング配列を変更する可能性を認識
- [ ] スライスからの部分参照でメモリリークしない（`strings.Clone` or コピー）
- [ ] 既知サイズのマップはプリアロケート: `make(map[K]V, n)`
- [ ] マップは縮小しない（大量データ後は再生成を検討）
- [ ] 比較不可能な型に `==` を使っていない（`reflect.DeepEqual` or カスタム比較）

## 3. 制御構造

- [ ] range ループの value はコピー（変更したい場合はインデックスアクセス）
- [ ] range の式はループ開始前に1回だけ評価される点を理解
- [ ] マップの反復順序に依存していない（順序は未定義）
- [ ] for+switch/select での `break` がどのステートメントを抜けるか確認（ラベル付き break）
- [ ] ループ内で `defer` を使っていない（関数に抽出）

## 4. 文字列

- [ ] ルーン（Unicode コードポイント）と バイトの違いを理解
- [ ] 文字列反復は `range` で（ルーン単位。バイト単位なら `[]byte`）
- [ ] `TrimRight`/`TrimLeft`（文字セット削除）vs `TrimSuffix`/`TrimPrefix`（部分文字列削除）
- [ ] 大量連結は `strings.Builder`（プリアロケート `Grow(n)` 推奨）
- [ ] `bytes` パッケージで不要な `string` ↔ `[]byte` 変換を回避

## 5. 関数 & メソッド

- [ ] レシーバ型の選択が適切（value vs pointer — `rules/go.md` 参照）
- [ ] 名前付き結果パラメータは意味がある場合のみ（同型の複数結果の区別、defer での変更）
- [ ] nil レシーバを返す関数で interface 型に nil 具象値を代入していない
- [ ] 関数入力にファイル名ではなく `io.Reader` を使用（再利用性・テスト性向上）
- [ ] `defer` 引数は宣言時に評価される（遅延評価にはクロージャ or ポインタ）

## 6. エラー処理（rules/go.md の補足）

- [ ] `panic` は回復不能な状況のみ（プログラマーエラー、必須依存の初期化失敗）
- [ ] `%w` wrap vs `%v` conversion の使い分け（呼び出し元がエラー型を検査する必要があるか）
- [ ] `errors.Is`（値比較）/ `errors.As`（型比較）を wrap されたエラーに使用
- [ ] エラーを2回処理していない（log OR return、両方しない）
- [ ] `_` でエラーを無視する場合はコメントで意図を明記
- [ ] defer のエラー（`rows.Close()` 等）も処理 or 明示的に無視

## 7. 並行処理: 基礎

- [ ] 並行（構造）と並列（実行）の区別を理解
- [ ] 並行化が本当に速いかベンチマークで検証
- [ ] 並列ゴルーチン間の状態保護 → mutex、ゴルーチン間のメッセージ → channel
- [ ] データ競合 vs 競合状態（race detector は前者のみ検出）
- [ ] CPU バウンド → `GOMAXPROCS` が上限、I/O バウンド → 外部システムが上限
- [ ] `context.Context` のデッドライン、キャンセル、値伝達を正しく使用

## 8. 並行処理: 実践

- [ ] 全 goroutine に明確な停止条件（`ctx.Done()` or チャネル close）
- [ ] `select` の複数 ready ケースはランダム選択（決定的動作を期待しない）
- [ ] 通知チャネルには `chan struct{}`（`chan bool` ではない）
- [ ] nil チャネルは永続ブロック（select ケースの動的無効化に活用）
- [ ] チャネルサイズは 0 か 1（大きいバッファは設計根拠をドキュメント化）
- [ ] `String()` メソッド内でのロック取得に注意（`fmt.Sprintf` でデッドロック）
- [ ] 共有スライスへの並行 `append` はデータ競合（mutex or チャネルで保護）
- [ ] `sync.WaitGroup.Add()` は goroutine 開始前に呼ぶ
- [ ] `errgroup` で goroutine 同期 + エラー伝播 + Context キャンセル
- [ ] sync 型（Mutex, WaitGroup, Cond 等）はコピー禁止

## 9. 標準ライブラリ

- [ ] `time.Duration` で期間を表現（`int` + ナノ秒単位にしない）
- [ ] ループ内で `time.After` を使わない（Timer リーク。`time.NewTimer` + `Stop`）
- [ ] JSON: 埋め込み型のフィールド昇格、`time.Time` の monotonic clock、`map[string]any` の型情報喪失に注意
- [ ] SQL: `Open` 後に `Ping`、コネクションプール設定、`rows.Close()` の defer、null 対応
- [ ] `io.Closer` 実装型は defer で確実に close
- [ ] `http.Error()` 後に `return` する
- [ ] 本番 HTTP クライアント/サーバーにはタイムアウト設定必須

## 10. テスト（rules/go.md の補足）

- [ ] テストを分類: ビルドタグ、`-short` フラグ、環境変数
- [ ] `-race` フラグ必須（CI でも有効化）
- [ ] `-shuffle` でテスト順序依存を検出
- [ ] table-driven tests + `t.Run()` サブテスト
- [ ] テスト内でスリープしない（同期 or リトライ or `testing.TB` のヘルパー）
- [ ] 時間依存テストは `time.Time` を注入可能にする
- [ ] `httptest.NewServer` / `iotest.ErrReader` 等のユーティリティ活用
- [ ] ベンチマーク: コンパイラ最適化でループが消えないよう結果を保持
- [ ] ファジング: 入力バリデーション・パース系関数に `Fuzz` テスト
- [ ] カバレッジ: `-coverprofile` で計測、別パッケージテスト（`package foo_test`）で公開 API を検証

## 11. パフォーマンス & 最適化

- [ ] **計測してから最適化**（`pprof`、`go test -bench`）
- [ ] `strconv` > `fmt` で型変換
- [ ] struct フィールドはサイズ降順に並べる（アラインメントパディング削減）
- [ ] ヒープ割り当て削減: `sync.Pool`、スタック活用、ポインタ返却の回避
- [ ] CPU キャッシュを意識: 配列 > リンクリスト、構造体のスライス > スライスの構造体
- [ ] false sharing: 並行アクセスされるフィールドはキャッシュライン分離
- [ ] インライン展開を阻害しない（小さな関数に保つ）
- [ ] GC 負荷: ポインタを多く持つ大きなヒープは GC を圧迫
- [ ] Docker/K8s: `GOMAXPROCS` は CFS quota を反映しない（`automaxprocs` 等で対応）

## 12. 境界でのデータ保護（Uber Style Guide）

```go
// Bad: 内部状態への参照を共有
func (d *Driver) SetTrips(trips []Trip) {
    d.trips = trips
}

// Good: コピーして内部状態を保護
func (d *Driver) SetTrips(trips []Trip) {
    d.trips = make([]Trip, len(trips))
    copy(d.trips, trips)
}

// Bad: 内部マップへの参照を返す
func (s *Stats) Snapshot() map[string]int {
    return s.counters
}

// Good: コピーを返す
func (s *Stats) Snapshot() map[string]int {
    result := make(map[string]int, len(s.counters))
    for k, v := range s.counters {
        result[k] = v
    }
    return result
}
```

## 13. Struct 初期化パターン（Uber Style Guide）

```go
// Bad: 位置引数
cfg := Config{true, "localhost", 8080}

// Good: フィールド名指定
cfg := Config{
    Enabled: true,
    Host:    "localhost",
    Port:    8080,
}

// ゼロ値 struct は var で宣言
var cfg Config

// enum は iota + 1 から開始（ゼロ値を無効値にする）
type Operation int
const (
    Add Operation = iota + 1
    Subtract
    Multiply
)
```

## 14. Functional Options パターン

```go
type Option func(*Server)

func WithPort(port int) Option {
    return func(s *Server) { s.port = port }
}

func WithTimeout(t time.Duration) Option {
    return func(s *Server) { s.timeout = t }
}

func NewServer(opts ...Option) *Server {
    s := &Server{port: 8080, timeout: 30 * time.Second}
    for _, opt := range opts {
        opt(s)
    }
    return s
}
```

## 15. Interface コンパイル時検証

```go
// 型が interface を実装していることをコンパイル時に保証
var _ http.Handler = (*Handler)(nil)
var _ io.ReadWriter = (*MyType)(nil)
```
