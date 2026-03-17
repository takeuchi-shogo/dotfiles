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

## Code Quality Checklist

Before marking work complete:
- [ ] Code is readable — 名前付き変数で意図が明確
- [ ] Functions are small (<50 lines) and single-responsibility
- [ ] Files are focused (<800 lines)
- [ ] No deep nesting (>4 levels) — early return を使う
- [ ] Proper error handling
- [ ] No hardcoded values — Config Externalization セクションに従う
- [ ] Command-Query Separation が守られている
