# Readability Principles Reference

munetoshi 氏のコード可読性シリーズ（全8セッション）から抽出した、
全レビューエージェントが参照すべき横断的原則。

## 1. 結合度の階層（Coupling Hierarchy）

強い順（上ほど避ける）:

| レベル | 説明 | 例 |
|--------|------|-----|
| **Content** | 内部状態・実行順序に依存 | `calc.prepare(); calc.calculate(); calc.result` |
| **Common** | グローバル/シングルトン参照 | `var REPO = NewRepo()` を直接参照 |
| **Control** | 引数で処理を分岐制御 | `showView(isCalledAtMain: true)` |
| **Stamp** | 不要に大きな構造体を渡す | 全フィールド持つ User を渡すが name しか使わない |
| **Data** | 基本型の値を渡す | `func(name string, id string)` — 順序間違いに弱い |
| **Message** | メッセージ/イベント経由 | 最も疎結合 |

### 緩和パターン
- Content → カプセル化（`calc.Calculate(42)` に統合）
- Common → コンストラクタインジェクション
- Control → 関数分割（`updateUserName()` と `updateBirthday()` に分ける）
- Data → Newtype パターン（`type UserID int64`）

## 2. 依存方向の原則

以下の方向を常に守る。逆転は循環依存・責務混乱の原因:

```
caller → callee
concrete → abstract
complex → simple
mutable → immutable
unstable → stable
algorithm → data model
```

### よくある違反パターン
- View が Presenter を直接参照して値を取得（caller-callee 逆転）
- データモデルが Repository を保持（simple → complex の逆転）
- Immutable なデータ構造が mutable なコンテキストに依存

### 修正方法
- 値を引数で渡す（依存方向を正す）
- interface を抽出して依存を逆転させる（DIP）
- 中間レイヤーを導入して N:M 依存を解消

## 3. 直交性（Orthogonality）

フィールド A の値が決まったとき、フィールド B の取りうる値が制限されるなら「非直交」。

### 非直交の危険性
- 不正な状態が表現可能になる（`coinCount=0, coinText="5 coins"`）
- 更新漏れバグの温床（片方だけ更新して不整合）

### 修正方法
- 導出可能な値は getter/computed property にする
- Sum type で排他的な状態を表現する
- 非直交なフィールドを別の型に分離する

## 4. 状態遷移の4タイプ

望ましい順:

| タイプ | 説明 | 例 |
|--------|------|-----|
| **Immutable** | 状態変更なし | `string`, value object |
| **Idempotent** | 同じ操作を何度実行しても同じ結果 | `Close()` を複数回呼んでも安全 |
| **Acyclic** | 一方向にのみ遷移（戻らない） | `Measuring → Finished`（リセット不可） |
| **Cyclic** | 循環的に遷移 | `Open ↔ Closed`（最小化すべき） |

### 設計指針
- Cyclic を見つけたら Acyclic にできないか検討する
- リセットが必要なら新しいインスタンスを生成する設計にする
- 冪等性を確保し、呼び出し前の状態チェックを不要にする

## 5. 命名の「what」原則

関数名は「何をするか（what）」を表現する。「いつ/誰が/どこから（when/who/where）」は表現しない。

| Bad | Good | 理由 |
|-----|------|------|
| `onMessageReceived` | `storeReceivedMessage` | 呼び出し側で何が起きるか分かる |
| `handleError` | `logAndReturnError` | 具体的な動作が分かる |
| `isCalledAtMainScreen` | `shouldShowDialogOnError` | 呼び出し元に依存しない |

## 6. Definition-Based Programming

ネスト・チェーンを名前付き変数で分割し、「上から下に読めるコード」にする:

```
// Bad: 内側から読む必要がある
showDialogOnError(presenter.update(repository.query(userId)))

// Good: 上から下に読める
userModel := repository.query(userId)
updateResult := presenter.update(userModel)
showDialogOnError(updateResult)
```

## 7. コメントの原則

- コメントが書きにくい = リファクタリングのサイン
- インフォーマルコメントが必要な3ケース:
  1. 大きなコードブロックのサマリー
  2. 反直感的なコードの理由説明
  3. ワークアラウンドの「何を・なぜ」＋issue リンク
- ドキュメントコメントは「名前の繰り返し」「コードの翻訳」「呼び出し元への言及」を避ける

## 出典

munetoshi「Code Readability」全8セッション
https://gist.github.com/munetoshi/65a1b563fb2c121a4ac63571
