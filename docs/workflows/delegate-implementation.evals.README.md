# delegate-implementation Workflow — 評価 ledger

`delegate-implementation` Workflow を実行するたびに、戻り値の `templateEval` を `delegate-implementation.evals.jsonl` に1行追記する。テンプレート (委譲メカニズム) の精度を時系列で追跡し、継続改善するための durable artifact。

## なぜ専用 ledger を分けるか

- `~/.claude/agent-memory/learnings/skill-executions.jsonl` は binary 結果のみで定性情報を持てない。
- `patterns.jsonl` は hook 自動・揮発的・git 管理外で用途が違う。
- `docs/resource-evaluations/` は外部知見 (記事・論文) の評価専用。
- → テンプレートの反復改善は人間レビュー前提の永続記録が要るので、git 管理下に独立 ledger を持つ。

## 1行スキーマ (jsonl)

```jsonc
{
  "timestamp": "ISO8601 (メインが付与 — Workflow 内では Date 禁止)",
  "template_id": "delegate-implementation",
  "iteration": 1,                // ledger の通し番号
  "task_count": 2,
  "result_summary": { "met": 2, "total": 2, "max_severity": "none" },
  "template_eval": { /* Phase 3 templateEval をそのまま (handoffClarity 等) */ },
  "next_fix": "次回適用する最小 diff (1テーマ)。なければ null"
}
```

## 改善トリガー (empirical-prompt-tuning の収束判定を流用)

- **安定**: 2連続の iteration で `sonnetStruggles` 空 + `handoffClarity≥4` + `wouldReuse:true`。→ テンプレートは触らない。
- **改善**: 上記未達なら、`suggestions` の最頻項目を **最小 diff で1テーマだけ** `delegate-implementation.js` に適用し、次 iteration で再計測する (複数同時修正は学習を汚すので禁止)。
- 方法論の出典: `empirical-prompt-tuning` skill (two-sided evaluation / bias-free read / 収束判定)。

## 注意 (PUBLIC dotfiles)

この ledger は dotfiles (PUBLIC) に commit される。`template_eval` / `next_fix` に **会社固有情報・機密を書かない**。記録は委譲メカニズムの一般的な品質に限定する。
