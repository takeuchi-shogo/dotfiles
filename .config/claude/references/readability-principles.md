---
status: reference
last_reviewed: 2026-04-23
---

# Readability Principles Reference

munetoshi 氏のコード可読性シリーズ（全8セッション）および
森崎修司「コードレビューに効く読みやすさの処方箋」（Findy, 2026-03）から抽出した、
全レビューエージェントが参照すべき横断的原則。

## 読みやすさの3層モデル

コードの「読みやすさ」は単一の概念ではなく、以下の3層に分解される（森崎, 2026; Oliveira et al., 2022）。
レビュー時はどの層の問題かを意識することで、指摘の精度が上がる。

| 層 | 名称 | 対象 | 主な検出手段 |
|----|------|------|-------------|
| **Legibility（判読性）** | 視覚的なレイアウトと形式 | インデント、空白、行長、単語区切り | Formatter / Linter（自動化可能） |
| **Readability（可読性）** | 名前と振る舞いの一致 | 識別子、Linguistic Anti-patterns | レビューアー（人間/AI） |
| **Understandability（理解性）** | ロジックの把握しやすさ | 結合度、依存方向、直交性、状態遷移 | レビューアー（人間/AI） |

- Legibility は formatter でほぼ自動化できる。**Readability と Understandability が人間レビューの主戦場**
- GitHub 385 PR 調査: レビュー指摘の **42.2% が読みやすさ**、うち Linter で検出可能なのは **30% 未満**（Oliveira et al., 2024）
- 以下のセクション §1-§4, §6 は主に Understandability、§5 は Readability に対応する
- §8 Atoms of Confusion は Readability/Understandability 両層、§9 Model-based 読解戦略はレビュー実践手法

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

## 8. Atoms of Confusion（誤読の最小単位）

IOCCC（国際C難読化コンテスト）上位作品から抽出された、**統計的に有意に誤読を誘発する**15種類のコードパターン（Gopstein et al., 2018）。
73名のプログラマで検証後、Linux・MySQL・Nginx 等の主要 OSS でも該当事例が確認された。

C 固有のパターンも含むが、概念は言語横断で応用可能（以下は代表的な6件。全15パターンは原論文参照）:

| パターン | 例 | 誤読の原因 |
|---------|-----|-----------|
| 暗黙の型変換 | `int x = 3/2.0` | 整数除算と浮動小数点除算の混同 |
| 演算子の優先順位 | `a & b == c` | `&` より `==` が優先されることの見落とし |
| 前置/後置インクリメント | `a[i++] = i` | 評価順序の未定義動作 |
| 条件式の副作用 | `if (a = b)` | 代入と比較の混同 |
| 三項演算子のネスト | `a ? b : c ? d : e` | 結合方向の誤解 |
| 論理演算子の短絡評価 | `f() \|\| g()` | g() が実行されない可能性の見落とし |

**レビューでの活用**: これらのパターンを含むコードは、たとえ正しくても `consider:` で簡明な書き換えを提案する。
正しく読める開発者は「モデルベース意思決定」（下記§9）をしている傾向がある（Sugiyama et al., 2025; 有意水準5%）。

## 9. Model-based 読解戦略

誤読しやすいコードを正しく読める開発者は、**コードをメンタルモデル化してから判断**する傾向がある（Sugiyama et al., 2025）。

レビュー時の実践:
1. **まず構造を把握**: 関数の入出力・副作用・状態遷移を頭の中でモデル化する
2. **モデルと実装を照合**: モデルから期待される振る舞いと実際のコードを比較する
3. **不一致を指摘**: モデルと異なる箇所が「バグ」か「意図的な設計」かを判別する

「上から下に1行ずつ読む」のではなく、「全体像を掴んでから細部を検証する」アプローチ。
§6 の Definition-Based Programming（名前付き変数で分割して上から下に読めるコードにする）はこの読解を支援する書き方。

## 出典

munetoshi「Code Readability」全8セッション
https://gist.github.com/munetoshi/65a1b563fb2c121a4ac63571

森崎修司「コードレビューに効く読みやすさの処方箋」Findy, 2026-03
- [1] Oliveira et al. (2024) "Understanding code understandability improvements in code reviews" IEEE TSE
- [2] Oliveira et al. (2022) "A systematic literature review on formatting elements" SSRN
- [3] Arnaoudova et al. (2016) "Linguistic antipatterns" Empirical Software Engineering
- [4] Gopstein et al. (2018) "Atoms of confusion in the wild" MSR
- [5] Sugiyama et al. (2025) "Model-based Decision-making and Comprehension" IEEE TSE
- [6] Sarsa et al. (2022) "Automatic generation with large language models" ICER
