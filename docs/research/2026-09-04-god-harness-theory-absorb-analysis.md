---
title: "「神ハーネス理論」(@MakeAI_CEO) — absorb 分析"
date: 2026-09-04
source:
  title: "今日からClaudeを触る人でも理解できる「神ハーネス理論」"
  author: "@MakeAI_CEO"
  url: https://x.com/MakeAI_CEO/status/2093264660082597994
  published: 2026-08-28
  type: x-post
  fetched: "Obsidian Vault の raw clipping (ローカルファイル、全文 700 行)"
status: implemented
family: harness-engineering
saturation: "PASS (warning) — N=12+、直近 3 件の採用 5/1/2 で採用率 20% 超。連続 reject trend なし"
adopted: 3
validation-only: 3
degraded: "Phase 2.5 / Review Gate は Codex 単独。Gemini は IneligibleTierError (feedback_gemini_cli_sunset.md)"
---

# 「神ハーネス理論」— 記事の新規性ゼロ、露出した実バグ 3 件

## 結論

初心者向けの harness 入門記事で、**記事由来の新規 instruction は 1 件も採用していない**。13 手法のうち 9 が named rehash、残り 4 も dotfiles では既存機構でカバー済みだった。

にもかかわらず採用 3 件が出た。すべて **記事の framing が dotfiles 内の実バグを照らした**もので、記事の手法を足したのではない。

| # | 実バグ | 記事のどの lens が照らしたか |
|---|--------|--------------------------|
| B1 | `AGENTS.md:27` / `.codex/AGENTS.md:9` が指す root `CLAUDE.md` の Karpathy 4 原則が 4 ヶ月不在 | 手法 2「地図 — AI には説明書でなく、必要なページへたどり着ける地図を渡す」 |
| B2 | `success_criteria` の schema 二重定義。YAML list 形式の plan は gate に空として読まれ汎用文言へ silent fallback | 手法 6「検品条件は作業前に決める / 自己申告を合格理由にしない」 |
| B3 | `launch-worker.sh` が codex/gemini で `--worktree` を silent に無視。`race-runner.sh` は 2 モデルを同一 tree に並列書き込みさせていた | 手法 12「別々の Bot を作っても、完全に分離された安全領域にはならない」 |

## Source Summary

**主張**: AI の実力はモデルの賢さでは決まらず、周囲に作る「仕事場」(ハーネス) で決まる。`AIの実用上の強さ = モデルの能力 × ハーネスの質 × 検品の質`。

**手法 (13)**: ハーネス8部品 (ゴール / 地図(SSOT) / 分解 / 役割分離 / 道具(MCP) / 検品 / 記録 / 安全柵) / AGENTS.md は百科事典でなく目次 / CLAUDE.md は AGENTS.md を import し Claude 差分のみ / 役割は最大3 / 完成条件を事前定義し証拠で判定 / tasks.json + progress.md の外部記憶 / 権限5段階 / バトンを構造化成果物ファイルで渡す / スキル = 業務マニュアル / 失敗時は「頑張れ」でなく不足能力を問う / 神ハーネス生成メタプロンプト / Grok Bot の環境共有警告 / codex mcp-server 非推奨。

**根拠**: Anthropic / OpenAI / Cursor / xAI の公式ドキュメント引用。独自の測定データはなし。

**前提条件**: コードが書けない初心者。ターミナル未経験を明示的な読者に置く。

## Phase 1.5 Saturation Gate

family = `harness-engineering` (キーワード `harness` / `hook`(フック) / `agent platform`(4ツール比較) の 3 語 hit で閾値到達)。同 family の過去 absorb は 12 件超、直近 3 件 (monotaro 08-06 = 採用 5 / harness-loop-graph 08-02 = 採用 1 / dex 07-27 = 採用 2) が全て採用ありで採用率 20% を超えるため **PASS (warning)**。Step 4.5 の連続 reject trend ガードも不発。

