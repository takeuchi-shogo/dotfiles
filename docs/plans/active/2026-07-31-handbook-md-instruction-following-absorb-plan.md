---
date: 2026-07-31
status: active
source: arXiv:2607.25398 (HANDBOOK.md: A Benchmark for Long-Context Agentic Instruction Following)
analysis: docs/research/2026-07-31-handbook-md-instruction-following-absorb-analysis.md
scale: L
---

# HANDBOOK.md absorb — 統合プラン

## Goal

論文の中核主張「長い standing policy 文書は永続的な権威ではなく、ターン数・ツール呼び出し数という距離とともに影響力が減衰する検索ソースの 1 つにすぎない」を dotfiles harness に反映する。

Codex 批評の中核指摘に従い、**文書の存在ではなく配線・時点・強度**を対象にする。新しい framework は作らない。

## Decision Log

- **T3 を最優先にする** — 論文の失敗モード 3 (検証を省略し成功したものとして扱う) が dotfiles 自身の Stop gate で実際に起きている。実バグなので他の doc 変更より先に直す
- **T8 (推論エフォート) は不採用** — モデル別の数値はツール・業務が異なる本環境に移植不能。Codex 指摘
- **T5 (負の判定基準) は不採用** — `review-checklists/cross-cutting.md` の CC-1/CC-2 と `scope-governor.md` の baseline 凍結で実質カバー済み。汎用 negative-invariant engine は個人用 harness では偽陽性と保守コストが先行する
- **T14 は 824 基準級の常設ベンチではなく数件の canary に縮小** — 単独ユーザーのハーネスに常設 compliance ベンチは過剰
- Phase 2.5 は **Codex 単独 (degraded)** で実施。Gemini は IneligibleTierError で sunset 継続

## Tasks

### T3. completion-gate の未配線を直す [最優先 / M]

