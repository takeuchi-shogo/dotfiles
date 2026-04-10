---
source: "Medium — Skills for Claude Code: The Ultimate Guide from an Anthropic Engineer"
date: 2026-04-11
status: integrated
---

# Skills for Claude Code — The Ultimate Guide 分析レポート

## Source Summary

**主張**: Skills は Markdown プロンプトではなく「フォルダベースのエージェントプラグイン」。scripts/data/configs/templates/memory/hooks/tools を束ねて Claude を chatbot から operator に変える。良いスキルは 9 タイプに分類でき、品質は Gotchas・filesystem context engineering・反復改善から生まれる。

**9 Types**: Library & API Reference / Product Verification / Data Retrieval & Analysis / Business Process Automation / Code Templates & Scaffolding / Code Quality & Review / CI/CD & Deployment / Runbook / Infrastructure Operations

**9 Best Practices**:
1. Don't write the obvious
2. Gotchas section = most valuable
3. Filesystem as context engineering
4. Guidelines not rules
5. Setup config.json pattern
6. Description field = trigger condition
7. Skills can store memory (logs/JSON/SQLite)
8. Scripts over instructions
9. Hooks on demand (/careful, /freeze)

**補足**: composition, usage measurement, iterative "start small + one gotcha" 進化、repo vs marketplace 共有

**根拠**: Anthropic 本番で数百スキル稼働、Product Verification は「1週間エンジニア専任の価値」、多くのスキルは数行から進化

**前提**: Claude Code 環境、iteration 可能なチーム、反復可能なオペレーション。Anthropic 社内 (standup/oncall/infra ops) が暗黙のユースケース

---

## Phase 2: ギャップ分析（初版 Sonnet Explore）

当初 Sonnet Explore は記事の 90% 以上がカバー済みと判定。主要 exists 9 項目 + partial 5 項目 + gap 1 項目の構造。

## Phase 2.5: Codex 批評による修正

Codex が実ファイル確認ベース（92 SKILL.md 全走査）で以下の [verified] 修正を行った:

### 見落とし

- **BP5 config.json**: `Partial` → **実質 Gap**。`config.json` / setup schema は見当たらず、skill-lessons 分析 (2026-03-18) も「具体的適用は今後」と記述
- **BP7 memory**: `review` / `timekeeper` / `daily-report` は個別 JSONL 蓄積に留まり、`capture-and-write.md` に「スキル自己状態管理」を選ばせる標準はない
- **Gotchas 普及率**: `## Gotchas` は **23/92 SKILL.md (25%)**。当初想定「35/54」とは大幅にズレ
- **skill sharing**: 完全 Gap ではない。`ai-workflow-audit.md` に repo/global 昇格基準あり、但し marketplace 配布/退役ポリシーなし

### 過大評価

- **9-type taxonomy**: 「5パターン+5カテゴリで統合済」は甘い。`skill-design.md` に 9 カテゴリあるが、`skill-archetypes.md` は構造設計の 5 型でカバレッジ分類ではない。**「Documented / Not operationalized」が正確**
- **90% カバー済み**: 強すぎる。hooks 使用は **4 スキルのみ**、Chaining section は **9 件のみ**。体系はあるが浸透率低

### 過小評価

- **Product Verification**: `webapp-testing` / `validate` は**汎用検証基盤**。記事の「製品固有 oracle に 1 週間投資」とは別物
- **BP6 description trigger**: 設計は強いが実 skill 全体の品質は未監査。`Already` ではなく「基盤あり、棚卸し必要」
- **BP9 hooks on demand**: `careful` は "Blocks rm/DROP..." と宣伝するが実装は**全 Bash に prompt**、`freeze` も Edit/Write prompt で決定論的 block ではない。記述と実装が乖離

### 前提の誤り

- Anthropic 社内 (standup/oncall/infra ops) 前提は個人 dotfiles では ROI が下がる (chaos-engineer-analysis.md の事例参照)
- Product Verification 1 週間投資は dotfiles 自体では低価値、別 repo 横断支援時のみ価値あり
- Infrastructure Ops は `N/A` 寄りが妥当（個人 dotfiles は本番運用 runbook 対象ではない）
- Anthropic engineer 権威づけは独立確認できず。結論の妥当性は肩書きではなく repo 適合性で判断すべき

