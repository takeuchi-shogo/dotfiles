---
source: https://zenn.dev/seeda_yuto/articles/otel-ai-agent-observability
date: 2026-03-22
status: analyzed
---

# OTel AI Agent Observability 分析レポート

## Source Summary

**記事**: 「Claude Code の動きを OpenTelemetry で可視化したら『何してたか分からない』が消えた」(yuto[SEEDA], 2026-03-21)

### 主張

AI エージェントの可観測性が失われている問題を、Web サービスの分散トレーシングと同じ発想で OTel を使えば解決できる。

### 手法

1. **JSONL → OTel Spans 変換**: Claude Code の `~/.claude/projects/` セッションログを 150 行の Python スクリプトで変換
2. **3 階層 Span 設計**: session > turn > tool_call（Web サービスの request > middleware > external API に対応）
3. **ツールカテゴリ分類**: file_read, file_write, shell, web, agent, system
4. **セキュリティ**: 「サイズだけ記録して中身は捨てる」 - input_size/output_size のみ、会話テキスト・ファイルパス・コマンド内容は記録しない
5. **可視化基盤**: Docker (Jaeger) + pip install (opentelemetry-api/sdk/exporter)

### 根拠（実データ: 1 日分・148 ターン・130 ツール呼び出し）

| 発見 | 値 |
|------|-----|
| Bash がツール呼び出しの 69% | 90/130 回 |
| サブエージェント待ちが最大ボトルネック | TaskOutput 平均 79 秒、合計 29 分 |
| エラー率 12.3% | 16/130 回 |
| キャッシュ効率 99.6% | 909 万 vs 3.9 万トークン |

### 前提条件

- Claude Code が JSONL セッションログを自動保存していること
- `tool_result` は `user` イベントの content 配列内に含まれる（Anthropic API 仕様）

## Background Research: OTel GenAI Semantic Conventions (2026-03)

### ステータス

- **バージョン**: v1.40.0 / **安定性**: 全て Experimental
- Agent スパン (`create_agent` / `invoke_agent`) と MCP 規約が定義済み
- 主要属性: `gen_ai.usage.input_tokens`, `gen_ai.agent.name`, `gen_ai.tool.name` 等
- Stable 化の具体日程は未定だが、業界で事実上の標準として採用加速中

### 計装ライブラリ

| ライブラリ | アプローチ | 初期化 |
|-----------|-----------|--------|
| OpenLLMetry (Traceloop) | OTel 拡張 | 1 行 |
| OpenInference (Arize/Phoenix) | 属性規約+プラグイン | 複数ステップ |
| OpenLIT | フルプラットフォーム | 1 行 |

### プロダクション採用

- OTel 採用率: 6% → 11%（前年比倍増）
- LLM Observability 完成: わずか 8%（36% 進行中、41% 計画段階）
- ベンダー OTel 準拠の重要性: 89% が「重要」以上

## Gap Analysis

| # | 手法 | 判定 | 既存実装 | 差分 |
|---|------|------|---------|------|
| 1 | セッションログ定量分析 | Partial | `session_events.py` でイベント蓄積 | ツール別層別集計（回数・duration・error_rate）なし |
| 2 | 3 階層 Span 設計 | Gap | — | session > turn > tool_call の親子関係が未構造化 |
| 3 | ツールカテゴリ分類 | Gap | — | file_read/shell/web/agent 等のカテゴリ分けなし |
| 4 | トークン使用量追跡 | Gap | — | input/output/cache_read tokens の記録なし |
| 5 | サブエージェント待ち時間 | Partial | `subagent-monitor.py` (complete のみ) | start イベントなく duration 計算不可 |
| 6 | エラーパターン検出 | Partial | FM-001~015 regex マッチング | 集計 dashboard（時系列・カテゴリ分布）なし |
| 7 | OTel エクスポート | Gap | — | Jaeger/Grafana 送信なし。ローカル JSONL のみ |
| 8 | セキュリティ (redaction) | Partial | メッセージ 80 文字 truncate | API key/password の明示的フィルタリングなし |

## Integration Decisions

全項目を取り込み対象として選択。3 フェーズに分割:

- **Phase A (基盤)**: Span 階層化 + ツールカテゴリ → セッション分析の定量的基盤
- **Phase B (データ拡充)**: トークン追跡 + サブエージェント改善 + エラー集計 + session_events 統合
- **Phase C (外部連携)**: OTel エクスポート + Redaction + Docker Compose

## Plan

### アーキテクチャ

後処理型（セッション完了後に JSONL を変換）。既存 hook への侵襲を最小化。

```
~/.claude/projects/*/sessions/*.jsonl
        | converter.py (後処理)
  Span 構造化データ (JSON)
        |
   +----+----+
stats.py   exporter.py
(CLI 統計)  (Jaeger/OTLP)
```

### タスク一覧

| Phase | ID | タスク | 成果物 | 規模 | 依存 |
|-------|-----|--------|--------|------|------|
| A | A-1 | JSONL → Span 変換スクリプト | `tools/otel-session-analyzer/converter.py` | M | — |
| A | A-2 | ツールカテゴリ定義 | `tools/otel-session-analyzer/tool_categories.py` | S | — |
| A | A-3 | セッション統計集計コマンド | `tools/otel-session-analyzer/stats.py` | S | A-1 |
| B | B-1 | トークン使用量パーサー | converter.py 拡張 | S | A-1 |
| B | B-2 | サブエージェント duration | converter.py 拡張 | S | A-1 |
| B | B-3 | エラー集計 dashboard | stats.py 拡張 | S | A-1 |
| B | B-4 | session_events.py 統合 | 既存 hook にカテゴリ・Span ID 追加 | M | A-2 |
| C | C-1 | OTel/Jaeger エクスポーター | `tools/otel-session-analyzer/exporter.py` | S | A-1 |
| C | C-2 | Sensitive data redaction | `tools/otel-session-analyzer/redactor.py` | S | — |
| C | C-3 | Docker Compose (Jaeger) | `tools/otel-session-analyzer/docker-compose.yml` | S | — |

### 規模: M（新規ツールとして隔離、既存コードへの影響は B-4 のみ）
