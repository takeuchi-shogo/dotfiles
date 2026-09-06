---
status: reference
last_reviewed: 2026-04-23
---

# Resume Anchor Contract

**目的**: セッション中断・compact・複数セッション跨ぎでも作業を確実に再開するための「anchor」の規約。
End-to-End Completion 原則 (`model-routing.md`) を支える土台。

## 3 つの anchor

| Anchor | スコープ | 配置 | 寿命 (契約) | Owner (書き込み) | 検知・cleanup 経路 |
|--------|---------|------|------|-------|------------------|
| **Plan (Success Criteria)** | プロジェクト/タスク全体 | `docs/plans/active/*.md` | 完了まで永続 | ExecPlan Contract (`PLANS.md`) | `scripts/lifecycle/plan-close-detector.py` が nightly (`scripts/runtime/nightly/run-plan-close-scan.sh`) で **報告** する。30 日以上未更新は Tier 3 `STALE`、完了済みは Tier 1-2。移動はしない |
| **HANDOFF.md** | 1 セッション | `tmp/HANDOFF.md` (worktree なら root) | 次セッション開始まで | `skills/checkpoint` | `.config/claude/scripts/runtime/session-load.js` が `SessionStart` で読み、読了後に **削除** する。内容の検査は `task resume-anchor-lint` (別責務、下記参照) |
| **RUNNING_BRIEF.md** | プロジェクト全体 (累積) | プロジェクト root | プロジェクト寿命 | `skills/checkpoint brief` | `scripts/lifecycle/doctor-stale.sh` の `[resume anchors]` 節が **報告** する。mtime > `DOCTOR_STALE_DAYS` (既定 30d) を stale candidate として列挙。削除はしない |

**Owner と検知経路は別の責務である**。Owner は anchor を書く経路で、検知経路は寿命が
切れた anchor を観測する経路。列を分ける理由は、書く仕組みがあることを「寿命が管理されている」
と読み違える事故が実際に起きたため。2026-09-05 以前は RUNNING_BRIEF に検知経路が無く、
完了済みプロジェクトの記述が 104 日放置されていた。`.gitignore` 対象で git 履歴からも追えず、
`orphan-artifact-scan.sh` は worktree / branch 専用で対象外だった。

なお 30 日 mtime は「寿命切れ」の証明ではなく **レビュー要求の candidate** である。
判断は人間が行う (`doctor-stale.sh` は inventory であって mutate しない)。

新しい anchor を足すときは両方の列を埋めること。

### HANDOFF.md の寿命 (2026-09-05 修正済み)