### Gemini の扱い

Gemini は別調査（Gotchas パターン調査）に分岐し有意な出力を返さず（空振り）。Codex 批評のみで Phase 2.5 を完了。

---

## Phase 2.5 修正後の分析テーブル

### Gap / Partial / N/A

| # | 項目 | 判定 | 現状 |
|---|------|------|------|
| 1 | BP5 config.json / setup schema | **Gap** | スキーマも setup detection も不在 |
| 2 | Gotchas 浸透率 | **Partial** | 23/92 (25%)。lessons-learned → SKILL.md ## Gotchas の昇格経路なし |
| 3 | 9-type taxonomy | **Documented/Not operationalized** | 分析ドキュメントはあるが skill-creator/skill-audit の operational schema に未統合 |
| 4 | Product Verification (repo 固有型) | **Partial** | 汎用 wrapper のみ、記事の「repo 固有 oracle」派生型は不在 |
| 5 | BP9 hooks 宣伝/実装乖離 | **Partial** | careful/freeze の説明と非決定論的 prompt block が乖離 |
| 6 | BP6 description quality 棚卸し | **Partial** | 基盤強いが実 skill 品質監査未実施 |
| 7 | BP7 スキル単位 memory 標準 | **Partial** | 個別の JSONL 蓄積あり、標準パターン不在 |
| 8 | Skill composition 具体例 | **Partial** | 関係定義あり、具体例不在 |
| 9 | Marketplace distribution policy | **Partial** | 昇格基準あり、退役/配布ポリシーなし |
| - | Infrastructure Ops 特化スキル | **N/A** | 個人 dotfiles では ROI 低 |

### Already (強化不要) — 記事より深く体系化済み

| 項目 | 理由 |
|------|------|
| BP3 DBS Rubric | scripts/references/assets 体系化済み |
| BP4 Onboarding philosophy | skill-writing-guide で明記 |
| BP8 Scripts over instructions | DBS Rubric に統合済み |
| Usage measurement | skill-tracker.py → skill-executions.jsonl → skill-audit の実装線あり |
| Iterative dev (Meta-Harness) | 3-5 debug runs 明記 |

---

## Phase 3: Triage 選別結果

Codex Top 3 優先を採用:

### 採用

1. **BP5 config/setup schema 追加** → `skill-writing-principles.md` に最小スキーマ
2. **Gotchas promotion loop** → `skill-audit/SKILL.md` に coverage scan + lessons-learned 昇格経路
3. **Product Verification 派生型** → `skill-archetypes.md` に 5a 派生型

### 見送り（Codex 推奨）

- 9-type 全面 metadata 化（92 スキルへの付与は M-L 規模、ROI 合わない）
- Infrastructure Ops 専用スキル（個人 dotfiles で不要）
- marketplace policy 重装備化（オーバーエンジニアリング）
- BP9 hooks on demand 全面再設計（設計思想レベルで異なる、現行維持）

---

## Phase 4: 実装

### 変更ファイル

1. **`/Users/takeuchishougo/dotfiles/.config/claude/skills/skill-creator/references/skill-writing-principles.md`**
   - 「Setup Config & Persistent State — 標準スキーマ」セクション追加
   - `config.json` / `~/.claude/skill-data/{skill}/` namespace 定義
   - Setup detection フロー（`required_setup` → AskUserQuestion → 書き戻し）
   - Python 読み書きパターン（`skill_data_dir()` helper with `SKILL_NAME_RE` validation + containment check）
   - 秘密情報は `config.json` に**絶対書かない**、`secrets.env` or keychain へ分離

2. **`/Users/takeuchishougo/dotfiles/.config/claude/skills/skill-audit/SKILL.md`**
   - 「Gotchas Coverage Scan」セクション追加
   - Coverage 集計（find/grep で SKILL.md 走査）
   - Gotchas-less skill 抽出 + Usage Tier Dominant/Weekly 優先フラグ
   - Promotion Backlog 検出（lessons-learned → SKILL.md `## Gotchas` 昇格候補）
   - 判定基準（Coverage < 40% / 40-70% / ≥ 70% の 3 段階）
   - 昇格ワークフロー（lessons-learned は削除せず両方に残す）

