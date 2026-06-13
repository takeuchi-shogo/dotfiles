---
status: reference
last_reviewed: 2026-04-23
---

# Cross-Cutting Review Checklist

言語非依存の共通レビュー観点。`code-reviewer` が**全ての変更**に対して適用する。

## CC-1. シークレット・機密情報

- `must:` API キー、トークン、パスワード、接続文字列がハードコードされていないか
- `must:` `.env` ファイルや設定ファイルが `.gitignore` に含まれているか
- `must:` ログ出力にユーザーの個人情報やシークレットが含まれていないか

## CC-2. エラーハンドリングの可視性

- `must:` catch/recover で**何もしない**パターンがないか（サイレント障害）
- `consider:` エラー時にユーザーまたはオペレーターが問題を特定できるログが出ているか
- `consider:` リトライ可能な操作とリトライ不可の操作を区別しているか

## CC-3. 環境依存・ハードコード

- `must:` 環境固有の値（URL, ポート, パス）がハードコードされていないか
- `consider:` マジックナンバーに名前付き定数が使われているか

## CC-4. TODO / FIXME / HACK

Google eng-practices `pushback.md` の no-cleanup-later 原則: 「後で直す」を許すと debt が蓄積する。
本 CL で**新規追加**された TODO と、本 CL では変更されていない**既存**の TODO を区別する。

### 新規 TODO (本 CL で追加されたもの)

- `must:` 新規追加された `TODO` / `FIXME` / `HACK` に Issue 番号・期限・オーナーのいずれかが欠落していないか
  - 例 NG: `// TODO: refactor later`
  - 例 OK: `// TODO(#1234): refactor by 2026-06-30 (owner: @takeuchi)`
- `must:` "cleanup later" を理由に未完成のロジックを merge していないか (no-cleanup-later 原則)

### 既存 TODO (本 CL では変更されていないもの)

- `nit:` 周辺に既存 TODO があれば追跡 issue 化を提案 (本 CL のスコープ外、修正強制はしない)
- `nit:` 解決済みの TODO が残っていないか

### 検出方法

- `git diff` の `+` 行に `TODO` / `FIXME` / `HACK` が新規追加 → 新規 TODO 扱い
- diff 外の既存 TODO への言及は nit 扱い
- 詳細 rubric: `agents/code-reviewer.md` Section A: Cleanup-Later Boundary

## CC-5. ログ・オブザーバビリティ

- `consider:` 重要な操作（認証、データ変更、外部 API 呼び出し）にログが出力されているか
- `consider:` ログレベルが適切か（DEBUG/INFO/WARN/ERROR の使い分け）
- `nit:` 構造化ログ（JSON 形式等）が使用されているか

## CC-6. テストとの整合性

- `consider:` 新しいロジックに対応するテストが追加されているか
- `consider:` 既存テストが変更後のコードと整合しているか（テストの更新漏れ）

## CC-7. 破壊的変更

- `must:` public API / exported 関数のシグネチャ変更が後方互換性を保っているか
- `ask:` DB スキーマ変更がマイグレーションと対になっているか

## CC-8. Linguistic Anti-patterns（命名と振る舞い/属性の矛盾）

名前が示す意味と実際の振る舞い・属性が矛盾するパターン。開発者の約70%が「許容できない」と評価（Arnaoudova et al., 2016）。
A-F 分類の定義はこのチェックリスト内に完結。命名一般原則は `references/readability-principles.md` §5 参照。

### 振る舞いレベル

| 分類 | パターン | 例 | 重要度 |
|------|---------|-----|--------|
| **A: 名前以上の処理** | get/find が副作用を持つ | `getUser()` が存在しなければ作成もする | `consider:` |
| **B: 処理以上の名前** | bool メソッドが非 bool を返す | `isValid()` が検証結果オブジェクトを返す | `must:` |
| **C: 名前と逆の動作** | 名前と反対の処理をする | `open()` が実際には close する | `must:` |

### 属性レベル

| 分類 | パターン | 例 | 重要度 |
|------|---------|-----|--------|
| **D: 名前以上の状態** | 単数形が複数値を保持 | `item` が実は配列 | `consider:` |
| **E: 状態以上の名前** | 複数形が単一値を保持 | `users` が実は単一ユーザー | `consider:` |
| **F: 名前と逆の属性** | 名前と反対の値を持つ | `startTime` が終了時刻を格納 | `must:` |

## CC-9. Iterative Slop Detection（反復的品質劣化）

