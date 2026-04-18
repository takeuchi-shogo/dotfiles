---
name: rewrite
description: >
  テキストをターゲットオーディエンス向けにリライトする。プリセット（technical, executive, slack, casual）
  またはカスタムペルソナを指定可能。
  Triggers: 'リライト', 'rewrite', '書き直して', '言い換えて', 'rewrite for', 'この文章を変換'.
  Do NOT use for: 翻訳（直接依頼で十分）、文献ノート作成（use /digest）、コンテンツ生成（use /obsidian-content）。
origin: self
argument-hint: "[preset: technical|executive|slack|casual] or [for persona]"
allowed-tools: AskUserQuestion
metadata:
  pattern: transformer
---

# /rewrite — Context-Aware Rewriting

テキストをターゲットオーディエンス向けにリライトするスキル。

## 引数の解釈

- `/rewrite technical` → technical プリセット
- `/rewrite executive` → executive プリセット
- `/rewrite slack` → slack プリセット
- `/rewrite casual` → casual プリセット
- `/rewrite for [ペルソナ]` → カスタムペルソナ（例: `/rewrite for 新入社員`）
- `/rewrite`（引数なし） → AskUserQuestion でプリセットまたはペルソナを聞く

## Step 1: テキスト取得

AskUserQuestion で聞く:

「リライトするテキストを貼り付けてください。」

（引数にテキストが含まれている場合はスキップ）

## Step 2: ターゲット確認

引数でプリセットまたはペルソナが指定されていない場合、AskUserQuestion で聞く:

「どのオーディエンス向けにリライトしますか？」
- `technical` — 実装者・エンジニア向け（具体的、正確、コード例あり）
- `executive` — 意思決定者向け（結論先行、インパクト重視、数字で語る）
- `slack` — Slack メッセージ向け（3-bullet、簡潔、アクションアイテム明確）
- `casual` — 一般向け（平易な言葉、専門用語を避ける）
- または自由にペルソナを指定（例: 「懐疑的な CTO」「初めてのユーザー」）

## Step 3: リライト実行

指定されたオーディエンスに合わせてテキストをリライトする。

### プリセット別ガイドライン

| プリセット | トーン | 構造 | 特徴 |
|-----------|--------|------|------|
| `technical` | 正確・簡潔 | 問題→解法→実装 | コード例、具体的な数値、技術用語OK |
| `executive` | 結論先行 | 結論→根拠→Next Steps | ビジネスインパクト、ROI、リスク |
| `slack` | カジュアル・簡潔 | 3 bullet points max | アクションアイテム、メンション想定 |
| `casual` | 平易・親しみやすい | ストーリー形式 | 専門用語を避ける、比喩を活用 |

### カスタムペルソナ

プリセット以外のペルソナが指定された場合:
1. そのペルソナの知識レベル・関心事・コミュニケーションスタイルを推定
2. 推定に基づいてリライト
3. 「このペルソナの想定: ...」を冒頭に1行添える

## Step 4: 出力

リライト結果を表示する。

```
## Rewrite ({target})

{リライト後のテキスト}

---
**変更ポイント**: {元テキストからの主な変更点を1-2行で}
```

## Chaining

- `/obsidian-content` → `/rewrite` で Vault コンテンツの多形式展開
- `/digest summarize` → `/rewrite` で要約のオーディエンス別変換
- 複数プリセットで連続実行して比較も可能

## Anti-Patterns

| NG | 理由 |
|----|------|
| 元テキストの意味を変える | リライトは形式の変換。内容の正確性は保つ |
| 情報を勝手に追加する | 元テキストにない情報は追加しない |
| 全プリセットを一度に出力する | 聞かれていないバリエーションは出さない |
