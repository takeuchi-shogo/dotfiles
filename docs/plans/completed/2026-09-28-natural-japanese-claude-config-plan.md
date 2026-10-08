# .config/claude の日本語見直し

## Goal

`.config/claude` 配下の自作ファイルの日本語を、`natural-japanese` skill と `references/japanese-ai-prose.md` の基準で読みやすくする。指示の意味は一切変えない。

## Scope

- 対象: `CLAUDE.md`、`rules/`、`output-styles/`、`agents/`、`commands/`、`skills/`（自作のみ）、`references/`。日本語を含む行は約 1.9 万行で、7 割が `references/`
- 対象外: vendor した skill（`natural-japanese`、`stop-ai-slop-jp`、`taste-skill`、`ui-ux-pro-max`、`webapp-testing`）、symlink の `orca-cli`、`skills/**/synced/`。上流と差分ができると更新が壊れるため
- 対象外: 英語の文、コードブロック、inline code、パス、コマンド、frontmatter（`description` は skill のルーティング文なので語を変えると発火が変わる）

## 進め方

層ごとに PR を分ける。PR1 で方針を固め、その判断を後続 PR の委譲指示に反映する。

| PR | 対象 | 日本語行 |
|---|---|---|
| 1 | CLAUDE.md, rules/, output-styles/ | 約 1,100 |
| 2 | agents/, commands/ | 約 1,900 |
| 3 | skills/（自作） | 約 4,800 |
| 4〜6 | references/ を 3 分割 | 約 11,500 |

## 直す基準

- 中国語の技術書から持ち込んだ語（動態拼装、包裹規則、起止境界、片段、本地規則、可調試性など）を日本語に置き換える
- `japanese-ai-prose.md` の AI 臭（「〜することができる」、前置き、ヘッジ、機械翻訳調の受動態）を抜き、行為者を主語にする
- 意味の通らない和英混在（英単語を助詞でつないだだけの文）を、日本語の文として読めるようにする
- 列挙が本質の箇条書き・表はそのまま残す。一律に散文化しない

## 直さないもの

- 悪い例として引用している表現（`derivation-honesty.md` の検出シグナル、禁止語リストなど）
- 他ファイルからアンカー参照されている見出し。変えるなら参照側も直す
- 重大度ラベル（MUST/CONSIDER/NIT）、固有名詞、ツール名

## 検証

- 各ファイルで `natural-japanese` の lint を before/after で比較し、finding が増えていないこと
- `git diff --word-diff` を人間の目で読み、意味が変わっていないこと
- `task validate-configs` / `task validate-symlinks`
- 見出しを変えた場合は旧見出しを grep して参照切れがないこと

## Progress

- [x] PR1: CLAUDE.md, rules/, output-styles/ → #265
- [x] PR2〜6: agents/, commands/, skills/, references/ → #266 にまとめた
- [x] templates/: 直す箇所なし（この計画を閉じる PR で確認）

## Decision Log

- 2026-09-28: 範囲はユーザーが「.config/claude 全体」を選択
- 2026-09-28: vendor skill は対象外。上流更新時の差分衝突を避ける
- 2026-09-29: PR2〜6 は実差分が合計 40 行程度だったため 1 本 (#266) にまとめた
- 2026-09-29: 「政体」は日本語の通常語なので残し、「運行時」「控制面」は「実行時」「制御面」に揃えた。docs/research の過去メモは書かれた時点の記録なので書き換えない

## Outcome

自作の約 280 ファイルを読み、直したのは 16 ファイル・約 50 行。直す価値があったのは、ほぼ harness-books から持ち込んだ 3 ファイル (`rules/codex-delegation.md`、`references/harness-polity-comparison.md`、`references/harness-10-principles-checklist.md`) に残っていた中国語の語 (拼装、纪律、截断、按需、主動など) だった。手書きの部分はもともと `japanese-ai-prose.md` の基準で書かれていて、「〜を行う」を動詞に戻す程度で済んだ。

学んだこと: 渡した語のリストだけでは中国語由来の語を網羅できず、subagent は「按需」「角色」「工程システム」を見落とした。中国語の常用語に広げたパターンで全体を再走査して拾えた。外部の中国語資料を /absorb するときは、取り込み時点でこの走査をかけると後から直す手間が要らない。

残したもの: `rules/typescript.md` の「ペリメータ」(Effective TypeScript 邦訳の表記を未確認)、`skills/obsidian-knowledge/SKILL.md` の「thoughtful な人」(出典の概念名の可能性)。
