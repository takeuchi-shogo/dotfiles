package stats

import (
	"fmt"
	"sort"
	"strings"
	"time"

	"github.com/fatih/color"

	"github.com/takeuchishougo/osa/internal/model"
)

var (
	bold    = color.New(color.Bold).SprintFunc()
	dim     = color.New(color.Faint).SprintFunc()
	cRed    = color.New(color.FgRed).SprintFunc()
	cGreen  = color.New(color.FgGreen).SprintFunc()
	cYellow = color.New(color.FgYellow).SprintFunc()
	cCyan   = color.New(color.FgCyan).SprintFunc()
)

// Print outputs formatted session statistics to stdout.
func Print(s *model.SessionSpan) {
	line := strings.Repeat("━", 50)
	fmt.Println(line)
	fmt.Printf("  Session  %s  │  %s  │  %d turns\n",
		bold(s.SessionID[:min(8, len(s.SessionID))]),
		bold(s.Duration.Human()),
		len(s.Turns),
	)
	fmt.Printf("  Tools    %-4d         │  Errors  %s\n",
		s.TotalToolCalls(),
		formatErrors(s.TotalErrors(), s.ErrorRate()),
	)
	fmt.Println(line)

	printTokens(&s.Tokens)
	printToolStats(s)
	printCategoryStats(s)
	printSlowestTurns(s)
	fmt.Println()
}

func formatErrors(count int, rate float64) string {
	if count == 0 {
		return cGreen("0")
	}
	return cRed(fmt.Sprintf("%d (%.1f%%)", count, rate))
}

func printTokens(t *model.TokenUsage) {
	fmt.Printf("\n  %s\n", bold("Tokens"))
	fmt.Printf("  ├─ Input          %s\n", formatNum(t.Input))
	fmt.Printf("  ├─ Output         %s\n", formatNum(t.Output))
	fmt.Printf("  ├─ Cache read     %s", formatNum(t.CacheRead))
	if eff := t.CacheEfficiency(); eff > 0 {
		fmt.Printf("  %s", dim(fmt.Sprintf("(%.1f%% hit)", eff)))
	}
	fmt.Println()
	fmt.Printf("  └─ Cache create   %s\n", formatNum(t.CacheCreation))
}

func printToolStats(s *model.SessionSpan) {
	type toolStat struct {
		Name     string
		Count    int
		Errors   int
		TotalDur float64
	}

	m := make(map[string]*toolStat)
	for i := range s.Turns {
		for j := range s.Turns[i].ToolCalls {
			tc := &s.Turns[i].ToolCalls[j]
			st, ok := m[tc.Name]
			if !ok {
				st = &toolStat{Name: tc.Name}
				m[tc.Name] = st
			}
			st.Count++
			if tc.Duration != nil {
				st.TotalDur += tc.Duration.Seconds()
			}
			if tc.IsError {
				st.Errors++
			}
		}
	}

	if len(m) == 0 {
		return
	}

	stats := make([]*toolStat, 0, len(m))
	for _, v := range m {
		stats = append(stats, v)
	}
	sort.Slice(stats, func(i, j int) bool {
		return stats[i].Count > stats[j].Count
	})

	fmt.Printf("\n  %s\n", bold("Tool Calls"))
	fmt.Printf("  %-18s %5s %8s %10s %6s\n",
		dim("Tool"), dim("Count"), dim("Avg"), dim("Total"), dim("Err"))
	fmt.Printf("  %s\n", dim(strings.Repeat("─", 50)))

	for _, st := range stats {
		avg := 0.0
		if st.Count > 0 {
			avg = st.TotalDur / float64(st.Count)
		}
		errStr := ""
		if st.Errors > 0 {
			errStr = cRed(fmt.Sprintf("%d", st.Errors))
		}
		fmt.Printf("  %-18s %5d %7.1fs %9.1fs %6s\n",
			st.Name, st.Count, avg, st.TotalDur, errStr)
	}
}

func printCategoryStats(s *model.SessionSpan) {
	type catStat struct {
		Cat      string
		Count    int
		TotalDur float64
	}

	m := make(map[string]*catStat)
	for i := range s.Turns {
		for j := range s.Turns[i].ToolCalls {
			tc := &s.Turns[i].ToolCalls[j]
			st, ok := m[tc.Category]
			if !ok {
				st = &catStat{Cat: tc.Category}
				m[tc.Category] = st
			}
			st.Count++
			if tc.Duration != nil {
				st.TotalDur += tc.Duration.Seconds()
			}
		}
	}

	if len(m) == 0 {
		return
	}

	stats := make([]*catStat, 0, len(m))
	for _, v := range m {
		stats = append(stats, v)
	}
	sort.Slice(stats, func(i, j int) bool {
		return stats[i].TotalDur > stats[j].TotalDur
	})

	grandTotal := 0.0
	for _, st := range stats {
		grandTotal += st.TotalDur
	}

	fmt.Printf("\n  %s\n", bold("Categories"))
	fmt.Printf("  %-14s %5s %10s %6s\n",
		dim("Category"), dim("Count"), dim("Time"), dim("%"))
	fmt.Printf("  %s\n", dim(strings.Repeat("─", 38)))

	for _, st := range stats {
		pct := 0.0
		if grandTotal > 0 {
			pct = st.TotalDur / grandTotal * 100
		}
		dur := model.NewDuration(
			durFromSecs(st.TotalDur),
		)
		bar := categoryBar(pct)
		fmt.Printf("  %s %-12s %5d %10s %5.1f%%\n",
			bar, st.Cat, st.Count, dur.Human(), pct)
	}
}

func printSlowestTurns(s *model.SessionSpan) {
	if len(s.Turns) == 0 {
		return
	}

	sorted := make([]model.Turn, len(s.Turns))
	copy(sorted, s.Turns)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].Duration.Seconds() >
			sorted[j].Duration.Seconds()
	})

	limit := 5
	if len(sorted) < limit {
		limit = len(sorted)
	}

	fmt.Printf("\n  %s\n", bold("Slowest Turns"))
	for _, t := range sorted[:limit] {
		tools := summarizeTools(t.ToolCalls)
		fmt.Printf("  #%-3d %8s  %s\n",
			t.Index,
			cYellow(t.Duration.Human()),
			dim(tools),
		)
	}
}

func summarizeTools(calls []model.ToolCall) string {
	if len(calls) == 0 {
		return "(no tools)"
	}
	counts := make(map[string]int)
	order := make([]string, 0)
	for i := range calls {
		n := calls[i].Name
		if counts[n] == 0 {
			order = append(order, n)
		}
		counts[n]++
	}
	var parts []string
	for _, n := range order {
		if c := counts[n]; c > 1 {
			parts = append(parts, fmt.Sprintf("%s×%d", n, c))
		} else {
			parts = append(parts, n)
		}
	}
	return "[" + strings.Join(parts, ", ") + "]"
}

func categoryBar(pct float64) string {
	if pct >= 50 {
		return cRed("■")
	}
	if pct >= 20 {
		return cYellow("■")
	}
	return cCyan("■")
}

func formatNum(n uint64) string {
	if n == 0 {
		return "0"
	}
	s := fmt.Sprintf("%d", n)
	if len(s) <= 3 {
		return s
	}
	var parts []string
	for len(s) > 3 {
		parts = append([]string{s[len(s)-3:]}, parts...)
		s = s[:len(s)-3]
	}
	parts = append([]string{s}, parts...)
	return strings.Join(parts, ",")
}

func durFromSecs(s float64) time.Duration {
	return time.Duration(s * float64(time.Second))
}
