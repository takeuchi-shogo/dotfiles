# AI Workflow Audit Checklist

## Skills
- [ ] Skills vs memory vs scripts 境界が適切か
- [ ] 重複スキルがないか
- [ ] description が正確でトリガーが適切か
- [ ] 未使用スキルがないか

## Agents
- [ ] エージェント定義にドメイン知識が50%以上含まれるか
- [ ] ルーティング条件が明確か
- [ ] 不要なエージェントがないか

## Hooks
- [ ] 必要なフィードバックループが実装されているか
- [ ] hook 間の依存関係が明確か
- [ ] エラーハンドリングが適切か

## Memory
- [ ] MEMORY.md が200行以内か
- [ ] 陳腐化したメモリがないか
- [ ] 重複エントリがないか

## Configuration
- [ ] CLAUDE.md が簡潔か（指示数 < 50）
- [ ] Progressive Disclosure が守られているか
- [ ] 言語別ルールが整備されているか
