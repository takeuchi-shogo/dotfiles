---
source: "Obsidian × Claude Code — .claude/ ディレクトリ設計パターンと35個のコマンド実例 (@akira_papa_AI) https://qiita.com/akira_papa_AI/items/4ac1edc7e93604b0199a"
date: 2026-04-21
status: analyzed
---

## Source Summary

**主張**: Obsidian Vault に Claude Code の `.claude/` ディレクトリを配置し、35 コマンド / 18 ルール / 10 スキルを設計することで、ナレッジ管理を AI と共に動かすシステムへ転換できる。「考える脳（Obsidian）」と「動く手足（Claude Code）」を統合する運用パラダイム。

**手法**:
- CLAUDE.md: プロジェクト自己紹介書（300行以内、実運用では80行）
- .claude/commands/: 35 スラッシュコマンド化（daily, weekly-review, inbox-review 等）
- .claude/rules/: 18 判断基準明文化（tech-stack, naming, timezone, security 等）
- .claude/skills/: 10 複合ワークフロー（vault-master, sprint-task-sync 等）
- パススコープ: 特定ディレクトリ限定ルール
- 5 設計原則: ①薄 CLAUDE.md + 厚 rules/ ②動詞+名詞命名 ③禁止より推奨 ④1コマンド1タスク ⑤定期棚卸し

**根拠**:
- Daily Note 作成: 5分 → 10秒（約97%削減）
- 週次レビュー: 30分 → 5分（約83%削減）
- CLAUDE.md: 500行 → 80行に削減
- 2ヶ月継続運用、1,000+ ノート環境での実績

**前提条件**:
- Obsidian Vault 利用者
- 2026年2月時点の Claude Code 仕様
- 個人運用中心
- ナレッジ管理時間が本来業務を圧迫している状況

### Gap Analysis (Pass 1: 存在チェック + Pass 2 + Codex/Gemini 修正後)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Daily Note 作成コマンド | N/A | `/morning` + `timekeeper` + `auto-morning-briefing.sh` で実質カバー、新規追加は command 増殖 |
| 2 | Obsidian Inbox triage | Gap | Vault `00-Inbox/` の triage loop が decision cycle と未接続（GitHub Issue inbox と別物） |
| 3 | Sprint Task Sync | N/A | 著者固有運用（チーム開発）、個人 dev setup には不要 |
| 4 | パススコープ限定ルール | Partial | `.config/claude/rules/*.md` に `paths:` frontmatter あり、cwd 間 routing policy 未確認 |
| 5 | 「禁止より推奨」方針 | Partial | KISS/search-first/mechanism 化は positive routing、rules 全体の一貫性不足 |
| 6 | 1コマンド1タスク原則 | Partial | skill-writing-principles にあり、トップレベル 5-9 個制約は未 codify |
| 7 | Vault root に .claude/ 配置 | Already | obsidian-vault-setup で対応済み、dotfiles 混線リスクは #4 で対応 |

### Already Strengthening Analysis (Pass 2 + Codex 修正後)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| A | `/weekly-review` skill | Obsidian 00-Inbox/ + maintenance report と未接続、GitHub Issue 中心 | 00-Inbox/ triage + vault-maintenance report routing を weekly-review に吸収 | 強化可能 |
| B | vault-maintenance.sh | report 生成で止まりやすい、誰の inbox にいつ流すか未定義 | SKILL 化より先に「report 決定フロー先」を decide | 強化可能 |
| C | CLAUDE.md 94行 + rules/ 18ファイル | 実態は thin/thick だが設計原則として明文化なし | ADR-0007 "Thin CLAUDE.md / Thick rules" codify、IFScale 根拠併記 | 強化可能 |
| D | 動詞+名詞命名が実態として多い | skill-writing-principles に明示なし | naming convention + トップレベル 5-9 制約を明文化 | 強化可能 |
| E | Build to Delete + AutoEvolve | improve-policy.md に "not yet wired" 明記、削除候補浮上運用未完成 | dead-weight scan / skill usage / maintenance report → 削除候補流入 wiring | 強化可能 |
| F | Obsidian skill 8個 | 35個と比べ少数だが dev 中心 setup では妥当 | 新規追加より既存 routing 強化を優先 | 強化不要 |
| G | Vault root .claude/ パターン | 対応済み | — | 強化不要 |

