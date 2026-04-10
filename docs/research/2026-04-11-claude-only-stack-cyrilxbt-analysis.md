---
source: "How to Build a Full AI Stack Using Only Claude in 2026 (Full Course) — @cyrilXBT"
date: 2026-04-11
status: skipped
---

## Source Summary

**主張**: Claude だけで Coding / Research / Writing / Automation / Knowledge / Product の6レイヤーをカバーできる。複数ツールを管理するより「1ツールを深く使う」方がレバレッジが高い、というマーケティング主張。

**手法**:
1. Claude Code をコーディング環境に（ターミナル/全ファイル読み込み/複数ファイル同時編集）
2. CLAUDE.md をプロジェクトルートに置いてコンテキスト注入
3. Daily Research Prompt（Claude + web search で毎朝 AI/crypto ニュース5件を要約）
4. Claude Projects（永続ワークスペースでスタイルガイド/例をロード）
5. Repurposing Prompt（1記事→Thread/LinkedIn/Newsletter/単独ツイートに変換）
6. Claude Code Agents on Railway/Modal（スケジュール実行）
7. Multi-Agent Pipeline: Research → Draft → QC の3エージェント
8. Knowledge Capture Prompt（セッション終了時に要約を Obsidian へ）
9. Claude Code + Vercel + Supabase + Stripe（最小プロダクトスタック）

**根拠**: 事例ベース。定量データゼロ。末尾は `Follow @cyrilXBT` の宣伝。

**前提条件**: solo builder / content creator / crypto trader 向け。記事自身も「専門特化ニーズがあれば専用ツールの方が良い」と認める。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | CLAUDE.md context injection | Already | 多層 CLAUDE.md + Progressive Disclosure + `<important if>` 条件タグ（`.config/claude/CLAUDE.md`, root `AGENTS.md`）|
| 2 | 全コードベース context | Already | `/check-health`, Explore agent, search-first ポリシー |
| 3 | 複数ファイル同時編集 | Already | `/epd`, `/rpi`, Plan Contract, `docs/plans/` |
| 4 | Daily research prompt | Already | `/research`（マルチモデル並列）, `/timekeeper`, `/morning`, `/daily-report` |
| 5 | 永続 workspace / Projects | Already | 3層 memory（user/project/local）, MEMORY.md, auto-memory |
| 6 | Content repurposing | Already | `/rewrite`, `/obsidian-content`, `/digest` |
| 7 | Scheduled BG agents | Already | `/schedule`, `/loop`, `CronCreate`, cmux Worker, Managed Agents |
| 8 | Multi-agent pipeline（R→D→QC）| Already | codex-reviewer + code-reviewer 並列, `/review`, `/epd` |
| 9 | Knowledge capture at session end | Already | `obsidian-bridge` hook, `/checkpoint`, `/note`, `/timekeeper` |
| 10 | Vercel + Supabase + Stripe | N/A | dotfiles リポは product-building の対象外 |
| 11 | Web search integration | Already | `/research` + brave-search MCP + WebSearch |
| 12 | Cron-driven agents | Already | `/schedule`, `scheduled_tasks.lock` 稼働中 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

11項目すべてについて、記事の具体例と既存実装を突き合わせた結果、既存の仕組みが記事の主張を完全にカバーしているか、より精緻である。強化余地なし。

---

**保留メモ（Codex 指摘）**: 記事の `daily prompt` / `repurposing prompt` のような「軽量な運用テンプレート」という視点は、既存の高度な仕組みに対する低摩擦フロントエンドとして使える可能性がある。ただしこれは能力向上ではなく運用省エネ化であり、現時点で具体的な適用先はないため未採用。将来 prompt packaging 系のニーズが発生した場合に参照する。

## Phase 2.5 Refine 結果

**Codex（codex-rescue サブエージェント）の批評**:
- 結論はほぼ正しい。「完全にゼロ価値」は少し雑で、prompt packaging の視点は抽出候補。
- Coding / Automation / Knowledge は記事が明確に格下。
- crypto-specific daily prompt を切る判断は正しい。
- 最終推奨: 分析ログのみ保存 + prompt packaging を保留メモ化。

**Gemini（gemini-explore + Google Search grounding）の周辺知識**:
- 2026 コンセンサス: 「Claude 単一では不十分、マルチモデルルーティングが必須」（Claude=推論/設計, Codex=低レイテンシコード, Gemini=1M+ 分析）。
- 記事が隠す制約: Attention Narrowing, Sycophancy, コンテキストコスト, ベンダーロック, レート制限。
- 2026 先端パターン: Managed Agent Runtimes（LangGraph Cloud, PydanticAI）, Graph-based Memory, Continuous Eval（Promptfoo 2.0+）, Local-First Hybrid。
- 記事の「Claude Code + Railway + Obsidian」は既にレガシー化、と明言。
- 記事の主張と逆の方向に既存セットアップは既に進んでいる（`feedback_codex_reasoning.md`, `rules/codex-delegation.md`, `rules/gemini-delegation.md`）。

## Integration Decisions

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1–9, 11–12 | 全 Already 項目 | スキップ | 既存実装が記事を完全カバーまたは超過 |
| 10 | Vercel + Supabase + Stripe | N/A | dotfiles リポのスコープ外 |

## Decision（Plan セクションに代わる最終判定）

**最終判定: Skip integration, log only.**

理由:

1. 記事の主張する6レイヤーのうち 11/12 は既存セットアップで Already — 強化不要。
2. 唯一の partial（Vercel/Supabase/Stripe）は dotfiles リポのスコープ外で N/A。
3. 記事自体がマーケティングスタイルで定量データゼロ。ユーザーペルソナも crypto trader / solo content creator 寄りでミスマッチ。
4. Gemini の周辺知識調査から、記事の主張（Claude-only）は 2026 コンセンサス（マルチモデルルーティング）と真逆であり、既存セットアップは既に正しい方向に進んでいる。

**後処理**:
- MEMORY.md 更新: なし（同種の浅い marketing 記事を追記すると index が肥大化するため）
- Obsidian Bridge 保存: なし
- Wiki Log: なし

**将来参照用キーワード**: `Claude-only stack`, `cyrilXBT`, `marketing article`, `prompt packaging pending`
