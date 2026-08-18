---
title: "Coding Agentの「All tests passed」を信用する前に確認したい5項目 (absorb 分析)"
date: 2026-08-16
source:
  title: "Coding Agentの「All tests passed」を信用する前に確認したい5項目"
  author: kiritani_r
  url: https://zenn.dev/kiritani_r/articles/a16f25f3390246
  type: blog-post
  published: 2026-08-11
  fetched: "ユーザーが全文を貼り付け（fetch 不要）"
family: code-review-best-practices
saturation: "PASS (warning) — N=13、直近 monotaro absorb 時点で 11 件中 7 件採用（採用率 64%）で閾値 20% を大きく超過"
status: implemented
type: absorb-analysis
---

# 「All tests passed」を信用する前に確認したい5項目 — absorb

## Source Summary

記事の主張は、同じ Coding Agent が実装とテストを両方書くと「要件を誤解 → 誤った実装 → その実装に合うテストを書く → All tests passed」が成立するというものだ。テストが通ったことと要件どおり実装できていることは別で、Merge 前に「テストだけでは保証できない場所」から順に見る必要がある。挙げられている5項目は、①変更範囲、②要件との一致、③テストが本当にバグを検出できるか、④境界値・失敗時の挙動、⑤変更漏れ・影響範囲。加えて「調査」と「変更」の分離（agent にまず read-only で探させ、人間が判断してから直させる）、レビュー可能な単位への PR 分割も挙げる。記事の決め台詞は「このテストは、今回の修正を消したら本当に失敗する？」。

## Phase 1.5 Saturation Gate

family=code-review-best-practices、N=13。採用率が閾値を超えるため PASS (warning)。Step 7 Stale-Plan Audit は直近3件（2026-08-06 monotaro=planned / 2026-07-31 stopped-reviewing=implemented / 2026-07-27 estie=analyzed）がいずれも30日猶予内のため audit skip。

## per-method 照合台帳（記事の8手法）

| # | 手法 | verdict | matched_prior / 根拠 |
|---|---|---|---|
| M1 | 変更範囲を先に見る | Partial（当初 rehash → Codex 指摘で降格） | `skills/review/SKILL.md:108,150` の `diff --stat`/`--name-only` は規模判定と reviewer 振り分けの入力。`agents/product-reviewer.md:40` の Scope Creep は spec 前提かつ 50 行以上起動。依頼と変更ファイル集合を対応付ける配線は無い |
| M2 | 要件→実装→テストの三点照合 | rehash | `skills/review/SKILL.md:465` Mandatory Review Dimension「仕様整合性」— spec 不在時もユーザーの意図と照合し、未確認なら `[SPEC UNCHECKED]` を出す |
| M3 | テストの検出力（修正を消したら落ちるか） | **Gap → 採用** | `agents/test-analyzer.md:65` 4b（トートロジーテスト静的検出）と `:77` 4c（diff の assertion 書き換え検出）は存在するが、どちらも静的読解と diff 差分の検査。反実仮想は無い。`review-checklists/cross-cutting.md:56` CC-6 はテスト追加の有無のみ。`blueprints/autocover.yaml:42` の mutation-check は `${MUTATION_CMD:-true}` で no-op、かつ `settings.json:193` で autocover skill 自体が `off`（休眠） |
| M4 | 境界値 | rehash | `agents/edge-case-hunter.md` + `skills/edge-case-analysis` |
| M4' | 「正しく失敗するか」（retry / idempotency） | **Gap → 採用** | `references/task-archetypes/external-api.md` が retry を3箇所（落とし穴表・不変条件・テスト戦略）で指示しながら、idempotency / 冪等性の言及が全46行で0件 |
| M5 | diff に出ていない場所 | rehash | `agents/cross-file-reviewer.md:19` が impact radius (depth=2)、`:88` 以降で署名/型/export/設定値/DB スキーマ・API コントラクト不整合 |
| M6 | 「調査」と「変更」の分離 | rehash | `skills/freeze` が PreToolUse で Edit/Write に確認を挟む、`agents/product-reviewer.md:12` EXPLORE ONLY、`references/subagent-delegation-guide.md:1220` |
| M7 | PR 分割 | rehash（強化不要） | `agents/code-reviewer.md:190` Section E Refactor-Mixing Block #17（refactor 50 行以上 かつ feature/bugfix 20 行以上で mixing 判定）+ `skills/github-pr/SKILL.md:93` の5分割パターン |
| M8 | ドメイン別 merge 前チェック | rehash（DB）/ Gap（外部 API） | `task-archetypes/db-migration.md:29,38` に冪等性テストあり。外部 API は M4' の穴 |

## Phase 2.5（Codex 批評）

経路の記録: 初回の `codex exec` は Bash tool の 600000ms 上限に当たって打ち切られた（出力は `Command timed out after 9m 50s`）。これは自分の設定した上限が原因であり、Codex 側の no-progress ではない。cmux Worker への切り替えを試みたが `launch-worker.sh` が `cmux is not available` を返した（cmux 外セッション）ため、短縮プロンプト + `timeout 470` の bounded 再試行で取得した。

Codex が判定を覆した点。

- M1 を rehash から Partial に降格した。理由は「`diff --stat` は規模・ルーティング・impact 調査の入力であり、依頼・spec と変更ファイル集合を対応付けて『過大』を判定する配線ではない」。
- M3 の採用を支持した。理由は「4b/4c は『テストの見た目』と『期待値改変の不審さ』を読む検査で、修正とテストの因果結合は証明しない」。
- 実装方式は mechanism ではなく instruction を推奨した。理由は「汎用 hook で強制しても、対象テストと最小 mutant の選定が静的には決められない」。

