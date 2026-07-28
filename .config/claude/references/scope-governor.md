---
name: scope-governor
description: レビュー→修正ループが元の依頼を超えて膨らむのを止めるゲート。finding を修正する前と各再レビュー前に適用する
type: reference
last_reviewed: 2026-07-27
---

# Scope Governor

レビューは closeout ゲートであって、タスクを書き直す許可ではない。

このリファレンスは `/review` Step 5 のサイクルルールから参照される。**finding を修正する前**と**各再レビューの前**に適用する。

> 出典: openclaw/agent-skills `autoreview` SKILL.md § Scope Governor (2026-07-27 absorb。同ソースの 2026-05-28 absorb 時点には存在しなかった新規セクション)。
>
> 動機となった観測: 著者が「厄介なリファクターで 66 ラウンド」を報告している。レビュー起因の修正が次の指摘を生み、それが更に次を生む発散パターンを、サイクル数の上限だけでは止められない。

## 1. baseline を凍結する

最初のレビューの前に、次を記録して以降の基準にする:

- 元の依頼または Issue
- 対象ブランチ
- 意図した挙動
- owner 境界（どのモジュール・レイヤの責任範囲か）
- 変更ファイル一覧
- 非テスト LOC

既に膨らんでいるブランチや引き継いだブランチでは、**現状の全 diff を基準にしない**。意図した PR の diff を基準に取る。そうしないと既存の drift を承認したことになる。

## 2. finding を修正前に分類する

| 分類 | 条件 | アクション |
|---|---|---|
| **in-scope blocker** | 現 diff が持ち込んだ問題 + 同じ owner 境界 + タスクの契約を変えずに直せる | 直す |
| **follow-up** | 実在する問題だが、隣接するバグクラス・別サーフェス・掃除・より広い hardening に属する | 直さない。記録して follow-up に回す |
| **stop-and-escalate** | 新しい protocol / config / storage / public API の契約、別の owner 境界、リリースプロセスの変更、元依頼の外にある設計判断を要する | 手を止めて報告する |

重大度ラベル（`agents/code-reviewer.md` の MUST / CONSIDER / NIT / ASK / FYI）とは**軸が違う**。重大度は「どれだけ悪いか」、この分類は「今この PR で直してよいか」。MUST でも stop-and-escalate になりうる。

## 3. 手を止めて scope 破綻を報告する条件

以下のいずれかに当たったら、修正を続けずに報告する:

- 狭い PR がアーキテクチャ変更・プロトコル変更・マイグレーション・リリースプロセス変更に化けた
- diff が **`max(2 × 初期非テスト LOC, 初期非テスト LOC + 50)`** を超えた、または変更ファイル数が初期の 2 倍を超えた
  - **非テスト LOC の数え方**: テストファイル以外の **追加行 + 削除行**（net ではない）。`git diff --numstat` の合計から test / spec / fixture / snapshot のパスを除いた値
  - 下限の `+50` は小さな diff 用の床。初期 20 行の修正が 40 行になっただけで止まるのを防ぐ
  - これは `references/pr-splitting-patterns.md` の 300 行閾値とは別物。300 行は**レビュー可能性の絶対上限**、こちらは**レビュー起因で膨らんだことを検知する相対ゲート**。両方が同時に効く
- **レビュー起因の修正サイクルが 2 回で収束しなかった** → 一旦停止し、残っている全 finding を §2 で**再分類**する
- 最善の修正が「まず正典となる契約を定義する」であって、ローカルな推論層をもう一枚足すことではない
- accepted finding を直すと、その PR が元の挙動・Issue・owner 境界を説明しなくなる

## 4. 2 サイクル停止後の続行条件

`/review` の最大サイクル数は 3 回（`skills/review/SKILL.md` サイクルルール 5）。Scope Governor はその 3 回目の中身を制限する。

- 2 回で収束しなかったら §2 の再分類を行う
- **3 回目は「再分類後もなお in-scope blocker である finding」だけを対象にする**
- それ以外は follow-up か stop-and-escalate に落とす
- 3 回目でも PASS にならなければ既存どおりユーザーにエスカレーションする

レビューアを満足させるための投機的な修正を積み続けてはならない。続行できないときは、有用な分析を保存し、安全に着地できる最小の部分集合があるならそれを特定し、大きい修正は follow-up として起票または依頼する。

## 5. scope 未確定のまま commit を積まない

scope 分類と focused proof（該当テストの実行）が終わるまで、探索的な編集は**ローカルに留めて commit / push に含めない**。scope が壊れたと分かったら、その編集は履歴として残さず取り除く。

理由: 未確定の修正がコミット履歴に入ると、その PR が「何をした PR なのか」を説明できなくなり、レビュー後の rebase 禁止ルール（`skills/github-pr/SKILL.md`）と組み合わさって取り返しがつかなくなる。

## 6. rebaseline と「scope を破る」は別

§3 で止まったあとの続行には 2 通りある。混同すると §3 と本節が矛盾して読める。

| | 意味 | 必要なもの |
|---|---|---|
| **rebaseline** | baseline を引き直して**この Governor をもう一度最初から適用する** | ユーザーの明示承認。緊急である必要はない |
| **scope を破る** | 分類も再分類も飛ばして Governor 自体を**適用しない** | 緊急事態のみ |

§3 で手が止まったあと**続行するために必要なのがユーザーの明示承認**であり、それは rebaseline の条件である。承認を得たら §1 の baseline を新しい値で引き直し、§2 の分類をやり直す。承認は Governor の免除ではない。

**Governor 自体を飛ばしてよいのは緊急事態に限る。例外の定義は `references/emergency-definition.md` が唯一の正**（ここに二重定義を作らない）。その定義に当たらないなら、Governor を飛ばすほど critical ではない。

リリース・beta・stable・hotfix・署名・notarization・appcast・パッケージ公開・リリースチェックに関わる作業では、ブランチ名がリリース系でなくても凍結側に倒す（rebaseline も認めず §3 で止める）。ここでの「凍結」は `/freeze` skill とは無関係の運用規律を指す。

## 7. 報告

Scope Governor が発火した場合、完了報告に次を含める:

- 実行したコマンド
- **実行したテストとその結果**（`skills/review/templates/synthesis-report.md` の Tests Run セクション）
- finding の分類結果（in-scope blocker / follow-up / stop-and-escalate の各件数）
- clean 判定の根拠

> 出典 (verbatim): "Stop patching and report the scope break instead of continuing" / "Do not keep committing speculative fixes just to satisfy the reviewer" — openclaw/agent-skills `autoreview` SKILL.md § Scope Governor

## Gotchas

- **重大度と scope 分類を混ぜない**: MUST だから直す、ではない。MUST かつ stop-and-escalate なら止める
- **相対ゲートは絶対閾値の代わりではない**: 300 行上限（`pr-splitting-patterns.md`）と 2x 相対ゲートは別の失敗モードを見ている。片方だけ通っても安全とは言えない
- **例外定義をここに書かない**: `emergency-definition.md` を参照する。二重定義は片方が腐る
