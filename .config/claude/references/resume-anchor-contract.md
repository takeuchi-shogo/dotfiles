---
status: reference
last_reviewed: 2026-04-23
---

# Resume Anchor Contract

**目的**: セッション中断・compact・複数セッション跨ぎでも作業を確実に再開するための「anchor」の規約。
End-to-End Completion 原則 (`model-routing.md`) を支える土台。

## 3 つの anchor

| Anchor | スコープ | 配置 | 寿命 | Owner |
|--------|---------|------|------|-------|
| **Plan (Success Criteria)** | プロジェクト/タスク全体 | `docs/plans/active/*.md` | 完了まで永続 | ExecPlan Contract (`PLANS.md`) |
| **HANDOFF.md** | 1 セッション | `tmp/HANDOFF.md` (worktree なら root) | 次セッション開始まで | `skills/checkpoint` |
| **RUNNING_BRIEF.md** | プロジェクト全体 (累積) | プロジェクト root | プロジェクト寿命 | `skills/checkpoint brief` |

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
