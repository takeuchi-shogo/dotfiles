# Comprehension Debt Policy

AI 生成コードの「理解債務」を防ぐためのポリシー。
Addy Osmani の Comprehension Debt 記事 + Anthropic 研究（AI ユーザーの理解度 17% 低下）に基づく。

## Design Rationale (M/L 変更で必須)

M/L 規模の変更では、レビュー開始前に以下の 3 点を記述する。
S 規模（typo 修正、1 行変更）は免除。

```
1. **What**: この変更は何を解決するか
2. **Why this approach**: なぜこのアプローチを選んだか（却下した代替案含む）
3. **Risk mitigation**: 何が壊れうるか、どう防いでいるか
```

### 適用ルール

- Plan ファイルまたはコミットメッセージに Design Rationale を含める
- レビュー時に rationale が不十分な場合、`ask:` ではなく `must:` に昇格する
- 「なぜこのアプローチか」に対する回答が「動いたから」のみの場合は不十分と判定

### Good / Bad Example

**Good**:
```
1. What: ユーザー認証のセッション管理を JWT に移行
2. Why this approach: Session-based は水平スケーリングに不向き。
   OAuth2 は現時点で過剰（外部 IdP 不要）。JWT + refresh token が最小構成。
3. Risk mitigation: トークン漏洩リスク → 有効期限 15 分 + HttpOnly cookie。
   既存セッションの移行 → 2 週間の並行運用期間を設定。
```

**Bad**:
```
1. What: 認証を変更
2. Why this approach: JWT がモダンだから
3. Risk mitigation: 特になし
```
