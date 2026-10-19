---
name: codex-verification-before-completion
description: Mandatory verification workflow for Codex. Use before declaring work complete, after edits, before commit or review-ready reports, or whenever you need evidence from build, test, lint, diff, or validation commands.
platforms: [agents, codex]
---

# Codex Verification Before Completion

完了宣言の前に、必ず実コマンドを実行して結果を確認する。

## Workflow

1. 変更対象に最も近い validation を選ぶ。
2. review-ready report や複数領域変更では、必要なら built-in subagent への review 委譲を先に走らせる。
3. build / test / lint / typecheck / diff / `cccc`（ソース変更時、`task validate-cccc`）のうち必要なものだけ実行する。
4. exit code と要点を確認する。
5. 失敗があれば修正し、同じコマンドを再実行する。
6. 実行できない場合は、その理由を明示して完了扱いにしない（`cccc` 未導入は skip 可だが、導入可能な環境では入れる）。

## Minimum Evidence

- 実行したコマンド
- exit code
- 重要な warning / failure の有無
- `git diff --stat` または同等の差分確認
- subagent review を使った場合は、その findings を最終判断へ統合したこと

## Verdict（完了宣言のとき）

主張や「直った」の報告は、次のどれか一つにする（`.config/claude/references/trust-verification-policy.md` ルール 6）:

- `VERIFIED` — 選んだ validation が通った、またはベースライン対比で主張どおり動いた
- `NOT VERIFIED` — 失敗した、または主張と逆方向だった
- `INCONCLUSIVE` — コマンドを走れない、比較が無効、観測が壊れている

`INCONCLUSIVE` を pass や完了扱いにしない。理由を書いて止め、実行可能なら同じ検証を取り直す。

## Dotfiles Hints

- config / script 変更: `task validate-configs`
- README / doc 変更: `task validate-readmes`
- symlink / `.codex` / `.claude` 変更: `task validate-symlinks`
- ソース変更の複雑度: `task validate-cccc`（`cccc` 未導入時は skip）
- 複数領域変更: `task validate`
- validation 選定に迷う場合: built-in subagent に探索を委譲するか、`Taskfile.yml` と `.bin/validate_*.sh` を直接読む

## Anti-Patterns

- コマンド未実行で「完了」と言う
- 古い成功結果を使い回す
- failure を把握せずに warning 扱いで流す
- diff を見ずに副作用なしと判断する
- 測定不能・比較不能を「たぶん大丈夫」で閉じる（`INCONCLUSIVE` と書き、完了にしない）