### Codex/Gemini Refine Notes

**Codex の主要指摘で修正した点:**
- Daily Note: 重複リスクで Partial → N/A
- Inbox Review: 二重 inbox 混同指摘で Partial → Gap（Obsidian 側）
- cwd-aware: paths: frontmatter 既存で Gap → Partial
- 禁止より推奨: positive routing 既存で Gap → Partial
- /weekly-review: Obsidian 未接続で強化不要 → 強化可
- Build to Delete: improve-policy.md "not yet wired" で強化不要 → 強化可

**Gemini の周辺知識補完:**
- Karpathy raw/wiki/CLAUDE.md 3層パラダイム（2025-2026 主流）
- Noun-Verb 階層化、トップレベル 5-9 個（Miller's magic number, Hick の法則）
- 自動化メンテ負荷で 30% 削減効果相殺の事例
- Anthropic Constitutional AI: 規範的フレーミング > 禁止的（r=0.925 Mirror Effect）
- IFScale: 40,000-50,000 文字が上限、80行は十分余裕、Progressive Disclosure で 30% ハルシネーション削減

### Integration Decisions

#### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | Daily Note コマンド追加 | スキップ | 既存で実質カバー、command 増殖リスク |
| 2 | Obsidian Inbox triage | 採用 | Codex 最優先 #2、decision loop 接続必須 |
| 3 | Sprint Task Sync | スキップ | 個人 setup に不要 |
| 4 | cwd/path routing matrix | 採用 | Codex 最優先 #1、混線防止 |
| 5 | 「禁止より推奨」方針 codify | 採用 | Constitutional AI 根拠、トーン統一 |
| 6 | 1コマンド1タスク + 5-9 制約 | 採用 | 認知負荷根拠、skill 乱立防止 |
| 7 | Vault root .claude/ 配置 | 既対応 | — |

#### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| A | /weekly-review 強化 | 採用（B/E に吸収） | Obsidian 00-Inbox/ + maintenance report 統合 |
| B | vault-maintenance report 決定フロー | 採用 | Codex 指摘、report → 裁きの流れ確立 |
| C | Thin CLAUDE.md + Thick rules ADR | 採用 | 原則 codify で将来判断軸を確立 |
| D | 動詞+名詞命名 + 5-9 制約 | 採用（Gap #6 と統合） | skill-writing-principles 更新 |
| E | Build to Delete wiring | 採用 | Codex 最優先 #3、削除運用完成 |
| F | Obsidian skill 数 | スキップ | 新規追加より routing 強化 |
| G | Vault root .claude/ | スキップ | 既対応 |

## Plan

5 タスクに統合。詳細は `docs/plans/active/2026-04-21-obsidian-claudecode-absorb-plan.md` 参照。

| ID | タスク | 規模 | ファイル |
|---|---|---|---|
| A1 | cwd/path routing matrix codify | S | .config/claude/references/cwd-routing-matrix.md（新規） |
| A2 | weekly-review に Obsidian Inbox triage + maintenance report routing 統合 | S | .config/claude/skills/weekly-review/SKILL.md（編集） |
| B1 | Build to Delete 実測 wiring | M | .config/claude/references/improve-policy.md + scripts/lifecycle/dead-weight-scan.sh |
| C1 | Thin CLAUDE.md + Thick rules ADR | S | docs/adr/0007-thin-claudemd-thick-rules.md（新規） |
| C2 | skill-writing-principles 大更新（動詞+名詞命名 + 5-9 制約 + 規範的フレーミング） | S | .config/claude/skills/skill-creator/references/skill-writing-principles.md（編集） |
