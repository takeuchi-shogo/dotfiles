---
name: autocover
description: "テスト自動生成パイプライン。カバレッジ分析 → ギャップ特定 → テスト生成 → 実行 → 結果報告。Triggers: '/autocover', 'テスト生成', 'カバレッジ改善', 'uncovered functions'. Do NOT use for: 手動テスト設計（use test-engineer agent）、既存テストの修正（use debugger）。"
origin: self
metadata:
  pattern: pipeline
disable-model-invocation: true
---

# Autocover - Test Auto-Generation Pipeline

カバレッジレポートを起点に、未テスト関数を特定し、テストを自動生成するパイプライン。
Uber Autocover パターンに基づく。

## Usage

```
/autocover [target_dir]
```

- `target_dir`: テスト生成対象のディレクトリ（省略時はプロジェクトルート）

## Blueprint

詳細なノード定義: `references/blueprints/autocover.yaml`

## Workflow

### Phase 1: カバレッジ分析

1. プロジェクトのテストフレームワークを自動検出:
   - `package.json` → Jest / Vitest / Mocha
   - `pytest.ini` / `pyproject.toml` → pytest
   - `go.mod` → go test
   - `Cargo.toml` → cargo test
2. カバレッジレポートを生成（既存のカバレッジコマンドがあれば使用）
3. ファイル別・関数別のカバレッジ率を集計

### Phase 2: ギャップ特定

1. カバレッジ 0% のファイル/関数を優先リスト化
2. 以下の優先度でソート:
   - **P1**: 公開 API / エクスポート関数（利用者に影響）
   - **P2**: エラーハンドリングパス（障害耐性）
   - **P3**: ビジネスロジック（正確性）
   - **P4**: ユーティリティ関数
3. 生成対象を上位 10 関数に絞る（1回のセッションで管理可能な量）

### Phase 3: テスト生成

1. 対象関数のソースコードと既存テストパターンを読み込む
2. プロジェクトの既存テストスタイルに合わせてテストを生成:
   - Arrange-Act-Assert パターン
   - Happy path + Edge cases + Error cases
   - 既存のモック/フィクスチャパターンを踏襲
3. テストファイルをプロジェクト規約に従った場所に配置

### Phase 4: 実行・検証

1. 生成したテストを実行
2. 失敗したテストを修正（最大 3 イテレーション）
3. 全テスト（既存 + 新規）がパスすることを確認

### Phase 5: 結果報告

```
## Autocover Report

### Generated Tests
- `src/utils/__tests__/parser.test.ts` — 3 tests (parse, parseError, parseEmpty)
- `src/api/__tests__/handler.test.ts` — 5 tests (get, post, auth, 404, 500)

### Coverage Change
- Before: 62% → After: 78% (+16%)

### Skipped (manual review recommended)
- `src/db/migration.ts` — DB 依存、integration test が適切
```

## Constraints

- 既存テストを変更しない（新規追加のみ）
- テストフレームワークを変更しない（プロジェクト既存のものを使用）
- 1 セッションで生成するテストは最大 10 関数分
- mutation testing は任意（ツールがインストールされている場合のみ）

## Anti-Patterns

| NG | 理由 |
|----|------|
| テストフレームワークを勝手に変更する | プロジェクト既存のフレームワークを尊重する |
| 1セッションで10関数超のテストを生成する | 品質が下がる。最大10関数分の制約を守る |
| 生成テストを検証せずにコミットする | 誤ったアサーションは偽の安心感を生む。必ず実行して確認 |
