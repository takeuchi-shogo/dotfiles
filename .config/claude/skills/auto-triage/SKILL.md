---
name: auto-triage
description: patterns.jsonl の learned 昇格候補を mechanical/advisory/reject/defer に無人分類し dry-run レポートを出す。完全無人 PR 化 (Wave3) の前段 calibration。Triggers: 'auto-triage', 'triage dry-run', '昇格候補を分類', '無人トリアージ'. Do NOT use for: 対話的に昇格して artifact を実際に編集する (use /promote-learnings)、外部記事の取り込み (use /absorb)、コードレビュー (use /review)。
allowed-tools: Read, Bash, Write, Grep, Glob
pattern: learned-triage-classification
---

# Auto-Triage (dry-run)

`patterns.jsonl` の `learned` 昇格候補を**無人で分類**し、レポートだけ出す。
**この skill は読み取り + レポート生成のみ。artifact を一切編集せず、commit/PR/ledger 書き込みもしない。**

## なぜ dry-run か

完全無人で SKILL.md を日次 Edit するのは echo chamber / 誤学習の蓄積 / PR spam を生む
(Codex Spec/Plan Gate + 自前 design doc `docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md`
が独立して「完全自動は誤爆」と結論)。そこでまず**分類精度を 2 週間 calibrate** する。

このループは段階導入:
1. **(now) dry-run 分類** — 候補を mechanical/advisory/reject/defer に分け、根拠付きでレポート
2. **calibration** — 人間がレポートを見て「mechanical 分類が正しいか」を検証、採用分から allowlist を作る。
   裁定は `scripts/learner/calibration-verdict-logger.py log` で記録する (agree/disagree)。
   `... stats` で agreement rate (判断 frontier 指標) と mechanical-confirmed allowlist を集計。
   この裁定記録が Wave3 着手の前提データ (詳細: 上記 design doc の Wave3 entry requirements)。
3. **(Wave3) 無人 PR 化** — allowlist に載った mechanical 種別のみ、決定論ゲート通過後に日次無人 PR

dry-run は state を持たない (ledger に書かない)。分類はスキル改善で変動しうるため、calibration 中は確定させない。
**calibration の裁定記録は dry-run の no-write 保証の外** (書き込み先は agent-memory であって repo artifact ではない)。

## calibration 実測 (2026-06-06 時点)

直近の全 139 件 learned を分類した時点では **mechanical 0 / advisory 129 / reject 5 / defer 5**。
borderline (tournament-mode リンク切れ / typo / drift) も精査したが、すべて「判断が要る」で advisory だった。
**現時点では機械照合可能な mechanical 種別が出現しておらず、Wave3 (無人 PR 化) の発火条件は未充足**。
これは「learned ストアの中身が今は advisory に偏っている」という観測であって Wave3 の恒久放棄ではない
— learned の分布が変われば mechanical が出現しうるため、calibration を継続して出現率を再測定する。

詳細: `docs/research/2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md` の Follow-up

## Workflow

1. **候補を取得**:
   ```bash
   python3 ~/.claude/scripts/learner/extract-promotion-candidates.py
   ```
   `count` が 0 なら「pending な learned はありません」と報告して終了。
   コアは promoted-ledger と照合し未処理のみ・importance 降順で返す (冪等)。

2. **上位 N=10 を分類**: importance 上位 10 件について、各候補を下表のいずれかに分類する。
   分類は `detail` の内容と、既存 artifact の実態 (Grep/Read で確認) に基づく。**推測で膨らませない**。

   | 分類 | 定義 | 判定基準 (客観) | 例 |
   |------|------|----------------|-----|
   | **mechanical** | 決定論で検証できる構造改善 | lint / grep / schema / 重複照合で正否が機械的に決まる | 重複ルールの統合、冗長文の削減、leak 除去、typo、行数超過の分割 |
   | **advisory** | 設計判断系 | 「このルールは妥当か」「優先度」等、主観・文脈依存で機械照合不可 | 新ルールの是非、トレードオフ判断、命名・設計方針 |
   | **reject** | 昇格不適 | 既存 artifact に同等あり / 一般知識 / ノイズ / scope 不明瞭 | already covered、汎用的すぎる知見 |
   | **defer** | 情報不足 | 単発で再現性不明、文脈待ち | 1 回限りの観測、根拠が薄い |

   **mechanical と advisory の線引きが肝** (Wave3 の無人化対象は mechanical のみ)。
   迷ったら advisory に倒す (無人化対象を保守的に狭く保つ)。

