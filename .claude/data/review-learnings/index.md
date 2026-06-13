# review-learnings 索引

`/review` 時に、変更ファイルパスに応じた domain 別レビュー観点を code-reviewer プロンプトへ注入するための索引。
各 domain ファイルは過去のレビュー指摘 (`~/.claude/projects/.../memory/feedback_*.md` と `~/.claude/agent-memory/learnings/review-findings.jsonl`) から蒸留した個人レビュー観点。全 rule に出典コメント (`<!-- source: ... -->`) を付与。

> 注: AI 生成ドラフトをユーザーが「見る / 見ない / 部分的に見る」で線引きレビューし、2026-06-13 に全 rule 採用で確定済み。事業判断・違和感ベースの観点は意図的に除外している (本人に残す)。

## (a) domain マップ表

変更ファイルパス (第 1 階層 / 拡張子) → 適用する domain ファイル:

| 変更パターン | domain ファイル |
| --- | --- |
| `.config/claude/settings.json` | harness.md |
| `.config/claude/scripts/**` | harness.md |
| `.config/claude/hooks/**` / `tools/claude-hooks/**` | harness.md |
| `.config/claude/agents/**` | harness.md |
| `.config/claude/skills/**` | harness.md, docs.md |
| `*.zsh` / `*.sh` (zsh/bash script) | harness.md |
| `*.py` (harness script) | harness.md |
| `templates/claude-md/**` / `CLAUDE.md` / `AGENTS.md` | docs.md, harness.md |
| `docs/**/*.md` / `.config/claude/references/**` | docs.md |
| `*.tf` / `lefthook.yml` / `Taskfile.yml` / git workflow | harness.md (settings/script 系の観点を流用) |

未マップのパスはどの domain も注入しない (汎用 code-reviewer のみ)。

### 作成しなかった domain と理由

- **go.md**: Go コード固有のレビュー指摘がソースに存在しない (`feedback_language_choice.md` は「Go を選べ」という言語選択の話で、Go コードのレビュー観点ではない)。trace 可能な rule が 3 個未満のためパディング禁止ルールに従い未作成。Go コードを書くようになり実 finding が蓄積したら作成する。
- **typescript.md**: 同上。TS/JS 固有のレビュー指摘がソースにゼロ。未作成。

## (b) 出典内訳

- **作成ファイル**: harness.md (rule 17 件), docs.md (rule 9 件), index.md
- **採用ソース (feedback)**: 11 件 — settings_json_grep_first / worktree_review_symlink_stale / zsh_reserved_vars / lefthook_intent_to_add / dotfiles_worktree_pr_workflow / hidden_impact_analysis / language_choice / instruction_cost / claudemd_length / bad_example_pattern / memory_style
- **採用ソース (review-findings.jsonl)**: accepted/accept/partial の finding を蒸留。主に harness script (agent-invocation-logger / brevity-benchmark / harness-snapshot / webfetch-truncation-detector / skill-count-alert)、settings.json、reference md。outcome=`?` (未記録) や rejected/deferred (scope 外) は原則除外。
- **除外したソース (理由カテゴリ別)**:
  - absorb 運用ノウハウ (レビュー規則でない): absorb_already_deepdive / absorb_already_hallucination / absorb_architectural_arrogance / absorb_sonnet_imagination / absorb_thoroughness
  - Codex/Gemini/cmux 運用 (レビュー規則でない): codex_bash_tool_unreachable / codex_casual_use / codex_invocation_pattern / codex_reasoning / codex_searching_phase / cmux_claude_teams_overstated / cmux_events_launchctl / gemini_q1_opusplan_unverified / model_fable_classifier_outage / sonnet_cursor_underused / stall_proceed_with_evidence / explore_subagent_bash_limit / tool_call_parse_context
  - commit ワークフロー (レビュー観点でなく実行手順): commit_convention / use_commit_skill
  - レビュー進行の手順論 (観点でなくプロセス): review_readonly / review_quality_first / review_timing — これらは「レビューをどう進めるか」であり「変更をどう見るか」の domain rule ではないため domain ファイルには入れず、review SKILL 側の責務として除外
  - 入力安全・課金など review 対象外: quoted_text_instructions / max_plan_credit_safety / obsidian_vault_subfolder_write
