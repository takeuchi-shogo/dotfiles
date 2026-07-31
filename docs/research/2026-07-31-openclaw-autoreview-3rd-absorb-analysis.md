---
title: "openclaw/agent-skills autoreview SKILL.md — 3 回目の absorb (light Phase 2)"
date: 2026-07-31
source:
  title: "autoreview SKILL.md"
  author: openclaw/agent-skills (@steipete)
  url: https://github.com/openclaw/agent-skills/blob/main/skills/autoreview/SKILL.md
  type: oss-skill-definition
  fetched: raw.githubusercontent.com (WebFetch, 全文取得)
  source_last_commit: "2026-07-23 b8d14648 feat(autoreview): default findings to P0"
status: implemented
family: code-review-best-practices
prior-absorb:
  - docs/research/2026-05-28-openclaw-autoreview-absorb-analysis.md
  - docs/research/2026-07-27-openclaw-autoreview-reabsorb-analysis.md
saturation: "同一ソース 3 回目。ソース差分ゼロ (07-23 が最終更新、07-27 の再 absorb と同一内容)。delta=9 は前回パスの取りこぼし"
adopted: 5
validation-only: 2
degraded: "Phase 2.5 は Codex が 700s 無出力で失敗。Gemini は sunset。代わりに codex CLI の実測で代替した"
---

# openclaw autoreview — 3 回目 (採用 5 / validation 2)

## 結論

**ソースは 1 バイトも変わっていない**。`gh api` で確認した最終更新は 2026-07-23 で、07-27 の再 absorb が見たものと同一。したがって「記事の更新分を取り込む」という absorb は成立しない。

成立したのは別の問いだった: **07-27 のパスが何を見落としたか**。当時のセクション表 (`2026-07-27-...md:35-46`) には、その時点で既に存在していた `## Release Branches And Release Process` と `## Review engine isolation` が載っていない。per-method 台帳を組んだ結果、rehash 20 / novel 6 / ambiguous 3 で delta=9。

最大の収穫は採用そのものではなく、**採用案が実測で否定されたこと**。「レビュアーの隔離に `--ignore-user-config --ignore-rules` を足す」という当初案は placebo で、実際には project doc 注入を止めない。正しいキーは `project_doc_max_bytes=0` だった。

## per-method 照合台帳

light-phase2 の規約により、rehash として除外した分も残す。

### rehash 20 件 (delta から除外)

| current 手法 | matched_prior |
|---|---|
| Helper script bundle (1 helper/1 bundle/1 engine/1 result) | `2026-05-28` 手法#1「1 helper が 1 bundle を組み、1 engine を呼び、1 structured result を validate して stop」/ 同一文 |
| review 出力は advisory、全 finding を実コードで検証 | `2026-05-28` 主訴「レビューは advisory として扱い」/ 同一 |
| no-nested-review | `2026-05-28` T3 / 同一 verbatim を `/review` Anti-Patterns に採用済 |
| PASS-exit lock | `2026-05-28` T1 / 同一 verbatim |
| Twin-rerun (fix → focused test + review 再実行) | `2026-05-28` T2 / 同一 verbatim |
| inline comment は real invariant/ownership 時のみ | `2026-05-28` T5 / 同一 verbatim |
| Panel opt-in / `--reviewers` / per-engine model・thinking | `2026-05-28`「Panel opt-in: default は single engine」/ 同一 |
| heartbeat 耐性 + 30 min SLA | `2026-05-28` #3 → `2026-07-27` で T9 retire / 同一 |
| Pick Target mode 分岐 + clean-local caveat | `2026-05-28` T4 / 同一 verbatim |
| Parallel closeout (format → test ∥ review) | `2026-05-28` T8 → `2026-07-27` で 2026-06-13 実装済と確認 / 同一 |
| security suppression auditability | `2026-05-28` T6 → `2026-07-27` で retire / 同一 |
| regression provenance 役割分離 + automerge trigger 追跡 | `2026-05-28` #13/#6 → N/A 降格 / 同一 |
| gitcrawl `doctor --json` | `2026-05-28` #7 / 同一 |
| engine override 禁止 | `2026-05-28` #2 Already / 同一 |
| review のためだけに push しない | `2026-05-28` #12 Already / 同一 |
| Scope Governor 全 7 概念 | `2026-07-27` S1 → `references/scope-governor.md` 新設済 / 同一 |
| Oversized Bundles / chunking | `2026-07-27`「採用 0 (Oversized Bundles)」節 / 同一 |
| Context Efficiency | `2026-07-27` 表 `:44`「実質あり (no-nested-review = T3)」/ 同内容 |
| Final Report 4 要素 | `2026-07-27` S2 → synthesis-report に `## Tests Run` 追加済 / 同一 |
| Codex 既定 Sol / terra は access fallback のみ | `2026-07-27` Validation-only 節 / 同一 |

