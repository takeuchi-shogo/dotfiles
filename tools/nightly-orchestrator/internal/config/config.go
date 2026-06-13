package config

import (
	"fmt"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Runtime Runtime `yaml:"runtime"`
	Jobs    []Job   `yaml:"jobs"`
}

type Runtime struct {
	MaxParallel int `yaml:"max_parallel"`
}

type Job struct {
	Name       string `yaml:"name"`
	Script     string `yaml:"script"`
	TimeoutSec int    `yaml:"timeout_sec"` // orchestrator 側のハング保険。0 = 無制限（bash 内 gtimeout に委譲）
	Retry      int    `yaml:"retry"`       // 即時リトライ回数（1 推奨）
}

func Parse(data []byte) (*Config, error) {
	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("yaml unmarshal: %w", err)
	}
	if cfg.Runtime.MaxParallel <= 0 {
		cfg.Runtime.MaxParallel = 3 // デフォルト
	}
	seen := make(map[string]bool, len(cfg.Jobs))
	for i, j := range cfg.Jobs {
		if j.Name == "" {
			return nil, fmt.Errorf("job[%d]: name is required", i)
		}
		if j.Script == "" {
			return nil, fmt.Errorf("job %q: script is required", j.Name)
		}
		if seen[j.Name] {
			return nil, fmt.Errorf("duplicate job name: %q", j.Name)
		}
		seen[j.Name] = true
	}
	return &cfg, nil
}
