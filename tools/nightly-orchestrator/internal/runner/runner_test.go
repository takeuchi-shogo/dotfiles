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
	script := writeScript(t, `echo "$NIGHTLY_ORCHESTRATED $NIGHTLY_NOTIFY_DISABLE $NIGHTLY_DATE_OVERRIDE" > "`+out+`"`)
	r := Runner{
		Env: map[string]string{
			"NIGHTLY_ORCHESTRATED":   "1",
			"NIGHTLY_NOTIFY_DISABLE": "1",
			"NIGHTLY_DATE_OVERRIDE":  "2026-06-13",
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
