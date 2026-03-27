# Definition of Done Template

> M/L 規模タスクの Plan 段階で binary pass/fail 基準を事前定義する。
> Anthropic Harness Design v2: End-state QA には「完成の定義」が必要。

---

## テンプレート

Plan の中に以下のセクションを含める:

### Definition of Done

**Layer 0（決定論的検証）**:
- [ ] テストが全て通過する（検証: `{test_command}`）
- [ ] lint エラーがない（検証: `{lint_command}`）
- [ ] 型チェックが通る（検証: `{typecheck_command}`）

**Layer 1（主観的評価）**:
- [ ] {機能要件 1}（検証: 目視確認 / レビュー）
- [ ] {機能要件 2}（検証: ...）
- [ ] {非機能要件}（検証: ...）

### ルール

1. **各項目は binary**: pass/fail で判定可能であること。「おおむね良い」は NG
2. **検証方法を明示**: 各項目に具体的な検証手段を記載
3. **Layer 0 を必ず含む**: 決定論的検証は省略不可
4. **適用レベル**: M/L 規模のみ。S 規模では省略可

### completion-gate.py との連携

- completion-gate.py が Plan 内の DoD セクションを検出
- 未チェック項目がある場合、advisory メッセージを出力
- Layer 0 項目が未達の場合、テスト未実行警告を強化

### 例

```
## Definition of Done

**Layer 0**:
- [x] `go test ./...` が全て通過する
- [x] `golangci-lint run` でエラーなし

**Layer 1**:
- [x] API エンドポイントが仕様通りのレスポンスを返す（検証: curl テスト）
- [ ] エラーメッセージが日本語化されている（検証: 目視確認）
```
