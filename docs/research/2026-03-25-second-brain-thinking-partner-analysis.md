---
source: "How to Build a Second Brain That Actually Thinks With You (article)"
date: 2026-03-25
status: integrated
---

## Source Summary

**主張**: 大半の「第二の脳」は情報のファイリングキャビネットに過ぎず思考を助けない。真の第二の脳には3要素が必要 — コンテキストドキュメント、思考プロトコル、永続的環境。「情報の保存 ≠ 思考の実行」。

**手法**:
1. **コンテキストドキュメント** — 4つの質問（今の問題/信念と不確実性/保留中の意思決定/30日の成果物）。週1更新
2. **思考プロトコル** — 自分の考えを先に述べる → 最強の反論を求める → 「何が見えていないか」で締める
3. **永続的環境** — セッション間コンテキスト持続 + 複数モデル使い分け
4. **セッション開始プロンプト** — CONTEXT → SESSION GOAL → MY CURRENT THINKING → WHAT I NEED FROM YOU → RULES

**根拠**: 前頭前皮質のワーキングメモリは約4チャンク限界（認知科学）。30日の継続で思考習慣が定着。

**前提条件**: 個人の知的作業者向け。意思決定・思考を重視する人。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | コンテキストドキュメント | **Partial** | ユーザープロファイル + /morning + /timekeeper は存在するが「タスク管理」寄り。「今何を考えていて何が不確実か」の思考ブリーフは未実装 |
| 2 | 思考プロトコル | **Partial** | /debate、/deep-read、brainstorming は存在するが、汎用的な「考えを述べる→反論→盲点」プロトコルは明示化されていない |
| 3 | 永続的環境 | **Already (強化可能)** | Memory + マルチモデル + session-protocol + checkpoint。ただしメモリは「プロジェクト知識」中心で「思考状態」は記録対象外 |
| 4 | セッション開始プロンプト | **Gap** | /morning はタスク提案、/timekeeper plan は計画。「思考セッション」開始スキルは存在しない |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 3 | Memory + マルチモデル | 毎回ゼロからの stranger 問題。memory は知識・フィードバック中心で「信念・不確実性・未決定事項」は対象外 | /timekeeper review に「信念の変化」「未解決の問い」セクションを追加 |

## Integration Decisions

全4項目を取り込む:
1. [Partial] 思考コンテキストドキュメント — Obsidian に構造化テンプレート
2. [Partial] 思考プロトコル — references に明示化
3. [Gap] `/think` スキル — コンテキストロード + 思考プロトコル起動
4. [強化] /timekeeper review に「信念の変化」「未解決の問い」追加

## Plan

### Task 1: 思考コンテキストテンプレート作成 (S)
- `skills/think/templates/thinking-context-template.md` — 4つの質問の構造化テンプレート
- Obsidian Vault の `06-Areas/thinking-context.md` に実体を配置する設計

### Task 2: 思考プロトコル reference 作成 (S)
- `skills/think/references/thinking-protocol.md` — 3ルールの明示化 + セッション構造

### Task 3: `/think` スキル作成 (M)
- `skills/think/SKILL.md` — 2モード: `session`（思考セッション開始）、`update`（コンテキスト更新）
- session: コンテキストドキュメント自動ロード → 思考プロトコル適用
- update: 4つの質問を対話形式で更新

### Task 4: `/timekeeper review` 強化 (S)
- SKILL.md の Review モードに Q8「信念の変化」、Q9「未解決の問い」を追加
- evening-review-template.md に対応セクション追加
