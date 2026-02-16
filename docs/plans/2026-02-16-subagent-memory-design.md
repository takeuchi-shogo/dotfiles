# サブエージェントメモリ機能の追加

## 概要

全6つのカスタムエージェントに永続メモリを設定し、プロジェクト固有のパターン・規約を学習・蓄積させる。

## アプローチ

- 全エージェントの frontmatter に `memory: user` を設定（`~/.claude/agent-memory/<name>/` に保存）
- プロンプトにメモリ参照・記録の明示的指示を追加
- 各エージェント用の初期 MEMORY.md テンプレートを事前配置

## 変更対象

### エージェント定義ファイル（`.config/claude/agents/`）

| ファイル | frontmatter 変更 | プロンプト追加 |
|---|---|---|
| code-reviewer.md | なし（設定済み） | Memory Management セクション追加 |
| backend-architect.md | なし（設定済み） | Memory Management セクション追加 |
| frontend-developer.md | なし（設定済み） | Memory Management セクション追加 |
| golang-pro.md | なし（設定済み） | Memory Management セクション追加 |
| typescript-pro.md | なし（設定済み） | Memory Management セクション追加 |
| nextjs-architecture-expert.md | `memory: user` 追加 | Memory Management セクション追加 |

### 初期 MEMORY.md テンプレート（`~/.claude/agent-memory/<name>/MEMORY.md`）

各エージェントの専門分野に応じたセクション見出しを持つテンプレートを配置。

## メモリ指示の設計

各エージェントのプロンプト末尾に追加する共通構造:

```markdown
## Memory Management

作業開始時:
1. メモリディレクトリの MEMORY.md を確認し、過去の知見を活用する

作業完了時:
1. プロジェクト固有の<専門分野固有の項目>を発見した場合、メモリに記録する
2. 頻出する問題パターンがあれば記録する
3. MEMORY.md は索引として簡潔に保ち（200行以内）、詳細は別ファイルに分離する
```

## エージェント別記録対象

| エージェント | 記録対象 |
|---|---|
| code-reviewer | コーディング規約、頻出問題パターン、セキュリティ上の注意点 |
| backend-architect | API設計パターン、DB設計規約、インフラ構成の決定事項 |
| frontend-developer | コンポーネント設計パターン、UI規約、アクセシビリティルール |
| golang-pro | Go固有のパターン、エラー処理規約、パッケージ構成 |
| typescript-pro | 型設計パターン、tsconfig設定、命名規則 |
| nextjs-architecture-expert | ルーティング構成、データフェッチパターン、パフォーマンス設定 |
