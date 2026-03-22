package export

import (
	"bytes"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/takeuchishougo/osa/internal/model"
)

// otlpPayload represents a minimal OTLP JSON trace export request.
type otlpPayload struct {
	ResourceSpans []resourceSpan `json:"resourceSpans"`
}

type resourceSpan struct {
	Resource   otlpResource `json:"resource"`
	ScopeSpans []scopeSpan  `json:"scopeSpans"`
}

type otlpResource struct {
	Attributes []otlpKV `json:"attributes"`
}

type scopeSpan struct {
	Scope otlpScope  `json:"scope"`
	Spans []otlpSpan `json:"spans"`
}

type otlpScope struct {
	Name string `json:"name"`
}

type otlpSpan struct {
	TraceID           string      `json:"traceId"`
	SpanID            string      `json:"spanId"`
	ParentSpanID      string      `json:"parentSpanId,omitempty"`
	Name              string      `json:"name"`
	Kind              int         `json:"kind"`
	StartTimeUnixNano string      `json:"startTimeUnixNano"`
	EndTimeUnixNano   string      `json:"endTimeUnixNano"`
	Attributes        []otlpKV    `json:"attributes,omitempty"`
	Status            *otlpStatus `json:"status,omitempty"`
}

type otlpKV struct {
	Key   string    `json:"key"`
	Value otlpValue `json:"value"`
}

type otlpValue struct {
	StringValue *string `json:"stringValue,omitempty"`
	IntValue    *string `json:"intValue,omitempty"`
}

type otlpStatus struct {
	Code int `json:"code"`
}

func strVal(s string) otlpValue {
	return otlpValue{StringValue: &s}
}

func intVal(n int64) otlpValue {
	s := fmt.Sprintf("%d", n)
	return otlpValue{IntValue: &s}
}

func tsNano(t time.Time) string {
	return fmt.Sprintf("%d", t.UnixNano())
}

func newTraceID() string {
	b := make([]byte, 16)
	_, _ = rand.Read(b)
	return hex.EncodeToString(b)
}

func newSpanID() string {
	b := make([]byte, 8)
	_, _ = rand.Read(b)
	return hex.EncodeToString(b)
}

// OTLP exports session spans to an OTLP HTTP endpoint.
func OTLP(s *model.SessionSpan, endpoint string) error {
	traceID := newTraceID()
	sessionSpanID := newSpanID()

	var spans []otlpSpan

	// Session span.
	spans = append(spans, otlpSpan{
		TraceID:           traceID,
		SpanID:            sessionSpanID,
		Name:              fmt.Sprintf("session %s", shortID(s.SessionID)),
		Kind:              1,
		StartTimeUnixNano: tsNano(s.StartTime),
		EndTimeUnixNano:   tsNano(s.EndTime),
		Attributes: []otlpKV{
			{Key: "session.id", Value: strVal(s.SessionID)},
			{Key: "session.turns", Value: intVal(int64(len(s.Turns)))},
			{Key: "session.tool_calls", Value: intVal(int64(s.TotalToolCalls()))},
			{Key: "tokens.input", Value: intVal(int64(s.Tokens.Input))},
			{Key: "tokens.output", Value: intVal(int64(s.Tokens.Output))},
			{Key: "tokens.cache_read", Value: intVal(int64(s.Tokens.CacheRead))},
		},
	})

	// Turn + tool call spans.
	for i := range s.Turns {
		turn := &s.Turns[i]
		turnSpanID := newSpanID()
		spans = append(spans, otlpSpan{
			TraceID:           traceID,
			SpanID:            turnSpanID,
			ParentSpanID:      sessionSpanID,
			Name:              fmt.Sprintf("turn %d", turn.Index),
			Kind:              1,
			StartTimeUnixNano: tsNano(turn.StartTime),
			EndTimeUnixNano:   tsNano(turn.EndTime),
			Attributes: []otlpKV{
				{Key: "turn.index", Value: intVal(int64(turn.Index))},
				{Key: "turn.tool_count", Value: intVal(int64(len(turn.ToolCalls)))},
				{Key: "turn.input_tokens", Value: intVal(int64(turn.Tokens.Input))},
				{Key: "turn.output_tokens", Value: intVal(int64(turn.Tokens.Output))},
			},
		})

		for j := range turn.ToolCalls {
			tc := &turn.ToolCalls[j]
			endTime := turn.EndTime
			if tc.EndTime != nil {
				endTime = *tc.EndTime
			}
			toolSpan := otlpSpan{
				TraceID:           traceID,
				SpanID:            newSpanID(),
				ParentSpanID:      turnSpanID,
				Name:              tc.Name,
				Kind:              3, // CLIENT
				StartTimeUnixNano: tsNano(tc.StartTime),
				EndTimeUnixNano:   tsNano(endTime),
				Attributes: []otlpKV{
					{Key: "tool.name", Value: strVal(tc.Name)},
					{Key: "tool.category", Value: strVal(tc.Category)},
					{Key: "tool.input_size", Value: intVal(int64(tc.InputSize))},
					{Key: "tool.output_size", Value: intVal(int64(tc.OutputSize))},
				},
			}
			if tc.IsError {
				toolSpan.Status = &otlpStatus{Code: 2}
			}
			spans = append(spans, toolSpan)
		}
	}

	payload := otlpPayload{
		ResourceSpans: []resourceSpan{{
			Resource: otlpResource{
				Attributes: []otlpKV{
					{Key: "service.name", Value: strVal("claude-code")},
				},
			},
			ScopeSpans: []scopeSpan{{
				Scope: otlpScope{Name: "osa"},
				Spans: spans,
			}},
		}},
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal OTLP payload: %w", err)
	}

	url := strings.TrimRight(endpoint, "/") + "/v1/traces"
	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Post(url, "application/json", bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("POST %s: %w", url, err)
	}
	defer func() {
		_, _ = io.Copy(io.Discard, resp.Body)
		resp.Body.Close()
	}()

	if resp.StatusCode >= 300 {
		errBody, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("OTLP export failed: %s: %s", resp.Status, errBody)
	}

	fmt.Printf("Exported %d spans to %s\n", len(spans), endpoint)
	return nil
}

func shortID(id string) string {
	if len(id) > 8 {
		return id[:8]
	}
	return id
}
