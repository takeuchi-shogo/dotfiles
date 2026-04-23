# ADR-NNNN: {{DECISION_TITLE}}

- **Status**: Proposed / Accepted / Deprecated / Superseded by ADR-XXXX
- **Date**: {{YYYY-MM-DD}}
- **Deciders**: @{{DECIDER_1}}, @{{DECIDER_2}} ...
- **Consulted**: @{{CONSULTED_1}} ...
- **Informed**: {{ZONES_OR_PEOPLE_TO_NOTIFY}}

---

## Context

（この決定が必要になった背景・問題・制約を書く。過去の経緯・関連する障害・市場環境など）

## Decision

（「我々は X を採用する」という一文 + 補足。抽象的でなく具体的に）

例: 「認証には JWT + refresh token rotation を採用する。session cookie は使わない。」

## Rationale

なぜそれを選んだか。以下を含める:
- 技術的根拠（性能/スケール/保守性）
- 事業的根拠（cost/time-to-market）
- リスク軽減（セキュリティ/信頼性）

## Alternatives Considered

| 選択肢 | Pros | Cons | 却下理由 |
|-------|------|------|---------|
| A. {{ALT_A}} | ... | ... | ... |
| B. {{ALT_B}} | ... | ... | ... |

## Consequences

- **Positive**: （この決定がもたらすメリット）
- **Negative**: （トレードオフ・技術的負債）
- **Mitigation**: （negative への対応策）

## Validation / Exit Criteria

- **採用後の成功指標**: （何が改善されれば正しかったと判定できるか）
- **撤退条件**: （どうなったら別案に切り替えるか）

## Related

- ADR-XXXX: ...
- Issue / PR: #XXX
- External reference: {{URL}}

---

**Update History**:
- {{YYYY-MM-DD}}: Proposed by @{{AUTHOR}}
- {{YYYY-MM-DD}}: Accepted after team review
- ...
