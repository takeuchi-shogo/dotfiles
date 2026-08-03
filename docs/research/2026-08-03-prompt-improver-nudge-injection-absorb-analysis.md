---
date: 2026-08-03
source: https://github.com/severity1/claude-code-prompt-improver
source_type: repository
family: none (閾値未達を明示判断)
status: planned
adopted: 6
---

## Source Summary

- リポジトリ: `severity1/claude-code-prompt-improver` v0.6.1、非 .git ファイル 32 個・約 5295 行。初コミット 2025-10-18、直近 2026-06-03
- 主張: プロンプト改善とは書き換えではなく「プロンプト→出力の経路全体」を整えること。UserPromptSubmit / PreToolUse / SubagentStart の各 hook タイミングで文脈を注入し、手戻り (correction round-trip) を減らす。単一 Python エンジン (`engine.py`) が JSON 宣言ルール (nudge) をディスパッチし、新 capability は JSON 1 ファイル追加で足せる
- 前提: Claude Code 2.0.22+ (AskUserQuestion 依存)、Python 標準ライブラリのみ、plugin 配布前提
- 定量エビデンス: README/CHANGELOG は「v0.4.0 で 31% トークン削減 (~275→~189 tokens/prompt)」を主張するが、リポジトリ内に実測コードはない。唯一 `tests/test_integration.py:114-138` の `test_token_overhead` が `len(fragment)//4 < 250` という粗い文字数ヒューリスティックを assert するのみで、31% も 189 tokens も検証していない。設計原則側の根拠も「見逃し=手戻り1周 / 誤発火=数トークン」という非対称性コスト論で、データではなく設計者の主張

verbatim 引用 (原文のまま、英語のまま載せる):

1. `"Fire wide, self-cancel cheap - a missed nudge costs a full correction loop, a false fire costs a few tokens Claude ignores. That asymmetry justifies high-recall gates, so every nudge leads with a condition ("If this is X... if not, ignore") and dismisses itself when it does not fit."` (README.md:204)
2. `"Audience rule - hook output is read by a specific audience: SubagentStart text is read by the subagent (how it should behave), UserPromptSubmit/PreToolUse text by the main agent. Never inject author-side or parent-side advice where it cannot be acted on."` (CLAUDE.md, Authoring rules)
3. `"Timing rule - PreToolUse additionalContext lands next to the tool result, read on the next model request. For EnterPlanMode that context persists for the whole plan-mode session... An ExitPlanMode nudge would land after the plan is already presented (too late), and the engine only emits inject_context, not permissionDecision gating, so it could not block either."` (CLAUDE.md, Authoring rules)

## Phase 1.5: Saturation Gate — PASS (新分野扱い)

family taxonomy 照合結果 (`references/topic-family-saturation.md`):

| Family | 必要 hit 数 | 実 hit | 判定 |
|---|---|---|---|
| `harness-engineering` | 3+ (`harness`/`hook`/`scaffold`/`agent platform`/`harness everything`) | 1 (`hook` のみ。repo 内に harness/scaffold の語なし) | 不成立 |
| `claude-code-tips` | 2+ | 0 | 不成立 |
| `skill-graphs` | 2+ | 1 (`skill` のみ) | 不成立 |
| `obsidian-second-brain` | 3+ | 0 | 不成立 |

閾値未達を明示判断として記録 (silently に family なし扱いにしない)。先例: `2026-07-31-handbook-md-instruction-following-absorb-analysis.md` も `harness` 1 hit のみで PASS 判定。Step 7 Stale-Plan Audit は N=0 のため skip。

## Phase 2 + 2.5: 判定テーブル (Codex 批評で 6 件修正済み)

Gap/Partial/N-A 表 (最終判定):

