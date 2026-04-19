# Extraction Heuristics — 候補語抽出の判断基準

ubiquitous-language skill が Phase 1 Extract と Phase 2 Normalize で参照するヒューリスティクス。

## 抽出対象 (Include)

### 1. ドメインエンティティ

- **判定**: ビジネス的な意味を持つ名詞。削除するとドメイン記述が成立しない
- **例**: Order, Customer, Invoice, InventoryItem, ShippingAddress
- **シグナル**: コードで class/struct として定義、PRD で繰り返し登場、DB テーブルに対応

### 2. 値オブジェクト・属性

- **判定**: エンティティの属性で、ドメイン固有の不変条件を持つもの
- **例**: OrderStatus, Money, EmailAddress, SKU
- **シグナル**: validation ロジックが存在、enum/sealed type、formatter が複数箇所にある

### 3. ドメイン動詞句

- **判定**: ビジネスプロセスを表す動作
- **例**: 「注文を確定する (place order)」「在庫を引き当てる (reserve inventory)」
- **シグナル**: Service/UseCase メソッド名、state transition、event 名 (OrderPlaced 等)

### 4. 略語・頭字語

- **判定**: チーム内で頻用されるが初見で不明瞭なもの
- **例**: SKU (Stock Keeping Unit), MRR (Monthly Recurring Revenue), TTFB (Time To First Byte)
- **シグナル**: 複数人の会話で展開形なしに使われる、コード・PRD でそのまま登場

## 除外対象 (Exclude)

| 分類 | 例 | 理由 |
|------|-----|------|
| 一般プログラミング語 | function, class, array, loop | 言語仕様であってドメインではない |
| 言語キーワード | async, await, const, let | 同上 |
| インフラ一般語 | database, cache, queue | 文脈なしでは意味を持たない |
| UI ラベル | "Submit", "Cancel" ボタン文言 | i18n リソースに属する |
| 一時変数名 | tmp, data, result | ドメイン意味を持たない |

## Drift 検出パターン

### Pattern A: 同義語 (同じ概念、異なる呼称)

- **例**: 「注文」vs「オーダー」、「顧客」vs「ユーザー」vs「クライアント」
- **判定**: 既存エントリの定義と候補の定義が 80%+ 重複
- **対応**: 正規形を 1 つ選び、他を alias として記録

### Pattern B: 曖昧語 (同じ呼称、異なる概念)

- **例**: 「ユーザー」がエンドユーザーと管理者の両方を指す、「ステータス」が注文と配送の両方で使われる
- **判定**: 既存エントリと候補の定義が 30% 未満しか重複しない (同名だが別物)
- **対応**: context 別にエントリを分割 (`User (end-user)` / `User (admin)`)

### Pattern C: 粒度不整合

- **例**: 「商品」と「商品バリアント」「商品マスタ」が混在
- **判定**: 既存エントリが候補の上位/下位概念を含む
- **対応**: 階層を明示 (See also で関連付け) し、どのレベルで使うべきか定義

## 優先度判定

1 セッションで抽出した候補が 10 を超える場合、以下で絞り込む:

| 優先度 | 条件 |
|--------|------|
| **High** | コード 3+ 箇所 かつ PRD 登場、または drift 検出済み |
| **Medium** | コード 2+ 箇所 または PRD 繰り返し登場 |
| **Low** | 1 箇所のみ (新概念) |

Low は次回に持ち越す。一度に多く登録すると consensus が追いつかず、glossary が死文化する。
