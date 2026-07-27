---
title: "Claude Cookbook (Anthropic 公式, 84 レシピ) — absorb analysis"
date: 2026-07-27
source:
  title: "Claude Cookbook"
  author: Anthropic
  url: https://platform.claude.com/cookbook/
  type: vendor-reference-collection
  note: "索引 + 4 レシピを defuddle 取得。84 レシピ中 4 本のみ精読 (残 80 本は索引の title+description で一次トリアージ)"
  trigger: "https://x.com/Xudong07452910 のいいね経由 (rank 17)"
status: analyzed
family: "なし (リファレンス集。単一の主張を持つ記事ではない)"
saturation: "N/A — family 判定の対象外 (collection)"
adopted: 3
coverage: "84 レシピ中 4 本精読 / 12 本を index description で triage / 68 本は未検討"
degraded: "Phase 2.5 は Codex のみ。Gemini は IneligibleTierError"
---

# Claude Cookbook — absorb 分析 (採用 3)

## 結論

Cookbook は 84 レシピの**リファレンス集**で、大半が Claude API アプリ開発向け (RAG / embeddings / vision / third-party 連携 / Agent SDK / Managed Agents)。dotfiles は Claude Code の設定リポジトリで API アプリを作っていないため、コレクション全体としては文脈がずれる。

実質があったのは 1 本だけ — `managed-agents-cma-verify-with-outcome-grader`。独立 grader が rubric で成果物を検査し、pass か per-criterion の gap リストを返すループのレシピで、その中の **rubric 執筆 5 ルール**が dotfiles の review gate 設計に接続した。3 件採用。

## 精読したレシピ (4 本)

| slug | 判定 | 理由 |
|---|---|---|
| `managed-agents-cma-verify-with-outcome-grader` | **採用 3** | rubric 執筆 5 ルール。下記詳細 |
| `managed-agents-cma-prompt-versioning-and-rollback` | N/A | server-side prompt versioning は Managed Agents API の機能。dotfiles では prompt が git にあり versioning = git / review = PR。転用可能な「pin vs latest の分離」も、dotfiles は symlink が working tree を直に指すため構造的に不可能で、その性質は memory `feedback_worktree_review_symlink_stale.md` に既記録 |
| `patterns-agents-async-multi-agent-orchestration` (Jun 2026) | N/A (採用 0) | 5 プリミティブ全てが Claude Code ネイティブに対応済 — `Hub`/`send_message`→`SendMessage`、`create_subagents` (即時 return)→`Agent(run_in_background: true)`、`get_status`→herdr `agent_status` (working/blocked/idle/done)、`kill_subagents`→`TaskStop`。ドメインロジックなしの骨格デモ |
| `misc-session-memory-compaction` | 未判定 | 68KB の notebook。API 側の会話圧縮 (background threading + prompt caching) で、dotfiles の PreCompact flush / PostCompact verify とは層が違う。精読せず N/A 寄りとして未検討に分類 |

## index description で一次トリアージした 12 本

Codex 指摘「3 本だけで閉じるのは早い」を受けて、追加 fetch なしで索引の title + description + 掲載月から判定した。

| slug | 掲載 | 判定 |
|---|---|---|
| `skills-notebooks-01/02/03` | Oct 2025 | N/A — claude.ai/API の Excel・PowerPoint・PDF skill と組織ワークフロー向け。Claude Code harness の skill とは別物。より新しく Claude Code 固有の `docs/research/2026-07-27-anthropic-skills-lessons-absorb-analysis.md` が上位互換 |
| `misc-building-evals` | Mar 2024 | N/A — 汎用 eval 構築。`skill-creator` eval + `references/evaluator-calibration-guide.md` が後発で詳しい |
| `tool-evaluation-tool-evaluation` | Sep 2025 | N/A — API tool 定義の評価。dotfiles は API tool を書かない |
| `patterns-agents-evaluator-optimizer` | Dec 2024 | Already — 生成/評価ループ。`/improve`, review-loop, implement-loop。Codex も「Outcomes の一般形なので低優先」 |
| `patterns-agents-orchestrator-workers` | Dec 2024 | Already — cmux hub-and-spoke / `/dispatch`。multi-agent-orchestration family は N=14 で飽和 |
| `tool-use-memory-cookbook` | May 2025 | Already — 7 層メモリモデル (`references/cc-7-layer-memory-model.md`) |
| `tool-use-automatic-context-compaction` | Nov 2025 | N/A — API 側の会話圧縮 |
| `coding-prompting-for-frontend-aesthetics` | Oct 2025 | Already — `references/design-stance.md` + `frontend-design` / `taste-skill` / DESIGN.md + `references/design-skill-routing.md` (19 skill) |
| `misc-metaprompt` | Mar 2024 | Already — `skill-creator`, `/spec` |

