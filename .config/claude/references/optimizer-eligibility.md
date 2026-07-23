---
status: reference
last_reviewed: 2026-07-22
---

# Optimizer Eligibility Classifier — 自動最適化の入口分類

> SkillOpt absorb (`docs/research/2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md`) 由来。
> SkillOpt は「正解キーで照合できないタスクには間違ったツール」と明言する。
> /improve が 2026-05-03 に retire した根因は、この入口判別なしに判断タスクを
> 自動最適化して false-positive を量産したこと。artifact を自動最適化の
> 対象に入れる前に、必ずこの分類を通す。

## 2 lane 定義

| Lane | 判定基準 | 最適化方式 |
|------|---------|-----------|
| **objective-checkable** | 正解キーとの機械照合で pass/fail が決まる。人間の再判断なしに採点できる | `holdout_accept_gate.py` の strict gate (playbook 手動起動) |
| **judgement** | 「良い出力」が人間嗜好・文脈適合に依存し、固定の正解キーが存在しない | human-in-loop のみ (`/promote-learnings`) |

**デフォルトは judgement lane。** objective-checkable と証明できたものだけを allowlist に載せる。

## 分類テスト (3 問)

artifact を objective-checkable lane に入れるには、3 問すべて Yes であること:

1. **正解キーが存在するか** — 各 eval ケースに、artifact の作者以外が事前に固定した期待値 (ラベル・期待出力・実行結果) があるか。「LLM judge がスコアを付けられる」は No (judge の代理目的を最適化するだけで Goodhart 化する)
2. **照合が機械的か** — pass/fail 判定がスクリプトで再現可能か (文字列一致・分類ラベル一致・テスト実行・schema 検証)。人間が読んで「良し悪し」を判断する工程が挟まるなら No
3. **ケースが 10 件以上あるか** — `split_holdout.py` で train/holdout に割って両側に意味のある数が残るか (holdout < 5 は split_holdout.py 自体が拒否する)

## Allowlist (objective-checkable lane)

新規追加は**人間承認必須**。この表にない artifact はすべて judgement lane。

| Artifact | 正解キー | 照合方法 |
|----------|---------|---------|
| code-review finding 分類 (reviewer-eval-tuples.json) | failure_mode ラベル | ラベル一致 |
| routing 判定 (model-routing / decision-tables の分岐) | 期待ルート先 | ラベル一致 |
| extraction / classification 系 script (`extract-promotion-candidates.py` 等) | fixture の期待出力 | pytest |
| runnable な hook・script (`scripts/{runtime,policy,lifecycle,learner}/`) | 既存テスト | pytest / exit code |
| validator 選択 (spec-quality-check 等の判定ロジック) | fixture の期待 verdict | pytest |

## 試験分類 (既存 artifact 6 件)

| Artifact | Lane | 根拠 |
|----------|------|------|
| reviewer eval tuples による finding 分類 | objective | failure_mode ラベルが正解キー。3 問すべて Yes |
| `extract-promotion-candidates.py` | objective | fixture 照合の pytest あり |
| golden-check hook | objective | 期待 verdict が fixture で固定可能 |
| `/absorb` skill | judgement | 「取り込む価値があるか」に正解キーなし |
| `/review` skill | judgement | 指摘の妥当性は文脈依存。finding「分類」は objective だが、レビュー全体の良し悪しは judgement |
| `/think` skill | judgement | 思考の深まりは人間しか判定できない |

判断不能ケースは出なかった。今後の運用で **2 回以上「どちらの lane か判断不能」が出たら**、二分をやめて「allowlist 列挙 + デフォルト judgement」方式に縮退する (plan の撤退条件)。

## ルール

- strict gate (`holdout_accept_gate.py`) の対象は objective lane **のみ**。judgement lane への自動最適化は block (improve-policy.md Rule 10/22 と同趣旨)
- 1 つの skill の中に objective な部分 (分類・routing) と judgement な部分 (提案文) が混在する場合、objective な部分だけを切り出して最適化する。skill 全体を objective 扱いしない
- lane 割当の変更・allowlist への追加は人間承認必須。自動プロセス (nightly / AutoEvolve) が本ファイルを書き換えることを禁止する (Rule 22 の延長)

## 関連

- 運用手順: `docs/playbooks/objective-lane-optimization.md`
- gate 本体: `.config/claude/scripts/eval/holdout_accept_gate.py`
- holdout 分割: `.config/claude/scripts/eval/split_holdout.py`
- 設計根拠: improve-policy.md Rule 43/47 (holdout gate)、Rule 23 (metric diversity)
