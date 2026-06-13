---
status: active
---

# Nightly Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 夜間バッチを「個別 launchd 11本の時刻ずらし直列」から「単一 Go orchestrator が並列実行 + 成否集約 + Discord 集約通知 + 偽成功検出の全ジョブ横展開」に置き換え、信頼性と総実行時間を改善する。

**Architecture:** Go single binary (`tools/nightly-orchestrator/`) が `jobs.yaml` を読み、既存 `run-*.sh` を**子プロセスとして並列起動**する（semaphore で同時数 3 に制限）。各 bash は gate 判定を自分で行い（既存 `should_run_today` に委譲）、orchestrator は `NIGHTLY_ORCHESTRATED=1`（新規・後述の単一スイッチ）を渡して (1) bash 内の atomic-mkdir claude lock を無効化（同時実行数制御を orchestrator に一本化）、(2) bash 内の fail-count/翌日 catch-up リトライ機構を無効化（リトライ制御を orchestrator に一本化）する。`NIGHTLY_DATE_OVERRIDE` を起動時に 1 回確定して全ジョブへ配り、0 時跨ぎの日付ズレを根治。各ジョブの個別 Discord 通知は `NIGHTLY_NOTIFY_DISABLE=1` で抑制し、全完了後に orchestrator が JSONL（`~/.cache/nightly/status-YYYY-MM-DD.jsonl`）を読んで成否を集約し、既存 Discord webhook に**1通だけ**送る。偽成功検出は共通 lib の `status_end` に組み込み、現在 `run-learned-promote.sh` だけが持つ検出を全ジョブへ横展開する。

**設計の中核（Gemini 敵対的レビューで修正した 2 つの欠陥）:**
- **二重リトライ機構の解消**: bash には元々「fail 1 回目は last-run を mark せず翌日 catch-up で 1 回再試行、2 連続で諦め」という fail-count リトライ機構がある。orchestrator が即時リトライを持つと、この 2 つが衝突する。具体的には `_read_fail_count` が**前夜**の fail も数えるため（`nightly-status.sh:171`）、2 夜連続 fail で今夜の 1 回目 fail が即 `fail-count=2` となり mark され、orchestrator の再起動が `already ran today` で弾かれる。**対策**: `NIGHTLY_ORCHESTRATED=1` のとき `status_end` は fail-count 機構を**完全にバイパス**し「ok のときだけ mark、fail では mark しない」に切り替える。これで orchestrator が唯一のリトライ制御者になり、`should_run_today` の `already ran today` がリトライを弾かない。最終 fail でも mark されないため、DAILY ジョブは翌夜再実行・DOW/DOM ジョブは catch-up window で翌夜再試行され、既存機構より素直に「翌日リトライ」が効く。
- **JSONL 並列追記の行混ざり**: 並列実行で複数 bash が `echo >> status.jsonl` する際、`detail` が PIPE_BUF（macOS 4096B）を超えると O_APPEND のアトミック性が崩れ行が混ざる。混ざった行を reader が malformed スキップすると、fail ジョブが `missing`（skip 扱い）になりリトライも警告もされない silent loss が起きる。**対策**: (a) `status_end` の JSONL 書き込みを atomic-mkdir lock（既存 `acquire_claude_lock` と同じパターン）で排他化、(b) orchestrator 側で「JSONL 記録なし **かつ** プロセスが timeout/異常終了」を `missing` ではなく `fail` 扱いにして二重で救う。

**Phase 切り分け:**
- **Phase 1（本 Plan のスコープ）**: 並列実行 + lock 根治 + 日付統一 + 偽成功検出横展開 + 即時リトライ + 集約通知 + 移行。これでユーザーの動機（push + 信頼性・並列化）はほぼ達成される。
- **Phase 2（別 Plan、未着手）**: codex/cursor フォールバック（claude -p 失敗時に別ランタイムで再実行）。bash の `claude -p` 呼び出し抽象化が必要で、かつ codex/cursor が同等の Vault md を書けるかは未検証 → spike が前提のため本 Plan から分離する。

**Tech Stack:** Go 1.25、`gopkg.in/yaml.v3`、`golang.org/x/sync/errgroup`+`semaphore`、`os/exec`、`context`。テストは標準 `testing` の table-driven。既存資産（bash ラッパー / Python JSONL 集約 / Obsidian 書き込み）はそのまま子プロセスとして再利用。

---

## File Structure

**新規（Go orchestrator）:**
- `tools/nightly-orchestrator/go.mod` — モジュール定義
- `tools/nightly-orchestrator/main.go` — エントリポイント（flag パース → orchestrator 起動）
- `tools/nightly-orchestrator/jobs.yaml` — ジョブ宣言（既存 TASKS 配列の YAML 化）
- `tools/nightly-orchestrator/internal/config/config.go` — jobs.yaml パース + バリデーション
- `tools/nightly-orchestrator/internal/config/config_test.go`
- `tools/nightly-orchestrator/internal/status/status.go` — JSONL リーダ（task ごと最新レコード + 成否集約）
- `tools/nightly-orchestrator/internal/status/status_test.go`
- `tools/nightly-orchestrator/internal/runner/runner.go` — bash 子プロセス起動（timeout + env 注入）
- `tools/nightly-orchestrator/internal/runner/runner_test.go`
- `tools/nightly-orchestrator/internal/notify/notify.go` — Discord 集約 payload 生成 + 送信
- `tools/nightly-orchestrator/internal/notify/notify_test.go`
- `tools/nightly-orchestrator/internal/orchestrator/orchestrator.go` — 並列実行 + リトライ + 統合
- `tools/nightly-orchestrator/internal/orchestrator/orchestrator_test.go`
- `tools/nightly-orchestrator/Taskfile.yml` — build/test タスク（otel-session-analyzer 踏襲）

**修正（既存 bash）:**
- `scripts/runtime/nightly/lib/nightly-status.sh` — `acquire_claude_lock` に `NIGHTLY_SKIP_LOCK` guard 追加 + `status_end` に偽成功検出組み込み
- `scripts/runtime/nightly/launchd-install.sh` — 11 個別エントリ → orchestrator 単一エントリ（caffeinate は維持）
- `scripts/runtime/nightly/launchd-uninstall.sh` — orchestrator エントリ対応

**責務境界:** Go 層は「並列・リトライ・集約・通知」のみ。gate 判定・偽成功検出・JSONL 書き込み・Vault 出力は bash 層に残す（既存資産の再利用 + DRY）。Go 層は JSONL を**読むだけ**で、書き込みは一切しない。

---

## 前提となる既存インターフェース（実装者向けの事実）

実装前にこれらを理解すること。ソースは `scripts/runtime/nightly/lib/nightly-status.sh` と `notify-discord.sh`。

1. **全 run-*.sh は常に `exit 0`** で返る（preflight fail / gate skip / claude fail すべて 0）。成否は JSONL の `status` フィールドでしか判定できない。
2. **JSONL スキーマ**（`~/.cache/nightly/status-YYYY-MM-DD.jsonl`、1 行 1 レコード）:
   ```json
   {"ts":"2026-06-13T23:16:42+09:00","task":"golden-check","status":"ok","duration_sec":183,"report":"06-Nightly/2026-06-13-golden.md","detail":"...","metric":{"violations":"3","msg":"violations=3"}}
   ```
   gate skip 時は JSONL に**何も書かれない**（bash が `should_run_today` で `exit 0`）。
3. **fail-count メカニズム**（`status_end` 内）: `fail` 1 回目は `last-run-<task>.txt` を mark せず `fail-count-<task>.txt` に 1 を記録。`fail` 2 連続で mark（諦め）。`ok` で mark + fail-count リセット。`FORCE_RUN=1` は mark も fail-count も触らない。
4. **gate 判定**（`should_run_today`）: `last_run == today` なら skip、`LOOP_DISABLED` ファイルがあれば全 skip、`DAILY`/`DOW`/`DOM` + catch-up days。
5. **claude lock**（`acquire_claude_lock`）: atomic `mkdir "$HOME/.cache/nightly/.lock-claude-p"`、最大 `NIGHTLY_CLAUDE_LOCK_WAIT_SEC`（1200s）待機。
6. **Discord webhook**: `~/.config/notifications/discord.env` の `DISCORD_WEBHOOK_URL`。`NIGHTLY_NOTIFY_DISABLE=1` で `notify_discord` が即 return。embed 形式（ok=緑 color 3066993 / fail=赤 color 15158332 + `@here`）。
7. **偽成功検出の既存実装**（`run-learned-promote.sh` のみ）: `grep -qiE '^[[:space:]]*execution error' "$CLAUDE_LOG"` で stdout を検査し fail 扱い。
8. **既存ジョブ一覧**（`launchd-install.sh` の TASKS 配列）:

   | name | script | gate | bash timeout | claude lock |
   |---|---|---|---|---|
   | dep-audit | run-dep-audit.sh | DOM=1, 7日 | なし | 不要 |
   | learned-promote | run-learned-promote.sh | DOW=7, 2日 | 900s | 要 |
   | golden-check | run-golden-check.sh | DAILY | 600s | 要 |
   | friction-aggregate | run-friction-aggregate.sh | DAILY | — | 要 |
   | health-check | run-health-check.sh | DAILY | 600s | 要 |
   | daily-report | run-daily-report.sh | DAILY | 600s | 要 |
   | audit | run-audit.sh | DOW=1, 6日 | 1200s | 要 |
   | skill-audit | run-skill-audit.sh | DOW=4, 6日 | 900s | 要 |
   | plan-close-scan | run-plan-close-scan.sh | DAILY | — | 不要 |
   | tech-researcher | ../tech-researcher/run-tech-researcher.sh | DAILY | — | 要 |

   （caffeinate は LLM ジョブではなくスリープ抑止アンブレラ。orchestrator の管理対象外、別 plist で維持）

