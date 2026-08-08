---
title: "MonotaRO Makasetaro (AI レビューエージェント) absorb"
date: 2026-08-06
source:
  title: "AI が書いたコードを AI にレビューさせる — Makasetaro の設計"
  author: MonotaRO Tech Blog
  url: https://tech-blog.monotaro.com/entry/2026/08/05/090000
  type: blog-post
  fetched: defuddle (全文取得成功)
status: planned
family: code-review-best-practices
saturation: "PASS (warning) — N=11、採用ありが7件で採用率64%、閾値20%を超過"
plan: docs/plans/active/2026-08-06-review-finding-contract-plan.md
adopted: 5
validation-only: 4
---

# MonotaRO Makasetaro — review finding 契約の absorb

## Source Summary

MonotaRO の社内 AI レビューエージェント "Makasetaro" は Claude Agent SDK ベースで GitHub App として動き、専用サーバを持たず GitHub Actions 上で完結する。記事の主張は明快で、AI が書いたコードを AI にレビューさせること自体は特別でない、質を決めるのは「やらせ方」だとする。fetch_metadata は url=https://tech-blog.monotaro.com/entry/2026/08/05/090000、domain=tech-blog.monotaro.com、route=defuddle、全文取得成功。

## 手法 M1-M10 (記事側)

| # | 手法 |
|---|---|
| M1 | エージェントに GitHub を触らせない（ブリンカー思想=不必要な自由度は渡さない、サンドボックスとは目的が違う） |
| M2 | 投稿の最終決定をハーネスのコードが行う（重要度ルール / コメント数上限 / 指摘行番号が diff 上で有効かの検証 / 既存コメントとの重複排除） |
| M3 | コメントに severity + confidence を必須付与し、ハーネス側でフィルタ |
| M4 | インナーループ: 構造化出力+カスタムツールで1件ずつ累積（部分エラーで全体リトライしない） |
| M5 | アウターループ: マルチラウンドレビュー。過去ラウンド履歴・既存 bot コメント（commit SHA 付き）・人間とのやり取りを毎回プロンプトに織り込み、ラウンドごとにスコープを狭める |
| M6 | 実装セッションの文脈を引き継がない独立レビュー（第三者性の再現） |
| M7 | ターン数上限+予算上限をコードで縛る。目的は削減でなく「想定上限/観測分布/過去最大/発動回数」の4点を常時答えられる説明可能性 |
| M8 | エンゲージメント指標（Actioned=指摘を引用するコミットが後続したか / Engaged=返信・リアクション / ポジネガ比）でトークンコストを正当化 |
| M9 | 同一制約をプロンプト内の異なる位置で複数回提示（arXiv:2512.14982 Prompt Repetition、非 reasoning モデルでの結果） |
| M10 | ACI エンジニアリング: ツール粒度・引数スキーマ・拒否メッセージの設計（SWE-agent arXiv:2405.15793） |

## Phase 1.5 Saturation Gate

family=code-review-best-practices は N=11（agents-md-review-skills / findy-code-review-readability / openclaw-autoreview ×3 / cursor-auto-review-run-mode / 6-stages-ai-human-boundary / agentic-code-review / review-ai-code-mari / estie-dialect-reviewer / stopped-reviewing-my-code）。採用ありが7件で採用率64%、閾値20%を超えるため PASS (warning) とする。Step 7 の Stale-Plan Audit は直近3件が implemented / implemented / analyzed（10日経過、30日猶予内）なので全て audit skip とした。

## Phase 2 判定テーブル（Phase 2.5 修正後の最終版）

