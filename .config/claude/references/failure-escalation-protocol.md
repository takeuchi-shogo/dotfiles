# Failure Escalation Protocol — Issue + Worktree

セッション中に harness/tool 失敗・期待外挙動に遭遇した時、ワークアラウンドで進めずに **GitHub Issue + 別 worktree** に escalate するための判定プロトコル。

> CLAUDE.md core principles の **「壊れたら即STOP・ごまかし禁止」** + **「失敗 → capability gap → durable artifact」** を session-runtime に落とし込む。

## なぜ必要か

ワークアラウンドだけで進めると:

- 同じ failure が次回また発生する (Codex 不可で Gemini fallback → 次回また Codex 試して失敗)
- feedback memory に「次回どう逃げるか」を書くだけで根本修正への道が立たない
- Build to Delete 原則違反 (「何が改善されればこの避策は不要か？」が宙に浮く)
- 隠れた tech debt として蓄積する

## Escalation 判定基準

failure に遭遇した時、以下のトリガー表で判定する。**Yes が 1 つ以上**なら escalate。

| トリガー | 判定基準 | 例 |
|---|---|---|
| **再現性** | 同じ操作で同じ failure を 2 回以上観測した | Codex Bash-tool unreachable (TTY 不在 + silent exit) |
| **将来 block** | 今後の workflow (/absorb, /debate, /improve, /spike 等) を継続的に妨げる | Phase 2.5 Codex 批評が常時実行不能 |
| **修正候補あり** | 不確実でも仮説ベースの修正経路が 1 つ以上見える | pty wrapper / `script` コマンド / launch-worker headless mode |
| **harness の欠陥** | hook, script, settings.json, agent definition の bug / 設計不整合 | golden-check hook の false positive、agent ルーティング誤り |

### Escalate **しない** ケース

| ケース | 理由 |
|---|---|
| 一時的なネットワーク・API rate limit | Issue 化しても意味がない (再試行で解決) |
| ユーザー設定起因の typo / 名前違い | session 内で即訂正 (例: `gemini-3-pro` 存在せず → デフォルトモデルに切替) |
| Phase 1.5 saturation 等の "skip is correct" 判断 | 失敗ではなく設計通りの動作 |
| 一度きりの観測でパターン化していない事象 | 再現性確認後に再判定 |
| ユーザーが明示的に「今は進めて」と指示した | ユーザー判断を優先、session 末で再 surface |

## Escalation 手順

1. **session 内のワークアラウンドを完了する** (current task を完成させる、宙吊りにしない)
2. **failure を analysis report / feedback memory に記録** (証拠を残す: exit code, error message, 再現手順)
3. **`gh issue create` で Issue を立てる** (本文は下記テンプレ参照)
4. **`git worktree add` で別 worktree を切る** (branch 名: `fix/<issue-number>-<slug>`)
5. **新しい cmux pane で worktree に cd し調査開始** (現在 session は閉じてよい / 並行作業時は session を別保持)
6. **修正完了後 PR → main**、Issue close

### Issue テンプレート

```markdown
## 症状

- いつ: <YYYY-MM-DD HH:MM TZ>
- どこで: <session_id / workflow / skill name>
- 何をしたら: <再現手順>
- 期待: <期待挙動>
- 実際: <実際の出力 + exit code + error message>

## 影響範囲

- block されるワークフロー: </absorb Phase 2.5, /debate, ...>
- 頻度: <observed N times>
- 回避策: <現状のワークアラウンド (例: Gemini fallback)>

## 仮説と修正候補

- 仮説 1: <root cause hypothesis>
  - 修正候補: <具体的アプローチ>
- 仮説 2: ...

## Build to Delete

「何が改善されればこの Issue は不要か？」を 1 行で:
> <例: codex CLI が non-TTY モードで stdout に推論結果を返すようになれば不要>

## 関連

- feedback memory: <link>
- 関連 commit / session: <link>
```

## 例外: blast radius が大きい場合

Issue + worktree の手順自体がコスト過大な場合 (1 行 typo の修正、commit 1 つで終わる軽微な harness fix 等) は以下を許容:

- **直接 commit** (S 規模、reversible、harness 影響範囲 1 ファイル以内)
- ただし commit message に「failure observation」を含めて検索可能にする (`fix(harness): ...` + 本文に failure 内容)

判定不能なら escalate 側に倒す (Build to Delete + 「失敗 → durable artifact」原則優先)。

## このプロトコル自体の評価

「何が改善されればこのプロトコルは不要か？」:

> failure 検出時に hook が自動的に Issue draft + worktree branch を提案する mechanism が組まれれば、本プロトコルは「runbook → automation」に昇格して unload できる。現状は手動規律。
