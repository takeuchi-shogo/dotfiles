# Objective-lane Skill Optimization — 運用手順

SkillOpt 型の strict gate で objective-checkable な artifact のみを実証的に改善する。
**手動起動専用**。nightly / AutoEvolve / cron からは呼ばない (Build to Delete — /improve の轍を踏まない)。

- 入口判別: `.config/claude/references/optimizer-eligibility.md`
- gate 本体: `.config/claude/scripts/eval/holdout_accept_gate.py`
- 由来: `docs/research/2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md`

## 前提

- 対象 artifact が optimizer-eligibility.md の **allowlist に載っている** (載っていなければ先に 3 問テスト + 人間承認で追加)
- 正解キー付き eval ケースが 10 件以上ある
- 改善は 1 回につき **1 編集** (improve-policy.md Rule 20 単一変更規律)

**gate の保証範囲 (SkillOpt と同じ限界)**: gate は渡された eval 結果 JSON の数値だけを判定する。
その結果が「正しい artifact バージョンで正直に実行された」ことは検証できない — 正解キーと
eval 実行の正直さに全面依存する (SkillOpt 論文自身が明言する前提)。eval の実行と結果ファイルの
生成は必ず操作者自身が行い、候補編集を提案した agent に結果ファイルを作らせない。

## 手順

### 1. train/holdout 分割

```bash
cd ~/.claude/scripts/eval
python3 split_holdout.py --input <tuples.json> --seed 42
# → *-train.json / *-holdout.json。holdout < 5 なら script が拒否する (データ不足、ここで中止)
```

holdout ケースは**候補編集の設計に使わない** (見たら contamination)。

### 2. baseline 計測

split_holdout.py の出力 (`tuples` キー = テストケース定義) と gate の入力 (`results` キー = 実行結果) は
**別 schema**。中間変換スクリプトは無く、artifact ごとに eval を手動実行して results ファイルを作る
(tuples の各ケースを実行し、正解キーとの照合結果を `pass` に、第 2 指標を `metrics` に記録する)。

現行の artifact で train / holdout 両方の eval を実行し、結果を gate 入力 schema で保存する:

```json
{"description": "baseline train", "results": [{"id": "t1", "pass": true, "metrics": {"finding_precision": 0.8}}]}
```

- `pass`: 正解キーとの機械照合結果
- `metrics`: 第 2 指標。pass_rate (primary) + secondary の**計 2 独立指標**で判定することで Rule 23 (metric diversity, 最低 2 指標) を満たす。secondary は pass_rate と独立な指標にする (例: finding_precision, false_positive_rate)

### 3. 候補編集の提案

- **train セットの失敗ケースのみ**を見て、artifact への編集を 1 つ提案する
- 過去の reject を再提案しない: `scripts/eval/results/rejected-edits.jsonl` の同一 lane エントリを提案プロンプトに注入する (SkillOpt rejected-edit buffer)
- 編集は bounded に: add/delete/replace いずれか 1 箇所。全面 rewrite 禁止

### 4. candidate 計測

編集後の artifact で train / holdout を再実行し、同 schema で保存。

### 5. gate 判定

```bash
python3 holdout_accept_gate.py \
  --baseline-train bt.json --baseline-holdout bh.json \
  --candidate-train ct.json --candidate-holdout ch.json \
  --secondary-metric finding_precision:higher \
  --edit-id <短い編集説明 slug> --lane <allowlist の lane 名>
```

| verdict | 条件 | アクション |
|---------|------|-----------|
| accept (exit 0) | holdout pass_rate が**厳密向上** (tie は reject) かつ secondary 非劣化 | 編集を commit (通常の PR フロー) |
| reject (exit 1) | tie / 劣化 / overfitting (train↑ holdout↓) / secondary 劣化 | 編集を revert。buffer に自動記録済み → 次の提案で再提案しない |
| error (exit 2) | 入力不正 (空 results / ID 不一致 / metric 欠落) | 入力を直す。gate を緩めない |

### 6. 反復 or 終了

- accept が出たら 1 サイクル終了。続けるなら手順 3 から (連続実行は最大 3 編集/日)
- **3 試行連続で +1pp 以上の改善が出ない** → この artifact への最適化を中止 (plan の撤退条件)。gate 側を緩める調整は禁止 (Rule 22)

## 禁止事項

- judgement lane の artifact (absorb / review / think 等) にこの手順を適用する
- holdout 結果を見てから候補編集を作り直す (contamination)
- gate script・eligibility allowlist を自動プロセスが書き換える
