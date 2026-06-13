package notify

import (
	"strings"
	"testing"

	"github.com/takeuchishougo/nightly-orchestrator/internal/orchestrator"
	"github.com/takeuchishougo/nightly-orchestrator/internal/status"
)

func recordWithMsg(msg string) status.Record {
	return status.Record{Metric: map[string]string{"msg": msg}}
}

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