**未検討: 68 本**。third-party 連携 (llamaindex / pinecone / mongodb / deepgram / elevenlabs / wolframalpha / wikipedia)、multimodal、capabilities (RAG / embeddings / classification / summarization / text-to-sql)、Agent SDK 8 本、finetuning、observability。いずれも API アプリ開発向けで harness に接続する見込みが薄いため一次トリアージから除外した。**これは網羅ではない** — 将来 API アプリを書くときは Cookbook 自体を引くべきで、その意味でこのコレクションは reference pointer としての価値が本体。

## outcome grader の rubric 執筆 5 ルールと Pass 1 結果

記事の 5 ルール (原文の表より):

1. Make the grader earn `satisfied` — pass させる前に具体的な証拠 (fetch したページ / 辿った式 / `file:line`) を要求する
2. Describe the goal, not the steps — 特定コマンドを指定すると環境に無いとき silently に検査が飛び、気にしていた検査が一度も走らない
3. Anticipate the writer's shortcuts — 「mirror / repost / 検索スニペットで裏取りするな」の一行がないと、死んだ一次資料が scraper ページに差し替わって grader が通す
4. Mandate the feedback format — スコアボード 1 行 + 失敗 1 件につき 1 bullet
5. Tell the grader what to ignore — no-fire list がないと grader は style nit / 既存課題 / scope クリープで thrash する

| # | 概念 | Pass 1 | 現状 |
|---|---|---|---|
| 1 | PASS 側にも証拠要求 | exists | `skills/validate/SKILL.md:122-123` (「コードの存在だけで Pass と判定する」を Anti-Pattern 化) + `validate/templates/validation-report.md:8-10` (PASS 行も Evidence 列必須) |
| 2 | goal を書き step を書かない | **not_found** | 近接: `references/evaluator-calibration-guide.md:11-21` Outcome over Trajectory。ただし「手段固定 → silently スキップ」の予防規則は未明文化 |
| 3 | 近道の先回り禁止 | **not_found** | 近接: `references/review-consensus-policy.md:343-412` Reward Hacking Mitigation だが**事後検出のみ** (PASS 連続 / 指摘の単調化で人間監査へ escalate) |
| 4 | フィードバック形式強制 | exists | `skills/review/templates/review-output.md:9-48` + `synthesis-report.md:1-52` + `agents/code-reviewer.md:10-21` COMPLETION CONTRACT |
| 5 | no-fire list | exists | `skills/review/references/reviewer-routing.md:209-213` (confidence<60 / pre-existing / linter 領域 / style nitpick を自動除外) + `skills/review/SKILL.md:80-100` Author Preference Authority |
| 6 | known-good から rubric 逆生成 | **not_found** | 近接: `evaluator-calibration-guide.md:52` の train split few-shot。ただし既存 rubric の校正用で、基準そのものの抽出ではない |
| 7 | grader 独立性 (おまけ) | exists | `skill-creator/instructions/testing-evaluation.md:138` — 2026-07-06 fable-unknowns absorb で追加した箇所 |

## Phase 2.5 Refine

**Gemini: 実行不能** (`IneligibleTierError` / `UNSUPPORTED_CLIENT`)。周辺知識補完は未取得。

**Codex (gpt-5.6-terra, xhigh, read-only)** の指摘と反映:

