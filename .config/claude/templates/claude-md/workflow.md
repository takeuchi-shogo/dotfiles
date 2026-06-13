## ワークフロー

| 規模  | 例                       | 必須段階                                                                                                          |
| ----- | ------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| **S** | typo修正、1行変更        | Implement → Review (tier-based: light=Verify のみ / standard 以上=Codex Review Gate 含む) → Verify                |
| **M** | 関数追加、バグ修正       | Plan → Codex Spec/Plan Gate → Edge Case Analysis → Implement → Test → Codex Review Gate → Verify                  |
| **L** | 新機能、リファクタリング | Plan → Codex Spec/Plan Gate → Edge Case Analysis → Implement → Test → Codex Review Gate → Verify → Security Check |

失敗時のループ・エージェントルーティング・メモリシステム・トークン予算は `references/workflow-guide.md` を参照。

tier (light/standard/deep) の定義と判定は skills/review/SKILL.md Step 0 を参照。
