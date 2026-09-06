---
success_criteria:
  - "doctor-stale.sh に anchor 節があり、stale な RUNNING_BRIEF.md / HANDOFF.md を件数付きで報告する (active plan は plan-close-detector.py の所管につき対象外)"
  - "resume-anchor-contract.md の 3 anchor テーブルに『寿命切れの検出者』列があり、3 行すべてが実在するスクリプトを名指ししている"
  - "RUNNING_BRIEF.md が retire 済み (存在しないか、現行タスクの内容に更新されている)"
---

# Resume Anchor の寿命を検出可能にする

## Goal

`resume-anchor-contract.md` は 3 つの anchor に「寿命」と「owner」を定義しているが、
owner は**書き込み経路**でしかなく、寿命が切れたことを検出する配線は 2/3 しかない。

| Anchor | 寿命 | 寿命切れの検出者 (現状) |
|--------|------|------------------------|
| Plan (success_criteria) | 完了まで永続 | `plan-close-detector.py` / `plan-lifecycle.py` |
| HANDOFF.md | 次セッション開始まで | `session-save.js` が正常終了時に削除 |
| RUNNING_BRIEF.md | プロジェクト寿命 | **なし** |

実害が出ている: `RUNNING_BRIEF.md` は 2026-05-23 が最終更新で、完了済みの Nix 全面移行を
記述したまま 3.5 ヶ月放置されていた。`.gitignore:58` で除外されているため git 履歴も
rollback も監査もなく、`orphan-artifact-scan.sh` は worktree / branch しか見ないため
検出もされない。

契約が寿命を定義しているのに、切れたことを誰も観測しない状態を解消する。

## 出典

arXiv 2608.26263 "SKILL.state: Scalable Long-Horizon Agent Skills" の absorb。
論文の中核 (会話履歴を明示的 mutable state に置換) は Claude Code runtime の制御外だが、
著者が挙げる失敗条件と「state が将来実行の十分統計量か」という検査軸が既存 anchor に
そのまま当たる。分析: `docs/research/2026-09-05-skill-state-absorb-analysis.md`

## Success Criteria

- `bash scripts/lifecycle/doctor-stale.sh` の出力に `[resume anchors]` 節があり、
  stale な anchor をパスと経過日数つきで列挙する。該当なしなら `none` を出す。
  `docs/plans/active/` は `plan-close-detector.py` が所管するため再スキャンせず、
  その旨を出力に明記する (検出者の重複を作らない)
- summary 行に anchor の件数が加わる
- `resume-anchor-contract.md` の 3 anchor テーブルに「寿命切れの検出者」列が追加され、
  3 行すべてが実在するスクリプト名を持つ (grep で実在確認できること)
- `RUNNING_BRIEF.md` が retire されている
- 既存の 2 節 (codex job state / backup residue) の出力と exit 0 は変わらない

## Scope

触る:
- `scripts/lifecycle/doctor-stale.sh` (節追加)
- `.config/claude/references/resume-anchor-contract.md` (テーブル 1 列追加)
- `RUNNING_BRIEF.md` (削除)

触らない:
- `orphan-artifact-scan.sh` — worktree/branch 専用。責務を混ぜない
- `memory-integrity-check.py` — 監視対象は memory/ のみで anchor は非対象。
  当初この hook を block 化する案を検討したが、対象 artifact が違ううえ、
  削除・縮小での block は正当な retirement を止め、文字数は意味保存を測らないため撤回した
- `session-save.js` / `plan-close-detector.py` — 既に検出者として機能している

## Tasks

- [x] T1 (S): `doctor-stale.sh` に `[resume anchors]` 節を追加。既存の `newest_mtime` /
      `STALE_DAYS` / `don't mutate` パターンを再利用する
