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
6. 実行できない場合の扱いは下記 Verdict の SKIP / INCONCLUSIVE に従う。完了扱いにしない（`cccc` 未導入は下記の optional SKIP 可だが、**導入可能な環境では入れる**）。

## Minimum Evidence

- 実行したコマンド
- exit code
- 重要な warning / failure の有無
- `git diff --stat` または同等の差分確認
- subagent review を使った場合は、その findings を最終判断へ統合したこと

## Verdict（完了宣言のとき）

主張や「直った」の報告は、次のどれか一つにする（`.config/claude/references/trust-verification-policy.md` ルール 6）:

- `VERIFIED` — 選んだ validation が通った、またはベースライン対比で主張どおり動いた
- `NOT VERIFIED` — 失敗した、または主張と逆方向だった（**変更が原因の** Layer 0 Fail を含む）
- `INCONCLUSIVE` — 必須の validation が**環境要因**で実行・比較できない（必須 toolchain 未導入を含む。下記）

`INCONCLUSIVE` を PASS や完了扱いにしない。理由を書いて止め、実行可能なら同じ検証を取り直す。

**Fail と INCONCLUSIVE が混在**したら **Fail（NOT VERIFIED）を優先**する。環境か変更かの切り分けは、完了を主張する側が根拠を示す。flaky なテストは再実行しても不安定なら `INCONCLUSIVE`。

### 必須 / optional（SKIP の前提）

「対象外」はこの節の意味だけで使う: **手順上、この validation をこの変更面で走らせないことが正しい**。

| 区分 | 判定基準 | 例 |
|------|----------|-----|
| **必須** | 変更種別に対し Dotfiles Hints / `Taskfile.yml` / CI / 当該 playbook・skill が要求するもの | ソース変更時の lint・test。task skill の A/B（create-skill Step 5） |
| **optional** | 文書が「未導入時は skip 可」と明記した optional binary、または変更面に無関係なチェック | `cccc` 未導入時の `validate-cccc`。ソース変更なしでの `cccc` |

自分で「optional だ」と宣言しただけでは SKIP できない。上表の基準に当てはまる場合だけ。

### SKIP（対象外）と三値

- `SKIP` = 対象外（上表の optional、または変更面に無関係）。三値の第四の値ではない。
- `SKIP` を `VERIFIED` / PASS / 完了の根拠にしない。必須の結果だけで三値を決める。
- **必須**が実行できないときは `SKIP` と書かず **`INCONCLUSIVE`**（抜け道にしない）。
- optional の `SKIP` だけが残り、必須がすべて `VERIFIED` なら全体は `VERIFIED` にしてよい。SKIP 項目を「通った」と報告しない。
- `cccc`: 未導入は optional SKIP 可だが、導入可能な環境では入れる（Workflow 6）。

### 境界（policy ルール 6 と同型）

- **環境起因**の失敗（必須 toolchain〈pytest / uv 等〉の未導入、測定基盤ダウン、比較不能な環境差。optional binary 未導入は SKIP）→ `INCONCLUSIVE`
- **変更そのものが原因**の ImportError・構文エラー・テスト Fail → `NOT VERIFIED`（Fail）。INCONCLUSIVE にしない
- 必須チェックの一部だけ Pass、他が Fail → `NOT VERIFIED`（Fail 優先）
- 主張と無関係な箇所だけ Pass（主張面を測っていない）→ `INCONCLUSIVE`

## Dotfiles Hints

- config / script 変更: `task validate-configs`
- README / doc 変更: `task validate-readmes`
- symlink / `.codex` / `.claude` 変更: `task validate-symlinks`
- ソース変更の複雑度: `task validate-cccc`（`cccc` 未導入時は optional **SKIP（対象外）**。VERIFIED の根拠にしない。導入可能なら入れる）
- 複数領域変更: `task validate`
- validation 選定に迷う場合: built-in subagent に探索を委譲するか、`Taskfile.yml` と `.bin/validate_*.sh` を直接読む

## Anti-Patterns

- コマンド未実行で「完了」と言う
- 古い成功結果を使い回す
- failure を把握せずに warning 扱いで流す
- diff を見ずに副作用なしと判断する
- 測定不能・比較不能を「たぶん大丈夫」で閉じる（`INCONCLUSIVE` と書き、完了にしない）
- optional の `SKIP` を PASS 扱いにして抜け道にする
- 変更起因の ImportError / 構文エラーを INCONCLUSIVE にする
