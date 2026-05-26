---
status: reference
last_reviewed: 2026-05-24
source_url: https://google.github.io/eng-practices/review/developer/small-cls.html
source_repo: https://github.com/google/eng-practices/blob/master/review/developer/small-cls.md
---

# PR Splitting Patterns

Google eng-practices `small-cls.md` ([Web](https://google.github.io/eng-practices/review/developer/small-cls.html) / [Repo](https://github.com/google/eng-practices/blob/master/review/developer/small-cls.md)) 由来の 5 つの CL 分割パターン。
300 行を超える CL は本ドキュメントを参照して分割する。

## 1. Five Patterns

| Pattern | 説明 | 使い所 |
|---------|------|--------|
| **stacking** | 依存 CL を直列に積み、先行 CL が merge されるまで次を作成 | 段階的な API 拡張、依存順がある refactoring |
| **by-files** | 1 CL = 1 ファイルグループ | refactoring file A + feature file B が分離可能なとき |
| **horizontal** | 全 layer (DB/API/UI) で 1 機能 X を実装する thin vertical slice | 機能フラグ付きの段階的リリース |
| **vertical** | 1 CL = 1 layer (DB schema のみ、API のみ、UI のみ) | DB migration を先行させたい、layer ごとに reviewer が異なる |
| **grid** | 機能 × layer の格子を 1 セルずつ CL 化 | 大規模機能 (例: 認証システム全面刷新) |

### 具体例

**stacking**:
- CL-1: `pkg/user/repository.go` に `FindByEmail()` 追加 (依存なし)
- CL-2: CL-1 マージ後、`pkg/auth/service.go` で `FindByEmail()` を利用した SSO ハンドラ追加
- CL-3: CL-2 マージ後、`api/handlers/login.go` で SSO エンドポイント有効化

**by-files**:
- CL-A: `pkg/billing/calculator.go` の純粋な refactoring (関数抽出のみ、振る舞い不変)
- CL-B: `pkg/billing/discount.go` に新規割引ロジック追加 (CL-A と独立)

**horizontal**:
- 1 CL で `db/migrations/001_add_tags.sql` + `pkg/tags/service.go` + `web/components/TagInput.tsx` を一括追加 (機能フラグ off で merge)

**vertical**:
- CL-1: DB schema のみ (`db/migrations/001_add_tags.sql`)
- CL-2: API layer のみ (`pkg/tags/service.go` + handler)
- CL-3: UI layer のみ (`web/components/TagInput.tsx`)

**grid**:
- 認証システム刷新の場合: (Login × DB) → (Login × API) → (Login × UI) → (Signup × DB) → … と 1 セルずつ

## 2. 適用基準

| 状況 | 推奨 pattern |
|------|------------|
| 300 行以上の diff | splitting 検討必須 |
| refactoring + feature 混在 | **by-files** または separate CL 強制 (`agents/code-reviewer.md` Section E refactor-mixing-block) |
| 複数の独立 subsystem 変更 | **vertical** または **grid** |
| 依存関係が直列 | **stacking** |
| 機能フラグで段階的有効化したい | **horizontal** |

### horizontal vs vertical の選択基準

**horizontal（layer 軸で分割）を選ぶとき**:
- layer ごとに reviewer が異なる（DB は DBA、UI は フロントエンド等）
- 特定 layer（DB migration 等）を先行デプロイする必要がある
- 共有 proto/stub/interface でlayer 間を抽象化して独立して進めたい
- 1 つの layer（DB schema 等）が後続 CL の前提になる

**vertical（feature 軸で分割）を選ぶとき**:
- 機能が互いに独立しており、並列で実装できる（multiplication と division を別々に）
- 一部の機能を先にリリースしたい
- 機能単位でロールバック可能にしたい

**grid（両軸）を選ぶとき**:
- 機能も layer も両方多い大規模実装（認証システム全面刷新等）
- horizontal と vertical 両方の理由が同時に成立するとき

## 3. Anti-Patterns

- **「後でまとめて PR」**: no-cleanup-later 原則違反 (`references/review-checklists/cross-cutting.md` CC-4 + `agents/code-reviewer.md` Section A)
- **refactoring と bugfix の混在**: review cost 増大、bugfix の意図が refactoring に埋もれる
- **Large CL exception 乱用**: emergency 定義外への適用は禁止 (`references/emergency-definition.md`)
- **「依存があるから 1 CL でやる」**: stacking pattern で分割可能なケースが大半

## 4. Large CL Exception

300 行を超える CL は原則禁止だが、`references/emergency-definition.md` で定義される emergency に該当する場合のみ Large CL が許容される。

emergency 該当時の必須記載事項:
- emergency 種別 (本番障害 / リリースブロッカー / harness 破損)
- 影響範囲
- follow-up CL 計画

## 5. 参照

- `skills/github-pr/SKILL.md` — PR ライフサイクル全体
- `skills/github-pr/self-review.md` — セルフレビュー時の threshold チェック
- `references/emergency-definition.md` — Large CL exception の判定基準
- `agents/code-reviewer.md` — Section E: Refactor-Mixing Block