記事より重い、Codex が掘り当てた実配線バグが2件ある。

1. `skills/review/SKILL.md:308` と `reviewer-routing.md:74` が dispatch する subagent_type は `pr-test-analyzer` だったが、素の名前の agent は存在しない（あるのは `test-analyzer` と名前空間付きの `pr-review-toolkit:pr-test-analyzer`）。`agents/test-analyzer.md:11` は自ら「正典」「プラグイン同梱の別実装は名前が異なる点に注意」と警告しており、その警告を書いた本人が名前違いの被害者になっていた。4b/4c が一度も起動していなかった可能性がある。
2. test reviewer のトリガーが「テストファイルが変更されている」のみで、記事が名指しする最悪ケース（実装だけ変えてテストを足さない）では一度も起動しない。

## 採用（5件、commit 済み）

- T1: `SKILL.md:308` / `reviewer-routing.md:72,74` の dispatch 名を `pr-test-analyzer` から `test-analyzer` に是正
- T2: test reviewer のトリガーに「バグ修正・既存ロジックの振る舞い変更（テストファイルが1つも変更されていない場合も含む）」を追加
- T3: `agents/test-analyzer.md` に 4d「検出力の反実仮想チェック」を追加。対象仕様 / 壊す最小変更 / 失敗すると想定されるテスト / 実際の失敗内容 の4点を要求し、read-only なので実行は必須にせず未検証なら `[COUNTERFACTUAL UNCHECKED]` を明記させる
- T4: `task-archetypes/external-api.md` に冪等性を3箇所（落とし穴表・不変条件・テスト戦略）で追加。retry と idempotency を必ず対で設計させる
- T5: migration-guard drift の一括修正（下記）

## Validation-only から採用に昇格した drift（T5）

`migration-guard` エージェントは `docs/archive/agents/` に退避済みで起動できないのに、`stage-transition-rules.md:68` / `task-archetypes/db-migration.md:45` / `high-risk-change-patterns.md:26` / `change-surface-preflight.md:16` / `scripts/runtime/change-surface-advisor.py` の5箇所が「起動推奨」と名指ししていた。DB Migration は Critical 指定なのに、実質レビュアー不在だった。`cross-file-reviewer`（§5 マイグレーションとコードの整合性）に付け替え、単一ファイル・50行未満でも必須起動する override を SKILL.md 規模別表 / コンテンツベース表 / reviewer-routing / agent frontmatter / agent-orchestration-map / architecture.html の6箇所で揃えた。`cross-file-reviewer.md` §5 に up/down rollback（無ければ CRITICAL）・冪等性・expand-contract・本番ロック影響の4点を報告必須として追加。`agent-design-lessons.md:351` が指していた `.config/claude/agents/archive/` は存在せず（実体は `docs/archive/agents/`）、列挙されていた `autoevolve-core` はリポジトリのどこにも存在しなかったため、パス訂正と併せて実在しない名前を落とした。

## Codex Review Gate

4回 BLOCK、5回目で PASS。BLOCK で潰した内容を順に記録する。

1. `change-surface-advisor.py` の docstring だけ書き換えて db_migration の advice 本体が `edge-case-hunter + security-reviewer` のまま残り、docstring がスクリプトの実挙動を偽る状態を自分で作っていた
2. `cross-file-reviewer` の起動条件が「2ファイル以上」なので単一 migration ファイルでは起動せず、migration-guard の穴が残っていた
3. `cross-cutting.md` CC-7 は「migration と対になっているか」を問う2行しかないのに、rollback・後方互換性を担保するかのように書いていた（付け替え先の能力を誇張した）
4. 必読参照を裸の `references/...` で書いたが実行時に解決しない（慣習は `~/.claude/references/...`。`typescript-reviewer.md:24` / `SKILL.md:252` で確認）。加えて `agent-orchestration-map.md:174` と `architecture.html:779` に旧条件が残っていた

最終判定の verbatim: 「**PASS** / DB Migration の例外は、行数・ファイル数に関わらず `cross-file-reviewer` を必須選定する形で一貫しています。」

## 教訓

- 記事の framing が検査器として働いた典型例。記事由来の新規観点は実質2件（M3 の反実仮想、外部 API の冪等性）だが、「そのチェックは本当に発火するのか」という問いを既存ハーネスに向けた結果、test reviewer が誤った名前で dispatch されて起動していなかったこと、DB Migration の推奨レビュアーが実在しないことが出た。採用件数より、露出した実バグの方が価値が大きい。
- drift 修正が新しい drift を生むことを自分で実演した。付け替え先（CC-7）の能力を確認せずに「rollback を担保する」と書き、docstring だけ直して実データを放置した。どちらも Codex の BLOCK で潰したが、`feedback_drift_fix_creates_drift` が警告していた失敗そのものだった。
- 休眠 artifact を採用根拠に数えない。mutation testing は `autocover.yaml` に存在するが、コマンドが no-op デフォルトで skill 自体が `off`。「存在する」と「動く」は別。
- Bash tool の `timeout` 上限 600000ms に当てた打ち切りを「Codex が応答しなかった」と書かない。ツール出力は `Command timed out` としか言っていない。

## 未実施

- M1（依頼と変更ファイル集合の対応付け）は Partial のまま。Codex は「要件→変更ファイルの明示的対応付けを追加する価値がある」としたが、今回は見送った。
- `.hammerspoon/README.md` と `daily_enforcer.lua` に本セッション中、本作業とは無関係な差分が発生した（alert 削除・通知のみ残す変更）。コミット対象から除外し未コミットのまま残してある。
