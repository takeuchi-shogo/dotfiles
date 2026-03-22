package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "osa",
	Short: "OpenTelemetry Session Analyzer for Claude Code",
	Long:  "Analyze Claude Code JSONL session logs with structured spans, statistics, and OTLP export.",
}

// Execute runs the root command.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
