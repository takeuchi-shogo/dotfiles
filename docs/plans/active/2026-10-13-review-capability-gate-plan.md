---
status: planned
date: 2026-10-13
source: docs/research/2026-10-13-every-harness-layering-absorb-analysis.md
size: M
success_criteria: 拡張子で区別できない差の実例を集め、0 件なら retired、あれば宣言あり / [] / 未設定 の 3 ケースで /review の注入が変わる
---

# review の capability gate (repo ごとの stack 宣言) 導入

## Goal

`/review` が、拡張子では区別できないフレームワーク差 (例: 同じ `.tsx` で Next.js App Router と
Pages Router、同じ `.go` で connect-go と net/http) に応じてチェックリストを読み分けられるようにする。
出典は every.tv Android チームの記事 (2026-10-08) の「capability gate」。
ただし実害が確認できなければ作らない。

## Success Criteria

- T0 で実例の有無が結論づいている (0 件なら `status: retired` で終了)
- 実装する場合: 宣言あり / `[]` / キー未設定 の 3 ケースで、`code-reviewer` に注入されるチェックリストが変わることを確認している
- 宣言と diff の拡張子が食い違うケースで警告が出る

## Scope

- 対象: `.config/claude/skills/review/SKILL.md` の Step 1.2 と「言語固有チェックリスト（プロンプト注入）」節、
  `.config/claude/references/review-checklists/` 配下へのフレームワーク別ファイル追加
- 対象外: review 以外の skill が宣言を読むこと (読み手が増えるなら別 plan)、言語単位の分岐 (拡張子ゲートと `rules/*.md` の `paths:` で足りている)

## Constraints

- 言語は diff の拡張子から推論する現行方式を維持する。宣言は推論できない差だけに使う (宣言は実スタックから drift するため)
- チェックリストが読めないときに黙って省略しない (review SKILL の既存の暗黙フォールバック禁止に揃える)

## Unknowns

答えによって設計が変わるので、T1 でユーザーと決める。

1. 読み手: 宣言を読むのは `/review` だけか。複数なら schema は共有契約になる
2. 置き場所と名前: `<repo>/.claude/capabilities.json` か。本業 repo に commit してよいか (チームの合意が要る)
3. 値の意味論: 記事の区別を採るか。`[]` = その層を持たない (該当観点は指摘せず終了) / キー未設定 = 「未宣言」と出力に明記して拡張子ゲートのみで進める
4. 優先順位: 宣言と diff の実態が食い違ったとき (宣言 `ui: []` なのに `.tsx` が変更された) どちらを信じ、どう警告するか

## Validation

- T0: 本業 repo の直近レビュー結果を読み、見逃し・ノイズの実例を file 単位で記録する
- T2/T3: 宣言を 3 通りに変えた fixture repo で `/review` を実行し、注入されたチェックリスト名を出力で確認する

## Steps

| # | 内容 | 完了条件 |
|---|------|---------|
| T0 | 拡張子では区別できない差による見逃し・ノイズの実例を集める | 実例 2 件以上、または「なし」の結論 |
| T1 | Unknowns 1-4 をユーザーと決める | Decision Log に記録 |
| T2 | schema と `.config/claude/references/review-checklists/<framework>.md` を実装 | 3 ケースで注入結果が変わる |
| T3 | 宣言と diff 拡張子の食い違い検出 | 意図的に食い違わせた diff で警告が出る |

撤退条件: T0 で実例 0 件なら T1 以降に進まず `status: retired`。宣言の更新漏れによる誤注入が 1 回でも
観測されたら、宣言方式をやめて依存定義 (package.json / go.mod) からの推論に切り替える。

## Progress

- [ ] T0
- [ ] T1
- [ ] T2
- [ ] T3

## Surprises & Discoveries

(未記入)

## Decision Log

- 2026-10-13: absorb の Phase 3 でユーザーが採用を選択。Opus は「現状は拡張子ゲートと paths: で足りる」として見送り寄りを提示していたため、T0 を実害確認のゲートにした

## Outcome

(未記入)
