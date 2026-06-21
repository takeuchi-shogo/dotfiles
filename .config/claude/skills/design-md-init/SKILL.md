---
name: design-md-init
description: プロジェクト root に DESIGN.md を 1 度だけ配置 (grill-me で 8 軸の意図抽出 → awesome-design-md exemplar fetch → grilling delta 上書き)。Triggers&#58; 'DESIGN.md 置きたい', 'DESIGN.md 作りたい', 'デザインシステム決めたい', 'design tokens 整えたい', 'スタイルがブレる'. Do NOT use for&#58; 既存 UI overhaul (use redesign-skill), 既存 DESIGN.md 改修 (手動 rm/rename), UI 実装 (use taste-skill / frontend-design).
---

# design-md-init — Project DESIGN.md Bootstrap

## Overview

プロジェクト root に **DESIGN.md を 1 度だけ置く** ための skill。
DESIGN.md は agent が UI を組む前に読む契約物で、色 / 型階層 / spacing / radius / shadow / component rule を plain text で固定する(Google Stitch 由来の概念、`AGENTS.md` がビルド手順なら `DESIGN.md` は見た目)。

このスキルの責務は 3 つだけ:

1. **grill-me に投げる** — `references/design-decision-tree.md` をシードに、47 branch のデザイン意図を引き出してもらう。grill-me 本体には触らない(管理ボールを持たない)。
2. **awesome-design-md から exemplar を 1 件取ってくる** — grilling 結果の vibe profile に最も近い 1 件を WebFetch でコピー、grilling で出た delta(色上書き / フォント差替 / 禁則追記)だけ反映。
3. **agent に読ませる線を引く** — `CLAUDE.md` / `AGENTS.md` の末尾に固定の "## Design" 段落を append。

## Prerequisites

- このプロジェクトに DESIGN.md がまだ無いこと(あれば abort)
- インターネット接続(`github.com` / `raw.githubusercontent.com` へ WebFetch)
- Claude Code セッション(Skill tool で grill-me を呼ぶ)

## Execution Steps

### Step 1 — 既存 DESIGN.md チェック

```
test -f ./DESIGN.md
```

存在したら **即 abort**。以下のメッセージを出して終了:

> `./DESIGN.md` がすでに存在します。再生成するには手動で `rm ./DESIGN.md`(または `mv DESIGN.md DESIGN.md.old`)してから再実行してください。

理由: DESIGN.md は契約物で silent 上書き禁止。merge mode は意図的に持たない(YAGNI、必要になったら別 skill で `/design-md-revise` を切る)。

### Step 2 — grill-me 起動

`Skill(mattpocock-skills:grill-me)` を以下のシード付きで起動する。シードは `references/design-decision-tree.md` を読み込んで args に展開する:

```
このプロジェクトに置く DESIGN.md の中身を決める。以下の 47 branch を
一問ずつ relentlessly に grill してください。各 branch に推奨デフォルトを
書いておきました(default を accept する場合は次の question に進んで OK)。

<design-decision-tree.md の中身を貼る>

最終ゴール: 全 47 branch の resolution と、特に下記 5 軸の vibe profile を確定:
  - vibe word (Linear / Stripe / Notion / Vercel / Airbnb / Apple / Brutalist / Editorial)
  - density (airy / balanced / dense)
  - variance (symmetric / asymmetric / chaotic)
  - motion (static / fluid / cinematic)
  - mode (light / dark / both)
```

grill-me は一問ずつ進めるので、ユーザーが default を accept していけば 5–10 分で抜けられる。こだわりがあれば 47 全部詰められる。

### Step 3 — Vibe profile 抽出

grilling 完了後、回答を集約して以下の structured profile を作る:

```yaml
vibe_word: linear           # 何に近いか(exemplar マッチ用)
density: balanced           # airy / balanced / dense
variance: asymmetric        # symmetric / asymmetric / chaotic
motion: fluid               # static / fluid / cinematic
mode: dark                  # light / dark / both
neutral_base: zinc          # zinc / slate / stone / warm-gray
accent_count: 1
accent_hue: blue
display_font: Geist
body_font: Geist
mono_font: Geist Mono
banned_aesthetics:
  - ai-purple-neon
  - inter-overuse
  - glassmorphism
brand_evoke: [linear, notion]
brand_avoid: [generic-saas, gradient-heavy]
deltas:                      # exemplar に上書きする項目
  - "primary accent → #2563EB (user override)"
  - "ban Inter completely (user constraint)"
```

