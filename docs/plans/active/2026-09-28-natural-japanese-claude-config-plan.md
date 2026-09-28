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

- [ ] PR1: CLAUDE.md, rules/, output-styles/
- [ ] PR2: agents/, commands/
- [ ] PR3: skills/
- [ ] PR4〜6: references/

## Decision Log

- 2026-09-28: 範囲はユーザーが「.config/claude 全体」を選択
- 2026-09-28: vendor skill は対象外。上流更新時の差分衝突を避ける

## Outcome

（完了時に記入）
