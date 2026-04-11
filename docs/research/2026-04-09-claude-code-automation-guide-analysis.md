---
source: "テキスト貼り付け（URL なし）"
title: "You can automate anything — 7 easy prompts to automate your life"
author: 不明
date: 2026-04-09
status: integrated
session: /absorb
---

# Claude Code 日常自動化ガイド — 分析レポート

## メタデータ

- **ソース**: テキスト貼り付け（URL なし）
- **タイトル**: "You can automate anything — 7 easy prompts to automate your life"
- **著者**: 不明
- **分析日**: 2026-04-09
- **統合セッション**: /absorb

## 記事の概要

Claude Code を使った日常タスクの自動化ガイド。主な内容:
- Discovery Interview（7ラウンド）でユーザーの繰り返しタスクを掘り下げ
- 頻度×時間×苦痛度でタスク優先順位を算出
- Context-Specific（ユーザーの実パス・アプリ名）なプロンプトを生成
- Discovery → Analysis → Output の3段階で自動化コマンドを渡す
- 7つの例: Download整理、Telegram転送、プロジェクト監査、CSV処理、朝ブリーフィング、Markdown→Twitter変換、自動コミット
- CLAUDE.md, cron, pipeline.sh のボーナスTips
- 前提: 技術初心者〜中級者向け

## 構造化抽出

### 主張
Claude Code（無料・ローカル実行）を活用することで、コーディング知識がなくても日常業務の繰り返しタスクを自動化できる。キーは「正確なプロンプト設計」と「Discovery Interview」による個人固有のワークフロー把握にある。

### 手法
1. Discovery Interview（7ラウンド） — Daily work, File tasks, Communication, Content, Data, Code, Time audit
2. Task Ranking by Impact — 頻度×時間×苦痛度
3. Context-Specific Prompt Formula — ユーザーの実パス・アプリを埋め込み
4. Staged Delivery（3フェーズ） — Discovery → Analysis → Output
5. Task Categorization — Files/Messaging/Content/Data/Code/Scheduling の6分類
6. Feasibility Assessment — 全自動/部分/不可の3段階評価
7. Prompt Chaining & Cron Integration — pipeline.sh + cron/launchd

### 根拠
- 7つの具体例による実証
- 心理的根拠: 退屈な繰り返しタスクの顕在化プロセス
- Claude Code の3つの能力: ローカル実行・自動エラー修正・終了まで自動継続

### 前提条件
- 技術初心者〜中級者
- Bash/Python で制御可能なタスク
- GUI-only 操作は自動化困難

## ギャップ分析（修正済み）

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Discovery Interview (自動化対象発見) | N/A | /improve + friction loop が開発ワークフロー自動化を担う。記事は非技術者の生活自動化が対象 |
| 2 | Task Ranking (頻度×時間×苦痛) | N/A | friction-events.jsonl + eval hill-climbing が同等機能を別形式で提供 |
| 3 | Context-Specific Prompt (パーソナライズ) | Partial | autonomous が動的生成するが、文脈不一致で価値は限定的 |
| 4 | Staged Delivery (自動化マップ出力) | Partial | autonomous は Analyze→Plan→Execute。エンジニア向けには /autonomous が上位 |
| 5 | Task Categorization (6カテゴリ) | N/A | Blueprint タイプ分類が文脈に適合 |
| 6 | Feasibility Assessment (全自動/部分/不可) | Partial | /spike に3段階ラベルを追加（T1で実装済み） |

### Already 項目

| # | 既存の仕組み | 判定 |
|---|-------------|------|
| 7 | Prompt Chaining / cron | Already (強化可能) — 設計は上位互換だが定期実行タスクのレパートリー拡充余地あり |
| 8 | claude -p / --allowedTools | Already (強化不要) — 4レベルスコーピングで自動管理済み |

## セカンドオピニオン

### Codex 批評
- #2 は N/A が妥当（friction loop が同等機能）
- #1 も N/A 寄り（/improve + friction loop）
- #7 は設計は上位互換だが運用の充実度は別問題
- 優先度: #6 Feasibility Assessment のみ取り込み価値あり

### Gemini 周辺知識
- ヘッドレス自動化の隠れた制約: 権限不足、レート制限、デバッグ困難
- 最新代替手法: Pally, DevPod, LangGraph, Vercel AI SDK
- 当セットアップは既にモダンなラッパーを実装済み

## 統合タスク

| # | タスク | 対象 | ステータス |
|---|--------|------|-----------|
| T1 | /spike に Feasibility ラベル追加 | skills/spike/SKILL.md | ✅ 完了 |
| T2 | 定期実行タスクのレパートリー拡充 | scripts/runtime/ + crontab | ✅ 完了 |

## 総合評価

記事は「非技術者の日常タスク自動化」に特化しており、当セットアップ（エンジニアリングハーネス）との文脈乖離が大きい。claude -p ヘッドレスモード、cron 統合、パイプライン連鎖は既に上位互換の仕組みが存在。取り込み価値があったのは Feasibility Assessment の3段階ラベル（/spike 強化）と定期実行タスクのレパートリー拡充のみ。
