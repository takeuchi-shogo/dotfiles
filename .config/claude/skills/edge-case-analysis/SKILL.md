---
name: edge-case-analysis
description: >
  実装前に異常系・境界値・nil パスを強制的に洗い出す。M/L 規模のタスクで Plan → Implement の間に挟む。
  移行タスク、新機能実装、バグ修正のいずれでも使用。
  Triggers: 'エッジケース', '境界値', 'nilチェック', '異常系', 'what if', '壊れるケース',
  'edge case', 'boundary', 'corner case', 'error path'.
  Do NOT use for S規模タスク(typo修正、1行変更) — オーバーキル。
origin: self
allowed-tools: "Read, Bash, Grep, Glob, Agent"
metadata:
  pattern: reviewer
---

# Edge Case Analysis — 実装前の異常系洗い出し

実装コードを書く**前に**、データフローを追跡して異常系・境界値・nil パスを洗い出す。
「何が起きるか」ではなく **「何が起きないはずか（暗黙の前提）」** を可視化する。

## Trigger

以下のいずれかに該当する場合、**実装前に**このスキルを起動する:

- M/L 規模のタスク（関数追加以上）
- 既存処理の移行・リプレイス（フレームワーク移行、GraphQL → RPC 等）
- ポインタ型・Option 型・nullable なフィールドを扱うコード
- 複数レイヤーをまたぐデータフロー（conv → service → repository 等）

## Workflow

```
0. ASSUMPTION AUDIT   → 技術的前提を洗い出し「証拠あり/慣習のみ/未検証」に分類
1. DATA FLOW TRACE    → 入力から出力までデータがどう流れるか図示
2. NIL / ZERO HUNT    → 各ポイントで nil/zero/empty になりうる箇所を列挙
3. IMPLICIT SAFETY    → 旧コードで「偶然守られてた安全性」を特定（移行時）
4. EDGE CASE MATRIX   → パターン組み合わせ表を作成
5. TEST PLAN          → 欠けてるテストケースを明示
```

## Step 0: Assumption Audit

対象処理に関する**技術的前提**を洗い出し、信頼度で分類する。

| 前提 | 分類 | 根拠 |
|------|------|------|
| 「この API は常に 200 を返す」 | 未検証 | ドキュメントに明記なし |
| 「レイテンシは 100ms 以下」 | 慣習のみ | 計測データなし、経験則 |
| 「入力は必ずバリデーション済み」 | 証拠あり | middleware で検証済み |

**分類基準:**
- **証拠あり**: コード・テスト・ドキュメントで裏付けられる
- **慣習のみ**: 「今までそうだった」だけで保証がない
- **未検証**: 確認すらされていない

**「慣習のみ」「未検証」の前提が崩れたら何が起きるか？** を Step 2 以降で重点的に追跡する。

## Step 1: Data Flow Trace

対象処理の入力から出力までのデータフローを図示する。

```
入力(Proto/HTTP) → 変換層(Conv) → ビジネスロジック(Service) → 永続化(Repository/Writer)
```

各ステップで:
- **何が変換されるか**（型の変化）
- **何がフィルタ/バリデーションされるか**
- **何がそのまま素通りするか**

を明示する。特に「素通り」が危険信号。

## Step 2: Nil / Zero Hunt

データフロー上の各構造体について、**ポインタ型・Option 型・スライスのフィールド**を列挙し、以下を確認する:

| フィールド | 型 | nil/zero になる条件 | nil のまま下流に渡ったらどうなる？ |
|---|---|---|---|
| `ObjectField` | `*ObjectField` | Lead のみ設定時 | writer で panic (dereference) |
| `Items` | `[]Item` | 入力が空の場合 | DB に空 INSERT (問題なし) |

**チェックリスト:**
- [ ] ポインタ型フィールドが dereference される箇所に nil ガードがあるか
- [ ] Option 型の `.Get()` が ok チェック付きで呼ばれてるか
- [ ] スライスが空の場合に不要な DB 操作が走らないか

