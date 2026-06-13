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
		CacheDir:      cache,
		Date:          "2026-06-13",
		Runner:        runner.Runner{},
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

// TestMissingRescue: fake script が非ゼロ終了し JSONL を書かない場合、
// orchestrator が該当ジョブを "fail" として報告すること（silent loss 防止）。
func TestMissingRescue(t *testing.T) {
	cache := t.TempDir()
	// JSONL を書かずに exit 1 する fake script
	dir := t.TempDir()
	p := filepath.Join(dir, "failing-job.sh")
	body := "#!/usr/bin/env bash\nexit 1\n"
	if err := os.WriteFile(p, []byte(body), 0o755); err != nil {
		t.Fatal(err)
	}

	cfg := &config.Config{
		Runtime: config.Runtime{MaxParallel: 1},
		Jobs: []config.Job{
			{Name: "failing-job", Script: p, TimeoutSec: 10, Retry: 0},
		},
	}
	o := New(cfg, Options{
		CacheDir:      cache,
		Date:          "2026-06-13",
		Runner:        runner.Runner{},
		ResolveScript: func(s string) string { return s },
	})
	summary, err := o.Run(context.Background())
	if err != nil {
		t.Fatalf("Run: %v", err)
	}
	jr, ok := summary.Results["failing-job"]
	if !ok {
		t.Fatal("expected result for failing-job")
	}
	if jr.Status != "fail" {
		t.Errorf("missing-rescue: status = %q, want fail", jr.Status)
	}
}
