---
status: reference
last_reviewed: 2026-10-13
---

# Failure → Skill Loop

失敗イベントを skill 候補に落とす運用手順。
`failure-taxonomy.md`（分類）と `edit-failure-tracker.py`（Edit/Write 失敗の計測）は既にあるが、
**候補化 → skill 草案 → eval → merge** の手順が無かったため、ここを正本にする。

> 出典（読めた範囲）: [@distortgeekin](https://x.com/distortgeekin/status/2109637916922159360)
> 添付画像 "Lauren Tan's 12 Rules"
>
> - Rule 02: Attach proof… **No proof, no merge.**
> - Rule 10: Every failure I catch becomes a skill, written the same day.
> - Rule 11: Every skill gets an eval, judged by a different model…
>
> Caveat: 投稿テキストは 3 行要約のみ。12 条全文は画像。本手順は画像から確認できた
> Rule 02 / 10 / 11 に限定する（他ルールの全文転載・捏造はしない）。

## Inputs（既存）

| ソース | 役割 | パス |
|--------|------|------|
| Failure Taxonomy | FM 定義・recoveryType・suggestedFix | `.config/claude/references/failure-taxonomy.md` |
| Edit Failure Tracker | Edit/Write 失敗を `failure_pattern` 付きで session_events へ | `.config/claude/scripts/learner/edit-failure-tracker.py` |
| Failure Escalation | 再現性のある harness 失敗を Issue+worktree へ | `.config/claude/references/failure-escalation-protocol.md` |
| Skill Audit | A/B・5D・Gotchas 昇格 | 本 skill (`SKILL.md`) |

## Procedure

### 1. 証拠を集める（No evidence → 候補にしない）

最低 1 つ:

- session_events の error（`failure_pattern` / `failure_mode` / 再現メッセージ）
- CI / `task validate-*` / pytest の失敗ログ（決定的な 1 行を verbatim）
- 人間が同一失敗を 2 回以上観測した記録（escalation protocol の「再現性」）

証拠が無い失敗談・感想だけでは skill 候補にしない。

### 2. Taxonomy に載せる / 突き合わせる

1. `failure-taxonomy.md` の既存 FM に当てはまるか検索する
2. 当てはまる → その FM の `suggestedFix` / Graph vs Prompt 診断を使う
3. 当てはまらない → Open Coding メモを `insights/failure-taxonomy-proposals.md` 候補に残し、
   **まず FM 追加を検討**してから skill 化（taxonomy が先、skill が後）

Edit/Write 経路: `edit-failure-tracker.py` の `_classify_failure` が出す
`str_replace_mismatch` / `file_not_found` 等をクラスタキーにする。

### 3. Skill 候補の形を決める

優先順位（環境を先に直す。読めない「12 rules 全体」ではなく、既存 harness 方針と整合）:

1. architecture / data / types で起きなくする
2. lint / hook / test / CI で機械的に止める
3. 残る判断だけを skill / Gotchas / reference に書く

Skill 候補カード（必須欄）:

```markdown
## Skill candidate
- Observed failure: <verbatim 1 line + source path>
- FM / pattern: <FM-xxx or edit-failure pattern>
- Evidence count: <N>=2 recommended>
- Proposed durable artifact: <skill | Gotchas | hook | lint | test>
- Eval plan: <skill-audit A/B or fixture>
- Proof for merge: <command that must pass>
```

### 4. 当日中に草案を書く（Rule 10 の運用解釈）

「written the same day」は画像文言。本 repo では:

- 当日中に **候補カード + 最小 durable 断片**（Gotchas 1 行、または skill stub、または failing test）まで書く
- 完全な skill + A/B 完了までは必須にしない（コスト）。未完了なら候補カードに残し、
  `/skill-audit` の Promotion Backlog へ載せる

### 5. Eval してから merge（Rule 11 + No proof, no merge）

- 新規/改修 skill は `skill-audit` の A/B（または fixture pytest）で効果を測る
- **proof が無い PR は merge しない** — `docs/agent-harness-contract.md` の Merge Criteria
- 異なるモデルでの採点は推奨だが、環境に無い場合は「単一モデル eval + 人間レビュー」と明記し、
  「10/10 達成」を捏造しない

## Anti-patterns

- ✗ 失敗を「次は気をつける」prompt だけで閉じる → ✓ durable artifact か Issue
- ✗ 証拠 0 件で skill を増やす → ✓ Inputs 表のどれかを必須
- ✗ taxonomy を無視して毎回新規 skill 名を作る → ✓ FM / pattern キーでクラスタ
- ✗ green CI のみを proof とする → ✓ 変更面に最も近い validation を選ぶ

## Wiring

- `/skill-audit` 実行時: Promotion Backlog に加え、session_events 由来の
  `failure_pattern` 上位を「Failure→Skill candidates」節に列挙してよい
- harness contract: Merge Criteria（No proof, no merge）
- create-skill playbook: 本手順の候補カードを Step 1 前の入力として使う
