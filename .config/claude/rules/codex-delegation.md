# Codex CLI 委譲ルール

Codex CLI は設計判断、深い推論、複雑なデバッグを担当する。以下の場面で Codex への委譲を検討せよ。

## 委譲すべきケース

- **実装前リスク分析**: Plan 策定後、実装前に潜在リスクを洗い出す → `codex-risk-reviewer` エージェント。Claude の「注意の幅」（プロダクト直感）を Codex の「注意の深さ」（リスク検出）で補完する
- **セキュリティ深掘り調査**: 潜在的脆弱性の根本原因分析、攻撃ベクトル評価、セキュリティアーキテクチャレビュー → `codex exec -p security`（xhigh reasoning + read-only）。`security-reviewer` エージェントの表面チェックを Codex の深い推論で補完する
- **設計判断**: アーキテクチャ選定、モジュール構造、API設計、技術選定
- **トレードオフ分析**: 「AとBどちらが良いか」という比較・評価
- **複雑なデバッグ**: 通常の debugger エージェントで原因特定が困難な場合 → `codex-debugger` エージェント
- **コードレビュー（深い分析）**: ~100行以上の変更で `codex-reviewer` エージェントを並列起動
- **リファクタリング計画**: 大規模な構造変更の計画策定

## 委譲方法

- **リスク分析**: `codex-risk-reviewer` エージェント（read-only、Plan → Implement の間で起動）
- **セキュリティ分析**: `codex exec --skip-git-repo-check -m gpt-5.4 -p security "..."` — profiles.security で xhigh + read-only が自動適用
- **分析・レビュー**: `codex-debugger` エージェント（read-only）
- **コードレビュー**: `codex-reviewer` エージェント（read-only、他レビューアーと並列起動）
- **スキル実行**: `codex` スキル or `codex-review` スキル（手動実行用）
- **直接呼び出し**: `codex exec --skip-git-repo-check -m gpt-5.4 --sandbox read-only "..." 2>/dev/null`
- **レビュー/セキュリティは必ず xhigh**: `--config model_reasoning_effort="xhigh"` を指定する

## Codex 3エージェントの使い分け

| タイミング | エージェント | reasoning_effort | 目的 |
|---|---|---|---|
| Plan → Implement の間 | `codex-risk-reviewer` | high | 潜在リスク・障害モードの事前検出 |
| コード完成後 | `codex-reviewer` | xhigh | コードの正確性・セキュリティレビュー |
| セキュリティ調査 | `codex exec -p security` | xhigh | 脆弱性の深掘り分析・攻撃ベクトル評価 |
| エラー発生時 | `codex-debugger` | high | 根本原因の深い分析 |

## 委譲しないケース

- 単純なコード編集、git操作、ファイル作成
- 大規模コードベース分析（→ Gemini）
- 外部リサーチ、ドキュメント検索（→ Gemini）
- マルチモーダル処理（→ Gemini）

## 言語プロトコル

Codex への指示は英語。結果はユーザーの言語（日本語）で報告。
