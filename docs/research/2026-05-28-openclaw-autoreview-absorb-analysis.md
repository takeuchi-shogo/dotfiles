---
date: 2026-05-28
source_url: https://raw.githubusercontent.com/openclaw/agent-skills/main/skills/autoreview/SKILL.md
source_title: openclaw/agent-skills autoreview SKILL.md
author: Peter Steinberger (@steipete)
ecosystem: OpenClaw (openclaw + agent-scripts)
topic_family: code-review-best-practices (5 件目, saturated)
status: adopted-bundle-a-b-plus-pending
adoption_count: 5 即実装 + 4 plan 保留
codex_phase25: failed-both-routes (cmux worker TTY + codex exec 0-byte stall)
gemini_grounding: completed (5 主張全 HIGH 確認)
---

# OpenClaw autoreview SKILL.md 取り込み分析

## 1. Source Summary

### 主訴
PR land 前の最終 closeout として helper script で 1-engine/1-bundle の構造化レビューを実行し、Codex を default engine とする。レビューは advisory として扱い、accepted/actionable findings がゼロになるまで loop する。長時間 (~30 分) の review SLA を受容し、heartbeat で生存通知することで kill されないようにする。fix 後は focused test と review の二重 rerun を必須化、PASS exit を得た後の cosmetic 再実行は明示的に禁止する。

### 手法 (35 個抽出)
- **Helper script bundle**: 1 helper が 1 bundle を組み、1 engine を呼び、1 structured result を validate して stop
- **Heartbeat 耐性**: 2-5 分の沈黙では kill しない (helper が heartbeat 出力)
- **No-nested-review**: review の中から built-in codex review / nested reviewers / reviewer panels を起動しない
- **Panel opt-in**: panel は explicit に opt-in が必要、default は single engine
- **Regression provenance 5 要素**: regression の起源を 5 軸 (PR ID / commit SHA / file / line / author) で記録
- **automerge bot trigger 追跡**: clawsweeper[bot] 等の trigger 経路をログ化
- **gitcrawl health check**: `doctor --json` で portable cache 修復
- **Parallel closeout**: format → (test, review) parallel
- **Mode 自動分岐**: clean local diff / staged-only / branch-diff の自動判別
- **30 min SLA**: deep audit を許容、capacity retry で engine override 禁止
- **Suppression auditability**: security-audit suppression は structured output に保存、active 出力にも notice、aggregate で隠蔽不能
- **Final report 4 elements**: command / tests / findings / clean
- **PASS-exit lock**: 0 exit 後の cosmetic 再 review を明示禁止
- **Twin-rerun**: review-triggered fix で code 変更があれば focused test + structured review helper を両方 rerun
- **Inline-comment 厳格化**: rejected finding でも real invariant / ownership 説明時のみ inline code comment を追加
- **Clean-local caveat**: clean local review は「no local patch」のみ証明、no remote risk は別途検証
- **crabbox.sh isolation**: 30 min autoreview の test rerun のため remote VM lease する isolated execution environment
- (他 18 件は記事 verbatim verbatim 中の派生ルール)

### 前提条件
- **openclaw/agent-scripts ecosystem**: gitcrawl (GitHub metadata cache) + clawsweeper[bot] (2-lane Review/Apply) + crabbox.sh (VM lease)
- **Multi-engine CLI**: Codex / Claude / droid / copilot CLI
- **長時間レビュー受容**: 最大 30 分の deep audit ワークフロー
- **WebSearch/WebFetch 常時 enable**: harness-wide で許可

### 根拠
- 著者 @steipete の経験的主張: "most impactful skill I've added"、"Finds so many edge cases"
- Gemini grounding 確認: openclaw ecosystem (gitcrawl / clawsweeper / crabbox) の 5 主張すべて HIGH 信頼度で実在性確認
- 30 min SLA は Anthropic Review Gate default 15 min / GitHub Copilot 数秒との対比で deep audit trade-off と位置づけ

---

## 2. Phase 1.5 Saturation Gate

### Family 確認
- **topic_family**: code-review-best-practices
- **既往 absorb 履歴**:
  1. Findy code-review-graph
  2. Google eng-practices (13 件採用)
  3. Cursor Team Kit Thermo-Nuclear Review (3 件採用)
  4. (派生) Code Review Discipline 関連
  5. **本記事** (5 件目)

### 採用率
- Google eng-practices で 13 件採用 → 採用率 >> 20% (閾値超過)

### 判定
- **PASS (warning)** — 重複領域だが novel 角度あり:
  - Helper script bundle (1-engine/1-bundle/1-result の atomic gate)
  - Panel opt-in (default single engine)
  - gitcrawl ecosystem (portable cache + doctor)
  - automerge bot trigger 追跡
  - 30 min SLA + heartbeat 耐性
  - Suppression auditability (security-audit suppression の hide-prevention)

### Step 7 Stale-Plan Audit
- 直近 3 件 (Google eng-practices / Cursor / Findy) は全て 30 日未満 → **skip**

