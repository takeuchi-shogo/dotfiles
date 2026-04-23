---
status: active
last_reviewed: 2026-04-23
---

# Decision Journal — 軽量決定ログ

> 日常の設計・ワークフロー決定を記録し、結果を追跡する。
> ADR（docs/adr/）はアーキテクチャ決定用。こちらは軽量な日常決定用。
>
> `/timekeeper review` で outcome の振り返りを促す。
> `/improve` の Garden フェーズで outcome 未記入の古いエントリをリマインドする。

## フォーマット

```
### [YYYY-MM-DD] 決定タイトル

- **状況**: 何がきっかけか
- **選択**: 何を選んだか
- **根拠**: なぜそれを選んだか（参照: knowledge-pyramid tier, memory ファイル等）
- **期待結果**: 何が起きると予想するか
- **実際結果**: _（後で記入: good / bad / mixed + 1行説明）_
```

## 記入ルール

1. 可逆な小さい決定は記録不要（変数名、import 順序など）
2. 記録すべき決定: ツール選定、ワークフロー変更、設計パターン選択、スキル/hook の追加・削除
3. outcome は 1-2 週間後に振り返って記入
4. good outcome → 根拠に使った知見の tier を昇格検討
5. bad outcome → 根拠に使った知見の tier を降格検討 + lessons-learned.md に 1 行追記

---

## ログ

_（新しいエントリを上に追記する）_