**リトライ設計の核心（修正版）**: orchestrator は `NIGHTLY_ORCHESTRATED=1` を渡す。このモードでは `status_end` が bash の fail-count 機構をバイパスし「ok のときだけ last-run を mark、fail では mark しない」に切り替わる。よって orchestrator が 1 回目 `fail` を JSONL で検知して**同じ bash を即再起動**しても、`should_run_today` は last-run 未 mark のため「already ran today」で弾かない。`job.Retry` 回まで再起動し、ok になれば mark、最終的に fail でも mark しない（→ DAILY は翌夜再実行、DOW/DOM は catch-up window で翌夜再試行）。**重要**: この設計の前提は「bash の fail-count を `NIGHTLY_ORCHESTRATED=1` でバイパスすること」（Task 5c）。バイパスしないと前夜の fail-count が今夜の 1 回目 fail を即 `count=2` に押し上げ mark され、リトライが死ぬ（Gemini CRITICAL 指摘）。`FORCE_RUN` は使わない（FORCE_RUN は検証専用で本番状態を汚さない別用途）。

---

## Task 1: Go プロジェクト骨格

**Files:**
- Create: `tools/nightly-orchestrator/go.mod`
- Create: `tools/nightly-orchestrator/main.go`
- Create: `tools/nightly-orchestrator/Taskfile.yml`
- Create: `tools/nightly-orchestrator/.gitignore`

- [ ] **Step 1: go.mod を作成**

```
module github.com/takeuchishougo/nightly-orchestrator

go 1.25
```

- [ ] **Step 2: 最小 main.go を作成（コンパイルが通るだけ）**

```go
package main

import "fmt"

func main() {
	fmt.Println("nightly-orchestrator")
}
```

- [ ] **Step 3: .gitignore を作成（ビルド成果物を除外）**

```
nightly-orchestrator
*.test
```

- [ ] **Step 4: Taskfile.yml を作成（otel-session-analyzer 踏襲）**

```yaml
version: "3"
tasks:
  build:
    desc: Build the orchestrator binary
    cmds:
      - go build -o nightly-orchestrator .
  test:
    desc: Run all tests
    cmds:
      - go test ./...
  lint:
    desc: Vet
    cmds:
      - go vet ./...
```

- [ ] **Step 5: ビルド確認**

Run: `cd tools/nightly-orchestrator && go build -o nightly-orchestrator . && ./nightly-orchestrator`
Expected: `nightly-orchestrator` が出力される

- [ ] **Step 6: Commit**

```bash
git add tools/nightly-orchestrator/go.mod tools/nightly-orchestrator/main.go tools/nightly-orchestrator/Taskfile.yml tools/nightly-orchestrator/.gitignore
git commit -m "feat(nightly): orchestrator プロジェクト骨格"
```

---

## Task 2: config パッケージ（jobs.yaml パース + バリデーション）

**Files:**
- Create: `tools/nightly-orchestrator/jobs.yaml`
- Create: `tools/nightly-orchestrator/internal/config/config.go`
- Test: `tools/nightly-orchestrator/internal/config/config_test.go`

- [ ] **Step 1: yaml.v3 を依存に追加**

Run: `cd tools/nightly-orchestrator && go get gopkg.in/yaml.v3`
Expected: go.mod に `require gopkg.in/yaml.v3 v3.x.x` が追加される

- [ ] **Step 2: 失敗するテストを書く**

```go
package config

import "testing"

func TestLoad(t *testing.T) {
	yaml := `
runtime:
  max_parallel: 3
jobs:
  - name: golden-check
    script: scripts/runtime/nightly/run-golden-check.sh
    timeout_sec: 900
    retry: 1
  - name: dep-audit
    script: scripts/runtime/nightly/run-dep-audit.sh
    timeout_sec: 0
    retry: 0
`
	cfg, err := Parse([]byte(yaml))
	if err != nil {
		t.Fatalf("Parse: %v", err)
	}
	if cfg.Runtime.MaxParallel != 3 {
		t.Errorf("MaxParallel = %d, want 3", cfg.Runtime.MaxParallel)
	}
	if len(cfg.Jobs) != 2 {
		t.Fatalf("len(Jobs) = %d, want 2", len(cfg.Jobs))
	}
	if cfg.Jobs[0].Name != "golden-check" {
		t.Errorf("Jobs[0].Name = %q, want golden-check", cfg.Jobs[0].Name)
	}
	if cfg.Jobs[0].TimeoutSec != 900 {
		t.Errorf("Jobs[0].TimeoutSec = %d, want 900", cfg.Jobs[0].TimeoutSec)
	}
}

func TestParseRejectsDuplicateNames(t *testing.T) {
	yaml := `
runtime:
  max_parallel: 3
jobs:
  - name: dup
    script: a.sh
  - name: dup
    script: b.sh
`
	if _, err := Parse([]byte(yaml)); err == nil {
		t.Fatal("expected error for duplicate job names, got nil")
	}
}

func TestParseRejectsEmptyScript(t *testing.T) {
	yaml := `
runtime:
  max_parallel: 3
jobs:
  - name: noscript
    script: ""
`
	if _, err := Parse([]byte(yaml)); err == nil {
		t.Fatal("expected error for empty script, got nil")
	}
}
```

- [ ] **Step 3: テストが失敗することを確認**

Run: `cd tools/nightly-orchestrator && go test ./internal/config/`
Expected: FAIL（`Parse` undefined）

- [ ] **Step 4: config.go を実装**

```go
package config

import (
	"fmt"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Runtime Runtime `yaml:"runtime"`
	Jobs    []Job   `yaml:"jobs"`
}

type Runtime struct {
	MaxParallel int `yaml:"max_parallel"`
}

type Job struct {
	Name       string `yaml:"name"`
	Script     string `yaml:"script"`
	TimeoutSec int    `yaml:"timeout_sec"` // orchestrator 側のハング保険。0 = 無制限（bash 内 gtimeout に委譲）
	Retry      int    `yaml:"retry"`       // 即時リトライ回数（1 推奨）
}

func Parse(data []byte) (*Config, error) {
	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("yaml unmarshal: %w", err)
	}
	if cfg.Runtime.MaxParallel <= 0 {
		cfg.Runtime.MaxParallel = 3 // デフォルト
	}
	seen := make(map[string]bool, len(cfg.Jobs))
	for i, j := range cfg.Jobs {
		if j.Name == "" {
			return nil, fmt.Errorf("job[%d]: name is required", i)
		}
		if j.Script == "" {
			return nil, fmt.Errorf("job %q: script is required", j.Name)
		}
		if seen[j.Name] {
			return nil, fmt.Errorf("duplicate job name: %q", j.Name)
		}
		seen[j.Name] = true
	}
	return &cfg, nil
}
```

- [ ] **Step 5: テストが通ることを確認**

Run: `cd tools/nightly-orchestrator && go test ./internal/config/`
Expected: PASS

- [ ] **Step 6: jobs.yaml を作成（既存 TASKS を移植。script は dotfiles ルートからの相対パス）**

```yaml
# nightly-orchestrator ジョブ定義
# script パスは dotfiles リポジトリルートからの相対。orchestrator は repo_root を解決して結合する。
runtime:
  max_parallel: 3
jobs:
  - name: dep-audit
    script: scripts/runtime/nightly/run-dep-audit.sh
    timeout_sec: 600
    retry: 0
  - name: learned-promote
    script: scripts/runtime/nightly/run-learned-promote.sh
    timeout_sec: 1080   # bash 900s + 余裕
    retry: 1
  - name: golden-check
    script: scripts/runtime/nightly/run-golden-check.sh
    timeout_sec: 720    # bash 600s + 余裕
    retry: 1
  - name: friction-aggregate
    script: scripts/runtime/nightly/run-friction-aggregate.sh
    timeout_sec: 600
    retry: 1
  - name: health-check
    script: scripts/runtime/nightly/run-health-check.sh
    timeout_sec: 720
    retry: 1
  - name: daily-report
    script: scripts/runtime/nightly/run-daily-report.sh
    timeout_sec: 720
    retry: 1
  - name: audit
    script: scripts/runtime/nightly/run-audit.sh
    timeout_sec: 1440   # bash 1200s + 余裕
    retry: 1
  - name: skill-audit
    script: scripts/runtime/nightly/run-skill-audit.sh
    timeout_sec: 1080
    retry: 1
  - name: plan-close-scan
    script: scripts/runtime/nightly/run-plan-close-scan.sh
    timeout_sec: 300
    retry: 0
  - name: tech-researcher
    script: scripts/runtime/tech-researcher/run-tech-researcher.sh
    timeout_sec: 900
    retry: 1
```

- [ ] **Step 7: Commit**

```bash
git add tools/nightly-orchestrator/internal/config tools/nightly-orchestrator/jobs.yaml tools/nightly-orchestrator/go.mod tools/nightly-orchestrator/go.sum
git commit -m "feat(nightly): jobs.yaml パーサ + バリデーション"
```

---

## Task 3: status パッケージ（JSONL リーダ + 成否集約）

orchestrator が「全ジョブ exit 0」の世界で成否を知る唯一の経路。task ごとに**最新レコード**を採用する（リトライで同一 task が複数行になるため）。

**Files:**
- Create: `tools/nightly-orchestrator/internal/status/status.go`
- Test: `tools/nightly-orchestrator/internal/status/status_test.go`

- [ ] **Step 1: 失敗するテストを書く**