| # | 手法 | 判定 | 詳細 |
|---|---|---|---|
| M1 | Already (reviewer 経路) / Partial (pr-autofix 経路) | `templates/pr-review/REVIEW_TASK.md.tpl:22` で gh pr review/comment/merge を厳禁、`:162` `:620` で再掲。settings.json permissions.allow に gh mutation が不在で subagent は自動 deny。ただし `pr-autofix-routine` は agent 自身が push・bot 返信・resolve を実行する（Codex 指摘で Already → 経路別に分割） |
| M2 | Partial | フィルタは `review-consensus-policy.md` の式（boosted_confidence = max + 5*(agreeing-1) / confidence<60 除外 / 10件超は MUST のみ）を LLM が計算する markdown 記述。`scripts/policy/` に review/finding 系スクリプトは0件。行検証は grep 0件で不在 |
| M3 | Partial (契約が二重) | `code-reviewer.md:16` は主観 0-100、`security-reviewer.md:188` は証拠充足型。同一 harness に2契約が並存し、前者にだけ算術がかかる |
| M4 | 条件付き Gap（見送り） | リポジトリ内 ReportFindings 参照 0件。inline 投稿しない現行 `/review` では tool の存在自体が価値を生まない（Codex 指摘で無条件 Gap → 条件付きに降格） |
| M5 | Partial → Gap 相当 | `gh-unresolved-threads`（GraphQL isResolved==false）とマーカー `{"head":SHA,"last_comment_ts"}` はあるが、これはスキップ判定と冪等性の状態にすぎない。Phase1 周回（2.2→2.4→2.2、最大3周）は前ラウンドの指摘を review プロンプトに渡していない |
| M6 | Already（強化不要） | `review/SKILL.md:328` が diff のみを渡す。`code-reviewer.md:453` に Blind-first→Context-aware の2パスがあり、severity 変動を自己検知して `[BIAS_DETECTED]` を出す |
| M7 | Partial | 14の review agent 全てに maxTurns（`code-reviewer.md:7` = 20）はあるが、上限到達を記録する仕組みがない。`cost-gate.py`（WARN_USD=5/STOP_USD=10）は AutoEvolve 専用で review 経路には非適用 |
| M8 | Partial（Already は強すぎ、追加は却下） | `skill-usage-tracker.py` / `extract-promotion-candidates.py` / `reconcile-promoted-ledger.py` / `benchmark/reviewer-calibration.py`（TPR/TNR）/ `reviews.jsonl` は既存。ただし記録は main agent への指示と動的 `python -c` 依存で決定論的コレクタではない（Codex 指摘）。Actioned 指標の追加は却下 |
| M9 | Already（軸の取り違えを訂正） | CLAUDE.md:117 の instruction DRY は artifact 間の重複禁止であり、記事の repetition は1プロンプト内の位置の話。`REVIEW_TASK.md.tpl` は gh 禁止を既に3箇所で再掲済み。引用論文は非 reasoning モデルの結果なので reasoning 前提のレビュアー群に一般化しない（Codex 指摘） |
| M10 | Partial | `pre_tool.rs:84-90` `:188` `:207` は BLOCKED [rule-id]→説明→WHY→FIX の4段で統一されているが、`:14` の一括 add 禁止は1文のみ。deny は stderr+exit 2、全 deny は audit.jsonl に記録される |

## 追加観点で出た穴（定義済み agent/skill ワークフローの見直し）

穴1は `review/SKILL.md:402` の統合ルールにある。confidence<60 除外と boosted_confidence を全 findings に適用するが、confidence を要求するのは code-reviewer / cross-file-reviewer / edge-case-hunter の3 agent のみで、残る11 agent は confidence を出さない。欠落時の扱いが未定義のまま統合ルールが走る。

穴2は verdict のマッピングにある。Critical 1件以上→BLOCK、Important 3件以上→NEEDS_FIX という規則に対して、実際の severity 語彙は MUST/CONSIDER/NIT/ASK/FYI、CRITICAL〜LOW、必須/重要/推奨/参考、絵文字3段、見出しのみ、と5通りに分岐している。golang-reviewer と typescript-reviewer は出力フォーマット節すら持たない。語彙から Critical/Important への対応表は存在しない。

## 実測: review-findings.jsonl の実態

`~/.claude/agent-memory/learnings/review-findings.jsonl`（157行）を数えると、M3・穴1・穴2 の懸念がそのまま実データとして出ている。

| 項目 | 実測値 |
|---|---|
| severity 欠落 | 121件（77%） |
| severity 分布（残り36件） | critical 3 / important 4 / Important 4 / Watch 2 / consider 2 / SHOULD 1 / NIT 2 / MUST 5 / CONSIDER 7 / RETRACTED 1 / ASK 1 / MEDIUM 2 / HIGH 1 / PLAN 1（15値、大文字小文字の異体を含む） |
| confidence | 151件が int、欠落6件 |
| reviewer 欄 | 自由記述。複合値の区切りが `+` と `,` で混在（`code-reviewer+codex-reviewer` / `code-reviewer,codex-reviewer`）、他に `self` / `manual-review` / `gemini-explore` / `pr-test-analyzer` |

原因は `append_to_learnings`（`session_events.py:360-364`）がスキーマ検証をせず、session_id / tier / score を setdefault するだけで書き込んでいることにある。パイプライン自体は生きていて最終書き込みは2026-07-31、`review-metrics.jsonl` も7行ある。

もう1件、`agent-invocations.jsonl`（1724行）は全て `exit_status: completed` だった。実装を見ると `"completed" if tool_response else "unknown"`（`agent-invocation-logger.py:111`）であり、途中で切れた応答も completed と記録される silent success になっている。

## Phase 2.5