| # | 手法 | Pass2 初期判定 | 最終判定 | 根拠 (file:line) |
|---|---|---|---|---|
| 14 | hook token budget guard | Partial | **Broken (実バグ)** | `settings.json` に `measure-instruction-budget` 0 hit。実行すると `hook_injected: 0 tokens` — glob 先が `~/.claude/logs/session-*.jsonl` (実在 0 件) なのに Rust hook は `agent-memory/current-session.jsonl` に書く (`tools/claude-hooks/src/events.rs:154`) |
| 13 | plan mode nudge | Partial | **Broken (orphan)** | `scripts/policy/plan-implement-bridge.py` の docstring は `Triggered by: hooks.PostToolUse (Edit\|Write)` と宣言するが `settings.json` に 0 hit |
| 5 | self-cancel 注入文 | Gap | **Partial** | 「全 hook が断定形」は誤り。`tools/claude-hooks/src/post_edit.rs:357` に `この警告は情報提供であり、修正不要です。` が既存。欠けているのは router 系のみ (`user_prompt.rs:94` の `[Agent Router]`、`pre_tool.rs:435` の `[Suggest-Gemini]` は検出を事実として述べ推奨するだけ) |
| 1 | 宣言的エンジン + JSON nudge registry | N/A (ADR-0006 が根拠) | **N/A (根拠差し替え)** | `docs/adr/0006-hook-philosophy.md:43` の Semantic Advisory は「false positive が避けられない warn hook」を明示的に許容しており、JSON エンジン棄却の根拠にならない。正しい理由は「個人 harness で generic dispatcher + schema validation + 観測を新設する費用に見合う実測需要がない」。なお `pre_tool.rs:229` の `load_project_overrides()` が `.claude/file-pattern-routes.json` を読む限定的な宣言拡張点は既に存在する |
| 3 | progressive disclosure (hook→skill lazy load) | Partial (hook 導線なし) | **Partial (根拠訂正)** | `scripts/runtime/skill-suggest.py` は `settings.json` に配線済みで、編集パスから条件付き・セッション一回限りで skill を提案する (`skill-suggest.py:92`)。「hook 層に条件付き skill 導線なし」は誤り。ただし提案止まりで起動はしない |
| 10 | subagent dispatch / context isolation | Already | **Partial** | 文書規約は強い (`references/subagent-delegation-guide.md:246`, `:573`)。ただし SubagentStart の runtime 注入は 0 |
| 12 | audience rule / timing rule | Gap | **Gap (P1)** | hook event ごとの読者・到達時点・持続性を規約化した表は不在。ただし SubagentStart 自体が未使用なので P0 の機能欠落ではなく P1 の設計規約 |
| 2 | UserPromptSubmit prompt evaluation | Partial | **Partial** | 「曖昧なまま実装しない」は `.config/claude/CLAUDE.md:45` の instruction のみ。毎ターン距離ゼロで届く注入ではない |
| 4 | bypass prefix | Gap (低) | **Gap (低・保留)** | UserPromptSubmit hook を一時停止する手段なし。#2 採用時のみ必要。なお `settings.json:98` の `--no-verify`/`-n` deny は安全制約であり、記事の「nudge をユーザーが明示回避する prefix」とは層が違うので混同しない |
| 8 | directory authoritative / event validation | N/A | **N/A** | `references/hook-failure-policy.md` が「event の権威ソースは settings.json の hooks ブロック」と正反対を明記 |
| 9 | allowlist / no eval no importlib | N/A | **N/A** | ルールエンジン不在ゆえ守る対象がない。関連するが別物として `scripts/policy/skill-security-scan.py:28-29` が third-party skill の `eval()`/`exec()` を CRITICAL 検出する |
| 15 | fail-safe exit 0 | Already | **Already (behavior) / Gap (test)** | `scripts/lib/hook_utils.py:229-249` の fail-open + `tools/claude-hooks/src/main.rs:9` の raw passthrough で behavior は実装済み。ただし異常系 (malformed JSON / 欠損ペイロード) を直接検証するテストは `scripts/tests/` に 0 件 |
| 6 | priority merge / fragment isolation | Partial | **Already** | `tools/claude-hooks/src/pre_tool.rs:356-375` で 3 チェックが互いを止めずに `\n\n` join。priority フィールドを持つ宣言ルール群ではないが機能同等 |
| 7 | append_when / conditional injection | Partial | **Already** | `pre_tool.rs:32-46` の `check_timeout_clamp()` が条件付き追記。加えて CLAUDE.md の `<important if="...">` がプラットフォームネイティブ機構として同等 |
| 11 | AskUserQuestion grounded options | exists | **Already (強化不要)** | `skills/interviewing-issues/SKILL.md:55` (3-7 問)、`references/methodology-sdd-bdd.md:72`、`skills/grill-interview/SKILL.md:53-54` (AI 推奨回答を添える / コードベースで答えられるなら先に調べる) |

## Phase 2.5 の記録 (Gemini degraded)