```go
package status

import (
	"os"
	"path/filepath"
	"testing"
)

func writeTemp(t *testing.T, lines string) string {
	t.Helper()
	dir := t.TempDir()
	p := filepath.Join(dir, "status-2026-06-13.jsonl")
	if err := os.WriteFile(p, []byte(lines), 0o644); err != nil {
		t.Fatal(err)
	}
	return p
}

func TestLatestByTask(t *testing.T) {
	// golden-check が fail→ok でリトライ成功したケース: 最新(ok)を採用
	lines := `{"ts":"2026-06-13T23:10:00+09:00","task":"golden-check","status":"fail","duration_sec":5,"report":"","detail":"","metric":{"msg":"timeout"}}
{"ts":"2026-06-13T23:15:00+09:00","task":"golden-check","status":"ok","duration_sec":183,"report":"06-Nightly/x.md","detail":"","metric":{"violations":"3"}}
{"ts":"2026-06-13T23:20:00+09:00","task":"audit","status":"fail","duration_sec":7,"report":"","detail":"boom","metric":{"msg":"crash"}}
`
	recs, err := ReadLatestByTask(writeTemp(t, lines))
	if err != nil {
		t.Fatalf("ReadLatestByTask: %v", err)
	}
	if len(recs) != 2 {
		t.Fatalf("len = %d, want 2", len(recs))
	}
	if recs["golden-check"].Status != "ok" {
		t.Errorf("golden-check status = %q, want ok (latest wins)", recs["golden-check"].Status)
	}
	if recs["audit"].Status != "fail" {
		t.Errorf("audit status = %q, want fail", recs["audit"].Status)
	}
}

func TestReadLatestByTaskToleratesMalformed(t *testing.T) {
	// morning-briefing と同じく malformed 行に寛容であること
	lines := `not json
{"ts":"2026-06-13T23:15:00+09:00","task":"golden-check","status":"ok","duration_sec":1,"report":"","detail":"","metric":{}}
`
	recs, err := ReadLatestByTask(writeTemp(t, lines))
	if err != nil {
		t.Fatalf("ReadLatestByTask: %v", err)
	}
	if len(recs) != 1 {
		t.Fatalf("len = %d, want 1 (malformed line skipped)", len(recs))
	}
}

func TestReadLatestByTaskMissingFile(t *testing.T) {
	// ファイルが存在しない場合は空マップ + nil error（全 skip された夜）
	recs, err := ReadLatestByTask("/nonexistent/status.jsonl")
	if err != nil {
		t.Fatalf("want nil error for missing file, got %v", err)
	}
	if len(recs) != 0 {
		t.Errorf("len = %d, want 0", len(recs))
	}
}
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `cd tools/nightly-orchestrator && go test ./internal/status/`
Expected: FAIL（`ReadLatestByTask` undefined）

- [ ] **Step 3: status.go を実装**

```go
package status

import (
	"bufio"
	"encoding/json"
	"errors"
	"io/fs"
	"os"
)

type Record struct {
	TS          string            `json:"ts"`
	Task        string            `json:"task"`
	Status      string            `json:"status"` // "ok" | "fail"
	DurationSec int               `json:"duration_sec"`
	Report      string            `json:"report"`
	Detail      string            `json:"detail"`
	Metric      map[string]string `json:"metric"`
}

// ReadLatestByTask は JSONL を読み、task ごとに最後に現れたレコードを返す。
// ファイル不在は空マップ + nil error（全ジョブが gate skip された夜は正常）。
// malformed 行は morning-briefing と同様にスキップする。
func ReadLatestByTask(path string) (map[string]Record, error) {
	f, err := os.Open(path)
	if err != nil {
		if errors.Is(err, fs.ErrNotExist) {
			return map[string]Record{}, nil
		}
		return nil, err
	}
	defer f.Close()

	out := make(map[string]Record)
	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 0, 64*1024), 1024*1024) // detail が長い行に備える
	for sc.Scan() {
		line := sc.Bytes()
		if len(line) == 0 {
			continue
		}
		var r Record
		if err := json.Unmarshal(line, &r); err != nil {
			continue // malformed 行は無視（tolerant）
		}
		if r.Task == "" {
			continue
		}
		out[r.Task] = r // 後勝ち = 最新
	}
	if err := sc.Err(); err != nil {
		return nil, err
	}
	return out, nil
}
```

- [ ] **Step 4: テストが通ることを確認**

Run: `cd tools/nightly-orchestrator && go test ./internal/status/`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/nightly-orchestrator/internal/status
git commit -m "feat(nightly): JSONL ステータスリーダ (task ごと最新採用)"
```

---

## Task 4: runner パッケージ（bash 子プロセス起動）

1 ジョブを 1 回起動する責務だけを持つ。env 注入（lock 無効化 / 通知抑制 / 日付統一）と context timeout を扱う。リトライは Task 6 の orchestrator が担う。

**Files:**
- Create: `tools/nightly-orchestrator/internal/runner/runner.go`
- Test: `tools/nightly-orchestrator/internal/runner/runner_test.go`

- [ ] **Step 1: 失敗するテストを書く（実際の bash を起動して env 注入を検証）**

```go
package runner

import (
	"context"
	"os"
	"path/filepath"
	"testing"
	"time"
)

// fake script を作り、orchestrator が渡す env が届くか + timeout が効くかを検証
func writeScript(t *testing.T, body string) string {
	t.Helper()
	dir := t.TempDir()
	p := filepath.Join(dir, "fake.sh")
	if err := os.WriteFile(p, []byte("#!/usr/bin/env bash\n"+body), 0o755); err != nil {
		t.Fatal(err)
	}
	return p
}

func TestRunInjectsEnv(t *testing.T) {
	out := filepath.Join(t.TempDir(), "env.txt")
	script := writeScript(t, `echo "$NIGHTLY_SKIP_LOCK $NIGHTLY_NOTIFY_DISABLE $NIGHTLY_DATE_OVERRIDE" > "`+out+`"`)
	r := Runner{
		Env: map[string]string{
			"NIGHTLY_ORCHESTRATED":     "1",
			"NIGHTLY_NOTIFY_DISABLE": "1",
			"NIGHTLY_DATE_OVERRIDE": "2026-06-13",
		},
	}
	res := r.Run(context.Background(), "fake", script, 0)
	if res.TimedOut {
		t.Fatal("unexpected timeout")
	}
	got, _ := os.ReadFile(out)
	want := "1 1 2026-06-13\n"
	if string(got) != want {
		t.Errorf("env injected = %q, want %q", got, want)
	}
}

func TestRunTimeout(t *testing.T) {
	script := writeScript(t, `sleep 5`)
	r := Runner{}
	start := time.Now()
	res := r.Run(context.Background(), "slow", script, 1) // 1 秒で kill
	if !res.TimedOut {
		t.Error("expected TimedOut = true")
	}
	if time.Since(start) > 3*time.Second {
		t.Error("timeout did not kill the process promptly")
	}
}
```

- [ ] **Step 2: テストが失敗することを確認**

Run: `cd tools/nightly-orchestrator && go test ./internal/runner/`
Expected: FAIL（`Runner` undefined）

- [ ] **Step 3: runner.go を実装**

```go
package runner

import (
	"context"
	"os"
	"os/exec"
	"syscall"
	"time"
)

type Runner struct {
	// Env は全ジョブ共通で注入する環境変数（OBSIDIAN_VAULT_PATH 等）。
	// os.Environ() に上書きマージされる。
	Env map[string]string
}

type Result struct {
	Task     string
	ExitCode int
	TimedOut bool
	Err      error
	Duration time.Duration
}

// Run は 1 ジョブを 1 回だけ起動する。timeoutSec=0 は無制限（bash 内 gtimeout に委譲）。
// stdout/stderr は launchd ログに流すため親プロセスへ継承する。
func (r Runner) Run(ctx context.Context, task, scriptPath string, timeoutSec int) Result {
	if timeoutSec > 0 {
		var cancel context.CancelFunc
		ctx, cancel = context.WithTimeout(ctx, time.Duration(timeoutSec)*time.Second)
		defer cancel()
	}

	cmd := exec.CommandContext(ctx, "/bin/bash", "-lc", scriptPath)
	cmd.Env = append(os.Environ(), envSlice(r.Env)...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	// timeout 時は SIGKILL でプロセスグループごと止める（claude 子プロセスを残さない）
	cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
	cmd.Cancel = func() error {
		return syscall.Kill(-cmd.Process.Pid, syscall.SIGKILL)
	}

	start := time.Now()
	err := cmd.Run()
	dur := time.Since(start)

	res := Result{Task: task, Duration: dur, Err: err}
	if ctx.Err() == context.DeadlineExceeded {
		res.TimedOut = true
	}
	if exitErr, ok := err.(*exec.ExitError); ok {
		res.ExitCode = exitErr.ExitCode()
	}
	return res
}

func envSlice(m map[string]string) []string {
	out := make([]string, 0, len(m))
	for k, v := range m {
		out = append(out, k+"="+v)
	}
	return out
}
```

- [ ] **Step 4: テストが通ることを確認**

