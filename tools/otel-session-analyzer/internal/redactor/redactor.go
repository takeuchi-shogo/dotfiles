package redactor

import "regexp"

var patterns = []*regexp.Regexp{
	regexp.MustCompile(`(?i)(api[_-]?key|token|secret)[=:]\s*['"]?[a-zA-Z0-9_\-]{20,}`),
	regexp.MustCompile(`AKIA[0-9A-Z]{16}`),
	regexp.MustCompile(`(?i)(password|passwd|pwd)[=:]\s*['"]?\S{8,}`),
	regexp.MustCompile(`(?i)Bearer\s+[a-zA-Z0-9_\-.]+`),
	regexp.MustCompile(`-----BEGIN [A-Z ]+ KEY-----`),
}

// Redact replaces sensitive patterns with [REDACTED].
func Redact(s string) string {
	for _, p := range patterns {
		s = p.ReplaceAllString(s, "[REDACTED]")
	}
	return s
}