### Step 4 — Exemplar 一覧取得

`VoltAgent/awesome-design-md` repo の README を WebFetch:

```
WebFetch("https://github.com/VoltAgent/awesome-design-md", "73 件すべての DESIGN.md ファイル名 / 由来ブランド / vibe 系統(minimalist / editorial / brutalist / dashboard / consumer / etc)を抽出して列挙する。各エントリの raw URL も併記")
```

WebFetch 失敗時の対処:

> `awesome-design-md` の README 取得に失敗しました。`gh repo view VoltAgent/awesome-design-md` でリポジトリ生存を確認、ネットワーク疎通を確認してから再実行してください。

### Step 5 — Top 3 提示 + ユーザー選択

vibe profile と README 一覧を突き合わせ、スコアリング:

- vibe_word 完全一致 +5
- density / variance / motion / mode の各軸一致 +1
- banned_aesthetics に該当する exemplar(例: AI purple neon を ban しているのに Stripe Hero 系を選ぶ等) は除外

上位 3 件をユーザーに提示:

```
Top 3 matches:
1. stripe.md — Vibe: minimalist + balanced + symmetric + light. Match: 8/10.
2. linear.md — Vibe: minimalist + balanced + asymmetric + dark. Match: 9/10.
3. vercel.md — Vibe: minimalist + airy + asymmetric + dark. Match: 7/10.

どれを base にしますか? (番号で回答)
```

選ばれた 1 件で次へ。

### Step 6 — Exemplar 取得

```
WebFetch("<選ばれた exemplar の raw URL>", "ファイル全文をそのまま返す")
```

失敗時: 1 回 retry → なお失敗なら **Top 2 の次候補に自動切替**(再 fetch)→ それも失敗なら abort。

### Step 7 — Delta 適用して書き出し

取得した exemplar 本文に対して、Step 3 の `deltas` リストを反映:

- 色値の上書き(`#XXXXXX` の置換)
- フォント宣言の差替(`Inter` → `Geist` 等)
- 禁則追記(`## Anti-Patterns` セクションに新規行を append)
- brand_evoke / brand_avoke の言及があれば `## Brand Voice` セクションに追記

最終形を `<project>/DESIGN.md` に Write。

### Step 8 — CLAUDE.md / AGENTS.md に参照行追記

両方をチェック、無ければ新規作成、あれば末尾に追記。
**既存ファイル内に文字列 `DESIGN.md` が含まれていたら append を skip**(冪等)。

追記内容(固定、CLAUDE.md / AGENTS.md 共通):

```markdown

## Design

This project has a `DESIGN.md` at the root. **Before any UI work**
(components, pages, styles, copy, layout), read `DESIGN.md` and
follow its tokens, type scale, spacing, and component rules.
Do not introduce styles, fonts, or colors that contradict it.
```

### Step 9 — 完了報告

最後に以下を 1 段落で報告:

- 採用した exemplar 名 + 適用した delta の件数
- 触ったファイル(`DESIGN.md` 新規 / `CLAUDE.md` 追記 or 新規 / `AGENTS.md` 追記 or 新規)
- 次に UI 作業を始める時、agent は CLAUDE.md/AGENTS.md 経由で DESIGN.md を読む

## Failure modes

| 事象 | 挙動 |
|---|---|
| 既存 DESIGN.md | abort、手動削除案内 |
| README WebFetch 失敗 | abort、疎通確認案内 |
| 選択した exemplar fetch 失敗 | 1 回 retry → next best → 全失敗で abort |
| vibe profile が極端で match 候補なし | 中立 default(`vercel.md`)を提示、ユーザー accept で続行 |
| grill-me 中断 | DESIGN.md 配置せず終了、再実行時は Step 1 から |

## Non-goals (意図的に持たない)

- 既存 DESIGN.md の diff / merge / 部分更新
- decision log の出力(必要なら `/decision` skill 使う)
- Codex からの直接起動(grill-me が Claude Code 専用)
- 73 exemplar のローカル cache / vendor(upstream に一任)
- DESIGN.md に従っているかの lint / hook(YAGNI、3 回事故るまで待つ)
