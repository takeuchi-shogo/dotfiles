---
status: active
last_reviewed: 2026-04-23
---

# Pre-mortem Checklist

> 出典: CREAO AI-First 統合 (2026-04-14) — 「批評を成果物にする」原理の具体化。
> criticism は会話の副産物ではなく pre-mortem / review / retrospective の 1st-class artifact として残す。

---

## When To Use

- **M/L 規模タスクの Plan フェーズ**で必ず実施
- **S 規模では省略可** だが、不可逆な変更（DB migration / API 公開 / 設定の破壊的変更）では S でも実施推奨
- `friction-events.jsonl` で同一 friction_class が 3 連続発生したとき、自動トリガされる（`improve-policy.md` Signal Routing R3）

`reversible-decisions.md` のチェックリストと**併用**する（差別化は末尾参照）。

---

## Checklist (5 項目)

Plan 策定の最後に、以下 5 項目に書面で答える:

### 1. この仮定が間違っていたら何が起きる？

Plan の中核仮定（最重要のもの 1-2 つ）を抜き出し、それが外れたときの影響を 1 文ずつ書く。

例:
- 仮定: 「security-reviewer の機能拡張が既存 prompt の recall を下げない」
- 外れた場合: 「review-findings.jsonl の AGREE 率が低下し、capability-score が自動で下がる」

### 2. 失敗モード 3 つを列挙

「この実装が想定通り動かないとしたら、どんな形で壊れるか」を最低 3 つ書く。

| # | 失敗モード | 兆候 | 検出方法 |
|---|-----------|------|---------|
| 1 | (例) 行数制約超過 | wc -l が 150 行超 | `task validate-configs` の wc check |
| 2 | (例) 既存テスト破壊 | review-findings.jsonl の AGREE 率低下 | `/improve` Garden phase |
| 3 | (例) 循環参照 | session が無限ループ | post-session metrics |

### 3. 反証条件 — 何が起きたらこの設計を捨てる？

「これが観測されたら設計を撤回する」という具体的なシグナルを書く。

例:
- /review が BLOCK verdict を連続 2 回出した
- review finding recall が ベースライン比 -10% 低下した
- 新責務追加で security-reviewer の実行時間が 2 倍以上になった

### 4. 撤退条件 — rollback / fallback / manual override

失敗が確定した場合の撤退手段を具体的に書く（手動操作のステップ、git revert の対象 commit、影響を受けるユーザー通知の方法）。

例:
- A2 の責務ドメイン化が既存 review flow を破壊 → triage-router.md の旧 3 並列ルールに `git revert <hash>` で戻し、A1+A3+B1+B3 のみで完了
- security-reviewer 拡張が失敗 → Core Responsibilities 8. のみ revert、他は維持

### 5. 既存 reversible-decisions.md との関係

reversible-decisions.md のチェックリスト（Why/What/Who/撤退条件/リスク要因/先行事例/反証）を埋めたかを確認する。
両者の責務は次のように分かれる:

| | reversible-decisions.md | pre-mortem-checklist.md (本ファイル) |
|---|---|---|
| **主軸** | 後戻りコスト (decision cost) | 失敗想定 (failure mode) |
| **問い** | 「やり直し可能か？投資上限は？」 | 「具体的にどう壊れる？何で気付く？」 |
| **アウトプット** | 撤退条件 + 反証 (1-2 行) | 失敗モード 3 つ + 反証条件 + 撤退手段 (詳細) |

→ **両方を実施し、Plan ドキュメントの "Risks" / "Pre-mortem" セクションに併記する**

---

## Output Format

Plan ドキュメント (`tmp/plans/{name}.md` または長時間/handoff タスクなら `docs/plans/{name}.md`) の Risks セクション直前に "Pre-mortem" セクションを追加する:

```markdown
## Pre-mortem (`references/pre-mortem-checklist.md`)

### 中核仮定
- [仮定 1]
- [仮定 2]

### 失敗モード
| # | 失敗モード | 兆候 | 検出方法 |
|---|---|---|---|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |

### 反証条件
- ...

### 撤退手段
- ...
```

---

## 既存システムとの接続

- **`improve-policy.md` Rule 43 (Principle Traceability)**: 全提案に `pre_mortem` フィールドを必須化済み。本 checklist はそのフィールドの埋め方を具体化したもの。
- **`improve-policy.md` Signal Routing R3**: friction-events 3 連続発生時に本 checklist を自動トリガ（1 セッション 1 回制限あり、循環参照防止）。
- **`reversible-decisions.md`**: 後戻りコスト観点と併用。両者は競合しない。
- **`agent-harness-contract.md` Operational Contract**: SOP 昇格時の Failure Branching 要素は、本 checklist の "失敗モード" と "撤退手段" を流用できる。
