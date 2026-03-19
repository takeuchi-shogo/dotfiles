# Comprehension Debt ルール

AI 生成コードの理解債務を防ぐためのルール集。

---

## Tautological Test Detection

AI が実装とテストを同時生成した場合、テストが実装の「鏡像」になりやすい。
以下のパターンを検出したらテストの書き直しを求める。

### Bad Example: 実装の鏡像テスト

```typescript
// 実装
function calculateDiscount(price: number, tier: string): number {
  if (tier === 'gold') return price * 0.8;
  if (tier === 'silver') return price * 0.9;
  return price;
}

// Bad: 実装ロジックをテストにコピーしている
test('calculates discount', () => {
  expect(calculateDiscount(100, 'gold')).toBe(100 * 0.8);   // 実装の式をそのまま再現
  expect(calculateDiscount(100, 'silver')).toBe(100 * 0.9);
});

// Good: 期待値を独立して定義している
test('calculates discount', () => {
  expect(calculateDiscount(100, 'gold')).toBe(80);    // 具体的な値
  expect(calculateDiscount(100, 'silver')).toBe(90);
  expect(calculateDiscount(100, 'bronze')).toBe(100); // デフォルトケースも検証
});
```

### Bad Example: モック循環検証

```typescript
// Bad: モックの戻り値をそのまま検証（何も検証していない）
test('fetches user', async () => {
  const mockUser = { id: 1, name: 'test' };
  jest.spyOn(db, 'findUser').mockResolvedValue(mockUser);
  const result = await getUser(1);
  expect(result).toEqual(mockUser);  // モックが返したものがそのまま返る = tautology
});

// Good: モックは入力を制御し、出力の変換を検証する
test('fetches user and formats display name', async () => {
  jest.spyOn(db, 'findUser').mockResolvedValue({ id: 1, name: 'test' });
  const result = await getUser(1);
  expect(result.displayName).toBe('Test');  // 関数が何かを「変換」していることを検証
});
```

### Bad Example: ハードコード期待値コピー

```go
// Bad: 実装の定数をテストにコピー
func TestMaxRetries(t *testing.T) {
    // 実装に maxRetries = 3 と書いてあるから 3 と書いた
    if getMaxRetries() != 3 {
        t.Error("expected 3")
    }
}

// Good: 振る舞いを検証する
func TestRetriesExhausted(t *testing.T) {
    handler := newRetryHandler()
    for i := 0; i < getMaxRetries()+1; i++ {
        handler.attempt()
    }
    if !handler.isExhausted() {
        t.Error("expected handler to be exhausted after max retries")
    }
}
```

### Bad Example: 常に通る条件

```python
# Bad: 条件が常に真
def test_validation():
    result = validate(data)
    assert result is not None or result is None  # 常に通る
```

---

## Passive Delegation Detection

AI への「丸投げ」は理解債務を蓄積する最大の要因。

### 受動的委譲の兆候

| 兆候 | 具体例 |
|------|--------|
| レビューなし即 accept | AI 出力を読まずにそのまま採用 |
| 設計意図の説明不能 | 「なぜこのアプローチ？」に「AI が提案したから」としか答えられない |
| エラー丸投げ | 自分で調査せず「直して」と再依頼 |
| 変更の影響範囲が不明 | 何が壊れうるか説明できない |
| 代替案の不在 | 他のアプローチを検討した形跡がない |

### 対策

- **実装前**: Design Rationale を自分の言葉で書く
- **実装中**: 各変更の「なぜ」を説明できるか自問する
- **実装後**: 「この変更を明日の自分に説明できるか？」を確認する
