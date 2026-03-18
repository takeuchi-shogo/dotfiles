---
name: continuous-learning
description: >
  Auto-detect and record reusable patterns from corrections, debugging, and repeated work.
  Triggers: user corrections ('no not that', 'instead do', 'don't do X'), recurring patterns (same fix applied 2+ times),
  new project conventions discovered during work, debugging insights worth preserving.
  Do NOT use for one-off fixes or task-specific context — use memory system instead.
allowed-tools: "Read, Bash, Grep, Glob"
metadata:
  pattern: pipeline
---

# Continuous Learning

## Trigger

以下の状況で自動的に発動する:

- ユーザーから修正フィードバックを受けた
- 同じ種類のバグを2回以上修正した
- プロジェクト固有の規約・パターンを発見した
- デバッグで有用な手順を確立した
- レビューで繰り返し指摘されるパターンを検出した

## Workflow

### 1. Detect Pattern

修正・フィードバック・繰り返しを検知したら、以下を評価:

| 質問 | Yes → 記録対象 |
|------|---------------|
| 同じミスを2回以上した？ | パターンとして記録 |
| ユーザーが明示的に「覚えて」と言った？ | 即座に記録 |
| プロジェクト固有の規約を発見した？ | 規約として記録 |
| デバッグ手順が3ステップ以上？ | 手順として記録 |
| レビューで同じ指摘が2回？ | アンチパターンとして記録 |

### 1.5. 帰納的に分類する（ブレストしない）

パターンの分類は、観察から帰納的に導出する。事前にカテゴリを定義しない。

- 表面的に似ていても根本原因が異なるなら分割
- 根本原因が同じなら、表現が異なってもグルーピング
- **最初に壊れた箇所に注目** — エラーはカスケードするため、根本原因を特定する

詳細な手法は `references/error-analysis-methodology.md` を参照。

### 2. Classify

記録するパターンを分類:

- **convention**: プロジェクト固有の規約（命名、ファイル配置、ツール使い方）
- **debug-pattern**: デバッグ手順・トラブルシューティング
- **anti-pattern**: 避けるべきパターン（やってしまいがちなミス）
- **tool-usage**: ツール・ライブラリの効果的な使い方
- **preference**: ユーザーの好み・ワークフロー

### 3. Record

記録先の判断:

```
MEMORY.md に追記（索引として1-2行）
  → 詳細が必要なら別ファイルに分離
    例: debug-patterns.md, conventions.md, anti-patterns.md
```

記録フォーマット:

```markdown
## [分類]: [パターン名]
- **状況**: いつ発生するか
- **対処**: 何をすべきか
- **理由**: なぜそうするか（省略可）
```

### 4. Validate Before Writing

記録前に必ず確認:

1. **重複チェック**: 既存の MEMORY.md と詳細ファイルを読み、同じ内容がないか確認
2. **正確性**: 1回の観察ではなく、複数の証拠があるか（ユーザー明示指示は除く）
3. **機密情報**: token, password, secret が含まれていないか
4. **簡潔性**: MEMORY.md は200行以内を維持

### 5. Apply

次回以降、記録したパターンを積極的に活用:

- 作業開始時に MEMORY.md を確認
- 関連パターンがあれば事前に適用
- パターンが古くなっていたら更新・削除

## Anti-Patterns

- 1回しか起きていない事象を一般化して記録しない
- セッション固有の情報（現在のタスク詳細、一時的な状態）を記録しない
- CLAUDE.md の指示と矛盾する内容を記録しない
- 推測や未検証の結論を記録しない
- トレースを読む前に失敗カテゴリをブレインストーミングしない
- 表面的な類似性でグルーピングしない（根本原因で分類する）

## Examples

**Example 1: ユーザー修正からの学習**
```
ユーザー: 「bun を使って。npm じゃなくて」
→ 記録: preference: パッケージマネージャーは bun を使用（npm 不可）
```

**Example 2: デバッグパターンの記録**
```
Next.js の hydration mismatch を2回修正
→ 記録: debug-pattern: Next.js hydration mismatch
  - 状況: SSR と CSR の出力が異なる
  - 対処: useEffect で client-only 処理を分離、Date/Math.random を避ける
```

## Skill Assets

- パターン記録テンプレート: `templates/pattern-record.md`
- 検出シグナル一覧: `references/detection-signals.md`