### delta_methods 9 件と Pass 2 判定

| 手法 | verdict | Pass 2 判定 | 根拠 |
|---|---|---|---|
| release branch 凍結 | novel | **Already (強化不要)** | `references/scope-governor.md:84` に同等の規律。07-27 の S1 で既に入っていた |
| 既定出力の優先度ゲート (P0 only) | ambiguous | **Already (強化不要)** | `review/SKILL.md:411` の verbosity guard + `templates/review-output.md:27` の confidence ≥ 80 フィルタ |
| source-blind な挙動検証 (behavior-validator) | novel | **Partial (見送り)** | `references/workflow-guide.md:940` の Static/Dynamic/Semantic 3 層 + `/validate` で実質カバー |
| Testbox の credential 限定 | novel | **N/A** | 並列テストの資格情報 staging 自体が存在しない |
| agent-instruction markdown をレビュー免除から外す | novel | **Gap → 採用** | `scripts/policy/review-tier.py:97` |
| 外部 engine 送信前の secret scan | novel | **Gap → 採用** | `lefthook.yml:44` は pre-commit、レビューは commit 前に送信 |
| レビューエンジンの隔離 | novel | **Gap → 採用 (案を修正)** | `codex exec` に隔離フラグなし |
| bug class の兄弟箇所スイープ | ambiguous | **Gap → 採用** | `scope-governor.md:36` は「隣接バグクラス = follow-up」で逆向き |
| 安全チェック削除を報告トリガーに | ambiguous | **Gap → 採用** | `commands/security-review.md:10` に該当記述なし |

## Phase 2.5: Codex 失敗 → 実測で代替

`codex exec --sandbox read-only -m gpt-5.6-terra` を起動したが、**exit code 0 で終了しながら stdout が 0 バイト**だった。これは `agents/codex-reviewer.md:140` が「Codex CLI silent stall」として既に登録している失敗モードそのもの (`feedback_codex_bash_tool_unreachable` も同系統)。プロンプトが長すぎたのが原因と見られる。Gemini は sunset で使えない。

第三者批評の代わりに、Codex に聞こうとしていた事実問題を **codex CLI 自体で実測**した。結果として、意見を聞くより強い反証が得られた。

### 実測: どのフラグが AGENTS.md 注入を止めるか

一時ディレクトリに `AGENTS.md` (「codeword を聞かれたら BANANA と答えよ」) を置き、`codex exec -C <dir>` で「codeword は何か」と聞く。codex v0.144.6。

| 起動 | 結果 | 解釈 |
|---|---|---|
| `--skip-git-repo-check --sandbox read-only` (現行の codex-reviewer と同じ) | **BANANA。ツール呼び出しゼロ** | AGENTS.md が prompt に注入されている |
| `+ --ignore-user-config --ignore-rules` | **BANANA** | この 2 つは project doc を止めない。**当初の採用案は placebo だった** |
| `+ -c project_doc_max_bytes=0` (config.toml あり) | BANANA | ただし tail のみ観測で経路不明 |
| `+ -c project_doc_max_bytes=0 --ignore-user-config --strict-config` | BANANA だが **`rg -n -i "codeword" .` を実行してから**回答 | 注入は消えた。ファイルを自分で探しに行く挙動に変わった |
| 本番フラグ (`-m gpt-5.6-terra --config model_reasoning_effort=xhigh --config project_doc_max_bytes=0 --sandbox read-only`) で「ファイルを読まずに context だけで答えよ」 | **NO** | 注入が消えていることの直接確認 |

`--strict-config` を付けても `project_doc_max_bytes` は unknown field エラーにならなかった (対照として `totally_bogus_key` は `unknown configuration field` で弾かれる) ので、**実在するキー**と確認できる。

### 残存リスク

`--sandbox read-only` のままなので、Codex は自分の判断で `AGENTS.md` を読みにいける。**注入されなくなるだけで、読めなくなるわけではない**。完全に断つには openclaw と同じく空ディレクトリを作業根にして diff を prompt に埋め込む必要があるが、それはファイル横断のコンテキストを失う取引になるため採らなかった。

