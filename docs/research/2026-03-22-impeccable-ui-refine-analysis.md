---
source: https://github.com/pbakaus/impeccable
date: 2026-03-22
status: integrated
---

## Source Summary

Impeccable は AI コーディングアシスタント（Claude Code, Cursor, Gemini）向けのデザインスキルパッケージ。
7つのドメイン別リファレンスファイルと20のステアリングコマンドで構成。
「AI生成UIのジェネリックな見た目」を具体的な操作コマンドで改善する設計。

### 手法
- 20のデザインコマンド（distill, polish, critique, colorize, animate, bolder, quieter 等）
- 7つのリファレンスファイル（typography, color, spatial, motion, interaction, responsive, UX writing）
- Anti-patterns ガイダンス（Inter禁止、gray-on-color禁止、pure black禁止等）

### 根拠
- 12,000+ GitHub スター。作者 pbakaus は元 Google DevRel
- 具体的な操作に分解する設計が実用的

### 前提条件
- Claude Code / Cursor 等の AI コーディング環境を前提

## Gap Analysis

| 手法 | 判定 | 詳細 |
|------|------|------|
| UI作成時のAI臭排除 | Already | frontend-design の anti-patterns.md |
| デザインシステムDB | Already | ui-ux-pro-max（50+スタイル、161パレット） |
| UIコンプライアンス監査 | Already | /web-design-guidelines |
| 既存UI改善コマンド群 | **Gap** | 「作る」はあるが「磨く」がない |
| colorize | Partial | カラー検索はあるが適用コマンドなし |
| animate | Partial | ルールはあるが追加特化コマンドなし |
| L0/L1/L2コンテキスト | Already | Progressive Disclosure + session-load.js |
| 使用頻度ベース自動圧縮 | Partial | importance + TTL あり、アクセス頻度なし |

## Integration Decisions

- **採用**: 既存UI改善コマンド群 → frontend-design スキルに Refine モード追加
- **スキップ**: OpenViking コンテキスト管理 → 既存が上位互換

## Implementation

- `skills/frontend-design/SKILL.md` に Refine Mode セクション追加
- `skills/frontend-design/references/refine-operations.md` 新規作成
- Impeccable 20コマンド → 5操作（distill, polish, critique, energize, calm）に集約
