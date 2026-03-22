package batch

import (
	"fmt"
	"sort"
	"strings"
	"time"

	"github.com/fatih/color"

	"github.com/takeuchishougo/osa/internal/model"
)

// Summary holds aggregated statistics across multiple sessions.
type Summary struct {
	Count         int
	TotalDuration float64
	TotalTools    int
	TotalErrors   int
	Tokens        model.TokenUsage
	Sessions      []*model.SessionSpan
}

// Aggregate computes a batch summary from multiple sessions.
func Aggregate(sessions []*model.SessionSpan) *Summary {
	s := &Summary{
		Count:    len(sessions),
		Sessions: sessions,
	}
	for _, sess := range sessions {
		s.TotalDuration += sess.Duration.Seconds()
		s.TotalTools += sess.TotalToolCalls()
		s.TotalErrors += sess.TotalErrors()
		s.Tokens.Merge(sess.Tokens)
	}
	return s
}

// Print outputs batch summary to stdout.
func (s *Summary) Print() {
	bold := color.New(color.Bold).SprintFunc()
	dim := color.New(color.Faint).SprintFunc()

	line := strings.Repeat("━", 55)
	fmt.Println(line)
	fmt.Printf("  %s sessions  │  Total %s  │  Avg %s\n",
		bold(fmt.Sprintf("%d", s.Count)),
		bold(model.NewDuration(durSecs(s.TotalDuration)).Human()),
		bold(model.NewDuration(durSecs(s.avgDuration())).Human()),
	)
	fmt.Printf("  Tools %-5d       │  Errors %s  │  Cache %.1f%%\n",
		s.TotalTools,
		formatErrors(s.TotalErrors, s.errorRate()),
		s.Tokens.CacheEfficiency(),
	)
	fmt.Println(line)

	// Per-session breakdown.
	fmt.Printf("\n  %s\n", bold("Sessions"))
	fmt.Printf("  %-10s %8s %6s %6s %8s\n",
		dim("ID"), dim("Duration"), dim("Tools"),
		dim("Err%"), dim("Tokens"))
	fmt.Printf("  %s\n", dim(strings.Repeat("─", 44)))

	sorted := make([]*model.SessionSpan, len(s.Sessions))
	copy(sorted, s.Sessions)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].StartTime.After(sorted[j].StartTime)
	})

	for _, sess := range sorted {
		fmt.Printf("  %-10s %8s %6d %5.1f%% %8s\n",
			sess.SessionID[:min(10, len(sess.SessionID))],
			sess.Duration.Human(),
			sess.TotalToolCalls(),
			sess.ErrorRate(),
			formatTokens(sess.Tokens.Total()),
		)
	}
	fmt.Println()
}

func (s *Summary) avgDuration() float64 {
	if s.Count == 0 {
		return 0
	}
	return s.TotalDuration / float64(s.Count)
}

func (s *Summary) errorRate() float64 {
	if s.TotalTools == 0 {
		return 0
	}
	return float64(s.TotalErrors) / float64(s.TotalTools) * 100
}

func formatErrors(count int, rate float64) string {
	if count == 0 {
		return color.GreenString("0")
	}
	return color.RedString("%d (%.1f%%)", count, rate)
}

func formatTokens(n uint64) string {
	switch {
	case n >= 1_000_000:
		return fmt.Sprintf("%.1fM", float64(n)/1_000_000)
	case n >= 1_000:
		return fmt.Sprintf("%.1fK", float64(n)/1_000)
	default:
		return fmt.Sprintf("%d", n)
	}
}

func durSecs(s float64) time.Duration {
	return time.Duration(s * float64(time.Second))
}