3. **echo chamber 観察**: 分類対象の `scope` 分布を集計し、同一 scope / 同じ結論への偏りを記録する。
   同一 scope が候補の過半を占める、または既存 memory に矛盾・反証する learned があれば明記する
   (monoculture 化の早期シグナル。design doc リスク3 の watch 条件)。

4. **レポート出力**: `.triage/$(date +%F)-triage-report.md` に書き出す (`.triage/` は .gitignore 済)。
   ```bash
   mkdir -p .triage
   ```
   レポート構成 (下記テンプレート)。各候補に **key 先頭8桁 / scope / detail 要約 / 推奨 artifact / 分類根拠 / (mechanical なら) 推奨 validation コマンド / 既存重複の有無** を含める。

5. **報告**: 分類内訳 (mechanical N / advisory N / reject N / defer N) と echo chamber 観察を 1 段落で要約。
   レポートパスを示す。**artifact は変更していないこと**を明示する。

## レポートテンプレート

```markdown
# Auto-Triage Dry-Run Report — YYYY-MM-DD

候補総数: N (extract-promotion-candidates) / 分類対象: 上位 M

## mechanical (k件) — Wave3 無人 PR 候補
- `[key8]` scope=<scope>: <detail 要約>
  - 推奨 artifact: <path>
  - 根拠: <なぜ機械照合可か>
  - validation: `<lint/grep コマンド>`
  - 既存重複: <有無 + 該当箇所>

## advisory (k件) — 人間判断必須
- `[key8]` scope=<scope>: <detail 要約> / 推奨: <path> / 判断点: <何が主観か>

## reject (k件)
- `[key8]` scope=<scope>: <理由 (already covered / 一般知識 等)>

## defer (k件)
- `[key8]` scope=<scope>: <保留理由>

## echo chamber 観察
- scope 分布: <上位 scope と件数>
- 偏り: <有無>。反証 learned: <有無>
- watch 条件該当: <yes/no>
```

## Constraints

- **dry-run 厳守**: artifact の Edit、git commit、gh pr create、promoted-ledger 書き込みを**一切しない**。出力は `.triage/` レポートのみ
- **N=10 上限**: 1 回の分類は上位 10 件まで (消化不良防止)
- **保守的分類**: mechanical と advisory で迷ったら advisory (無人化対象を狭く保つ)
- **推測で膨らませない**: `detail` に書かれていない改善案を fabricate しない。既存 artifact は Grep/Read で実在確認してから「重複あり」と判定する

## Anti-Patterns

| NG | 理由 |
|----|------|
| dry-run なのに artifact を Edit する | このスキルの存在意義 (calibration) が壊れる。編集は /promote-learnings (対話) か Wave3 (無人 PR) の役割 |
| mechanical を広く取る | Wave3 で無人 PR 化される対象。広く取ると echo chamber/誤学習リスクが戻る。迷ったら advisory |
| 重複チェックを Grep せず「重複なし」と書く | already covered の見落としは promote-learnings と同じ誤爆。実ファイル確認必須 |
| 候補を 10 件超分類する | レポートが肥大化し人間の calibration 負荷が上がる。上位 10 件に絞る |

Score: 8/10 — dry-run の境界 (編集しない) を Constraints + Anti-Patterns で二重に固めた。mechanical/advisory の線引き基準が calibration の成否を握るが、これは 2 週間の実データで詰める設計。
