---
title: "1日500コミットは、もう読めない ── だからコードレビューをやめた (absorb 分析)"
date: 2026-07-31
source_url: https://zenn.dev/singularity/articles/stopped-reviewing-my-code
source_author: isamu (シンギュラリティ・ソサエティ)
family: code-review-best-practices
saturation: PASS (warning) — N≈11、採用率高で非飽和
status: implemented
commit: 231adf5725e2bc4bf54565aca1743a45252f28d8
type: absorb-analysis
---

# 1日500コミットは、もう読めない ── だからコードレビューをやめた

## Source Summary

エージェント並列運用でコミットが 1 日 500 を超え、人間が diff を読む速度が追いつかなくなった。
選択肢は「生成を減らして読める量に合わせる」か「読まなくても壊れないようにする」の 2 つで、
著者は後者を選んだ。これは精神論ではなく **「壊れたら赤くなって止まる」を積み上げる作業** だった、
というのが主張。

実装は 6 層:

1. **CLAUDE.md 2 層** — global に重みを置き、repo 側はディレクトリ構成と repo 固有の罠だけ
2. **ESLint 極限厳格化** — サイズ/複雑度/型を全部 error。例外は inline でなく設定ファイルに理由付き
3. **テスト** — ルールを pure 関数に切り出し、境界では依存を引数で渡す。MulmoClaude で spec 799 本
4. **重複/デッドコードスキャン** — jscpd / knip。ただし **どちらもビルドを落とさない**
5. **3 OS CI** — PR ごとに ubuntu + macOS、Windows は daily
6. **別モデルのクロスレビュー** — Claude Code が書き、Codex が読む。全 PR に自動発火

### 記事の鍵になる論点

- 「人間のチームなら 3 日で緩和 PR が飛んでくる厳しさが、書き手が AI なら成立する。**lint を緩めるという判断は技術的判断ではなく社会的判断だった**。その社会的コストがゼロになったなら天秤は片側にしか傾かない」
- 「**drain してから ratchet する**」— 既存違反をゼロにしてから warn を error に上げる。「誰も読まない警告リストに 1 件足す」を許さない
- 「**初日からブロックすると回避の作法が育つ**」— jscpd / knip は gate でなく report から
- 「何を守っているか workflow の先頭に書ける。**書けないゲートは、要らないか、要るのに守れていないかどちらか**」
- 「テスト優先順位は **どれだけ静かに失敗するか** で決める。例外を投げる関数は自分で報告してくれる。怖いのはそれっぽい間違った値を返すもの」
- 「新しいテストは対象を壊して赤くなるか確認する。**壊れたコードでも通るテストは、何か別のものをテストしている**」
- 「レビューの価値は 1 回の指摘ではなく **往復の回数**。1 往復のコストが上がると質そのものが落ちる」
- 「ボットの指摘を機械的に全部適用してはいけない。複数走らせると普通に矛盾する」
- 「repo ごとの CLAUDE.md が長くなってきたら、規約が足りないのではなく **揃え方が足りない**」
- 「全自動に進むなら次にやるべきは賢いレビューではなく、**何かあったときに確実に戻せること**」

## Phase 1.5: Saturation Gate

- family: `code-review-best-practices`（taxonomy 未登録だが `_index.md` / MEMORY.md で実運用中）
- N ≈ 11（`docs/research/` の review 系 absorb レポート実数）
- 採用率: 高（Google eng-practices 18 件 / openclaw autoreview 9+2 件 / estie 2 件 / 30-subagents 4 件）
- 判定: **PASS (warning)** — 重複領域だが飽和ではない。delta 計算は SATURATED 候補でないため不要
- Stale-Plan Audit: 直近 3 件が全て 2026-07-27（30 日未満）のため skip

## Phase 2: 判定テーブル

### 前提の設定

dotfiles は Python 中心の harness repo で TypeScript 実装資産をほぼ持たない
（Codex 実測: tracked TS は memory-vec の 4 ファイル、Python は 182 ファイル）。
よって ESLint 系手法は「dotfiles 自身の CI に入れるか」ではなく
**「`rules/*.md` が実プロジェクトへ配布する規約として書けているか」** で判定した。
この枠組みは Phase 2.5 で Codex が妥当と確認。ただし「global rule だけで強制済みとは言えない、
実プロジェクト側の CI / template への翻訳が別途要る」という留保付き。