Run: `cd tools/nightly-orchestrator && go test ./internal/runner/`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/nightly-orchestrator/internal/runner
git commit -m "feat(nightly): bash 子プロセス runner (env 注入 + timeout)"
```

---

## Task 5: 共通 lib 修正（orchestrator スイッチ + 偽成功検出 + JSONL 排他）

Go 側ではなく bash 共通 lib を修正する。**1 箇所の修正で全ジョブに効く**のが肝（DRY）。`NIGHTLY_ORCHESTRATED=1` を単一スイッチとし、(5a) claude lock 無効化、(5c) fail-count リトライ機構バイパスの両方を駆動する。さらに (5b) 偽成功検出の横展開・強化、(5d) JSONL 並列追記の排他を入れる。

**Files:**
- Modify: `scripts/runtime/nightly/lib/nightly-status.sh:280-293`（`acquire_claude_lock`）
- Modify: `scripts/runtime/nightly/lib/nightly-status.sh:55-146`（`status_end`）

### 5a: NIGHTLY_ORCHESTRATED で claude lock を無効化

- [ ] **Step 1: `acquire_claude_lock` の冒頭に guard を追加**

`nightly-status.sh` の `acquire_claude_lock()` 関数（現 280 行目）の `local waited=0` の直前に挿入:

```bash
acquire_claude_lock() {
    # NIGHTLY_ORCHESTRATED=1: orchestrator が同時実行数を制御する場合、bash 内 lock を無効化する。
    # launchd 直叩き (移行前 / フォールバック) では未設定 → 従来どおり lock 有効。
    if [[ "${NIGHTLY_ORCHESTRATED:-0}" == "1" ]]; then
        _NIGHTLY_HAS_LOCK=0
        echo "[nightly] claude lock skipped (NIGHTLY_ORCHESTRATED=1, orchestrator-managed)" >&2
        return 0
    fi
    local waited=0
    # ...（既存のまま）
```

- [ ] **Step 2: 手動検証（lock がスキップされること）**

Run:
```bash
NIGHTLY_ORCHESTRATED=1 bash -c 'source scripts/runtime/nightly/lib/nightly-status.sh; acquire_claude_lock && echo "ACQUIRED ok"; [[ -d "$HOME/.cache/nightly/.lock-claude-p" ]] && echo "LOCK DIR EXISTS (BUG)" || echo "no lock dir (correct)"'
```
Expected: `ACQUIRED ok` と `no lock dir (correct)` が出る（lock ディレクトリが作られない）

### 5b: 偽成功検出を status_end に組み込む（全ジョブ横展開）

`status_end "ok" ... "report=<vault相対md>"` で呼ばれたとき、その md に `Execution error` が残っていれば `ok→fail` に倒す。これで `run-learned-promote.sh` 以外の 9 本にも検出が効く。

- [ ] **Step 3: `status_end` に検出ロジックを追加**

`nightly-status.sh` の `status_end()` 内、`# message も metric に含める`（現 93-94 行目）の**直前**に挿入:

```bash
    # 偽成功検出 (全ジョブ横展開): claude -p が失敗しつつ exit 0 で返り、呼び出し側が ok と
    # 誤判定したケースを最終 md から拾う。報告が Vault 相対 .md で実在する場合のみ検査する
    # (PR URL や別パスは対象外)。2 つの signal を見る:
    #   (a) 空 or 極小レポート (<50B): claude -p がほぼ何も書かず終わった = 失敗の典型。
    #       Execution error / Overloaded / Rate limit / 途中切れ等、マーカー文字列に依存せず
    #       捕捉できる最も頑健な signal。
    #   (b) 末尾 20 行に行頭 "execution error": マーカーが残るケース。全文 grep だと大規模
    #       レポート (audit/daily-report) の本文中の言及で False Fail するため末尾に限定する。
    if [[ "$status" == "ok" && -n "$report_path" && "$report_path" == *.md && -n "${OBSIDIAN_VAULT_PATH:-}" ]]; then
        local _report_abs="${OBSIDIAN_VAULT_PATH}/${report_path}"
        if [[ -f "$_report_abs" ]]; then
            local _sz
            _sz=$(wc -c < "$_report_abs" 2>/dev/null | tr -d ' ' || echo 0)
            if [[ "$_sz" =~ ^[0-9]+$ ]] && (( _sz < 50 )); then
                echo "[nightly] $task: false success (report nearly empty ${_sz}B); flipping ok→fail" >&2
                status="fail"
                msg="${msg:+$msg; }false success: report nearly empty (${_sz}B)"
            elif tail -n 20 "$_report_abs" 2>/dev/null | grep -qiE '^[[:space:]]*execution error'; then
                echo "[nightly] $task: false success (Execution error at report tail); flipping ok→fail" >&2
                status="fail"
                msg="${msg:+$msg; }false success: Execution error at report tail"
            fi
        fi
    fi
```

挿入位置の根拠: fail-count / orchestrator バイパス判定（5c で置換する 102-117 行目）より**前**に置くこと。これで ok→fail に倒した結果が後続のリトライ判定に正しく乗る。

**未捕捉の残リスク（Phase 2 候補）**: report は md に書けたが内容が「途中で API が Overloaded になり不完全」というケースは、空でなく末尾マーカーもないため捕捉できない。完全な捕捉には bash の `claude -p` 呼び出し箇所で raw stdout を検査する必要があり、各 run-*.sh のリダイレクト構造が異なるため Phase 2 に分離する。

- [ ] **Step 4: 手動検証（偽成功が fail に倒れること）**

Run:
```bash
tmpdir=$(mktemp -d)
mkdir -p "$tmpdir/06-Nightly"
printf 'Execution error\n\nsome output\n' > "$tmpdir/06-Nightly/fake.md"
OBSIDIAN_VAULT_PATH="$tmpdir" NIGHTLY_CACHE_DIR_OVERRIDE="$tmpdir/cache" NIGHTLY_NOTIFY_DISABLE=1 NIGHTLY_DATE_OVERRIDE=2026-06-13 \
  bash -c 'source scripts/runtime/nightly/lib/nightly-status.sh; status_begin faketask; status_end ok "" "report=06-Nightly/fake.md"'
echo "--- JSONL ---"
cat "$tmpdir/cache/status-2026-06-13.jsonl"
```
Expected: JSONL の `status` が `"fail"` になっている（`"status":"fail"` を含む）

- [ ] **Step 5: 回帰確認（正常 md は ok のまま）**

Run:
```bash
tmpdir=$(mktemp -d)
mkdir -p "$tmpdir/06-Nightly"
printf '# Report\n\n3 violations found\n' > "$tmpdir/06-Nightly/ok.md"
OBSIDIAN_VAULT_PATH="$tmpdir" NIGHTLY_CACHE_DIR_OVERRIDE="$tmpdir/cache" NIGHTLY_NOTIFY_DISABLE=1 NIGHTLY_DATE_OVERRIDE=2026-06-13 \
  bash -c 'source scripts/runtime/nightly/lib/nightly-status.sh; status_begin oktask; status_end ok "" "report=06-Nightly/ok.md"'
cat "$tmpdir/cache/status-2026-06-13.jsonl"
```
Expected: `status` が `"ok"` のまま

### 5c: fail-count リトライ機構を orchestrator モードでバイパス（CRITICAL 修正）

`status_end` の fail-count ブロック（現 102-117 行目、`local _do_mark=1 _fail_count=0` から `fi` まで）を、`NIGHTLY_ORCHESTRATED` 分岐を**先頭に追加**する形に書き換える。既存の `FORCE_RUN` / `fail` ロジックは `elif` として温存（launchd 直叩き時の後方互換）。

- [ ] **Step 1: fail-count ブロックを書き換える**

```bash
    local _do_mark=1 _fail_count=0
    if [[ "${NIGHTLY_ORCHESTRATED:-0}" == "1" ]]; then
        # orchestrator がリトライを制御する。bash の fail-count/翌日 catch-up 機構はバイパス。
        # ok → mark (last-run 更新で同日重複防止), fail → mark しない
        # (orchestrator が即リトライ。最終 fail でも未 mark → DAILY は翌夜再実行 /
        #  DOW・DOM は catch-up window で翌夜再試行)。
        # これをしないと前夜の fail-count が今夜 1 回目 fail を即 count=2 に押し上げ mark し、
        # orchestrator の再起動が should_run_today の "already ran today" で死ぬ (Gemini CRITICAL)。
        if [[ "$status" == "ok" ]]; then _do_mark=1; else _do_mark=0; fi
    elif [[ "${FORCE_RUN:-0}" == "1" ]]; then
        # 検証実行 (FORCE_RUN) は last-run も fail-count も汚さない (本番スケジュールと独立)
        _do_mark=0
    elif [[ "$status" == "fail" ]]; then
        _fail_count=$(( $(_read_fail_count "$task") + 1 ))
        if (( _fail_count >= 2 )); then
            echo "[nightly] $task: ${_fail_count} consecutive fails; giving up until next gate" >&2
            metric_obj=$(echo "$metric_obj" | jq --argjson n "$_fail_count" '. + {consecutive_fails: $n, retry: "gave up until next gate"}')
        else
            _do_mark=0
            _write_fail_count "$task" "$_fail_count"
            echo "[nightly] $task: fail (attempt ${_fail_count}); will retry via tomorrow catch-up" >&2
            metric_obj=$(echo "$metric_obj" | jq --argjson n "$_fail_count" '. + {consecutive_fails: $n, retry: "tomorrow catch-up"}')
        fi
    fi
```

- [ ] **Step 2: 手動検証（orchestrator モードで fail が mark されないこと）**

Run:
```bash
tmpdir=$(mktemp -d)
NIGHTLY_ORCHESTRATED=1 NIGHTLY_CACHE_DIR_OVERRIDE="$tmpdir/cache" NIGHTLY_NOTIFY_DISABLE=1 NIGHTLY_DATE_OVERRIDE=2026-06-13 \
  bash -c 'source scripts/runtime/nightly/lib/nightly-status.sh; status_begin t; status_end fail "boom"'
[[ -f "$tmpdir/cache/last-run-t.txt" ]] && echo "MARKED (BUG)" || echo "not marked (correct: orchestrator retries)"
[[ -f "$tmpdir/cache/fail-count-t.txt" ]] && echo "FAIL-COUNT WRITTEN (BUG)" || echo "no fail-count (correct)"
```
Expected: `not marked (correct...)` と `no fail-count (correct)`（orchestrator モードでは fail で last-run も fail-count も触らない）

- [ ] **Step 3: 回帰検証（非 orchestrator モードでは従来どおり fail-count が動く）**

Run:
```bash
tmpdir=$(mktemp -d)
NIGHTLY_CACHE_DIR_OVERRIDE="$tmpdir/cache" NIGHTLY_NOTIFY_DISABLE=1 NIGHTLY_DATE_OVERRIDE=2026-06-13 \
  bash -c 'source scripts/runtime/nightly/lib/nightly-status.sh; status_begin t; status_end fail "boom"'
cat "$tmpdir/cache/fail-count-t.txt"
```
Expected: `2026-06-13 1`（従来どおり fail 1 回目を記録）

### 5d: JSONL 並列追記を atomic-mkdir lock で排他（HIGH 修正）

`status_end` の JSONL 書き込み（現 131 行目 `echo "$line" >> "$NIGHTLY_STATUS_JSONL"`）を排他化する。

- [ ] **Step 1: JSONL 書き込みをロックで囲む**

131 行目を以下に置換:

```bash
    # 並列実行 (orchestrator) で複数ジョブが同時追記する際の行混ざりを防ぐ。detail が
    # PIPE_BUF (macOS 4096B) を超えると O_APPEND のアトミック性が崩れ、混ざった行を reader が
    # malformed スキップ → fail ジョブが missing 扱いで silent loss する (Gemini HIGH)。
    # atomic mkdir lock — 書き込みは一瞬なので競合待ちは最小。launchd 直叩き (単一プロセス) でも
    # 即取得で無害。macOS の flock(1) は標準で無いため mkdir を使う (既存 acquire_claude_lock 同様)。
    local _jsonl_lock="${NIGHTLY_STATUS_JSONL}.lockd" _jw=0
    while ! mkdir "$_jsonl_lock" 2>/dev/null; do
        sleep 0.05; _jw=$((_jw + 1))
        (( _jw >= 200 )) && { echo "[nightly] WARN: JSONL lock timeout (10s), writing anyway" >&2; break; }
    done
    echo "$line" >> "$NIGHTLY_STATUS_JSONL"
    rmdir "$_jsonl_lock" 2>/dev/null || true
```

- [ ] **Step 2: 並列追記の健全性検証（10 並列で長い detail を書いても全行が valid JSON）**

Run:
```bash
tmpdir=$(mktemp -d); cache="$tmpdir/cache"; mkdir -p "$cache"
big=$(head -c 5000 /dev/zero | tr '\0' 'x')   # 5KB の detail (PIPE_BUF 超)
for i in $(seq 1 10); do
  ( NIGHTLY_CACHE_DIR_OVERRIDE="$cache" NIGHTLY_NOTIFY_DISABLE=1 NIGHTLY_DATE_OVERRIDE=2026-06-13 \
    bash -c "source scripts/runtime/nightly/lib/nightly-status.sh; status_begin job$i; status_end ok '' 'detail=$big'" ) &
done
wait
total=$(wc -l < "$cache/status-2026-06-13.jsonl")
valid=$(jq -c . "$cache/status-2026-06-13.jsonl" 2>/dev/null | wc -l)
echo "total lines=$total valid JSON lines=$valid"
```
Expected: `total lines=10 valid JSON lines=10`（行混ざりゼロ。ロックなしだと valid < 10 になり得る）

### 5e: shellcheck + Commit

- [ ] **Step 1: shellcheck**

Run: `shellcheck scripts/runtime/nightly/lib/nightly-status.sh`
Expected: 既存と同レベル（新規 warning が増えていない）

- [ ] **Step 2: Commit**

```bash
git add scripts/runtime/nightly/lib/nightly-status.sh
git commit -m "feat(nightly): NIGHTLY_ORCHESTRATED スイッチ + 偽成功検出強化 + JSONL 排他"
```

---

## Task 6: orchestrator パッケージ（並列実行 + リトライ + 統合）

中核。semaphore で同時数を制限し、各ジョブを並列起動、fail なら 1 回だけ即リトライ、LOOP_DISABLED を尊重、NIGHTLY_DATE を 1 回確定して全ジョブへ配る。

**Files:**
- Create: `tools/nightly-orchestrator/internal/orchestrator/orchestrator.go`
- Test: `tools/nightly-orchestrator/internal/orchestrator/orchestrator_test.go`

- [ ] **Step 1: semaphore 依存を追加**

Run: `cd tools/nightly-orchestrator && go get golang.org/x/sync/semaphore`
Expected: go.mod に追加

- [ ] **Step 2: 失敗するテストを書く（fake script でリトライ・並列・LOOP_DISABLED を検証）**

```go
package orchestrator

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"sync/atomic"
	"testing"

	"github.com/takeuchishougo/nightly-orchestrator/internal/config"
	"github.com/takeuchishougo/nightly-orchestrator/internal/runner"
)

// status JSONL に追記する fake script を生成する。
// behavior: "ok" は常に ok を書く。"fail-then-ok" は 1 回目 fail / 2 回目 ok（リトライ検証）。
func fakeJobScript(t *testing.T, cacheDir, task, behavior string) string {
	t.Helper()
	dir := t.TempDir()
	p := filepath.Join(dir, task+".sh")
	body := fmt.Sprintf(`#!/usr/bin/env bash
set -uo pipefail
COUNT_FILE="%s/count-%s"
n=$(cat "$COUNT_FILE" 2>/dev/null || echo 0); n=$((n+1)); echo "$n" > "$COUNT_FILE"
ts=$(date +%%s)
if [[ "%s" == "fail-then-ok" && "$n" == "1" ]]; then
  status=fail
else
  status=ok
fi
echo "{\"ts\":\"$ts\",\"task\":\"%s\",\"status\":\"$status\",\"duration_sec\":0,\"report\":\"\",\"detail\":\"\",\"metric\":{}}" >> "%s/status-2026-06-13.jsonl"
exit 0
`, cacheDir, task, behavior, task, cacheDir)
	if err := os.WriteFile(p, []byte(body), 0o755); err != nil {
		t.Fatal(err)
	}
	return p
}

func TestRunRetriesFailedJob(t *testing.T) {
	cache := t.TempDir()
	script := fakeJobScript(t, cache, "golden-check", "fail-then-ok")
	cfg := &config.Config{
		Runtime: config.Runtime{MaxParallel: 2},
		Jobs: []config.Job{
			{Name: "golden-check", Script: script, TimeoutSec: 10, Retry: 1},
		},
	}
	o := New(cfg, Options{
		CacheDir:     cache,
		Date:         "2026-06-13",
		Runner:       runner.Runner{},
		ResolveScript: func(s string) string { return s }, // テストは絶対パスをそのまま
	})
	summary, err := o.Run(context.Background())
	if err != nil {
		t.Fatalf("Run: %v", err)
	}
	if summary.Results["golden-check"].Status != "ok" {
		t.Errorf("after retry, status = %q, want ok", summary.Results["golden-check"].Status)
	}
	if summary.Results["golden-check"].Attempts != 2 {
		t.Errorf("attempts = %d, want 2", summary.Results["golden-check"].Attempts)
	}
}

func TestRunHonorsLoopDisabled(t *testing.T) {
	cache := t.TempDir()
	disabledFile := filepath.Join(cache, "LOOP_DISABLED")
	os.WriteFile(disabledFile, []byte(""), 0o644)
	var started atomic.Int32
	script := fakeJobScript(t, cache, "audit", "ok")
	cfg := &config.Config{
		Runtime: config.Runtime{MaxParallel: 2},
		Jobs:    []config.Job{{Name: "audit", Script: script, TimeoutSec: 10}},
	}
	o := New(cfg, Options{
		CacheDir:         cache,
		Date:             "2026-06-13",
		LoopDisabledPath: disabledFile,
		Runner:           runner.Runner{},
		ResolveScript:    func(s string) string { started.Add(1); return s },
	})
	summary, err := o.Run(context.Background())
	if err != nil {
		t.Fatalf("Run: %v", err)
	}
	if started.Load() != 0 {
		t.Error("no job should start when LOOP_DISABLED present")
	}
	if !summary.Aborted {
		t.Error("summary.Aborted should be true")
	}
}
```

- [ ] **Step 3: テストが失敗することを確認**

Run: `cd tools/nightly-orchestrator && go test ./internal/orchestrator/`
Expected: FAIL（`New` undefined）

- [ ] **Step 4: orchestrator.go を実装**

```go
package orchestrator

import (
	"context"
	"os"
	"path/filepath"
	"sync"

	"github.com/takeuchishougo/nightly-orchestrator/internal/config"
	"github.com/takeuchishougo/nightly-orchestrator/internal/runner"
	"github.com/takeuchishougo/nightly-orchestrator/internal/status"
	"golang.org/x/sync/semaphore"
)

type Options struct {
	CacheDir         string                  // ~/.cache/nightly
	Date             string                  // NIGHTLY_DATE_OVERRIDE に渡す確定日付
	LoopDisabledPath string                  // ~/.claude/agent-memory/LOOP_DISABLED
	Runner           runner.Runner           // env 注入済み runner
	ResolveScript    func(rel string) string // repo 相対 → 絶対パス
}

type JobResult struct {
	Status   string // "ok" | "fail" | "missing"（JSONL に記録がない=gate skip）
	Attempts int
	Record   status.Record
}

type Summary struct {
	Aborted bool // LOOP_DISABLED で全 skip
	Results map[string]JobResult
}

type Orchestrator struct {
	cfg  *config.Config
	opts Options
}

func New(cfg *config.Config, opts Options) *Orchestrator {
	return &Orchestrator{cfg: cfg, opts: opts}
}

func (o *Orchestrator) statusPath() string {
	return filepath.Join(o.opts.CacheDir, "status-"+o.opts.Date+".jsonl")
}

func (o *Orchestrator) Run(ctx context.Context) (*Summary, error) {
	// グローバル circuit-breaker
	if o.opts.LoopDisabledPath != "" {
		if _, err := os.Stat(o.opts.LoopDisabledPath); err == nil {
			return &Summary{Aborted: true, Results: map[string]JobResult{}}, nil
		}
	}

	sem := semaphore.NewWeighted(int64(o.cfg.Runtime.MaxParallel))
	attempts := make(map[string]int)
	lastResults := make(map[string]runner.Result)
	var mu sync.Mutex
	var wg sync.WaitGroup

	for _, job := range o.cfg.Jobs {
		job := job
		wg.Add(1)
		go func() {
			defer wg.Done()
			if err := sem.Acquire(ctx, 1); err != nil {
				return
			}
			defer sem.Release(1)
			n, last := o.runWithRetry(ctx, job)
			mu.Lock()
			attempts[job.Name] = n
			lastResults[job.Name] = last
			mu.Unlock()
		}()
	}
	wg.Wait()

	// 全完了後に JSONL を 1 回読んで集約（task ごと最新）
	latest, err := status.ReadLatestByTask(o.statusPath())
	if err != nil {
		return nil, err
	}
	results := make(map[string]JobResult, len(o.cfg.Jobs))
	for _, job := range o.cfg.Jobs {
		jr := JobResult{Attempts: attempts[job.Name]}
		if rec, ok := latest[job.Name]; ok {
			jr.Status = rec.Status
			jr.Record = rec
		} else {
			// JSONL 記録なし: 正常終了なら真の gate skip。だが timeout/異常終了なら
			// status_end 前に死んだ or 行破損でスキップされた疑い → fail 扱いで救う
			// (silent loss を missing に偽装させない。Gemini HIGH 指摘の二重防御)。
			lr := lastResults[job.Name]
			if lr.TimedOut || lr.ExitCode != 0 {
				jr.Status = "fail"
				jr.Record = status.Record{Metric: map[string]string{"msg": abnormalMsg(lr)}}
			} else {
				jr.Status = "missing"
			}
		}
		results[job.Name] = jr
	}
	return &Summary{Results: results}, nil
}

func abnormalMsg(r runner.Result) string {
	if r.TimedOut {
		return "timed out, no JSONL record"
	}
	return "abnormal exit, no JSONL record"
}

// runWithRetry は 1 ジョブを起動し、JSONL が fail なら job.Retry 回まで即再起動する。
// NIGHTLY_ORCHESTRATED=1 により bash は fail で last-run を mark しないため、should_run_today が
// 再実行を弾かない（Task 5c）。戻り値は (試行回数, 最後の runner.Result)。
func (o *Orchestrator) runWithRetry(ctx context.Context, job config.Job) (int, runner.Result) {
	abs := o.opts.ResolveScript(job.Script)
	attempts := 0
	var last runner.Result
	for {
		attempts++
		last = o.opts.Runner.Run(ctx, job.Name, abs, job.TimeoutSec)
		if attempts > job.Retry {
			break
		}
		// JSONL を読んでこの task の最新が fail かを判定
		latest, err := status.ReadLatestByTask(o.statusPath())
		if err != nil {
			break
		}
		rec, ok := latest[job.Name]
		if !ok {
			// JSONL 記録なし。異常終了なら status_end 前に死んだ可能性 → リトライ。
			// 正常終了で記録なしは真の gate skip → リトライ不要。
			if last.TimedOut || last.ExitCode != 0 {
				continue
			}
			break
		}
		if rec.Status != "fail" {
			break // 成功 → リトライ不要
		}
		// fail → ループ継続（即リトライ）
	}
	return attempts, last
}
```

- [ ] **Step 5: テストが通ることを確認**

Run: `cd tools/nightly-orchestrator && go test ./internal/orchestrator/`
Expected: PASS（`TestRunRetriesFailedJob` と `TestRunHonorsLoopDisabled` 両方）

- [ ] **Step 6: Commit**

```bash
git add tools/nightly-orchestrator/internal/orchestrator tools/nightly-orchestrator/go.mod tools/nightly-orchestrator/go.sum
git commit -m "feat(nightly): orchestrator 並列実行 + 即時リトライ + LOOP_DISABLED"
```

---

## Task 7: notify パッケージ（Discord 集約通知）

全完了後の Summary を 1 通の embed にまとめて既存 webhook に送る。webhook URL は `~/.config/notifications/discord.env` から読む。

**Files:**
- Create: `tools/nightly-orchestrator/internal/notify/notify.go`
- Test: `tools/nightly-orchestrator/internal/notify/notify_test.go`

- [ ] **Step 1: 失敗するテストを書く（payload 生成を純粋関数として検証）**

```go
package notify

import (
	"strings"
	"testing"

	"github.com/takeuchishougo/nightly-orchestrator/internal/orchestrator"
)

func TestBuildPayloadAllOK(t *testing.T) {
	sum := &orchestrator.Summary{Results: map[string]orchestrator.JobResult{
		"golden-check": {Status: "ok"},
		"audit":        {Status: "missing"}, // gate skip
	}}
	p := BuildPayload(sum, "2026-06-13")
	if p.failCount() != 0 {
		t.Errorf("failCount = %d, want 0", p.failCount())
	}
	if got := p.Embeds[0].Color; got != 3066993 {
		t.Errorf("color = %d, want green 3066993", got)
	}
	if strings.Contains(p.Content, "@here") {
		t.Error("no @here mention when all ok")
	}
}

func TestBuildPayloadWithFailure(t *testing.T) {
	sum := &orchestrator.Summary{Results: map[string]orchestrator.JobResult{
		"golden-check": {Status: "ok"},
		"audit":        {Status: "fail", Attempts: 2, Record: recordWithMsg("crash")},
	}}
	p := BuildPayload(sum, "2026-06-13")
	if p.failCount() != 1 {
		t.Errorf("failCount = %d, want 1", p.failCount())
	}
	if p.Embeds[0].Color != 15158332 {
		t.Errorf("color = %d, want red 15158332", p.Embeds[0].Color)
	}
	if !strings.Contains(p.Content, "@here") {
		t.Error("expected @here mention on failure")
	}
	if !strings.Contains(p.Embeds[0].Description, "audit") {
		t.Error("failed job name should appear in description")
	}
}

func TestBuildPayloadAborted(t *testing.T) {
	sum := &orchestrator.Summary{Aborted: true, Results: map[string]orchestrator.JobResult{}}
	p := BuildPayload(sum, "2026-06-13")
	if !strings.Contains(p.Embeds[0].Title, "LOOP_DISABLED") {
		t.Error("aborted summary should mention LOOP_DISABLED in title")
	}
}
```

`recordWithMsg` ヘルパは notify_test.go 内に置く:

```go
func recordWithMsg(msg string) orchestrator.JobResult { return orchestrator.JobResult{} }.Record // placeholder
```

（注: 実装 Step で `status.Record` を直接構築するため、テストヘルパは下の Step 2 で確定形にする）

- [ ] **Step 2: テストヘルパを確定（status.Record を import して msg を埋める）**

notify_test.go の冒頭 import に `"github.com/takeuchishougo/nightly-orchestrator/internal/status"` を追加し、ヘルパを差し替え:

```go
func recordWithMsg(msg string) status.Record {
	return status.Record{Metric: map[string]string{"msg": msg}}
}
```

`TestBuildPayloadWithFailure` の `Record: recordWithMsg("crash")` がこれで `status.Record` を返す。

- [ ] **Step 3: テストが失敗することを確認**

Run: `cd tools/nightly-orchestrator && go test ./internal/notify/`
Expected: FAIL（`BuildPayload` undefined）

- [ ] **Step 4: notify.go を実装**

```go
package notify

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"sort"
	"strings"
	"time"

	"github.com/takeuchishougo/nightly-orchestrator/internal/orchestrator"
)

type Payload struct {
	Content string  `json:"content"`
	Embeds  []Embed `json:"embeds"`
}

type Embed struct {
	Title       string `json:"title"`
	Description string `json:"description"`
	Color       int    `json:"color"`
	Timestamp   string `json:"timestamp"`
}

func (p Payload) failCount() int {
	n := 0
	for _, line := range strings.Split(p.Embeds[0].Description, "\n") {
		if strings.HasPrefix(line, "❌") {
			n++
		}
	}
	return n
}

// BuildPayload は Summary を 1 通の embed に変換する純粋関数（送信副作用なし）。
func BuildPayload(sum *orchestrator.Summary, date string) Payload {
	const green, red = 3066993, 15158332
	ts := time.Now().Format(time.RFC3339)

	if sum.Aborted {
		return Payload{
			Content: "",
			Embeds: []Embed{{
				Title:       fmt.Sprintf("⏸️ nightly %s: LOOP_DISABLED（全ジョブ skip）", date),
				Description: "circuit-breaker が有効なため夜間バッチを実行しませんでした。",
				Color:       green,
				Timestamp:   ts,
			}},
		}
	}

	names := make([]string, 0, len(sum.Results))
	for n := range sum.Results {
		names = append(names, n)
	}
	sort.Strings(names)

	var b strings.Builder
	failed := 0
	for _, n := range names {
		r := sum.Results[n]
		switch r.Status {
		case "ok":
			fmt.Fprintf(&b, "✅ %s\n", n)
		case "missing":
			fmt.Fprintf(&b, "➖ %s (skip)\n", n)
		default: // fail
			failed++
			msg := r.Record.Metric["msg"]
			fmt.Fprintf(&b, "❌ %s (%d 回試行) — %s\n", n, r.Attempts, msg)
		}
	}

	color := green
	content := ""
	title := fmt.Sprintf("✅ nightly %s: 全ジョブ正常", date)
	if failed > 0 {
		color = red
		content = "@here"
		title = fmt.Sprintf("❌ nightly %s: %d 件失敗", date, failed)
	}

	return Payload{
		Content: content,
		Embeds: []Embed{{
			Title:       title,
			Description: b.String(),
			Color:       color,
			Timestamp:   ts,
		}},
	}
}

// Send は payload を webhook に POST する。URL 空なら no-op（bash と同じく通知失敗で全体は壊さない）。
func Send(webhookURL string, p Payload) error {
	if webhookURL == "" {
		return nil
	}
	body, err := json.Marshal(p)
	if err != nil {
		return err
	}
	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Post(webhookURL, "application/json", bytes.NewReader(body))
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 && resp.StatusCode != 204 {
		return fmt.Errorf("discord webhook returned %d", resp.StatusCode)
	}
	return nil
}
```

- [ ] **Step 5: テストが通ることを確認**

Run: `cd tools/nightly-orchestrator && go test ./internal/notify/`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tools/nightly-orchestrator/internal/notify
git commit -m "feat(nightly): Discord 集約通知 (1 通サマリ)"
```

---

## Task 8: main.go 統合 + フラグ

全パッケージを束ねる。`--dry-run`（起動せず計画表示）、`--once <job>`（1 ジョブだけ手動実行）を持たせて移行検証を可能にする。

**Files:**
- Modify: `tools/nightly-orchestrator/main.go`

- [ ] **Step 1: main.go を実装**

```go
package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/takeuchishougo/nightly-orchestrator/internal/config"
	"github.com/takeuchishougo/nightly-orchestrator/internal/notify"
	"github.com/takeuchishougo/nightly-orchestrator/internal/orchestrator"
	"github.com/takeuchishougo/nightly-orchestrator/internal/runner"
)

