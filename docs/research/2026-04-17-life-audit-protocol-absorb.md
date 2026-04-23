---
created: 2026-04-17
source: "How to fix your life in 1 prompt (Dan Koe 風心理監査プロトコル)"
absorbed_at: 2026-04-17
type: absorb-analysis
slug: life-audit-protocol
status: active
last_reviewed: 2026-04-23
---
# How to fix your life in 1 prompt — Absorb 分析レポート

## 記事ソース

- タイトル: "How to fix your life in 1 prompt"
- 著者スタイル: Dan Koe 風コミュニティ記事（作者明記なし）
- URL: 不明（ユーザー貼り付けテキスト）
- 取得日: 2026-04-17

## 主張の要約

6フェーズ構成の全人生監査プロトコル。「1日の集中会話で数年分の明晰さを得る」という主張。

- **Phase 1**: 心理的発掘（Anti-vision + Identity/Fear mapping）
- **Phase 2**: 9ドメイン生活監査（Career, Money, Health, Mental, Relationships, Romance, Daily life, Purpose, Growth）
- **Phase 3**: 全生活診断（Root pattern + 実際の敵）
- **Phase 4**: 生活アーキテクチャ（Vision MVP + Identity declaration + 90-day mission + 3 non-negotiables + Weekly reset）
- **Phase 5**: ドメイン別実装計画（START/STOP/CHANGE × 9ドメイン + 30-day experiments）
- **Phase 6**: デイリープロトコル（Morning / Deep work / Midday interrupt / Evening / Weekly anchor）

## Phase 2 ギャップ分析結果（15手法）

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Anti-vision exercise | Gap | TELOS に stop-doing 概念なし |
| 2 | Identity declaration | Gap | /think にあるが専用ではない |
| 3 | Psychological excavation | Gap | 多段階掘削フレームワークなし |
| 4 | 9-domain life audit | Gap | /profile-drip は漸進的、9域体系監査なし |
| 5 | START/STOP/CHANGE per domain | Gap | 専用フレームワークなし |
| 6 | Environment design (friction) | Gap | 摩擦設計ドキュメントなし |
| 7 | 30-day experiment | Gap | 実験フレームワークなし |
| 8 | 3 daily non-negotiables | Partial | /timekeeper plan は単一最重要タスクのみ |
| 9 | 90-day mission + 30-day boss fight | Gap | 時間カスケード構造なし |
| 10 | Weekly reset ritual | Partial | /weekly-review は GTD 式（Horizon 5 Life 視点欠如） |
| 11 | Root pattern / Actual enemy naming | Gap | 根本パターン診断なし |
| 12 | Daily protocol (Midday interrupt) | Partial | /timekeeper に朝夜はあるが Midday なし |
| 13 | Vague answer follow-up rule | Partial | /think で部分的に実装 |
| 14 | Reflect before moving on | Partial | /timekeeper review に実装 |
| 15 | Push on comfort | Already(強化可能) | /think + /grill-interview でカバー |

**集計**: Gap 7 / Partial 4 / Already強化可能 3 / N/A 1（90-day mission の N/A 扱いを Phase 2.5 で修正）

## Phase 2.5 Codex 批評サマリ

**最優先取り込み推奨**:
- Anti-vision: 既存 TELOS の "Stop-doing list" に直接マップできる。最小コストで最大効果
- 3 non-negotiables: /timekeeper plan に Q0 追加だけで実装可能。侵襲性が低い

**新規 skill 化は非推奨**:
「9-domain audit を agent 化すると Insight abandonment 問題（75%の人が洞察を行動に移さない）が悪化する。プロンプト = 行動化の心理的契約であって、自動化すると契約が消える」

**TELOS 最小拡張が安全**:
- 9-domain audit 全体や Identity declaration は「過剰な心理化」を招くリスク
- 採択するなら既存フレームワークへの最小追加にとどめるべき

## Phase 2.5 Gemini 批評サマリ

