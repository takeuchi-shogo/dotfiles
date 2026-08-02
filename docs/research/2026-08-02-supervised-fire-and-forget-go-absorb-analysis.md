---
source: https://rednafi.com/go/supervised-fire-and-forget/ (Redowan Delowar, 2026-07-25)
date: 2026-08-02
status: integrated
family: go-concurrency (新設, N=1)
---

# rednafi — Supervised, Fire-and-Forget Goroutines in Go

## Source Summary

**主張**: 管理されない `go func()` の fire-and-forget は 4 つの欠陥を同時に抱える — (a) リクエストごとに goroutine が増え同時実行数に上限がない (b) `r.Context()` を継承するため net/http がハンドラ復帰時にキャンセルする (c) 誰も recover しない panic がプロセスを落とす (d) main が shutdown 時に待てない。解決は buffered channel + 固定 worker の単一 pool を composition root (main) が所有し、New/Submit/Stop の3関数 API に閉じること。

**手法**:
- bounded worker pool (buffered channel + 固定 worker 数)
- タスクは `func()` closure、戻り値なし
- `sync.RWMutex` で send (RLock) と close (Lock) を排他 — closed channel への send は panic するため
- worker 側 `defer recover()` + `onPanic` コールバック (コールバック自身も recover で保護)
- `context.WithoutCancel` で request の値だけ引き継ぎキャンセルを切る
- タスクごとに closure 内で `WithTimeout` (計測はキュー待ち込みでなく実行開始から)
- エラーは closure 内で完結
- `WaitGroup.Go` (Go 1.25)
- shutdown 順序 = `server.Shutdown()` → `pool.Stop()` (defer で後入れ先出し)
- in-memory の限界を明示、耐久性が要るなら Asynq

**根拠**: 実装コードと Dave Cheney の maxim「never start a goroutine without knowing how it will stop」。ベンチマーク数値なし。

**前提条件**: 長寿命 HTTP サーバー、best-effort タスク (通知・診断ログ)、Go 1.25+、プロセスクラッシュ時のタスクロストを許容できること。

## Phase 1.5 Saturation Gate

family "go-concurrency" は新設 (過去の Go 系 absorb は `2026-03-30-cc-skills-golang-analysis.md` の 1 件のみ、かつ主題は skill 設計論で並行処理ではない)。N < 3 → PASS。

## Phase 2 判定 (Pass 1 = Sonnet Explore / Pass 2 = Opus)

Phase 2.5 の Codex 批評で 4 件の判定を変更した。最終判定:

| # | 手法 | Phase 2 初期判定 | 最終判定 | 根拠 |
|---|------|---------|---------|------|
| 1 | bounded worker pool | Gap | Partial | review-checklists/go.md GO-4 が終了パス・送信ブロックを部分カバー。欠けていたのは admission/drain の契約 |
| 2 | goroutine の panic 隔離 | Gap | Gap | task-archetypes/error-handling.md:20 は「panic の乱用を避けろ」= 逆向き。「拾わない panic がプロセスを落とす」側の記述なし |
| 3 | context.WithoutCancel 例外規則 | Gap | Gap | GO-7「context.Background() を深い層で直接使うな」は detached background task で誤答を返す。API 自体も repo 内ゼロヒット |
| 4 | detach 後の自前 timeout | Partial | Partial | GO-7 に defer cancel() はあるが「切り離したら誰も止めない」前提が欠落 |
| 5 | shutdown 順序 (server → pool) | Gap | Partial | GO-4 の終了パス要求の延長線。Go アプリ層の graceful shutdown 記述は repo 全体で not_found (ヒットは GKE/Cloudflare のコンテナ層のみ) |
| 6 | closed channel send の競合排他 | Partial | Gap (格上げ) | admission close と send の排他は独立した観点で既存資産になし |
| 7 | エラーは closure 内で完結 | Already | Partial (格上げ) | silent-failure-hunter.md:70 が検出はするが、checklist 側に「ログ/metric/trace で可視化せよ」の要求がない |
| 8 | WaitGroup.Go (Go 1.25) | Already | Already (但し解決策ではない) | go-modernize-checklist.md:18,58 に記載済み。ただし worker の待機を短く書くだけで recover / bounded admission の代替にならない |
| 9 | 耐久性が要るなら Asynq | N/A | N/A | プロジェクト依存。dotfiles の review 資産に置く性質ではない |

