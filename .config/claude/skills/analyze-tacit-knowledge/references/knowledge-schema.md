# Knowledge Base Schema

## knowledge-base.jsonl

1行1エントリの JSONL 形式。各エントリは1つの暗黙知を表す。

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | 一意ID。形式: `tk-YYYYMMDD-NNN` |
| knowledge | string | yes | 暗黙知の内容（自然言語） |
| gap | string | yes | AIの出力とユーザーの期待のズレ |
| user_correction | string | yes | ユーザーの修正指示 |
| domain | string | yes | ドメインカテゴリ（例: `content-creation/tone`） |
| layer | number | yes | 知識レイヤー（2: スキルルール/個別の学び, 3: 上位原則） |
| confidence | number | yes | 確信度 0.0-1.0 |
| sources | string[] | yes | 検出元セッションID |
| created | string | yes | 作成日 ISO 8601 |
| updated | string | yes | 更新日 ISO 8601 |
| applied_to | string[] | no | 反映先ファイルパス |
| status | string | yes | `active`, `promoted`, `superseded` |

### Example

```jsonl
{"id":"tk-20260322-001","knowledge":"受け手に判断を委ねるスタンス。処方的表現は信頼を損なう","gap":"AIが処方的トーンで書いた（〜すべき）","user_correction":"確信の表明だけで止める。行動指示はしない","domain":"content-creation/tone","layer":2,"confidence":0.85,"sources":["session-abc123"],"created":"2026-03-22","updated":"2026-03-22","applied_to":[],"status":"active"}
```

### Verdict Types (Stage 4 Integration)

| Verdict | Condition | Action |
|---------|-----------|--------|
| new | 既存indexに類似なし | 新規エントリ追加 |
| reinforce | 同domain・同方向の既存あり | confidence上昇、sources追加 |
| contradict | 既存と逆方向 | フラグ立て、Stage 6議論対象 |
| promote | 同domainの知見3件以上 | Layer 3昇格候補 |