- Gemini は `IneligibleTierError` で sunset のため Codex 単独 = degraded。周辺知識補完 (他プロジェクトの採用事例・記事が言及しない制約・より新しい代替手法) は未取得
- 経路: `codex exec --skip-git-repo-check -m gpt-5.6-terra --sandbox read-only --config model_reasoning_effort="xhigh"`、timeout 580s 以内に完了
- Codex verdict の verbatim 抜粋:
  - `結論：#14 と #13 は「Gap」より **既存実装の未配線バグ**として扱うべきです。#5 は完全な Gap ではなく Partial、#1 の N/A 根拠は ADR の読み違いです。`
  - `**#1 declarative engine — N/A は維持可能だが、ADR-0006 を根拠にするのは誤り。** ADR は semantic advisory を明示的に許容しています。（略）N/A にするなら理由は「個人 harness で generic dispatcher・schema validation・観測を新設する費用に見合う実測需要がない」です。ADR を盾にした棄却にはしない方がよいです。`
  - `優先順位は **(1) #14 の計測器を修理または撤去、(2) #13 の orphan を配線か撤去、(3) UserPromptSubmit の false-positive / 採用率 / correction round-trip を測る eval、(4) audience/timing 表と例外 fixture、(5) router のみ self-cancel 文面調整** です。JSON engine、global bypass prefix、EnterPlanMode hook は、この計測基盤なしには後回しでよいです。`
- Codex の指摘はすべて Opus が実ファイルで裏取りしてから採用した (grep -c 0 hit / スクリプト実走 / events.rs:154 / post_edit.rs:357 / ADR-0006:43 の原文確認)

## 履歴照合: #14/#13 の orphan は 3 度目の検出

- `docs/plans/completed/2026-04-23-skill-graphs-2.0-plan.md:88` — 別セッションの harness 変更が両 hook を settings.json から削除、ユーザーに escalation 済み (2026-04-23)。本プランの範囲外として送られた
- `docs/research/2026-06-07-karpathy-147k-claudemd-absorb-analysis.md:60` — BL-3 として再検出、「wire (weekly cron) or retire。先に BL-2 修正で数値を信頼可能に」と提案 (2026-06-07)
- 2026-08-03 (今回) — 依然 orphan。BL-2 (`~/.claude/references/` 非存在) の方は修正済み (`get_references_dir()` 使用、167 files / 186778 tokens を計測) だが BL-3 だけが 2 回見送られた。加えて `hook_injected` 恒常 0 という未記録の 3 件目の欠陥が今回判明
- 実走行結果 (2026-08-03): `total=11518 tokens, status=warn` / `claude_md: 1884` / `mcp_descriptions: 1500` / `hook_injected: 0` / `skill_descriptions: 8134` / `references (advisory): 186778 (167 files)`

### `hook_injected` は path 誤りではなく producer 不在だった (実装時に確定)

当初は「glob 先を `~/.claude/logs/session-*.jsonl` から Rust hook の実出力先 `~/.claude/agent-memory/current-session.jsonl` に直せば計測できる」と見立てたが、実装前の確認で否定された。

- `measure_hook_outputs()` が探す `_HOOK_EVENT_TYPES = ("hook_output", "tool_result", "context_injection")` を emit する実装が **repo 全体に存在しない** (`grep -rn '"hook_output"\|"context_injection"' --include="*.py" --include="*.rs" --include="*.js" --include="*.sh"` が自身以外 0 hit)
- `current-session.jsonl` の中身は `{"timestamp","session_id","category","type":"subagent_complete","importance",...}` という telemetry だけで、**hook 注入テキストの本文はどこにも記録されていない**
- `~/.claude/logs/` に `session-*.jsonl` は 1 件も無く、書く実装も無い

つまりこの関数は最初から存在しないログ形式を読んでおり、path 修正では復旧しない。T1 の撤退条件が部分発動し、**`hook_injected` カテゴリのみ撤去・残り 4 カテゴリは配線**という処理に確定した。hook 注入量を測るには先に「hook 出力本文を JSONL に落とす仕組み」を作る必要があり、それは別タスク。

皮肉な符合として、`~/.claude/agent-memory/learnings/quality.jsonl` に残る `hook_output` の唯一のヒットは、2026-04-18 の lint が `measure_hook_outputs` 自身を「関数の本体が 72 行 (閾値: 50)」と指摘した記録だった。構造は検査されたが、読む先が存在するかは誰も検査していない。