## Phase 2.5 (Codex 単独 / Gemini 未取得)

Gemini は verbatim `IneligibleTierError ... reasonCode: 'UNSUPPORTED_CLIENT'` で失敗。既知の individuals sunset (memory `feedback_gemini_cli_sunset.md`) の再確認であり、**Gemini 側の周辺知識補完は未取得のまま Phase 3 に進んだ**。Codex は `codex exec --sandbox read-only -m gpt-5.6-terra` (reasoning effort xhigh) で取得、50,618 tokens。

Codex の結論 (verbatim): 「取り込む価値は高いですが、記事の「単一・固定 worker pool / 3 関数 API」自体を規則化するのは過剰です。レビュー資産には「管理された detached background work の契約」を追加するのが適切です。」

Codex が指摘した記事の見落とし・注意点:

- 過負荷方針を明示せよ (満杯時に待たせる / 即時 reject・drop / 短時間だけ待つ)。無制限 goroutine を追加して回避してはいけない
- Stop() の drain に時間上限がない。タスクが context を無視すると drain が永久に終わらない
- 同一 pool 内から同期 Submit すると全 worker が詰まり queue 満杯時に自己デッドロックする
- closure は必要な値だけコピーする。`*http.Request` や body を保持するとリクエスト寿命とメモリが延びる
- Submit のブロックは欠陥ではなく backpressure の選択。HTTP handler で許容するかは別判断
- errgroup は代替にならない (短命な一まとまりの並行処理向けで、長寿命 queue の admission/drain 所有権を与えない)
- GO-7 と記事は矛盾しない。Background() 禁止は「リクエスト処理の深い層で伝播を切るな」であり、例外は所有権境界での detach のみ

## Phase 3 Triage (ユーザー選択)

T1/T2/T3/T4 の全4件を採用。

## Phase 4 実施内容 (すべて実装済み)

- T1: `.config/claude/references/review-checklists/go.md` GO-4 に小見出し「### 管理外の background task (fire-and-forget)」+ 4 項目を追加 (所有者と同時実行上限 / spawn した goroutine の recover / 満杯時の block・reject+metric・drop の明示 / admission close と send の競合)
- T2: 同ファイル GO-7 に 3 行追加 (detach してよいのは所有権境界のみ / WithoutCancel は親の deadline も捨てるので自前 WithTimeout + defer cancel 必須 / closure には必要な値だけコピー、`*http.Request` を掴まない)
- T3: `.config/claude/rules/go.md` — context.Context 節の「途中で context.Background() を使わない」行に例外条項を追記、並行処理節に 2 行追加 (裸の `go func()` を撒かない / shutdown は server.Shutdown() → pool drain の順、drain に時間上限)
- T4: `.claude/skills/golang-safety/SKILL.md` の L109/L184/L259 が指す `samber/cc-skills-golang@golang-concurrency` は dotfiles・~/.claude・plugins のどこにも実在しない dead reference だった (skills-lock.json にも無い手動 vendor)。3 箇所を `~/.claude/references/review-checklists/go.md` (実在を ls で確認済み、nix mkOutOfStoreSymlink で live) に張り替え。残存 0 件を grep で確認

pool 実装コードと Asynq 推奨は Codex の助言に従い**足していない**。

## Validation-only Follow-up (記事とは別枠、未着手)

| 対象 | 内容 | 確度 |
|------|------|------|
| `.config/claude/rules/go.md` の自動ロード経路 | `paths:` frontmatter (`**/*.go`) を読んで rules/*.md をロードする実装が hook/script のどこにも見つからなかった。`~/.claude/rules/` 自体が存在しない (`~/.claude` は実ディレクトリで、`references` だけが nix 経由の symlink)。`.config/claude/rules/` を名指しするのは context-drift-check.py と doc-garden-check.py の鮮度監視のみ | **未確定** — Claude Code 本体が `$CLAUDE_CONFIG_DIR/rules/` を読むかは未検証。dormant の可能性があるが断定していない |
| `golang-safety/SKILL.md` の他の dead cross-reference | 同ファイルに `cc-skills-golang` 参照が計 13 箇所あり、うち `golang-data-structures` / `golang-error-handling` も同様に MISSING を確認済み。今回は scope 外として未修正 | 確認済み (実在しない) |

## 検証

`task validate-configs` 実行、失敗表示なし。`grep -rn 'golang-concurrency' .claude/skills/golang-safety/` は 0 件。
