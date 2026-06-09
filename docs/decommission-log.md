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
| 未配線 | scripts/policy/tool-scope-enforcer.py | settings.json 未登録 + Rust 統合なし = どこからも実行されない (削除すると機能消滅のため保留。再配線 or 削除の判断待ち) | 2026-07-10 評価 |
