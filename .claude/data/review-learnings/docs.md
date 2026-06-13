# ドキュメント / md レビュー観点

用途: `/review` 時に code-reviewer プロンプトへ注入される個人レビュー観点 (docs/ 配下の md / CLAUDE.md 系 / reference / skill 定義の散文部分)。
更新方法: 過去のレビュー指摘 (`feedback_*.md` / `review-findings.jsonl`) から蒸留。新しい指摘が出たら出典コメント付きで追記する。創作禁止。

## 指示数 / トークンコスト

- CLAUDE.md / AGENTS.md にルールを追加する変更で、その指示が hook で自動強制できないか確認したか。「hook で強制 > 指示で伝達」の優先順位。 <!-- source: feedback_instruction_cost.md -->
- 追加する指示が既存の指示と統合できないか、既に hook で強制済みのルールの二重記載になっていないか確認する (指示 1 つあたり推論トークン +1-2%)。 <!-- source: feedback_instruction_cost.md -->
- CLAUDE.md を「行数」で評価しない。信号対雑音比で見て、矛盾する指示・冗長な指示・コードから推論できる情報 (コードベース概要等) を削る。 <!-- source: feedback_claudemd_length.md -->

## Bad Example 併記

- 繰り返し違反されるルールを CLAUDE.md / rules に書く場合、`Good:` / `Bad:` のペアで間違い例も併記したか。ただし全ルールには付けない (指示コスト考慮)。 <!-- source: feedback_bad_example_pattern.md -->

## MEMORY.md スタイル

- MEMORY.md にインライン詳細を長文で書いていないか。1-2 行サマリ + 別ファイルへのパス参照にする (毎ターンロードされ命令バジェットを圧迫するため)。 <!-- source: feedback_memory_style.md -->

## ドキュメント整合性 / drift

- コード変更に伴い更新すべきだった md (reference / taxonomy / spec) が diff から漏れていないか。例: reviewer 名やステップ定義がコードと不整合 (code-doc drift)。 <!-- source: rf-2026-06-12-002 / feedback_hidden_impact_analysis.md -->
- 「現存」「実装済」等の事実記述が、本 PR の削除・変更で事実に反していないか。削除日 / 確定日に更新する。 <!-- source: rf-2026-06-12-003 -->
- 「N 段階」と書いて N 個列挙されていない等、本文と列挙数の不一致がないか。 <!-- source: rf-2026-04-11-010 -->
- 未実装機能への参照 (例: `--three-arm` 未実装) に注記があるか。docstring の誤記 (例: stdin/stdout の取り違え) がないか。 <!-- source: rf-2026-04-11-009 / rf-2026-05-06-005 -->
