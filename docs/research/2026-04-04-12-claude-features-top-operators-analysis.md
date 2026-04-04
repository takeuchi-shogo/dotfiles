---
source: "12 Claude Features the Top 1% of Operators Use Every Day"
date: 2026-04-04
status: analyzed
focus: "Feature 10 (Parallel Agents / Model Council), 11 (Ollama), 12 (VPS)"
---

## Source Summary

エンタープライズ向け AI 自動化基盤を構築してきた著者が、大半のユーザーが見逃している Claude/Claude Code の 12 機能を紹介。
「Claude をチャットボックスから解放し、インフラとして運用せよ」が主張。

### 12 機能一覧

| # | 機能 | 要点 |
|---|------|------|
| 1 | Projects | 永続的環境。指示・メモリ・ファイルが会話を跨いで継承 |
| 2 | Skills | 繰り返し使える構造化指示セット |
| 3 | CLAUDE.MD | AI 向けオンボーディングドキュメント |
| 4 | Claude Code | ターミナルベースエージェント。機能単位で丸投げ |
| 5 | Subagents | 専門エージェント。コンテキスト保持+コストルーティング |
| 6 | Remote Control / Dispatch | セッションをスマホ/ブラウザから監視・操作 |
| 7 | MCPs | 外部ツールへの実際の読み書きアクセス |
| 8 | Plugins | スキル・エージェント・Hook・MCP のバンドル |
| 9 | Channels | Slack/Telegram/iMessage/Discord 経由で Claude Code とやりとり |
| 10 | Parallel Agents / Model Council | 並列実行＋モデル別役割分担 |
| 11 | Local Models (Ollama) | ローカルモデルでコスト・プライバシー最適化 |
| 12 | VPS 運用 | ローカル/リモート/VPS の使い分け |

### フォーカス分析: Feature 10, 11, 12

**Feature 10: Parallel Agents and Model Council**
- 主張: 逐次 AI はボトルネック。並列実行＋モデル別役割分担で桁違いの速度
- 手法:
  - 独立サブタスクに対して複数 Claude インスタンスを同時実行
  - Subagents = 単一セッション内、Agent Teams = セッション跨ぎ
  - Model Council: 安いモデル(Groq $0.001/call)でフィルタ → 高いモデル(Claude $0.05/call)で判断
- 事例: リード 200 社エンリッチメント — 逐次 1 時間 → 並列で数分

**Feature 11: Local Coding Models (Ollama)**
- 主張: Claude API に縛られない。コスト・プライバシーの最適化
- 手法: Ollama 経由で Qwen2.5-Coder/DeepSeek-Coder 接続。API コールなし、レート制限なし
- 使い分け: 複雑推論 = Claude、反復作業 = ローカルモデル

**Feature 12: VPS 運用**
- 主張: 実行場所で運用モデルが変わる
- 使い分け: ローカル = 短タスク、Remote Desktop = 長時間、VPS = 夜間バッチ自動化
- 事例: Hetzner で夜間パイプライン自動実行

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 10a | 並列エージェント実行 | Already | Agent(BG), worktree 隔離, /dispatch, /autonomous で実装済み |
| 10b | Model Council（段階フィルタリング） | Already (強化可能) | モデル別ルーティング表はあるが「段階フィルタリング」パターンの明文化なし |
| 10c | Agent Teams（セッション跨ぎ協調） | Already | cmux Worker + /autonomous + setup-background-agents |
| 11 | Ollama ローカルモデル | N/A | dotfiles はハーネス設計が主目的。コスト分散は Codex/Gemini で済み |
| 12a | VPS デプロイ Playbook | Partial | unattended-pipeline.md とテンプレートは存在するが実 Playbook なし |
| 12b | Remote Desktop 活用 | N/A | 標準機能。設定不要 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す視点 | 強化案 |
|---|-------------|---------------|--------|
| 10a | /dispatch, Agent(BG), worktree | バッチ処理パターンの強調 | 強化不要 — 同等以上のカバレッジ |
| 10b | モデル別ルーティング表 | 「安いモデルでフィルタ→高いモデルで判断」の段階パイプライン | subagent-delegation-guide.md に段階フィルタリングパターン追記可能 |
| 10c | cmux Worker + autonomous | セッション跨ぎ出力合成 | 強化不要 — cmux Worker + dispatch_logger.sh で同等 |

## Integration Decisions

- **10b (段階フィルタリング)**: スキップ。現状の需要に対して過剰
- **12a (VPS Playbook)**: スキップ。実際に VPS 運用を始める段階で検討
- **10 全般に関するフィードバック取り込み**: ユーザーは dispatch/cmux Worker を実際に使ったことがなく、サブエージェントで全て済ませていた。「ブラッシュアップ時に Codex/Gemini と対話ラリーしてほしい」というフィードバックを `feedback_codex_casual_use.md` に統合。終了条件（改善なし/合意収束/最大5ラウンド）も明文化

## Plan

記事からの直接的な実装タスクなし。行動変更（Worker 活用）をフィードバックメモリとして記録済み。
