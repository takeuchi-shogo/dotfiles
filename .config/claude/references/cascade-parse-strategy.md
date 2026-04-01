# Cascade Parse Strategy

サブエージェント/外部ツールの出力パースにおけるカスケードリトライ戦略。

> 着想元: Mulian+ 2026 "AgentFixer" — パース障害が全障害の 38%。
> "sequential parsing mechanism across all agents that attempts multiple parsing strategies in cascade"

## 戦略

出力を以下の順序で試行し、最初に成功した結果を採用する:

```
1. Strict JSON parse (JSON.parse / json.loads)
2. JSON repair (trailing comma, unquoted keys の自動修正)
3. Markdown code block 抽出 → 再パース (```json ... ``` ブロック)
4. Regex ベース構造抽出 (key-value ペア、リスト)
5. LLM リパース ("以下の出力を JSON に変換してください" — 最終手段)
```

## 適用場面

| 場面 | 例 |
|------|---|
| サブエージェント出力 | Agent ツールの返り値が期待フォーマットでない |
| MCP ツール応答 | MCP サーバーが非標準レスポンスを返す |
| CLI 出力パース | `codex exec`, `gemini` 等の stdout パース |

## 実装ガイドライン

- Step 1-3 は **同期的に即時試行**（コスト: ゼロ）
- Step 4 は **構造が部分的に壊れている場合のみ**
- Step 5 は **最終手段**。LLM コール追加のコストがあるため、他が全て失敗した場合のみ
- 全ステップ失敗時は **元の出力をそのまま文字列として返し**、呼び出し元に判断を委ねる

## FM-021 との関係

`failure-taxonomy.md` の FM-021 (Output Parse Failure) の suggestedFix として参照される。
パース失敗の検出は FM-021、対処はこのドキュメントが担当する。
