---
source: "https://tech.every.tv/entry/2026/10/08/121837 (株式会社エブリー Android チーム 岡田「ハーネスの一元管理」, 2026-10-08)"
date: 2026-10-13
status: integrated-partial
family: none
---

<!-- 取得経路: defuddle で全文 markdown を取得 -->

## Source Summary

**主張**: ハーネスを repo ごとにコピペして各 repo で効かせようと具体化するほど、同名ファイルが分岐する(同名 5 ファイルの差分が 1,632 行)。大きな技術差は plugin の層で吸収し、小さな差は capability gate で吸収する。結果は -5,254 / +884 行。

**手法**:
- plugin を層に分ける(Kotlin 共通 → Android 共通 → ドメイン)。境界の基準は「その層を使う repo のうち、最も技術が少ない repo でも成り立つか」
- capability gate: repo 内の JSON で `reference/<tech>.md` を読み分ける。`[]` は「層なし」で、指摘せず終了する。未設定は「未適用」として通常どおりレビューする
- 却下した案: 共通部分だけ共有する案、組み合わせごとに配布物を作る案

**根拠**: 同名 5 ファイルの差分行数(1,632 行)と、一元化後の行数増減(-5,254 / +884)。

**前提条件**: 複数 repo に同じハーネスを配る組織。dotfiles は 1 人・1 配備元なので、前提が一部成り立たない。

## Saturation Gate

family なしで PASS。harness-engineering family のキーワードは harness と hook の 2 語のみで閾値 3 に届かない。agentic-instruction-following は CLAUDE.md の 1 語のみ。N=0 のため Stale-Plan Audit の対象外。

## Gap Analysis (Pass 1: 存在チェック)

Phase 2 と Phase 2.5 の修正を反映した後の判定。

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| M1 | 同名 diff で drift を計測する | N/A | `~/.claude` は実ディレクトリだが、skills / agents / rules / references / scripts は home-manager の `mkOutOfStoreSymlink` で nix store を経由して dotfiles の作業ツリーに解決する (`nix/home/default.nix:5` の `outLink`)。配備はコピーではなく live なので、作業ツリーとの `diff -qr` は全件 0 件(2026-10-13 実測)。当初「スナップショット型でずれうる」と判定したのは、symlink 連鎖を 1 段しか辿らなかった誤り |
| M2 | 層分割と境界基準 | Partial | global CLAUDE.md、rules/common(常時)、言語別 rules(`paths:` 条件ロード)、project CLAUDE.md の層はある。ただし「global 層が前提にしてはいけないもの」の契約が無かった |
| M3 | capability gate | Partial | review は diff の拡張子でチェックリストを選ぶ(SKILL.md:157, 250)。project の reviewer data / learnings は存在するときだけ注入する(SKILL.md:273)。宣言ファイルは無い。宣言は実スタックから drift する(Gemini の指摘)ので拡張子推論を優先し、宣言の対象は拡張子に現れないフレームワーク差だけに絞る |
| M4 | `[]` と未設定の区別 | N/A | 対象となる設定が無い。近い規律として、review のチェックリスト読込失敗時は暗黙フォールバックを禁じている |
| M5 | 却下案の記録 | Already(強化不要) | commit skill が `rejected()` の理由を必須にしている(commit/SKILL.md:74)。review は設計根拠を要求する(review/SKILL.md:218) |

集計: Gap 0 / Partial 2 / Already 1 / N/A 2。

## Phase 2.5 記録 (外部批評)

Codex (gpt-5.6-terra, read-only, xhigh, `project_doc_max_bytes=0`) と Gemini (agy) に並列で批評させた。

**Codex の主張 1**: 「実環境では `~/.claude` は symlink ではありません(`test -L`=false、`diff -qr`=184 件)」。
→ ディレクトリ構造の指摘は正しかった。ただし配備対象ディレクトリの差分は 0 件で、184 件は実行時 state を含む数と推定する(未確認)。M1 は N/A を維持した。

**Codex の主張 2**: 「`rules` の `paths:` を稼働中のレイヤーと数えるのは危険で、repo 自身の資料は自動ロード未実装と記します(cwd-routing-matrix.md:36)」。
→ 根拠にした資料自体が stale だった。PR #245 (2026-09-07, 4a06db95) で `paths:` 条件ロードは復活済み。Codex の指摘は棄却し、資料側を直した(下記 2)。

**Codex の優先順位**: P0 配備 drift、P1 scope 分類、P2 実例が出た場合だけ capability JSON。

**Gemini の指摘**: rulesync / submodule 共有の事例、plugin の update lag、宣言と実スタックの drift、どの reference がロードされたか観測しにくいこと、plugin skill と project skill の優先順位、代替としての `paths:` frontmatter。楽観バイアスを割り引き、採用したのは drift と可観測性の指摘だけ。

## Integration Decisions

Phase 3 でユーザーが 4 項目すべてを採用した。

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| M2 | Skill scope 判断に第 3 分類を追加 | 採用 | global 層が前提にしてよい範囲の契約が欠けていた |
| M3 | capability gate | 採用(plan 化) | 実例が出るまで実装しない。Codex の P2 に沿う |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| M5 | 却下案の記録 | スキップ | 強化不要 |

## 実施内容 / Validation-only Follow-up

| # | 内容 | 場所 | 種別 |
|---|------|------|------|
| 1 | MEMORY.md「プロダクト開発」節の `/init-project --team` 案内を、APPLY.md の手動手順へ差し替える。`/init-project --team` は 2026-09-23 に退役済み | `templates/team-project/APPLY.md:34` | 検証で見つけた stale 修正 |
| 2 | `cwd-routing-matrix.md` L11 と L36 以降の「rules は自動ロードされない」を、PR #245 以降の `paths:` 条件ロードの実態に直す。経緯は #207 → #235 → #245 | `.config/claude/references/cwd-routing-matrix.md` | 検証で見つけた stale 修正 |
| 2b | 同じ旧前提 (「rules は自動ロードされない」「`~/.claude/rules/` は存在しない」) を書いていた残り 2 箇所。Codex 再レビューの BLOCK で判明 | `nix/home/default.nix:115` のコメント、`.config/claude/agents/typescript-reviewer.md:25` | 検証で見つけた stale 修正 |
| 3 | Skill scope 判断に「dotfiles を操作対象にする個人 skill」の第 3 分類を追加。実例は absorb のみ(27 skill 中 1 本)。CLAUDE.md は `build-claude.sh` の生成物なので、生成元の `templates/claude-md/rules.md:22` を同じ文に直した (Codex Review Gate の BLOCK 指摘で判明。`--check` で一致を確認) | `.config/claude/templates/claude-md/rules.md:22` → `.config/claude/CLAUDE.md:24` | 採用(記事由来) |
| 4 | capability JSON は plan 化する。M 規模で、T0 で実例が 0 件なら retired とする撤退条件を付けた | `docs/plans/active/2026-10-13-review-capability-gate-plan.md` | 採用(記事由来) |

## Plan

### Task 1: capability gate の実例調査と実装判断
- **Files**: `docs/plans/active/2026-10-13-review-capability-gate-plan.md`
- **Changes**: T0 で「拡張子に現れないフレームワーク差が原因の誤指摘」が実在するかを調べる。0 件なら plan を retired にする
- **Size**: M

## 教訓

外部記事の framing をきっかけに、#235 → #245 の前提反転に追従し損ねた reference が見つかった。「配線を直した」PR は、その配線が無いと書いている文書を grep して一緒に直す。
