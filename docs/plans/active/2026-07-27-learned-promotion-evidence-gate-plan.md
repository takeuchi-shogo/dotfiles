---
title: "learned 昇格に観測件数と source health のゲートを入れる"
date: 2026-07-27
status: planned
scale: M
origin: docs/research/2026-07-27-estie-dialect-reviewer-absorb-analysis.md
---

# learned 昇格の証拠ゲート

estie の「自社レビュー履歴から方言レビュアーを作った」記事 absorb の採用 2 件。

現状の `promote-learnings` は候補を `importance` (float, 既定 0.5) の降順で出すだけで、**その learned が過去に何回観測されたか**を持たない。また抽出元のログが生きているかを問わない。dotfiles ではこの 2 つ目が既に現実化している — memory の記録によれば improve-policy の Friction→Eval Loop の producer が停止していた (errors.jsonl 16 日 / friction 25 日)。**枯れたログから「もっともらしい learned」を昇格できる状態**になっている。

記事の該当主張 (verbatim):

> 各項目に「この指摘は実績◯件」という分析結果を必ず添える (中略) 大事なのは、AIにそれっぽい規約を作らせることではなく、過去に本当に出ていた指摘と、その強さを残すことです

> この方法が効くのは、レビューの中身が伴っている場合だけです。レビューが形骸化していたら、いくらデータを集めても意味のある規約は抽出できません

## 責務の分離 (Codex 指摘)

決定論的に算出できるものは script、判断は skill に置く (CLAUDE.md「static-checkable rules は mechanism に寄せる」)。

| 層 | ファイル | 責務 |
|---|---|---|
| 算出 | `.config/claude/scripts/learner/extract-promotion-candidates.py` | 観測件数と source health を計算して候補に付与する |
| 判断 | `.config/claude/skills/promote-learnings/SKILL.md` | 昇格の停止・例外承認を判断する |
| 表示のみ | `.config/claude/skills/auto-triage/SKILL.md` | 同じ値を dry-run レポートに出す。**唯一のゲートにはしない** |

## P1: 観測件数の算出と付与 (script)

`extract-promotion-candidates.py` に、候補ごとの独立観測件数を付ける。

- `importance` に**混ぜない**。別フィールドとして併記する (混ぜるとスコア 1 本に潰れて根拠が消える)
- 「独立」の定義: リトライによる重複を 1 件に畳む。同一セッション内の連続発生は 1 件とみなす
- 遡れること: 各件について生ログの時刻・ID を保持し、昇格後の artifact から元ログに戻れるようにする

## P2: 昇格閾値 (skill)

Codex 推奨をそのまま採る。単一ユーザーの dotfiles は team よりサンプルが圧倒的に少ないため、team 事例の実数 (estie は「過去のレビューコメント 18 件」等) をそのまま持ち込まない。

| 条件 | 扱い |
|---|---|
| 180 日以内に独立観測 **3 件以上** かつ **2 セッション以上** | 通常昇格 |
| 独立観測 **2 件** | provisional 昇格。**60 日の失効期限**付き。期限内に 3 件目が来なければ失効させる |
| 独立観測 **1 件** | 原則昇格しない。例外は security 境界 / 再現済みの破壊的障害など**強い因果証拠**がある場合のみ、明示判断として記録 |

昇格した artifact 本文には件数を根拠として残す (記事の「実績◯件」に相当)。

## P3: source health の事前検査 (script が測り skill が判断)

件数だけを見ると Goodhart になる (Codex 指摘)。次の 4 つを見る。

| # | 見るもの | 落ちたときの意味 |
|---|---|---|
| a | upstream producer の**鮮度と継続性** — 最終書き込み日時、書き込み間隔の途切れ | producer が死んでいる。ここから昇格してはいけない (errors.jsonl 16 日停止の実例) |
| b | 候補から**生ログの時刻・ID・根拠に遡れる**か | 遡れない候補は検証不能。昇格の根拠にならない |
| c | リトライ重複でない**独立性**、および受容・解決などの**結果シグナル** | 同じ失敗の再試行を N 件と数えていないか。指摘が受容されたのか放置されたのか |
| d | 各 source の**少数サンプルの人手監査** — 欠損 / parse error / 単一 emitter 偏重 | 1 つの emitter だけが吐いているログは全体の傾向ではない |

d は自動化しない。昇格セッションのたびに数件だけ人が見る。

## 実装順序と撤退条件

P1 → P3 → P2 の順。**P2 (skill 側の gate 文言) を先に入れてはならない** — 参照先のフィールドが存在しない gate は、環境に無い検査手段を指定した rubric と同じで silently に飛ぶ (`references/scope-governor.md` および `skill-creator/instructions/testing-evaluation.md` の Rubric authoring で今日 codify した失敗モード)。

**撤退条件**: P1 実装後、3 件以上の独立観測を満たす候補が全体の 5% 未満だった場合、単一ユーザーの観測量では閾値 3 が機能しない。その時点で閾値を下げるのではなく、**learned 昇格ループそのものの有効性を再評価する** (memory `project_friction_detection_loop.md` の旧 friction ループ退役と同じ判断。件数を成否の指標にしない = `feedback_skill_audit_conflict_metric.md`)。

## 検証

- P1/P3: `extract-promotion-candidates.py` を実データに対して実行し、既存候補に件数と health が付くことを確認する。単体実行の成功を発火の証拠にしない (`references/harness-stability.md`)
- P2: `/promote-learnings` を実際に起動し、health が落ちている source から昇格が止まることを確認する
- `task validate-configs`

## 記事から Reject したもの

- **MUST/blocker を「実バグと破壊的変更」だけに限定し設計の好みを 1 段下げる** — dotfiles の MUST は security + Golden Principles 違反を含む設計。estie 版に狭めると security escalation が弱くなる (Codex 同意)
- **最上位 severity に修正コード必須** — 現行 `code-reviewer.md` は BLOCK (MUST あり) で suggestion block を要求済。全 severity に無差別にコード修正を強制するより現行が適切 (Codex 同意)
- **レビュー履歴マイニング本体 (収集→集計→蒸留→6 役割並列レビュアー)** — team 前提 (複数リポジトリ / 複数レビュアー / 7 年の履歴)。単一ユーザーに元データがない
