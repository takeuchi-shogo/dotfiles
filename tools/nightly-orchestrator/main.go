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

	if cf, err := exec.LookPath("caffeinate"); err == nil {
		if err := exec.Command(cf, "-i", "-w", fmt.Sprintf("%d", os.Getpid())).Start(); err != nil {
			fmt.Fprintln(os.Stderr, "warn: caffeinate:", err)
		}
	}

	commonEnv := map[string]string{
		"NIGHTLY_ORCHESTRATED":   "1",
		"NIGHTLY_NOTIFY_DISABLE": "1",
		"NIGHTLY_DATE_OVERRIDE":  date,
		"OBSIDIAN_VAULT_PATH":    os.Getenv("OBSIDIAN_VAULT_PATH"),
		"NIGHTLY_CODEX_MODEL":    envOr("NIGHTLY_CODEX_MODEL", "gpt-5.6-terra"),
		"NIGHTLY_CODEX_EFFORT":   envOr("NIGHTLY_CODEX_EFFORT", "high"),
		"NIGHTLY_CODEX_BIN":      envOr("NIGHTLY_CODEX_BIN", "codex"),
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

func resolveRepoRoot() (string, error) {
	exe, err := os.Executable()
	if err == nil {
		root := filepath.Dir(filepath.Dir(filepath.Dir(exe)))
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

func readWebhookURL(home string) string {
	f, err := os.Open(filepath.Join(home, ".config", "notifications", "discord.env"))
	if err != nil {
		return ""
	}
	defer f.Close()
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		line := strings.TrimSpace(sc.Text())
		if v, ok := strings.CutPrefix(line, "DISCORD_WEBHOOK_URL="); ok {
			return strings.Trim(v, `"'`)
		}
	}
	return ""
}
