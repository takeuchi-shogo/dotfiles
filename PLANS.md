# ExecPlan Contract

複数ステップ・複数ファイル・長時間の変更では、実装前に plan を作り、作業中に更新する。

## When Required

- 複数ディレクトリをまたぐ
- 新しい skill / script / MCP / workflow を追加する
- Claude / Codex / symlink / validation のような harness 面を変更する
- 30 分以上かかる見込みがある
- 途中で中断・handoff・resume の可能性がある

軽微な typo や 1 ファイルの小修正では省略してよい。

## File Location

- 既定: `tmp/plans/<topic>.md` — 使い捨て、git 管理外 (`plansDirectory`)
- 昇格: handoff・resume・将来参照が要るものだけ `docs/plans/YYYY-MM-DD-<topic>-plan.md` (進行中は `docs/plans/active/`)
- design を分けるときは `...-design.md` を隣に置いてよい

## Plan Retirement

作業が終わったら plan を畳むか残すかを必ず決める。放置しない。

- `tmp/plans/` の plan: Goal / Decision Log / Surprises をコミットメッセージの body に畳んで、ファイルを削除する (`/commit` が実行)
- `docs/plans/` の plan: `Outcome` を埋めて `docs/plans/completed/` に移す

git 履歴が plan の最終的な置き場。`/recall` が commit body から文脈を復元する。

→ 詳細: [resume anchor contract](.config/claude/references/resume-anchor-contract.md) (Plan / HANDOFF / RUNNING_BRIEF の wiring)

## Required Sections

```md
---
success_criteria: "1行で書ける検証可能な完了条件（任意、completion-gate が Ralph Loop で参照する）"
---

# <Task title>

## Goal
- 何を変えるか

## Success Criteria
- 完了したと言える verifiable な条件（テスト・コマンド・観測可能な結果）
- 「make it work」ではなく「これが通れば完了」の形で書く

## Scope
- 触るファイル、触らないファイル

## Constraints
- 壊してはいけない挙動
- 既存ルール、互換性、承認条件

## Unknowns
- 検証していない仮定と高影響 unknown（答えでアーキテクチャ・データモデル・UX が変わる不確実性）
- 不慣れな領域なら着手前に pre-plan unknowns pass を実施（`.config/claude/references/pre-mortem-checklist.md`）

## Program Design（該当時のみ）
- 主要な型とメソッドシグネチャ、データの所有者、call graph
- 変更単位の順序と、各単位で何を検証するか
- 次のいずれかに当たるとき書く: 複数モジュールに跨る interface / ownership の変更 / caller が複数ある public API の変更 / 状態・並行性・失敗意味論の変更
  - caller はリポジトリ内で解決できるものを数える。リポジトリ外に公開している API は、内部 caller が 0 件でも対象に含める
- 当たらなければ節ごと省く（小さい変更にこの層は要らない）
- 理由: アーキテクチャが決まればモデルが実装できる、は成り立たない（`.config/claude/references/why-humans-read-code.md`）
- call graph とファイル構成は diff 記法で書く。`+` / `~` を打つ行は、書かなければコードレビュー時に暗黙に決まる判断であり、そこが最も変更コストの高い時点になる

  ```text
  entrypoint
    runCommand
  +   handleCreateResource
  +     ResourceClient.create(input)
  ```

  ```text
  src/resource
  +  ├── resource-client.ts      # NEW
  ~  └── resource-route.ts       # MODIFIED
  ```

## Validation
- 実行する task / test / lint / review

## Steps
1. 調査
2. 実装
3. 検証

## Progress
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Surprises & Discoveries
- 作業中に分かったこと

## Decision Log
- 重要な判断と理由

## Outcome
- 最終結果
- 未解決事項
```

## Working Rules

- plan は作って終わりではなく、作業中に更新する
- goal、scope、validation を途中で暗黙に変えない
- 変わりやすい判断（データモデル・型・UX・user 確認が要る事項）を先頭の Step に置き、機械的作業は後ろに置く
- 想定外を見つけたら `Surprises & Discoveries` に残す
- 重要な方針変更は `Decision Log` に残す
- 中断前は checkpoint と plan の両方を最新化する
- 並列で別 task を進めるときは worktree で filesystem を分離する
- frontmatter に `success_criteria:` を 1 行で書くと `.config/claude/scripts/policy/completion-gate.py` が Ralph Loop 継続時に参照する (任意)。本文の `## Success Criteria` は required、frontmatter は optional な補助索引。

### frontmatter 完了判定欄 (推奨)

plan-close-detector (`scripts/lifecycle/plan-close-detector.py`) が走査して close 候補を機械判定するための欄。simple `key: value` parser 互換 (1行・カンマ区切り、detector が outer quote を strip する)。

- `lifecycle: active` — plan の生存状態 (active/completed/deferred/paused/pending)。`status:` とは別名前空間 (status は doc-status-audit の active/reference/archive 用)。
- `artifacts: "path/a.py, path/b.sh"` — 成果物パス列挙。全実在で **Tier2 (ARTIFACTS_PRESENT, 報告のみ)**。「作成済み」の弱い証拠であり、これだけでは自動クローズしない。
- `asserts: "validate-configs, plan-close-tests"` — detector の固定 allowlist (`ASSERTS` map) のキー列挙。全 assert が exit 0 かつ working tree clean で **Tier1 (VERIFIED_DONE, 自動 PR 提案)**。任意コマンドは書けない (allowlist 外のキーは無視)。

何も書かない plan は stale + checkbox の Tier2/3 報告のみ対象。

## Compound Plan Ceiling

Skill Graphs 2.0 ([docs/research/2026-04-23-skill-graphs-2.0-absorb-analysis.md](docs/research/2026-04-23-skill-graphs-2.0-absorb-analysis.md)) の実証と $0.9^n$ の指数減衰モデルから、compound skill / plan の Success Criteria は **≤ 8 molecules (step)** を推奨する。9 step 以上は以下のいずれかを選ぶ:

- Phase 境界で plan を分割し、`docs/plans/active/<topic>-phase-N.md` に別ファイル化する
- subagent に autonomous 実行を委譲し、Coordinator (人間) の `understanding` 負荷を減らす
- drive 責任の層を下げる (compound → complex molecule に再分類する)

根拠と drive 責任のレイヤリングは [docs/adr/0008-coordinator-vs-human-ram.md](docs/adr/0008-coordinator-vs-human-ram.md) を参照。
`.config/claude/skills/skill-audit/SKILL.md` の Step 0.7 が静的解析で composition depth を計測する。

## Agent Notes

- Codex:
  - 長時間作業は `$codex-checkpoint-resume` と併用する
  - 必要なら `$codex-session-hygiene` を使う
- Claude Code:
  - `plansDirectory` は `./tmp/plans` だが、永続化したい plan は `docs/plans/` に保存する
  - workflow の詳細は `.config/claude/references/workflow-guide.md` を参照する