---

## 3. Phase 2 Analysis Table

20 キーワード調査の Pass 1 + Pass 2 統合、Phase 2.5 修正反映済み。

### Gap / Partial / N/A

| # | 手法 (verbatim quote) | 最終判定 | 強化案 |
|---|----------------------|---------|--------|
| 11 | "Stop as soon as the helper exits 0 with no accepted/actionable findings. Do not run an extra review just to get a nicer clean line, a second opinion, or clearer closeout wording" | **Gap** | `/review` Anti-Patterns に 1 行追加 |
| 9 | "If a review-triggered fix changes code, rerun focused tests and rerun the structured review helper" | **Gap** | Step 5 サイクルルールに 1 行追加 |
| 5 | "Do not invoke built-in codex review, nested reviewers, or reviewer panels from inside the review. The helper builds one bundle, calls one selected engine, validates one structured result, and stops" | **Partial** | Anti-Patterns に explicit ban 追加 (既存は "Skill 直起動禁止" のみ) |
| 17 | "A clean local review only proves there is no local patch" | **Partial** | Step 1 に diff scope mode 表 + clean-local caveat |
| 18 | "add a brief inline code comment only when it explains a real invariant or ownership decision" | **Gap** | `code-reviewer.md` Section A 派生で新 rule |
| 15 | "For security-audit suppression changes... suppressed findings stay in structured output, active output keeps an unsuppressible suppression notice, and aggregate findings cannot hide unrelated active risk" | **Gap** | `security-reviewer.md` に新 section |
| 10 | Final report 4 elements (command / tests / findings / clean) | **Partial** | `synthesis-report.md` template に Tests Run section |
| 8 | "Format first if formatting can change line locations. Then it is OK to run tests and review in parallel" | **Partial** | `/review` or `/github-pr` SKILL.md に format → test+review 並列 step |
| 3 | "Structured review can take up to 30 minutes... Do not kill a review just because it has been quiet for 2-5 minutes" | **Partial → Already (cmux 既存運用で実質カバー)** | `codex-reviewer.md` に SLA 文言追加 (弱) |
| 2 | engine override 禁止 + capacity retry | **Already (強化不要)** | `codex-reviewer.md` Self-preference Bias 対策で異モデル必須 + memory 遮断強制済 |
| 13 | regression provenance 5-split | **N/A (降格)** | dotfiles に automerge bot ecosystem なし、git blame ad-hoc で十分 |
| 1, 6, 14, 16, 19, 20 | various | **N/A** | dotfiles 文脈と不一致 / multi-script で equivalent / 既存代替あり |

### Already (強化不要)

| # | 既存実装 | 理由 |
|---|---------|------|
| 4 | WebSearch / WebFetch harness-wide enable | settings.json 既設定済 |
| 7 | `gh pr view --json baseRefName` 実装済 (`prepare-pr-review.sh`) | branch base 自動判別済 |
| 12 | git push permission deny + read-only tools | 技術的 block 済 |

---

## 4. Phase 2.5 Refine

### Codex 経路: 両方失敗

**BG 1 回目 (cmux worker)**:
- Command: `scripts/runtime/launch-worker.sh --model codex --task ...`
- Error: `Surface is not a terminal`
- 原因: TTY 不在 — subagent context での launch-worker.sh codex case は TTY 必須

**BG 2 回目 (codex exec read-only)**:
- Command: `codex exec --sandbox read-only -m gpt-5.5 --config model_reasoning_effort=xhigh`
- Error: 0 byte stall (silent fail)
- 原因: xhigh + 大規模 prompt で silent fail
- 既知パターン: MEMORY.md `feedback_codex_casual_use.md` に蓄積済

### Gemini grounding 結果 (5 主張全 HIGH 確認)

1. **openclaw/agent-skills 実在**: Peter Steinberger (@steipete) が中心 architect、autoreview は ecosystem の中核 skill
2. **autoreview pattern**: 1-engine/1-bundle/1-result は OpenClaw philosophy の hallmark。Qodo PR-Agent / Kodus と差別化 (atomic gate の徹底)
3. **30 min SLA**: Anthropic Review Gate default 15 min、GitHub Copilot 数秒、autoreview は deep audit trade-off の極致
4. **clawsweeper[bot]**: 2-lane (Review Lane + Apply Lane)、conservative な merge policy
5. **gitcrawl**: GitHub metadata → SQLite キャッシュ、`doctor --json` で portable cache 修復、zero-network mode 対応

### 追加 insight (Phase 2 で未反映)

- **Token consumption**: 30 min Codex review = 500k-1M tokens/run → small team には cost-prohibitive
- **Maintenance debt**: helper scripts は GitHub API 変更で frequent update 必要
- **Multi-engine parity**: Codex / Claude / GPT-5 で結果不一致 → SOUL / PROMPT tuning 必要
- **crabbox.sh**: 30 min autoreview の test rerun のため remote VM lease する isolated execution environment

