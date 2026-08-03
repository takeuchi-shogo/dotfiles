---
source: "https://zenn.dev/torukona/articles/4b6f0bfe083d2b"
date: 2026-08-03
status: analyzed
adopted: 0
family: multi-agent-orchestration
---

## Source Summary

**主張**: ループを回すこと自体を目的に WF を組むのではなく、実 PJ と同じような形で体制を構築し、統制をかける仕組みを構造化することで、結果的に自律実行ができている。Copilot がこれを「構造化ループエンジニアリング (Structured Loop-Engineering)」と命名した。著者 torukona は旅行アプリ「タベリエ」を Claude Code のみで開発した実例をもとに、フェーズ1 (1対1の壁打ち) → フェーズ2 (PM を立てて design/imple/QA に分業) → フェーズ3 (UI/UX・マーケ・法務の専門職を増員) → フェーズ4 (重大インシデントと統合役の配置) という体制の段階的拡張を記述している。

**手法**:
- 人間の窓口を単一 PM エージェントに固定する
- 統括役 (PM) が実作業を持たない規律を敷く
- design/imple/QA のロール分業
- 非エンジニア職能 (UI/UX・マーケ・法務・ブランディング・ステージング) のエージェント化
- 横断ナレッジの knowledge-base への集約
- 設計開発標準の明文化
- 欠陥発生 → 振り返り → 標準更新 + 横展開調査
- インシデント由来ルールを decisions/ に codify
- 改善案を専用担当に検討させる
- 外部配布 URL を実ブラウザでボタンまで押して確認する

**根拠**: 実害の記録2件。(a) ローンチ当日、X の告知に載せた URL が `#` 抜きの実パス `/about` だったため、初日約50人が訪問したが「無料で始める」ボタンを押しても画面が変わらず多くが離脱した。真因はハッシュルーターと実パスの継ぎ目 (`navigate('#/')` が pathname 側の正規化に負ける)。(b) PM (統括役) 自身が「軽微な修正だったから」という理由で直接コードを書き、QA 担当のレビューを通さずに報告した。品質が落ち工数をロスした。記事の原文: 「なぜルールを守らなかったのかを聞いたところ、『軽微な修正だったから』という回答がありました。人間の PJ でも見た気がします」

**前提条件**: 常設のプロダクト開発チーム相当の体制、個人開発、マネタイズ視野、Claude Code のみ。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | 人間の窓口を単一PMエージェントに固定 | Already | `references/cmux-ecosystem.md:100` の hub-and-spoke (conductor = メイン Claude) |
| 2 | 統括役が実作業を持たない規律 | Already | `references/model-routing.md:12` / `references/agent-orchestration-map.md:25-31` |
| 3 | design/imple/QA のロール分業 | N/A (前提差) | `references/subagent-delegation-guide.md:40` はタスク分割をロールでなくコンテキストで決めると明示的に逆 |
| 4 | 非エンジニア職能のエージェント化 | N/A (棄却済み) | 2026-05-02 `30-subagents-2026-absorb-analysis.md` で business team 15個を out_of_scope として棄却済み |
| 5 | knowledge-base への横断ナレッジ集約 | Already | `references/knowledge-pyramid.md` の4層昇格パイプライン + `CLAUDE.md:33-36` |
| 6 | 設計開発標準の明文化 | Already | `rules/{go,python,react,rust,test,typescript,proto}.md` / `references/design-stance.md` |
| 7 | 欠陥→振り返り→標準更新+横展開調査 | N/A (意図的設計) | `references/lessons-learned.md` と `references/failure-escalation-protocol.md:19` で前半は exists。横展開は `references/scope-governor.md:41` が意図的に限定 |
| 8 | インシデント由来ルールを decisions/ に codify | Already | `references/decision-journal.md` + `skills/decision/SKILL.md` |
| 9 | 改善案を専用担当に検討させる | Already | `skills/dispatch/SKILL.md:150` self-improve preset |
| 10 | 外部配布URLを実ブラウザでボタンまで押して確認 | N/A (プロダクト側の責務) | 該当機構は not_found。`skills/webapp-testing` は変更した UI の verify、`skills/check-health` は参照切れ検出であり用途が異なる |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | `references/model-routing.md:12` (メインが全部自前でやらない規律) | PM が「軽微な修正だから」と規律を破ってコードを書きレビューを迂回した | メイン直編集を hard-block する判定材料 | 強化不要 (Phase 2 では「強化可能」だったが Codex 批評で降格) |
| S2 | `references/scope-governor.md:41` (同diff内の兄弟インスタンスは blocker、未変更サーフェスは follow-up) | 欠陥の横展開調査を組織的に行っていない | 常に全横展開調査を強制するルール追加 | 強化不要 (Phase 2 では Partial だったが Codex 批評で降格) |

## Integration Decisions

### Gap / Partial

(該当なし。Pass 1 で Gap 0 件、Partial 0 件。)

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | メイン直編集の hard-block 化 | スキップ | Sonnet 累計509件・8/2単日17件の起動実績があり「現在の問題」とは確認できない。既存 hook (SessionStart 委譲リマインド、Agent 呼出記録、探索スパイラル検出) はあるが、小修正まで阻害する hard-block は不要 |
| S2 | 横展開調査の常時強制 | スキップ | 現行ルールは「調査と当該PRへの混入を分ける」設計であり、常設プロダクトチームの「必ず全横展開」は継続的バックログ・オーナー・リリース責任がある前提で成立する。単発 harness で強制すると scope 発散と検証不能な修正を招く |

