# Claude Code グローバル設定

## 基本方針

- **サブエージェント・スキルを積極的に活用する**
- **独立したタスクは並行処理で効率化する**
- **日本語で応答する**

## サブエージェントの活用

以下のサブエージェントを適切な場面で積極的に使用すること：

| Agent | 用途 |
|-------|------|
| `typescript-pro` | TypeScript開発、型定義、リファクタリング |
| `golang-pro` | Go開発、並行処理、パフォーマンス最適化 |
| `backend-architect` | バックエンドAPI設計、システム構成 |
| `frontend-developer` | フロントエンド実装、コンポーネント開発 |
| `code-reviewer` | コードレビュー、品質チェック |

### サブエージェント使用ルール

1. **コード変更後は `code-reviewer` でレビューを実行**
2. **複数ファイルの調査は `Explore` エージェントを使用**
3. **言語固有の最適化には専用エージェントを使用**（TypeScript → `typescript-pro`、Go → `golang-pro`）
4. **設計判断が必要な場合は `backend-architect` または `Plan` エージェントを使用**

## スキルの活用

以下のスキルを適切な場面で呼び出すこと：

| Skill | 用途 |
|-------|------|
| `senior-frontend` | React/Next.js開発、パフォーマンス最適化 |
| `senior-backend` | API開発、DB最適化、セキュリティ |
| `senior-architect` | システム設計、アーキテクチャ図作成 |
| `react-best-practices` | Reactパフォーマンス最適化、ベストプラクティス |
| `frontend-design` | UI/UXデザイン、コンポーネントスタイリング |
| `code-reviewer` | コードレビュー、セキュリティチェック |
| `git-commit-helper` | コミットメッセージ生成 |

## 並行処理

以下の場合は並行処理を行うこと：

1. **複数ファイルの読み込み** - 依存関係がなければ並列でRead
2. **複数の検索** - Glob/Grepを並列実行
3. **独立したサブエージェント** - 複数のTaskを同時起動
4. **テストとリント** - 並列で実行可能

```
# 例: 並行処理が適切な場面
- フロントエンドとバックエンドの同時調査
- 複数コンポーネントの同時レビュー
- テスト実行とコード解析の同時実行
```

## ワークフロー

### 新機能開発
1. `Plan` または `senior-architect` で設計
2. 適切な専門エージェント（`typescript-pro`、`frontend-developer`等）で実装
3. `code-reviewer` でレビュー
4. `git-commit-helper` でコミット

### バグ修正
1. `Explore` で問題箇所を調査
2. 専門エージェントで修正
3. `code-reviewer` で確認

### リファクタリング
1. `senior-architect` で方針決定
2. 専門エージェントで実装
3. `code-reviewer` で品質確認

## コード品質

- 実装完了後は必ず `code-reviewer` エージェントまたはスキルを実行
- セキュリティ・パフォーマンス・保守性を確認
