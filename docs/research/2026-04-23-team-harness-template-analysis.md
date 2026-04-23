---
source: "claudecode-harness — Team Claude Code Harness Template (anothervibecoder-s) https://github.com/anothervibecoder-s/claudecode-harness"
date: 2026-04-23
status: integrated
---

# Team Harness Template Absorb Analysis — anothervibecoder-s/claudecode-harness

## Source Summary

**主張**: AI 支援開発でチームが成功するには、明確なロール所有権・実行境界・検証プロトコルの 3 点が必須。「CLAUDE_EXAMPLE.md」という軽量テンプレ (136 スター) で具体化されており、Hub & Spoke 構造・ゲート検証・永続メモリを組み合わせることで個人 dotfiles と同等の品質保証をチームで再現できる。

**手法**:
- Hub & Spoke CLAUDE.md: 中核 1 ファイル + spoke (rules/skills) による Progressive Disclosure
- 検証ゲート: Spec/Plan Gate (設計前) + Review Gate (実装後) の 2 段階
- 実行境界: Zone 別 OWNERSHIP.md で "誰が何に責任を持つか" を明示
- 永続メモリ: facts.md に不変知識 (tech stack / env / key decision) を集約
- セキュリティ境界: auth / payment に AI 自動修正禁止ゾーンを設定
- ML Pipeline pattern: 実験追跡・再現性確保をチームで標準化
- コンテキスト規律: session 開始時の `/recall` + 終了時の `/checkpoint` を強制

**根拠**: GitHub 136 スター、CLAUDE_EXAMPLE.md の実運用テンプレとしての採用実績。明示的なデータよりも "構造が正しい" という設計整合性で評価。

**前提条件**: Medium → Large SaaS チーム、Zone-based team 分担、modern web stack (TypeScript/Go 等)、Claude Code を全員が使用する環境。

---

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | Hub & Spoke CLAUDE.md 構造 | Already | `CLAUDE.md(130行) + references/ + rules/` の Progressive Disclosure 実装済み |
| 2 | model-routing (Codex/Gemini 委譲) | Already | `references/model-routing.md` + agent-router.py hook 実装済み |
| 3 | Spec/Plan Gate (M 規模以上) | Already | `codex:setup` + `/spec` + `/spike` ワークフローで対応 |
| 4 | Review Gate (全規模) | Already | `codex-reviewer + code-reviewer 並列` が S 規模以上で必須 |
| 5 | PLANS.md + plan lifecycle | Already | `PLANS.md` + `plan-lifecycle hook` + `completion-gate.py` 実装済み |
| 6 | ADR (Architecture Decision Records) | Already | `docs/decisions/` + `references/reversible-decisions.md` |
| 7 | session-learner / experiment tracker | Already | `scripts/learner/session-learner.py` + `experiment_tracker.py` |
| 8 | lefthook pre-commit 検証 | Already | `lefthook.yml` に polyglot pre-commit + commit-msg 実装済み |
| 9 | completion-gate (タスク完了前検証) | Already | `scripts/policy/completion-gate.py` が stop hook で動作 |
| 10 | セキュリティレビュー (auth/payment) | Already | `/security-review` skill + `agentic_security_insights.md` |
| 11 | `/recall` でセッション開始時復元 | Already | `recall` skill 実装済み |
| 12 | `/checkpoint` でセッション途中保存 | Already | `checkpoint` skill 実装済み |
| 13 | facts.md 的な不変知識集約 | Partial | `MEMORY.md` + `references/` に分散。チーム向け単一ファイルとしては未整備 |
| 14 | Zone 別 OWNERSHIP.md | N/A → Gap | 個人 dotfiles には不要。**team project テンプレとしては必要** |
| 15 | 2-sign-off ルール (機密変更) | N/A → Gap | 個人には不要。**CODEOWNERS + branch protection として team template に組み込む価値あり** |
| 16 | Timezone / 非同期コミュニケーション規律 | N/A | 個人開発環境には該当コンテキストなし |
| 17 | ML Pipeline 再現性標準化 | N/A | dotfiles ユーザーの tech stack (Go/TypeScript) と乖離 |

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | MEMORY.md (不変知識 + 学習サマリ) | チーム共有には適さない (個人 auto-memory)。新規 team member が読む "facts" が散在 | team 向け `facts.md.tpl` を templates/ に追加。個人 MEMORY.md との責務分離を明示 | 強化可能 |
| S2 | completion-gate.py (個人 hook) | team repo に Python hook をコピーする運用は維持コスト + 権限問題が大きい | CODEOWNERS + GitHub branch protection で代替。翻訳マップを `references/team-harness-patterns.md` に記載 | 強化可能 |
| S3 | `/init-project` skill | team 立ち上げ時の使い方が未定義。--team / --apply-to オプションなし | skill ドキュメントに `--team` と `--apply-to <dir>` セクションを追加 | 強化可能 |
| S4 | ADR テンプレート (`docs/decisions/`) | 個人用 ADR が team ADR テンプレとして使えるか不明確。記入例がない | base template に `0000-template.md` + variants に記入済みサンプル ADR を含める | 強化可能 |

