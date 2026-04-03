# Lessons Learned — 1行 Gotcha 集

> セッション中に「壊れた→直した」パターンを発見したら、1行で追記する。
> エッセイ不要。教訓と対処だけ。このファイルをセッション開始時に最初に読む。
>
> フォーマット:
> ```
> - [何が起きた] -- [何で直した / 次回どうすべきか]
>   verify: Grep("pattern", path="scope") → 期待結果
> ```
> verify: 行は `/improve` の Garden フェーズで機械検証される。
> verify を書けないルールは曖昧すぎる — 書けるまで具体化する。

## Memory & Config

- hook の正規表現で `\b` を使うと日本語で誤動作する -- `(?=[^a-zA-Z0-9]|$)` を使う
  verify: Grep("\\\\b", path=".config/claude/scripts/") → 0 matches（新規追加分）
- 成功より失敗エピソードを優先記録する -- 失敗の再発防止が信頼性向上に最も寄与する（Generative Agents: Reflection 研究）
  verify: manual（記録方針）
- MEMORY.md に詳細を書くとすぐ 200行上限に達する -- ポインタ + 1行サマリのみ
  verify: MEMORY.md の各エントリ行が 150文字以下
- CLAUDE.md の行数より指示数(IFScale)がトークンコストに効く -- 行を減らすより指示を減らす
  verify: manual（定性的ルール）
- lint config を「直す」と hook 体系が壊れる -- 設定ではなくコードを直す
  verify: git diff に .eslintrc*, biome.json, .prettierrc* が含まれない
- `git commit --no-verify` で hook を飛ばすと品質ゲートが全て無効化される -- 絶対禁止
  verify: Grep("--no-verify", path=".config/claude/") → 0 matches

## Review & Debug

- レビュー中に Edit/Write すると差分が汚れる -- レビューは read-only で完了させる
  verify: レビューエージェントの tools に Edit/Write が含まれていない
- diff 直接参照だけでは隠れた影響範囲を見落とす -- 暗黙の契約変更・間接依存も調査する
  verify: manual（行動ルール）
- Codex の指摘を「些末」と判断して無視すると後でバグになる -- 速さより品質、指摘は全て確認
  verify: manual（行動ルール）
- ユーザーの解釈よりも生のエラーログ・スタックトレースを信頼する -- 生データ優先
  verify: manual（行動ルール）

## Agent & Model

- Claude は失敗が蓄積すると萎縮（保守化）または desperation（reward hacking）に分岐し、期待を感じると追従(Sycophancy)する -- 萎縮: 消極的提案、desperation: テスト迂回・検証スキップ、Sycophancy: 結果捏造・検証虚偽申告に注意 (Anthropic "Emotion Concepts", 2026)
  verify: manual（認知バイアス警告）
- Gemini は過度に楽観的な見積もりを出す -- 楽観バイアスを割り引く
  verify: manual（認知バイアス警告）
- Codex の reasoning effort は通常 high、レビュー時は xhigh -- 用途で使い分ける
  verify: Grep("reasoning.*effort", path=".config/claude/rules/codex-delegation.md") → 1+ matches
- LLM 自動生成のスキル修正は平均 -1.3pp -- 人間レビュー必須
  verify: Grep("auto_accept.*skills", path=".config/claude/references/improve-policy.md") → 0 matches

## Workflow

- 2回同じドメイン知識を説明したら spec/reference に書き下ろす -- 繰り返し説明は codify のシグナル
  verify: manual（行動ルール）
- 探索時は precision に偏りやすい -- 意識的に recall(網羅)を上げる
  verify: manual（行動ルール）
- 12時間放置するとエージェントが別の問題を解き始める -- ドリフトガード必須
  verify: Grep("drift|ドリフト", path=".config/claude/references/improve-policy.md") → 1+ matches
