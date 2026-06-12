# Decommission Log

| 措置日 | 対象 | 理由 | 削除評価日 |
|---|---|---|---|
| 2026-06-01 | settings.json Stop hook の failure-clusterer.py | category==error 空振り(入力スキーマ不整合) | 2026-07-01 |
| 2026-06-01 | friction-weekly-digest.sh | friction-events 入力枯渇、learned-nudge.sh に置換 | 2026-07-01 |
| 2026-06-01 | launchd friction-aggregate(旧 run-friction-aggregate.sh 指向) | 同上 | 2026-07-01 |
| 休眠中 | autoevolve-runner.sh(cron 未登録で元から不動) | 触らず寝かせる | 2026-07-01 評価 |
| 2026-06-05 | settings.json Stop hook の session-trace-store.py + 本体 | /improve(retire 2026-05-03)で traces/ の reader 消失。hook 除去 + no-op 化 | 2026-07-05 |
| 2026-06-05 | contrastive-trace-analyzer.py | /improve 下流の孤児(reader 不在)。no-op 化 | 2026-07-05 |
| 2026-06-05 | cross-domain-mapper.py | /improve 下流の孤児(reader 不在)。no-op 化 | 2026-07-05 |
| 2026-06-05 | findings-to-autoevolve.py | /improve 下流の孤児(reader 不在)。no-op 化 | 2026-07-05 |
| 2026-06-05 | session-learner.py の strategy-outcomes 書き込み + _classify_* 3関数 | reader(contrastive-trace-analyzer)退役に伴いコード除去 | 除去済 |
| 2026-06-06 | データ実体: logs/observe(9.7M)/traces(4.4M)/strategy-outcomes.jsonl(990K) | reader 不在の死蔵データ。計15M 削除 | 削除済 |
| 2026-06-09 | scripts/policy/{agent-router,suggest-gemini,post-test-analysis}.py + scripts/tests/test_agent_router.py | Rust claude-hooks (user_prompt/pre_tool/post_bash) 移行済・settings.json 未登録の残骸。test_agent_router のロジックは user_prompt.rs mod tests に移植 (移植時 follow.?up drift を Rust に補填) | 即削除済 |
| 2026-06-10 | post_bash.rs の check_stagnation (Rust 側) | stagnation 二重実行解消 — settings.json で Rust post-bash と Python stagnation-detector.py が両方発火していた。Python は friction/consolidate/excessive-edit/alignment-tipping 含む多機能版のため Python に一本化 (Rust は 2/7 パターンの部分統合だった) | 除去済 |
| 2026-06-10 | scripts/policy/{file-pattern-router,tdd-guard,review-feedback-tracker,search-first-gate}.py + scripts/tests/test_review_feedback_tracker.py | Rust claude-hooks (pre_tool/post_bash) 移行済・settings.json 未登録の残骸 (per-hook 並列検証で deletion_safe 確認)。**flag**: review-feedback-tracker の Rust 版は部分統合 — partial 3値判定 / R-05 explicit 優先 / findings への outcome 書き戻し / redaction が欠落 (Python 未発火だったため稼働喪失はないが、復活には post_bash.rs への追補が必要)。file-pattern-router の「/security-scan 実行推奨」文言も Rust で脱落 | 即削除済 |
| 2026-06-10 | scripts/policy/protect-linter-config.py | Rust claude-hooks pre-edit (check_protect_linter) 移行済・settings.json 未登録の残骸。BLOCKED_FILES 25項目完全一致 + Rust は content も検査する上位互換を手動検証。enforcement guardrail のためユーザー承認の上で削除 (lint 設定保護は Rust が継続) | 即削除済 |
| 未配線 | scripts/policy/tool-scope-enforcer.py | settings.json 未登録 + Rust 統合なし = どこからも実行されない (削除すると機能消滅のため保留。再配線 or 削除の判断待ち) | 2026-07-10 評価 |
| 2026-06-12 | agents/autoevolve-core.md (34K) + meta-analyzer.md (14K) | /improve(retire 2026-05-03) の中核 agent。完全孤児 (実行コード参照はコメント/docstring のみ)・retire 後 30 日経過 | 即削除済 |
| 2026-06-12 | scripts/experimental/gh-skill-wrapper.sh + Taskfile skills:install-gh / skills:search-gh + scripts/migrations/ 3件 (add-origin-to-skills / add-platforms-to-skills / add-provenance-to-lock) | wrapper は gh skill v2.90+ 前提で実行不能 (手動 clone フォールバック運用が確定済)、migrations は適用完了済の one-shot。評価期間経過 | 即削除済 |
| 2026-06-12 | 死蔵 skill 8件を skillOverrides "off" で抑制: analyze-tacit-knowledge / autonomous / daily-report / morning-briefing / security-review / empirical-prompt-tuning / review-loop / implement-loop (ai-workflow-audit は PR #70 で抑制済) | 自動版・代替が稼働中 (sync-tacit-knowledge cron / nightly daily-report / launchd morning-briefing / security-reviewer agent 30日20回) or 0回ラッパー。使用ゼロは skill-executions.jsonl + 全期間 transcript の手動 slash (`<command-name>`) 照合の両経路で確認 — jsonl は agent の Skill tool 呼び出しのみ記録し手動 slash は記録しない計測盲点があるため transcript 照合を退役判定の必須手順とする。可逆 (SKILL.md 不編集) | 2026-07-12 評価 |
| 2026-06-12 | agents/_archived/ 10件 → docs/archive/agents/ へ移動 | `agents/` 配下はサブディレクトリもロード対象で Agent tool 一覧に出現=実質 live だった。同時整理: pre_tool.rs FILE_AGENT_ROUTES の archived 4 agent 行 / post_edit.rs + golden-check.py の golden-cleanup 提案 / eval-generator.py FM-008→debugger / regression-gate.py KNOWN_REVIEWERS / change-surface-advisor.py db_migration advice / validate-agents.sh 例外 / security-reviewer.md + review SKILL.md の triage-router 参照 | 移動済 (定義は docs/archive/agents/ に保全) |