2026-09-05 以前、`session-save.js` は `Stop` に matcher なしで配線され `cleanupHandoff()`
を無条件に呼んでいた。`Stop` はアシスタントのターン毎に発火するため、`/checkpoint` が
書いた HANDOFF.md はそのターンの終了時点で削除され、契約の寿命「次セッション開始まで」を
満たしていなかった (Issue #243)。

**現在は読み手が retire する**。`session-load.js` が `SessionStart` で HANDOFF.md を読み、
内容を出力した直後に `retireHandoff()` で削除する。`session-save.js` は state 保存だけを
担い、HANDOFF には触れない。

書き手でも `SessionEnd` でもなく読み手に置くのは、契約の寿命が「次セッション開始まで」
だからである。他の配置は両方とも寿命を満たさない。

| 配置 | 何が起きるか |
|------|------------|
| `Stop` (2026-09-05 以前) | ターン毎に発火し、書いた直後に消える |
| `SessionEnd` | 次セッションが `session-load.js` で読む**前**に消える。加えて SessionEnd は既定 timeout が短く、git を複数回叩く処理の後では到達しないことがある |
| `SessionStart` の読み手 (現在) | 読了後に消える = 寿命どおり |

**retire するのは実際に読んだ 1 ファイルだけ**で、候補パス全体を消さない。24 時間を超えた
HANDOFF.md は `loadHandoff()` が読まずに `continue` するため retire にも到達せず残る。
これは意図した挙動で、`doctor-stale.sh` の `[resume anchors]` 節が stale candidate として
拾う。候補を一括削除すると、読まれなかった古い残骸まで消えて検出できなくなる
(2026-09-05 に一度そう書いてレビューで差し戻した)。

削除に失敗した場合 (権限 / I/O) は stderr に出るが処理は続行する。次の SessionStart で
再度読まれ、24 時間を超えていれば stale として報告される。

### 内容の検査 (寿命とは別)

寿命の検出 (`doctor-stale.sh`) は anchor が古いかを見るだけで、**再開に足る内容が
書かれているか**は見ない。`task resume-anchor-lint` が各節を MISSING / HOLLOW / ok で
判定する。`/checkpoint` の手順 5 から呼ばれる。

**HANDOFF のスキーマは 2 つある**。lint はファイルを見てどちらか判定する。

| スキーマ | 定義元 | 節 | 用途 |
|---------|-------|-----|------|
| checkpoint | `skills/checkpoint/SKILL.md` | Goal / Progress / What Worked / What Didn't Work / Next Steps / Context Files | `/checkpoint` が実際に書くのはこちら |
| escalation | `references/handoff-template.md` | 1. コンテキスト 〜 5. 再開ガイド (3.5 Dead Ends, 3.7 検証済み事実を含む) | エージェントから人間へのエスカレーション |

重点は checkpoint 側の `What Didn't Work`、escalation 側の 3.5 / 3.7。git は branch と
diff は知っているが、試して捨てた approach は知らない。ここが空だと次セッションが
同じ dead end を踏み直す。

ただし lint の pass は「形が揃っている」であって「再開できる」ではない。観測時に
重要と気づかず書き落とした事実があるかは、ファイルからは決定できない。

## Success Criteria Schema

Plan ファイル (`docs/plans/active/*.md`) は以下の形式で Success Criteria を持つ:

### Frontmatter (任意、completion-gate が参照)

```yaml
---
success_criteria:
  - "1 行で書ける検証可能な完了条件 (string array)"
  - "テスト・コマンド・観測可能な結果で書く"
---
```

条件が 1 つなら `PLANS.md` Required Sections の scalar 形式 (`success_criteria: "..."`)
でもよい。`completion-gate.py` の `_extract_success_criteria` は両形式を読む
(list は `" / "` で結合)。2026-09-04 以前は scalar しか読めず、list 形式の plan は
criteria が空のまま汎用 `COMPLETION_PROMISE` に落ちていた。

### 本文 (必須)

```markdown
## Success Criteria

- 完了したと言える verifiable な条件
- 「make it work」ではなく「これが通れば完了」の形で書く
- 各 criterion は grep / test / 出力検査で機械的に確認できること
```

**ルール**:
- 本文 `## Success Criteria` セクションは **必須** (PLANS.md Required Sections に準拠)
- frontmatter は `completion-gate.py` が Ralph Loop 継続判定に使う **任意の補助索引**
- 既存 plan に対しては retroactive 強制なし (soft warning のみ)

## Wiring (依存関係)

```
┌────────────────────────────────────────────────────┐
│  User Request                                      │
└──────────────────┬─────────────────────────────────┘
                   ↓
         ┌─────────────────────┐
         │  /spec or /rpi      │   ← Plan 起票
         └──────────┬──────────┘
                    ↓ writes
         ┌─────────────────────┐
         │ docs/plans/active/  │   ← Anchor #1: Plan
         │  *.md (success_     │
         │  criteria + body)   │
         └──────────┬──────────┘
                    │
       ┌────────────┼────────────┐
       ↓            ↓            ↓
  ┌─────────┐  ┌─────────┐  ┌──────────────┐
  │/checkpoint│ │ Ralph    │  │ /commit      │
  │ skill    │  │ Loop +   │  │ skill        │
  │          │  │ completion│ │              │
  │ writes:  │  │ -gate.py │  │ reads plan   │
  │ HANDOFF  │  │ reads:   │  │ for context  │
  │ .md      │  │ success_ │  │              │
  │          │  │ criteria │  │              │
  └─────────┘  └─────────┘  └──────────────┘
       ↓                          ↓
  ┌──────────────────────────────────────┐
  │  Next session resume:                │
  │  1. Read HANDOFF.md (last state)     │
  │  2. Read plan (Success Criteria)     │
  │  3. Continue from "Next Steps"       │
  └──────────────────────────────────────┘
```

## Resume Protocol

新セッション開始時、または compact 後の resume では以下の順で anchor を参照:

1. **HANDOFF.md** が存在 → 直前セッションの "Next Steps" を読む
2. **`docs/plans/active/*.md`** から該当 plan の `## Success Criteria` で「何が done か」確認
3. **RUNNING_BRIEF.md** (あれば) で project 全体の決定履歴を把握
4. 残タスクを TaskCreate に展開、in_progress 状態のものから再開

## Anti-Patterns

- ❌ Success Criteria を「make it work」で書く → completion-gate が判定不能
- ❌ HANDOFF.md だけで resume しようとする → plan の global goal を失う
- ❌ Plan ファイルを `tmp/` に置きっぱなしにする → checkpoint 後に消失
- ❌ frontmatter の `success_criteria:` だけ書いて本文 `## Success Criteria` を省略 → PLANS.md contract 違反

## References

- `PLANS.md` — Required Sections 定義
- `.config/claude/skills/checkpoint/SKILL.md` — HANDOFF/RUNNING_BRIEF テンプレート
- `.config/claude/scripts/policy/completion-gate.py` — frontmatter 参照ロジック
- `.config/claude/references/model-routing.md` — End-to-End Completion 原則
- 由来: 「How I got banned from GitHub due to my harness pipeline」(2026-04) — anchor 喪失で pipeline が完走しなかった事例の翻訳
