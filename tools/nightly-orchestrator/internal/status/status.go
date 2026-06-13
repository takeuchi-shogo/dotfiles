package status

import (
	"bufio"
	"encoding/json"
	"errors"
	"io/fs"
	"os"
)

type Record struct {
	TS          string            `json:"ts"`
	Task        string            `json:"task"`
	Status      string            `json:"status"` // "ok" | "fail"
	DurationSec int               `json:"duration_sec"`
	Report      string            `json:"report"`
	Detail      string            `json:"detail"`
	Metric      map[string]string `json:"metric"`
}

// ReadLatestByTask は JSONL を読み、task ごとに最後に現れたレコードを返す。
// ファイル不在は空マップ + nil error（全ジョブが gate skip された夜は正常）。
// malformed 行は morning-briefing と同様にスキップする。
func ReadLatestByTask(path string) (map[string]Record, error) {
	f, err := os.Open(path)
	if err != nil {
		if errors.Is(err, fs.ErrNotExist) {
			return map[string]Record{}, nil
		}
		return nil, err
	}
	defer f.Close()

	out := make(map[string]Record)
	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 0, 64*1024), 1024*1024) // detail が長い行に備える
	for sc.Scan() {
		line := sc.Bytes()
		if len(line) == 0 {
			continue
		}
		var r Record
		if err := json.Unmarshal(line, &r); err != nil {
			continue // malformed 行は無視（tolerant）
		}
		if r.Task == "" {
			continue
		}
		out[r.Task] = r // 後勝ち = 最新
	}
	if err := sc.Err(); err != nil {
		return nil, err
	}
	return out, nil
}
