# Skill Archetypes — 新スキル作成時の型選択ガイド

## 判断フロー

```
スキルの主な役割は？
├─ 操作をブロック/確認する → Guard
├─ 複数ステップを順序実行する → Pipeline
├─ ファイルを生成する → Generator
├─ 知識を提供し判断を支援する → Knowledge Base
└─ 外部CLIツールをラップする → Tool Wrapper
```

## Archetype 定義

### 1. Guard（ガード型）
**役割**: 操作インターセプト、安全担保
**構造**: SKILL.md のみ
**例**: freeze, careful, verification-before-completion

### 2. Pipeline（パイプライン型）
**役割**: 複数フェーズの順序実行 + ゲート
**必須**: templates/ (出力フォーマット)
**推奨**: references/ (フェーズ別ガイド)
**任意**: scripts/ (自動化)
**例**: review, research, improve, absorb

### 3. Generator（ジェネレータ型）
**役割**: 構造化ファイル生成
**必須**: templates/ (出力テンプレート)
**任意**: scripts/ (データ収集), data/ (ドメインコンテンツ)
**例**: daily-report, eureka, spec, digest

### 4. Knowledge Base（知識ベース型）
**役割**: ドメイン知識の構造化、意思決定支援
**必須**: references/ (パターンカタログ)
**任意**: data/ (判断マトリクス), scripts/ (検証ツール)
**例**: senior-frontend, edge-case-analysis, react-best-practices

### 5. Tool Wrapper（ツールラッパー型）
**役割**: 外部CLIツールの最適な使い方を教える
**推奨**: scripts/ (ヘルパー), references/ (CLIリファレンス)
**任意**: examples/ (実行可能サンプル)
**例**: codex, gemini, webapp-testing

## 新スキル作成時の手順

1. 上記判断フローで archetype を選択
2. archetype の「必須」ディレクトリを作成
3. SKILL.md に `## Skill Assets` セクションで参照ポインタを記載
4. 「任意」は実際に必要になってから追加 (YAGNI)
