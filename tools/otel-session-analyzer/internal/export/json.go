package export

import (
	"encoding/json"
	"fmt"
	"io"
	"os"

	"github.com/takeuchishougo/osa/internal/model"
)

// JSON writes the session span as formatted JSON.
func JSON(s *model.SessionSpan, outPath string) error {
	var w io.Writer = os.Stdout
	if outPath != "" {
		f, err := os.Create(outPath)
		if err != nil {
			return err
		}
		defer f.Close()
		w = f
	}

	enc := json.NewEncoder(w)
	enc.SetIndent("", "  ")
	enc.SetEscapeHTML(false)
	if err := enc.Encode(s); err != nil {
		return err
	}

	if outPath != "" {
		fmt.Fprintf(os.Stderr, "Written to %s\n", outPath)
	}
	return nil
}