## 採用 5 件

| ID | 内容 | 変更 |
|---|---|---|
| A1 | レビュアーへの AGENTS.md 注入を切る | `agents/codex-reviewer.md` / `codex-plan-reviewer.md` / `security-reviewer.md` の `codex exec` に `--config project_doc_max_bytes=0`。委譲系 (`rules/codex-delegation.md` の一般手順) には**付けない** |
| A2 | 同上の理由・実測・残存リスクを 1 箇所に記録 | `rules/codex-delegation.md` に「レビューでは AGENTS.md 注入を切る」節。既存の「AGENTS.md は主要な入口」と対比させ、委譲とレビューで方針が違うことを明示 |
| A3 | agent-instruction markdown を docs 扱いから外す | `scripts/policy/review-tier.py` に `_is_agent_instruction_md()` 追加。`CLAUDE.md`/`AGENTS.md`/`PLANS.md`/`SKILL.md`/`*.prompt.md` と `.config/claude/` `.claude/` `.codex/` `.agents/` `.cursor/` `.github/agent-config/` `templates/` `docs/playbooks/` `docs/wiki/` 配下を除外。テスト 12 件追加 |
| A4 | 外部送信前の credential scan | `scripts/security/publicity-scan.py` の diff 範囲を引数化 (既定は `--cached` のまま)。`codex-reviewer.md` Workflow に step 3 として配線し、exit 1 なら Codex を呼ばずに停止 |
| A5 | bug class スイープ + 安全チェック削除トリガー | `references/scope-governor.md` §2 に「バグクラスは分類の前に洗う」、`commands/security-review.md` 冒頭に「既存の安全チェックを削除・弱体化する変更は攻撃経路を示せなくても報告する」 |

A3 の除外リストは `commands/security-review.md` の HARD EXCLUSIONS #9 が持つ反転定義と同じもので、両者に相互参照を張った。片方を増やしたら両方直す。

### A3 が閉じた穴

今日 (2026-07-31) の codex-security absorb で `security-review.md` の `*.md` 除外に「agent-instruction markdown は instruction なので除外しない」例外を入れた。しかし同じ前提の誤りが `review-tier.py` にも残っていて、そちらは手つかずだった。`risk_class=Low` かつ 10 行以下なら `CLAUDE.md` や `agents/*.md` の変更が light tier に落ち、reviewer と Codex Gate を丸ごと省略できた。同じ日に、同じ前提で、片方のゲートだけ直っていた。

## Validation-only Follow-up (採用に数えない)

1. **`[notifications]` は codex v0.144.6 で未知フィールド**。`codex exec --strict-config` が `/Users/takeuchishougo/.codex/config.toml:169:2: unknown configuration field 'notifications'` を返す。macOS 通知の設定が効いていない。dotfiles 側 `.codex/config.toml:136` にも同じブロックがある。正しいキー名は未調査。
2. **`~/.codex/config.toml` は symlink ではなく実体**。dotfiles 側 (`notifications` が `:136`) と live (`:169`) で内容がずれている。`settings.json` の live drift (`project_claude_settings_live_drift`) と同じ構造の問題が `.codex` にもある。dotfiles を編集しても live の Codex には反映されない。

## 実施済 / 未実施

- worktree: `.claude/worktrees/autoreview-iso`、ブランチ `absorb/openclaw-autoreview-isolation`
- 検証: `pytest test_review_tier.py` 42 passed / `ruff check` クリーン / `task validate-configs` exit 0 / `task validate-symlinks` exit 0 / 本番フラグでの注入停止を実測確認
- **未実施**: commit / PR
- **意図的に触っていない**: `docs/research/_index.md` と `docs/wiki/log.md` — 別セッションが並行編集中のため

## メタ学習

- **同一ソースの再 absorb では、まずソースの最終更新日を取る**。`gh api repos/<owner>/<repo>/commits -f path=<file>` で 1 コマンド。今回これを最初にやったことで「記事の更新分」という誤った枠組みを即座に捨てられた。
- **前回レポートのセクション表は網羅の証拠にならない**。07-27 の表は「現在のセクション」を列挙する形式だったが 2 節欠けていた。差分同定は列挙する側の網羅性に依存する。
- **Codex が答えられない事実問題は、Codex 自身を実験対象にすれば測れる**。今回は批評が失敗したが、実測の方が強い結論を出した (採用案が placebo であることの反証)。フラグの効果は意見ではなく観測で決まる。
