---
source: "How I built a hyper-personalization system with AI (everydayisayear.ai)"
date: 2026-03-19
status: integrated
---

## Source Summary

**主張**: AIモデルの性能向上より「パーソナライゼーション」が10x効果をもたらす。plain textファイルで個人ナレッジベースを構築し、毎セッション読み込むことで「知っているAI」を実現できる。

**手法**:
1. USER.md — 基礎プロファイル（名前、ルーティン、仕事、趣味、コミュニケーション好み等）
2. MEMORY.md — 長期記憶（蒸留されたインサイト、意思決定パターン）
3. brain/family/ — 人物別ファイル（家族、ペット。誕生日、好み、ギフトアイデア）
4. オンボーディングインタビュー — 構造化対話で初期プロファイルを一括生成（~60%カバー）
5. Daily Drip — cronで毎朝1問。既存ファイルのギャップを見つけて質問→回答を適切なファイルに自動格納

**根拠**: 6週間のdaily dripで初回インタビュー以上の有用コンテキストが蓄積

**前提条件**: system prompt/file contextを読み込める個人AIエージェント環境

## Gap Analysis

| 手法 | 判定 | 現状 |
|------|------|------|
| USER.md（個人プロファイル） | **Gap** | auto-memoryに `type: user` カテゴリが定義済みだが実際のユーザーメモリが0件 |
| MEMORY.md（長期記憶） | **Already** | index + 詳細ファイル方式で記事より高度。31ファイル運用中 |
| brain/family/ | **N/A** | 開発ワークフロー特化。個人アシスタント用途とはスコープが異なる |
| オンボーディングインタビュー | **Partial** | `/interview` はGitHub Issue用。開発者プロファイル構築の仕組みなし |
| Daily Drip | **Gap** | `/timekeeper` は作業計画・振り返り特化。プロファイル構築メカニズムなし |

**核心**: パイプラインはあるがデータがない。`type: user` メモリが空。

## Integration Decisions

1. **[採用] ユーザープロファイル初期構築** — 対話でプロファイルを聞き取り `type: user` メモリとして保存
2. **[採用] Daily Drip 導入** — Cron で毎朝1問、プロファイルのギャップを埋める
3. **[採用] オンボーディングスキル** — 開発者特化インタビュー → user メモリ一括生成

## Plan

### Task 1: オンボーディングスキル作成
- `.config/claude/skills/developer-onboarding/` — 開発者プロファイル構築インタビュー
- `.config/claude/commands/onboarding.md` — `/onboarding` コマンド

### Task 2: Daily Drip cron 設定
- CronCreate で毎朝1問のプロファイル質問を設定

### Task 3: 初回オンボーディング実行
- `/onboarding` を実行し、`type: user` メモリを初期構築
