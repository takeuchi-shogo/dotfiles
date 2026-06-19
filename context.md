# Context: 応答の「溜め」問題と恒久化

## 問題

ユーザーは私 (Claude) の応答が「ためてためてる」(溜める) ことを嫌う。
具体的には: 結論・判定を後回しにする / 「〜します」「まず〜を確認する」と段取りを予告してから本題に入る / 思わせぶりな前置き・修辞疑問で導出を演出する。

## 自己認識の限界 (正直な現状)

- リアルタイムには気づけない。出力を一語ずつ生成しながら「今溜めている」と検閲する仕組みが私にはない。
- 後から指摘されればわかるが、生成の最中に自律的には止められない。
- さっき `prose.md` に「溜め回避」を書いた直後の同一セッションでも、まだ溜めた (「後処理を進める。まず〜を確認する」)。

## なぜ書いても直後に効かないか (構造)

- `output-styles/prose.md` に「溜め・もったいぶりを避ける」を追記済み。ただし output-style が有効化 (`settings` の `outputStyle: prose`) されていないと、その内容は私のコンテキストに載らない。
- memory `feedback_response_no_buildup` も MEMORY.md 経由で索引されるのは次セッション以降。
- → 書いた内容が「今このセッションの私のコンテキスト」に入っていない限り、直後でも繰り返す。

## 恒久化の選択肢 (どれにするか未決)

1. **`/output-mode prose` を有効化** — 即効くが揮発的 (セッション限り)
2. **CLAUDE.md 本体 (常時ロード) に1行** — 全セッション恒久。ただし指示数コスト (IFScale)
3. **memory が次セッションから索引** — 自動だが遅効

## 既に完了した関連作業 (japanese-tech-writing absorb, 2026-06-18)

- `references/japanese-ai-prose.md` を文章規範へ拡張 (論証の厳密さ / 段落と論証 / 整形 / 演出の節度、長文ドキュメント限定)
- `output-styles/prose.md` に「溜め・もったいぶりを避ける」
- memory `feedback_response_no_buildup` + MEMORY.md ポインタ
- 分析レポート `docs/research/2026-06-18-japanese-tech-writing-absorb-analysis.md`
- Obsidian `05-Literature/lit-k16shikano-japanese-tech-writing.md`
