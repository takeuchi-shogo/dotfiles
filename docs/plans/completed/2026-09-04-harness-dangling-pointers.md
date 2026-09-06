---
success_criteria: "AGENTS.md の 4 原則ポインタが root CLAUDE.md の実在節を指し、YAML list 形式の success_criteria を completion-gate が読め、launch-worker が codex/gemini でも --worktree を無視しない"
---

# ハーネスの参照切れ 3 件を直す

## Goal
`/absorb`（神ハーネス理論）で露出した、指示と実配線の乖離 3 件を潰す。

- B1: `AGENTS.md:27` / `.codex/AGENTS.md:9` が root `CLAUDE.md` の Karpathy 4 原則を指すが、`37a3e397`(2026-05-05) の pruning で本文が消え 4 ヶ月ポインタだけ残った
- B2: `success_criteria` の schema が二重定義（`PLANS.md:36` = scalar / `resume-anchor-contract.md:23-32` = list）で、`completion-gate.py:396-409` は scalar しか読めず list 形式の plan は空にフォールバックする
- B3: `launch-worker.sh:82` の worktree 作成が `MODEL == "claude"` の AND 条件で、codex/gemini に `--worktree` を渡すと silent NO-OP。`race-runner.sh:66` はこれに依存して同一 tree に 2 モデルを並列書き込みさせる

## Success Criteria
- `grep -c "Think Before Coding" CLAUDE.md` >= 1、4 原則すべての見出しが root CLAUDE.md に実在
- YAML list 形式の plan（`docs/plans/active/2026-04-20-karpathy-absorb-plan.md`）で `_extract_success_criteria` が空でなく list を結合した文字列を返す（self-check で検証）
- `launch-worker.sh` の worktree ブロックが model 非依存になり、codex/gemini でも `cd <worktree>` が送られる
- `race-runner.sh` が各 worker に一意の `--worktree` を渡す
- `task validate-configs` が pass

## Scope
触る: `CLAUDE.md`, `AGENTS.md`, `.codex/AGENTS.md`, `.config/claude/scripts/policy/completion-gate.py`, `.config/claude/references/resume-anchor-contract.md`, `PLANS.md`, `scripts/runtime/launch-worker.sh`, `scripts/runtime/race-runner.sh`, `docs/research/2026-07-27-dex-harness-not-enough-absorb-analysis.md`(frontmatter のみ)

触らない: `.config/claude/rules/common/*`（4 原則の詳細版は user スコープに残す）、既存 plan の success_criteria 本文、race-runner の勝敗判定ロジック

## Constraints
- 4 原則は root CLAUDE.md に**要約**を戻す。`rules/common/` の詳細版は消さない（詳細と要約の二層は 37a3e397 以前から成立していた構造）
- schema はどちらか一方に倒さない。実データに両形式が 3 件ずつ存在するため、gate 側を両対応にする
- race-runner の「最初の完了を採用」設計は変えない。隔離を足すだけ
- `git commit --no-verify` 禁止

## Unknowns
- codex worker に `cd <worktree>` を送った後、`codex exec` が worktree 内で正しく動くかは未実測（cmux 起動が要る）。実行実績ゼロの経路なので、静的な整合性までを今回の完了条件とする

---

## 中断時点の状態 (2026-09-05)

**中断理由**: 別セッションが同じ working tree で作業を開始し、私が stage した
`resume-anchor-contract.md` と `docs/wiki/log.md` を上書き (`MM` 状態)。
Stop gate も別セッションの `docs/plans/active/2026-09-05-resume-anchor-lifetime-plan.md`
で塞がっている。ユーザー判断で中断。

**staged (commit 未実施、10 ファイル / +407 -23)**: B1/B2/B3 + Stale-Plan Audit + 分析レポート。
`git diff --cached` で確認できる。commit は staged スナップショットを取るので別セッションの
unstaged 変更は巻き込まない。

**Codex Review Gate**: BLOCK 2 回 → 両方対応済み。3 回目は exit 144 と 30 分無応答で **判定未取得**。

**`/review` (deep tier, 7 体)**: 2 体完了、3 体が turn limit で未完、2 体 (security-reviewer /
codex-reviewer) は結果未取得。**verdict 未確定**。

### Deferred — 未対応の指摘 (次回セッションの起点。本セッションでは着手しない)

test-analyzer (Coverage: partial):
- `completion-gate.py:433` インラインコメント付き scalar (`success_criteria: "foo" # comment`)
      がコメントごと返る。例外なしで誤った文字列が `effective_criteria` に流れる (実行確認済み)
- `completion-gate.py:433` 非空 flow list (`["a","b"]`) が生文字列で返る。`[]`/`{}` は
      特別扱いするのに非空 flow は素通りする非対称
- 実データ回帰テスト不在。同ディレクトリの `test_completion_gate_detect.py` には
      実リポジトリ対象テストがあり、それが family の慣習
- `test_yaml_list_form_is_read` の assertion が部分文字列で緩い。他は `==` 全一致

silent-failure-hunter (Coverage: complete):
- `race-runner.sh:110-111` cleanup の `2>/dev/null || true` が worktree 削除失敗を握り潰し、
      この PR が直そうとした孤児 worktree 蓄積を自分で再導入しうる。warn を stderr に出す
- `race-runner.sh:127-137,:184` collector の失敗理由 (exit 1 = error / exit 2 = timeout) を
      捨てており、全滅時に無条件で「No worker completed within timeout」と誤った理由を報告する
- `completion-gate.py:396-448` 「意図的に空」「認識できない形式」「キーが無い」が全て `None` に
      潰れ、同じフォールバックに合流する。今回直したバグと同型の構造が残る (severity は低い —
      誤情報は出さず表示が消えるだけ)。キーはあったが認識できなかった場合のみ stderr 警告を検討

