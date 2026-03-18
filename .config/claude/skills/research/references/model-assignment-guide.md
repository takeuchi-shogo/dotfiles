# Model Assignment Guide

サブタスクの性質に応じてモデルを自動割り当てする基準。

## Assignment Matrix

| サブタスク性質 | 推奨モデル | 理由 |
|---------------|-----------|------|
| 外部リサーチ（Web検索、最新情報） | Gemini CLI | Google Search grounding、1Mコンテキスト |
| 深い推論・設計分析 | Codex CLI (gpt-5.4) | reasoning effort: high で深い分析 |
| コードベース分析 | claude -p | ローカルファイル直接アクセス |
| 論文要約・文献調査 | Gemini CLI | 1Mコンテキストで長文処理 |
| 比較分析・トレードオフ | Codex CLI | 構造化推論が得意 |
| デフォルト（汎用） | claude -p | 最も安定・高速 |

## Model Characteristics

### Gemini CLI
- **強み**: 1M コンテキスト、Google Search grounding、マルチモーダル
- **弱み**: 過度に楽観的な傾向、指示の細部を見落とす場合あり
- **コマンド例**: `gemini -p "Research topic" --grounding`

### Codex CLI (gpt-5.4)
- **強み**: 深い推論、構造化分析、reasoning effort 調整可能
- **弱み**: 外部検索なし、ローカルファイルアクセスが限定的
- **コマンド例**: `codex exec "Analyze..." --reasoning-effort high`

### claude -p (headless)
- **強み**: ローカルファイル完全アクセス、ツール使用、安定性
- **弱み**: 200K コンテキスト制限
- **コマンド例**: `claude -p "Analyze..." --allowedTools Read,Grep,Glob`

## Language Protocol

- CLI への指示は **英語** で記述する
- ユーザーへの最終レポートは **日本語** で記述する
