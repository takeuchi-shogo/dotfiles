# Codex CLI 委譲ルール

Codex CLI は設計判断、深い推論、複雑なデバッグを担当する。以下の場面で Codex への委譲を検討せよ。

## 委譲すべきケース

- **実装前リスク分析**: Plan 策定後、実装前に潜在リスクを洗い出す → `codex-risk-reviewer` エージェント。Claude の「注意の幅」（プロダクト直感）を Codex の「注意の深さ」（リスク検出）で補完する
- **セキュリティ深掘り調査**: 潜在的脆弱性の根本原因分析、攻撃ベクトル評価、セキュリティアーキテクチャレビュー → `codex exec -p security`（xhigh reasoning + read-only）。`security-reviewer` エージェントの表面チェックを Codex の深い推論で補完する
- **設計判断**: アーキテクチャ選定、モジュール構造、API設計、技術選定
- **トレードオフ分析**: 「AとBどちらが良いか」という比較・評価
- **複雑なデバッグ**: 通常の debugger エージェントで原因特定が困難な場合 → `codex-debugger` エージェント
- **コードレビュー（セカンドオピニオン）**: ~30行以上の変更で `codex-reviewer` エージェントを並列起動
- **Plan 批評（Second Opinion）**: L 規模の Plan 策定後、clean context で盲点を指摘させる
- **Debate（マルチモデル議論）**: `/debate` スキルで Gemini と並列に独立した視点を提供
- **リファクタリング計画**: 大規模な構造変更の計画策定

## 委譲方法

- **リスク分析**: `codex-risk-reviewer` エージェント（read-only、Plan → Implement の間で起動）
- **セキュリティ分析**: `codex exec --skip-git-repo-check -m gpt-5.4 -p security "..."` — profiles.security で xhigh + read-only が自動適用
- **分析・レビュー**: `codex-debugger` エージェント（read-only）
- **コードレビュー**: `codex-reviewer` エージェント（read-only、他レビューアーと並列起動）
- **スキル実行**: `codex` スキル or `codex-review` スキル（手動実行用）
- **直接呼び出し**: `codex exec --skip-git-repo-check -m gpt-5.4 --sandbox read-only "..." 2>/dev/null`
- **レビュー/セキュリティは必ず xhigh**: セキュリティ分析には `-p security` を使用（profiles.security で xhigh + read-only が自動適用）。通常レビューは `--config model_reasoning_effort="xhigh"` を指定

## Codex 深掘り分析の使い分け

| タイミング | エージェント | reasoning_effort | 目的 |
|---|---|---|---|
| Plan 策定直後（L規模） | `codex exec` 直接 | high | Plan の盲点・前提の誤りを clean context で批評 |
| Plan → Implement の間 | `codex-risk-reviewer` | high | 潜在リスク・障害モードの事前検出 |
| コード完成後（~30行以上） | `codex-reviewer` | xhigh | コードの正確性・セキュリティレビュー |
| セキュリティ調査 | `codex exec -p security` | xhigh | 脆弱性の深掘り分析・攻撃ベクトル評価 |
| エラー発生時 | `codex-debugger` | high | 根本原因の深い分析 |

## 編集指示のベストプラクティス

Codex (GPT系) は `apply_patch` 形式に最適化されているが、`str_replace` の正確な再現は苦手な傾向がある（"The Harness Problem" ベンチマーク: patch failure rate が高い）。委譲時は以下を意識する:

- **行番号ベースの指示を優先**: 「L42-L55 を以下に置換」のように行範囲で指定する
- **古いコンテンツの正確な再現を求めない**: 変更箇所の特定にはファイルパス + 関数名 + 行番号を使う
- **大きな変更はファイル全体の書き換えを許容**: 400行以下のファイルでは全書き換えの方が精度が高い場合がある
- **空白・インデントの厳密な一致に依存しない**: コンテキストの意味的な一致で指示する

## トークン予算による実装委譲

長時間セッションや並列セッションで Claude のトークン消費が大きい場合、重い実装タスクを Codex に委譲してトークンを分散する。

| 状況 | アクション |
|------|----------|
| セッション後半で大きな実装が残っている | `codex exec` で実装を委譲し、Claude はレビュー・統合に集中 |
| 並列セッションが 3+ 同時稼働中 | 新規の実装タスクは Codex に委譲を優先 |
| Plan は完成、実装が機械的 | Plan を `codex exec -p` に渡して実装を委譲 |

### 委譲方法

```bash
# Plan ファイルを渡して実装を委譲
codex exec --skip-git-repo-check -m gpt-5.4 \
  "Read tmp/plans/{plan}.md and implement all tasks. Follow the acceptance criteria exactly."
```

Claude はプラン策定・レビュー・統合の上流/下流を担当し、Codex は中間の実装を担当する分業モデル。

## タスク性質別の委譲ガイダンス

> context-and-impact のタスク分類器の知見を応用。タスクの性質に応じて最適なモデルにルーティングする。

| タスク性質 | 推奨先 | 理由 |
|-----------|--------|------|
| fix / debug / root-cause | Codex | 深い推論が必要。reasoning effort: high〜xhigh |
| feat / refactor / large-scope | Gemini | 広いコンテキストが必要。1M ウィンドウ活用 |
| review / security | Codex + Claude | 多角的検証。異種シグナルの組み合わせ |
| docs / config / small-edit | Claude 直接 | 委譲のオーバーヘッドが利益を上回る |

**既存ルーティングとの関係**: `agent-router.py` のキーワードベースルーティングと競合しない。agent-router は特定エージェントへの振り分け、このガイダンスはモデル選択の指針。両方を組み合わせて使う。

## 委譲しないケース

- 単純なコード編集、git操作、ファイル作成
- 大規模コードベース分析（→ Gemini）
- 外部リサーチ、ドキュメント検索（→ Gemini）
- マルチモーダル処理（→ Gemini）

## 性格傾向バイアス

Codex (GPT系) は指示に忠実で、失敗データに対しても比較的ニュートラル。ただし「精度を上げろ」等の曖昧な指示には教科書的な定番施策のみ提案する傾向がある。**具体的な仮説や方向性を含む指示**を与えることで提案の質が上がる。

## Expertise Map

ドメイン別の expertise score は `references/model-expertise-map.md` を参照。`/debate` の重み付けに使用。

## 言語プロトコル

Codex への指示は英語。結果はユーザーの言語（日本語）で報告。
