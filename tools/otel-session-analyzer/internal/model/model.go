package model

import (
	"encoding/json"
	"fmt"
	"time"
)

type SessionSpan struct {
	SessionID string     `json:"session_id"`
	Project   string     `json:"project,omitempty"`
	StartTime time.Time  `json:"start_time"`
	EndTime   time.Time  `json:"end_time"`
	Duration  Duration   `json:"duration"`
	Tokens    TokenUsage `json:"tokens"`
	Turns     []Turn     `json:"turns"`
}

func (s *SessionSpan) TotalToolCalls() int {
	n := 0
	for i := range s.Turns {
		n += len(s.Turns[i].ToolCalls)
	}
	return n
}

func (s *SessionSpan) TotalErrors() int {
	n := 0
	for i := range s.Turns {
		for j := range s.Turns[i].ToolCalls {
			if s.Turns[i].ToolCalls[j].IsError {
				n++
			}
		}
	}
	return n
}

func (s *SessionSpan) ErrorRate() float64 {
	total := s.TotalToolCalls()
	if total == 0 {
		return 0
	}
	return float64(s.TotalErrors()) / float64(total) * 100
}

type Turn struct {
	Index     int        `json:"index"`
	StartTime time.Time  `json:"start_time"`
	EndTime   time.Time  `json:"end_time"`
	Duration  Duration   `json:"duration"`
	Tokens    TokenUsage `json:"tokens"`
	ToolCalls []ToolCall `json:"tool_calls"`
}

type ToolCall struct {
	ToolID     string     `json:"tool_id"`
	Name       string     `json:"name"`
	Category   string     `json:"category"`
	InputSize  int        `json:"input_size"`
	OutputSize int        `json:"output_size"`
	IsError    bool       `json:"is_error"`
	StartTime  time.Time  `json:"start_time"`
	EndTime    *time.Time `json:"end_time,omitempty"`
	Duration   *Duration  `json:"duration,omitempty"`
}

type TokenUsage struct {
	Input         uint64 `json:"input"`
	Output        uint64 `json:"output"`
	CacheRead     uint64 `json:"cache_read"`
	CacheCreation uint64 `json:"cache_creation"`
}

func (t *TokenUsage) Total() uint64 {
	return t.Input + t.Output + t.CacheRead + t.CacheCreation
}

func (t *TokenUsage) CacheEfficiency() float64 {
	total := t.Total()
	if total == 0 {
		return 0
	}
	return float64(t.CacheRead) / float64(total) * 100
}

func (t *TokenUsage) Merge(other TokenUsage) {
	t.Input += other.Input
	t.Output += other.Output
	t.CacheRead += other.CacheRead
	t.CacheCreation += other.CacheCreation
}

// Duration wraps time.Duration with human-friendly JSON serialization.
type Duration struct {
	time.Duration
}

func NewDuration(d time.Duration) Duration {
	return Duration{d}
}

func (d Duration) MarshalJSON() ([]byte, error) {
	return json.Marshal(d.Seconds())
}

func (d *Duration) UnmarshalJSON(b []byte) error {
	var secs float64
	if err := json.Unmarshal(b, &secs); err != nil {
		return err
	}
	d.Duration = time.Duration(secs * float64(time.Second))
	return nil
}

func (d Duration) Human() string {
	s := d.Seconds()
	switch {
	case s < 60:
		return fmt.Sprintf("%.1fs", s)
	case s < 3600:
		m := int(s) / 60
		sec := int(s) % 60
		return fmt.Sprintf("%dm%ds", m, sec)
	default:
		h := int(s) / 3600
		m := (int(s) % 3600) / 60
		return fmt.Sprintf("%dh%dm", h, m)
	}
}
