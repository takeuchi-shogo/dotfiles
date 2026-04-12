---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.go"
  - "**/*.py"
  - "**/*.rs"
---

# Code Quality

## Readability First

可読性が最優先。Beautiful code ≠ Readable code:
- チェーンを1行に詰めるより、名前付き変数で分割する方が読みやすい場合がある
- Immutability は手段であり目的ではない — mutable の方が読みやすいケースでは mutable を使う
- 関数の責務を「一文で要約」できるかが分割の判断基準

## Immutability as Default

デフォルトは immutable だが、以下のケースでは mutable を許容:
- アルゴリズム実装（BFS のキュー、グラフ探索等）で mutable の方が明瞭な場合
- パフォーマンスが重要で、コピーのコストが無視できない場合
- 判断基準: 「どちらが読み手にとって理解しやすいか」

## File Organization

MANY SMALL FILES > FEW LARGE FILES:
- 200-400 lines typical, 800 max
- Extract utilities from large modules
- Organize by feature/domain, not by type
- High cohesion, low coupling

## Function Design

- Functions: 50 lines max, nesting 4 levels max
- Single responsibility: 「一文で要約」できなければ分割する
- Early return: アンハッピーパスを先に追い出してフラットに書く
- Command-Query Separation: 副作用のある関数は値を返さない、値を返す関数は副作用を持たない
- Split by object, not condition: switch を関数内で繰り返すのでなく、対象ごとの関数に分割する

### Few-shot: Readability & Structure

```typescript
// NG: 深いネスト
if (user) {
  if (user.isActive) {
    if (user.hasPermission) {
      doWork(user);
    }
  }
}

// OK: early return でフラット化
if (!user) return;
if (!user.isActive) return;
if (!user.hasPermission) return;
doWork(user);
```

```typescript
// NG: let + 再代入
let result = items.filter(x => x.active);
result = result.map(x => x.name);

// OK: const + チェーン or 新変数
const activeNames = items.filter(x => x.active).map(x => x.name);
```

## Boy Scout Rule の Don't 側

巨大な構造には要素を追加しない:
- 巨大なファイル/クラスに新メンバーを追加しない → 先に分割する
- 巨大な関数に新しい分岐/条件を追加しない → 先に責務を分割する
- 深いコール階層に新レイヤーを追加しない → 先にフラット化する

## Error Handling

→ 詳細は `rules/common/error-handling.md` を参照

## Input Validation

→ 詳細は `rules/common/security.md` の入力バリデーションセクションを参照

## Config Externalization

ハードコードされた値を設定ファイルや環境変数に分離する:

- **マジックナンバー**: 意味のある定数名を付ける（`MAX_RETRIES = 3`）
- **環境依存値**: 環境変数 or `.env` で管理する（URL, ポート, APIキー）
- **チューニング可能なパラメータ**: YAML/TOML/JSON の設定ファイルに外部化する
- **判断基準**: 「この値を変えるときにコードを再デプロイしたいか？」— No なら外部化する

## Scope Discipline

1つの PR / Issue は1つの目的に絞る:

- **Feature Creep 防止**: 実装中に見つけた改善は別 Issue に切り出す
- **スコープの判定**: 「この変更を1文で要約できるか？」— できなければ分割する
- **目安**: 400行超の差分は分割を検討する

### スコープ外変更の3層禁止（Karpathy "Surgical Changes"）

タスクに無関係な変更は、影響が小さく見えても混入させない:

| 層 | 禁止される変更例 |
|----|----------------|
| **コードレベル** | 既存の死亡コード削除、フォーマット変更、quote スタイル統一、boolean 形式変更 |
| **依存レベル** | import の並べ替え、未使用 import の除去、パッケージバージョン更新 |
| **設計レベル** | 「ついでにインターフェースを改善」「ここのAPI、ついでに整理」 |

改善が必要だと気づいた場合は、別 Issue に切り出す（実装中のタスクに混ぜない）。
例外: 自分の変更が直接引き起こした不要コード（import 等）のみ削除してよい。

## LLM Anti-Slop Patterns

LLM が反復的編集で特に陥りやすいパターン（SlopCodeBench, Orlanski et al. 2026）。
プロンプトで初期品質は改善できるが、反復ごとの劣化速度はプロンプトだけでは変わらない。
詳細: `references/iterative-degradation-awareness.md`

### 禁止パターン

- **God function 化**: 既存の大関数にロジックを追加するのではなく、新しい focused callable に分割する
- **Scaffold コピペ**: 同じ引数パース/バリデーション構造を複数箇所にコピーしない → 共通関数に抽出
- **elif/case チェーンの成長**: 新しい条件を追加するなら dispatch table やポリモーフィズムを検討

### 過度な抽象化アンチパターン（Karpathy "Simplicity First"）

シンプルな関数を不要なデザインパターンで複雑化しない:

```python
# NG: 単純な割引計算に Strategy pattern を導入
class DiscountStrategy(ABC): ...
class PercentageDiscount(DiscountStrategy): ...
class FlatDiscount(DiscountStrategy): ...
class DiscountContext: ...

# OK: 関数で十分
def apply_discount(price: float, discount_type: str, value: float) -> float:
    if discount_type == "percentage":
        return price * (1 - value / 100)
    return price - value
```

判断基準: 「この抽象化を導入しなかった場合、何が困るか？」に具体的に答えられなければ過剰。
不要になりがちなパターン: Strategy, Factory, Builder, Observer（用途が1つしかない場合）

### 冗長コードの回避

```python
# NG: identity list comprehension（filter で十分）
result = [x for x in items if x.active]

# OK: filter を使う
result = list(filter(lambda x: x.active, items))
# Or: そのままリスト内包表記でも良いが、変換なしの filter 相当なら意図を明確に
```

```python
# NG: single-use 中間変数（意味のある名前でなければ不要）
temp_list = get_items()
filtered = [x for x in temp_list if x.valid]
return filtered

# OK: 直接返す（中間変数に意味がない場合）
return [x for x in get_items() if x.valid]
```

```python
# NG: empty check + continue（iteration に組み込める）
for item in items:
    if not item.applicable:
        continue
    process(item)

# OK: filter してから loop
for item in filter(lambda x: x.applicable, items):
    process(item)
# Or: 条件が単純なら内包表記で十分
```

## Code Quality Checklist

Before marking work complete:
- [ ] Code is readable — 名前付き変数で意図が明確
- [ ] Functions are small (<50 lines) and single-responsibility
- [ ] Files are focused (<800 lines)
- [ ] No deep nesting (>4 levels) — early return を使う
- [ ] Proper error handling
- [ ] No hardcoded values — Config Externalization セクションに従う
- [ ] Command-Query Separation が守られている
- [ ] No god function 化 — 既存大関数への追加ではなく分割しているか
- [ ] No scaffold コピペ — 同じ構造の繰り返しが共通化されているか
