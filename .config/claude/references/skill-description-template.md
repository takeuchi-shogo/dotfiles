# Skill Description Template (Revitalization 用)

> **Date**: 2026-05-09
> **Source**: spike on `recall/SKILL.md` revitalization (PC 全体 1 回 → 改善)
> **Reference well-used skills**: `/absorb` (91 回), `/commit` (146 回), `/review` (86 回)
> **Plan**: [docs/plans/2026-05-09-skill-revitalization-plan.md](../../../docs/plans/2026-05-09-skill-revitalization-plan.md)

## なぜこのテンプレートが必要か

200-session × 172 inventory の集計で、**全 skill のうち 71% が未使用または低使用** と判明。原因の 1 つが「Claude が auto-invoke できる description / trigger になっていない」こと。具体的には:

1. `disable-model-invocation: true` 設定で auto-invoke が封じられている (例: 旧 recall)
2. Triggers が少ない / 抽象的すぎて Claude が match できない
3. 他 skill との境界が不明瞭で、重複機能の代表 1 件に流れる
4. Use case / Chain / Examples が薄く、Claude が「いつ呼ぶか」判断できない

## テンプレート (frontmatter)

```yaml
---
name: <skill-name>
allowed-tools: <必要最小権限のみ列挙>
argument-hint: <引数の形式>
description: "<動詞 + 名詞 + 1 文の目的>。<処理の概要 1 文>。Triggers: '<語1>', '<語2>', ..., '<語N>'. Do NOT use for: <他 skill が担う領域 (use /<other-skill>)>."
origin: self
user-invocable: true   # auto-invoke を許可するなら必須。誤起動を絶対に避けたい場合のみ disable-model-invocation: true
metadata:
  pattern: <query | pipeline | gate | tool | reference>
  chain:
    upstream: ["<前段 skill>"]
    downstream: ["<後段 skill>"]
---
```

### key fields

- **`description`**: **1 行 string** (multi-line `>` block scalar は避ける)。本環境の core 機能は 1 行で書かれている。
- **`Triggers`**: 日本語 + 英語、自然な言い回しを 8-12 個。Claude の auto-invoke は description 内の Triggers を見て判定する。
- **`Do NOT use for`**: 他 skill との境界を明示。重複している場合、`use /<other-skill>` で振り分けを誘導。
- **`user-invocable: true`**: 必須。`disable-model-invocation: true` は誤起動が壊滅的な場面のみ。

## テンプレート (本文)

```markdown
# <Title>

<1-2 文で skill の目的>

## When to use

- **<シナリオ 1>**: <具体的なユーザー発話例>
- **<シナリオ 2>**: <具体的なユーザー発話例>
- **<シナリオ 3>**: <具体的なユーザー発話例>

## Chain

- **前段**: <この skill を呼ぶ前に通常実行される skill>
- **後段**: <完了後に通常移行する skill>
- **対比**: <混同しやすい類似 skill との違い>

## Examples

- ユーザー発話: 「<実際の発話例 1>」 → `/<skill-name>`
- ユーザー発話: 「<例 2>」 → `/<skill-name> <args>`

<以下、既存の skill 本文 / workflow 詳細を維持>
```

## Triggers の書き方ベストプラクティス

### 良い例 (`/absorb`)

```
'活かしたい', '取り込みたい', '考えて', 'absorb', '統合して', 'この記事', 'integrate'
```

- 日本語の自然な発話 (「活かしたい」「取り込みたい」「考えて」)
- 英語キーワード (skill 名 + 同義語)
- "この記事" のような **文脈指示語**

### 悪い例 (旧 `/recall`)

```
'recall', '前回の続き', '文脈復元', 'what was I working on', 'reconstruct context'
```

- 5 個と少なすぎ
- 「文脈復元」は不自然な日本語、ユーザーは普通言わない
- 「前回の続き」だけでは ambiguous (`/checkpoint` と被る)

### 改善後 (新 `/recall`)

```
'recall', '前回の続き', '文脈復元', 'これまでの作業', 'どこまでやった',
'コンテキスト復元', 'context 復元', 'continue', '再開', '続きから',
'what was I working on', 'reconstruct context'
```

- 12 個に増加
- 自然な日本語 (「どこまでやった?」「再開」「続きから」)
- 英語表現も保持

## チェーン (chain) の表現

`metadata.chain` は machine-readable なので、将来的に `skill-audit` で自動 chain 検証可能。

```yaml
metadata:
  chain:
    upstream: ["/commit (contextual commit を残す)", "/checkpoint (別経路)"]
    downstream: ["/rpi", "/spec", "/spike"]
```

- **upstream**: この skill の前提となる skill (実行順序)
- **downstream**: 完了後に通常移行する skill
- **コメント可**: `/foo (理由)` 形式で why を残せる

## Pattern 分類 (`metadata.pattern`)

| pattern | 説明 | 例 |
|---|---|---|
| `query` | 情報を読み取る | `/recall`, `/audit` |
| `pipeline` | 多段パイプライン | `/absorb`, `/digest` |
| `gate` | pass/block 判定 | `/review`, `/validate` |
| `tool` | 特定ツール実行 | `/commit`, `/codex`, `/gemini` |
| `reference` | 参照情報のみ | `/justfile`, `/dotenvx` |

## 適用フロー (revitalization 時)

1. 対象 skill の SKILL.md を読む
2. well-used skill (`/absorb` 等) と description 構造を比較
3. 上記テンプレに沿って書き直し
4. Triggers を 8-12 個に拡充 (日本語 + 英語、自然な言い回し)
5. Do NOT use for で他 skill との境界明示
6. `user-invocable: true` 確認、`disable-model-invocation: true` は原則削除
7. 本文に When to use / Chain / Examples を追加 (既存 workflow 部分は維持)
8. Codex Review Gate (S 規模なので軽量で OK)
9. Commit

## 観察期間 (60 日)

改善後 60 日経過時点で:

- 利用 0 回 → 真の dead と判定 → 削除候補
- 利用 1+ 回 → keep + 利用率を継続観察
- 利用 5+ 回 → Well-used 入り、改善成功

詳細: [docs/plans/2026-05-09-skill-revitalization-plan.md](../../../docs/plans/2026-05-09-skill-revitalization-plan.md) Phase 4-5
