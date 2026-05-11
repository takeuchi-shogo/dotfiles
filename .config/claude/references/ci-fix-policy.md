# CI Fix Policy — 安全制約と Minimal Diff の規律

> 出典: Warp `oz-skills/ci-fix` (2026-05-06 absorb)。`docs/research/2026-05-07-warp-oz-skills-absorb-analysis.md` の T1。
>
> 適用先: `/gh-fix-ci` (mizchi external) / `/create-pr-wait` / `/pull-request` を経由した CI 修正フロー。

CI 失敗を直すときに **絶対に守る** ガードレールと、`gh-fix-ci` がカバーしない安全制約をまとめる。

## 3 つの hard rule（違反は STOP）

### 1. workflow `permissions:` を緩めない

CI が `pull_request` イベントで権限不足になったとき、`.github/workflows/*.yml` の `permissions:` ブロックを書き換えて広げる修正は **禁止**。

```yaml
# NG: 直すべきはコード or workflow ロジック、権限の拡張ではない
permissions:
  contents: write     # ← read で動いていたものを書き換えない
  pull-requests: write
  id-token: write     # ← OIDC 不要なら付けない
```

権限が本当に必要なら別 PR で正面から提案し、レビューを受ける。CI fix のついでに混ぜない。

### 2. `pull_request_target` への切り替え禁止

`pull_request` で動かない workflow を `pull_request_target` に変更するのは **禁止**。これは PR 作成者の権限ではなく **base リポジトリの secret + write 権限** で実行されるため、悪意ある PR でリポジトリ全体を乗っ取られる経路になる（GitHub Actions 既知の sev-1 攻撃面）。

代わりに:
- secret が必要なら `workflow_run` イベント + 別 job 分離を検討
- 外部 contributor 由来 PR は手動承認 (`environments` 保護) を併用

### 3. flaky test の盲 rerun 禁止

`gh run rerun` で通すのは **「flaky だと過去履歴で証明できている test だけ」**。直前の修正で fail した test を rerun で誤魔化すのは禁止。

判断手順:
1. fail した test 名を取得
2. 同 test の過去 30 日 fail 率を `gh run list --json` で確認
3. fail 率 5% 超 = 既知 flaky → rerun 可（ただし issue にメモ）
4. fail 率 5% 未満 = real failure → コードを直す

## Minimal-diff philosophy（CI fix 限定の追加規律）

`/gh-fix-ci` の plan-then-fix を通すときの追加規律:

| 観点 | 守る規律 |
|------|---------|
| 変更行数 | 失敗箇所に直結する **最小行のみ**。隣接コード「ついで」リファクタは別 PR |
| import 追加 | 失敗解消に必須なものだけ。未使用 import 削除も別 PR |
| test 修正 | 仕様変更を伴うなら "fix CI" ではなく "spec" として扱い、別 PR |
| lint 設定変更 | 禁止（`protect-linter-config` hook が enforce）。コードを直す |
| `.gitignore` / `package.json` 改変 | CI 失敗解消の一環でなければ禁止 |

## ブランチ運用

Warp は `ci-fix/<branch>` の別ブランチを切るが、当 dotfiles は **既存ブランチへ直 commit** を採用（個人 dotfiles で PR ブランチが浅いため）。ただし以下の条件で別ブランチに切り替える:

- `/create-pr-wait` の retry 上限（3 回）に達した
- 修正が 50 行以上に膨らんだ → spec か別 PR を切る合図
- main / master を直接修正している（hotfix を除き fork 必須）

## Anti-Patterns

| NG | 理由 |
|----|------|
| `--ignore-fail` や `continue-on-error: true` を追加して通す | 失敗を握り潰す。silent failure pattern |
| test を skip / xfail で通す | 偽の green。後で本番障害として返ってくる |
| `git push --force-with-lease` を CI fix 中に使う | 他者の push と衝突。retry の冪等性が壊れる |
| `secrets.GITHUB_TOKEN` のスコープ拡張 | `permissions:` ルール 1 と同じ理由で禁止 |
| 修正 commit メッセージに「とりあえず」 | 後追い不能。`fix(ci): <component> - <root cause>` 形式で書く |

## 参照される側

このポリシーを守る skill / agent:
- `/gh-fix-ci` (mizchi/skills external) — 修正実装前にこの policy を Read
- `/create-pr-wait` — Step 4-3 (修正の実装) の前に確認
- `/pull-request` — CI fix 由来 PR の本文に "ci-fix-policy 準拠" の checkbox 提示
- `build-fixer` agent — type/build error fix と CI fix の境界判断時に参照

## 撤退条件

このポリシーが過剰だった場合の signal:
- 30 日以内に 3 回以上 `/gh-fix-ci` 実行で「policy が邪魔した」記録 → ルール緩和を検討
- 個人 repo 限定で team workflow が無いと判明したルール（`pull_request_target`）→ 注釈で "team repo only" 明示