**Insight abandonment 75%**:
研究によれば、self-audit で得た洞察のうち行動化されるのは約25%。残り75%は "performed clarity" として消える。記事のプロトコルはその典型的な構造を持つ。

**Performative audit trap**:
9ドメイン一括監査は「やり遂げた感」によって実際の変化を代替してしまう（Barbara Ehrenreich "Bright-sided" 批判の構造）。

**Anti-vision のコルチゾール副作用**:
恐怖による動機付けは短期的に強力だが、慢性的コルチゾール上昇で意思決定品質が低下する可能性がある。代替案: James Clear Annual Review（実績ベースの前向きアプローチ）。

**Ashcroft End-gaining 警告**:
Alexander Technique の「目標への直接突進（end-gaining）が問題を悪化させる」。Identity declaration は "I am the type of person who..." の繰り返しがギャップによる焦りを生む可能性。

## Phase 3 Triage 結果（採択4項目）

### 採択

1. **Anti-vision → Stop-doing list を telos_strategies.md に追加**
   - 理由: 既存 TELOS フレームワークへの最小追加。恐怖ではなく「明確化」として機能させる
   - 実装: telos_strategies.md に「やらないことリスト」節を追加

2. **3 daily non-negotiables → /timekeeper plan に Q0 追加**
   - 理由: 既存スキルへの1質問追加のみ。侵襲性ゼロ
   - 実装: SKILL.md の Q1 の前に Q0「今日の3つの non-negotiables は？」を追加

3. **Midday check → /timekeeper midday モード新設**
   - 理由: 午後の autopilot 防止。/timekeeper の既存構造に自然に収まる
   - 実装: SKILL.md に `midday` コマンドを追加（1質問: 「今日の non-negotiables は進んでいるか？」）

4. **Horizon 5 life 質問 → /weekly-review Phase 5.5 追加**
   - 理由: GTD 式 weekly-review に欠けていた「人生スケール」の視点を補完
   - 実装: SKILL.md の Phase 5（レビュー待ち PR）の後に Phase 5.5 を追加

## 棄却項目と理由

| 項目 | 棄却理由 |
|------|---------|
| 9-domain audit 全体 | 重すぎる、Performative audit trap（やった感で終わる）、Insight abandonment 75% |
| Identity declaration | Ashcroft End-gaining リスク、ギャップ焦りを生む |
| Psychological excavation | Ehrenreich 批判の構造（dark 探索の商業化）、心理相談化リスク |
| Root pattern naming | 専門的心理支援なしでの「敵の命名」は逆効果の可能性 |
| Push on comfort の agent 化 | Codex 警告: 自動化すると心理的契約が消える |

## 実装済み変更（ファイル別）

| ファイル | 変更内容 |
|----------|---------|
| `memory/telos_strategies.md` | 「やらないことリスト（Stop-doing list）」節を追加 |
| `.config/claude/skills/timekeeper/SKILL.md` | Q0「今日の3つの non-negotiables」を plan モードに追加、midday モード新設 |
| `.config/claude/skills/weekly-review/SKILL.md` | Phase 5.5「Horizon 5 Life 質問」を追加 |

## 運用上の注意

- **四半期見直し**: 採択した non-negotiables は四半期ごとに見直し、形骸化を防ぐ
- **深掘り禁止**: Anti-vision セッションを繰り返すことは推奨しない（コルチゾール副作用）
- **心理領域への踏み込み禁止**: Psychological excavation、Root pattern naming は Claude にやらせない
- **Obsidian との連携**: Literature Note は `05-Literature/lit-life-audit-protocol.md` に保存済み

## 再利用パターン

「外部 self-help 記事を技術 harness に取り込むときは最小採択 + 副作用警告併記」

- 全手法を採択しない（Insight abandonment 75% 問題）
- 心理的手法は技術系 agent での自動化を避ける
- 既存フレームワーク（TELOS / timekeeper）への最小追加が最も安全
- Codex + Gemini 並列批評で "performed clarity" トラップを事前検出する
