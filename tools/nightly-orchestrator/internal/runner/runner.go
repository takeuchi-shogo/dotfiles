package runner

import (
	"context"
	"os"
	"os/exec"
	"syscall"
	"time"
)

// Runner は 1 ジョブを 1 回起動する責務だけを持つ。
// リトライは orchestrator が担う。
type Runner struct {
	// Env は全ジョブ共通で注入する環境変数（NIGHTLY_ORCHESTRATED 等）。
	// os.Environ() に上書きマージされる。
	Env map[string]string
}

// Result は 1 回の実行結果を表す。
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
