---
source: "Launching Claude Managed Agents (Anthropic Blog)"
date: 2026-04-09
status: integrated
---

## Source Summary

**主張**: Claude Managed Agents はハーネス陳腐化問題と長期タスク対応を、pre-built configurable agent harness + managed infrastructure で解決する。ハーネスの進化はインフラレベルの課題であり、特定のハーネス設計ではない。

**手法**:
- Brain/Hands/Session 分離 — ハーネス(脳)・ツール実行サンドボックス(手)・セッションログ(状態)を独立インタフェースに
- Agent = Config as Code — YAML テンプレートで model, system prompt, tools, skills, MCP servers をバージョン管理
- Environment 抽象化 — Sandbox テンプレートで runtime type, networking policy, package config を定義
- SDK × CLI ハイブリッド — CLI でセットアップ（リソース管理）、SDK（6言語）でランタイム（セッション駆動）
- 複数トリガーモデル — Event-triggered / Scheduled / Fire-and-forget / Long-horizon の4パターン

**根拠**: METR benchmark で 10 human-hours 超。3層アーキテクチャで単一障害点排除。

**前提条件**: 長期・本番・チーム環境。インフラ復旧・secrets 管理が必須。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Agent = Config as Code（統合YAML定義） | Partial | .codex/agents/*.toml + .config/claude/agents/*.md で分散定義。Managed Agents 統合形式未対応 |
| 2 | Environment 抽象化 | N/A | サンドボックス制約（外部API プロキシ必須、バイナリ制限）。ローカルのフルOSアクセスが優位 |
| 3 | SDK × CLI ハイブリッド | Partial | claude -p + codex exec で CLI 実行あり。Managed Agents SDK（6言語）未導入 |
| 4 | Hybrid Architecture（新規） | Gap | Managed Agents を計画/推論層、Custom Harness を実行/検証層として併用するパターン未導入 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | Brain/Hands/Session 分離（Scaffolding/Harness 2層 + session-load/save） | ベンダーロックイン時の可搬性欠如 | Agent 定義ポータビリティ確保 + Decision Journal 連携 | 強化可能 |
| S2 | 複数トリガーモデル（4パターン網羅: launchd/cron/hooks） | クラウド基盤の方が信頼性高い。コスト爆発リスクあり | Managed Agents API でスケジュール実行移行 + ハード予算キャップ | 強化可能 |

## Gemini 周辺知識（Phase 2.5）

### 競合比較
| 特性 | Claude Managed Agents | OpenAI Agents v3 | Devin / Factory |
|------|----------------------|-------------------|-----------------|
| 核心強み | 推論堅実性＋低幻覚 | エコシステム広さ＋速度 | コーディング特化＋垂直統合 |
| 安全性 | Constitutional AI | ガードレール | サンドボックス |
| 主用途 | 規約重視企業、R&D | 消費者向け | 自律エンジニアリング |

### 重要トレードオフ（記事未言及）
- コスト爆発: 長期タスク自律再試行で一晩数千ドル → ハード予算キャップ必須
- コールドスタート: 環境セットアップ 3-8秒 → 短時間タスク×多数並列で無視できない
- ベンダーロックイン: Agent 設定/学習履歴のポータビリティ低い
- 推論品質 ≠ 実装品質: 計画と検証の組み合わせが肝

### Gemini の推奨構成
ハイブリッド:「脳は Managed、手足は Custom」
- Managed Agent 層: 計画・推論
- Custom Harness 層: コード変更・ビルド・テスト・検証
- ローカル環境: 成果物

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | Agent Config 標準化 | 採用 | 分散定義の統合ビジョンを文書化 |
| 2 | Environment 抽象化 | スキップ | N/A — ローカル優位性を維持 |
| 3 | SDK × CLI ハイブリッド | 採用 | Managed Agents API 活用の基盤 |
| 4 | Hybrid Architecture | 採用 | 最もインパクト大。Custom Harness との併用パターン |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | ポータビリティ強化 | 採用 | ベンダーロックイン回避 |
| S2 | スケジュール実行移行 | 採用 | クラウド基盤の信頼性向上 |

## Plan

### Task 1: Hybrid Architecture リファレンス (Wave 1)
- **Files**: references/managed-agents-hybrid.md (新規)
- **Changes**: Managed Agents(計画/推論層) × Custom Harness(実行/検証層) 併用パターンを文書化
- **Size**: S

### Task 2: CLAUDE.md マルチモデルルーティング更新 (Wave 1)
- **Files**: .config/claude/CLAUDE.md
- **Changes**: ルーティングテーブルに Managed Agents 行追加
- **Size**: S

### Task 3: Agent Config 標準化リファレンス (Wave 2)
- **Files**: references/agent-config-standard.md (新規)
- **Changes**: 分散定義の統合ビジョン + Managed Agents YAML 対応表
- **Size**: S

### Task 4: Scheduled タスク移行検討 (Wave 2)
- **Files**: references/managed-agents-scheduling.md (新規)
- **Changes**: launchd/cron 移行候補評価 + コスト設計指針
- **Size**: S

### Task 5: Agent 定義ポータビリティガイド (Wave 3)
- **Files**: references/agent-portability.md (新規)
- **Changes**: エクスポート/インポート形式 + ベンダーロックイン回避策
- **Size**: S
