---
title: "育てるClaude Code から 勝手に育つ Claude Code — 新陳代謝の話 (absorb)"
date: 2026-05-13
source_type: article
source_author: "@0xfene (X account, unverifiable)"
source_url: "(none; text pasted directly)"
absorb_verdict: "Reference only (content farm pattern 6件目だが副次採用 2 件)"
adopted_tasks: [T1, T2]
rejected_main_claims:
  - X 専用 CLI
  - /absorb 軽量モード
  - 月1 ritual
  - SSoT detector
  - Dreams 専用 skill
---

## Section 1: 記事の主張 (Phase 1 構造化抽出)

### 4 本柱

1. **摂取**: X 投稿 URL → 要約・タグ・スキル追記候補・新スキル草案・context メモ自動生成 (X CLI 連携前提)
2. **代謝**: 各 skill 末尾に Gotchas (過去にハマったケース) セクション + Dreams (週次パターン抽出)
3. **排泄**: 月1 で 3 問 (未使用スキル / 半年以上未更新ファイル / 処理遅延原因)
4. **体質**: SSoT (Single Source of Truth) + フロー/ストック分離

### 著者バイアス警戒

- 「マジでエグい」「ガチで衝撃」連発
- 定量データ・出典なし
- @0xfene は X account verify 不可
- Telegram/skool.com 系の content farm pattern 候補 (6 件目: Boris / Three-Model Stack / Cyril / 12-rule / zodchixquant に続く)

---

## Section 2: Gap Analysis

Pass 1 + Pass 2 は Section 3 の修正済みテーブルに統合。

---

## Section 3: Codex + Gemini 並列批評後の修正済みテーブル (Phase 2.5)

### Gap / Partial / N/A

| # | 手法 | 判定 | 修正前 | 根拠 |
|---|------|------|--------|------|
| 1a | X 専用 ingestion CLI | N/A | N/A | /absorb が URL/テキスト両対応で十分 (absorb/SKILL.md:34-43) |
| 1b | /absorb 軽量モード | N/A | Partial | Codex 棄却、KISS/YAGNI 違反 |
| 3 | 週次パターン抽出 (Dreams) | Partial | Partial | 軽量集計 (digest only) に限定。/improve 復活なし |
| 4 | 月1 ritual | N/A | Partial | scripts/runtime/skill-usage-weekly.sh:55-75 で weekly 自動化済み |
| 5 | SSoT detector | N/A | Partial | 原則は context-constitution.md:31-40 にあり、全面実装は過剰 |
| (新) | CLAUDE.md 肥大化検出 | Already | (見落とし) | claudemd-size-check.py + check-claudemd-lines.sh で実装済み (Codex 指摘) |

### Already 項目の強化分析

| # | 既存の仕組み | 判定 | 修正前 | 強化案 |
|---|-------------|------|--------|--------|
| 2 | Skill 内の failure modes 表現 | Partial | Already | skill-creator の必須項目は Hard Rules/Anti-Patterns/eval のみ。Gotchas (after-the-fact descriptive) は未明示 (Codex 修正) |
| 6 | tmp/plans, RUNNING_BRIEF, _drafts/, _index.md | Already (強化不要) | (同) | 既存の方が記事より構造化されており強化の必要なし |

---

## Section 4: 採用判定と Codex/Gemini の批評ポイント

### Codex 批評の重要な発見

- Sonnet Explore が「skill-creator が Gotchas を必須化」と誤報告 → 実際は Hard Rules/Anti-Patterns/eval のみが必須 (skill-creator/SKILL.md:64-74)
- 月1 ritual は scripts/runtime/skill-usage-weekly.sh:55-75 と重複、追加不要
- CLAUDE.md 肥大化対処は既に claudemd-size-check.py + check-claudemd-lines.sh で実装済み
- /improve は 2026-05-03 retire、R1-R3 not wired (improve-policy.md:1-11,182-190)

### Gemini 批評の重要ポイント

