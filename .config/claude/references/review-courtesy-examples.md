---
status: reference
last_reviewed: 2026-05-24
source_url: https://google.github.io/eng-practices/review/reviewer/comments.html
source_repo: https://github.com/google/eng-practices/blob/master/review/reviewer/comments.md
---

# Review Courtesy Examples

Google eng-practices `comments.md` ([Web](https://google.github.io/eng-practices/review/reviewer/comments.html) / [Repo](https://github.com/google/eng-practices/blob/master/review/reviewer/comments.md)) "Courtesy" 原則の Bad/Good 例文集。
`agents/code-reviewer.md` の Section B (courtesy core) から参照される。

## 1. 原則: "Subject the code, not the author"

レビューコメントは **コード** に向ける。**書いた人** に向けない。
人格・能力への評価は感情的 pushback を引き起こし、技術判断を歪める。

| 良くない例 | 良い例 |
|----------|--------|
| 「なぜこんな実装にしたんですか？」 | 「この実装は X の場合に Y 問題が起きます。Z にするとどうでしょう？」 |

## 2. Bad/Good 例文 5 件

### 例 1: 設計批判

❌ **Bad**: 「設計のセンスがない。最初からやり直したほうが良い」
- 人格攻撃 (sense)、全否定 (やり直し)、代替案なし

✅ **Good**: 「`[CONSIDER]` この設計は order と payment の責務が混在しているため、payment 失敗時に order rollback が複雑になります。`OrderService` と `PaymentService` を分離し、Saga パターンで連携する案はいかがでしょうか？」
- 技術的根拠 (責務混在 → rollback 複雑)、具体的代替案 (Saga)、severity 明示

### 例 2: 命名批判

❌ **Bad**: 「変な名前。読みづらい」
- 主観 (変)、根拠なし、代替案なし

✅ **Good**: 「`[NIT]` `doStuff()` は処理内容が読み取れません。実装を見ると user notification を送っているので `notifyUser()` あたりはどうでしょう？」
- 具体的問題 (読み取れない)、実装観察に基づく代替案、severity 明示

### 例 3: 同意の表明 (good things を述べる)

❌ **Bad**: (無言)
- 良い実装に何も言わないと、reviewer の評価軸が「悪い点だけ」に偏る (coldness bias)

✅ **Good**: 「`[FYI]` この抽象化は依存方向が `concrete → abstract` に統一されていてきれいです。テストもよくカバーされています」
- 良い点を具体的に言語化、抽象論ではない

### 例 4: 重要度の明示

❌ **Bad**: 「ここのテストを追加してください」
- severity 不明 — MUST なのか NIT なのか分からず開発者が優先順位を決められない

✅ **Good**: 「`[MUST]` 認証フローのテストが欠落しています。auth bypass の regression を防ぐため、最低でも happy path + invalid token + expired token の 3 ケースが必要です」
- severity 明示、必要性の根拠、最小要件を提示

### 例 5: pushback への対応

❌ **Bad**: 「そうですね、わかりました」
- 自分の懸念を取り下げる根拠を示していない (pushback に屈しただけ)

✅ **Good**: 「`[ASK]` 理解しました。それでも懸念が残るのは、CL-1234 で同じパターンが原因で incident #5678 が起きたためです。今回はこの理由で許容できますか、それとも前回と異なる事情がありますか？」
- 開発者の主張を一度受け止める (理解しました)、根拠付きで懸念を維持、判断を委ねる

## 3. Severity Label マッピング表

本リポジトリの severity ラベルと Google eng-practices 元用語の対応:

| 本リポジトリ (既存) | Google eng-practices 元用語 | 意味 |
|-------------------|---------------------------|------|
| `MUST` | Blocking | 修正必須 (セキュリティ・バグ・GP 違反) |
| `CONSIDER` | Optional (or Consider) | 検討推奨 (設計改善・保守性) |
| `NIT` | Nit | 些末な指摘 (スタイル・好み) |
| `ASK` | Question / 要回答 | 設計意図の質問 |
| `FYI` | FYI | 参考情報共有 (対応不要) |

**注**: マッピング表の `Blocking` / `Suggestion` / `Nit` は Google 元用語の説明であり、本リポジトリの severity ラベルとしては**使用しない** (Verdict 計算式が既存ラベルに依存)。

本リポジトリでは既存の `MUST/CONSIDER/NIT/ASK/FYI` を維持する (`agents/code-reviewer.md` の Verdict 計算式 — `MUST≥1→BLOCK` / `CONSIDER≥3→NEEDS_FIX` — が依存)。
Google 元用語に慣れた reviewer / Google eng-practices 由来の他文献を参照する際は本マッピングで読み替える。

詳細: `agents/code-reviewer.md` "Severity Labels: Pragmatic Expert" Section (本リポジトリ既存ラベル定義)。

**更新ルール**: Google が元用語を変更した場合 (例: "Nit" → "Minor")、本マッピング表と `agents/code-reviewer.md` "Severity Labels" を**同時更新**する。Verdict 計算式 (本リポジトリ既存ラベル側) は変更しない。

## 4. 参照

- `agents/code-reviewer.md` Section B (courtesy core)、Section D (pushback-who-is-right)
- `skills/review/SKILL.md` Principle 2 (Evidence-Based Feedback) — courtesy + evidence の組み合わせ運用