### Gap / Partial / N/A（Phase 2.5 修正後）

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| G1 | inline `eslint-disable`/`@ts-ignore` を禁止、例外は設定ファイルに理由付き | **Gap（逆行）** | `rules/typescript.md:39` が「やむを得ない場合は `eslint-disable-next-line` + 理由コメントを要求」= 記事と真逆。`protect-linter-config` は設定を守るが inline 抜け道だけ開いていた |
| G2 | 複雑度/サイズを機械強制 | **Partial** | `scripts/policy/structure-check.py:16-20` が `MAX_FUNC_LINES=50 / MAX_NESTING_DEPTH=3 / MAX_FUNC_PARAMS=5 / MAX_FILE_LINES=300` を実装、`settings.json:668` で全 Edit/Write に発火。不足は advisory 止まりという点のみ |
| G3 | drain-then-ratchet + gate/report 段階導入 | **Partial** | `ast-grep-practice/references/cli.md:32-48` に段階的厳格化、`improve-policy.md:715-717` に collect-only 3 サイクル。ただし後者は deprecated doc |
| G4 | テストが本当に赤くなるか確認 | **Gap** | `testing.md` の TDD RED は「先に書く」場合のみ。`autocover/SKILL.md:85` は「mutation testing は任意」 |
| G5 | テスト順序を「静かに失敗する度合い」で決める | **Gap** | `test-engineer.md:53-58` は critical path / recent change 起点、`autocover` は公開 API → エラーパス順 |
| G6 | pure 関数抽出 + 境界の依存注入（`now()`/platform/home dir） | **Partial** | 「I/O と pure function を分ける」原則のみ。DI 対象の具体列挙なし |
| G7 | 「何を守っているか書けないゲートは要らない」 | **ほぼ既存** | `review-consensus-policy.md:353-368`「事前封じ: 被評価者の近道を rubric で塞ぐ」が新 verifier に同等の記述を要求済み |
| G8 | repo CLAUDE.md の厚さ = スタック不統一のサイン | **Mostly covered** | `dead-weight-scan-protocol.md:11-16` が厚さを発火条件にしている。欠けているのは診断語だけ |
| P1 | CI で全 PR に無条件自動レビュー | **Partial** | `team-harness-patterns.md:18-32` に `pull_request` 上の Codex review が**翻訳先として明記されているが未実装** |
| N1 | jscpd / knip を CI に | **N/A** | TS 資産なし。記事自身も「最初にやらなくていい」 |
| N2 | マルチ OS CI（Windows daily） | **N/A** | macOS 専用 harness |

### Already（強化不要）

| 既存の仕組み | 記事の対応手法 |
|---|---|
| `<important if="...">` 条件付きポインタ | 「いつ読むか」を添える（dotfiles の方が条件式で強い） |
| `review-consensus-policy.md:38` 異種シグナル優先 | 「レビュアーは数より種類」 |
| `codex-reviewer.md:16` PASS / NEEDS_FIX / BLOCK | `CODEX VERDICT:` マーカー |
| `commands/review-loop.md:35` `--max-iterations 10` + 状態ファイル | `codex-cross-review` の 5 イテレーション上限 |
| `skills/github-pr/review-response.md:42-46` | `gh-review-loop` のインラインスレッド対応 |
| `review-findings.jsonl` + `session_events.py:417-489` | 「過去の判断を学習させる」 |
| `improve-policy.md` の `rollback_plan` 必須 | 「全自動の前提はロールバック可能性」 |

## Phase 2.5: Codex 批評による修正

Gemini は `IneligibleTierError`（individuals sunset）で恒久使用不可のため **Codex 単独 = degraded**。

Opus の Pass 2 判定を **4 件訂正**（すべて実ファイルで裏付け確認済み）:

| 訂正 | 内容 |
|---|---|
| G2 Gap → Partial | `structure-check.py` の存在を見落とし「散文の規約だけ」と誤判定していた |
| G3 Gap → Partial | ast-grep / improve-policy の段階導入先例を見落とし |
| G7 Partial → ほぼ既存 | `review-consensus-policy.md:353-368` を見落とし |
| G8 Gap → Mostly covered | `dead-weight-scan-protocol.md` を見落とし |

さらに事実誤認 1 件を訂正: github-pr の指摘分類は **PR thread 側が 3 分類**
（`review-response.md:48-72`）、4 分類は `review/SKILL.md:651-663` の内側ループ。両者を混同していた。
P1 の「待ちゼロという核心は満たす」も言い過ぎとして撤回。

### `why-humans-read-code.md` との衝突

dotfiles は 4 日前（2026-07-27、Dex Horthy absorb 由来）に
「gate / loop / reviewer の PASS を『人間がコードを読まなくてよい』の根拠に昇格させない」を codify した。
この記事はその反対側の実践報告にあたる。

**結論: 方針は反転させない。** `why-humans-read-code.md:57-69` の見直し条件は
「代表的変更で設計劣化を高再現率で検出できる verifier の実証」であり、
記事の運用報告・500 コミット・異モデルレビューはその再現率を示す実験ではない。
著者の責任が自分に閉じる（自作 OSS のオーナー）点も全自動を許す根拠にならない。
dotfiles は単一ユーザーでも長期運用する複雑な harness であり、同文書が区別する
「個人の小規模 project」には当たらない（`why-humans-read-code.md:71-75`）。

採るのは **「人間レビューの前に機械的に減らせる欠陥を減らす」部分まで**。
reviewer PASS を人間が読まない根拠にはしない現行の線引きを維持する。

## Phase 3-4: 採用と実装

### 採用 4 件（commit `231adf57`）

