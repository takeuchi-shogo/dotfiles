# Integration Rules - Stage 4

抽出した暗黙知を既存の knowledge-base.jsonl と突合するためのルール。

## Matching Algorithm

### Step 1: 類似度判定

新規抽出した知見と既存エントリを以下の基準で比較:

1. **domain 一致**: 同じ domain カテゴリかどうか
2. **意味的類似**: knowledge フィールドの意味的な近さ（LLM判定）
3. **方向性**: 同じ方向の知見か、矛盾する知見か

### Step 2: Verdict 判定

| Verdict | 条件 | アクション |
|---------|------|-----------|
| `new` | 既存indexに domain 一致かつ意味的に類似するエントリがない | 新規エントリとして追加候補に |
| `reinforce` | 既存エントリと同 domain・同方向 | 既存エントリの confidence を `min(existing + 0.05, 1.0)` に更新、sources に新セッションID追加 |
| `contradict` | 既存エントリと同 domain だが逆方向 | 両エントリにフラグ立て、Stage 6 の議論対象に |
| `promote` | 同 domain の active エントリが3件以上 | Layer 3（上位原則）への昇格候補としてマーク |

### Step 3: 昇格候補の判定

以下の条件をすべて満たす場合、昇格候補とする:
- 同一 domain に active な Layer 2 エントリが3件以上
- 各エントリの confidence がすべて 0.7 以上
- 矛盾するエントリ（contradict verdict）がない

## Prompt for LLM-based Matching

既存の knowledge-base.jsonl エントリと新規抽出した知見を比較し、各知見について verdict を判定してください。

### Input
- 新規知見: {extracted_knowledge}
- 既存エントリ: {existing_entries}

### Output
```yaml
verdicts:
  - knowledge_id: "tk-xxx"
    verdict: "new|reinforce|contradict|promote"
    matched_entry_id: "tk-yyy"  # reinforce/contradict の場合
    reason: "判定理由"
```
