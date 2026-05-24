---
title: "@cyrilXBT How to Organize Your Obsidian Vault — absorb analysis (light-phase2)"
date: 2026-05-25
status: light-phase2-only
adopt_count: 2
family: obsidian-second-brain
family_entry: 15
author: "@cyrilXBT"
prior_absorb_count: 14 (obsidian-second-brain family) / 5 (cyrilXBT author within family)
verdict: Adopt (S 規模 vault-maintenance.sh 拡張 2 件)
related:
  - 2026-05-23-cyrilxbt-18-steps-absorb-analysis.md (claude-code-tips family, Reject)
  - 2026-05-23-damidefi-claude-obsidian-second-brain-absorb-analysis.md (obsidian-second-brain family 10、Reject)
  - 2026-05-22-cyril-one-folder-absorb-analysis.md (obsidian-second-brain family 11、light-phase2 adopt=1)
  - 2026-05-19-cyril-obsidian-dashboard-absorb-analysis.md (obsidian-second-brain family 12、adopt=2)
  - 2026-05-08-cyril-obsidian-vault-absorb-analysis.md (obsidian-second-brain family 8、adopt=3)
---

# @cyrilXBT 「How to Organize Your Obsidian Vault So You Can Always Find What You Need」

## Source Summary

- 著者: @cyrilXBT — obsidian-second-brain family で **5 件目**、cyril-family 全体で 12 件目以上
- 形式: 12 手法から成る full course 形式の整理ガイド（Retrieval-First Principle → 8-folder structure → naming convention → YAML properties → tag prefix system → MOC → Inbox processing → 3 search modes → Quarterly review → Filesystem MCP integration → Progressive Reorganization plan）
- 主張: vault は filing cabinet ではなく thinking system として組み立てる、retrieval 30 秒以内が達成基準
- 根拠: anecdotal only。データ・出典・事例引用なし、`@cyrilXBT` follow 誘導で締め

## Phase 1.5: Saturation Gate

