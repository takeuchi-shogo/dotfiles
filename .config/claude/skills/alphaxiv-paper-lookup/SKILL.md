---
name: alphaxiv-paper-lookup
description: >
  arxiv 論文を alphaxiv.org 経由で構造化レポートとして取得する。PDF を読むより高速・高精度。
  Triggers: arxiv URL, 論文 ID (2401.12345), alphaxiv URL, '論文を読んで', 'paper lookup'.
  Do NOT use for non-arxiv content — use WebFetch or /research instead.
allowed-tools: WebFetch, Bash, Read
disable-model-invocation: true
metadata:
  pattern: lookup
---

# AlphaXiv Paper Lookup

arxiv 論文の構造化レポートを alphaxiv.org から取得する。

## When to Use

- ユーザーが arxiv URL / 論文 ID / alphaxiv URL を共有した
- 論文の要約・分析・統合を依頼された
- `/research` のサブタスクとして論文内容が必要な場合

## Step 1: Paper ID の抽出

| 入力例 | Paper ID |
|---|---|
| `https://arxiv.org/abs/2401.12345` | `2401.12345` |
| `https://arxiv.org/pdf/2401.12345` | `2401.12345` |
| `https://alphaxiv.org/overview/2401.12345` | `2401.12345` |
| `2401.12345v2` | `2401.12345v2` |
| `2401.12345` | `2401.12345` |

バージョン指定（`v2` 等）がある場合はそのまま保持する。

## Step 2: 構造化レポートの取得

```
WebFetch: https://alphaxiv.org/overview/{PAPER_ID}.md
```

これが **第一選択**。AI 生成の構造化分析レポートが返る。

## Step 3: フォールバック（必要な場合のみ）

Step 2 のレポートに不足がある場合（特定の数式・表・セクションの詳細が必要）:

```
WebFetch: https://alphaxiv.org/abs/{PAPER_ID}.md
```

論文全文が markdown で返る。

## Error Handling

| 状況 | 対応 |
|---|---|
| Step 2 が 404 | Step 3 を試す |
| Step 3 も 404 | ユーザーに `https://arxiv.org/pdf/{PAPER_ID}` を案内 |

## Anti-Patterns

- 両エンドポイントを同時に叩く（Step 2 で十分なケースが大半）
- レポート内容をそのまま貼り付ける（ユーザーの質問に合わせて要約・構造化する）
- arxiv 以外のソースにこのスキルを使う