func main() {
	var (
		jobsPath = flag.String("jobs", "", "path to jobs.yaml (default: alongside binary)")
		dryRun   = flag.Bool("dry-run", false, "print plan and exit")
	)
	flag.Parse()

	if err := run(*jobsPath, *dryRun); err != nil {
		fmt.Fprintln(os.Stderr, "nightly-orchestrator:", err)
		os.Exit(1)
	}
}

func run(jobsPath string, dryRun bool) error {
	repoRoot, err := resolveRepoRoot()
	if err != nil {
		return err
	}
	if jobsPath == "" {
		jobsPath = filepath.Join(repoRoot, "tools", "nightly-orchestrator", "jobs.yaml")
	}
	data, err := os.ReadFile(jobsPath)
	if err != nil {
		return fmt.Errorf("read jobs.yaml: %w", err)
	}
	cfg, err := config.Parse(data)
	if err != nil {
		return err
	}

	home, _ := os.UserHomeDir()
	date := time.Now().Format("2006-01-02")
	cacheDir := filepath.Join(home, ".cache", "nightly")

	if dryRun {
		fmt.Printf("nightly-orchestrator dry-run (date=%s, max_parallel=%d)\n", date, cfg.Runtime.MaxParallel)
		for _, j := range cfg.Jobs {
			fmt.Printf("  - %-18s timeout=%ds retry=%d  %s\n", j.Name, j.TimeoutSec, j.Retry, j.Script)
		}
		return nil
	}

	// 自プロセス実行中のスリープを確実に抑止する。caffeinate plist の起動順/タイミングに
	// 依存せず、orchestrator が生きている間 (-w <pid>) だけスリープを止める二重保険。
	if cf, err := exec.LookPath("caffeinate"); err == nil {
		_ = exec.Command(cf, "-i", "-w", fmt.Sprintf("%d", os.Getpid())).Start()
	}

	// orchestrator が全ジョブへ配る共通 env
	commonEnv := map[string]string{
		"NIGHTLY_ORCHESTRATED":   "1",  // claude lock 無効化 + fail-count リトライ機構バイパス（Task 5a/5c）
		"NIGHTLY_NOTIFY_DISABLE": "1",  // 個別 Discord 通知を抑制（集約 1 通に一本化）
		"NIGHTLY_DATE_OVERRIDE":  date, // 0 時跨ぎの日付ズレ根治（全ジョブ同一日付）
		"OBSIDIAN_VAULT_PATH":    os.Getenv("OBSIDIAN_VAULT_PATH"),
		"NIGHTLY_CLAUDE_MODEL":   envOr("NIGHTLY_CLAUDE_MODEL", "claude-sonnet-4-6"),
	}

	o := orchestrator.New(cfg, orchestrator.Options{
		CacheDir:         cacheDir,
		Date:             date,
		LoopDisabledPath: filepath.Join(home, ".claude", "agent-memory", "LOOP_DISABLED"),
		Runner:           runner.Runner{Env: commonEnv},
		ResolveScript:    func(rel string) string { return filepath.Join(repoRoot, rel) },
	})

	ctx := context.Background()
	summary, err := o.Run(ctx)
	if err != nil {
		return err
	}

	// 集約通知（webhook URL は discord.env から読む）
	webhook := readWebhookURL(home)
	payload := notify.BuildPayload(summary, date)
	if err := notify.Send(webhook, payload); err != nil {
		fmt.Fprintln(os.Stderr, "warn: discord send failed:", err)
	}
	return nil
}