3. **`/Users/takeuchishougo/dotfiles/.config/claude/skills/skill-creator/references/skill-archetypes.md`**
   - Tool Wrapper 5a: Product Verification 派生型追加
   - 必須要素: `scripts/run.sh` / `scripts/assertions/` / `evidence/` / `references/product-invariants.md`
   - **Credential 分離**: `config.json` / `.spec.ts` / `.http` に hardcode 禁止、`~/.config/{skill}/secrets.env` or keychain
   - **Evidence sanitize**: HAR の authorization/cookie/set-cookie ヘッダ除外、screenshot PII マスク
   - **Retention policy**: `evidence/` は 7 日のみ保持
   - Tool Wrapper との違いテーブル、いつ作るかの判断基準

### Security Review 対応

security-reviewer サブエージェントから 3 つの Medium 指摘を受けて追加修正済み:

1. **skill_name path traversal** (M) → `skill-writing-principles.md` の Python 例に `SKILL_NAME_RE` validation + `Path.resolve().relative_to(root)` containment check を追加
2. **Evidence PII 取扱い** (M) → `skill-archetypes.md` 5a に HAR sanitize / screenshot PII マスク / 7日 retention を必須要素化
3. **Product Verification credential 取扱い** (M) → 同ファイルに seed user 認証情報の secrets.env/keychain 分離を明記

### 変更規模

全 3 ファイル S 規模。後続修正（Security Review 対応）含め計 5 edit。

---

## 総評

**記事の実質カバー率**: 60-70%（初期 Sonnet Explore の 90% 判定は Codex 批評で下方修正）

**既存ハーネスが先行している領域**:
- DBS rubric (Description as Trigger)
- Progressive Disclosure (CLAUDE.md 130行 → references/ → rules/)
- "Onboarding not manuals" (PostHog absorb で先行統合)
- Scripts over instructions (5 カテゴリ体系)
- Filesystem as context engineering (output-offload + 3 スコープメモリ)
- Meta-Harness iterative dev (3-5 debug runs)

**記事が明示した実質的ギャップ**:
- config.json 永続設定の標準スキーマ（Gap → T1 対応）
- Gotchas セクション普及率 25%（Partial → T2 対応）
- Product Verification の独立アーキタイプ未整備（Partial → T3 対応）

**Codex 批評の貢献**: 「Already」への過大評価バイアスを修正し、実質的な Gap/Partial を特定。特に `config.json` パターンが「メモリで代替できる」という思い込みを崩したことで T1 の実装価値が明確化。

**Gemini の評価**: 空振り（別調査に分岐）。今回の absorb では貢献なし。Codex 単独でも十分な批評精度だった事例。

**記事自体の評価**:

| 次元 | 評価 |
|---|---|
| 直接タスク生成力 | 中（3 タスク採用） |
| 既存設計との重複 | 高（60-70% カバー済み） |
| Codex 批評の追加価値 | **高**（初期判定の重要修正、特に Gotchas 実態 25% の発見） |
| 長期参照価値 | 中（config.json パターンは新規スキル作成時に参照） |

---

## Deferred / Next Session

- **description 品質監査**: 92 スキルのトリガー精度計測は大規模作業 → 次回 `/skill-audit` 実行時
- **Gotchas 普及率 25% → 60% 向上**: T2 で導入した coverage scan を使って段階的改善 → 3 ヶ月以内
- **スキル別 hook 追加フロー文書化**: BP9 の思想的差異は維持しつつ、必要なら将来タスク化

---

## 出典

- Medium: "Skills for Claude Code — The Ultimate Guide from an Anthropic Engineer" (URL 特定不可、Codex による確認も不可)
- 関連先行 absorb:
  - `docs/research/2026-03-18-skill-lessons-analysis.md`
  - `docs/research/2026-04-11-posthog-agent-first-rules-analysis.md` ("Onboarding not manuals")
  - `docs/research/2026-04-10-notebooklm-claude-extend-sessions-analysis.md` (DBS rubric)
- 変更先: `skill-writing-principles.md`, `skill-audit/SKILL.md`, `skill-archetypes.md`

---

*Generated: /absorb Phase 4 — 2026-04-11*