- @0xfene は X account verify 不可。Telegram daily-tips / skool.com 系の content farm pattern 6 件目 (Boris / Three-Model Stack / Cyril / 12-rule / zodchixquant に続く)
- Anthropic 公式 skills (google/skills, mizchi/skills) で「Gotchas 永続学習ループ」は未確認
- Dreams 概念は friction-detection-loop + daily-health-check で実装度 ~70%
- SSoT より Zettelkasten / PARA / context-engineering が知識発見性で優位
- CLAUDE.md 肥大化閾値は行数ではなく time-to-grok

---

## Section 5: 採用タスク

### T1: skill-creator rubric に Gotchas を追加 (S 規模)

- **ファイル**: `.config/claude/skills/skill-creator/SKILL.md` L73
- **変更**: Anti-Patterns 推奨の下に Gotchas 推奨を追加
- **区別**:
  - Anti-Patterns = prescriptive (design time 回避すべきパターン)
  - Gotchas = descriptive (after-the-fact、実際にハマった事例の記録)
- **理由**: skill-creator は Anti-Patterns を必須化しているが、運用後に発見される Gotchas の記録場所が明示されていない

### T2: friction-weekly-digest スクリプト (S-M 規模)

- **新規**: `.config/claude/scripts/runtime/friction-weekly-digest.sh`
- **スタイル**: skill-usage-weekly.sh 踏襲 (Inbox 出力、idempotent)
- **データソース**: `~/.claude/agent-memory/learnings/friction-events.jsonl`
- **出力先**: `$HOME/Documents/Obsidian Vault/00-Inbox/friction-weekly-${TODAY}.md`
- **LaunchAgent plist は本フェーズでは作らない理由**:
  - macOS スリープ中はスケジュール飛ぶ仕様、catch-up window が必要
  - 現状 7 events と母数が少ない → 手動実行で十分 (YAGNI)
- **初回実行確認**: 4 events in 7d, severity=info, webfetch_truncation_suspect 主体

---

## Section 6: 棄却タスクと理由

| 棄却項目 | 理由 |
|---------|------|
| X 専用 ingestion CLI | /absorb が URL/テキスト両対応で十分 (absorb/SKILL.md:34-43) |
| /absorb 軽量モード | KISS/YAGNI、現行で十分 |
| 月1 ritual playbook | scripts/runtime/skill-usage-weekly.sh:55-75 + skill-health LaunchAgent で既に自動化 |
| SSoT detector 全面実装 | 原則は context-constitution.md にあり、検出機構は過剰 |
| Dreams 専用 skill 新設 | friction-detection-loop + retrospective-codify で実装済み (実装度 ~70%)、新 skill は scope creep |

---

## Section 7: 教訓 (Lessons learned)

1. **content farm pattern 6 件目 (@0xfene)**: 著者バイアス強・定量根拠なし・集客誘導疑惑あり。Boris / Three-Model Stack / Cyril / 12-rule / zodchixquant に続くパターン。

2. **zodchixquant 教訓の適用**: 著者バイアスで全棄却せず、Codex 並列批評で副次採用 2 件 (T1/T2) を救出。記事 Reject でも批評過程で価値抽出が可能。

3. **Sonnet Explore の Pass 1 誤報告を Codex 深推論が修正**: skill-creator の Gotchas 必須化は誤情報。Phase 2.5 の Codex 深推論ステップの必須性を再確認。

4. **LaunchAgent 化判断の原則**: macOS スリープ中はスケジュール飛ぶ仕様。catch-up window が必要になる + 母数が少ない場合は手動実行で十分。自動化は母数と重要度が閾値を超えてから。

---

## Section 8: 関連参照

- `references/web-fetch-policy.md` — friction-events 記録経路
- `references/context-constitution.md` — P4: Memory="what", Skill="how" (SSoT 原則の在処)
- `references/improve-policy.md` — /improve retire 経緯
- `scripts/runtime/skill-usage-weekly.sh` — T2 スタイル踏襲元
- `scripts/policy/claudemd-size-check.py` — CLAUDE.md 肥大化検出 (Already 実装)
- 過去の content farm pattern absorb:
  - `docs/research/2026-04-30-boris-30tips-absorb-analysis.md`
  - `docs/research/2026-05-10-12-rule-claude-md-absorb-analysis.md`
  - `docs/research/2026-05-10-zodchixquant-15-settings-absorb-analysis.md`