### per-method 照合台帳 (全 13 手法)

| # | current 手法 | verdict | matched_prior |
|---|---|---|---|
| 1 | ハーネス8部品の列挙 | rehash | `2026-08-02-harness-loop-graph-3layers` 台帳 #2「Harness 6 要素」→ `2026-04-08-cc-harness-blueprint`「4層フレームワーク + 18手法 → 7項目統合」。harness 構成要素の列挙として同一 |
| 2 | AGENTS.md は百科事典でなく目次 | rehash | `2026-04-23-agents-md-patterns`「Progressive disclosure (100-150 lines + reference files)」「huge cross-cutting repo-root は逆効果」。単一巨大ファイル回避で同一命題 |
| 3 | CLAUDE.md ↔ AGENTS.md の依存配線 | **ambiguous** | 200行制約は `2026-08-03-shirai-claude-md-trim` と重なるが、@import による二重管理の解消を名指しできる prior なし |
| 4 | 役割は最大3、増やしすぎない | rehash | `2026-05-02-30-subagents-2026` Subagent Count Ceiling / `2026-05-30-14-subagents-4-survived` |
| 5 | 完成条件を事前定義し証拠で判定 | rehash | `2026-06-14-opik-self-repairing-harness` 手法5「verification bar」手法6「green-but-unread」 |
| 6 | tasks.json の evidence 欄 / ゴール改竄防止 | **ambiguous** | 外部記憶ハンドオフは checkpoint/HANDOFF で既出。「AI が完成条件を書き換えられない」の名指し先なし |
| 7 | 権限5段階エスカレーション | rehash | `agency-safety-framework.md` + `2026-05-31-zero-trust-ai-agents`「全 12 原則 exists」 |
| 8 | バトンを構造化成果物ファイルで渡す | rehash | `2026-07-25-herdr-agmsg-orchestration-wall` / `2026-08-02-codex-orchestrator-worker-subagent` |
| 9 | スキル = 業務マニュアル、クロスツール移植 | rehash | `2026-06-02-agents-best-practices`「provider-neutral Agent Skill、harness-engineering 飽和で採用0」 |
| 10 | 失敗時は不足能力を問う | rehash | `CLAUDE.md` core_principles「失敗 → capability gap → durable artifact」(同出典 OpenAI harness-engineering、`2026-04-24` で absorb 済) |
| 11 | 神ハーネス生成メタプロンプト | rehash | `/init-project` skill + `templates/team-project/`。新規プロジェクトのハーネス一式生成という同一目的 |
| 12 | Bot を分けても環境は共有される | **novel** | Grok Bot の absorb 前例なし |
| 13 | codex mcp-server 非推奨 | **novel** | codex 系 prior に非推奨の記載を名指しできない |

delta = 4 (novel 2 / ambiguous 2)。PASS 判定のため full workflow。

### Step 7 Stale-Plan Audit

同 family 直近 3 件のうち `2026-07-27-dex-harness-not-enough` が 39 日経過で `status: analyzed` のまま。採用 2 件 (`references/why-humans-read-code.md`、`PLANS.md` の Program Design 節) の実在を確認し **implemented** に更新した。他 2 件は 30 日未満または status 明示済みで skip。

## Phase 2 判定 (Phase 2.5 修正後の最終版)