### Opus self-critique (Sonnet imagination 補正)

- **#2 訂正**: Sonnet Explore が `codex-reviewer.md` Self-preference Bias 対策 (異モデル必須 + memory 遮断) を見逃していた → **Already に修正**
- **#5 再評価**: Sonnet が `/review` Anti-Patterns 既存 1 項目を見逃していた → **Partial に修正** (nested ban の文言は既存無し)
- 各強化候補は記事 verbatim quote で照合済、Sonnet imagination 罠回避

---

## 5. Phase 3 Triage 結果

ユーザー回答: **Bundle A+B+保留 9 件全採用** (max adoption)

- Bundle A (S × 3, 即実装) → ✅
- Bundle B (S × 2, 即実装) → ✅
- 保留 4 件 (M+S) → `docs/plans/active/2026-05-28-autoreview-absorb-plan.md` に保存、別セッション /rpi 推奨

---

## 6. Adoption Plan

### Bundle A (S × 3, 即実装)

| Task | Target | Change |
|------|--------|--------|
| **T1** | `/review` SKILL.md Anti-Patterns table | "PASS exit 後の cosmetic 再 review 禁止" 行を追加。verbatim: "Stop as soon as the helper exits 0... Do not run an extra review just to get a nicer clean line" |
| **T2** | `/review` SKILL.md Step 5 サイクルルール | "fix→focused test rerun + review rerun の二重 rerun" を追加。verbatim: "rerun focused tests and rerun the structured review helper" |
| **T3** | `/review` SKILL.md Anti-Patterns table | "review 中の nested reviewer / panel 起動禁止" を追加。verbatim: "Do not invoke built-in codex review, nested reviewers, or reviewer panels from inside the review" |

### Bundle B (S × 2, 即実装)

| Task | Target | Change |
|------|--------|--------|
| **T4** | `/review` SKILL.md Step 1 | diff scope mode 表 (clean local / staged / branch-diff) + "A clean local review only proves there is no local patch" caveat |
| **T5** | `agents/code-reviewer.md` Section A 派生 | "rejected finding は real invariant / ownership 説明時のみ inline comment" 追加。verbatim: "add a brief inline code comment only when it explains a real invariant or ownership decision" |

### 保留 4 件 (M+S, 別セッション /rpi 推奨)

| Task | Target | Size | Detail |
|------|--------|------|--------|
| **T6** | `agents/security-reviewer.md` | M | security-audit suppression auditability rule (suppressed findings は structured output 保持 + active output に notice + aggregate hide-prevention) |
| **T7** | `templates/synthesis-report.md` | S | "Tests Run" section 追加 (4-element final report: command / tests / findings / clean) |
| **T8** | `/review` または `/github-pr` SKILL.md | M | format → test+review 並列 step (順序: format first if line locations can change, then parallel) |
| **T9** | `agents/codex-reviewer.md` | 弱 S | 「cmux worker 30 min まで kill しない」SLA 明記 (heartbeat 耐性) |

Plan ファイル: `docs/plans/active/2026-05-28-autoreview-absorb-plan.md` (T6-T9 詳細実装インストラクション)

---

## 7. Validation-only Follow-up

- なし (記事は dotfiles 内 stale fact を露出しなかった)

---

## 8. Metadata

| 項目 | 値 |
|------|-----|
| 分析時間 | ~45 分 |
| Phase 2 委譲 | Sonnet Explore (1 回、20 キーワード調査) |
| Phase 2.5 | Codex 両ルート失敗 + Gemini grounding 成功 |
| Phase 3 | AskUserQuestion 2 件 |
| saturation | SATURATED-but-novel (delta 高、5 件目だが helper script bundle / 30min SLA / suppression auditability 等の novel 角度あり) |
| 採用 | 5 即実装 + 4 plan 保留 |
| 棄却 | 7 件 (#1/6/13/14/16/19/20 N/A + #2 Already 強化不要) |

---

## 9. メタ学習 (次回 absorb へ)

- **Codex 両ルート失敗 → Gemini 単独で Phase 2.5 完了**: cmux worker TTY 不在 + codex exec xhigh 0-byte stall の組合せで両方 fail。Gemini grounding が code-review-best-practices family 5 件目の bias mitigation を単独で達成
- **Sonnet imagination 罠 (5 件目連続)**: Phase 2 で Sonnet Explore が `codex-reviewer.md` の Self-preference Bias 対策と `/review` Anti-Patterns 既存項目を見逃した → Opus self-critique で訂正。`/absorb` Step 3.7 の verbatim 照合は今後も必須
- **5 件目 PASS-warning で novel 9 件**: saturation gate を強引に通すべきではなかったか? → helper script bundle / 30min SLA / suppression auditability の 3 軸は実質的に novel domain (review pipeline mechanics vs. review content). family 名を `code-review-best-practices` から `code-review-pipeline-mechanics` に分離する余地あり (次回検討)
