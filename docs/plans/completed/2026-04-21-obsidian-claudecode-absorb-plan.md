---
source: "Obsidian × Claude Code (@akira_papa_AI, Qiita 2026-03-10)"
analysis: "docs/research/2026-04-21-obsidian-claudecode-absorb-analysis.md"
date: 2026-04-21
status: active
size: L
success_criteria:
  - "A1: cwd/path routing matrix が references/ に codify され、Vault/dotfiles/外部repo での skill/rule 読み込み差分が明示されている"
  - "A2: /weekly-review 実行時に Vault 00-Inbox/ + vault-maintenance.sh report の未処理項目が decision loop に吸い上げられる"
  - "B1: dead-weight scan が実行可能で、使用頻度ゼロの skill/hook/script を候補リスト化し improve-policy.md の wiring が稼働する"
  - "C1: docs/adr/0007 が追加され、Thin CLAUDE.md + Thick rules 原則が IFScale 根拠と共に記録される"
  - "C2: skill-writing-principles に (1) 動詞+名詞命名 (2) トップレベル 5-9 制約 (3) 規範的フレーミング方針の 3 節が追加されている"
---

# Integration Plan: Obsidian × Claude Code (@akira_papa_AI)

## Overview

| Field | Value |
|---|---|
| Source | Obsidian × Claude Code (@akira_papa_AI, Qiita 2026-03-10) |
| Analysis | docs/research/2026-04-21-obsidian-claudecode-absorb-analysis.md |
| Total Tasks | 5 |
| Estimated Size | L |

### Success Criteria (PLANS.md 準拠)

- [ ] A1: cwd/path routing matrix が references/ に codify され、Vault/dotfiles/外部repo での skill/rule 読み込み差分が明示されている
- [ ] A2: /weekly-review 実行時に Vault 00-Inbox/ + vault-maintenance.sh report の未処理項目が decision loop に吸い上げられる
- [ ] B1: dead-weight scan が実行可能で、使用頻度ゼロの skill/hook/script を候補リスト化し improve-policy.md の wiring が稼働する
- [ ] C1: docs/adr/0007 が追加され、Thin CLAUDE.md + Thick rules 原則が IFScale 根拠と共に記録される
- [ ] C2: skill-writing-principles に (1) 動詞+名詞命名 (2) トップレベル 5-9 制約 (3) 規範的フレーミング方針の 3 節が追加されている

### Tasks

#### Task A1: cwd/path routing matrix codify

| Field | Value |
|---|---|
| Files | .config/claude/references/cwd-routing-matrix.md（新規） |
| Dependencies | なし |
| Size | S |

**Changes:**
- Vault root / dotfiles root / 外部 repo / その他 cwd の 4 区分について、読み込むべき rules/skills/agents と読み込まない skills を matrix で明記
- 既存 rules/*.md の `paths:` frontmatter を活用し、matrix と整合させる
- CLAUDE.md から "cwd-aware context" セクションへのリンク追加

#### Task A2: /weekly-review に Obsidian 統合

| Field | Value |
|---|---|
| Files | .config/claude/skills/weekly-review/SKILL.md |
| Dependencies | なし |
| Size | S |

**Changes:**
- Phase 2 (Inbox 処理) に Vault 00-Inbox/ triage を追加
- 新 Phase: vault-maintenance.sh の最新 report を読み込み、未処理項目を Horizon 1 decisions に変換
- GitHub Issue inbox と Vault 00-Inbox/ を明確に分離して扱う

#### Task B1: Build to Delete 実測 wiring

| Field | Value |
|---|---|
| Files | .config/claude/references/improve-policy.md（編集）, .config/claude/scripts/lifecycle/dead-weight-scan.sh（新規 or 既存拡張） |
| Dependencies | なし |
| Size | M |

**Changes:**
- dead-weight-scan.sh: skill/hook/script の 30日使用ログから使用頻度ゼロを検出
- 結果を maintenance report と統合し、improve-policy.md の "removal candidate" セクションに流す
- /improve 起動時に candidate を提示、30日評価ルールと接続

#### Task C1: Thin CLAUDE.md + Thick rules ADR

| Field | Value |
|---|---|
| Files | docs/adr/0007-thin-claudemd-thick-rules.md（新規） |
| Dependencies | なし |
| Size | S |

**Changes:**
- Context: IFScale ベンチマーク、Progressive Disclosure、現行 CLAUDE.md 94行 / rules/ 18ファイル構成
- Decision: CLAUDE.md は常時コンテキスト用の decision heuristics のみ、rules/ は条件付き詳細
- Consequences: 80-150行上限、追加は rules/ へ、など

#### Task C2: skill-writing-principles 大更新

| Field | Value |
|---|---|
| Files | .config/claude/skills/skill-creator/references/skill-writing-principles.md |
| Dependencies | なし |
| Size | S |

**Changes:**
- 新節: 命名規約（動詞+名詞、例 enumeration）
- 新節: トップレベルコマンド 5-9 個制約（Miller 7±2 / Hick 根拠）
- 新節: 規範的フレーミング優位（Constitutional AI, Mirror Effect r=0.925 根拠）

## Risk Assessment

| Risk | Impact | Mitigation |
|---|---|---|
| 5タスクを一気に実行して消化不良 | 中 | Codex 推奨順 A1 → A2 → B1 → C1 → C2 で段階実行、各 task 単独でも価値を持つ設計 |
| cwd routing matrix が既存と矛盾 | 中 | 既存 paths: frontmatter を source of truth にし matrix はその要約 |
| /weekly-review が肥大化 | 低 | 既存 6 フェーズを維持、Vault 統合は Phase 2 への追加のみ |
| dead-weight scan の誤検出 | 中 | 30日評価期間を維持、手動確認を挟む fail-safe |
| ADR 後の既存 rules/ 再編リスク | 低 | 原則の codify のみ、既存構成は維持 |

## Execution

| Size | Approach |
|---|---|
| L | docs/plans/active/ に保存、新セッションで /rpi or 手動実行 |

推奨順: A1 → A2 → B1 → C1 → C2。各タスクは独立に完了可能。