---

## Integration Decisions

### Gap / Partial → 採用判定

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| G1 | Zone 別 OWNERSHIP.md | 採用 (team template として) | team project 立ち上げで最初に必要。dotfiles 個人 harness への組み込みは N/A だが `templates/team-project/` に同梱する価値大 |
| G2 | facts.md (team 不変知識) | 採用 (team template として) | tech stack / env / key decision の "書き始め" 痛みを下げる。個人 MEMORY.md との責務分離も明確化 |
| G3 | 2-sign-off (auth/payment) | 採用 (CODEOWNERS + branch protection 形式) | hook コピーではなく GitHub native 機構で実装。team template の `.github/CODEOWNERS.tpl` に含める |
| P1 | facts.md 的な不変知識 (Partial) | 採用 (team template として) | MEMORY.md との分離を明文化。team 向けには `docs/facts.md.tpl` を新設 |

### Gap → N/A に再判定

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| N1 | Timezone / 非同期規律 | スキップ | 個人 dotfiles での適用コンテキストなし。team template にも不要 (チーム固有運用) |
| N2 | ML Pipeline 再現性 | スキップ | tech stack 乖離 (Go/TypeScript ≠ ML)。dotfiles 汎用化の障壁になる |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | MEMORY.md → team facts.md 分離 | 採用 | template 内で個人 MEMORY.md と team facts.md の責務差を解説することで理解コスト下げる |
| S2 | completion-gate → CODEOWNERS 翻訳 | 採用 | `references/team-harness-patterns.md` に "個人 hook vs team native 機構" 対照表を載せる |
| S3 | `/init-project --team` 拡張 | 採用 | skill ドキュメント + factory agent 委譲。新 script なし (Build to Delete 原則) |
| S4 | ADR に記入例 | 採用 | variants に具体例 ADR (例: "Next.js App Router 採用理由") を含める |

---

## Plan

### Task 1: templates/team-project/base/CLAUDE.md.tpl
- **Files**: `templates/team-project/base/CLAUDE.md.tpl`
- **Changes**: team 向け CLAUDE.md テンプレ。Hub & Spoke 構造 + 最小 placeholder (PROJECT_NAME / STACK / TIMEZONE)
- **Size**: S

### Task 2: base 支援ファイル 6 本
- **Files**: `templates/team-project/base/docs/facts.md.tpl`, `docs/zones/OWNERSHIP.md.tpl`, `docs/decisions/0000-template.md`, `docs/security/auth-payment-policy.md.tpl`, `.github/CODEOWNERS.tpl`, `README.md`
- **Changes**: facts / OWNERSHIP / ADR / security zone / CODEOWNERS の最小テンプレ。placeholder はシンプルに、コメントで意図を説明
- **Size**: M

### Task 3: variants/nextjs-go-connect-gcpaws/
- **Files**: `templates/team-project/variants/nextjs-go-connect-gcpaws/` 以下 4-5 ファイル
- **Changes**: 本業 (Next.js + Go + Connect RPC + GCP/AWS) 向け差分。facts.md に実際の tech stack 記入例、ADR サンプル 1 本
- **Size**: S

### Task 4: variants/nextjs-trpc-hasura-aws/
- **Files**: `templates/team-project/variants/nextjs-trpc-hasura-aws/` 以下 4-5 ファイル
- **Changes**: 副業 (Next.js + tRPC + Hasura + AWS) 向け差分。同上
- **Size**: S

### Task 5: APPLY.md + references/team-harness-patterns.md
- **Files**: `templates/team-project/APPLY.md`, `.config/claude/references/team-harness-patterns.md`
- **Changes**: APPLY.md は `cp -R` 手順 + placeholder 置換チェックリスト。team-harness-patterns.md は個人 hook → team 機構の翻訳マップ
- **Size**: M

