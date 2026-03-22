package discovery

import (
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

// SessionFile represents a discovered JSONL session file.
type SessionFile struct {
	Path      string
	Project   string
	SessionID string
	ModTime   time.Time
}

// claudeProjectsDir returns ~/.claude/projects/.
func claudeProjectsDir() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".claude", "projects"), nil
}

// ListSessions discovers all JSONL session files.
// Results are sorted by modification time (newest first).
func ListSessions(project string) ([]SessionFile, error) {
	base, err := claudeProjectsDir()
	if err != nil {
		return nil, err
	}

	entries, err := os.ReadDir(base)
	if err != nil {
		return nil, err
	}

	var sessions []SessionFile
	for _, projDir := range entries {
		if !projDir.IsDir() {
			continue
		}
		projName := projDir.Name()
		if project != "" && !matchProject(projName, project) {
			continue
		}

		projPath := filepath.Join(base, projName)
		files, err := os.ReadDir(projPath)
		if err != nil {
			continue
		}
		for _, f := range files {
			if f.IsDir() || !strings.HasSuffix(f.Name(), ".jsonl") {
				continue
			}
			info, err := f.Info()
			if err != nil {
				continue
			}
			sid := strings.TrimSuffix(f.Name(), ".jsonl")
			sessions = append(sessions, SessionFile{
				Path:      filepath.Join(projPath, f.Name()),
				Project:   humanProject(projName),
				SessionID: sid,
				ModTime:   info.ModTime(),
			})
		}
	}

	sort.Slice(sessions, func(i, j int) bool {
		return sessions[i].ModTime.After(sessions[j].ModTime)
	})

	return sessions, nil
}

// matchProject does a case-insensitive substring match
// against the encoded project directory name.
func matchProject(dirName, query string) bool {
	lower := strings.ToLower(dirName)
	return strings.Contains(lower, strings.ToLower(query))
}

// humanProject converts "-Users-foo-bar-project" to "bar/project".
// It strips the leading "-Users-<username>-" prefix.
func humanProject(encoded string) string {
	parts := strings.Split(encoded, "-")
	// Skip empty first element, "Users", and username.
	if len(parts) > 3 {
		return strings.Join(parts[3:], "/")
	}
	return encoded
}
