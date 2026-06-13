---
title: サーヴァントエンジニアリング absorb — レビュー速度改善 (tiering/計測/蒸留/学習ループ)
created: 2026-06-12
status: pending
source: docs/research/2026-06-12-servant-engineering-absorb-analysis.md
article: https://speakerdeck.com/nrslib/implementation-got-faster-so-what-about-reviews-an-invitation-to-servant-engineering-recreating-your-own-code-reviews-with-ai
scale: L (8 tasks, 4 waves, ~6+ files)
priority: high (Wave 1-2 がレビュー速度に直結)
---

# サーヴァントエンジニアリング absorb 統合プラン

ユーザー要望「レビュー速度を改善したい」に対する統合プラン。
Codex 批評 (Phase 2.5) の優先度提案に従い Wave 構成。**品質を落とす変更は含まない**
(「速さより品質」feedback_review_quality_first と整合 — 品質要求を risk に合わせる整理 + 待ち時間の並列化 + 人間レビュー負荷の削減)。

## 撤退条件 (references/reversible-decisions.md)

- T1/T2 (tiering): light tier 導入後 30 日で「light 判定だった変更に起因する regression」が 1 件でも出たら tier 閾値を見直し、2 件で revert
- T5 (蒸留): review-learnings 注入で reviewer の指摘が体感ノイズ増となったら該当 domain ファイルを削除 (注入機構は条件付きなのでファイル削除 = 即無効化)

---

## Wave 1: 速度の本丸 — review tiering + 計測

### T1: deterministic preflight (light/standard/deep) を /review に追加 (M)

- **File**: `.config/claude/skills/review/SKILL.md` (Step 0 新規) + `.config/claude/skills/review/references/reviewer-routing.md`
- 既存の「リスクカテゴリ自動判定」(reviewer-routing.md High/Medium/Low 表) を入力として tier を決定論で判定:
  - **light**: docs-only / test-only / ≤10行 かつ Low リスクパス → Verify のみ (Codex Gate 省略)
  - **standard**: 通常コード変更 → 現行の行数スケール表どおり
  - **deep**: High リスクパス (auth/migration/security/harness/hooks) or 200行超 or 依存 (lockfile/go.mod/package.json) 変更 → codex-reviewer 必須 + security-reviewer
- 判定ロジックは「Static-checkable rules は mechanism に寄せる」原則に従い
  `scripts/policy/review-tier.py` (新規 S) に切り出し、SKILL.md は出力を参照する
- **重複定義を作らない**: リスクカテゴリ表は reviewer-routing.md が正、tier 表はそれを参照

### T2: CLAUDE.md ワークフロー表の policy conflict 解消 (S)

- **File**: `templates/claude-md/*.md` (生成元を編集 — CLAUDE.md 直接編集は build-claude-check が reject)
- S 規模の必須段階「Implement → Codex Review Gate → Verify」を
  「Implement → Review (tier-based; light は Verify のみ) → Verify」に変更
- 根拠: `review/SKILL.md` の「~10行 = レビュー省略」と矛盾している現状の解消 (Codex 検出)
- **検証**: `task validate-configs` + build-claude-check

### T3: レビュー計測基盤 (M)

- **File**: `.config/claude/skills/review/SKILL.md` (Step 4 Synthesis に記録手順追記) +
  `review-findings.jsonl` スキーマ拡張 (`.config/claude/skills/review/references/findings-and-feedback.md`)
- 記録項目: reviewer 別 duration / findings 数 / confidence 分布 / verdict / rerun 数
- 目的: 「5-10 分」が体感値のまま — どの reviewer / どの tier が遅いかを可視化してから削る
- T6 (outcome 書き戻し) とスキーマを共有する

## Wave 2: 待ち時間短縮 (品質そのまま)

### T4: T8 並列 closeout の実装 — 既採用・未実装の消化 (M)

- **既存プラン**: `docs/plans/active/2026-05-28-autoreview-absorb-plan.md` の T8 (pending 15 日)
- format → tests ∥ review の並列実行を `github-pr/SKILL.md` (第一候補) に追加
- 実装内容・verbatim quote・caveat は既存プラン記載に従う。完了したら旧プランの T8 を done に更新

## Wave 3: 記事の核心 — 自分のレビュー観点の再現

### T5: feedback_*.md → review-learnings/*.md 蒸留 (M)

- **Source**: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/feedback_*.md` (~20個) +
  `~/.claude/agent-memory/learnings/review-findings.jsonl` の過去指摘
- **出力**: `.claude/data/review-learnings/{harness,go,typescript,docs}.md` + `index.md`
  (dotfiles 向け domain マップを index.md に定義 — SKILL.md 記載例 product/recording 等は別リポジトリ用)
- **Codex 補強**: feedback_*.md の直注入は危険 — domain 別 **5-10 個の短い rule に蒸留**する
- **記事の棚卸し手順 (p.34-40) を適用**: AI がドラフト → ユーザーが「見る/見ない/部分的に見る」の
  線引きでレビューして確定。違和感・事業判断は明文化しない (本人に残す)
- 注入機構は `review/SKILL.md` に実装済み (`ls .claude/data/review-learnings/*.md`) — ファイルを置けば即有効

## Wave 4: 学習ループ・保守性

### T6: outcome 書き戻しの復旧 (M)

- **Flag 済み**: decommission-log — review-feedback-tracker の Rust 版欠落 4 点
  (partial 3値 / R-05 explicit 優先 / findings 書き戻し / redaction)
- **実装先**: `tools/claude-hooks` post_bash.rs 追補 (decommission-log の復活条件に従う)
- accept/reject の実運用配線が弱い (Codex: Output Contract は形式 Already / 学習ループ Partial)

### T7: checklist 適用 manifest (S)

- **File**: `.config/claude/agents/code-reviewer.md` — COMPLETION CONTRACT に
  `Applied Checklists: cross-cutting@<hash>, go@<hash>` 行を必須出力として追加
- Read 強制 (tool trace) はコスト増のため不採用 (Codex 提案の軽量代替)
- synthesis 側 (review SKILL.md Step 4) で manifest 欠落時に警告

### T8: Policy 一元化 (M, 優先度最低)

- **File**: `.config/claude/agents/code-reviewer.md` 内の CC 系基準 (結合度分析等) を
  `references/review-checklists/cross-cutting.md` へ移動、agent は参照のみに
- 「一箇所直せば全レビューに反映」(記事 Faceted Prompting) の回復
- Codex: 「compiled prompt として機能している面もある。最後でよい」

---

## 依存関係

```
T1 → T2 (tier 定義が先、CLAUDE.md が参照)
T3 ∥ T1 (並行可)、T3 → T6 (計測スキーマ共有)
T4, T5, T7 は独立
T8 は任意のタイミング (最後)
```

## 検証

- T1/T2: `task validate-configs`, build-claude-check, 直近 PR 3 件の diff で tier 判定の dry-run
- T3: /review 1 回実行後に review-findings.jsonl へ duration が記録されること
- T5: /review 実行時に code-reviewer プロンプトへ learnings が注入されること (transcript 確認)
- 全体: Codex Review Gate (harness 変更のため deep tier 相当)

## 関連

- 分析レポート: `docs/research/2026-06-12-servant-engineering-absorb-analysis.md`
- 既存プラン (T4 の正): `docs/plans/active/2026-05-28-autoreview-absorb-plan.md`
- 周辺知識: AutoReview (FSE 2025) multi-agent F1+18.7% / popularity trap (異種モデル構成は維持) /
  GLOBIS・Cloudflare・minewo の同系事例 (レポート参照)