func envOr(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}

// resolveRepoRoot は binary の位置 (tools/nightly-orchestrator/) から 2 階層上を repo root とする。
// go run 時など解決できない場合は git に委譲。
func resolveRepoRoot() (string, error) {
	exe, err := os.Executable()
	if err == nil {
		root := filepath.Dir(filepath.Dir(filepath.Dir(exe))) // tools/nightly-orchestrator/<bin> → repo
		if _, err := os.Stat(filepath.Join(root, "CLAUDE.md")); err == nil {
			return root, nil
		}
	}
	out, err := exec.Command("git", "rev-parse", "--show-toplevel").Output()
	if err != nil {
		return "", fmt.Errorf("resolve repo root: %w", err)
	}
	return strings.TrimSpace(string(out)), nil
}

// readWebhookURL は ~/.config/notifications/discord.env から DISCORD_WEBHOOK_URL を抽出する。
func readWebhookURL(home string) string {
	f, err := os.Open(filepath.Join(home, ".config", "notifications", "discord.env"))
	if err != nil {
		return ""
	}
	defer f.Close()
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		line := strings.TrimSpace(sc.Text())
		if strings.HasPrefix(line, "DISCORD_WEBHOOK_URL=") {
			v := strings.TrimPrefix(line, "DISCORD_WEBHOOK_URL=")
			v = strings.Trim(v, `"'`)
			return v
		}
	}
	return ""
}
```

- [ ] **Step 2: ビルド + dry-run 確認**

Run: `cd tools/nightly-orchestrator && go build -o nightly-orchestrator . && ./nightly-orchestrator --dry-run`
Expected: 10 ジョブが timeout/retry 付きで一覧表示される

- [ ] **Step 3: 全テスト + vet**

Run: `cd tools/nightly-orchestrator && go test ./... && go vet ./...`
Expected: 全 PASS、vet クリーン

- [ ] **Step 4: Commit**

```bash
git add tools/nightly-orchestrator/main.go
git commit -m "feat(nightly): main 統合 + --dry-run"
```

---

## Task 9: launchd 単一エントリ化

11 個別 plist を廃止し、orchestrator 1 本に置き換える。caffeinate（スリープ抑止アンブレラ）は LLM ジョブではないので別 plist で維持する。

**Files:**
- Modify: `scripts/runtime/nightly/launchd-install.sh:25-46`（TASKS 配列 + orchestrator エントリ）
- Modify: `scripts/runtime/nightly/launchd-uninstall.sh`

- [ ] **Step 1: orchestrator バイナリのビルドを install スクリプトに組み込む**

`launchd-install.sh` の TASKS 定義の前に、orchestrator のビルドステップを追加:

```bash
# orchestrator バイナリをビルド（launchd は絶対パスでバイナリを叩く）
ORCH_DIR="${TASKFILE_DIR:-$(git -C "$NIGHTLY_DIR" rev-parse --show-toplevel)}/tools/nightly-orchestrator"
echo "=== Building nightly-orchestrator ==="
( cd "$ORCH_DIR" && go build -o nightly-orchestrator . ) || { echo "ERROR: orchestrator build failed" >&2; exit 1; }
ORCH_BIN="${ORCH_DIR}/nightly-orchestrator"
```

- [ ] **Step 2: TASKS 配列を caffeinate + orchestrator の 2 エントリに置き換える**

現 TASKS 配列（25-46 行目）を以下に置換:

```bash
# 移行後: 個別 11 ジョブは orchestrator が内部で並列実行する。
# launchd エントリは caffeinate（スリープ抑止）と orchestrator の 2 本のみ。
TASKS=(
    # caffeinate アンブレラ: wake 時刻に発火し、バッチ完了までスリープを抑止
    "caffeinate|${NIGHTLY_WAKE_HOUR}|${NIGHTLY_WAKE_MINUTE}|nightly-caffeinate.sh"
)
# orchestrator は別関数で専用 plist を生成（ProgramArguments が go バイナリで bash と異なるため）
```

- [ ] **Step 3: orchestrator 専用 plist 生成関数を追加**

`generate_plist()` の後に追加:

```bash
generate_orchestrator_plist() {
    local plist="$AGENTS_DIR/com.user.nightly.orchestrator.plist"
    # caffeinate (22:15) の 2 分後に起動し、スリープ抑止下で全ジョブを回す
    cat > "$plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.nightly.orchestrator</string>
    <key>ProgramArguments</key>
    <array>
        <string>${ORCH_BIN}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>${NIGHTLY_WAKE_HOUR}</integer>
        <key>Minute</key><integer>$((NIGHTLY_WAKE_MINUTE + 2))</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/nightly-orchestrator.launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/nightly-orchestrator.launchd.log</string>
    <key>WorkingDirectory</key>
    <string>${HOME}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key><string>${PATH}</string>
        <key>HOME</key><string>${HOME}</string>
        <key>TZ</key><string>Asia/Tokyo</string>
        <key>OBSIDIAN_VAULT_PATH</key><string>${OBSIDIAN_VAULT_PATH}</string>
        <key>NIGHTLY_CLAUDE_MODEL</key><string>${NIGHTLY_CLAUDE_MODEL:-claude-sonnet-4-6}</string>
    </dict>
</dict>
</plist>
PLIST
    plutil -lint "$plist" >/dev/null || { echo "ERROR: invalid orchestrator plist" >&2; return 1; }
    echo "$plist"
}
```

- [ ] **Step 4: install ループの後に orchestrator plist の load を追加**

既存の caffeinate load ループの後に:

```bash
echo "=== Installing orchestrator LaunchAgent ==="
orch_plist=$(generate_orchestrator_plist) || exit 1
launchctl unload "$orch_plist" 2>/dev/null || true
launchctl load "$orch_plist"
echo "  loaded com.user.nightly.orchestrator (starts $((NIGHTLY_WAKE_MINUTE + 2)) past ${NIGHTLY_WAKE_HOUR}:00)"
```

- [ ] **Step 5: uninstall スクリプトを旧 11 エントリ + orchestrator 両対応にする**

`launchd-uninstall.sh` を確認し、`com.user.nightly.*` を glob で全 unload するように更新（旧個別エントリの掃除も兼ねる）:

```bash
#!/usr/bin/env bash
set -euo pipefail
AGENTS_DIR="$HOME/Library/LaunchAgents"
echo "=== Uninstalling all com.user.nightly.* LaunchAgents ==="
for plist in "$AGENTS_DIR"/com.user.nightly.*.plist; do
    [[ -f "$plist" ]] || continue
    label=$(basename "$plist" .plist)
    launchctl unload "$plist" 2>/dev/null || true
    rm -f "$plist"
    echo "  removed $label"
