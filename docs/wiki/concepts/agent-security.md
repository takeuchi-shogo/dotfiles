---
title: エージェントセキュリティ
topics: [security]
sources: [2026-03-25-3-layer-prompt-injection-defense-analysis.md, 2026-03-23-verigrey-greybox-agent-validation-analysis.md, 2026-04-02-ai-agent-traps-analysis.md, 2026-03-18-scientist-ai-bengio-analysis.md, 2026-04-04-agentwatcher-rule-based-injection-monitor-analysis.md]
updated: 2026-04-04
---

# エージェントセキュリティ

## 概要

エージェントセキュリティは、自律型 AI エージェントが外部コンテンツ（Web・MCP・外部リポジトリ）を取り込む際に生じる攻撃面（Agent Traps）への対策体系である。LLM に「気をつけて」と指示するのではなく、LLM の外側にある実行境界（Hooks）で攻撃を止める設計思想が基本となる。エージェントの機能アーキテクチャに応じた 6 カテゴリ・22 攻撃ベクトルの体系的分類が、防御設計の出発点となる。

## 主要な知見

- **3 層 Hook 防御**: UserPromptSubmit（入力検査）→ PreToolUse（実行前ブロック、主軸）→ PostToolUse（出力監視）の 3 層構造で多層防御を実現する
- **Agent Traps の 6 カテゴリ**: Content Injection（知覚）/ Semantic Manipulation（推論）/ Cognitive State（記憶）/ Behavioural Control（行動）/ Systemic（マルチエージェント）/ Human-in-the-Loop（人間監視者）の 6 層が攻撃面となる
- **コンテキストブリッジング攻撃**: 悪意あるタスクをユーザーの本来タスクに自然言語で文脈接続する攻撃が、技術的パターン検出だけでは検知できない。VeriGrey でブラックボックス比較対比 +33pp の検出率向上を実証
- **Latent Memory Poisoning**: 内部メモリへの 0.1% 未満の汚染でも 80% 超の攻撃成功率。長期メモリシステムは特に慎重な設計が必要
- **Data Exfiltration Traps**: confused deputy 攻撃による機密漏洩成功率 80% 超。機密ファイルアクセスは hook レベルで検出・ブロックする
- **Dual-mode 検査**: raw テキスト + sanitized テキスト（クォート/heredoc 除去）の両方で OR 判定することで、難読化回避を防ぐ
- **fail-closed 設計**: フック異常時もブロックを維持する。フックがサイレント失敗してもエージェントが続行しない設計が必須
- **3 段階デプロイ**: audit（ログのみ）→ warn（警告）→ block（ブロック）の段階的投入で運用リスクを最小化する
- **Task-scoped Tool Filter**: タスク文脈に応じた動的ホワイトリストが最も ITSR（侵入タスク成功率）を下げつつ UTSR（通常タスク成功率）への影響が最小の防御策
- **Specification gaming 検出**: エージェントがメトリクスをハックする問題（Goodhart's Law 増幅）は、Gaming Detector と多目的バリデーションゲートで対処する
- **ルールベース検出 (AgentWatcher)**: 10 種攻撃ルール（R1-R10: 命令ハイジャック〜システムスプーフィング）+ 4 種ベナインルール（B1-B4: 偽陽性抑制）の体系的分類により、検出の説明可能性と保守性が向上する。ルール分類: `references/injection-rule-taxonomy.md`
- **Context Attribution の原則**: 検出対象を因果的に重要なコンテキスト断片に絞ることで、長文でも精度を維持できる。API 環境では「直近コンテキスト優先」「ツール出力境界重点チェック」「長文時の分割スキャン」で代替する
- **ベナインルールの重要性**: 「何が攻撃か」だけでなく「何が正常か」を明示的に定義することで、ツール使用エージェント環境での偽陽性を抑制する

## 実践的な適用

dotfiles では `prompt-injection-detector.py`（PreToolUse）が技術的パターン検出を担い、`mcp-audit.py` が MCP サーバーの入力監査を行う。`/security-review` スキルと `security-reviewer` エージェントが OWASP Top 10 準拠の検査を実行する。`settings.json` の deny rules で危険コマンド（curl|bash・rm -rf 等）を常時ブロックし、`/careful` スキルがオプトインで追加保護を提供する。`security-scan` スキルが AgentShield 経由でエージェント固有の脆弱性を検出する。

## 関連概念

- [adversarial-evaluation](adversarial-evaluation.md) — VeriGrey 等のグレーボックスファジングによる脆弱性発見手法
- [harness-engineering](harness-engineering.md) — セキュリティ防御を実装するハーネス設計の基盤
- [quality-gates](quality-gates.md) — セキュリティチェックを品質ゲートに統合するパターン

## ソース

- [3 層プロンプトインジェクション対策](../../research/2026-03-25-3-layer-prompt-injection-defense-analysis.md) — Hook ベースの 3 層防御・Dual-mode 検査・fail-closed・3 段階デプロイの実装ガイド
- [VeriGrey: Greybox Agent Validation](../../research/2026-03-23-verigrey-greybox-agent-validation-analysis.md) — ツール呼び出しシーケンスをカバレッジ指標としたグレーボックスファジングによる間接インジェクション脆弱性発見
- [AI Agent Traps](../../research/2026-04-02-ai-agent-traps-analysis.md) — Web 環境の攻撃面を 6 カテゴリ・22 ベクトルで体系化した DeepMind 論文
- [Scientist AI](../../research/2026-03-18-scientist-ai-bengio-analysis.md) — 知能と行為主体性の分離・Specification gaming 検出・Agency 3 本柱モデルのセキュリティ原則
- [AgentWatcher](../../research/2026-04-04-agentwatcher-rule-based-injection-monitor-analysis.md) — Context Attribution + 10 種ルール分類によるスケーラブルで説明可能なインジェクション検出
