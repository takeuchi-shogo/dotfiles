---
title: "leopardracer『I Gave My Second Brain 1,500 Conversations』+ AgriciDaniel claude-obsidian plugin — absorb analysis"
date: 2026-07-05
status: analyzed
adopt_count: 3
family: obsidian-second-brain
family_entry: 21
author: "@leopardracer (X/Substack)"
prior_absorb_count: 20 (obsidian-second-brain family absorb reports) + nemocake grill (2026-06-28, 非採用)
verdict: Adopt 3 件 (T1 orphan-artifact-scan / T2 行動観測 profile 検証 / T3 Claude.ai export→memory-vec)
---

## Source Summary

**主張**: 記事は 2 部構成。(1) X 投稿 — AgriciDaniel/claude-obsidian plugin (`/wiki` コマンドで LLM が維持する wiki を Obsidian に構築)。(2) leopardracer 本編 — Claude.ai 会話 1,391 件 + Claude Code セッション 138 件 + 記事 238 本を export し、tool-noise を除去して clean note 化。Karpathy 式 living wiki (one page per topic) を Obsidian に構築し、実会話からの real quotes で心理プロファイル (Leo-Psychology) を生成。4 種の角度別 agent (Post/Build/Stoic/Note) が 6 時間ごとに wiki write-back と提案生成を行い、接続は 1 件ずつ人間承認後に自動化する approval-gated 運用。提案は収益・エンゲージメント統計で根拠付けする。

**手法**:
- claude-obsidian plugin (`/wiki` コマンドで LLM 維持 wiki)
- living wiki (one page per topic)
- write-back loop (良い Q&A を wiki に戻す)
- approval-gated wiring (新規接続は 1 件ずつ人間承認)
- 定期実行 (6 時間ごとの cron)
- Claude.ai 会話 export → clean note 化 (tool-noise 除去)
- tool-noise 除去の前処理規約
- 心理プロファイルページ (real quotes 抽出)
- 角度別 4 agent (Post/Build/Stoic/Note)
- プライバシー exclude フィルタ (「迷ったら drop」)
- 実績データ grounding (収益/エンゲージメント統計で提案を根拠付け)
- Claude Code セッションマイニング (built-but-never-shipped 検出)

**根拠**: 著者自身の運用実績 (Claude.ai 1,391 会話 + Claude Code 138 セッション + 記事 238 本の実 export、6 時間ごとの実行ログ)。creator-monetization 系の一次体験談で第三者検証データなし。

**前提条件**: Substack/X での収益化を主目的とするクリエイターの個人運用。Web (Claude.ai) が主要作業場という前提、コーディング特化ハーネスとは職務・作業媒体が異なる。取得経路: テキスト直貼り (fetch なし)。

## Phase 1.5 Saturation Gate

- Family: obsidian-second-brain 21 件目 (キーワード hit: obsidian / second brain / vault / wiki)
- 形式判定 PASS (warning): N=20、採用率 ≈ 40% (8/20)。ただし採用の実体は 2026-03〜04 の integrated 5 件 + 2026-05 の S 規模 3 件に集中しており、直近 2 接触 (2026-05-31 delete-90 採用 0、2026-06-28 nemocake grill 非採用) は連続非採用 → 形式判定と直近トレンドが割れたため AskUserQuestion で明示判断を仰ぎ、**user は continue (フル workflow) を選択**
- Stale-Plan Audit (Step 7) 実施: organize-vault (2026-05-25) と notes-into-output (2026-05-30) の採用タスクを grep で実在検証し、frontmatter を `status: implemented` に更新済み (`check_rare_tags()`/`check_naming_compliance()` @ `vault-maintenance.sh:219,293`、Decision Feeder @ `obsidian-knowledge` SKILL.md + `capture.md`)。delete-90 (2026-05-31) は採用 0 のため audit 対象外

## per-method 照合台帳 (Phase 1.5、全 12 手法)