done
```

- [ ] **Step 6: plist 生成の lint 確認（load はしない）**

Run: `bash -n scripts/runtime/nightly/launchd-install.sh && shellcheck scripts/runtime/nightly/launchd-install.sh scripts/runtime/nightly/launchd-uninstall.sh`
Expected: 構文エラーなし、shellcheck 既存レベル

- [ ] **Step 7: Commit**

```bash
git add scripts/runtime/nightly/launchd-install.sh scripts/runtime/nightly/launchd-uninstall.sh
git commit -m "feat(nightly): launchd を orchestrator 単一エントリ化 (caffeinate は維持)"
```

---

## Task 10: 移行 + 検証 + rollback

無人で毎晩回る土台の切替なので、検証手順と rollback を明示する。**1 晩並走は不可**（同じ JSONL / last-run / lock を共有するため二重実行になる）。代わりに「日中 dry-run + 手動 1 ジョブ実行 → 1 晩 orchestrator 単独 → 翌朝 JSONL 検証」の順で切る。

**Files:**
- Create: `docs/playbooks/nightly-orchestrator-migration.md`

- [ ] **Step 1: 日中の動作確認（FORCE_RUN で本番状態を汚さずに 1 ジョブ実行）**

Run:
```bash
cd tools/nightly-orchestrator && go build -o nightly-orchestrator .
# dry-run で計画を確認
./nightly-orchestrator --dry-run
# 軽量ジョブ 1 本を手動実行（FORCE_RUN=1 で gate 無視、NIGHTLY_NOTIFY_DISABLE=1 で通知抑制、
# last-run/fail-count を汚さない）。golden-check を直接叩いて偽成功検出と JSONL 書き込みを確認。
FORCE_RUN=1 NIGHTLY_SKIP_LOCK=1 NIGHTLY_NOTIFY_DISABLE=1 \
  bash scripts/runtime/nightly/run-golden-check.sh
