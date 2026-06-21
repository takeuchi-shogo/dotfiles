---
source: "Automating SKILL.md Generation for Computer-Using Agents via Interaction Trajectory Mining (arXiv:2606.20363)"
date: 2026-06-20
status: analyzed
adoption: validation-only-followup
family: trajectory→skill mining / self-improving skill loop
phase_25: skipped (negative-result diagnostic + Opus bias correction value low)
---

## Source Summary

**Title:** Automating SKILL.md Generation for Computer-Using Agents via Interaction Trajectory Mining
**Authors:** Yuexing Hao, Xiaomin Li
**Submitted:** 2026-06-18 (arXiv:2606.20363 v1, cs.AI)

**主張**: GUI trajectory から skill library を自動抽出する 3 段階パイプライン (segment→cluster→GRPO 訓練) を構築。クラスタの readability は出る (5/8 ≥ 0.95 purity vs InteraSkill Workflows ラベル) が、cross-domain policy transfer は失敗する (GRPO 18.5%→20.5%、BrowseComp+ ほぼ不変、trivial frequency prior を下回るメトリクスあり)。著者自身が "diagnostic study" と framing し、boundary detector / orderless segment representation / offline reward model の 3 つを失敗主因と特定。

**手法**:
1. Trajectory segmentation (GUI trace の意味境界分割)
2. Segment clustering (候補 skill としてクラスタリング)
3. Skill-aware policy training via GRPO

**根拠**: InteraSkill Workflows + BrowseComp+ ベンチマーク。論文自報の transfer 失敗 (1.5pp 改善のみ、trivial prior 以下のメトリクスあり)。

**前提条件**: GUI CUA / 学習可能な model weights / trajectory データ収集インフラ / offline reward model 構築。

## Phase 1.5 Saturation Gate

**Family**: trajectory→skill mining / self-improving skill loop
**N**: 10+ (直近 3 ヶ月で直接競合 5 件以上)
**判定**: 形式的に PASS (warning) (採用率 >= 20%)、ユーザー選択で continue → フル workflow 実行

### per-method 照合台帳 (全 current 手法 → matched_prior 名指し)

| current 手法 | verdict | matched_prior (3点セット) |
|--------------|---------|---------------------------|
| Trajectory segmentation | **rehash** | `2026-03-14-trajectory-informed-memory.md` "IBM Tips 自動抽出" — trajectory を意味境界で discrete unit 化し帰納的抽出する点で目的・粒度同一 |
| Segment clustering | **rehash** | `2026-03-26-memcollab-contrastive-trajectory-distillation-analysis.md` "Contrastive Trajectory Distillation" + `2026-04-02-glean-trace-learning-analysis.md` "Multi-trace 合意検証" — trajectory 集約からの帰納的パターン抽出として同等 (本論文は単純クラスタリングで対比版より弱い) |
| Skill-aware policy training (GRPO) | **N/A (out-of-scope)** | Claude API は重み access 不可、LLM fine-tuning 不可能。dotfiles の skill 体系はテキスト SKILL.md で RL policy ではない (structural scope mismatch)。dotfiles の `rl_advantage.py` は variant selection 用 (skill-audit/k-variant-testing) であり論文と別用途 |

**delta** = 0 (rehash 2 + N/A 1 = 採用検証対象 0)

## Phase 2 Pass 1 (Sonnet Explore) 結果