| ID | 変更 | ファイル |
|----|------|---------|
| G1 | inline lint 抑制を禁止。エージェントが inline で書いてよい唯一の例外は型テストの `@ts-expect-error`。恒久例外は lint 設定ファイル側に 1 エントリ 1 理由で置き、追加は人間承認・対象ルール 1 件・対象パス最小に限る。この経路でも閾値/ルールの緩和は禁止（ADR-0004） | `rules/typescript.md:39-42`<br>`agents/typescript-reviewer.md:61` |
| G3 | 新しい検査は collect → drain → gate で昇格する。昇格させない判断も同じく正しい（false positive が構造的な検査は collect 据え置き + 「gate ではなくレビュー補助」と明記）。妥協には期限と解消条件を書く。検査導入の段階と hook のクラッシュ時挙動は別軸であることも明記 | `references/harness-stability.md:20-42` |
| G4 | 後から書いたテストは、仕様を壊す代表的な defect を一時的に入れて赤くなるのを見てから戻す。適用は誤った値を静かに返しうる対象に限る | `rules/common/testing.md:34-42` |
| G5 | テストを書く順序は「どれだけ静かに失敗するか」で決める。5 段階の優先順位 + 「先に静かに誤るかを判定し、該当すれば 1 に置く」という分類順を明文化 | `rules/common/testing.md:44-56` |

### Codex Review Gate（2 往復、計 6 件指摘）

| 指摘 | 対応 |
|------|------|
| `agents/typescript-reviewer.md:61` が `eslint-disable-next-line` を要求しており G1 と矛盾 | 同期して書き換え |
| `@ts-expect-error` は型テストで正当な用途があり lint 設定では代替できない | 例外条項を追加 |
| **G5 を置いた `autocover` は `settings.json:193` で `off` = 休眠 skill** | autocover の変更を完全に revert し、`rules/common/testing.md`（`paths` 指定で実プロジェクトのテストに効く）へ移設 |
| P1-P5 が排他的でなく P4 降格を保証しない | 分類順を明文化 |
| `silent-failure-hunter.md:20` は `git diff` 起点で coverage 0% の未変更コードに使えない | 参照を削除 |
| 先例に挙げた `improve-policy.md` は `status: deprecated`（2026-05-03） | 参照を削除、ast-grep のみ残す |
| `typescript.md` の「設定に例外を置く」と ADR-0004「Fix code, not rules」の緊張 | 承認境界（人間承認・最小スコープ・緩和は依然禁止）を明記 |

3 往復目で **PASS**。`task validate-configs` / `task validate-symlinks` ともに exit 0。

### 不採用（ユーザー判断で見送り）

| ID | 理由 |
|----|------|
| G6 | 実際のテスト困難が観測されてから。現時点では原則で足りる |
| G7 | `review-consensus-policy.md` の既存節の再配置以上の価値が薄い |
| G8 | `dead-weight-scan-protocol.md` でほぼカバー済み。診断語の追加だけでは挙動が変わらない |
| P1 | GitHub Actions での Codex 自動レビューは認証・コスト・権限面の新設を伴う。`team-harness-patterns.md:18-32` に翻訳先として記録済み |
| N1 / N2 | 記事の前提（TS プロジェクト / 3 OS 配布）が dotfiles に当たらない |

## Validation-only Follow-up

採用件数に数えないが、記事の framing が露出させた事実:

| 対象 | 内容 |
|------|------|
| `skills/autocover/SKILL.md` | `settings.json:193` で `off`。skill を編集しても挙動は変わらない。**休眠 skill への編集は実効性ゼロ** という一般則として、今後 skill を触る前に `skillOverrides` を確認する必要がある |
| `references/improve-policy.md` | `status: deprecated`（2026-05-03）だが、本文の Rule 群は生きた先例として引用されうる状態。deprecated doc からの引用は「過去の事例」と明示する必要がある |
| `agents/silent-failure-hunter.md:20` | `git diff` 起点のため、未変更コードの棚卸しには使えない。カバレッジ改善の入力としては別途対象指定が要る |
| `agents/typescript-reviewer.md` と `rules/typescript.md` | 同じ論点（lint 抑制の扱い）が 2 箇所に独立して書かれ、片方だけ直すと矛盾する。今回同期したが、この 2 ファイルは今後も対で扱う |

## 教訓

- **Opus 単独の Pass 2 は既存実装を 4 件見落とした**。いずれも「原則は知っているが実装ファイルを見ていない」型の誤り。`structure-check.py` のような hook 実装は `settings.json` 側から逆引きしないと存在に気づけない
- **休眠 skill / deprecated doc への編集・参照は、実ファイルの status 行・settings の override を読まないと検出できない**。Codex がこれを 2 件とも拾った
- 記事の主張が既存方針と正面衝突するとき、採否ではなく **既存方針の見直し条件に照らす**のが正しい扱い。今回は条件（verifier の再現率実証）を満たさないので方針維持、ただし「機械的に減らせる欠陥を減らす」部分は採用、という分割ができた