## Validation-only Follow-up

| 対象 | drift 内容 | 訂正方針 |
|---|---|---|
| `memory/feedback_explore_subagent_bash_limit.md` | 「Explore 型 subagent は Bash 制限あり」という因果が誤り。(1) memory が参照する `.config/claude/agents/Explore.md` は存在しない — Explore は Claude Code ビルトインの agent type で dotfiles 定義ではない (2) 実エラー `Permission to use Bash with command find ... -exec stat ... has been denied` は permission prompt の自動 deny であり、subagent は prompt に答えられないため agent type を問わず `permissions.allow` (71 entries) 外の Bash は落ちる (3) したがって workaround「general-purpose に切り替え」も誤り — 同じ制約を受ける。Issue #44 で実際に効いたのは親側実行のみ | memory を「subagent は permission prompt に答えられないので allowlist 外の Bash は agent type を問わず自動 deny される」に書き換え、存在しない `Explore.md` 参照を削除、workaround から「general-purpose に切り替え」を除去して「allowlist 追加 or 親側実行」に絞る |
| `references/system-prompt-policy.md:25` | 「Auto-generated 部分の意図しない肥大化は measure-instruction-budget.py で検出する」— 検出器が orphan なので decorative な記述 | T1 で配線するなら記述は生きる。撤去するなら同時に訂正する |

## 採用/不採用の決定

採用 6 件 (詳細は plan 参照):

- T1 (M) #14 `measure-instruction-budget.py` の修理 + 配線
- T2 (S) #13 `plan-implement-bridge.py` の配線 or 撤去の確定
- T3 (S) #5 router 系 hook に self-cancel 句 + ADR-0006 Semantic Advisory の実装規約に明文化
- T4 (S) #12 audience/timing 規約表を既存 reference に追記
- T5 (S) #15 `run_hook()` fail-open の回帰テスト
- T6 (S) validation-only: `feedback_explore_subagent_bash_limit.md` の因果訂正

不採用:

- #1 宣言的 JSON エンジン — 個人 harness で generic dispatcher + schema validation + 観測を新設する実測需要がない (ADR を盾にした棄却ではない)
- #8 directory authoritative — dotfiles は「event の権威は settings.json」を明記済みで正反対
- #9 allowlist dispatch — エンジン不在ゆえ守る対象がない
- #4 bypass prefix — #2 (UserPromptSubmit 評価注入) を採らない限り不要。Codex も「計測基盤なしには後回し」と判定
- #2 UserPromptSubmit prompt evaluation — 記事の 31% 削減主張に実測がなく、dotfiles 側にも false-positive / correction round-trip を測る基盤がない。T1 で計測基盤が直ってから再評価する
- #11 / #6 / #7 — Already (強化不要)

## 教訓

1. 記事本体の手法採用より副産物のバグ検出で元が取れた — 15 手法中、記事由来の新規規約は 3 件 (T3/T4/T5) にとどまり、残り 3 件は記事の framing が露出させた既存の穴 (orphan 2 件 + memory の誤因果 1 件)
2. 「Gap」判定は「既にあるが配線されていない」を見落とす — #14/#13 はどちらも実装が存在し docstring まで書かれていた。`2026-07-31-boris-cherny-yc-ablation` の教訓「概念名の不在を実装の不在と読み違えない」の逆パターンで、今回は「配線の不在を実装の不在と読み違えかけた」
3. escalation は解決ではない — #14/#13 は 2026-04-23 に「ユーザーに escalation 済み」と記録して閉じられ、2026-06-07 に再検出されてまた閉じられた。escalate した先で判断が確定したかを追う仕組みがない
4. N/A の根拠に自分の ADR を使うときは条文を読み直す — ADR-0006 は Semantic Advisory を明示的に許容しており、JSON エンジン棄却の根拠にならなかった。結論 (N/A) は正しかったが理由が誤っていた。Codex がこれを検出した
5. **「読む側が壊れている」と「読む先が存在しない」を分けて診断する** — `hook_injected: 0` を最初は path 誤りと見立てたが、実際は producer が一度も書かれていなかった。silent zero を見たら consumer の設定より先に producer の実在を確認する。lint は `measure_hook_outputs` の行数を検査したが、それが読む先の実在は誰も検査していなかった
