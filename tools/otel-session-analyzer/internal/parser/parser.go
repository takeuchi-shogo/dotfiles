package parser

import (
	"bufio"
	"encoding/json"
	"os"
	"time"

	"github.com/takeuchishougo/osa/internal/category"
	"github.com/takeuchishougo/osa/internal/model"
)

// rawEvent represents a single line from the JSONL session log.
type rawEvent struct {
	Type      string    `json:"type"`
	SessionID string    `json:"sessionId"`
	Timestamp time.Time `json:"timestamp"`
	Message   *message  `json:"message,omitempty"`
}

type message struct {
	Role    string          `json:"role"`
	Content json.RawMessage `json:"content"`
	Usage   *usage          `json:"usage,omitempty"`
}

type usage struct {
	InputTokens              uint64 `json:"input_tokens"`
	OutputTokens             uint64 `json:"output_tokens"`
	CacheReadInputTokens     uint64 `json:"cache_read_input_tokens"`
	CacheCreationInputTokens uint64 `json:"cache_creation_input_tokens"`
}

type contentBlock struct {
	Type      string          `json:"type"`
	ID        string          `json:"id,omitempty"`
	Name      string          `json:"name,omitempty"`
	Input     json.RawMessage `json:"input,omitempty"`
	ToolUseID string          `json:"tool_use_id,omitempty"`
	IsError   bool            `json:"is_error,omitempty"`
	Content   json.RawMessage `json:"content,omitempty"`
	Text      string          `json:"text,omitempty"`
}

// ParseFile parses a JSONL session file into a SessionSpan.
func ParseFile(path string) (*model.SessionSpan, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	var events []rawEvent
	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 0, 1024*1024), 10*1024*1024)
	for scanner.Scan() {
		var ev rawEvent
		if err := json.Unmarshal(scanner.Bytes(), &ev); err != nil {
			continue
		}
		events = append(events, ev)
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}

	return buildSpans(events), nil
}

func buildSpans(events []rawEvent) *model.SessionSpan {
	var (
		sessionID     string
		sessionStart  time.Time
		sessionEnd    time.Time
		turns         []model.Turn
		currentTurn   *model.Turn
		turnIndex     int
		pendingTools  = make(map[string]*model.ToolCall)
		resolvedTools = make(map[string]*model.ToolCall)
		totalTokens   model.TokenUsage
	)

	for _, ev := range events {
		ts := ev.Timestamp
		if ts.IsZero() {
			continue
		}
		if sessionID == "" {
			sessionID = ev.SessionID
		}
		if sessionStart.IsZero() {
			sessionStart = ts
		}
		sessionEnd = ts

		switch ev.Type {
		case "user":
			if ev.Message == nil {
				continue
			}
			raw := ev.Message.Content
			blocks := parseContentBlocks(raw)

			// Resolve pending tool results.
			for i := range blocks {
				b := &blocks[i]
				if b.Type != "tool_result" {
					continue
				}
				tc, ok := pendingTools[b.ToolUseID]
				if !ok {
					continue
				}
				delete(pendingTools, b.ToolUseID)
				end := ts
				tc.EndTime = &end
				dur := model.NewDuration(end.Sub(tc.StartTime))
				tc.Duration = &dur
				tc.OutputSize = measureContent(b.Content)
				tc.IsError = b.IsError
				resolvedTools[b.ToolUseID] = tc
			}

			// New user turn if there's text content.
			// Content may be a JSON string or an array of blocks.
			if hasUserText(blocks) || isStringContent(raw) {
				if currentTurn != nil {
					closeTurn(currentTurn, ts)
					turns = append(turns, *currentTurn)
				}
				turnIndex++
				currentTurn = &model.Turn{
					Index:     turnIndex,
					StartTime: ts,
				}
			}

		case "assistant":
			if ev.Message == nil {
				continue
			}
			blocks := parseContentBlocks(ev.Message.Content)

			// Accumulate token usage.
			if u := ev.Message.Usage; u != nil {
				tok := model.TokenUsage{
					Input:         u.InputTokens,
					Output:        u.OutputTokens,
					CacheRead:     u.CacheReadInputTokens,
					CacheCreation: u.CacheCreationInputTokens,
				}
				totalTokens.Merge(tok)
				if currentTurn != nil {
					currentTurn.Tokens.Merge(tok)
				}
			}

			// Extract tool calls.
			for i := range blocks {
				b := &blocks[i]
				if b.Type != "tool_use" {
					continue
				}
				tc := model.ToolCall{
					ToolID:    b.ID,
					Name:      b.Name,
					Category:  category.Categorize(b.Name),
					InputSize: len(b.Input),
					StartTime: ts,
				}
				pendingTools[b.ID] = &tc
				if currentTurn != nil {
					currentTurn.ToolCalls = append(
						currentTurn.ToolCalls, tc,
					)
				}
			}
		}
	}

	// Close last turn.
	if currentTurn != nil {
		closeTurn(currentTurn, sessionEnd)
		turns = append(turns, *currentTurn)
	}

	// Sync resolved tool call data back into turn slices
	// (Go copies structs, so pointer updates don't propagate
	// to the copies stored in turns).
	for i := range turns {
		for j := range turns[i].ToolCalls {
			tc := &turns[i].ToolCalls[j]
			if resolved, ok := resolvedTools[tc.ToolID]; ok {
				tc.EndTime = resolved.EndTime
				tc.Duration = resolved.Duration
				tc.OutputSize = resolved.OutputSize
				tc.IsError = resolved.IsError
			}
		}
	}

	dur := model.NewDuration(sessionEnd.Sub(sessionStart))
	return &model.SessionSpan{
		SessionID: sessionID,
		StartTime: sessionStart,
		EndTime:   sessionEnd,
		Duration:  dur,
		Tokens:    totalTokens,
		Turns:     turns,
	}
}

func closeTurn(t *model.Turn, endTime time.Time) {
	t.EndTime = endTime
	t.Duration = model.NewDuration(endTime.Sub(t.StartTime))
}

func parseContentBlocks(raw json.RawMessage) []contentBlock {
	var blocks []contentBlock
	if err := json.Unmarshal(raw, &blocks); err != nil {
		return nil
	}
	return blocks
}

func hasUserText(blocks []contentBlock) bool {
	for i := range blocks {
		if blocks[i].Type == "text" && blocks[i].Text != "" {
			return true
		}
	}
	return false
}

func isStringContent(raw json.RawMessage) bool {
	if len(raw) == 0 {
		return false
	}
	var s string
	if err := json.Unmarshal(raw, &s); err == nil {
		return len(s) > 0
	}
	return false
}

func measureContent(raw json.RawMessage) int {
	// Try as string first.
	var s string
	if err := json.Unmarshal(raw, &s); err == nil {
		return len(s)
	}
	// Try as array of text blocks.
	var blocks []struct {
		Text string `json:"text"`
	}
	if err := json.Unmarshal(raw, &blocks); err == nil {
		n := 0
		for _, b := range blocks {
			n += len(b.Text)
		}
		return n
	}
	return len(raw)
}
