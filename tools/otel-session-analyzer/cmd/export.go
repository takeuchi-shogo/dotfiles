package cmd

import (
	"fmt"

	"github.com/spf13/cobra"

	"github.com/takeuchishougo/osa/internal/export"
	"github.com/takeuchishougo/osa/internal/parser"
)

var (
	exportOutput string
	exportOTLP   string
)

func init() {
	exportCmd.Flags().StringVarP(&exportOutput, "output", "o", "", "output JSON file (default: stdout)")
	exportCmd.Flags().StringVar(&exportOTLP, "otlp", "", "OTLP HTTP endpoint (e.g. http://localhost:4318)")
	rootCmd.AddCommand(exportCmd)
}

var exportCmd = &cobra.Command{
	Use:   "export <file>",
	Short: "Export session spans as JSON or to OTLP endpoint",
	Args:  cobra.ExactArgs(1),
	RunE:  runExport,
}

func runExport(_ *cobra.Command, args []string) error {
	session, err := parser.ParseFile(args[0])
	if err != nil {
		return fmt.Errorf("parsing %s: %w", args[0], err)
	}

	if exportOTLP != "" {
		return export.OTLP(session, exportOTLP)
	}

	return export.JSON(session, exportOutput)
}
