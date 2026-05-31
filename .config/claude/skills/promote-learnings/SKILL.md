---
name: promote-learnings
description: patterns.jsonl の learned (運用ログから自動抽出された知見) を durable artifact (skill/reference/CLAUDE.md rule/policy) へ昇格させる。候補を提示し対話的に採否を決め、promoted-ledger.jsonl に記録して重複を防ぐ。Triggers: '昇格', 'learned 昇格', 'promote learnings', '学びを反映', '知見を取り込む'. Do NOT use for: 外部記事の取り込み (use /absorb)、コードレビュー (use /review)。
---

# Promote Learnings

運用ログ(patterns.jsonl)から溜まった `learned` を、再利用可能な artifact に昇格させる。

## Workflow

1. **候補を取得**: 次を実行し、未処理の昇格候補を得る。
   ```bash
   python3 ~/.claude/scripts/learner/extract-promotion-candidates.py
   ```
   `count` が 0 なら「pending な learned はありません」と報告して終了。

2. **トリアージ提示**: importance 降順で候補を最大 10 件ずつ提示する。各候補に:
   - `detail`(知見本文)、`scope`、`recommended_target`(初期推奨先)
   - これは「絞った absorb」と同じ。ユーザーに採否を聞く。

3. **採否と配置**: 採用する候補ごとに:
   - `recommended_target` が `(手動判断...)` なら、detail を読んで適切な昇格先(skill / references / CLAUDE.md rule / policy script)を Claude が提案し、ユーザーが承認する。
   - 採用なら実際に該当 artifact へ追記/編集する(該当ファイルを Read してから Edit)。
   - **誤爆防止**: 既存 artifact に同等内容が既にある場合は採用せず `decision:"rejected"`(理由: already covered)。

4. **ledger 追記**: 各候補の採否を記録する(冪等性のため必須)。
   ```bash
   CC_KEY="<候補の key>" CC_DECISION="adopted" CC_TARGET="<昇格先 path>" \
   python3 - <<'PYEOF'
   import os, sys
   sys.path.insert(0, os.path.join(os.path.expanduser('~'), '.claude/scripts/lib'))
   from session_events import append_to_learnings
   append_to_learnings("promoted-ledger", {
       "key": os.environ["CC_KEY"],
       "decision": os.environ["CC_DECISION"],
       "target_artifact": os.environ.get("CC_TARGET", ""),
   })
   PYEOF
   ```
   `decision` は `adopted` / `rejected` / `deferred`。`deferred` は「今回保留」(次回また候補に出る — 冪等キーは記録するが skip 扱いにしない場合は ledger に書かない選択も可。原則 deferred は書かず次回再提示)。

5. **報告**: 採用 N 件 / 棄却 M 件 / 各昇格先を要約する。artifact を変更したら `/review` を案内する。

## Notes
- ledger (`~/.claude/agent-memory/learnings/promoted-ledger.jsonl`) は追記専用。
- 一度 `adopted`/`rejected` した key は二度と候補に出ない(コアが照合)。
