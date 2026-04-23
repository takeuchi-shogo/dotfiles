---
status: active
last_reviewed: 2026-04-23
---

# 30 Claude Prompts, Workflows & Automations — 分析レポート

> Source: "30 Claude Prompts, Workflows & Automations I Use Every Single Day" (@eng_khairallah1)
> Date: 2026-04-09
> Type: Prompt collection / Workflow guide

## 記事の概要

著者は2025年からClaudeを毎日使用し、実務で機能する30のプロンプト/ワークフローに絞り込んだ実践集。9カテゴリ: Daily Operations (01-03), Content Creation (04-07), Research (08-10), Coding (11-14), Business (15-18), Learning (19-20), System Prompts (21-22), Editing (23-25), Weekly Planning (26-27), Meta-Prompts (28-30)。

核心的主張:
- 構造化テンプレートによる認知負荷削減
- Self-Correction Loop（4次元自己評価）で出力品質を85-90%改善
- Voice Matcher で一度作った voice guide を全ワークフローに注入
- Reverse Brainstorm（失敗パターン→反転）が通常のブレストより質が高い
- DELIBERATELY SKIPPING セクションが週次計画の最重要部分
- 1記事→8+コンテンツのリパーパスが最もROI高い

## ギャップ分析

### Gap / Partial / N/A

| # | 記事の手法 | 判定 | 現状 |
|---|-----------|------|------|
| 02 | メールトリアージ | N/A | Claude Code スコープ外 |
| 08 | 競合/トレンド分析 | N/A | /research + /debate で代替可能 |
| 14 | 価格設計 | N/A | 開発支援ツールの文脈では不要 |
| 16 | 提案書作成 | N/A | 記事はビジネス提案書。/spec とはドメインが異なる |
| 15b | ミーティング準備 | N/A | 開発者の会議準備は汎用テンプレートと合わない |
| 30 | 80/20分析 | Gap | パレート法則による活動選別なし |
| 03 | 意思決定ジャーナル | Partial | フォーマットあるがスキル未独立 |
| 05 | スレッド/記事作成 | Partial | /obsidian-content 内。voice guide 注入が体系的でない |
| 06-07 | リパーパス | Partial | /digest は取り込み方向のみ |
| 17 | 概念説明 | Partial | /output-mode learning あるが段階的構造なし |
| 18 | スキルギャップ分析 | Partial | /profile-drip は漸進的だがギャップ優先度分析なし |
| 23 | ボイスマッチング | Partial | プリセット切替のみ |

### Already (強化不要) — 10項目

| 既存の仕組み | 記事の手法 |
|-------------|-----------|
| /morning | #01 Morning Briefing |
| /research | #08 Deep Research |
| backend-architect + agents | #11 Architecture, #12 API |
| /review + Codex Review Gate | #12 Code Reviewer |
| debugger + codex-debugger | #13 Bug Debugger |
| /debate | #15 Business 3-View |
| /skill-creator | #19 System Prompt Builder |
| settings.json hooks | #22 Workflow Automator |
| /simplify | #23 Strict Editor (コード) |
| /skill-creator + /prompt-review | #28 Prompt Improver |
| /think + /challenge | #29 Reverse Brainstorm |

### Already (強化可能) — 3項目

| # | 既存の仕組み | 強化案 |
|---|-------------|--------|
| 01 | /morning | テンプレートに「ブロック中」+ Obsidian保存 |
| 24 | /verification-before-completion | コンテンツ生成に Self-Correction 追加 |
| 26-27 | /weekly-review + /timekeeper | DELIBERATELY SKIPPING セクション追加 |

## セカンドオピニオン

### Codex 批評
- 暗黙 Already の6項目を Partial に格上げすべきと指摘（#04, #19, #21, #25, #28, #29）
- #12 API, #15 ビジネス3視点, #26 逆ブレストは Already に格下げ
- 優先度 Top 3: 意思決定ジャーナル → プロンプトライブラリ → 80/20分析
- 最大の問題: 暗黙 Already の検証不足

### Gemini 周辺知識
- Self-Correction Loop: Reflexion (Shinn et al., 2023) で学術的に実証。AlfWorld で75%→97%
- Voice Guide: Context Rot リスクあり。200語上限推奨
- Reverse Brainstorm: GAP (Generative Adversarial Prompting) が新手法として台頭
- Prompt Library vs Agentic: 補完関係。決定論的コア + エージェント周辺層が最適
- DELIBERATELY SKIPPING: ゼイガルニク効果 + Via Negativa で科学的根拠が最も強い

## 統合プラン

Plan: `docs/plans/2026-04-09-30-prompts-integration.md`

### Wave 1 (S規模 x 7)
1. `/decision` スキル作成
2. `/weekly-review` テンプレート強化 (DELIBERATELY SKIPPING + 80/20)
3. `/morning` テンプレート強化 (Blocked/Waiting On)
4. `/output-mode learning` 段階的構造追加
5. `/profile-drip` スキルギャップ分析追加
6. `/obsidian-content` Self-Correction ステップ追加
7. `/obsidian-content` voice guide 自動生成追加

### Wave 2 (M規模 x 2, Wave 1 依存)
8. `/obsidian-content` リパーパス機能追加
9. スレッド/記事作成の体系化

## メタデータ

- 分析手法: /absorb (Extract→Analyze→Refine→Triage→Plan)
- 入力: 記事テキスト（ユーザー貼り付け）
- Refine: Codex 批評 + Gemini Google Search grounding
- 判定: exists 10, partial 6, gap 1, n/a 5, already-enhance 3
- 選択: 全項目取り込み (9タスク)
