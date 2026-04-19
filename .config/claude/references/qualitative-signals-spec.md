# Qualitative Signals Spec

> eval 実行で記録する定性シグナル (ambiguity / retry / failure_reason) のスキーマ定義。
> 出典: mizchi/empirical-prompt-tuning (`SKILL.md` Dual-Axis Evaluation)
> Reward Hacking 対策として tool_uses のような定量指標と必ず併用する (arXiv:2403.03023)。

## 目的

プロンプト改善ループにおいて「構造的欠陥の顕在化」に必要な定性情報を構造化ログとして残す。
単一の pass/fail だけでは検出できない以下のシグナルを捕捉する:

- **ambiguity**: プロンプトの指示に複数解釈があり、エージェントが判断に迷った箇所
- **retry**: 同じサブタスクで複数回 tool を呼び直した箇所 (= 仕様不明瞭)
- **failure_reason**: 失敗時の根本原因 (プロンプト不備 / モデル不備 / 環境不備)

## 記録先

`~/.claude/agent-memory/qualitative-signals/qualitative_signals.jsonl`

- 1 eval run = 1 行の JSONL
- 90 日で自動ローテーション (session-trace-store と同じ retention)
- 機密情報は redactor で除去してから書き込む

## スキーマ

```json
{
  "timestamp": "2026-04-19T12:00:00Z",
  "session_id": "abc123def456",
  "skill_name": "example-skill",
  "eval_id": 0,
  "iteration": 1,
  "evaluator_model_version": "claude-opus-4-7",
  "signals": {
    "ambiguity": [
      {
        "location": "step 3",
        "description": "'適切なフォーマット' が曖昧。JSON か Markdown か判断不能",
        "severity": "high|medium|low"
      }
    ],
    "retry": [
      {
        "tool": "Grep",
        "count": 3,
        "reason": "初回 pattern がマッチせず、2 回修正"
      }
    ],
    "failure_reason": {
      "category": "prompt_unclear|model_limitation|env_issue|none",
      "detail": "プロンプトで出力形式が指定されていなかった"
    }
  },
  "tool_uses": {
    "total_count": 12,
    "by_tool": {"Read": 5, "Grep": 3, "Edit": 4},
    "precision": 0.75
  }
}
```

### Field 定義

| Field | Type | Required | 説明 |
|-------|------|----------|------|
| timestamp | ISO8601 str | ✓ | 記録時刻 (UTC) |
| session_id | str | ✓ | セッション識別子 (先頭 12 文字) |
| skill_name | str | ✓ | eval 対象の skill 名 |
| eval_id | int | ✓ | evals.json の eval_id |
| iteration | int | ✓ | iteration 番号 (1-indexed) |
| evaluator_model_version | str | ✓ | 評価に使った LLM モデル ID (drift 検出用) |
| signals.ambiguity | list | ✓ | 空配列可。曖昧さが無ければ `[]` |
| signals.retry | list | ✓ | 空配列可 |
| signals.failure_reason.category | enum | ✓ | `none` = 成功 |
| tool_uses.total_count | int | ✓ | session-trace-store の risk_levels 長と一致 |
| tool_uses.precision | float | ✗ | `useful_calls / total_count` (0.0-1.0)。不明なら省略 |

### severity 判定基準

- **high**: 実装の根幹に関わる曖昧さ (インターフェース未定義、仕様矛盾)
- **medium**: 実装方針に影響する曖昧さ (命名規約、フォーマット)
- **low**: スタイル的な曖昧さ (コメント量、改行)

### failure_reason.category

| value | 説明 | アクション |
|-------|------|-----------|
| `prompt_unclear` | プロンプト自体が不明瞭 | **改善対象**。改善提案に include |
| `model_limitation` | モデル能力の限界 | 改善対象外 (モデル変更で解消) |
| `env_issue` | 環境・データの問題 | 改善対象外 (env 修正) |
| `none` | 成功した eval | — |

## 記録タイミング

1. **run_eval.sh**: 各 eval 実行完了直後、grader subagent が `signals` と `tool_uses` を算出
2. **aggregate.py**: iteration_dir 単位で集計し、`benchmark.json` に `qualitative_summary` を埋め込む
3. **Convergence Check**: `/improve` の Phase 1 で直近 N iteration の signals 変化を確認

## Convergence 判定での使用

`empirical-prompt-tuning` の収束条件を踏襲する:

1. **新規 ambiguity がゼロ** (2 iteration 連続)
2. **定量指標が ±10-15% で安定** (tool_uses.total_count, precision)
3. **holdout シナリオで再現性確認**

上記を全て満たすと収束 (改善ループ停止)。

## Anti-Patterns

| NG | 理由 |
|----|------|
| tool_uses.total_count のみで評価 | Reward Hacking で tool 呼び出しを人為的に減らす方向に収束 (arXiv:2403.03023) |
| ambiguity 空配列を「問題なし」と解釈 | 実際は「検出漏れ」かもしれない。3 iteration 連続で `[]` なら検出器の校正を疑う |
| failure_reason を自己採点させる | Self-preference Bias。必ず異モデルの grader に判定させる |
| 同一 evaluator_model_version で N 回評価し続ける | Evaluator Drift 検出不能。四半期に 1 回はモデル version を明示的に変える |

## 関連

- `.config/claude/skills/skill-creator/scripts/aggregate.py` — 集計実装
- `.config/claude/skills/skill-creator/instructions/testing-evaluation.md` — 記録フロー
- `.config/claude/skills/improve/SKILL.md` — Convergence Check
- `.config/claude/references/improve-policy.md` — Rule 47 (holdout) / Rule 48 (evaluator drift)