**採用: 0 件**

## Plan

(採用0件のため実装タスクなし。詳細は「Validation-only Follow-up」を参照。)

## Saturation Gate (Phase 1.5)

- family: `multi-agent-orchestration` (N=17+)
- 判定: **PASS (warning)** — 直近3件の採用実績が 採用4 / 採用1 / 採用1 で採用率 20% 超
- Step 4.5 連続 reject trend: 未発火 (直近2件が連続採用0ではない)
- Step 7 Stale-Plan Audit: 同 family の最新3件 (2026-08-02, 2026-07-27, 2026-07-25) が全て30日未満 → audit skip

## Phase 2.5 (マルチモデル批評)

- Gemini: **失敗**。`IneligibleTierError: This client is no longer supported for Gemini Code Assist for individuals` (individuals sunset、memory `feedback_gemini_cli_sunset.md` の3度目の再確認)。Codex 単独批評となった。
- Codex 呼び出しの失敗と復旧: 1回目と2回目の `codex exec` はプロンプトを引数のヒアドキュメントで渡したため `Reading additional input from stdin...` で stdin 待ちのままブロックし、Bash tool の 600秒上限で kill された。**Codex 側の no-progress ではなく呼び出し方の誤り**。3回目にプロンプトをファイル化して `cat prompt.txt | codex exec ... -` の stdin 経由に変えたところ成功 (101,815 tokens)。

Codex の verdict (verbatim):

> 結論：**採用ゼロでよい**です。記事の二つの事故への対策は、dotfiles 側では既にあるか、プロダクト固有に閉じるべきです。
>
> - Q1: **(c) YAGNI。ただし stale な feedback は再評価対象。**
>   未発火メモは 5/23 の観測ですが、現行 ledger では Sonnet が累計 **509 件**、8/2 だけでも **17 件**起動されています。現在の問題とは確認できません。
>   既存 hook も SessionStart の委譲リマインド、Agent 呼出の記録、探索スパイラル検出を持ちます。一方で「メイン直編集」を安全に hard-block する判定材料はなく、強制すると小修正まで阻害します。ルール追記・hook増設とも不要です。
>   むしろ古い feedback を現状不変の根拠にしないことが重要です。Cursor は「Sonnet が2回詰まった時」の経路なので、利用数が少ないこと自体は失敗ではありません。
>
> - Q2: **限定を維持。覆さない。**
>   現行ルールは同一 diff の兄弟バグを blocker として洗い、未変更サーフェスは follow-up に分離しています。これは「横展開を調べない」のでなく、**調査と当該PRへの混入を分ける**設計です。
>   常設プロダクトチームの「必ず全横展開」は、継続的なバックログ・オーナー・リリース責任がある前提。単発 harness で強制すると scope 発散と検証不能な修正を招きます。
>
> - Q3: **常設ロール、PM/実装分離の組織化、常時マーケ・法務、ローンチ運用は N/A。**
>   (a) の「軽微だからQA省略」は、既にサイズ別 workflow と Review/Verify、Completion Gate でカバーされています。
>   (b) の CTA は唯一の示唆ですが、global harness ではなく、実際に公開するプロダクトの deploy/release checklist に置くべきです（URL到達＋主要CTAの実行確認）。dotfiles に常設化する理由はありません。
>
> 一番の批評点は、観測を持つ harness なのに古い失敗メモを現行の失敗として扱いかねない点です。新しい統制より、既存 telemetry で「まだ失敗しているか」を先に再判定する方が筋が良いです。

## Validation-only Follow-up

記事の framing (「規律を書いても『軽微だから』で守られない」) で dotfiles を照らした結果、**dotfiles 側の「守られていない」という記録の方が stale だった**ことが露出した。

- 対象: memory `feedback_sonnet_cursor_underused.md` (2026-05-23 記録、71日前)
- 記録内容: 「Sonnet subagent と Cursor CLI を全然呼んでいない」「model-routing.md に経路定義はあるが実行ルーチンに組み込まれていない」
- 実測 (2026-08-03、`~/.claude/agent-memory/learnings/agent-invocations.jsonl`): `model=sonnet` が累計 **510 件**、2026-08-02 単日で **18 件** (うち1件は本 absorb の Explore 起動)。Cursor は累計 **7 件**
- 判定: Sonnet 側の主張は**事実に反する (解消済み)**。Cursor 側は 7 件だが `CLAUDE.md:17` が「Sonnet が 2 回詰まった実装だけ」の限定経路と定義しているため、少数であること自体は失敗ではない
- 対応 (実施済み): memory 本文冒頭に「現状 (2026-08-03 実測で更新)」節を追加し、Sonnet 側の解消と「この memory を『今も守られていない』の根拠に使わないこと」を明記。`MEMORY.md` の索引1行も同様に訂正
- なお Codex の数値 (509件/17件) は独立に検証し、私の Explore 起動1件分の差で一致した

## 教訓

1. 採用0でも記事の framing は資産になる — 「規律が守られない」という記事の切り口が、dotfiles 側の「守られていない」という**記録の staleness** を露出させた。記事の主張の正否とは別の経路で価値が出た
2. telemetry を持つ harness では、memory の失敗記述を新しい統制の根拠にする前に ledger で再判定する (Codex の締めの指摘)
3. ツール失敗の原因を相手側に帰属させない — `codex exec` の2回の失敗は `Reading additional input from stdin...` という自分の出力に原因が書かれていた。stderr を `2>/dev/null` で捨てていたため1回目は原因が特定できなかった
