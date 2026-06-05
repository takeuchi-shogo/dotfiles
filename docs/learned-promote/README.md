# learned-promote manifests

`run-learned-promote.sh` (nightly 週次) が生成する昇格 manifest の置き場。

## 役割

learned 昇格ループの **merge-coupled idempotency** を成立させる中核ファイル。

1. nightly が昇格候補を `claude -p` に非対話 promote させ、artifact (`.config/claude/...`)
   を編集 + この dir に `<RUN_ID>.json` (RUN_ID = `YYYYMMDD-HHMMSS`) を出力してブランチ/PR にする。
2. `claude -p` は **ledger を一切触らない**。昇格判断 (採否 + 昇格先) は manifest に記録される。
3. PR がマージされて manifest が master に到達すると、次回 nightly の reconcile
   (`reconcile-promoted-ledger.py`) が manifest の processed key を
   `~/.claude/agent-memory/learnings/promoted-ledger.jsonl` へ反映する。

これにより「PR をマージしなければ ledger に入らない = 却下した learned は再提案される」
という PR ゲートと冪等性の整合が取れる。**PR を close すれば key は ledger に入らない**。

## manifest schema

```json
{
  "date": "2026-06-06",
  "branch": "auto/learned-promote-20260606-013000",
  "max": 5,
  "promotions": [
    {"key": "<sha1>", "decision": "adopted", "scope": "...", "target_artifact": ".config/claude/...", "detail_excerpt": "..."},
    {"key": "<sha1>", "decision": "rejected", "scope": "...", "reason": "already covered: ...", "detail_excerpt": "..."}
  ]
}
```

reconcile は `adopted` / `rejected` の両方を processed として ledger に記録する
(rejected も「処理済み」= 再提案しない)。`key` は
`extract-promotion-candidates.py` が振る冪等キー (generalized_detail/detail の SHA1)。

## 設計

- プラン: `tmp/plans/typed-watching-mitten.md`
- 候補抽出: `.config/claude/scripts/learner/extract-promotion-candidates.py`
- reconcile: `.config/claude/scripts/learner/reconcile-promoted-ledger.py`
- 昇格 skill (対話版): `.config/claude/skills/promote-learnings/SKILL.md`