security-reviewer (Coverage: partial, verdict: NEEDS_HUMAN_REVIEW):
- **[修正済み]** HIGH: `launch-worker.sh` の model allowlist が worktree 作成 (`:85-90`) より後の
  起動分岐 (`:96`) にあり、`MODEL == "claude"` 条件を外したことで未検証の `$MODEL` が
  `WORKER_ID` → `/tmp/cmux-worktrees/<id>` に入る経路が全モデルで到達可能になっていた。
  `--models claude,gpt5` のタイポで worktree+branch を作ってから exit 1 し、race-runner は
  その worker を未登録なので cleanup も回らず孤児が確定的に残る。traversal 変種も直接呼び出しなら通る。
  → allowlist を引数パース直後 (WORKER_ID 生成前) へ前倒し。`gpt5` と `x/../../../../tmp/evil` が
  worktree 作成前に弾かれ、`/tmp/cmux-worktrees/` 未作成・`cmux/*` 0 件を実行確認済み
- MEDIUM (未対応、optional / not blocking): `completion-gate.py:415-433` の block/list 収集に
  行数・長さの上限がなく、`effective_criteria` は hook の block reason に verbatim で入る。
  既存の `pending` リストと同じ trust level だが、scalar 1 行だった injection capacity が
  多行に広がった。`items[:20]` 相当の cap と制御文字除去が hardening 候補

codex-reviewer (verdict: NEEDS_FIX、Requires Escalation: correctness 1/5):
- **[修正済み]** `docs/wiki/log.md:4` append-only 契約違反 (独立検証済み)。ingest 追記が intro の
  フォーマット例のバッククォート内に入り、`^## \[` grep 契約に一致せずログ運用ツールから不可視だった。
  原因は挿入位置を最初の `## [` で探索し、それがテンプレート行だったこと。構造を復元し
  `^## \[` が 231→232 になること・テンプレート行の残骸が消えたことを確認済み
- **[修正済み]** `race-runner.sh:91` 予測可能な `/tmp/race-$$` を `rm -rf` なしで `mkdir -p` していた。
  PID 再利用や前回の SIGKILL で `trap cleanup EXIT` が発火せず `ready`/`winner.txt` が残っていると、
  次回起動の最初の `wait -n` 直後に **stale marker で誤って勝者確定**する (独立検証済み)。
  今回私が ready marker を追加したことで stale 状態の危険が増した。→ `mkdir -p` の前に `rm -rf "$RACE_DIR"` を追加。**構文チェックのみで、stale marker を仕込んだ実行検証は permission denied のため未実施**
- **[未対応 MUST]** `race-runner.sh:109` launch は動的な global surface を解決するのに cleanup は
  `surface:1` 決め打ち。敗者が別 surface だと close 失敗を握り潰した直後に `:110` で
  **稼働中 worker の worktree を強制削除**する
- **[未対応 MUST]** `race-runner.sh:146` 勝者検出の `break` 後に残りの `COLLECT_PIDS` を kill/reap しない。
  遅い collector が既定 1800 秒まで polling を続け、race 終了後に dispatch log も書く
- **[未対応 CONSIDER]** `race-runner.sh:133` winner.txt の排他取得が result/ready 書込みより先なので、
  勝者が result 書込み前に kill されると後続の成功 worker も noclobber で勝者になれず全滅扱いになる
- **[未対応 CONSIDER/ASK]** `launch-worker.sh:91` `git worktree add` 後に `cmux send` が失敗すると
  `set -e` で終了し race-runner が ID を受け取れず cleanup 不能 / `cmux send` が `cd` の実行完了を
  保証するか未確認 (未保証なら codex/gemini は元の tree で走り隔離が崩れる)
- **[未対応 NIT]** ready-marker・全 collector 失敗・early winner cleanup・launch 失敗の shell 回帰テストなし

## Outcome (2026-09-06)

B1 / B2 / B3 とも Success Criteria を満たし、PR 化した。

**この再開セッションで追加対応した Deferred の MUST 2 件** (どちらも本 plan の変更が
新たに入れた経路なので、PR 前に潰した):

- `race-runner.sh` の cleanup が `surface:1` 決め打ちで close-surface していた件 →
  worker ごとに専用 workspace を作っているので `close-workspace` に変更し、
  **閉じられたときだけ** worktree / branch を回収するようにした。閉じ損ねた場合は
  「生死不明なので消さない」側に倒し、パスを stderr に出して手動回収に回す
- 勝者確定で `break` した後に残る collector が `--timeout` (既定 1800s) まで polling を
  続けていた件 → EXIT trap で `pkill -P` + `kill` して子の `collect-result.sh` ごと落とす

**残した Deferred** (影響が表示の歪みかテスト不足に留まり、破壊的でないため):

- `completion-gate.py` の `_extract_success_criteria` が、インラインコメント付き scalar
  (`success_criteria: "foo" # comment`) と非空 flow list (`["a","b"]`) を生文字列で返す
- 同 `items` に行数・長さの上限がなく、block reason への injection capacity が
  scalar 1 行から多行に広がった (trust level は既存 `pending` と同等)
- `race-runner.sh` の winner.txt 排他取得が result 書込みより先で、勝者が result 書込み
  前に kill されると後続の成功 worker も勝者になれない
- `launch-worker.sh` の `cmux send` が `cd` の実行完了を保証するか未確認
- race-runner の shell 回帰テストなし

**verdict**: Codex Review Gate は BLOCK 2 回とも対応済み。3 回目は exit 144 / 30 分無応答で
未取得のまま。`/review` deep tier も 7 体中 2 体完了で verdict 未確定。**この PR は
レビュー verdict なしで出す**ため、マージ前にレビューを通すこと。
