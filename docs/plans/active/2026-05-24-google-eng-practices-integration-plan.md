---
title: Google eng-practices Integration Plan
date: 2026-05-24
status: pending
scale: L
estimated_tasks: 8
estimated_files: 11
related_analysis: docs/research/2026-05-24-google-eng-practices-absorb-analysis.md
---

# Google eng-practices Integration Plan

## Goal

Google エンジニアリング慣行 (eng-practices) から採用した 13 手法を AI review harness に統合し、コードレビューの品質・規律・一貫性を Google エンジニア水準に引き上げる。新規 3 ファイルと既存 8 ファイル編集を通じて、PR 分割戦略・礼儀規約・緊急定義・threshold 統一・positive principle・evidence-based feedback を harness に組み込む。

## Scope

- 採用項目: 13 件 (Gap/Partial 7 + Already 強化可能 6)
- ユーザー意図: "Google エンジニアになりたい" 目線で mindset/discipline transfer を含めて全採用。AI review が Google 水準の規律を毎回適用する harness を構築する
- 棄却項目: 13 件 (#20/#23/#26/#10/#22/#24/#4/#5/#12/#19 + #7/#8/#9 N/A)
- 規模: 3 new files + 8 edited files = L 規模確定

---

## Tasks

### T1a: PR 分割パターン参照ドキュメント新設

**File**: `.config/claude/references/pr-splitting-patterns.md` (NEW)
**Items**: #16 (cl-splitting-strategies)
**Scale**: S

**Content**:
- Section 1: 5 patterns table
  - stacking: 依存 CL を直列に積む (先行 CL が merge されるまで次を作成)
  - by-files: 1 CL = 1 ファイルグループ (refactoring file A + feature file B を分離)
  - horizontal: 全 layer (DB/API/UI) で機能 X を実装する 1 CL (thin vertical slice)
  - vertical: 1 CL = 1 layer (DB schema のみ、API のみ、UI のみ)
  - grid: 機能 × layer の格子を 1 セルずつ CL 化 (大規模機能向け)
- Section 2: 適用基準
  - 300 行以上 → splitting 検討
  - refactoring + feature 混在 → by-files または separate CL 強制
  - 複数の独立 subsystem 変更 → vertical または grid
  - 依存関係が直列 → stacking
- Section 3: anti-patterns
  - "後でまとめて PR" (no-cleanup-later 原則違反)
  - refactoring と bugfix の混在 (review cost 増大)
  - Large CL exception 乱用 (emergency 定義外への適用)
- Section 4: Large CL exception (references/emergency-definition.md へのポインタ)

**Acceptance criteria**:
- 5 patterns 全てに具体例 (ファイル名・CL 名レベルの例)
- `skills/github-pr/SKILL.md` と `skills/spec/SKILL.md` から参照される 1 行が追加されること (T3 で実施)
- 300 行 threshold が T3/T4/T5 と整合していること

---

### T1b: レビューコメント礼儀例文集新設

**File**: `.config/claude/references/review-courtesy-examples.md` (NEW)
**Items**: #11 (kind-comments-courtesy)
**Scale**: S

**Content**:
- Section 1: 原則 "Subject the code, not the author"
  - Bad: "なぜこんな実装にしたんですか？"
  - Good: "この実装は X の場合に Y 問題が起きます。Z にするとどうでしょう？"
- Section 2: Bad/Good 例文 5 件
  - 例 1: 設計批判 (Bad: 人格攻撃 / Good: 技術的根拠 + 代替案)
  - 例 2: 命名批判 (Bad: "変な名前" / Good: "この名前は X を想起させます。Y はどうでしょう？")
  - 例 3: 同意の表明 (Bad: 無言 / Good: "この抽象化はきれいです。理由は〜")
  - 例 4: 重要度の明示 (Bad: severity 不明 / Good: "Nit: 好みの問題ですが〜" / "必須: セキュリティ上〜")
  - 例 5: pushback 対応 (Bad: "そうですね、わかりました" / Good: "理解しました。それでも懸念が残るのは〜")
- Section 3: severity label 一覧 (Nit / FYI / Suggestion / Must / Blocking)
- Section 4: code-reviewer.md との関係 (T2 で追加されるセクションへのポインタ)

**Acceptance criteria**:
- Bad/Good 例文が最低 5 件あること
- severity label が既存 code-reviewer.md の label と整合していること
- `agents/code-reviewer.md` の courtesy セクション (T2) からこのファイルが参照されること

---

### T1c: 緊急定義ドキュメント新設

**File**: `.config/claude/references/emergency-definition.md` (NEW)
**Items**: #21 (emergency-definition)
**Scale**: S

**Content**:
- Section 1: emergency の定義 (Google eng-practices emergencies.md 準拠)
  - 本番障害: サービス全停止 / 重大なデータ損失 / セキュリティ侵害
  - リリースブロッカー: ロールバック不能なデプロイ直前の致命的バグ
  - shell/hook 破損: CI/harness が完全停止してチームが作業不能
- Section 2: NOT emergency (Friday closeout / soft deadline / "早く終わらせたい" は含まない)
  - 金曜日の "終業前に merge したい"
  - "ソフト締め切り" (明示的な緊急性なし)
  - 個人的な作業効率上の都合
- Section 3: Large CL exception との関係
  - emergency のみ Large CL を送ることが許容される
  - emergency 後は必ず follow-up CL で分割・整理する義務
- Section 4: AI review context での判断基準
  - code-reviewer が Large CL を受け取ったとき、emergency か否かを CL description から判断する rubric

**Acceptance criteria**:
- emergency / NOT emergency の境界が明確に定義されていること
- "Friday closeout" と "soft deadline" が明示的に除外されていること
- `skills/github-pr/SKILL.md` (T3) からこのファイルが参照されること
- Large CL exception (T3) と矛盾がないこと

---

### T2: code-reviewer agent への 6 セクション追加

**File**: `.config/claude/agents/code-reviewer.md` (EDIT)
**Items**: #14 (cleanup-later boundary), #11 (courtesy core), #3 (every-line + good-things), #13 (pushback-who-is-right), #17 (refactor-mixing-block), #18 (refactor-only-tests-nuance)
**Scale**: M-L
**Depends on**: T1b (courtesy examples), T1c (emergency definition)

**Content** (6 セクション追加):

**セクション A: cleanup-later boundary** (#14)
- TODO コメントが "新規追加" か "既存" かを明示的に区別する rubric
- "後で直す" TODO に期限・issue 番号がない場合は Blocking コメントを返す
- 既存 TODO への言及は NIT 扱い (T6 の cross-cutting.md と同期)

**セクション B: courtesy core** (#11)
- "Subject the code, not the author" を review comment 生成の大原則として明記
- 参照: `references/review-courtesy-examples.md` (T1b)
- severity label を必ず付与する (Nit / FYI / Suggestion / Must / Blocking)

**セクション C: every-line + good-things** (#3)
- 全行レビューを原則とする (ランダムサンプリングは NIT 対象外ファイルに限定)
- 良い点 (good things) を 1 件以上コメントに含める
- 良い点ゼロの review は "coldness bias" として警告付きで出力する

**セクション D: pushback-who-is-right** (#13)
- 開発者からの反論を受け取った場合、まず "開発者が正しい可能性" を検討する
- 自分の主張を維持する場合は technical facts / data / principles を引用する
- 感情的・権威的な pushback には "courtesy + evidence" で返す
- 双方が主張を維持する場合は NEEDS_HUMAN_REVIEW を付与する

**セクション E: refactor-mixing-block** (#17)
- 大規模 refactor と feature/bugfix が同一 CL に混在している場合を検出する
- 混在 CL に対して NIT ではなく Suggestion: 分割推奨を返す
- 基準: refactor 変更が 50 行以上 + feature/bugfix 変更が 20 行以上 = mixing-block 対象

**セクション F: refactor-only-tests-nuance** (#18)
- refactor-only CL (機能変更なし) でも既存テストのパスは必須
- refactor-only テスト: 新テストは "behavior 証明" ではなく "不変量確認" にとどめる
- 独立テスト CL 先行パターン: テスト追加 CL → refactor CL の順を recommended として明記

**Acceptance criteria**:
- 6 セクション全てが独立して invocation-testable であること (各セクションを単体で参照できる見出し構造)
- T1b, T1c への参照リンクが正確であること
- 既存 code-reviewer.md のスタイル・構造に合致していること
- severity label (Nit/FYI/Suggestion/Must/Blocking) の用語が全セクションで一貫していること

---

### T3: github-pr/SKILL.md の threshold 統一 + Large CL exception 追加

**File**: `.config/claude/skills/github-pr/SKILL.md` (EDIT)
**Items**: #15 (small-cl-one-thing threshold), #25 (Large CL exception)
**Scale**: S
**Depends on**: T1a (pr-splitting-patterns), T1c (emergency-definition)

**Content**:
- `#15` threshold を既存の記述 (400 行?) から統一閾値に更新
  - 統一閾値: 300 行 (T4/T5 と同値)
  - 根拠: "one thing" の目安として Google eng-practices の小規模 CL 定義に準拠
- `#25` Large CL exception セクションを追加
  - emergency 定義に該当する場合のみ Large CL を送ることが許容される
  - 参照: `references/emergency-definition.md` (T1c)
  - Large CL 送付時の必須記載事項: emergency 種別 / 影響範囲 / follow-up CL 計画
- `#16` PR 分割戦略へのポインタ追加
  - 参照: `references/pr-splitting-patterns.md` (T1a)

**Acceptance criteria**:
- threshold が 300 行に統一されていること
- Large CL exception が emergency-definition.md を正確に参照していること
- T4/T5 との threshold 値が一致していること (verify: grep で確認)

---

### T4: github-pr/self-review.md の threshold 同期

**File**: `.config/claude/skills/github-pr/self-review.md` (EDIT)
**Items**: #15 (threshold sync)
**Scale**: S
**Depends on**: T3

**Content**:
- 既存の "400 行" 等の threshold 記述を "300 行" に統一
- T3 で確定した統一閾値に合わせる
- 変更は threshold 数値のみ (文脈・周辺テキストは変更しない)

**Acceptance criteria**:
- `grep -n "行\|lines\|threshold" self-review.md` で threshold 記述が全て 300 行になっていること
- T3 との値が一致していること

---

### T5: golang-reviewer.md の threshold 同期

**File**: `.config/claude/agents/golang-reviewer.md` (EDIT)
**Items**: #15 (threshold sync)
**Scale**: S
**Depends on**: T3

**Content**:
- 既存の "300 行" (既にこの値の場合は確認のみ) または他の threshold 記述を統一閾値に合わせる
- golang 固有の大規模ファイル事情 (generated code 等) を考慮した例外注記があれば維持する

**Acceptance criteria**:
- `grep -n "行\|lines\|threshold" golang-reviewer.md` で threshold 記述が統一閾値と一致していること
- generated code (`.pb.go`, `_gen.go` 等) の除外ルールが維持されていること

---

### T6: cross-cutting.md の TODO 新規 vs 既存 区別

**File**: `.config/claude/references/review-checklists/cross-cutting.md` (EDIT)
**Items**: #14 (cleanup-later boundary)
**Scale**: S
**Depends on**: T2 (セクション A の内容確定後)

**Content**:
- 既存の TODO チェック項目を "新規 TODO" と "既存 TODO" に分割
  - 新規 TODO: 期限・issue 番号がない場合は Blocking
  - 既存 TODO: レビュー対象 CL で変更されていない場合は NIT (言及のみ)
- "no-cleanup-later" 原則への参照を追加 (agents/code-reviewer.md セクション A)
- 既存の TODO 検出パターン (正規表現等) を維持しつつ新規/既存フラグを追加

**Acceptance criteria**:
- 新規 TODO と既存 TODO の区別が明確なチェックリスト形式であること
- T2 セクション A の rubric と矛盾がないこと
- `grep "TODO" cross-cutting.md` で新規/既存両方の基準が確認できること

---

### T7: review skill への positive principle + evidence-based rubric + design-first gate 追加

**Files**:
- `.config/claude/skills/review/SKILL.md` (EDIT)
- `.config/claude/references/review-consensus-policy.md` (EDIT)
**Items**: #1 (code-health-improvement-principle / positive principle), #2 (technical-facts-over-opinions), #6 (navigate-three-steps / design-first feedback gate)
**Scale**: M
**Depends on**: なし (独立)

**Content for skills/review/SKILL.md**:

**positive principle** (#1):
- review の primary purpose は "code health の改善" であり "完璧の追求" ではない
- approve 基準: CL が code health を改善するなら approve (完璧でなくても)
- "improve code health" の具体的チェックリスト (可読性 / テスト / 設計 / 保守性)

**evidence-based feedback rubric** (#2):
- review コメントは "technical facts / data / principles" のいずれかを引用すること
- 個人的好みや opinions を根拠にした feedback は NG
- 例外: 明示的に "個人的な好み" と label した提案 (Nit 扱い)
- evidence の種類: spec / RFC / language spec / established best practices / benchmark

**design-first feedback gate** (#6):
- navigate-three-steps: broad comment → specific comment の順で進める
- 設計上の重大問題 (design issues) を発見した場合、詳細コメントより先に返却する
- design-first feedback の発動基準: アーキテクチャ変更が必要 / API 境界の問題 / 不可逆な設計決定

**Content for references/review-consensus-policy.md**:
- evidence-based feedback の判定基準 (詳細版)
- design-first feedback gate の escalation パス
- pushback 解決フロー (T2 セクション D と連携)

**Acceptance criteria**:
- positive principle が approve/reject 判定フローの先頭に配置されていること
- evidence-based feedback rubric が "opinions vs facts" を明確に区別していること
- design-first feedback gate の発動条件が verifiable な基準で定義されていること
- review-consensus-policy.md の変更が skills/review/SKILL.md と矛盾しないこと

---

### T8: MEMORY.md へのポインタ追記

**File**: `.config/claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md` (EDIT)
**Items**: meta (absorb 記録)
**Scale**: S
**Depends on**: T1a, T1b, T1c, T2, T3, T4, T5, T6, T7 (全タスク完了後)

**Content**:
- 外部知見索引セクションに以下を追記:
  ```
  - [Google eng-practices (2026-05-24)](../../../dotfiles/docs/research/2026-05-24-google-eng-practices-absorb-analysis.md) — 13 手法採用 (PR 分割 5 patterns / courtesy Bad-Good 例文 / emergency 定義 / threshold 300 行統一 / positive principle / evidence-based feedback / design-first gate)。新規 3 ファイル + 既存 8 ファイル編集。
  ```

**Acceptance criteria**:
- 追記行が他のポインタエントリと同形式であること
- analysis ファイルパスが正確であること
- 採用手法の概要が 1 行以内に収まっていること

---

## Dependencies (graph)

```
T1a (pr-splitting-patterns.md NEW)
T1b (review-courtesy-examples.md NEW)
T1c (emergency-definition.md NEW)
    |                |                |
    v                v                v
  T3 (#16 ptr)    T2 (courtesy)    T3 (#25 exception)
                  T2 (cleanup)
    |
    v
T4 (self-review threshold sync)
T5 (golang-reviewer threshold sync)
    |
    v
T2 → T6 (TODO 区別 sync)

T7 (review skill) — 独立 (T1-T6 に依存なし)

T1a + T1b + T1c + T2 + T3 + T4 + T5 + T6 + T7
    |
    v
T8 (MEMORY.md pointer — 全完了後)
```

---

## Execution order

1. **T1a, T1b, T1c** (parallel — 3 NEW files, 依存なし)
2. **T2** (code-reviewer.md — T1b, T1c 完了後)
3. **T3** (github-pr/SKILL.md — T1a, T1c 完了後)
4. **T4, T5, T6** (parallel sync — T2/T3 完了後)
5. **T7** (review skill — 独立、どのタイミングでも実行可能だが T4/T5/T6 と並列推奨)
6. **T8** (MEMORY.md — 全タスク完了後)

推奨: 新セッションで `/rpi docs/plans/active/2026-05-24-google-eng-practices-integration-plan.md`

---

## Verification

各タスク完了後:
- `task validate-configs` — settings.json / config 整合性確認
- `task validate-symlinks` — symlink 健全性確認
- `lefthook run pre-commit` — pre-commit hook が通ること
- `grep -rn "300" ~/.claude/skills/github-pr/ ~/.claude/agents/golang-reviewer.md` — threshold 統一確認 (T3/T4/T5 完了後)

全タスク完了後:
- 13 採用項目すべてが対応ファイルに反映されていること (逆引きチェックリストを T8 実施前に作成)
- `grep -rn "review-courtesy-examples\|emergency-definition\|pr-splitting-patterns" ~/.claude/` — 参照整合性確認
- code-reviewer agent の 6 新セクションが個別に invocation-testable であること

---

## Acceptance criteria (全体)

- 13 採用項目 (#14/#21/#25/#1/#2/#6/#13/#15/#16/#11/#3/#17/#18) すべてが対応ファイルに反映されていること
- 新規 3 ファイル (T1a/T1b/T1c) が `~/.claude/references/` に配置されていること
- 統一 threshold 300 行が T3/T4/T5 の 3 ファイルで一致していること
- code-reviewer.md の 6 セクションが独立した見出しで構成され、個別参照可能であること
- 既存 dotfiles の golden-principles / KISS/YAGNI/DRY との矛盾がないこと
- L 規模なので task ごとに verify cycle を回すこと
- `task validate-configs` と `task validate-symlinks` が全タスク完了後に green であること

---

Generated by /absorb on 2026-05-24
