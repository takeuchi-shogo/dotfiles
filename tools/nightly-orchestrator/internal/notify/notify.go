package notify

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"sort"
	"strings"
	"time"

	"github.com/takeuchishougo/nightly-orchestrator/internal/orchestrator"
)

type Payload struct {
	Content string  `json:"content"`
	Embeds  []Embed `json:"embeds"`
}

type Embed struct {
	Title       string `json:"title"`
	Description string `json:"description"`
	Color       int    `json:"color"`
	Timestamp   string `json:"timestamp"`
}

func (p Payload) failCount() int {
	n := 0
	for _, line := range strings.Split(p.Embeds[0].Description, "\n") {
		if strings.HasPrefix(line, "❌") {
			n++
		}
	}
	return n
}

// BuildPayload は Summary を 1 通の embed に変換する純粋関数（送信副作用なし）。
func BuildPayload(sum *orchestrator.Summary, date string) Payload {
	const green, red = 3066993, 15158332
	ts := time.Now().Format(time.RFC3339)

	if sum.Aborted {
		return Payload{
			Content: "",
			Embeds: []Embed{{
				Title:       fmt.Sprintf("⏸️ nightly %s: LOOP_DISABLED（全ジョブ skip）", date),
				Description: "circuit-breaker が有効なため夜間バッチを実行しませんでした。",
				Color:       green,
				Timestamp:   ts,
			}},
		}
	}

	names := make([]string, 0, len(sum.Results))
	for n := range sum.Results {
		names = append(names, n)
	}
	sort.Strings(names)

	var b strings.Builder
	failed := 0
	for _, n := range names {
		r := sum.Results[n]
		switch r.Status {
		case "ok":
			fmt.Fprintf(&b, "✅ %s\n", n)
		case "missing":
			fmt.Fprintf(&b, "➖ %s (skip)\n", n)
		default: // fail
			failed++
			msg := r.Record.Metric["msg"]
			fmt.Fprintf(&b, "❌ %s (%d 回試行) — %s\n", n, r.Attempts, msg)
		}
	}

	color := green
	content := ""
	title := fmt.Sprintf("✅ nightly %s: 全ジョブ正常", date)
	if failed > 0 {
		color = red
		content = "@here"
		title = fmt.Sprintf("❌ nightly %s: %d 件失敗", date, failed)
	}

	return Payload{
		Content: content,
		Embeds: []Embed{{
			Title:       title,
			Description: b.String(),
			Color:       color,
			Timestamp:   ts,
		}},
	}
}

// Send は payload を webhook に POST する。URL 空なら no-op（bash と同じく通知失敗で全体は壊さない）。
func Send(webhookURL string, p Payload) error {
	if webhookURL == "" {
		return nil
	}
	body, err := json.Marshal(p)
	if err != nil {
		return err
	}
	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Post(webhookURL, "application/json", bytes.NewReader(body))
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 && resp.StatusCode != 204 {
		return fmt.Errorf("discord webhook returned %d", resp.StatusCode)
	}
	return nil
}
