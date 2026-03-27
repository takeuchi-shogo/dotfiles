# Context Compaction Policy

> Opus 4.6 の auto-compaction に依存しつつ、品質劣化を検知するポリシー。
> Anthropic Harness Design v2: Context Anxiety は長時間エージェントの主要失敗モード。

---

## 監視指標

### Compaction 前後の情報保持

以下の情報が Compaction 後も保持されているか確認する:

1. **Plan のステップ一覧**: アクティブな Plan の全ステップが参照可能か
2. **Definition of Done**: DoD の全項目が参照可能か
3. **Key Decisions**: セッション中の重要な意思決定（技術選定、スコープ変更）が保持されているか
4. **Dead Ends**: 試して失敗したアプローチの記録が保持されているか

### 品質劣化の兆候

以下のパターンが現れた場合、Context Anxiety による品質劣化の可能性がある:

- **同じ質問の繰り返し**: 既に回答済みの質問を再度する
- **矛盾する判断**: Compaction 前後で異なる判断を下す
- **Plan からの逸脱**: 合意した Plan のステップを飛ばす、または異なる順序で実行する
- **情報の再発見**: 既に読んだファイルを再度読み、同じ発見をする

## Fallback トリガー

| 条件 | アクション |
|------|----------|
| Plan ステップが Compaction 後に欠落 | `[COMPACTION WARNING]` + session handoff 推奨 |
| 3 回以上の compaction で判断の一貫性低下 | `/checkpoint` + 新セッション推奨 |
| Dead Ends の記録が消失 | HANDOFF.md の Dead Ends セクションを再確認 |
| DoD が参照不能 | Plan ファイルから DoD を再読み込み |

## PostCompact チェック

PostCompact hook 発火時に以下を確認（advisory）:
- アクティブな Plan ファイルのパスが session state に保持されているか
- 直近の key decision が参照可能か

## 緩和策

- **長時間タスク**: 30 分以上の作業では `/checkpoint` を定期的に実行
- **L 規模タスク**: Plan を docs/plans/ に書き出し、Compaction の影響を受けないようにする
- **Critical な意思決定**: memory system に保存し、Compaction 後も参照可能にする