| キーワード | 存在判定 | 主要ファイル | 備考 |
|------------|----------|--------------|------|
| Trajectory segmentation / session event | **exists** | `session-learner.py` / `session-trace-store.py` (no-op'd 2026-06-05) / `session_events.py` | 稼働中 (trace-store は退役待ち) |
| Segment clustering | **exists** | `failure-clusterer.py` (FM-code) / `extract-promotion-candidates.py` / `cross-domain-mapper.py` (no-op'd) | FM-code clustering 稼働 |
| GRPO / RL training | **exists (別用途)** | `rl_advantage.py` / `skill-audit/k-variant-testing.md` | variant selection 用、weight fine-tuning ではない |
| Boundary detector | **exists** | `_detect_critical_failure_step()` in session-learner / `contrastive-trace-analyzer.py` (no-op'd) | CFS 検出は稼働 |
| patterns.jsonl / Wave3 | **partial** | `promote-learnings` / `auto-triage` / `calibration-verdict-logger.py` | Wave3 は calibration 進行中、mechanical 未出現 |

## Phase 2 Pass 2 (Opus 強化判断)

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Trajectory segmentation | **Already (強化不要)** | session-learner / session_events で稼働。論文の "boundary detector insufficient" は dotfiles の境界検出シンプル化 (CFS のみ) 方針を validate |
| 2 | Segment clustering | **Already (強化不要)** | failure-clusterer (FM-code) が稼働。論文の "orderless segment representation insufficient" は clustering 強化方向が誤りであることを academic に裏付け |
| 3 | Skill-aware GRPO policy | **N/A** | Claude API は重み access 不可、RL fine-tuning 構造的に不可能 |
| 4 | Diagnostic finding: 3 failure modes | **Gap → Validation-only follow-up** | 論文唯一の novel 貢献。dotfiles の patterns.jsonl→Wave3 YAGNI (2026-06-06 sonicgarden) を academic に裏付け |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|-------------|--------------|--------|------|
| S1 | failure-clusterer (FM-code grouping) | orderless segment representation は cross-domain 転移失敗の主因 | **強化方向に進まない** memo (auto-triage Wave3 calibration 再開時の "再注意 failure mode" 保存) | 強化不要 (静観) |
| S2 | patterns.jsonl→/promote-learnings (manual triage) | trajectory mining は readable structure を出すが transfer failure | academic 裏付けを family lesson に追記 | 強化可能 (Validation-only) |

## Phase 2.5 — skip

ユーザー判断で Phase 2.5 (Codex + Gemini 並列批評) は skip。理由:
- 論文が明示的 negative-result diagnostic study として self-disclose 済
- dotfiles 側で独立に Wave3 YAGNI 判定済 (sonicgarden 2026-06-06)
- Sonnet Explore で既存 mechanism の no-op 状態を実ファイルで確認済
- Codex cmux Worker stall リスク + Gemini 周辺知識補完の drift 露出余地小

## Integration Decisions (Phase 3)

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | 新規 mechanism 採用 | **採用 0** | 全 3 手法 rehash or N/A、論文結果も weak (1.5pp) |

### Already 強化 / Validation-only follow-up

| # | 項目 | 判定 | 採用先 |
|---|------|------|--------|
| V1 | MEMORY.md "改善ループ" sonicgarden 行に academic 裏付け追記 | 採用 | `~/.claude/projects/.../memory/MEMORY.md` |
| V2 | auto-triage skill に "再注意 failure mode" memo (3 failure modes) | 採用 | `.config/claude/skills/auto-triage/SKILL.md` |
| V3 | docs/research/_index.md に 1 行索引追記 | 採用 | `docs/research/_index.md` |

## Plan (Phase 4)

### Task V1: MEMORY.md "改善ループ" に academic 裏付け追記 (S)
- **File**: `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md`
- **Change**: 改善ループ section に新規 bullet 1 行追加 (arXiv:2606.20363 academic 裏付け参照)

### Task V2: auto-triage skill に "再注意 failure mode" memo (S)
- **File**: `.config/claude/skills/auto-triage/SKILL.md`
- **Change**: "calibration 実測" の後ろに "Wave3 再開時の再注意 failure mode" 短節を追加 (3 failure modes 引用)

### Task V3: docs/research/_index.md に索引追記 (S)
- **File**: `docs/research/_index.md`
- **Change**: ハーネス理論セクションに 1 行追加 (本レポートへのリンク)

### Task V4: docs/wiki/log.md 追記 (S)
- **File**: `docs/wiki/log.md`
- **Change**: ingest エントリ追加

## Lessons / 教訓

- **negative-result paper も Validation-only 価値あり**: 自報失敗論文は dotfiles の独立 YAGNI 判定への academic backing として機能。採用 0 ≠ 終了
- **family 飽和 ≠ skip 即決**: 形式的 PASS (warning) でユーザー判断 continue → per-method 照合台帳で実質 delta=0 確認 → 適切なところに pruning 落ち
- **scope translation の徹底**: GUI CUA / RL fine-tuning 前提の論文を dotfiles (CLI / Claude API frozen) に持ち込まない判断は Phase 1.5 で済むため Phase 2.5 (高コスト) の節約余地あり
