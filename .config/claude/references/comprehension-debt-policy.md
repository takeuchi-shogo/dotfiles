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

## Linear Walkthrough（M/L 規模で推奨）

AI 生成コードの理解を促進するため、M/L 規模の変更では Linear Walkthrough の生成を推奨する。

**Linear Walkthrough とは:**
AI 生成コードの処理フローを、エントリポイントから順に step-by-step で説明するドキュメント。コードを読む人間が「何がどの順序で起きるか」を線形に追跡できる。

**Design Rationale への追加項目:**
既存の「What / Why this approach / Risk mitigation」3点に加え、以下を含める:

4. **Walkthrough**: 処理フローの step-by-step 説明
   - エントリポイントはどこか
   - データがどう流れるか
   - 主要な分岐点と条件
   - エラーパスの扱い

**なぜ必要か:**
- AI 支援を受けた開発者の技能習得が 17% 低下するという研究結果（Comprehension Debt）
- 「テスト通った → ちらっと見て OK → マージ → 3日後にどう動いているか説明できない」パターンの予防
- Walkthrough を読む時間を確保することで、コードの理解と保守能力を維持する

**適用条件:**
- M 規模以上の新機能追加
- 複雑なロジック変更（条件分岐3つ以上、非同期処理、状態マシン）
- 他の開発者がレビューする変更

出典: 逆瀬川 "Coding Agent Workflow 2026" — Comprehension Debt / Linear Walkthrough セクション
