---
source: https://github.com/aiming-lab/AutoHarness
date: 2026-04-02
status: integrated
---

## Source Summary

**AutoHarness** (aiming-lab/AutoHarness) — AI エージェント向け軽量ガバナンスフレームワーク。
"Agent = Model + Harness" の思想で、ツールコール単位の6/8/14ステップガバナンスパイプラインを提供。

### 主張
モデルの推論能力だけでは安全で信頼性の高いエージェントは構築できない。
コンテキスト管理、ツールガバナンス、コスト追跡、監査可能性を担う「ハーネス」が不可欠。

### 手法
1. 3段階パイプライン (Core 6-step / Standard 8-step / Enhanced 14-step)
2. YAML Constitution (宣言的ガバナンス設定)
3. Regex Risk Classifier (<5ms, 9カテゴリ)
4. Progressive Trust (セッション内承認パターン記録 + 1h decay)
5. Turn Governor (累積リスクスコア + denial spiral 検出 + レート制限)
6. 5層コンテキスト管理 (Budget → Truncation → Microcompact → AutoCompact + circuit breaker → File Restoration)
7. JSONL Audit Trail
8. Per-tool Cost Attribution
9. Multi-agent Profiles (ロールベース制限)
10. Claude Code Integration (`autoharness install --target claude-code`)

### 根拠
- 958テスト通過
- Claude Code, Codex の設計パターンをインスパイア元として明示
- Enhanced モードがデフォルト（最大ガバナンスをデフォルトとする安全志向）

### 前提条件
- Python ライブラリとして LLM クライアントをラップする設計
- OpenAI SDK との統合が主ユースケース
- CC の hook アーキテクチャ（各 hook が独立プロセス）とは根本的にアーキテクチャが異なる

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 3段階パイプライン | Partial | hooks は個別スクリプト。統一パイプラインとしての段階切替なし |
| 2 | YAML Constitution | Partial | ガバナンスが CLAUDE.md + settings.json + 個別 hook に分散 |
| 3 | 統一 Risk Classifier | Partial | 個別 hook が個別にリスク検出。統一分類器なし |
| 4 | Progressive Trust | N/A | CC 本体が ask/allow/deny を管理 |
| 5 | Turn Governor 累積リスク | Gap | doom-loop 検出のみ。リスク重み付き累積なし |
| 6 | Per-tool Cost Attribution | Gap | トークン per-tool 追跡なし（CC API 非公開） |
| 7 | Anti-distillation / Frustration | N/A | 個人 dotfiles 用途では不要 |
| 8 | Tool Alias Resolution | N/A | CC がネイティブ管理 |

### Already 項目の強化分析

| # | 既存の仕組み | 強化案 | 判定 |
|---|-------------|--------|------|
| A1 | session-trace-store.py | risk_level フィールド追加 | 強化可能 → 実施 |
| A2 | agents/*.md | disallowedTools 明示化 | 強化可能 → 見送り（instruction ベースで十分） |
| A3 | compact-instructions + resource-bounds.md | circuit breaker 既載 | 強化不要 |
| A4 | doom-loop 検出 | denial カウント追加 | 強化不要（CC が拒否情報を hook に渡さない） |

## Integration Decisions

全4項目を統合:
1. **Governance Map リファレンス** → `references/governance-map.md` — 9カテゴリマッピング + Constitution 的俯瞰 + 累積リスク概念
2. **session-trace-store risk_level** → `risk_levels` + `risk_score` フィールド追加
3. 分析レポート（本ファイル）
4. MEMORY.md ポインタ追記

## 設計判断

AutoHarness は汎用 Python ライブラリとしてのガバナンスフレームワークであり、
CC の hook + instruction 型ハーネスとはアーキテクチャが根本的に異なる。

- **リアルタイム累積リスクブロック** → 見送り（hook 間の共有状態コストが高い）
- **事後分析アプローチ** → 採用（trace に risk_level を付与し /improve で分析）
- **Constitution 一元管理** → governance-map.md として参照文書化（YAML ファイルではなく）
- **Progressive Disclosure 型** を維持（AutoHarness の "全部入り Enhanced" とは対照的）