- [x] T2 (S): `resume-anchor-contract.md` の anchor テーブルに「寿命切れの検出者」列を追加
- [x] T3 (M): **完了 (当初案から対象を変更)**。当初は `doc-status-audit.py` に検査を足す案
      だったが、同スクリプトは**どこからも呼ばれていない** (`plan-close-detector.py` が
      frontmatter parser を import しているだけ) ため、実装しても休眠 artifact になる。
      また anchor 3 つのうち HANDOFF / RUNNING_BRIEF は gitignore 対象でスキャン範囲外。
      実害が出る地点に移した: `completion-gate.py` (Stop フック、毎ターン稼働) の
      `success_criteria or COMPLETION_PROMISE` が、plan に criteria が無いとき汎用 env 値を
      黙って代入し「成功基準:」として plan 由来のように見せていた。これを
      `_format_criteria_lines()` に切り出し、出所 (plan frontmatter / 汎用 fallback) を明示、
      criteria 欠落時は plan 名つきで警告する。テスト 4 件追加 (計 12 passed)、
      分岐順の変異で 2 件が赤くなることを確認して識別力を検証済み
- [x] T5 (S/M, 新規): **完了 (初回の修正案は誤りで、レビューを受けて反転)**。
      最初は `cleanupHandoff()` を `--session-end` フラグに隠して `SessionEnd` に配線したが、
      Codex Review Gate が「`session-load.js:630` は `SessionStart` で HANDOFF を読む設計
      なので、`SessionEnd` で消すと次セッションが読む前に消える」と指摘。実地確認して
      その通りだった (`loadHandoff()` が true を返すと state 復元をスキップする)。
      **正しい配置は読み手**。`session-load.js` が HANDOFF を出力した直後に
      `retireHandoff()` で削除し、`session-save.js` からは HANDOFF 参照を全撤去、
      settings.json に足した `SessionEnd` エントリも両ファイルから撤去した。
      24 時間超の HANDOFF は `loadHandoff()` が読まずに `continue` するので retire にも
      到達せず、`doctor-stale.sh` が stale として拾える。
      実測: Stop 相当では残存 / SessionStart で読まれて削除 / 24h 超は読まれず削除もされない
- [x] T4 (M/L): **完了 (射程を明示して縮退)**。`scripts/lifecycle/resume-anchor-lint.sh` +
      `task resume-anchor-lint`、`/checkpoint` 手順 5 から起動。
      各節を MISSING / HOLLOW / ok で判定する。重点は「環境から導けない知識」が入る節
      (checkpoint スキーマの `What Didn't Work`、escalation スキーマの 3.5 / 3.7) —
      git は branch と diff は知っていても「試して捨てた approach」は知らない。
      **レビューで判明: HANDOFF のスキーマが 2 つあった**。`/checkpoint` が実際に書くのは
      `## Goal / Progress / What Worked / What Didn't Work / Next Steps / Context Files`
      (skills/checkpoint/SKILL.md) で、`references/handoff-template.md` の番号付き 1-5 節は
      人間へのエスカレーション用。当初は後者だけを見ており、実際に生成される HANDOFF は
      全節 MISSING になる状態だった。ファイルごとにスキーマを判別する方式に修正。
      副産物で `${entry##*|}` によるフィールド分割バグも露出 (パターンに `|` を入れた
      途端に壊れた) → `${entry#*|}` に修正。
      **射程の限界をスクリプト冒頭に明記**: 「未記録であること」は静的に決定不能 (Codex 指摘)。
      節が存在し非 placeholder でも、肝心の 1 件が抜けている可能性は排除できない。
      pass は「形が揃っている」であって「再開できる」ではない。
      検証 9 ケース: 両スキーマのテンプレートそのまま=全 HOLLOW / 中身あり=全 ok /
      節欠落=MISSING / `3.` だけ欠落で `3.5` に誤マッチしない / 節内 `####` を捨てない /
      anchor 不在=exit 2

T1/T2 は T3/T4 に依存しない。T3 は T2 の列定義を前提にする。

## 撤退条件

- T1 の anchor 節が 3 ヶ月運用して一度も stale を報告しない、かつ RUNNING_BRIEF が
  手動で回っている場合、節を削除して契約の記述だけ残す
- T4 の fixture が「anchor だけから再開できる」を安定して示すなら、T3 の frontmatter
  必須化は過剰なので縮退させる
