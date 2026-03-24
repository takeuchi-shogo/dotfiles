# Session Protocol

セッション境界を明確にし、マルチセッション開発の一貫性を保つプロトコル。

## Session Start Protocol

セッション開始時に `session-load.js` が自動実行する項目:

1. **前セッション状態の復元** — `last-session.json` or `HANDOFF.md`
2. **アクティブプラン確認** — `docs/plans/active/`, `tmp/plans/`
3. **Feature List 確認** — `feature_list.json` が存在すれば次の未完了機能を表示
4. **Progress Log 確認** — `progress.log` が存在すれば直近エントリを表示
5. **テストベースライン** — テストランナー検出と実行提案
6. **Learnings ロード** — タスク関連の過去の学びを表示

## Session End: Clean State Definition

セッション終了時に目指す状態（**main マージ可能レベル**）:

- [ ] `git status` がクリーン（uncommitted changes なし）
- [ ] テストが全パス
- [ ] `feature_list.json` の `passes` 状態が実際のテスト結果と一致
- [ ] `progress.log` にセッションの作業内容が記録済み
- [ ] `HANDOFF.md` が不要（全作業がコミット済み）

`completion-gate.py` が上記を advisory（警告のみ）でチェックする。

## State Persistence: 棲み分け

| 仕組み | スコープ | 寿命 | 用途 |
|--------|----------|------|------|
| **memory** (MEMORY.md) | グローバル / プロジェクト | 永続 | セッション横断の学び・パターン |
| **progress.log** | プロジェクト固有 | プロジェクト寿命 | 時系列の作業ファクト記録 |
| **checkpoint** | セッション | 短期（5世代保持） | セッション再開用の runtime state |
| **HANDOFF.md** | セッション間 | 次セッションまで | セッション引き継ぎの作業コンテキスト + 失敗アプローチ記録 |
| **feature_list.json** | プロジェクト固有 | プロジェクト寿命 | 機能単位の構造化進捗管理 |
| **Plan** (docs/plans/) | プロジェクト固有 | タスク寿命 | Goal/Scope/Validation/Decision の記録 |

## Dead-End Prevention (失敗アプローチ記録)

> Ref: "Long-Running Claude" — "Without them, successive sessions will re-attempt the same dead ends."

セッション跨ぎの長時間タスクでは、失敗したアプローチを構造的に記録する:

1. **記録場所**: `HANDOFF.md` の「3.5. 失敗したアプローチ (Dead Ends)」セクション
2. **記録タイミング**: アプローチを試して失敗した直後（記憶が新鮮なうちに）
3. **必須項目**: アプローチ名、失敗理由、次セッションへの学び
4. **セッション開始時**: `HANDOFF.md` の Dead Ends セクションを必ず確認し、同じアプローチを再試行しない

## Session Granularity Rules

`feature_list.json` が存在する L 規模プロジェクトでは:

- **1 セッション 1 機能** に集中する
- 同一セッションで複数機能を完了させない（コンテキスト喪失のリスク）
- S/M 規模タスクにはこのルールを適用しない（過剰制約を避ける）
- `completion-gate.py` が 2 機能以上の同時完了を検出した場合、警告を出す
