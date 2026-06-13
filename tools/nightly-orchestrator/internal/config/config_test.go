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