Gemini は IneligibleTierError で経路が死んでいる（`feedback_gemini_cli_sunset.md`）ため Codex 単独で実施した。`codex exec --skip-git-repo-check -m gpt-5.6-terra --sandbox read-only --config model_reasoning_effort=xhigh` で実行し、tokens used 134,990、応答取得に成功した。Codex の verdict は自己要約に置き換えず、以下を Codex 批評（verbatim 抜粋）として残す。

> 結論として、最優先は M5 ではなく「Synthesis が入力を正しく解釈・完走判定できること」です。穴1・穴2は単なる形式不統一ではなく、現在の verdict と confidence 集計の前提を崩しています。

> 見落とし: 合意数による confidence boost は、同じ diff・共通プロンプト・似た rubric を読む reviewer を「独立」とみなしています。相関した誤検知を増幅し得るため、合意は根拠ではなく優先順位の補助に留めるべきです。

> 見落とし: M5 で過去コメントを丸ごと渡すのは危険です。持ち越すのは原文履歴ではなく、`finding_id / 対象SHA / status / 人間の決定理由` の小さな ledger に限るべきです。

> M4 は「Gap」ではなく低優先の条件付き Gap です。導入するなら finding ごとの蓄積に加え、最後の `complete | turn_limit | error` 終端レコードを必須にしてください。途中までの findings が残っても、「問題なし」を結論してはいけません。

> M2 の hunk 内行検証も、個人向けの表示だけなら必須ではありません。hunk 外を一律除外すると、周辺文脈の正しい指摘も失います。

Codex が示した優先順は、(1) 穴1・穴2・M3をまとめた typed finding contract + reducer、(2) M7 の reviewer roster と完走状態、(3) M5 の最小 ledger、(4) M10 の false positive と拒否文、(5) M2 の軽量照合、の順。M4 は実害観測後に回すべきとした。組織固有で持ち込まないものとして、全コメントの投稿上限・リアクション比・全 PR 横断コスト分布ダッシュボードを挙げた。

Codex が指した実ファイル3件（`session_events.py:378` の `emit_review_finding` / `REVIEW_TASK.md.tpl:153` の untrusted 明示 / `review/SKILL.md:502` 付近の動的 `python -c`）は全て Opus が実在確認済み。

## Phase 3-4 採用結果

ユーザーは T1〜T5 の全部採用を選び、T1 の強度は fail fast（検証して書き込みを拒否する）とした。

| ID | 内容 |
|---|---|
| T1 | finding 出力契約の統一。canonical severity マッピング表 + confidence_kind 区別 + 欠落時の扱い定義 + `emit_review_finding` の fail-fast 検証 + 合意ブーストを優先順位補助に降格 |
| T2 | 完走判定。レビュアー出力に終端マーカーを必須化し roster と照合、欠落は INCOMPLETE / NEEDS_HUMAN_REVIEW。`emit_review_metrics` に `terminal_status` を追加 |
| T3 | `pr-autofix-routine` の Phase1 周回に finding ledger を引き継ぐ（原文コメントは渡さない） |
| T4 | `pre_tool.rs` の一括 add 判定の false positive 修正 + WHY/FIX の追記 |
| T5 | 投稿・自動修正の直前に file/line/snippet を照合 |

見送りは M4（ReportFindings）。却下は Actioned 指標・コメント数上限・リアクション比・コスト分布ダッシュボード・M9のプロンプト内反復追加。プランは `docs/plans/active/2026-08-06-review-finding-contract-plan.md`（L規模、9 Steps）。

## Validation-only Follow-up（採用件数に数えない）

- `agent-invocations.jsonl` の `exit_status` が定数 `completed` になっている silent success フィールド。1724行すべて同値で診断に使えない。
- `review-loop` は skill ではなく command（`.config/claude/commands/review-loop.md`、35行）として実装されている。棚卸し時の所在訂正。
- `settings.json` の `skillOverrides` で review 系は `codex-review-issue` のみ off。`review` / `validate` / `simplify` / `challenge` / `github-pr` / `pr-autofix-routine` 本体は抑制されていない。
- `pre_tool.rs` の一括 add 判定 false positive は、この absorb の実行中に Codex へのプロンプト内で禁止文字列を引用しただけの Bash が block されて実測された。

## 教訓

記事の「投稿判定をコードのロジックに通す」を逆から読むと、「findings のスキーマが厳密でなければフィルタは機能しない」になる。この lens で自分の台帳を見たところ、severity 欠落77%が出た。記事から新規手法を輸入したのではなく、記事の前提を検査器として使った結果の発見だった。

出力契約を14 agent に分散して定義すると、統合側が全語彙を知らないまま集計することになる。契約は消費側（Synthesis）が要求する1箇所に置くべきだと分かる。

検証なしの append は「書けている」ことを成功と誤認させる。パイプラインの生存（行数が増えている）は契約の充足を意味しない。

