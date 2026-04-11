---
source: https://github.com/danielmiessler/Personal_AI_Infrastructure
date: 2026-03-30
status: analyzed
---

## Source Summary

### 主張
PAI (Personal AI Infrastructure) は「ハーネス（足場）がモデル選択より重要」という思想に基づき、個人の目標・信念・学習を構造化し、セッション横断で蓄積することで AI を個人に最適化するフレームワーク。Claude Code ネイティブ。

### 主要手法
1. **TELOS** — 10個のアイデンティティファイル（MISSION/GOALS/BELIEFS/MODELS/STRATEGIES/NARRATIVES/LEARNED/CHALLENGES/IDEAS/PROJECTS）で深い目標理解
2. **Statusline** — ターミナルにコンテキスト使用率・学習シグナル・タスク状態を動的表示
3. **USER/SYSTEM 分離** — アップグレード安全なディレクトリ設計
4. **BuildCLAUDE.ts** — テンプレートから CLAUDE.md を Bun で動的生成
5. **学習シグナル収集** — 毎インタラクションから rating/sentiment/outcome を記録（3層: hot/warm/cold）
6. **SessionEnd 学習** — 5種の hook（WorkCompletionLearning, SessionCleanup, RelationshipMemory, UpdateCounts, IntegrityCheck）
7. **通知ルーティング** — 時間ベース（5分超→ntfy、エラー→ntfy+Discord）
8. **セキュリティバリデータ** — 全 PreToolUse に SecurityValidator
9. **PRD Sync hook** — Write/Edit 時にスペック同期
10. **コンテキスト圧縮閾値** — 83% で自動トリガー
11. **Voice システム** — ElevenLabs TTS 統合
12. **PAI Packs** — スタンドアロンの機能パック（Research, Security, Thinking 等 12種）

### 根拠
- 1371セッション・2592ユーザー評価の実運用データ
- 16原則体系（特に Scaffolding > Model, Deterministic Infrastructure, Code Before Prompts）
- v1.0 → v4.0.3 の 6 世代の反復改善

### 前提条件
- Claude Code ネイティブ（Bun ランタイム）
- Kitty/iTerm ターミナル
- ntfy.sh / Discord / Twilio 通知基盤

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | TELOS（10アイデンティティファイル） | Partial | `user_*.md` 4ファイル + `/onboarding` + `/profile-drip` あり。構造化された目標体系はない |
| 2 | Statusline（動的ターミナルステータス） | Gap | 未実装。context 使用率・学習シグナル・タスク状態のリアルタイム表示なし |
| 3 | BuildCLAUDE.ts（CLAUDE.md 動的生成） | Gap | CLAUDE.md は手動管理 + Progressive Disclosure。テンプレートからの自動生成なし |
| 4 | 学習シグナル（rating/sentiment/outcome） | Partial | AutoEvolve がセッションデータを収集するが、インタラクション毎の構造化 rating/sentiment はない |
| 5 | Voice システム | N/A | ユーザーのワークフロー（cmux + ターミナル中心）に不適合 |
| 6 | PAI Packs | N/A | skills.sh + カスタムスキルエコシステムで同等機能をカバー |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す知見 | 強化案 | 判定 |
|---|-------------|---------------|--------|------|
| 1 | 通知 — cmux-notify.sh | 時間ベースルーティング（5分超→ntfy等） | cmux-notify に実行時間閾値追加 | 強化可能 |
| 2 | コンテキスト圧縮 — context-compaction-policy.md | 83% 閾値で自動トリガー | 不要。品質劣化検知 + Fallback 既存 | 強化不要 |
| 3 | セキュリティ — AgentShield + protect-linter-config | 全 PreToolUse に SecurityValidator | 不要。既に広範適用済み | 強化不要 |
| 4 | SessionEnd — AutoEvolve | 5種の SessionEnd hook | UpdateCounts + IntegrityCheck を追加 | 強化可能 |
| 5 | USER/SYSTEM 分離 — dotfiles symlink | USER/ SYSTEM/ 明示分離 | 不要。symlink + git で同等 | 強化不要 |
| 6 | 原則体系 — core_principles | 16原則、特に「Scaffolding > Model」 | 原則に追加 | 強化可能 |

## Integration Decisions

全 Gap/Partial（4項目）+ 全 Already 強化可能（3項目）= 7項目を取り込み。

スキップ: Voice システム（N/A）、PAI Packs（N/A）、セキュリティ強化（不要）、コンテキスト圧縮強化（不要）、USER/SYSTEM 分離（不要）

## Plan

### Wave 1: Quick Wins（S規模 × 2）
- T1: 「Scaffolding > Model」原則追加 → CLAUDE.md
- T2: 通知ルーティング強化 → cmux-notify.sh

### Wave 2: Core Features（M規模 × 3）
- T3: Statusline 実装 → scripts/runtime/statusline.sh + settings.json
- T4: SessionEnd 学習強化 → scripts/lifecycle/ + settings.json
- T5: TELOS ライト版 → memory/ に mission/goals/strategies

### Wave 3: Advanced（M-L規模 × 2）
- T6: 学習シグナル収集 → AutoEvolve session hooks 拡張
- T7: CLAUDE.md ビルダー → scripts/lifecycle/build-claude.sh

依存: T1,T2 並列 → T3,T4 並列 → T5(T1後) → T6(T4後) → T7(T5後)
