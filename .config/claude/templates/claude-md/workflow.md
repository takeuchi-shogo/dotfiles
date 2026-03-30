## ワークフロー

タスク規模に応じてプロセスをスケールする:

| 規模  | 例                       | 必須段階                                                   |
| ----- | ------------------------ | ---------------------------------------------------------- |
| **S** | typo修正、1行変更        | Implement → Verify                                                        |
| **M** | 関数追加、バグ修正       | Plan → Risk Analysis → Implement → Test → Verify                          |
| **L** | 新機能、リファクタリング | Plan → Risk Analysis → Implement → Test → Review → Verify → Security Check |

```
Plan -> Risk Analysis -> Implement -> Test -> Review -> Verify -> Security Check -> Commit
失敗時:
- リスク分析で CRITICAL → Plan 修正
- テスト/検証/セキュリティ指摘 → Implement に戻る
- Review NEEDS_FIX → 修正 → 修正差分のみ再 Review（最大3回、PASS まで繰り返す）
- Review BLOCK → 修正 → フル再 Review（最大3回）
- Review NEEDS_HUMAN_REVIEW → ユーザーに判断を委ねる
- PASS → タスク完了をユーザーに報告
```

詳細なプロセス・エージェントルーティング・メモリシステム・トークン予算は
**`.config/claude/references/workflow-guide.md`** を参照。