## Step 3: Implicit Safety（移行タスク専用）

旧コードで「別の関心事のロジックが偶然フィルタしてた」ケースを探す。

```
問い: 旧フローでこのデータが安全に処理されてたのは、どの関数のおかげ？
     → その関数は新フローにも存在する？
     → 存在しない場合、誰がその責務を引き継ぐ？
```

**典型パターン:**
- 差分検出ロジック（ClassifyItems 等）が副作用的に nil フィルタしてた
- Upsert が内部で存在チェックしてたのに、Create/Update 分離で消えた
- バリデーションが上位層にあったのに、新しい入口ではスキップされる

## Step 4: Edge Case Matrix

入力フィールドの組み合わせパターンを**全列挙**する。

例: Lead フィールドと Converted フィールドの組み合わせ

| Lead | Converted | 期待動作 |
|:---:|:---:|---|
| あり | なし | Lead マッピングのみ作成 |
| なし | あり | Converted マッピングのみ作成 |
| あり | あり | 両方作成 |
| なし | なし | 何も作成しない |

**boolean フィールドなら 2^n、enum なら各値 + zero値。**
全パターンを書くのが無理なら、最低限:
- 正常系の代表値
- 各フィールドの zero 値（nil, 0, "", false）
- 境界値（enum の直後の値、最大長）
- 組み合わせの端（全部 nil、全部あり、片方だけ）

### 補足: 15 軸チェックリスト (汎用)

Step 4 (フィールド組み合わせ) と直交。Step 4 完了後の generic safeguard として横断検査する。**例示的チェックリストであり完全ではない** — race conditions / integer overflow / charset / cancellation timeout 等は別途検討する。null check 単独はリジェクト — 必ず具体シナリオを書く。

`empty / max / off-by-one / slow network / offline / concurrent users / permissions / i18n (RTL, 長名, emoji) / timezone / DST / leap year / currency rounding / partial failures / retries / stale cache`

> 出典: 30-subagents-2026 absorb (T3)。記事の `edge-cases` agent は probability×severity ranking を使うが、本スキルは Step 4 マトリックスの「組み合わせの端」とほぼ等価のためチェックリストとしてのみ採用。

## Step 5: Test Plan

Step 4 のマトリックスに対して、既存テストでカバーされてるパターンを突き合わせる。

```
| パターン | テスト存在 | ファイル:行 |
|---|---|---|
| Lead のみ | ✅ | conv_test.go:30 |
| Converted のみ | ❌ 欠落 | — |
| 両方 | ❌ 欠落 | — |
| 両方なし | ✅ | conv_test.go:18 |
```

**欠落パターンは実装前にテストケースを書く（TDD）。**

## Output Format

分析結果は以下の形式でユーザーに提示する:

```markdown
## Edge Case Analysis: [対象機能名]

### Assumption Audit
| 前提 | 分類 | 崩れた場合の影響 |
|------|------|------------------|

### Data Flow
[入力] → [変換] → [ロジック] → [永続化]

### Nil/Zero Risks
| フィールド | リスク | 対策 |
|---|---|---|

### Implicit Safety (移行時のみ)
- 旧: [関数名] が暗黙的にフィルタ
- 新: [対策が必要 / 対策済み]

### Edge Case Matrix
| パターン | テスト | 状態 |
|---|---|---|

### 必要なアクション
1. [具体的なアクション]
2. [具体的なアクション]
```

## Anti-Patterns

- 「正常系が動いたから OK」で終わる（異常系を見てない）
- 旧コードの動作を「仕様」と仮定する（偶然の動作かもしれない）
- ポインタ型フィールドを見て「呼び出し側が nil を渡さないはず」と信じる
- テストの網羅性を「行カバレッジ」で判断する（パターンカバレッジが重要）
- 分析を省略して「後でテストで見つける」と思う（テストも同じ前提で書かれる）

## Reference Files

- `references/boundary-patterns.md` — 境界値パターンカタログ。分析の網羅性チェックに使用