### Task 6: /init-project skill 拡張
- **Files**: `.config/claude/skills/init-project/SKILL.md` (編集), `references/team-templates.md` (新規)
- **Changes**: `--team` / `--apply-to <existing-dir>` セクション追加。実装は factory agent 委譲、新 script なし
- **Size**: M

### Task 7: MEMORY.md ポインタ追記
- **Files**: `.config/claude/projects/-Users-takeuchishougo-dotfiles/memory/MEMORY.md`
- **Changes**: "Team Project Templates" セクションに 1 行ポインタ + 削除条件 (2026-10-23 まで未使用で候補)
- **Size**: S

### Task 8: docs/research/2026-04-23-team-harness-template-analysis.md (本ファイル)
- **Files**: `docs/research/2026-04-23-team-harness-template-analysis.md`
- **Changes**: 本ファイル自体
- **Size**: S

### Task 9: Codex Review Gate
- **Files**: 上記全ファイル
- **Changes**: 実装完了後に codex-reviewer + code-reviewer 並列実行。L 規模ワークフロー遵守
- **Size**: M

---

## Handoff (Phase 5)

### 実装戦略

プロトタイプ先行 (ユーザー選択 A) で即日実装。年 1 回程度の使用頻度のため、完璧な spec より「使い始めやすさ」を優先する。`cp -R` 1 コマンドで立ち上げ開始できることを最低ラインとし、variants で「書き始めの痛み」を解消する。

### 最終成果物 (想定 20 ファイル)

- **新規 19 ファイル**: base 7 本 + variants 2 系統 (各 4-5 本) + APPLY.md + team-harness-patterns.md + team-templates.md
- **編集 2 ファイル**: init-project/SKILL.md + MEMORY.md

### Validation

- `task validate-configs` pass (harness contract 遵守)
- `task validate-symlinks` pass
- 手動確認: `cp -R templates/team-project/base/ /tmp/fake-team/` → placeholder 置換フローが自然か
- 思考実験: `--apply-to` フローで本業 repo (空 CLAUDE.md) への適用を通す

---

## 学び

### 外部記事の「個人 → team 翻訳」視点

本記事の分析で最も重要だったのは、初期 Gap 判定で N/A とした項目を「team project テンプレとして dotfiles に同梱する」という視点で再評価したことだ。Zone ownership / facts.md / 2-sign-off は個人 dotfiles に不要だが、「dotfiles に付属する team 向けスターターキット」としては高い価値を持つ。この翻訳先の切り替えにより、N/A の山が具体的な実装タスクへ転換された。

### ユーザー実態が template 設計を大きく変える

初期案では汎用 1 本のテンプレを検討していたが、ユーザーの「年 1 回程度の使用頻度」「本業と副業で tech stack が大きく異なる」という実態を踏まえると、汎用化よりも `base + variants 2 系統` が正解だった。placeholder 過多の汎用テンプレは書き始めの摩擦が大きく、結果として使われないリスクが高い。

### variants による concrete example の効果

ADR テンプレや facts.md を「空」で提供しても、実際に記入を始める際の「最初の 1 行」を書くコストは高い。variants に「Next.js App Router 採用理由」や「Hasura を選んだ背景」のような具体例 ADR を含めることで、この摩擦を大幅に下げられる。これは /absorb 記事の「禁止より推奨」原則の実装版とも言える。

### hook から GitHub native 機構への翻訳

個人 dotfiles の completion-gate.py は team repo に持ち込めない (権限・言語環境・維持コストの問題)。しかし「AI が auth/payment を自動修正しない」という保護目的は CODEOWNERS + branch protection で同等以上に実現できる。`references/team-harness-patterns.md` の翻訳マップがこの「個人 hook → team native 機構」のギャップを埋め、将来 team プロジェクトへ展開する際の設計判断を高速化する。

---

## 参考

- 成果物: `templates/team-project/` + `.config/claude/references/team-harness-patterns.md` + `.config/claude/skills/init-project/references/team-templates.md`
- 設計プラン: `docs/plans/completed/2026-04-23-team-harness-template-plan.md`
- 関連: `references/harness-stability.md` (削除条件 30 日ルール → 本タスクは 6 ヶ月猶予), `references/reversible-decisions.md`
