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
