package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/spf13/cobra"

	"github.com/takeuchishougo/osa/internal/batch"
	"github.com/takeuchishougo/osa/internal/discovery"
	"github.com/takeuchishougo/osa/internal/model"
	"github.com/takeuchishougo/osa/internal/parser"
	"github.com/takeuchishougo/osa/internal/stats"
)

var (
	analyzeProject string
	analyzeLast    int
	analyzeSince   string
)

func init() {
	analyzeCmd.Flags().StringVarP(&analyzeProject, "project", "p", "", "filter by project name")
	analyzeCmd.Flags().IntVarP(&analyzeLast, "last", "n", 0, "analyze last N sessions")
	analyzeCmd.Flags().StringVar(&analyzeSince, "since", "", "analyze sessions after date (YYYY-MM-DD)")
	rootCmd.AddCommand(analyzeCmd)
}

var analyzeCmd = &cobra.Command{
	Use:   "analyze [file...]",
	Short: "Analyze session logs and print statistics",
	Long:  "Parse JSONL session files and display tool call statistics, token usage, and bottleneck analysis.",
	RunE:  runAnalyze,
}

func runAnalyze(cmd *cobra.Command, args []string) error {
	sessions, err := resolveSessions(args)
	if err != nil {
		return err
	}
	if len(sessions) == 0 {
		return fmt.Errorf("no sessions found\nHint: run 'osa list' to check available sessions")
	}

	if jsonOutput {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		return enc.Encode(sessions)
	}

	if len(sessions) == 1 {
		stats.Print(sessions[0])
		return nil
	}

	// Batch mode: print individual + summary.
	summary := batch.Aggregate(sessions)
	summary.Print()
	return nil
}

func resolveSessions(args []string) ([]*model.SessionSpan, error) {
	// Direct file arguments.
	if len(args) > 0 {
		var sessions []*model.SessionSpan
		for _, path := range args {
			s, err := parser.ParseFile(path)
			if err != nil {
				fmt.Fprintf(os.Stderr, "Warning: skipping %s: %v\n", path, err)
				continue
			}
			sessions = append(sessions, s)
		}
		return sessions, nil
	}

	// Discovery mode.
	files, err := discovery.ListSessions(analyzeProject)
	if err != nil {
		return nil, fmt.Errorf("discovering sessions: %w", err)
	}

	// Apply filters.
	if analyzeSince != "" {
		since, err := time.Parse("2006-01-02", analyzeSince)
		if err != nil {
			return nil, fmt.Errorf("invalid --since date: %w", err)
		}
		var filtered []discovery.SessionFile
		for _, f := range files {
			if f.ModTime.After(since) {
				filtered = append(filtered, f)
			}
		}
		files = filtered
	}

	if analyzeLast > 0 && len(files) > analyzeLast {
		files = files[:analyzeLast]
	}

	// Default: last 1 if no filters specified.
	if analyzeLast == 0 && analyzeSince == "" && len(files) > 0 {
		files = files[:1]
	}

	var sessions []*model.SessionSpan
	for _, f := range files {
		s, err := parser.ParseFile(f.Path)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Warning: skipping %s: %v\n", f.Path, err)
			continue
		}
		s.Project = f.Project
		sessions = append(sessions, s)
	}
	return sessions, nil
}
