---
title: openclaw/agent-skills autoreview absorb — pending 4 tasks
created: 2026-05-28
status: pending
source: docs/research/2026-05-28-openclaw-autoreview-absorb-analysis.md
scale: M (4 tasks, mixed S+M, total ~60 min)
priority: medium (Bundle A+B 即実装済、本 Plan は保留 4 件)
related:
  - .config/claude/skills/review/SKILL.md (Bundle A+B 反映済)
  - .config/claude/agents/code-reviewer.md (Bundle A+B 反映済)
  - .config/claude/agents/security-reviewer.md (T6 対象)
  - .config/claude/agents/codex-reviewer.md (T9 対象)
  - .config/claude/skills/review/templates/synthesis-report.md (T7 対象)
  - .config/claude/skills/github-pr/SKILL.md (T8 候補)
---

# autoreview SKILL.md absorb — Pending Tasks (T6-T9)

`/absorb` で `openclaw/agent-skills autoreview SKILL.md` から得た強化候補 9 件のうち、Bundle A+B (S × 5) は 2026-05-28 セッションで即実装完了。本 Plan は **保留 4 件** (T6-T9) の実装インストラクションを保存する。別セッションで `/rpi` 経由または手動実行を推奨。

## 共通 Pre-conditions

- 全変更で Bundle A+B が既に反映されている前提 (Anti-Patterns #6/#7 / Step 5 ルール 8 / Step 1.1 mode 表 / Section H rejected-finding rule)
- 各 task は **記事 verbatim quote 引用** + **既存セクション構造との整合性** を維持
- Sonnet imagination 罠回避: Pass 2 で記事原文照合済の手法のみ採用
- 出典: openclaw/agent-skills `autoreview` SKILL.md (Peter Steinberger @steipete, OpenClaw ecosystem)

---

## T6: security-reviewer.md に Security-Audit Suppression Auditability rule (M)

### Target
`/Users/takeuchishougo/dotfiles/.config/claude/agents/security-reviewer.md`

### Insertion Point
`## Output Format` セクションの直後、または `## Codex Deep-Dive (オプション)` の前に新セクション `## Suppression Auditability` を追加。

### Verbatim Quote (記事より)
> "For security-audit suppression changes, verify accepted findings remain auditable: suppressed findings stay in structured output, active output keeps an unsuppressible suppression notice, and aggregate findings cannot hide unrelated active risk."

### 実装内容

```markdown
## Suppression Auditability

security-audit findings を suppression (除外 / 軽減 / 無効化) する変更をレビューする際は、以下 3 要件を必ず検証する。**suppression は「見えなくすること」ではなく「auditable に管理すること」が前提**。

### 必須要件 (3 つすべて)

1. **suppressed findings stay in structured output**: 抑制された finding も structured output (JSON / レポート) に残す。filter out するのではなく `suppressed: true` フラグで mark。後から audit 可能にする
2. **active output keeps an unsuppressible suppression notice**: ユーザーが見る active output (CLI stderr / summary report) には「N 件 suppression あり、詳細は structured output」という unsuppressible (= さらに抑制不可能) な notice を残す
3. **aggregate findings cannot hide unrelated active risk**: 1 つの aggregate finding (例: "lint 警告 100 件") の中に **関連しない別の active risk** (例: 認証バイパスの可能性) を埋めて隠さない。aggregate にする場合は同種類の risk のみまとめる

### 検出パターン

| パターン | 重要度 | 対処 |
|---------|--------|------|
| `nolint` / `# noqa` / `// eslint-disable-next-line` で security finding を local 抑制 + 理由コメントなし | HIGH | 理由コメント (invariant / known-safe context) を要求 |
| security tool の baseline file (`.semgrepignore` / `bandit.yml` 等) で過去 finding を bulk suppress + audit trail なし | HIGH | baseline 生成 commit + reviewer 承認の linkage を要求 |
| `severity: low` への一括 downgrade で実質 suppression、active output から消える | CRITICAL | severity downgrade rationale + reviewer sign-off を要求 |
| aggregate finding "lint: 50 件" の中に injection / auth bypass 等の異種 risk が混在 | CRITICAL | 同種類でない finding は分離して個別 report |

### Why

security 領域では「suppress = 見えなくする」ではなく「audit-friendly に管理する」が原則。
suppression が unsuppressible でないと、後から (a) review が見逃したか / (b) 後で別の reviewer が suppress を解いて再評価したか を tracking 不能になる。
aggregate hide は最も検出が難しい anti-pattern (バルク表示の中に異種 risk を埋める)。

### 出典

openclaw/agent-skills `autoreview` SKILL "For security-audit suppression changes, verify accepted findings remain auditable: suppressed findings stay in structured output, active output keeps an unsuppressible suppression notice, and aggregate findings cannot hide unrelated active risk"
```

### Scale
M (50-80 行追加、新セクション + 表 + 検出パターン)。

### Verification
- security-reviewer.md の他セクション (Output Format / Codex Deep-Dive / Common False Positives) と stylistic 整合
- OWASP Top 10 / Claude Code Ecosystem Check との内容重複なし
- `## Requires Escalation` table の Hand-off prerequisites と矛盾なし

---

## T7: synthesis-report.md template に "Tests Run" section 追加 (S)

### Target
`/Users/takeuchishougo/dotfiles/.config/claude/skills/review/templates/synthesis-report.md` (存在確認必要、無ければ skip / 新規作成判断)

### Insertion Point
`## Findings` セクションの **前** または `## Verdict` セクションの **直前** に `## Tests Run` セクション追加。`/review` Step 4.5 (Visual Output difit) と整合させる。

### Verbatim Quote (記事 Final Report 4 elements より)
> Final Report Include:
> - review command used
> - **tests/proof run**
> - findings accepted/rejected, briefly why
> - the clean review result from the final helper/review run, or why a remaining finding was consciously rejected

### 実装内容

template に以下のセクション追加:

```markdown
## Tests Run

このレビューに先立って実行されたテスト・proof の記録。
**Layer 0 Trust Verification (`references/trust-verification-policy.md`) と連携**: test 未実行 / 失敗状態でレビューを clean としない。

| Test type | Command | Status | Notes |
|-----------|---------|--------|-------|
| Unit tests | `<test command>` | ✅ pass / ❌ fail / ⚠️ skipped (理由) | 影響範囲: <変更ファイル + caller> |
| Integration tests | ... | ... | ... |
| Linter | `<lint command>` | ... | ... |
| Type check | `<type command>` | ... | ... |
| Manual proof | UI test / API call 等 | ... | ... |

- `[TESTS NOT RUN]`: テスト未実行のまま review した場合 → verdict は最低 1 段階引き下げ (`PASS` → `NEEDS_FIX`、または `[TESTS UNVERIFIED]` flag)
- `[TESTS FAILING]`: テスト失敗中 → verdict は自動的に `BLOCK` (Step 4 Synthesis ルール Layer 0 と整合)
- focused test rerun (`/review` Step 5 サイクルルール 8): fix 後の re-review では「影響テストのみ rerun」した結果をここに記録
```

### Scale
S (template に section 追加、~30 行)。

### Verification
- `/review` SKILL.md Step 4 Synthesis ルール 12 (収束停滞検出) + Layer 0 優先ルール (Trust Verification Policy) と整合
- Step 5 サイクルルール 8 (Bundle A T2 で追加した focused test rerun) と cross-reference

### Caveat
- template ファイルが既に存在しない場合は、`/review` SKILL.md の `## Skill Assets` セクションを確認 (`templates/synthesis-report.md` パス記載あり)
- 存在しない場合は task を skip し、Plan に「template 不在のため deferred」と記録

---

## T8: format → test + review 並列 step を `/review` or `/github-pr` SKILL.md に追加 (M)

### Target candidates
1. **第一候補**: `/Users/takeuchishougo/dotfiles/.config/claude/skills/github-pr/SKILL.md`
2. **第二候補**: `/Users/takeuchishougo/dotfiles/.config/claude/skills/review/SKILL.md` の Step 1.0 (新規) に追加

### Insertion Point の決定
- `github-pr` skill が「PR 作成・push・コメント対応」のワークフロー全体を扱うなら **第一候補**
- `/review` skill のスコープを「format → test + review pipeline」に拡張するなら **第二候補** (ただし scope creep のリスクあり)

### Verbatim Quote
> "Format first if formatting can change line locations. Then it is OK to run tests and review in parallel"
> "Tradeoff: tests may force code changes that stale the review. If tests or review lead to code edits, rerun the affected tests and rerun review until no accepted/actionable findings remain"

### 実装内容

新セクション or 既存セクション拡張:

```markdown
## Parallel Closeout: Format → (Tests ∥ Review)

PR commit 直前の closeout として、以下の順序で並列化する。format を先行することで line 位置を確定させ、test と review を**安全に**並列化できる。

### 実行順序

```
1. Format (must complete before test/review)
   ├─ Goal: line 位置確定 (review 後の formatting 修正は stale を生む)
   └─ Commands: <go fmt> / <prettier> / <ruff format> 等

2. Tests ∥ Review (並列)
   ├─ Tests: focused (変更ファイル + 影響 caller) を優先、full は CI に任せる
   └─ Review: `/review` または `codex-reviewer` を並列起動

3. Convergence (両方完了後)
   └─ 両方が clean なら commit、いずれかが NEEDS_FIX なら fix → rerun cycle
```

### Tradeoff (記事 verbatim)

> "tests may force code changes that stale the review. If tests or review lead to code edits, rerun the affected tests and rerun review until no accepted/actionable findings remain"

- Tests が code 変更を促した場合: 影響テスト rerun + review rerun の **二重 rerun** (`/review` Step 5 サイクルルール 8)
- Review が code 変更を促した場合: 同様に focused test rerun + review rerun
- 並列化の ROI: format が短い (~5 秒) + test/review が長い (~30 秒〜数分) の構成で最大

### Convergence Rule

- 両方 clean exit (test pass + review verdict PASS) → commit/push 可
- いずれかが NEEDS_FIX/BLOCK → fix → focused test rerun + review rerun
- 過度な rerun 防止: 最大 3 サイクル (`/review` Step 5 と同じ閾値)
- cosmetic re-review 禁止 (Anti-Pattern #7 と同じ): PASS 後の余計な再走禁止

### 出典

openclaw/agent-skills `autoreview` SKILL "Format first if formatting can change line locations. Then it is OK to run tests and review in parallel"
```

### Scale
M (新セクション 60-80 行、既存 skill 構造との整合確認必要)。

### Verification
- 第一候補なら: `github-pr` SKILL.md の commit/push 直前フローと結合
- 第二候補なら: `/review` Step 5 サイクルルール 8 と Step 4.5 Visual Output 並列化と矛盾なし

### Decision rule
実装前に第一候補 / 第二候補のどちらかを `AskUserQuestion` で確認。
迷ったら `github-pr` (第一候補) を推奨 — `/review` の scope creep 防止。

---

## T9: agents/codex-reviewer.md に cmux worker 30min SLA 明記 (弱 S)

### Target
`/Users/takeuchishougo/dotfiles/.config/claude/agents/codex-reviewer.md`

### Insertion Point
`## Workflow` セクションの末尾、または `## Requires Escalation` の `Codex CLI silent stall` 直上に新セクション `## Long-Running Review Tolerance` を追加。

### Verbatim Quote
> "Be patient with large bundles. Structured review can take up to 30 minutes while the model call is active, especially with Codex tools or web search"
> "Do not kill a review just because it has been quiet for 2-5 minutes, or because it is still running under the 30-minute window. Inspect the process only after missing multiple expected heartbeats, after 30 minutes, or after an obviously failed subprocess; prefer letting the same helper command finish"

### 実装内容

```markdown
## Long-Running Review Tolerance (cmux worker)

cmux worker 経由で Codex CLI を起動した場合の長時間運用 SLA。`xhigh` effort + 大規模 bundle で 5-30 分かかるのが正常 — 早期 kill は false positive を生む。

### Kill 判定の lower bound

以下を **すべて** 満たした時のみ Codex worker を kill する:

- (a) Heartbeat (`review still running: codex elapsed=Ns pid=P` 形式の stderr 出力) が **複数 (2 回以上)** 期待タイミングで来ない、または
- (b) Worker 起動から **30 分** 超過、または
- (c) Subprocess が **明らかに失敗** (exit code 非 0 / SIGSEGV / OOM)

**NG patterns** (これらだけでは kill しない):
- 2-5 分の静寂 (xhigh effort では reasoning に時間がかかる、normal)
- stdout が空 (`codex exec --sandbox read-only` は最終出力までバッファリングする場合あり)
- progress bar が動かない (Codex CLI は progress bar 表示しない、heartbeat が唯一の signal)

### 推奨運用

- cmux worker 起動時に `--timeout 1800` (30 分) を明示
- heartbeat を `/var/log/cmux/worker-*.log` で tail し、(a)(b)(c) の判定を automation
- 失敗時は `~/.codex/log/sessions/<session-id>` を確認、再現性ある fail は MEMORY.md `feedback_codex_casual_use.md` に追加

### 出典

openclaw/agent-skills `autoreview` SKILL "Structured review can take up to 30 minutes... Do not kill a review just because it has been quiet for 2-5 minutes, or because it is still running under the 30-minute window. Inspect the process only after missing multiple expected heartbeats, after 30 minutes, or after an obviously failed subprocess"
```

### Scale
S (新セクション 30-40 行)。

### Verification
- 既存 `## Requires Escalation` table の `Codex CLI silent stall` 条件と矛盾なし (むしろ補完: silent stall 判定の lower bound を明示化)
- cmux worker の実装 (`scripts/runtime/launch-worker.sh`) との整合 (timeout 設定の確認)

### Caveat (weak 強化)
本 task は **強化弱** — dotfiles 既存運用 (cmux worker で長時間 Codex review は実際に運用可能) は既に SLA を暗黙に許容しており、本明文化は readability 向上のみ。実装 priority は他 3 task より低い。

---

## 実装順序 (推奨)

1. **T9 (弱 S)**: codex-reviewer.md に SLA 明記 (最も影響範囲が狭く、low risk)
2. **T7 (S)**: synthesis-report.md template (file 存在確認 → 追加)
3. **T6 (M)**: security-reviewer.md に Suppression Auditability section (新 section、scope 明確)
4. **T8 (M)**: T8 の Decision rule (第一候補 / 第二候補) を `AskUserQuestion` で確認 → 実装

合計時間目安: T9 (~15 分) + T7 (~15 分) + T6 (~30 分) + T8 (~30 分 + 確認) = **~90 分**

## 別セッション実行手順

```bash
# このセッションで Plan ファイルを参照する場合
/rpi docs/plans/active/2026-05-28-autoreview-absorb-plan.md

# または手動実行
# 各 task の "Insertion Point" + "実装内容" + "Verification" に従って Edit
```

## 関連 references

- 分析レポート: `docs/research/2026-05-28-openclaw-autoreview-absorb-analysis.md`
- 出典記事: https://github.com/openclaw/agent-skills/blob/main/skills/autoreview/SKILL.md
- 既存 stack: `.config/claude/skills/review/SKILL.md` (Bundle A+B 反映済)、`.config/claude/agents/code-reviewer.md` (Bundle A+B 反映済)
- 関連 absorb (同 family): Findy code-review-graph / Google eng-practices (2026-05-24) / Cursor Team Kit (2026-05-24)
