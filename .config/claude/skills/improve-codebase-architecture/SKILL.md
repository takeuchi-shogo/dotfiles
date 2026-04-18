---
name: improve-codebase-architecture
description: >
  コードベースを能動的に探索し、エージェントフレンドリーな改善候補を提案する。
  浅いモジュール→深いモジュール化、結合度の改善、テスト境界の明確化を診断。
  週次または開発サージ後に実行。
  Triggers: 'アーキテクチャ改善', 'モジュール改善', 'codebase architecture',
  'deep module', 'エージェントフレンドリー', 'コード構造改善', 'module depth'.
  Do NOT use for: 機能実装（use /rpi）、リファクタリング実行（use /refactor-session）、
  コード品質監査（use /audit）。
origin: self
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion
metadata:
  pattern: diagnosis
  origin: mattpocock/skills/improve-codebase-architecture + agent-native-code-design.md
disable-model-invocation: true
---

# /improve-codebase-architecture — コードベース構造の改善診断

コードベースを能動的に探索し、「エージェントが扱いやすい構造」への改善候補を提案する。

**核心**: エージェントは小さなファイルの群れより、大きなモジュール＋薄いインターフェースを扱いやすい。
"Deep Modules" — インターフェースは薄く、実装は豊かに。

## いつ使うか

- **週次**: `/weekly-review` の後に定期実行
- **開発サージ後**: 大量のコードが追加された後
- **エージェントの困りごと**: エージェントがファイル間を行ったり来たりして迷っている場合
- **新プロジェクト参入時**: コードベースの構造を理解するついでに改善点を洗い出す

## Workflow

```
/improve-codebase-architecture {対象ディレクトリ（省略時はプロジェクトルート）}
  Step 1: 探索         → ディレクトリ構造・モジュール境界を把握
  Step 2: 診断         → 5つの観点で問題を検出
  Step 3: 提案         → 改善候補を優先度付きで提示
  Step 4: ハンドオフ   → /refactor-session にチェーン（任意）
```

## Step 1: 探索

対象ディレクトリの構造を把握する:

1. `Glob` でディレクトリ構造を俯瞰（`**/*.{ts,go,py,rs}` 等）
2. ファイル数・モジュール数を概算
3. エントリポイント（main, index, app）を特定
4. テストファイルの配置パターンを確認

**探索予算: 最大 20 回の Read/Grep/Glob 操作。** 全ファイルを読む必要はない。構造の把握が目的。

## Step 2: 診断（5つの観点）

### 観点 1: 浅いモジュール（Shallow Modules）

> 「インターフェースが実装と同じくらい複雑」なモジュール

検出パターン:
- 関数が 1-5 行で、単純な委譲やラッパーのみ
- `utils/`, `helpers/` に小さな関数が散在
- 1ファイル 1関数 export が大量にある

**改善方向**: 関連する小さな関数を凝集させ、薄いインターフェース＋豊かな実装のモジュールに統合

### 観点 2: テスタビリティのための過度な分離

> 「テストのために分離したが、本当のバグは呼び出し側にある」パターン

検出パターン:
- 純粋関数を別ファイルに切り出しているが、それを呼ぶ側にロジックが残っている
- mock が実装よりも複雑
- テストが内部構造に強く依存している

**改善方向**: テスト境界をモジュールの公開インターフェースに合わせる

### 観点 3: 概念の分散

> 「1つの概念を理解するために N 個のファイルを開く必要がある」

検出パターン:
- 同じプレフィックスのファイルが複数ディレクトリに散在（`userService`, `userController`, `userModel`）
- 1 つの変更が 5+ ファイルに波及する
- 水平スライス型のディレクトリ構造（`services/`, `controllers/`, `models/`）

**改善方向**: 機能単位（feature-based）のディレクトリ構造に再編。`references/agent-native-code-design.md` 原則 3 参照

### 観点 4: Grep 困難な命名

> 「エージェントが grep で見つけられない」

検出パターン:
- `export default` の多用
- 汎用的すぎる名前（`handle`, `process`, `data`, `item`）
- マジックストリング / マジックナンバー

**改善方向**: named export、具体的な命名、定数への抽出。`references/agent-native-code-design.md` 原則 1 参照

### 観点 5: テストの不在・分離

> 「テストがあるのかないのか、エージェントがすぐ判断できない」

検出パターン:
- テストが `__tests__/` や `test/` に集約され、ソースと離れている
- テストファイルの命名がソースと対応していない
- テストカバレッジが不明

**改善方向**: Collocated Tests（ソース隣接配置）。`references/agent-native-code-design.md` 原則 2 参照

## Step 3: 提案

診断結果を以下の形式で提示する:

```markdown
## コードベース構造レポート

### スコアカード
| 観点 | 状態 | 改善候補数 |
|------|------|-----------|
| モジュール深度 | ⚠️ | 3 |
| テスト境界 | ✅ | 0 |
| 概念の凝集 | ⚠️ | 2 |
| Grep 容易性 | ✅ | 0 |
| テスト配置 | ❌ | 5 |

### 改善候補（優先度順）

#### 1. {対象モジュール/ディレクトリ} — {問題の要約}
- **観点**: {該当する観点}
- **現状**: {具体的な問題の記述 — ファイルパス付き}
- **提案**: {具体的な改善案}
- **効果**: {改善後にエージェントがどう楽になるか}
- **規模**: S / M / L

#### 2. ...
```

**提案は最大 5 件に絞る。** 全部直そうとしない。最もインパクトの大きい改善から。

## Step 4: ハンドオフ（任意）

ユーザーに `AskUserQuestion` で次のアクションを確認:

- **`/refactor-session` にチェーン**: 改善候補を入力にリファクタリングセッションを開始
- **Issue 化**: `/create-issue` で改善タスクを GitHub Issue に登録
- **記録のみ**: レポートを保存して終了

## Anti-Patterns

| NG | 理由 |
|----|------|
| 全ファイルを Read する | 探索予算を超過。構造の把握が目的 |
| 既存コードを直接編集する | このスキルは診断のみ。実行は `/refactor-session` |
| 理想的な設計を押し付ける | 既存コードの文脈を尊重。段階的な改善を提案 |
| 一度に全部直す提案 | 最大 5 件。優先度の高いものから |

## Chaining

- **前**: `/weekly-review`（定期実行）or `/audit`（品質監査の補完）
- **後**: `/refactor-session`（改善実行）or `/create-issue`（タスク登録）
- **参照**: `references/agent-native-code-design.md`（5原則）
