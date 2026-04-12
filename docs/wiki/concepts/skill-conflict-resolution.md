---
title: スキル競合解決
topics: [skill]
sources: [2026-04-12-tan-thin-harness-fat-skills-analysis.md]
updated: 2026-04-12
---

# スキル競合解決

## 概要

複数のスキルが同一トリガーやユースケースに応答しようとする場合の衝突を検出・解決するパターン。Garry Tan の "Thin Harness, Fat Skills" 原則 #5「Negative Routing」に基づく。スキルは「何をするか」だけでなく「何をしないか」を明示することで、意図しない実行を防止する。

注意: このファイルはスキル間の競合（skill-level）を扱う。エージェント間の競合（agent-level）は [エージェント競合解決](agent-conflict-resolution.md) を参照。

## Negative Routing

スキルの `description` に `Do NOT use for:` セクションを設け、明示的に除外する文脈を定義する手法。

```markdown
## Do NOT use for:
- 既存ファイルの単純な編集（→ /edit を使う）
- テストコードの生成（→ /test を使う）
- ドキュメント生成（→ /docs を使う）
```

### Negative Routing が有効なケース

| 状況 | 問題 | Negative Routing |
|------|------|-----------------|
| 類似スキルが複数存在 | どちらを使うか曖昧 | 一方に「他方を使う状況」を明記 |
| 汎用スキルが特化スキルを侵食 | 汎用が過剰トリガー | 汎用に特化スキルの領域を Do NOT で除外 |
| スキルのスコープ拡大 | 最初の設計を超えた利用 | 新スコープを Do NOT に追記し別スキル作成を促す |

## 衝突優先度

スキルが衝突した場合の解決順序:

1. **`supersedes` 宣言が最優先** — プロジェクト固有スキルが汎用スキルを上書き
2. **`priority` フィールド** — 数値が高い方が優先（デフォルト: 0）
3. **specificity** — より具体的なトリガー条件を持つスキルが優先
4. **最終手段: ユーザー確認** — 自動解決不能な場合のみインタラクションを挟む

## 規模ガード

スキルの適用を規模（影響範囲）で制限する機構。

```markdown
## Scale Guard:
- S 規模（1-3 ファイル）: 直接実行
- M 規模（4-10 ファイル）: Plan 確認後に実行
- L 規模（10+ ファイル）: /spec を先に実行し承認を取る
```

規模ガードはスキルが本来意図しない大規模変更を引き起こすことを防ぐ。

## `/skill-audit conflict-scan` との連携

`/skill-audit` の `conflict-scan` モードが以下を自動検出する:

- **完全一致**: 2 つのスキルのトリガー条件が完全に重複
- **部分包含**: 一方のトリガー条件が他方に包含される
- **排他欠落**: 類似スキルが互いに `Do NOT use for:` で参照していない

衝突が検出された場合、Negative Routing の追加か `supersedes` 宣言が推奨される。

## 関連概念

- [スキル設計](skill-design.md) — スキル設計の基本原則（テリトリー衝突検出を含む）
- [スキル呼び出しパターン](skill-invocation-patterns.md) — World ごとのスキル分岐パターン
- [エージェント競合解決](agent-conflict-resolution.md) — エージェント間（agent-level）の競合解決
- [品質ゲート](quality-gates.md) — スキル実行前の規模ガードと検証

## ソース

- [Tan "Thin Harness, Fat Skills" 分析](../../research/2026-04-12-tan-thin-harness-fat-skills-analysis.md) — 原則 #5 Negative Routing, #7 Narrow Tools の解説と dotfiles 既実装との差分分析
