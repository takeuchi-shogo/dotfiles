---
title: "4-Agent Pipeline (Planner→Coder→Tester→Reviewer) absorb 分析"
date: 2026-05-31
source: "How to build a 4-agent team that ships a feature while you sleep (zodchixquant, Telegram-promoted / Teamly SaaS 集客)"
family: multi-agent-orchestration
status: light-phase2-adopted (adopt=1, S)
verdict: 採用1件 (test-engineer.md role boundary 1段落)
---

## Source Summary

- 主張: 4専門エージェント (Planner→Coder→Tester→Reviewer) を共有フォルダ `.pipeline/` のハンドオフファイル経由でパイプライン化し、`/ship` 単一スラッシュコマンドで夜間に機能をリリース。単一エージェントのコンテキスト汚染を防ぐ。
- 手法7件: (1) Planner subagent(opus, コード書かず spec, OPEN QUESTION) (2) Coder subagent(sonnet, spec実装) (3) Tester subagent(sonnet, テスト作成実行・失敗時STOP) (4) Reviewer subagent(opus, read-only, SHIP/NEEDS WORK/BLOCK) (5) ハンドオフファイル `.pipeline/*.md` (6) `/ship` オーケストレータ (7) ステージ別モデルルーティング
- 根拠: anecdotal、定量データなし。後半は Teamly ($29/月 SaaS) 集客。

## Phase 1.5 Saturation Gate

- Family: multi-agent-orchestration (N≥5: Multi-Agent Coordination Patterns 2026-04-11 / 30 Sub-Agents 2026-05-02 / google-skills ADK2.0 2026-04-24 / PostHog Agent-First / CORAL)
- 判定: delta≈0 pure-rehash だが user が continue (フル workflow) を選択

## Phase 2 + 2.5 修正済みテーブル

| # | 手法 | 最終判定 | 根拠 |
|---|------|----------|------|
| 1 | Planner subagent | N/A by design | agent-orchestration-map.md「Never delegate understanding」と衝突。独立 Planner は中核教義に反する |
| 2 | Coder subagent | Already | model-routing.md で Sonnet 実装委譲 |
| 3 | Tester 失敗時STOP | Already(強化可能)→採用 | trust-verification-policy「全reviewer PASSでもテスト失敗ならBLOCK」+ 壊れたら即STOP で振る舞いは担保。ただし test-engineer.md に「prodバグ起因なら自分で直さずSTOP」の明示行が欠落 → 1段落追加で採用 |
| 4 | Reviewer read-only/verdict | Already | code-reviewer.md read-only + PASS/NEEDS_FIX/BLOCK |
| 5 | ハンドオフファイル .pipeline/ | N/A(代替実装) | resume-anchor-contract.md の3 anchor (Plan/HANDOFF.md/RUNNING_BRIEF.md)。.pipeline/追加は source of truth 分裂 |
| 6 | /ship orchestrator | N/A by design | Implicit Coordinator パターン(意図的設計) |
| 7 | ステージ別モデルルーティング | Already | model-routing.md で完全定義 |

## Phase 2.5 批評

- Codex (gpt-5.5, exit 0): 「採用0が妥当。not_found 付けすぎ。#3はexists/Partial、#5は代替実装あり、#6はN/A by design。固定Planner→Coder→Tester→ReviewerはdotfilesのS/M/L動的分岐+Opus統合+task-specific reviewerと噛み合わない。強いて1つなら新workflowではなく/rpi・/epdからtrust-verification-policyへcross-link」
- Gemini: クォータ枯渇 ("exhausted capacity" リトライ2回失敗) で取得不能。Codex単独判定 (MEMORY.md前例準拠)。Gemini主目的のTeamly SaaS検証は採用判断に非依存

## 深掘り検証 (user「手抜きしてない？」challenge 後)

- cross-link gap (Codex提案): 実ファイル検証で**真のgapではない**と確定。/rpi Phase3 Must Contract が既に「verification-before-completion + lint/test実行 + /review起動」を強制、trust-verification-policy は /review が呼ぶゲート層に codify済み。直リンクは冗長。Codex自身も必要性を否定 ("強いて1つなら")
- Tester boundary (#3): test-engineer.md 全文確認。EXPLORE=no-modify / AUTOCOVER=テスト新規のみで構造的にテスト限定だが、「テスト失敗がprodバグ起因のときprodを自分で直さずSTOP」の明示1段落が欠落 → これが唯一の article-backed 強化

## 採用 (adopt=1, S規模)

- test-engineer.md の Operating Mode に「### On Test Failure (Role Boundary)」を追加: テスト側バグ→修正 / production側バグ→自分で直さず報告してSTOP(Implementに戻す)。根拠 trust-verification-policy + 壊れたら即STOP を併記。実装済み・task validate-configs pass

## 不採用 (Pruning-First + Codex採用0判定)

- 4-agent fixed pipeline / `.pipeline/` shared folder / `/ship` orchestrator: dotfiles の Implicit Coordinator + 動的分岐設計と衝突、退化リスク
- cross-link (/rpi・/epd → trust-verification-policy): 冗長と実証、不採用

## メタ学習

- Phase 2.5 で Gemini クォータ枯渇時は Codex 単独で判定可 (前例どおり)
- Sonnet Explore (medium) が trust-verification-policy.md を見落とし → Codex が捕捉。Pass1 の網羅性に限界、Phase 2.5 の異モデル批評が bias/見落とし両方を補正した実例
- user「手抜きしてない？」challenge により採用0→採用1に修正。Codexの「採用0」を鵜呑みにせず /rpi・test-engineer.md を実読したことで、cross-linkは棄却・tester boundaryは採用と精緻化できた
