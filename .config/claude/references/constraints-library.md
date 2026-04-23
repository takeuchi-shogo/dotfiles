---
status: reference
last_reviewed: 2026-04-23
---

# 制約ライブラリ（Constraints Library）

Cursor の Self-Driving Codebase 研究で「制約は指示より効果的」と実証された。
曖昧な指示（「慎重に依存を追加して」）より、明確な制約（「明示的承認なしに新規依存を追加しない」）が
エージェントの出力品質を高める。

Golden Principles (GP-001〜005) が hook による自動検出用パターンなのに対し、
このファイルはプロンプトに注入して使うソフト制約。

## 使い方

`/autonomous`, `/spike`, `/epd` などでエージェントにタスクを委譲する際、
関連する制約を executor-prompt に含める。

```markdown
## Constraints
- {C-001 の内容をコピペ}
- {C-003 の内容をコピペ}
```

---

## C-001: 完全性の制約

- **制約**: No TODOs, no partial implementations, no placeholder comments
- **適用**: 全てのコード生成タスク

```
Do not leave TODOs, partial implementations, or placeholder comments.
Every function must be fully implemented and working.
```

## C-002: 依存管理の制約

- **制約**: 新規依存は明示的承認なしに追加しない。メジャーバージョンアップは人間レビュー必須
- **適用**: package.json, go.mod, Cargo.toml, requirements.txt 変更時

```
Do not add new dependencies without explicit approval.
Minor/patch updates may proceed. Major version updates require human review.
```

## C-003: スコープの制約

- **制約**: 指示された範囲以外のコードを変更しない。リファクタリングは依頼時のみ
- **適用**: 全タスク（特に autonomous 実行時）

```
Do not modify files outside the specified scope.
Do not refactor code unless explicitly asked.
```

## C-004: DB スキーマの制約

- **制約**: スキーマ変更は必ずマイグレーションファイルで行う。直接 ALTER TABLE 禁止
- **適用**: データベース関連タスク

```
All schema changes must use migration files. Never run ALTER TABLE directly.
Include rollback steps in every migration.
```

## C-005: API 互換性の制約

- **制約**: 既存の公開 API シグネチャを変更しない（breaking change 禁止）
- **適用**: API/ライブラリ開発

```
Do not change existing public API signatures (no breaking changes).
Deprecate first (add @deprecated), remove in the next major version.
```

## C-006: テストの制約

- **制約**: 新ロジックにはテストを書く。既存テストを削除・スキップしない
- **適用**: 全コード変更

```
Write tests for new logic. Do not delete or skip existing tests.
All tests must pass before committing.
```

## C-007: セキュリティの制約

- **制約**: シークレットをハードコードしない。ユーザー入力を直接埋め込まない
- **適用**: 全コード変更
- **施行**: Hybrid — `pre-commit-check.js` が `sk-`, `ghp_`, `AKIA` 等のシークレットパターンを検出しコミットをブロック。`permissions.deny` が `.env*`, `*.pem`, `*credentials*` の読み取りを禁止。加えてプロンプト注入

```
Never hardcode secrets or credentials. Use environment variables or secret managers.
Never interpolate user input directly into SQL, HTML, or shell commands.
```

## C-008: 並行実行の制約

- **制約**: 他エージェントが触っているファイルを変更しない。共有状態への書き込みを避ける
- **適用**: autonomous, parallel agent 実行時

```
Do not modify files that other agents are working on.
Avoid writing to shared state. Produce independent artifacts.
Stop and report if a conflict is detected.
```

## C-009: コミットの制約

- **制約**: 1コミット = 1論理的変更。WIP コミット禁止
- **適用**: git 操作を含むタスク

```
One commit per logical change. No WIP commits.
Use conventional commit format with emoji prefix.
```

## C-010: ドキュメントの制約

- **制約**: コード変更に伴う公開ドキュメントの更新を忘れない。無関係なドキュメントは触らない
- **適用**: 公開 API や README に影響する変更

```
Update public documentation affected by your code changes.
Do not modify documentation for code you did not change.
```

## C-011: Regression 防止の制約

- **制約**: 既存テストを全て通過させること。テストを削除・無効化して通過させることは禁止
- **適用**: 全コード変更（特に autonomous / background agent 実行時）
- **関連**: C-006 の強化版。C-006 は「テストを書け・消すな」の基本規約。C-011 は「full suite 実行・weaken 禁止・コード側を直せ」の厳格版
- **背景**: SWE-CI ベンチマーク (arXiv:2603.03823) で 75% のモデルが既存コードを壊すことが判明。テスト削除による偽の成功が主要パターン

```
All existing tests must pass after your changes. Do not delete, skip, or
weaken existing tests to make them pass. If a test fails, fix the code
(not the test) unless the test itself is wrong — and explain why.
Run the full test suite, not just tests for changed files.
```

---

## クイックリファレンス: ユースケース別推奨制約

| ユースケース | 推奨制約 |
|---|---|
| 全タスク共通 | C-001, C-003, C-007, C-009 |
| 依存更新 | + C-002 |
| DB マイグレーション | + C-004 |
| API 開発 | + C-005 |
| 機能実装 | + C-006 |
| 並列エージェント | + C-008 |
| ドキュメント影響あり | + C-010 |
| 全コード変更（特に autonomous） | + C-011 |
