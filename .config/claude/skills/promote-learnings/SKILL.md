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
   - **多様性チェック (echo chamber 抑制)**: バッチの昇格候補が**同一 scope / 同じ結論に偏っている**場合、その方向だけを強化していないか一度立ち止まる。既存 memory に**矛盾・反証する** learned が混じっていたらそれを優先的に採否検討する(反証は monoculture を崩す価値が高い)。同一 scope の連続昇格が 3 バッチ以上続く、または反証 learned を恒常 reject していると気づいたら、design doc(`docs/superpowers/specs/2026-05-31-learned-promotion-loop-design.md` リスク3)の watch 条件に従い自動ガード配線を起票する。

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
   `decision` は `adopted` / `rejected` の2値のみ。**今回保留したい候補は ledger に書かない**(次回 /promote-learnings で再提示される。コアは ledger の key を見て skip するため、deferred を書くと永久に再提示されなくなる)。

   **書き込み検証 (Fail Fast)**: `append_to_learnings` は失敗を握り潰すため、追記後に必ず確認する:
   ```bash
   grep -q "\"$CC_KEY\"" ~/.claude/agent-memory/learnings/promoted-ledger.jsonl \
     || { echo "ledger 追記失敗: $CC_KEY"; exit 1; }
   ```
   見つからなければ即中断しユーザーに報告する(冪等性が壊れ、採用済み報告が嘘になるのを防ぐ)。

5. **報告**: 採用 N 件 / 棄却 M 件 / 各昇格先を要約する。artifact を変更したら `/review` を案内する。

## Notes
- ledger (`~/.claude/agent-memory/learnings/promoted-ledger.jsonl`) は追記専用。
- 一度 `adopted`/`rejected` した key は二度と候補に出ない(コアが照合)。