| Codex 指摘 | 反映 |
|---|---|
| Gap2/Gap3 を Already 寄りに倒すのは不正確。「Already-backed / Partial」が正しい。Gap2 は失敗時の禁止原則はあるが rubric 執筆時の予防規則が未明文化。Gap3 は `/absorb` では強いが汎用 grader 向けではなく射程が違う | 採用。Partial に修正し、ユーザー Triage で両方 codify を選択 |
| Gap6 は概念でなく**運用手順として novel**。既存の独立 grader / blind comparison は完成出力を判定するが、良い成果物から rubric を校正する入力経路がない。単一サンプルの文体コピーは避け、抽出した不変条件を人が確認してから採用する形にすべき | 採用。「不変条件を人が確認」「文体テンプレートにしない」を実装文言に反映 |
| 84 中 3 本で「memory に 1 行」で閉じるのは早い。skills-notebooks-03 / building-evals + tool-evaluation / memory・compaction 3 本 / frontend-aesthetics を一次トリアージすべき。evaluator-optimizer は低優先、agentic-search は API 色が強く低優先、metaprompt は最後 | 採用。索引 description で 12 本を追加トリアージ (上記表)。追加採用は 0 |
| memory 単独より source / 日付 / N-A 根拠を残す `Reference only` 記録の方が再評価可能 | 採用。本レポートがその記録 |

## Phase 3 Triage 結果 (ユーザー選択: 全部 codify)

| ID | タスク | 配置 | 規模 |
|---|---|---|---|
| C1 | known-good サンプルから rubric を逆生成する経路 | `skill-creator/instructions/testing-evaluation.md` に **Rubric authoring** 小節を新設 | S |
| C2 | rubric は「何が証拠か」を書き検証手段を固定しない | 同小節の 2 番目の bullet (C1 と 1 小節に統合、並列ルールを新設しない) | S |
| C3 | 被評価者の近道を rubric で事前に塞ぐ | `references/review-consensus-policy.md` §8 に **事前封じ** 小節を新設。既存の事後検出シグナルの直前に置き、対比構造にした | S |

C3 には dotfiles の既存実装 4 件を「塞いでいる近道」の対応表として載せ、新しい Verifier を作るとき同じ列を 1 行以上埋めることを要求した。載せた 4 件は全て実ファイルで確認済:

- `/absorb` Saturation Gate `matched_prior` 3 点必須 → 「似ているから rehash」で照合せず skip する近道
- `references/web-fetch-policy.md` trusted 外 WebFetch 禁止 → 内部 Haiku 要約を原文引用として使う近道
- `agents/code-reviewer.md:23` 「file:line と再現可能な根拠がない指摘は Non-Finding に降格」 → 根拠なしの印象論を finding に数える近道
- `skill-creator/instructions/testing-evaluation.md` process-adherence check → 成果物だけ整えてワークフロー実行を飛ばす近道

## 実施済

- ブランチ: `fix/careful-freeze-description-drift` (#41 と同一ブランチに継続)
- `.config/claude/skills/skill-creator/instructions/testing-evaluation.md` — Rubric authoring 小節追加 (C1 + C2)
- `.config/claude/references/review-consensus-policy.md` — §8 に事前封じ小節追加 (C3)
- 検証: `task validate-configs` exit=0 / 117 ok / 失敗 0
- 未実施: commit / PR

## 副次的な検証 (採用に数えない)

`patterns-agents-async-multi-agent-orchestration` は自身を「Claude Opus 4.8 system card の multi-agent 結果の背後にある 2 パターンの shape」と説明している。CLAUDE.md が既定にしている hub-and-spoke conductor (Sakana Fugu の手作り再現) が 1st-party の構成と同形だという裏付けになる。パターン選択の妥当性の確認であって、取り込むものはない。

## 未取得・未検証

- **Gemini 周辺知識補完**: 実行不能
- **68 レシピ未検討**: API アプリ開発向けと判断して一次トリアージから除外。網羅ではない
- `misc-session-memory-compaction` (68KB notebook): 精読せず
