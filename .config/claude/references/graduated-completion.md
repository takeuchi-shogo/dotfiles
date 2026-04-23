---
status: reference
last_reviewed: 2026-04-23
---

# Graduated Completion パターン

> Stripe Minions の知見: 「部分的に正しい成果でも価値を届ける」
> 週 1,300+ PR を無人生成するシステムで実証済み。完璧を待つより早く結果を返し、
> 「何ができて何ができなかったか」を構造化して人間にハンドバックすることが重要。

---

## 3段階の完成度

| レベル | 名前 | 条件 | アクション |
|--------|------|------|-----------|
| Full | 完全完了 | 全テスト通過、lint 通過 | 通常の完了フロー |
| Partial | 部分完了 | 一部成功、一部失敗 | ハンドバックレポート生成 → [WIP] PR 作成 |
| Blocked | 着手不能 | 実装開始できず | エラーレポートのみ → 人間に返却（PR なし） |

---

## ハンドバックレポートのフォーマット

```markdown
## Handback Report

### Status: Partial

### Completed
- [x] Task 1: description
- [x] Task 2: description

### Failed
- [ ] Task 3: description
  - Error: test failure in `test_foo.py::test_bar`
  - Attempted fixes: 2
  - Root cause (estimated): ...

### Recommended Actions
1. Review the failing test manually
2. The implementation for Task 3 is at `src/foo.py:42`
3. Consider: [specific suggestion]
```

ハンドバックレポートは `additionalContext` に注入し、エージェントが PR description に含める。

---

## Completion Mode 設定

環境変数 `COMPLETION_MODE` で動作を切り替える:

| 値 | 動作 |
|----|------|
| `strict`（デフォルト） | 従来動作。テスト失敗で block。`MAX_RETRIES` 到達で停止許可 |
| `graduated` | 部分完成を許容。`MAX_RETRIES` 到達時にハンドバックレポートを生成して停止 |

---

## いつ Graduated を使うか

| ユースケース | モード | 理由 |
|-------------|--------|------|
| Interactive セッション | strict | 人間が横にいる。即座にフィードバック可能 |
| `/autonomous` ヘッドレス | graduated | 無人実行。部分的でも PR があれば次のアクション可能 |
| CI / Background Agent | graduated | 非同期。完璧を待つより早く結果を返す |
| Security-critical な変更 | strict | 部分的な修正は危険 |

---

## PR の扱い

Partial 完成時の PR:

- **Title**: `[WIP] {original title}`
- **Body**: ハンドバックレポートを含む
- **Labels**: `wip`, `needs-human-review`
- **マージは人間が判断**: エージェントは PR を作るだけ。自動マージ禁止

---

## `/autonomous` との統合

`run-session.sh` のセッションループ完了時の判定:

1. 全タスク完了 → Full → 通常の PR
2. 一部完了 → Partial → `[WIP]` PR + ハンドバックレポート
3. 着手不能 → Blocked → エラーレポートのみ（PR なし）

`completion-gate.py` との関係:
- `strict` モード: 現行の `MAX_RETRIES` → 停止許可フローを維持
- `graduated` モード: `MAX_RETRIES` 到達時にハンドバックレポートを `additionalContext` に出力し、Partial 停止を許可

---

## 設計判断

- **デフォルトは strict**: 「壊さない」原則を優先。`graduated` は明示的 opt-in
- **Partial でも git commit は行う**: 作業の喪失防止。コミットメッセージに `[partial]` を付与
- **通知**: macOS notification + stdout メッセージでユーザーに状態を伝える
- **ハンドバックレポートの省略禁止**: 「何が失敗したか」がわからないと次のアクションが取れない

---

## Anti-Patterns

| NG パターン | 理由 |
|------------|------|
| `graduated` をデフォルトにする | 品質低下のリスク。opt-in であるべき |
| Partial PR を自動マージ | 人間のレビューが必須 |
| ハンドバックレポートを省略 | 次のアクションが取れなくなる |
| Blocked でも PR を作る | 着手不能なら PR の意味がない |

---

## 関連ドキュメント

- `scripts/policy/completion-gate.py` — 実装本体（`MAX_RETRIES` / `decision: block` フロー）
- `references/graded-guardrails.md` — completion-gate の変更リスクスコア設計
- `references/workflow-guide.md` — `/autonomous` セッションループの全体像
- `docs/agent-harness-contract.md` — hooks.Stop トリガー仕様