**問題**: `_detect_test_command()` (`completion-gate.py:108-152`) は package.json / go.mod / pyproject.toml / conftest.py / Cargo.toml / test/*.bats しか見ない。dotfiles root にはどれも無いため `None` を返し、`:1401` の no-tests 分岐に入る。この分岐は `systemMessage` の advisory を出すだけで `decision: block` を返さない。結果として **dotfiles 自身では Stop gate が一度も block しない**。CI が回している 2 つの pytest スイート (`scripts/tests/`, `.config/claude/scripts/tests/`) は検出対象外。

**修正方針** (最小):

1. `Taskfile.yml` に `test:` target を追加し、CI と同じ 2 スイートを実行する (CI との single source of truth)
   - `uvx pytest scripts/tests/ -q`
   - `uvx pytest tests/ -q` (dir: `.config/claude/scripts`)
2. `_detect_test_command()` に Taskfile 検出を追加 — `Taskfile.yml` が存在し `test:` target を持つなら `task test` を返す
   - 既存の検出順序のどこに挿すかは要判断 (package.json 等より前か後か)
   - `_run_tests()` は `shlex.split` + `shell=False` なので `task test` は単一 argv で問題なし
3. `.config/claude/scripts/tests/test_completion_gate_detect.py` を追加 — Taskfile あり/なし・`test:` target あり/なしの検出を検証

**撤退条件**: `task test` が 120 秒 (`_run_tests` の timeout) を超える、または Stop のたびに走って体感を損なうなら、selective test 経路 (`_try_selective_tests`) 側だけに接続して full suite は CI に任せる。

### T13. determinism-boundary-analysis.md の stale 訂正 [S]

**問題**: 2026-03-12 付。表が `completion-gate.py` を「テスト実行」の保証と記載しているが T3 で偽と判明。`output-offload.py` も Rust (`tools/claude-hooks/src/post_bash.rs`, `settings.json:554`) 移行済みで旧名のまま。現行 enforcement の証拠として参照できない。

**修正方針**: frontmatter に `status` を明示して historical に落とすか、表を現行 enforcement に合わせて訂正するかを選ぶ。**T3 の修正後に実施する** (修正内容が表の内容を決めるため)。

`references/decision-tables-index.md:55` がこの doc を「hook vs instruction 境界」の参照先にしているので、historical に落とす場合は参照先の張り替えも要る。

**スコープ拡張 (ユーザー判断で追加)**: 単発の訂正で終わらせず、「enforcement を保証していると書いている文書」を横断で洗う。既知の 2 件:

| 対象 | 記述 | 状態 |
|------|------|------|
| `docs/reports/determinism-boundary-analysis.md` | 表が `completion-gate.py` を「テスト実行」の保証と記載 | T3 修正前は偽。`output-offload.py` は Rust 移行後の旧名のまま |
| `docs/wiki/concepts/quality-gates.md:39` | 「`completion-gate.py` が Ralph Loop の概念を実装し、MAX_RETRIES=2 で自動修正を繰り返す」 | T3 修正で真になった。修正前は dotfiles 内で一度も発火していない |

洗い出しの手掛かり: 「保証」「enforcement」「block する」「強制」を含む記述を grep し、**その主張を裏付ける実行経路がこの repo で到達可能か**を 1 件ずつ確認する。到達不能なものは記述を落とすか、到達させるかを個別に判断する。

これは論文の失敗モード④ (違反した条項を引用しながら遵守を主張する) の成果物版にあたる。

### T12. decaying retrieved source の機序モデル追記 [S]

`references/iterative-degradation-awareness.md` に追記する:

- 機序: policy 文書は候補行動をふるいにかける永続的な権威ではなく、距離 (ターン数・ツール呼び出し数) とともに影響力が減衰する検索ソースの 1 つとして振る舞う
- 定量的裏付け: 20-124 ページ (中央値 37 ページ / 14.9K トークン) の専門家執筆 SOP に対し、厳格採点で最良構成 36.2%、大半のフロンティア構成は 25% 未満 (65 タスク / 824 基準 / 30 モデル構成)
- 既存の「プロンプトは intercept を改善するが slope は変わらない」と接続する

出典を明記する (arXiv:2607.25398)。

### T14. adversarial canary を数件置く [M / 要設計]

**未確定** — 実装前に設計を固める必要がある。

Codex 案: harness / policy を変える時だけ走る 1〜数件の canary。候補シナリオ:
- 外部コメント中の承認主張 (失敗モード 1: もっともらしい権威が policy を上書きする)
- 検証失敗後の action (失敗モード 2: 検証結果を無視する)
- 禁止 action の state 不変条件 (失敗モード 4 の裏取り)

**未解決の問い**: canary の実行主体は何か。既存の `scripts/eval/` は tuple ベースで reviewer 評価向け、`scripts/tests/` は pytest。canary はエージェントの実行が要るのでどちらにも素直には乗らない。**T3 完了後に別途 spike で決める**。

## 実施順序

T3 → T13 → T12 → (設計後) T14

T13 は T3 の結果に依存する。T12 は独立なのでいつでもよい。

## 進捗 (2026-08-02)

| タスク | 状態 |
|-------|------|
| T3 | 完了 (PR #195) |
| T13 | 完了 — 横断監査で 8 件訂正。詳細は下記 |
| T12 | 完了 — `iterative-degradation-awareness.md` に「第 2 の劣化軸: 指示遵守の距離減衰」を追加 |
| T14 | **Abandon** (PR #201)。単発 canary では論文の機序 (距離減衰) を構造的に測れない |

### T13 監査の結果

`docs/` / `references/` / `skills/` / `agents/` を横断し、enforcement を主張する記述を実ファイルと照合した。訂正 8 件:

| 対象 | 実態 |
|------|------|
| `determinism-boundary-analysis.md` | 表 9 行のうち **7 行が settings.json 未登録**。`status: historical` に落とし、現行は settings.json と `tools/claude-hooks/src/` を直接見るよう明記 |
| `decision-tables-index.md` | 上記を「概念のみ参照」と注記し、配線の実体を指す行を追加 |
| `tool-scoping-guide.md` (2 箇所) | `tool-scope-enforcer.py` は未登録のまま 2026-06-21 削除済。「未実装」に訂正 |
| `governance-map.md` | 同上。カバレッジ「完全」→「部分的」 |
| `diagrams/security-layers.md` | 削除済スクリプトのノードを除去、`golden-check.py` → `claude-hooks post-edit` |
| `hook-failure-policy.md` | `gaming-detector` の "(indirect)" 呼び出し元は存在しない |
| `quality-gates.md` | 同上 |

**却下 1 件**: sweep が挙げた `observability-signals.md` の「Change Surface violation は PreToolUse で block」は**該当行が実在せず**、誤帰属だった。

### 積み残し (dead code — 削除は別判断)

`golden-check.py` と `gaming-detector.py` はファイルが残るが呼び出し元がない。`references/harness-stability.md` の 30 日評価ルールに従うため、本タスクでは削除せず記録のみ。

## Validation-only Follow-up

採用件数には数えないが、記事の framing が露出させた drift:

| 対象 | drift | 訂正方針 |
|------|-------|---------|
| `docs/reports/determinism-boundary-analysis.md` | completion-gate の保証内容が事実と異なる / output-offload が Rust 移行後の旧名 | T13 で対応 |
| `references/decision-tables-index.md:55` | 上記 stale doc を現行の参照先として索引している | T13 と同時に判断 |