LLM エージェントが反復的編集で蓄積する品質劣化パターンの検出（SlopCodeBench, 2026）。
テストスイートは structural decay を検出できないため、レビューで捕捉する必要がある。
詳細: `references/iterative-degradation-awareness.md`

- `must:` 新ロジックが既存の大関数（50行超 or CC>10）にパッチされていないか → focused callable に分割すべき
- `must:` 同じ構造（引数パース、バリデーション等）が値だけ変えてコピーされていないか → 共通関数に抽出
- `consider:` elif/case チェーンが成長していないか → dispatch table やポリモーフィズムを検討
- `consider:` 変更が「既存コードに追加」ではなく「設計を拡張」しているか

## CC-10. Documentation Sync

Google eng-practices `looking-for.md` "Documentation" 由来。コード変更は対応する documentation の sync を伴わなければ陳腐化を蓄積する。

> **Severity 表記について**: 本ファイル (cross-cutting.md) の CC-1〜CC-10 は `must:` / `consider:` / `nit:` (小文字コロン) で統一。`agents/code-reviewer.md` Severity Labels の `MUST` / `CONSIDER` / `NIT` (大文字括弧) と意味は同一だが表記揺れあり (cross-cutting 側は checklist 記述、code-reviewer 側は出力フォーマット)。verdict 計算は code-reviewer.md の大文字側を参照する。

### 検出対象

- 公開 API / exported 関数のシグネチャ変更時に、対応する docstring / TSDoc / godoc が同期しているか
- public な振る舞いを変更したとき (戻り値・副作用・エラーケース) に README / 関連ドキュメント (`docs/`, `*.md`) が更新されているか
- CLI / コマンド / フラグ追加時に help text / usage example が追加されているか
- 削除した機能の参照が docs に残っていないか (dead link / dead reference)

### Severity

- `must:` 公開 API のシグネチャ変更 + docstring 不一致 (caller を誤誘導する)
- `must:` CLI フラグ追加 + `--help` 文字列未追加 (利用者が新機能を発見不可)
- `consider:` 内部関数の振る舞い変更 + コメント不一致 (誤読リスク)
- `nit:` 削除した機能への dead reference (実害は低いが整合性を欠く)

### 検出方法

- `git diff` で `func` / `class` / `export` キーワードを含むシグネチャ変更行を検出 → 同一ファイル or 隣接 `.md` の関連記述を grep (スラッシュは項目区切り、grep の OR 演算子ではない)
- CLI 変更検出: `argparse` / `cobra` / `clap` / `commander` の `add_argument` / `Flags()` 追加行 → `--help` 出力 or README usage section の sync 確認
- doc-gardener agent と直交: 本項目は **本 CL 内の同期** を強制、doc-gardener は **既存 docs の陳腐化定期スキャン** を担当

### 参照

- `agents/doc-gardener.md` — 既存ドキュメント陳腐化の定期スキャン (本 CL 範囲外の drift)
- `agents/code-reviewer.md` Section C (Every-Line + Good Things) — 全行レビュー原則の一環として本 CC-10 を毎レビュー適用

## CC-11. Presumptive Structural Blockers

Cursor `thermo-nuclear-code-quality-review` skill 由来。「振る舞いは正しいが構造が悪化する」変更を presumptive blocker として扱う。
代替設計 (code judo = behavior-preserving restructuring) が visible な場合、その path を merge 前に push する。

- `must:` 既存フローに「unrelated 場所への random if 文 bolt-on」が入っていないか → 専用 abstraction / state machine / policy object に push
- `must:` 機能固有のチェックが汎用モジュール (shared / common / base) に散布されていないか → 専用 abstraction の裏に隔離
- `must:` 薄い identity wrapper / `as any` / `unknown` 多用が「データ shape を隠す汎用機構」になっていないか → 明示的境界に置き換え
- `consider:` code judo opportunity 見逃し: branch / helper / layer 全体を消す restructuring path が visible なら、現 patch ではなくそちらを push
- `consider:` refactor が「complexity を移動させただけ」で concept 数を減らしていないか → モデル自体を simpler にできないか問う

### Review Phrases (structural critique 用)

- "this adds another special-case branch into an already busy flow. can we move this behind its own abstraction?"
- "this abstraction seems unnecessary. can we just keep the direct flow?"
- "i think there's a code-judo move here that makes this much simpler. can we reframe this so these branches disappear?"
- "this refactor moves complexity around, but doesn't really delete it. is there a way to make the model itself simpler?"