| # | 手法 | 判定 | 現状 |
|---|---|---|---|
| 3 | CLAUDE.md ↔ AGENTS.md の配線 | **Gap (実バグ)** | `AGENTS.md:27` / `.codex/AGENTS.md:9` が root `CLAUDE.md` の Karpathy 4 原則を指すが、`37a3e397`(2026-05-05,「prune project CLAUDE.md to specifics-only 435→210 word」) が本文を削除。3 原則の中身は見出し名を失って残っていたが、`Think Before Coding` は消失。詳細版は `rules/common/` = user スコープで Codex の読み取り経路外 |
| 6 | evidence / ゴール改竄防止 | **Partial** (Already から降格) | `PLANS.md:36` success_criteria、`completion-gate.py` は存在するが、gate は frontmatter を読むだけで初期値と比較しない。さらに schema が二重定義で list 形式は空読みされる |
| 12 | 環境共有 | **Gap (実バグ)** | `launch-worker.sh:82` が `MODEL == "claude" && -n "$WORKTREE"` の AND 条件で、codex/gemini では `--worktree` が silent NO-OP。`race-runner.sh:66` は「複数モデルで同一タスクを並列実装」しながらこれに依存 |
| 13 | codex mcp-server 非推奨 | **N/A (明示的棄却)** | `2026-04-27-codex-claude-parity:44`「G10 → N/A、YAGNI」。記事は既存判断を追認するのみで、現在の deprecated 状態の証拠にもならない |
| 1,2,4,5,7-11 | (台帳の named rehash) | Already | 台帳の matched_prior 参照 |

## Phase 2.5 (Codex 批評、verbatim)

> 結論：F1 は実在する「参照先の意味的ドリフト」です。ただし「一度も本文がなかった」「第4原則は repo にない」は誤りです。F3 は Partial より重く、並列書き込み隔離の実装欠陥です。

> ただし 73dac768 時点では target に4原則全文が存在しました。壊れたのは後続の `CLAUDE.md` 圧縮後です。したがって「never written」「Goal-Driven Execution が repo に皆無」は誤りです。

> F2：**Partial** です。(中略) しかし「AI が acceptance criteria を書き換えられない」は未達です。gate はその時点の frontmatter を読むだけで、初期値との比較も本文 `## Success Criteria` の評価も行いません。

> F3：**実害未確認ではなく、隔離不成立の実装欠陥**です。(中略) しかも `race-runner.sh` は「並列実装」を名乗り、Claude/Codex を `--worktree` なしで同じ task に起動します。

> F5：(中略) ただし「この repo で server が接続不能」は確認できませんでした。(中略) 従って「接続障害」は未確認、「障害時 fallback 不備」は確認済み、と分けるべきです。

**私の誤りの訂正**: `git log -S "Karpathy" -- CLAUDE.md` が 0 hit だったのを「一度も書かれていない」と断定したが、本文は "Karpathy" の語を含まず原則名だけで書かれていた。検索語の選択ミス。`git show 73dac768:CLAUDE.md` で `## 1. Think Before Coding` 〜 `## 4. Goal-Driven Execution` の全文を確認し、削除 commit を `37a3e397` と特定した。

**Codex の情報不足を私が補正した点**: F5 の「接続不能」は Codex の read-only sandbox からは見えないが、本セッションのシステムメッセージが `code-review-graph (CONNECT_TIMEOUT)` を明示している。ただし `~/.claude/debug/` の 2026-06-03 ログには接続成功の記録があるため、「常に不可用」ではなく「今セッションで失敗」に表現を限定した。

## Adopted

| # | 内容 | 規模 | 状態 |
|---|---|---|---|
| B1 | `CLAUDE.md` に Karpathy 4 原則を canonical 復活 (既存の 3 節に原則名を戻し、消えていた Think Before Coding を追加)。`rules/common/` の長文版との関係を冒頭に明記 | S | 実装済み |
| B2 | `completion-gate.py:_extract_success_criteria` を scalar / YAML list の両対応に。`PLANS.md` と `resume-anchor-contract.md` の schema 記述を相互参照で統一。回帰テスト `test_completion_gate_success_criteria.py` (3 case) を追加 | M | 実装済み・テスト pass |
| B3 | `launch-worker.sh` の worktree 作成から `MODEL == "claude"` 条件を除去 (root cause)。`race-runner.sh` は各 worker に一意 `--worktree` を渡し、勝者ブランチを stderr で告知、敗者の worktree/branch を cleanup で削除 | S | 実装済み・`bash -n` pass |
| — | `2026-07-27-dex` の frontmatter を `implemented` に更新 (Stale-Plan Audit) | S | 実装済み |

