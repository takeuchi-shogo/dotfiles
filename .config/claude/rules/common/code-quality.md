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

## Boy Scout Rule の Don't 側

巨大な構造には要素を追加しない:
- 巨大なファイル/クラスに新メンバーを追加しない → 先に分割する
- 深いコール階層に新レイヤーを追加しない → 先にフラット化する

## Error Handling

ALWAYS handle errors explicitly:
- Handle errors at every level
- User-friendly messages in UI-facing code
- Detailed error context in server logs
- Never silently swallow errors

## Input Validation

ALWAYS validate at system boundaries:
- Validate all user input before processing
- Use schema-based validation (zod, pydantic, etc.)
- Fail fast with clear error messages
- Never trust external data

## Code Quality Checklist

Before marking work complete:
- [ ] Code is readable — 名前付き変数で意図が明確
- [ ] Functions are small (<50 lines) and single-responsibility
- [ ] Files are focused (<800 lines)
- [ ] No deep nesting (>4 levels) — early return を使う
- [ ] Proper error handling
- [ ] No hardcoded values (use constants or config)
- [ ] Command-Query Separation が守られている