### 参照

- 出典: Cursor `cursor-team-kit` plugin `thermo-nuclear-code-quality-review` skill (2026, raw: `github.com/cursor/plugins`)
- CC-9 (LLM 反復編集での劣化) と相補: CC-9 は AI 編集起点、CC-11 は構造退行起点
- CC-12 (file size crossing) / CC-13 (canonical leak) と組合せて Cursor thermo-nuclear rubric の核を構成

## CC-12. File Size Crossing Threshold

Cursor `thermo-nuclear-code-quality-review` skill の 1k-line rule 由来。PR diff によって既存ファイルが 1000 行未満から 1000 行超に push される変更は presumptive blocker として扱う。

- `must:` 既存ファイル size が PR で `before < 1000 && after >= 1000` を transition + decompose の自明な道が visible (helper 抽出 / 副 module 化)
- `consider:` 既に 1000 行超のファイルに更に追加、または新規ファイルが 1000 行超で commit
- waive 条件: compelling structural reason + 結果ファイルが明確に組織化されている (作者が justification を提示)

### 既存仕組みとの関係

- `scripts/policy/structure-check.py:34` `MAX_FILE_LINES = 300` は **edit-time advisory** (PostToolUse warning)。本 CC-12 は **review-time presumptive blocker** で別軸
- 300 行 warning を無視して merge 直前に 1k 超に到達するケースを catch する保険
- 将来 mechanism shift (lefthook pre-commit で 1k crossing を hard block) も視野

### 参照

- 出典: Cursor `thermo-nuclear-code-quality-review` skill rule 1
- `scripts/policy/structure-check.py` (edit-time 300 行 advisory)

## CC-13. Canonical Helper / Layer Leak

Cursor `thermo-nuclear-code-quality-review` skill の canonical layer 由来。新規 helper / utility を追加する PR では、既存 canonical utility を duplicate していないか、logic が正しい layer (package / module) に置かれているかを検証する。

- `must:` 新規 bespoke helper が既存 canonical utility (`utils/` / `lib/` / `common/` 等の shared module) を duplicate していないか → 既存 helper を grep で検索、見つかれば置換を push
- `must:` 機能 logic が汎用 layer に leak していないか、または逆に汎用 logic が機能固有 layer に落ちていないか
- `consider:` 既存 architecture の natural extension にできる変更を、新規 abstraction で実装していないか

### 検出方法

- 新規追加された helper / 関数 / class の名前を `rg -t <lang> <name>` で codebase 全体検索
- 類似機能の派生命名 (例: `formatDate` / `dateToString` / `formatTimestamp`) も検索
- 同じ振る舞いの canonical 実装が見つかれば作者に置換を push

### Review Phrases

- "this looks like a bespoke helper for something we already have elsewhere. can we reuse the canonical one?"
- "is this logic living in the canonical layer, or did the diff leak details across a boundary?"

### 参照

- 出典: Cursor `thermo-nuclear-code-quality-review` skill rule 6
- CC-11 (structural blocker) と相補: CC-11 は branching / wrapper、CC-13 は helper duplicate / layer 配置

## CC-14. 結合度分析（Coupling）

結合度の強い順（上ほど危険）:

- `must:` **Content Coupling** — 呼び出し順序や内部状態に依存していないか
- `must:` **Common Coupling** — グローバル変数/シングルトンへの直接参照がないか → DI を使う
- `consider:` **Control Coupling** — 引数で「何をするか」を制御していないか → 関数分割で解消
- `consider:` **Stamp Coupling** — 不要に大きな構造体を渡していないか（ただし Data Coupling との兼ね合い）
- `consider:` **Data Coupling** — 基本型の引数順序間違いが起きないか → Newtype 検討

クラス/構造体内: フィールドを「メソッド間のデータ受け渡し」に使っていないか → 引数で渡す

## CC-15. 依存方向チェック

依存方向の原則に違反していないか:

- `must:` caller → callee（逆方向の依存は循環を生む）
- `must:` concrete → abstract（具体が抽象に依存する）
- `consider:` complex → simple（シンプルなデータモデルが複雑な Repository を持たない）
- `consider:` mutable → immutable
- `consider:` unstable → stable
- `consider:` algorithm → data model（data model が algorithm を持たない）

## CC-16. 冗長な依存の検出

- `consider:` A→B→C のとき、A が B を経由して C にアクセスしていないか → A→C に直接依存させる
- `consider:` N:M 依存が存在する場合は中間レイヤーの導入を検討