cat ~/.cache/nightly/status-$(date +%Y-%m-%d).jsonl | tail -1 | jq .
```
Expected: golden-check の JSONL レコードが 1 行追記され、`status` が記録される

- [ ] **Step 2: 旧個別 plist を全 unload（切替）**

Run:
```bash
bash scripts/runtime/nightly/launchd-uninstall.sh
launchctl list | grep nightly || echo "全 nightly エントリ削除済み"
```
Expected: 旧 11 エントリが消えている

- [ ] **Step 3: orchestrator + caffeinate を install**

Run:
```bash
task nightly:install   # または bash scripts/runtime/nightly/launchd-install.sh
launchctl list | grep nightly
```
Expected: `com.user.nightly.caffeinate` と `com.user.nightly.orchestrator` の 2 本のみ

- [ ] **Step 4: 翌朝の検証（1 晩走らせた後）**

Run:
```bash
# orchestrator のログ
cat /tmp/nightly-orchestrator.launchd.log
# JSONL に全 DAILY ジョブの最新レコードがあるか
jq -r '.task + " " + .status' ~/.cache/nightly/status-$(date +%Y-%m-%d).jsonl | sort -u
# Discord に集約 1 通が届いているか（手元で確認）
```
Expected: golden-check / friction-aggregate / health-check / daily-report / plan-close-scan / tech-researcher が `ok`、Discord に 1 通だけ届く

- [ ] **Step 5: morning-briefing 連携の回帰確認**

morning-briefing は前夜 JSONL を読む（変更不要のはず）。日付統一で 0 時跨ぎズレが消えたことを確認:

Run:
```bash
# 前夜分の JSONL が 1 つの日付ファイルに収まっているか（0:50 plan-close-scan も同じ日付か）
ls -la ~/.cache/nightly/status-*.jsonl | tail -3
jq -r .task ~/.cache/nightly/status-$(date -j -v-1d +%Y-%m-%d 2>/dev/null || date -d yesterday +%Y-%m-%d).jsonl | sort -u
```
Expected: plan-close-scan を含む全ジョブが前夜 1 ファイルに入っている（従来は 0 時跨ぎで別ファイルに分離していた）

- [ ] **Step 6: rollback 手順を playbook に記載**

`docs/playbooks/nightly-orchestrator-migration.md` を作成し、以下を記載:

```markdown
# Nightly Orchestrator 移行 playbook

## 切替（ビルド先行で空白期間を作らない）
1. `cd tools/nightly-orchestrator && go build -o nightly-orchestrator .` ← **ビルド成功を必ず先に確認**
2. `./nightly-orchestrator --dry-run` で計画を確認
3. `bash scripts/runtime/nightly/launchd-uninstall.sh`（旧 11 エントリ削除）
4. `task nightly:install`（caffeinate + orchestrator。内部で再ビルド）

**重要**: 1 でビルドが通らなければ 3 に進まない。先に uninstall すると、ビルド失敗時に
その夜のバッチが caffeinate 以外 1 本も起動しない空白が生じる（Gemini 指摘）。

## Rollback（orchestrator に問題が出た夜の翌日）
旧個別 plist 方式に戻す:
1. `launchctl unload ~/Library/LaunchAgents/com.user.nightly.orchestrator.plist && rm 同ファイル`
2. launchd commit を revert: `git revert <Task 9: launchd orchestrator 化 commit>`
3. `task nightly:install`（旧 11 エントリが復活）

**lib 変更（Task 5）は revert 不要**: `NIGHTLY_ORCHESTRATED` 未設定の旧 launchd 直叩きでは
lock/fail-count は従来動作（後方互換）、JSONL lock は単一プロセスで即取得＝無害。偽成功検出のみ
常時有効だが望ましい改善なので残す。完全に旧 lib へ戻す場合のみ Task 5 commit も revert する
（半移行状態でも壊れない設計だが、挙動を完全一致させたいとき）。

## 緊急停止（その夜だけ止める）
`touch ~/.claude/agent-memory/LOOP_DISABLED`
→ orchestrator は全ジョブ skip し「LOOP_DISABLED」サマリを Discord に送る。
解除: `rm ~/.claude/agent-memory/LOOP_DISABLED`

## 既知の注意
- 1 晩並走は不可（JSONL / last-run / lock 共有のため二重実行になる）
- orchestrator は go バイナリ。コード変更後は `task nightly:install` で再ビルドが必要
- 切替は必ず「ビルド成功確認 → uninstall → install」の順
```

- [ ] **Step 7: Commit**

```bash
git add docs/playbooks/nightly-orchestrator-migration.md
git commit -m "docs(nightly): orchestrator 移行 + rollback playbook"
```

---

## Self-Review チェック結果

**1. Spec coverage（合意した設計骨子 → タスク対応）:**
- 並列実行（semaphore=3）→ Task 6 ✓
- lock 根治（NIGHTLY_SKIP_LOCK）→ Task 5a ✓
- 日付統一（NIGHTLY_DATE_OVERRIDE）→ Task 8 commonEnv + Task 6 ✓
- 偽成功検出の全ジョブ横展開 → Task 5b ✓
- 即時リトライ（fail-count 協調）→ Task 6 runWithRetry ✓
- 集約 Discord 通知（1 通）→ Task 7 + Task 8 ✓
- 個別通知抑制 → Task 8 commonEnv `NIGHTLY_NOTIFY_DISABLE=1` ✓
- launchd 単一エントリ + caffeinate 維持 → Task 9 ✓
- 移行 + rollback → Task 10 ✓
- フォールバック（codex/cursor）→ **Phase 2 として意図的に分離**（本 Plan 対象外）

**2. Placeholder scan:** Task 7 Step 1 の `recordWithMsg` placeholder は Step 2 で確定形に差し替える手順を明示済み（意図的な 2 段階）。他に TBD/TODO なし。

**3. Type consistency:** `status.Record`（status pkg）→ `orchestrator.JobResult.Record`（同じ型を埋め込み）→ `notify.BuildPayload` が `r.Record.Metric["msg"]` で参照。`config.Job.Name/Script/TimeoutSec/Retry` は Task 2 定義 → Task 6/8 で一貫使用。`runner.Runner.Run(ctx, task, scriptPath, timeoutSec)` シグネチャは Task 4 定義 → Task 6 で一貫。

**Gemini 敵対的レビューで修正済み（Task に反映）:**
- リトライ vs fail-count の **CRITICAL 衝突**（前夜 fail が今夜 1 回目 fail を即諦めさせる）→ Task 5c の `NIGHTLY_ORCHESTRATED` バイパスで解消
- JSONL 並列追記の行混ざり → **silent loss** → Task 5d の atomic-mkdir lock + Task 6 の異常終了救済で二重防御
- 偽成功検出の False Fail（大規模 md の本文）/ False OK（空・マーカーなし）→ Task 5b の末尾 20 行 + 空ファイル検出
- 移行の空白期間 / caffeinate 起動ラグ / 半移行 rollback → Task 8 self-caffeinate + Task 10 playbook（ビルド先行・lib 後方互換明記）

**残存リスク（実装時に確認）:**
1. **偽成功の完全捕捉**: 「md は書けたが内容が API Overloaded で不完全」は空でも末尾マーカーもなく未捕捉。完全捕捉は各 run-*.sh の `claude -p` raw stdout 検査が必要 → Phase 2 に分離。
2. **JSONL lock の粒度**: `sleep 0.05` ポーリングで 10s 上限に達したら排他なしで書く fallback。10 並列・大 detail で競合頻度を実測（Task 5d Step 2）。
3. **tech-researcher の script パス**: jobs.yaml で repo ルート相対に正規化済（`scripts/runtime/tech-researcher/run-tech-researcher.sh`）。実パス存在を Task 2 Step 6 後に確認。
4. **Task 6 テストの追加**: 現テストは retry / LOOP_DISABLED の 2 ケース。Task 5c バイパスと Task 6 の異常終了救済（missing→fail）の結合テストを実装時に 1 ケース追加推奨。
5. **NIGHTLY_DATE と実時刻の差**: orchestrator が 22 時台に全ジョブを回す前提なら実時刻 = override で問題なし。fail-count ファイルは実時刻日付だが orchestrator モードでは fail-count 不使用のため影響しない。

---

## Execution Handoff

Plan を `docs/plans/active/2026-06-13-nightly-orchestrator-plan.md` に保存しました。
