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

> **モデル別 compaction 品質** (Anthropic "Harnessing Claude's Intelligence", 2026-04-02):
> Opus 4.6 = 84%, Sonnet 4.5 = 43%。Opus 4.6 では compaction 品質が大幅に向上しており、
> 過度な不信（Context Anxiety）自体が dead weight になりうる。閾値は定期的に見直すこと。
> 参照: `references/dead-weight-scan-protocol.md`

| 条件 | アクション |
|------|----------|
| Plan ステップが Compaction 後に欠落 | `[COMPACTION WARNING]` + session handoff 推奨 |
| 4 回以上の compaction で判断の一貫性低下 | `/checkpoint` + 新セッション推奨（Opus 4.6: 旧閾値 3→4 に緩和） |
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

## 参考: Observation Masking パターン

> JetBrains Junie (2026) が採用するコンテキスト最適化手法。
> Compaction とは異なるアプローチで context rot を軽減する。

**手法**: 古い tool output（ファイル内容、コマンド結果）を非表示にし、tool call 自体（何を実行したか）は残す。
これにより「何をしたか」の履歴は保持しつつ、中間結果の大量トークンを削減する。

**現状の適用**: Opus 4.6 の auto-compaction が類似の効果を提供しているため、ハーネス側での独自実装は不要。
ただし、サブエージェント設計では同等の原則を適用している — サブエージェントは広範に探索するが、
親に返すのは 1,000〜2,000 トークンの凝縮サマリのみ（tool output そのものは返さない）。

**将来の検討**: auto-compaction の品質が不十分な場合（Sonnet 4.5: 43%）、ハーネス側で
observation masking を実装する価値がある。その場合、tool_call メッセージは保持し、
tool_result メッセージのみを要約置換する方式を採る。
