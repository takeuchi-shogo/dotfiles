package cmd

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/fatih/color"
	"github.com/spf13/cobra"

	"github.com/takeuchishougo/osa/internal/discovery"
)

var listProject string

func init() {
	listCmd.Flags().StringVarP(&listProject, "project", "p", "", "filter by project name")
	rootCmd.AddCommand(listCmd)
}

var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List discovered session files",
	RunE:  runList,
}

func runList(_ *cobra.Command, _ []string) error {
	files, err := discovery.ListSessions(listProject)
	if err != nil {
		return err
	}
	if len(files) == 0 {
		if jsonOutput {
			fmt.Println("[]")
			return nil
		}
		fmt.Println("No sessions found.")
		return nil
	}

	if jsonOutput {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		return enc.Encode(files)
	}

	dim := color.New(color.Faint).SprintFunc()
	bold := color.New(color.Bold).SprintFunc()

	fmt.Printf("  %-12s %-20s %s\n",
		dim("Session"), dim("Project"), dim("Modified"))
	for _, f := range files {
		fmt.Printf("  %-12s %-20s %s\n",
			bold(shortID(f.SessionID)),
			f.Project,
			f.ModTime.Format("2006-01-02 15:04"),
		)
	}
	fmt.Printf("\n  %d sessions found\n", len(files))
	return nil
}

func shortID(id string) string {
	if len(id) > 10 {
		return id[:10]
	}
	return id
}
