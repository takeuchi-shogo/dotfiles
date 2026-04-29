---
source: "Claude Code Skills が \"勝手に動く\" 6つの設計法則 (zodchiii氏 X.com / 東大Claude Code研究所紹介, 2026-04)"
date: 2026-04-29
status: integrated
---

## Source Summary

**主張**: zodchiii氏が 100個 Skills をリバースエンジニアリングして抽出した「動く Skills」と「動かない Skills」を分ける 6つの設計法則。

**6法則**:
1. description に「いつ使うか」+ トリガーキーワード3つ以上 (50文字未満は呼出頻度3-5倍低)、最初の250文字にユースケース
2. 命令形・番号付きステップ・発注書スタイル (Anthropic公式 Skills も同パターン)
3. 出力フォーマット指定で再利用可能になる
4. 実行前に既存ファイルを読ませる ("まず読め")
5. Out of Scope 明記 (高品質Skillsの70%に存在、低品質には ほぼなし)
6. SKILL.md 500行以内 (公式300行、入り口50行が実運用最適)

**根拠**: 100 Skills のリバースエンジニアリング (元ポスト: https://x.com/zodchiii/status/2048345453096313005)。

**前提条件**: Skills system を活用した個人・チーム・組織のワークフロー。Anthropic Claude Code v1.x の description scan 仕様を前提。

## Gap Analysis

### Pass 1

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Trigger 設計ガイド | Already (微修正可) | description-optimization.md:9-30 + planning-guide.md:59-108 で `[What]+[When]+[Key capabilities]` 公式 + trigger phrase 例まで完備 |
| 2 | 出力フォーマット契約 | Already | skill-creator/SKILL.md:55-74 + skill-writing-guide.md:232-260 で既存。統一規格は過剰 |
| 3 | 「先読み」の理由づけ | Already | search-first は repo + skill 両方に既に強い |
| 4 | Out of Scope 70%→100% | 棄却 | 全 skill 必須化はノイズ |
| 5 | SKILL.md 入り口50行原則 | Partial → 軽吸収 | 独立原則化はせず Progressive Disclosure 節に追記 |
| 6 | 6法則 ↔ 12原則 crosswalk | 棄却 | docs 増殖。本レポート内一時表で十分 |
| 7 | Trigger Conflict Detection | Already | skill-audit.md:287-335 に Full Trigger Conflict Scan 既存 |
| 8 | description 50文字未満 ast-grep | 棄却 | 観察的相関で根拠薄、validation-checklist の WHAT/WHEN/1024文字上限で実害なし |

## Already Strengthening Analysis

### Pass 2

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| A1 | 法則2 命令形 (skill-writing-principles 原則1, 12) | 100% 実装、強化不要 | — | 強化不要 |
| A2 | 法則6 500行目標 (skill-writing-principles § 7) | entry SKILL.md は薄く保つべき | Progressive Disclosure 節に "first screen 50行" 追記 | 強化可能 |
| A3 | 法則1 Trigger 設計 | near-miss negative example の検証チェックがない | validation-checklist に "3 near-miss negative examples" 追加 | 強化可能 |

## Phase 2.5 Refinement

**Codex 批評** (codex-rescue subagent, 2026-04-29):
- #1, #2, #3, #7 は Already。description-optimization.md, planning-guide.md, skill-audit.md で既に網羅
- #4 (Out of Scope 100%) → 棄却。過剰正規化、必要な skill のみで十分
- #6 (crosswalk 新規) → 棄却。docs 増殖、6法則は既存12原則に包含
- #8 (50文字未満 ast-grep) → 棄却。観察的相関、規範的指針として弱い
- 最優先採択: #1 微修正 (validation-checklist に near-miss negative) + #5 軽吸収 (Progressive Disclosure に first screen 50行)

**Gemini 周辺知識補完** (Google Search grounding, 2026-04-29):
- anthropics/skills 存在は確認、ただし行数や Out of Scope 標準パターンの個別ファイル検証は capacity exhaustion で未完
- zodchiii X.com 元ポストはアクセス不可 (X.com grounding ブロック)
- 「50文字未満 → 3-5倍低」「70% Out of Scope」「公式300行」「entry 50行」いずれも観察的相関、Anthropic 公式根拠は未確認
- Codex の判定 (参考留め) を裏付ける方向

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | Trigger 設計ガイド微修正 | 採用 | validation-checklist に near-miss negative 1行追加で記事の実益を既存ループに接続 |
| 5 | first screen 50行原則 | 採用 | Progressive Disclosure 節への 1行追記で吸収 |
| 4, 6, 8 | Out of Scope 100% / crosswalk / ast-grep 50文字 | 棄却 | Pruning-First 違反、観察的相関、過剰正規化 |
| 2, 3, 7 | 出力フォーマット / 先読み / Trigger Conflict | 棄却 (Already) | 既存仕組みでカバー済 |

## Plan

### Task T1: validation-checklist.md に near-miss negative example チェック追加 [完了]

- **Files**: `.config/claude/skills/skill-creator/references/validation-checklist.md`
- **Changes**: line 68 と line 69 の間に `- [ ] Trigger phrases include 3 near-miss negative examples (similar requests that should NOT trigger this skill)` を追加
- **Size**: S (1行)
- **Status**: 完了 (2026-04-29)

### Task T2: skill-writing-principles.md § 7 に first screen 50行原則を追記 [完了]

- **Files**: `.config/claude/skills/skill-creator/references/skill-writing-principles.md`
- **Changes**: § 7 (No nested references) の line 119 直下に `- SKILL.md の first screen（冒頭 50 行以内）は trigger / usage / next-read pointers に絞る — 詳細は reference に逃がす` を追加
- **Size**: S (1行)
- **Status**: 完了 (2026-04-29)

## 教訓

- 「100個リバースエンジニアリング」という脳筋手法から得られる知見は、既に skill-writing-principles 12原則 + skill-creator + skill-audit に大半内蔵されていた
- 観察的相関 (50文字未満→3-5倍、70%が Out of Scope) を規範的指針として直輸入する誘惑に、Codex 批評で抵抗できた
- Pruning-First の徹底で、8項目中6項目を Already/棄却 として整理、採択は2項目 (各1行) に絞れた