B1 の方針はユーザーが「root CLAUDE.md に 4 原則を戻す」を選択 (Codex 推奨と一致)。`73dac768` の `rejected(karpathy-distribution): 4 原則を全 AGENTS ファイルに複製 — DRY 違反` は「AGENTS 側への複製」の棄却なので、CLAUDE.md 1 箇所への復活はこれに抵触しない。

## Rejected

記事由来の新規 instruction は全て不採用。台帳の named rehash 9 件に加え、手法 3 の「CLAUDE.md が AGENTS.md を @import する」構造も採らない — dotfiles は Codex 用 (`AGENTS.md`) と Claude 用 (`CLAUDE.md` + `rules/`) を意図的に分離しており、依存方向を逆転させると user スコープ rules との重複が増える。

## Validation-only Follow-up (採用に数えない)

| 対象 | drift | 方針 |
|---|---|---|
| `CLAUDE.md` MCP Tools 節 | 「code-review-graph を Grep/Glob/Read より優先」を毎セッション指示するが、本セッションは `CONNECT_TIMEOUT`。fallback 条件が「`list_repos_tool` が no rows」で接続失敗ケースを含まない | **未実装** (Codex Review Gate が scope creep として BLOCK、revert 済み)。別途提案。MEMORY.md の「本業稼働中のため維持」判断は変えない |
| `.codex/config.toml` の repo/live 乖離 | `~/.codex/config.toml` は symlink でなく実体 (`AGENTS.md:4-5` の「`~/.codex/` の実体は `.codex/`」に反する)。diff 244 行。repo 側の `notify` は存在しないユーザー名 `/Users/shogo_takeuchi/...` を指し、live 側が明示否定する legacy `[profiles.*]` テーブルも残る | 別 Issue 候補。`project_claude_settings_live_drift.md` と同型 |
| `task validate-configs` | `ask tier が 8 件出現。deny-rules-catalog.md に ASK セクションを追加して同期せよ` で fail。stash して master 相当でも同一失敗を確認した **pre-existing** | 別 Issue 候補 |
| memory `feedback_worktree_review_symlink_stale.md` | 「CLAUDE.md は templates/claude-md/*.md の生成物」と記録するが `templates/claude-md/` は存在しない | memory 訂正候補 |

## Codex Review Gate (verbatim)

`/review` skill 外の gate なので、reviewer の出力行をそのまま残す。Gemini は `IneligibleTierError` のため Codex 単独 = degraded。

### 1 回目: BLOCK

> - `.config/claude/scripts/policy/completion-gate.py:416` — YAMLとして有効な形式を誤抽出します。確認結果: コメント入りリスト→`None`、`success_criteria: []`→`'[]'`、nested key→誤って取得、folded scalar→`'>'`。
> - `scripts/runtime/race-runner.sh:137` — `wait -n` は成功ではなく「最初に終了した collector」で戻ります。先に一台が失敗・timeout すると、winner 未設定の cleanup が `:106-107` で、後から成功し得る worker の worktree/branch まで強制削除します。
> - Scope creep: `CLAUDE.md:47` の code-review-graph 可用性方針変更、および `docs/research/2026-07-27-dex-harness-not-enough-absorb-analysis.md:12` の research status 更新は、指定された3件の修正に紐づきません。

対応: scanner を unindented キー限定 + コメント/空行スキップ + block scalar 対応 + `[] {} ~ null` は None に書き換え、edge case 5 件をテストに追加 (計 8 件 pass)。`wait -n` を残 collector 数だけループさせ、winner 確定でのみ break。CLAUDE.md の可用性記述は revert。status 更新はユーザーが選択した 4 項目目なので保持 (Codex はこの経緯を知らない)。

### 2 回目: BLOCK

> - `scripts/runtime/race-runner.sh:129-153` — `WINNER_FILE` は内容を書き込む前に作成され得る一方、別 collector の終了で `wait -n` が返ると、空の winner file を winner と誤認します。空の `WINNER_MODEL` で line 153 が `bad array subscript` により終了し、EXIT cleanup が実際の勝者を含む全 worktree/branch を削除します。

**これは 1 回目の修正が作った新しい競合**。`noclobber` はファイル作成が atomic なだけで中身は後から書かれるのに、`-f WINNER_FILE` で勝者判定した。さらに勝者ブランチ告知のために足した `${WORKER_IDS[$WINNER_MODEL]}` が空キーで `set -u` に触れ、cleanup が勝者ごと削除する経路を私自身が開いていた。

対応: `WINNER_READY` marker を追加し、`winner.txt` (model + worker_id) → `result.txt` → ready の順で書く。待機ループと判定を ready 参照に切り替え、`read -r WINNER_MODEL WINNER_WID` で array subscript を排除。

### 3 回目

判定は本レポート作成時点で**未取得**。

## 教訓

**pruning は被参照を確認してから行う。** `37a3e397` は「project CLAUDE.md = project 固有チェックのみ」という正しい intent で圧縮したが、その 15 日前 (`73dac768`) に張った 2 本のポインタを見ていない。`feedback_drift_fix_creates_drift.md` は「参照切れを直すとき書き換え先が実配線か確認する」だったが、今回はその対偶 — **消す側が被参照を確認する** — が抜けていた。`docs/playbooks/stale-doc-retirement.md` は「新 pattern 導入時の旧 doc 降格」を扱うが、「節の削除時に inbound pointer を grep する」手順は持っていない。

**契約書が 2 冊あると、実装は片方しか読まない。** `success_criteria` は `PLANS.md` と `resume-anchor-contract.md` の両方が正典を名乗り、実データも両形式が 3 件ずつ存在した。gate は scalar 側だけを実装し、list 形式は `''` を返して汎用文言に落ちる。皮肉なことに、list 形式で書かれた `2026-04-20-karpathy-absorb-plan.md` の success_criteria には「`completion-gate.py` が読む frontmatter `success_criteria:` と形式整合する」と書いてあり、**形式整合させるという完了条件自体が形式不整合で読まれていなかった**。

**silent NO-OP は「使われていない経路」に隠れる。** `launch-worker.sh` の `--worktree` は codex/gemini で黙って捨てられていたが、`race-outcomes.jsonl` が存在しない = `race-runner.sh` は一度も完走していないため顕在化しなかった。休眠だから直さない、ではなく、**休眠だから壊れたまま残っていた**。root cause は race-runner ではなく launch-worker 側の AND 条件。

**「採用 0」で終わらせない価値は 3 回連続で確認された。** 本件は `2026-08-02-harness-loop-graph`(索引欠落)、`2026-08-16-all-tests-passed`(存在しない agent を dispatch) に続く 3 例目。記事の新規性と absorb の収穫は独立している。

## Decision Log

- Phase 1.5 は PASS (warning) 判定のため light-phase2 に落とさずフル workflow を実行した。delta 4 件のうち 2 件 (Grok Bot / codex mcp-server) は N/A 濃厚だったが、per-method 台帳の立証責任を満たすため検査は全件行った。
- Gemini は起動時に `IneligibleTierError` を返すため Phase 2.5 / Review Gate とも Codex 単独 = degraded。memory の記録 (2026-07-05) を本セッションで再確認した。
- `race-runner.sh` は実行実績ゼロの休眠経路だが、root cause が `launch-worker.sh` の共有ロジックにあり `--worktree` を直接叩く経路にも影響するため修正対象に含めた。
- `.codex/config.toml` の drift と `validate-configs` の pre-existing 失敗は scope 外として実装せず、上表に記録した。
