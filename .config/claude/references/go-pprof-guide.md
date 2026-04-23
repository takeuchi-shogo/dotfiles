---
status: reference
last_reviewed: 2026-04-23
---

# Go pprof Profiling Guide

計測してから最適化する。pprof で根拠を持って改善する。

## Profile Types

| Type | 内容 | 取得タイミング |
|------|------|--------------|
| CPU | 関数ごとの CPU 時間 | 高 CPU 使用時 |
| heap | 現在のメモリ割り当て | メモリ増大時 |
| allocs | 累積メモリ割り当て | GC 圧力調査時 |
| goroutine | 全 goroutine のスタック | ハング・リーク時 |
| mutex | mutex 競合の待ち時間 | ロック競合時 |
| block | ブロッキング操作の待ち時間 | レイテンシ調査時 |
| trace | 実行トレース | スケジューリング調査時 |

## pprof 有効化

### テスト・ベンチマーク

```bash
go test -bench=BenchmarkFoo -cpuprofile=cpu.prof -memprofile=mem.prof
go tool pprof cpu.prof
```

### HTTP サーバー

```go
import _ "net/http/pprof"

// 既存サーバーがない場合
go func() {
    log.Println(http.ListenAndServe("localhost:6060", nil))
}()
```

**本番環境**: 認証付き + 内部ネットワーク限定で公開する。公開インターネットに `pprof` を露出させない。

## プロファイル取得

### ローカル

```bash
# CPU (30秒)
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Heap
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine (テキスト形式)
curl http://localhost:6060/debug/pprof/goroutine?debug=2

# Mutex
go tool pprof http://localhost:6060/debug/pprof/mutex

# Block
go tool pprof http://localhost:6060/debug/pprof/block
```

### リモート

```bash
# プロファイルをファイルに保存
curl -o cpu.prof http://host:6060/debug/pprof/profile?seconds=30
go tool pprof cpu.prof
```

## 分析コマンド

```
(pprof) top 20           # 上位20関数
(pprof) top -cum 20      # 累積時間で上位20
(pprof) list FuncName    # 関数のソースコード + アノテーション
(pprof) web              # ブラウザでグラフ表示
(pprof) weblist FuncName # ブラウザでソース表示
```

### Flamegraph

```bash
go tool pprof -http=:8080 cpu.prof
# ブラウザで http://localhost:8080 → View → Flame Graph
```

## CPU Profiling ワークフロー

1. `go test -bench=. -cpuprofile=cpu.prof` またはHTTPエンドポイントから取得
2. `go tool pprof cpu.prof`
3. `top 20` で最も時間を消費する関数を特定
4. `list FuncName` でホットパスをソースレベルで確認
5. 改善を実装
6. 再ベンチマークで効果を検証

## Memory Profiling ワークフロー

1. `go tool pprof http://localhost:6060/debug/pprof/heap`
2. `top` で最大のメモリ消費者を特定
3. **heap** (inuse_space) = 現在のメモリ使用。メモリリーク調査に
4. **allocs** (alloc_objects) = 累積割り当て。GC 圧力調査に

```bash
# allocs profile
go tool pprof -alloc_objects http://localhost:6060/debug/pprof/heap
```

### 差分分析（リーク検出）

```bash
# 2時点のプロファイルを比較
go tool pprof -base heap1.prof heap2.prof
(pprof) top  # 増加分のみ表示
```

## Goroutine Leak 検出

```bash
# テキスト形式で全 goroutine のスタックを取得
curl http://localhost:6060/debug/pprof/goroutine?debug=2
```

確認ポイント:
- 同じスタックトレースの goroutine が大量にないか
- チャネル送受信でブロックしている goroutine がないか
- `context.Done()` を監視していない goroutine がないか

テストでは [`goleak`](https://github.com/uber-go/goleak) を使用:

```go
func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m)
}
```

## Mutex / Block Contention

```go
// 有効化（main で一度だけ）
runtime.SetMutexProfileFraction(5)   // mutex
runtime.SetBlockProfileRate(1000000) // block (ns)
```

```bash
go tool pprof http://localhost:6060/debug/pprof/mutex
(pprof) top  # 最もロック競合が多い箇所
```

## Escape Analysis

ヒープ割り当てを確認:

```bash
go build -gcflags="-m" ./...
# "escapes to heap" を確認
```

## ベンチマーク Tips

```go
func BenchmarkFoo(b *testing.B) {
    for b.Loop() {  // Go 1.24+: b.Loop() 推奨
        result = Foo(input)
    }
}
```

- 結果を変数に保持してコンパイラ最適化でループが消えるのを防ぐ
- `-benchmem` でメモリ割り当ても計測: `go test -bench=. -benchmem`
- `-count=5` で複数回実行して安定性を確認
- `benchstat` で前後比較: `benchstat old.txt new.txt`
