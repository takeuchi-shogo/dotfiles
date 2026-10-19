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
6. 実行できない場合の扱いは下記 Verdict の SKIP / INCONCLUSIVE に従う。完了扱いにしない。

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
- `INCONCLUSIVE` — 必須の validation が実行できない、比較が無効、観測が壊れている、インフラ起因で測定不能

`INCONCLUSIVE` を PASS や完了扱いにしない。理由を書いて止め、実行可能なら同じ検証を取り直す。

### SKIP（対象外）と三値

- `SKIP` は「この変更面ではその validation を走らせないことが手順上正しい」ときのラベル（例: ソース変更なしで `cccc`、optional binary `cccc` が未導入で公式に skip 可）。**対象外**であり、三値の第四の値ではない。
- `SKIP` を `VERIFIED` / PASS / 完了の根拠にしない。必須の他 validation の結果だけで三値を決める。
- 必須の validation が実行できないときは `SKIP` と書かず **`INCONCLUSIVE`** にする（抜け道にしない）。
- optional の `SKIP` だけが残り、必須がすべて `VERIFIED` なら全体は `VERIFIED` にしてよい。そのときも SKIP 項目を「通った」と報告しない。

### 境界（policy ルール 6 と同型）

- インフラ起因の ERROR（必須コマンドのクラッシュ・環境欠落・測定不能）→ `INCONCLUSIVE`
- 必須チェックの一部だけ Pass、他が Fail → `NOT VERIFIED`
- 主張と無関係な箇所だけ Pass（主張面を測っていない）→ `INCONCLUSIVE`

## Dotfiles Hints

- config / script 変更: `task validate-configs`
- README / doc 変更: `task validate-readmes`
- symlink / `.codex` / `.claude` 変更: `task validate-symlinks`
- ソース変更の複雑度: `task validate-cccc`（`cccc` 未導入時は **SKIP（対象外）**。VERIFIED の根拠にしない）
- 複数領域変更: `task validate`
- validation 選定に迷う場合: built-in subagent に探索を委譲するか、`Taskfile.yml` と `.bin/validate_*.sh` を直接読む

## Anti-Patterns

- コマンド未実行で「完了」と言う
- 古い成功結果を使い回す
- failure を把握せずに warning 扱いで流す
- diff を見ずに副作用なしと判断する
- 測定不能・比較不能を「たぶん大丈夫」で閉じる（`INCONCLUSIVE` と書き、完了にしない）
- optional の `SKIP` を Pass 扱いにして抜け道にする
