---
title: "Tech-Debt-Skill (ksimback) absorb 分析"
date: 2026-04-26
source: https://github.com/ksimback/tech-debt-skill
status: integrated
target: .config/claude/skills/audit/SKILL.md
---

# Tech-Debt-Skill (ksimback) absorb 分析

## ソース

- リポジトリ: https://github.com/ksimback/tech-debt-skill
- 著者: ksimback
- ライセンス: 確認推奨
- 取り込み日: 2026-04-26

## 記事の主張

Tech-Debt-Skill は Claude Code スキルで、**汎用ベストプラクティス・チェックリスト**ではなく**コードベース全体の徹底的で引用可能な技術負債監査**を行う。

3フェーズ:
- **Orient**: アーキテクチャ理解 mandatory（境界・主要 flow・invariants・runtime surface）
- **Audit**: 9次元（Architecture崩壊 / Consistency腐食 / Type-Contract負債 / Test負債 / Dependency負債 / Performance衛生 / Error/Observability / Security衛生 / Documentation drift）
- **Deliverable**: TECH_DEBT_AUDIT.md（executive summary + findings table 30-80 items + Top 5 priorities + Quick Wins + Open questions + Non-Findings）

哲学: "diplomatic vagueness を排除し、外交的でない、深さ優先の分析"

特徴:
- file:line citation 強制
- "looks bad but is fine" section 強制（監査者が検討した non-findings を可視化）
- Repeat-run mode: RESOLVED/NEW tag で時系列追跡
- Stack-specific tooling: TS (npm audit, madge, knip), Python (ruff, vulture), Rust (cargo audit), Go (govulncheck)
- Subagent dispatch (50k+ LOC で context exhaustion 回避)
- Project-level overrides

## 既存セットアップとのギャップ分析

### Pass 1: 存在チェック (Sonnet Explore)

| # | キーワード | 判定 | 既存ファイル |
|---|-----------|------|------------|
| 1 | tech-debt-audit | exists | `.config/claude/skills/audit/SKILL.md` |
| 2 | 3-phase audit | partial | 6ステップパイプライン |
| 3 | 9次元負債分類 | partial | 8カテゴリ（documentation 別管轄） |
| 4 | file:line citation | exists | audit/review で強制 |
| 5 | "looks bad but is fine" | partial | Step 6 事後分類のみ |
| 6 | Stack-specific tooling | exists | dependency-auditor (npm/go/cargo/pip) |
| 7 | Repeat-run tracking | not_found | 時系列差分追跡なし |
| 8 | Subagent dispatch | exists | Gemini + 並列エージェント |
| 9 | Project-level customization | exists | `.claude/skills/` パターン |
| 10 | Audit artifact | partial | QUESTIONS.md（TECH_DEBT_AUDIT.md なし） |

### Pass 2.5: Codex + Gemini 批評で修正

**Codex の主な指摘:**
- #5 Quick Wins/Top5: Gap → Partial に降格（QUESTIONS.md Summary に追加で十分）
- #4 Architecture mandatory: Partial の重要度が低すぎる（境界・データ流・invariants まで必要）
- #1 non-findings: 重要度上げる（Pruning-First で再発掘防止）
- #7 Diplomatic vagueness: N/A → Partial（output contract として翻訳可能）
- 9次元 vs 8カテゴリ圧縮: OK だが crosswalk 必要（/check-health 結果の引用統合）

**Gemini の主な指摘:**
- 2026 ベストプラクティス = SAST + LLM Triage hybrid（ast-grep/Semgrep を triage 入力に）
- LLM 監査は hallucination リスクあり（虚偽 line 検出が必要）
- Repeat-run は個人でも有効、ただし git + 前回 report diff で十分（専用 state 不要）

## ユーザー選択

全項目取り込み（P1-P6）+ 既存 /audit を強化のみ（Pruning-First）+ S-M 同セッション実行。

## 統合プラン (実施済み)

`.config/claude/skills/audit/SKILL.md` を強化:

1. **Step 1 → Orient Gate 昇格**: 境界・主要 flow・invariants・runtime surface の 4 要素を mandatory 化。要約できない要素は blind spot として QUESTIONS.md 冒頭に記録
2. **Step 2.0 Structural Pre-filter (Optional)**: ast-grep / madge / knip / vulture / ruff / Semgrep の結果を Gemini プロンプトの suspect_patterns に注入
3. **Step 3.5 Documentation Drift Crosswalk**: /check-health 結果を Documentation カテゴリ findings として引用
4. **Step 4 Severity × Effort 2軸**: effort (S/M/L) を追加。Quick Wins = High severity × Low effort で抽出
5. **Step 4 Conflict Detection**: 複数エージェント間の judgement 不一致を Conflicts セクションに両論併記
6. **Step 4 Hallucination Defense**: 虚偽 line 検出 + file:line specificity 閾値（最低 1 関数 / ±10 行）
7. **Step 5 QUESTIONS.md template 拡張**: Orient Summary / Top 5 Priorities / Quick Wins / Conflicts / Non-Findings セクション追加
8. **Output Contract**: "consider refactoring" 等の根拠なし中和表現禁止
9. **Repeat-Run Tracking 軽量版**: 専用 state なし。git log -- QUESTIONS*.md で前回版を特定し NEW/RESOLVED/PERSISTING タグ付与

## 棄却

- 新規スキル `/tech-debt-audit` 作成: Pruning-First 違反、`/audit` と機能重複
- 9 dimensions 独立次元化: 8カテゴリで実用十分、`/check-health` crosswalk で documentation カバー
- Repeat-run state file: YAGNI、git で十分
- Diplomatic vagueness 禁止 哲学節: output contract に 1 行で吸収

## 効果

- 監査品質向上: Orient Gate でアーキ理解が薄い監査を防ぐ
- 再発掘防止: Non-Findings で「検討して却下」を明示
- LLM hallucination 対策: Conflict Detection + Hallucination Defense + 構造検索 pre-filter
- Quick Wins 抽出: severity × effort 2軸で実行優先度を明確化
- Documentation 観測漏れ防止: /check-health crosswalk

## 関連リンク

- 強化対象: `.config/claude/skills/audit/SKILL.md`
- 既存スキル: `/check-health`, `/dependency-auditor`, `/security-review`, `/skill-audit`
- 依拠 absorb: 2026-04-19 harness-everything (CLI --help ファースト), 2026-04-21 obsidian-claudecode (Build to Delete 実測)

## 出典

- ksimback/tech-debt-skill: https://github.com/ksimback/tech-debt-skill
- Codex 批評: agentId a11c5e5627a8790e4
- Gemini 補完: agentId aa67e67354c5e22dc
