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
				// rescue assumes gate-skip paths exit 0; only abnormal exit/timeout with no JSONL becomes fail.
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
		// cmd-exit happens-before: bash 子プロセスの書き込み完了は cmd.Run() 返却前に保証される。
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