- Family: `obsidian-second-brain` (キーワード hit: `obsidian`, `vault`, `PARA`, `MOC`, `second brain` 全該当)
- 過去事例 N=14: notebooklm-obsidian (2026-03-16), obsidian-agent-persistent-memory (2026-03-22), claude-obsidian-ai-employee (2026-03-23), second-brain-thinking-partner (2026-03-25), obsidian-claude-code-meta (2026-04-09), notebooklm-claude-extend-sessions (2026-04-10), claude-only-stack-cyrilxbt (2026-04-11), karpathy-second-brain-modified (2026-04-14), obsidian-claudecode-akira-papa (2026-04-21), **cyril-obsidian-vault** (2026-05-08, adopt 3), **cyril-obsidian-dashboard** (2026-05-19, adopt 2), **cyril-one-folder** (2026-05-22, adopt 1), **cyrilxbt-18-steps** (2026-05-23, adopt 0), **damidefi-claude-obsidian** (2026-05-23, adopt 0)
- 直近 4 件採用率: 1/3 直近 3 件は 1 / 0 / 0 = **8%**（SATURATED）
- 手法 delta 計算:
  - 既知手法（9 件）: Retrieval-First Principle / 8-folder PARA / YYYY-MM-DD-[TYPE]-[TOPIC] naming (2026-05-22 で明示 Reject) / YAML frontmatter universal schema / 3-category tag prefix (#status/ #type/ #topic/ 既存) / MOC at 20+ notes / 3 search modes (Obsidian native) / Filesystem MCP retrieval / Progressive Reorganization plan (meta-cookbook)
  - 新規候補（1 件）: Quarterly Vault Review 4-axis (folder/tag/archive/naming inconsistencies)
  - ambiguous（1 件）: Inbox processing 3-question rubric
  - **delta = 1**（ambiguous = 1）
- 判定: **SATURATED-borderline → light-phase2** (ユーザー判断)

## Phase 2 (light): Pass 1 + Pass 2 統合判定

novel = 1 + ambiguous = 1 の合計 2 手法のみ検証。

### T1: Quarterly Vault Review 4-axis

| Axis | 既存実装 | 判定 |
|------|---------|------|
| 1. Folder audit | IPARAG 9-folder 固定 (`templates/obsidian-vault/CLAUDE.md`) | **N/A** — 構造固定、新規 folder 増殖の問題なし |
| 2. Tag audit (rare tag pruning) | `vault-maintenance.sh` は orphan note 検出のみ、**rare tag (< 5 notes) 検出なし** | **Gap** — 「最低 5 ノート閾値」rule 未実装 |
| 3. Archive sweep (active → archive 移動) | `#status/seed` + 30 日 Stale Seed 検出はあるが、`#type/project` long-inactive → 06-Archive 自動提案なし | **Partial** — Stale Seed と別 axis、既存拡張可能 |
| 4. Naming inconsistencies | `CLAUDE.md` に naming convention 定義あり、**compliance check 機構なし** | **Gap** |

### T2: Inbox processing 3-question rubric (ambiguous)

- Q1 (type?) → frontmatter type field で対応済
- Q2 (has home?) → MOC / project 確認は既存 `obsidian-knowledge` skill カバー
- Q3 (own note or append?) → 個人判断、harness 化すると過剰
- 判定: **N/A** — Cyril 系で多用される anecdotal personal cadence pattern、`/timekeeper review` + `/note` skill で十分

## Phase 2.5 Refine

- **Codex 批評**: 省略（light flag、ユーザー判断）
- **Gemini grounding**: 省略（family saturated、追加 grounding 不要）

## adopted / rejected decisions

### Adopted (2 件 / S 規模)

| # | 採用 | 既存ファイル | 変更内容 |
|---|------|--------------|----------|
| A1 | T1 axis 2: rare tag audit | `dotfiles/.config/claude/scripts/runtime/vault-maintenance.sh` | `check_rare_tags()` 関数追加。Vault 全体から `#tag` + frontmatter tags を集計、出現 < 5 のタグを dry-run で表示 |
| A2 | T1 axis 4: naming convention check | 同上 | `check_naming_compliance()` 関数追加。CLAUDE.md 規約 (04-Galaxy/ = `YYYYMMDDHHMMSS-kebab-case`、05-Literature/ = `lit-` prefix、01-Projects/proj-* = `YYYY-MM-DD-topic`) 違反ファイルを dry-run で列挙 |

### Rejected (10 件)

| # | 手法 | 理由 |
|---|------|------|
| R1 | Retrieval-First Principle | meta-principle、既設計思想 |
| R2 | 8-folder PARA 構造 (00-INBOX/01-NOTES/...) | IPARAG 9-folder 既採用、template Design Rationale 文書化済 |
| R3 | YYYY-MM-DD-[TYPE]-[TOPIC] ファイル命名 | 2026-05-22 cyril-one-folder で明示 Reject 済 (C2: frontmatter type で代替、ファイル名 encode は移行コスト大) |
| R4 | YAML frontmatter universal schema | 2026-05-22 で Reject 済 (C3: naming convention 既定義、universal 強制は YAGNI) |
| R5 | 3-category tag prefix (status/ project/) | `#status/`, `#type/`, `#topic/` 既採用 (CLAUDE.md L46-54) |
| R6 | MOC at 20+ notes | `04-Galaxy/_templates/permanent-note.md` で MOC 概念既採用 |
| R7 | Inbox processing 3-question rubric | T2 として N/A、個人運用 cadence |
| R8 | 3 search modes (full text/property/tag) | Obsidian native 機能、harness 範囲外 |
| R9 | Filesystem MCP retrieval | 既採用 (`mcp-config.json` で obsidian MCP 設定済) |
| R10 | Progressive Reorganization Week 1-Month 3 plan | meta-cookbook、新規 vault 立ち上げ向け - dotfiles は既存 vault 運用中 |

## Folder Audit 補足 (N/A 判定根拠)

T1 axis 1 を N/A 判定したが、記事の「最低 5 ノート閾値で folder 整理」は dotfiles では別文脈で適用可能性あり:
- 個人 vault は IPARAG 固定で folder 増殖なし → N/A 確定
- ただし `docs/research/` のサブカテゴリ・`scripts/runtime/*` の用途別整理など、**コードベース側** の「フォルダ 5 ファイル閾値」rule は別審議の余地あり（今回 absorb 範囲外、別途 audit 候補）

## Meta-findings

1. **Cyril 5 件目で初の「small but real adopt」事例**: 過去 4 件 (Vault/Dashboard/One Folder/18 Steps) は adopt 3 → 2 → 1 → 0 の漸減トレンド。今回 adopt=2 はトレンド反転だが、内容は **vault-maintenance.sh の dev-friendly 拡張** に留まり「vault 思想の根本的更新」ではない。サブシステム改善の rein は維持
2. **vault-maintenance.sh が次第に厚くなっている**: 現状 4 check (orphan/broken/stale/duplicate) + 今回 2 check (rare-tag/naming) = 6 check。さらに次回 absorb で axis 3 (Archive sweep) も追加可能性あり。`check_*()` 関数増加に対する Build-to-Delete 原則の検討必要（30 日後に効果測定）
3. **delta=1 が真の novel になった珍しい事例**: 同 family 14 件累積で delta=1 は通常 imagination 罠の前兆 (Sonnet が拡張可能性を膨らませる典型)、今回は実行可能で具体的な未実装機能（rare tag audit）として確定できた。Pass 2 の引用照合（vault-maintenance.sh 実装ファイル直接 Read）で検証

## Phase 5 Handoff

- **規模**: S（1 file, 2 functions, ~80 行）
- **推奨**: その場で実行可、ユーザー確認の上で実装
- **log.md 追記**: `ingest (light Phase 2)`、本体に「採用 2 件」明記
- **MEMORY.md 索引**: 既存 obsidian-second-brain family entry に追記（family_entry: 15）
- **Wiki/Obsidian 連携**: light-phase2 のため省略可（家族 saturated）

## 実装プラン

```bash
# 変更対象
dotfiles/.config/claude/scripts/runtime/vault-maintenance.sh

# 追加関数
1. check_rare_tags()
   - find $VAULT_PATH -name "*.md" -exec grep -hoE '#[a-zA-Z0-9/_-]+' {} \;
   - frontmatter `tags: [...]` も合わせて集計
   - sort | uniq -c | awk '$1 < 5 {print}' で rare tag 抽出
   - 結果: "<count>x <tag> (consider removing or merging)"

2. check_naming_compliance()
   - 04-Galaxy/: regex `^[0-9]{14}-[a-z0-9-]+\.md$`
   - 05-Literature/: regex `^lit-.+\.md$`
   - 01-Projects/proj-*/: regex `^[0-9]{4}-[0-9]{2}-[0-9]{2}-.+\.md$`
   - 違反ファイルパスを列挙

# 統合
main() ループに 2 関数を追加、--dry-run でデフォルト動作
```

## Verification

- `OBSIDIAN_VAULT_PATH="<user-vault>" vault-maintenance.sh --dry-run` で実行
- 既存 vault に対する false positive 件数を確認（5 件未満なら採用、超過なら閾値再調整）
- 初回は **dry-run 専用**、auto-fix なし