| # | current 手法 | verdict | matched_prior |
|---|---|---|---|
| 1 | claude-obsidian plugin (`/wiki`) | rehash | `2026-04-07-karpathy-kb-pattern-deep-analysis.md` "Case 1.1a: dotfiles リポジトリ" — dotfiles 自身が `docs/wiki` + `/compile-wiki` で同パターン実装済み、plugin は配布形態違いのみ |
| 2 | living wiki (one page per topic) | rehash | 同レポート "Pattern: ほぼ完全に実装、Scale: ~400 concept pages" |
| 3 | write-back loop | rehash | 同レポート "Case 1.2b: Filing Loop — 『良い Q&A を Wiki に戻す』フィードバック・ループ" (Lint 必須のリスク込みで既出) |
| 4 | approval-gated wiring | rehash | 同レポート "Human-in-the-Loop: すべての新規ページ・更新を人間が review" (粒度差のみ) |
| 5 | 定期実行 (6h cron) | rehash | `2026-04-14-hermes-personal-analyst-analysis.md` "Daily Briefing Automation" + `auto-morning-briefing.sh` 稼働、`2026-06-17-hermes-vps-24-7-os` "3 crons" |
| 6 | Claude.ai 会話 export → clean note 化 | novel | — (直近 7 レポート横断で該当なし) |
| 7 | tool-noise 除去の前処理規約 | ambiguous | #6 の従属手法、単独では novel 判定不可 |
| 8 | 心理プロファイルページ (real quotes 抽出) | ambiguous | 最近接 `2026-05-23-damidefi-...` "vault root CLAUDE.md (Thinking Style)" だが心理プロファイル明記なし |
| 9 | 角度別 4 agent (Post/Build/Stoic/Note) | ambiguous | 最近接 `2026-06-17-hermes-vps` "profiles = specialist team + model routing" だが自己分析レンズ構成は未出 |
| 10 | プライバシー exclude フィルタ | novel | — |
| 11 | 実績データ grounding (収益統計) | novel | — (dotfiles に該当データなし) |
| 12 | Claude Code セッションマイニング (built-but-never-shipped) | ambiguous | 改善ループ family に trajectory mining あるが本 family prior に名指し不可 |

delta = 7 (novel 3 + ambiguous 4)、rehash 5 件は引用句付きで立証。

## Phase 2 判定テーブル (Pass 1 Sonnet Explore + Pass 2 Opus)

### Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 6 | Claude.ai export 取り込み | Gap (条件付き・低優先) | 処理機構なし。価値は web 利用量次第。consumer は memory-vec recall hook (PR #139) に接続可能 |
| 7 | 会話 clean note 化 | N/A | session-learner → patterns.jsonl が消費者付きで稼働。人間可読 note は observe ログ死蔵 decommission (2026-06-05) と同じ轍を踏むリスク |
| 9 | 角度別 4 agent | N/A | Post/Note/Stoic は creator-monetization 前提 (Substack/X 収益) で dotfiles と不一致。Build lens は #12 へ統合 |
| 12 | セッションマイニング (未 ship 検出) | Partial | 学び抽出 (session-learner → patterns.jsonl → promote) は稼働。孤児 worktree/branch/未コミット作業の定期検出は未整備 (2026-06-06 に worktree 26 個 + 孤児ブランチ 19 個を手動掃除した実績 pain) |

### Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| 8 | user_* memory (`/onboarding`, `/profile-drip` = 自己申告ベース) | 自己申告は行動実態を捉えない。記事は実会話から real quotes で行動観測プロファイルを構築 | 1 回限り: transcript サンプルから行動観測で user_* を検証、差分のみ追記 | 強化可能 |
| 1-5, 10, 11 | `compile-wiki` / wiki concepts 41 件 / `log.md` write-back / auto-accept-policy / launchd + nightly 11 jobs / `.claudeignore` + memory scopes / observability-signals | — | — | 強化不要 (write-back の全 agent 拡大は compounding error リスクで意図的非採用) |

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 6 | Claude.ai export → memory-vec intake | 採用 (M) | web 利用量とは独立に memory-vec ソース拡充として価値あり、consumer (recall hook PR #139) 接続済み経路に乗せられる |
| 7 | 会話 clean note 化 | スキップ | observe ログ死蔵と同型リスク、人間可読 note の消費者なし |
| 9 | 角度別 4 agent | スキップ | creator-monetization 前提が dotfiles と不一致、Build lens は #12 に統合済み |
| 12 | orphan-artifact-scan (未 ship 検出) | 採用 (S) | 2026-06-06 の worktree/branch 手動掃除 pain の再発防止、既存 nightly orchestrator に接続可能 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 8 | 行動観測 profile 検証 | 採用 (S、運用タスク) | 自己申告バイアス補正は低コストで実行可能、real quotes による裏付けは差分追記のみで安全 |

## Phase 2.5 Refine

- **Codex (gpt-5.5, `codex exec --sandbox read-only` fallback — cmux 不在で `launch-worker.sh` exit 1)**: 判定変更なし・優先度確定。(1) 見落とし指摘: wiki 腐敗管理/重複統合/rollback/提案効果測定 → dotfiles では `/compile-wiki` lint + doc-gardener + `proposal-verdicts.jsonl` が既カバー。(2) Gap 過大評価の疑い: Claude.ai export は web が主要作業場でない限り低優先、clean note 化は再死蔵リスク → 判定支持 (変更なし)。(3) Already 過小評価の疑い: 差分は基盤でなく品質ループの話であり、improve-policy 閾値 + `proposal-verdicts` で既カバー → 変更なし。(4) 前提不一致の指摘: 収益統計より未 ship 成果物/失敗パターン/validation evidence の方が dotfiles では意思決定価値が高い。(5) 優先度確定: #12 最優先 (実績 pain + 既存 harness 接続) > #8 > #6 (consumer 確認後)
- **Gemini: 未取得 (degraded)** — `gemini -p` が IneligibleTierError (Code Assist for individuals sunset、2026-07-05 再確認)。`feedback_gemini_cli_sunset.md` の既知事象どおり。model-family diversity は Codex 単独で部分達成、周辺知識補完 (類似手法の成功/失敗事例・代替アプローチ) は未取得と明記する

## Phase 3 Triage

user 選択: **3 件全て採用** (#12 / #8 / #6)

## Plan

### Task 1: orphan-artifact-scan
- **Files**: `.config/claude/scripts/lifecycle/orphan-artifact-scan.sh` (新規)、`tools/nightly-orchestrator/jobs.yaml` (job 追加)
- **Changes**: stale worktree / merged・gone ブランチ / worktree 内未コミット変更を検出するスクリプトを新設し、nightly orchestrator の job として登録。worktree + PR 運用下での 2026-06-06 型の手動掃除 pain を再発防止する
- **Size**: S
- **依存**: なし

### Task 2: 行動観測 profile 検証
- **Files**: `user_ai_collaboration.md`, `user_dev_style.md` 等 `~/.claude/projects/-Users-takeuchishougo-dotfiles/memory/` 配下の user_* ファイル (対象は差分検出後に確定)
- **Changes**: 直近 transcript サンプルから行動パターンを real quotes 付きで抽出し、既存 user_*.md と突き合わせ。差分のみ user 確認後に追記する (自己申告ベースの `/onboarding`・`/profile-drip` を行動実態で検証する 1 回限りの運用タスク)
- **Size**: S (運用)
- **依存**: なし

### Task 3: Claude.ai export → memory-vec
- **Files**: `claudeai-export-intake.py` (新規)、memory-vec indexer (ソース追加)
- **Changes**: Step 0 として user が Claude.ai から会話 export を手動取得 (メールで数時間後に届く zip)。取得後、exclude フィルタ (プライバシー除外、「迷ったら drop」方針) + tool-noise 除去による clean note 化を行う intake スクリプトを新設し、memory-vec indexer のソースに追加。consumer は既存の recall hook (PR #139) を再利用する。Issue #100 (P1 ソース拡充) と接続
- **Size**: M
- **依存**: export zip の到着待ち (user 手動操作が先行タスク)

## 教訓

- 採用 3 件はいずれも「記事 tactic の直輸入」ではなく「dotfiles の実在 pain への翻訳」である: 未 ship 検出 = worktree 掃除 pain の再発防止、行動観測 = 自己申告バイアスの補正、export intake = memory-vec ソース拡充の具体化。family 教訓「creator-monetization genre は低収率」は維持しつつ、翻訳可能な骨格は拾えた
- Saturation Gate の形式判定 (PASS warning、採用率 40%) と直近トレンド (連続非採用) が割れるケースでは、AskUserQuestion による明示判断が機能した (自動 skip 短絡を避けられた)