## 実装後の追記 (2026-08-06 実行分)

T1〜T5 を同一セッションで実装した。T1/T2/T3/T5 は狙いどおり着地したが、**T4 だけは当初の目的を達成できず方針を変えた**。記録として残す。

### T4 が転回した経緯

T4 の出発点は「一括 add 禁止 hook が、禁止コマンドを**引用しただけ**の Bash まで block する」誤検知だった (この absorb 実行中に実際に踏んだ)。そこで「引用文か、実行されるコマンドか」を見分ける方向で 3 回実装した。Codex Review Gate はそのたびに新しい回避経路を出した。

| ラウンド | 実装 | Codex が出した回避経路 |
|---------|------|---------------------|
| 1 | 直前 1 文字が区切りかで判定 | `env` / `sudo` / `time` 経由、`/usr/bin/git`、heredoc delimiter `EOF-1` |
| 2 | セグメント分割 + 透過プレフィックス | `env -i` / `sudo -u root` / `nice -n 10`、引用内改行での過剰 block |
| 3 | クォート認識分割 | コマンド置換 `"$(...)"`、`bash --noprofile -c`、バックスラッシュ改行継続、`echo '<<EOF'` の heredoc 誤認 |

3 ラウンド目で Codex が構造を名指しした: **「現在の実装は意味論上 fail-closed ではなく、限られた表記だけを検出する fail-open regex」**。これを受けて判別を破棄し、引用文も block する fail-closed に転換した (誤検知は「テキストはファイル経由で渡す」で回避、deny メッセージに明記)。転換後も pathspec (`./` `:/` `:(top)`)、`-u`/`--update`、長い `-C`/`-c`、`--dry-run`/`-n`/`--patch` の過剰 block などの指摘が続き、計 5 ラウンドで収束させた。

最終的に受領した verdict は **BLOCK**。残存 2 件は難読化 (依頼時に除外、変更前も通っていた) と引用符内 `;` によるキャプチャ切れ (クォート解釈が必要 = 穴を空けた方向) で、既知の限界としてコードの doc コメントに記録した。

### 教訓 (この absorb の最大の収穫)

- **ガードの誤検知を消す改修は、bypass を空ける改修になりやすい**。「見分ける」実装は判別境界を持つが、シェルは境界を跨ぐ表記を無限に持つ。誤検知の解消と bypass の封鎖はトレードオフであり、ガードでは後者を優先する
- **同じレビュアーに複数ラウンド回すと、指摘の性質が変わる時点がある**。1〜3 ラウンド目は個別の穴、4 ラウンド目で層の誤り (テキスト層でやるべきでない) を名指しした。個別修正を続ける前に、この転換点を拾えるかが分かれ目になる
- **ハーネスの deny 経路はテストの死角に入りやすい**。`cargo test` は判定関数を直接呼ぶので、`deny()` が UTF-8 バイト境界の slice で panic して block が機能しない状態 (exit 101) をすり抜けた。実バイナリに payload を流すプローブで初めて出た。判定ロジックのテストは block の証明にならない
- **fail-closed の代償は自分に返ってくる**: 転換後、このセッション中に 4 回自分の Bash が block された (プロンプト本文やパッチスクリプトに禁止文字列を書いたため)。回避手段が deny メッセージに書いてあるかどうかで摩擦の大きさが変わる

### レビューの状態

Codex 5 ラウンドの最新 verdict は BLOCK (上記 2 件が残存)。`/review` のレビュアー 3 体のうち `code-reviewer` のみが遅れて `Coverage: complete` 付きで返し (verdict BLOCK)、`security-reviewer` と `edge-case-hunter` は本文なしの idle 通知だけで終わった = `missing_marker`。**本 absorb で導入した Roster 照合ルールに照らすとこのレビューはINCOMPLETE**。PASS は取得していない。

`code-reviewer` の MUST は round-1/2 時点のコード (`is_command_start` / `runs_through_wrapper`) に対する指摘で、fail-closed 転換で該当関数ごと消えている。挙げられた 6 経路 (`sudo` / `env` / `time` / `nohup ... &` / `command` / `find -exec`) と、同レビューが「旧実装でも未検出」とした `git add "."` は、いずれも現在のバイナリで block することを実測した。指摘どおりテストは空白だったので埋めた (58 passed)。

**ここに 1 つ運用上の教訓がある**: 遅れて返ってきたレビューは、レビュー対象が既に変わっている可能性がある。指摘を棄却するにも採用するにも、まず現在のバイナリ/コードで再現を取る。今回は「stale だから無視」でも「レビュアーが言うから直す」でもなく、実測してから 1 件 (テスト空白) だけ採用した。
