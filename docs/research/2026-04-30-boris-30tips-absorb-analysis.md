---
source: "ClaudeCodeStudio (URL 不明)"
date: 2026-04-23
status: partial
adopted: 6
---

# Boris の 30 Tips 完全版 — Absorb Analysis

## Source Summary

- **タイトル**: Claude Code 生みの親「Boris」が実践する 30 個の最強 Tips 完全版
- **著者**: ClaudeCodeStudio
- **公開日**: 2026-04-23
- **警戒シグナル**: 「リアルに生産性10倍」「神記事」「保存も必須」のマーケティング文体。同著者の 2026-04-29 codex-vs-claudecode-role-split 採用 1 件 (採用率低い)
- **30 Tips 一覧**: Plan Mode, 自己検証, worktree 3-5本, CLAUDE.md ruthless edit, skills 化, settings.json git, allow/ask/deny, --add-dir, subagents, PostToolUse hook, PR @claude メンション, statusline, Chrome 拡張, CLI 分析, Let Claude interview, auto memory, monorepo パスルール, /compact, /rewind, MCP, claude -p, fan-out 移行, Issue→impl, hooks 強制, /simplify, GitHub Action @claude, /ultrareview, Routines, /ultraplan, Remote Control

## Gap Analysis (Pass 1 + Pass 2 統合テーブル)

| # | Tip | 判定 | 詳細 |
|---|-----|------|------|
| 1 | Plan Mode | Already | plan-lifecycle hook + PLANS.md + plansDirectory 運用済み |
| 2 | 自己検証 (smoke test → heavy) | Partial→Adopt (T1) | verification-before-completion に段階化ガイドが不足 |
| 3 | worktree 3-5 本 | Already | `references/using-git-worktrees.md` + parallel session ガイド存在 |
| 4 | CLAUDE.md ruthless edit | Already | AutoEvolve session-learner で継続的 trim 実装済み |
| 5 | skills 化 | Already | skill-writing-principles + entry 50 行原則 (Karpathy absorb) で同等カバー |
| 6 | settings.json git 管理 | Already | dotfiles に settings.json コミット済み |
| 7 | allow/ask/deny (.env deny) | Already | settings.json L124-158 で Read/Write/Edit deny 完全列挙済 (W4 の Pass 2 直接確認で判明) |
| 8 | --add-dir | Already | CLAUDE.md + references 既存 |
| 9 | subagents | Already | agents/*.md 個別でツール制限済み |
| 10 | PostToolUse hook | Partial→Adopt (T2) | hook timeout / 実行時間モニタリングが harness-stability に未記載 |
| 11 | PR @claude メンション | Already | gh ベース github-pr skill で代替済み |
| 12 | statusline | Partial→Adopt (T4) | context% + REF + MEM + SKILL の 4 要素あり、cost 要素が未追加 |
| 13 | Chrome 拡張 | N/A | 個人 dotfiles スコープ外 |
| 14 | CLI 分析 | Already | check-health + audit skill で同等 |
| 15 | Let Claude interview | Already | /interview + /spec Phase 0 で実装済み |
| 16 | auto memory | Already | AutoEvolve + session-learner で実装済み |
| 17 | monorepo パスルール | N/A | 個人 dotfiles は monorepo 構造なし |
| 18 | /compact | Already | strategic-compact + context-compaction-policy.md |
| 19 | /rewind | Partial→Adopt (T3) | checkpoint skill に外部副作用警告が不足 |
| 20 | MCP | Already | mcp-audit + ~/.mcp.json で管理済み |
| 21 | claude -p | Already | dispatch skill + model-routing で実装済み |
| 22 | fan-out 移行 | Partial→Adopt (T5) | dispatch/SKILL.md に pilot-first ルールが未記載 |
| 23 | Issue→impl | Already | fix-issue skill + github-pr で実装済み。claude-code-threats.md で hook injection COVERED 確認済 |
| 24 | hooks 強制 | Already | harness-stability.md で 30 日評価ポリシー COVERED 確認済 |
| 25 | /simplify | Already | simplify skill 存在 |
| 26 | GitHub Action @claude | Already | team-harness-patterns 経由で代替 |
| 27 | /ultrareview | N/A | research preview 名称、未検証 |
| 28 | Routines | Partial→Adopt (T6) | managed-agents-scheduling.md に research preview 注意書きが未記載 |
| 29 | /ultraplan | N/A | research preview 名称、未検証 |
| 30 | Remote Control | N/A | research preview 名称、未検証 |

## Phase 2.5: Codex + Gemini 並列批評

### Codex 批評結論
- 採用 **0 件** 推奨 (初期)
- 降格判定 5 件: #4 (session-learner Already) / #11 (github-pr skill) / #17 (monorepo N/A) / #22 (dispatch Already) / #27 (N/A)
- 「記事の主張」批評が主体。具体的 warning vs 既存ファイル 1 行検証は不足 (Sonnet Explore 深掘り + Opus 直接 Read で補完)

### Gemini 批評結論
- 全主張「確認」、信頼性 95% を報告
- ただし `claude -w` フラグ・`claude -rc` QRコード・「30日259PR 4万行」等の独立検証不可な詳細を hallucinate
- 過度に楽観バイアス (MEMORY.md 既知パターン) が発症
- untrusted-stat タグ付き: 具体数値の独立検証不可

### 統合判定
Codex の降格判定を採用、Gemini の楽観評価は警戒タグ。ユーザー指示による deep-dive で 6 件を採用候補として特定。

## Integration Decisions

**採用合計: 6 件 (T1〜T6、各 S 規模)**

### T1 (W1, Tip 2): smoke test → heavy verify 段階化ガイド
- **対象**: `skills/verification-before-completion/SKILL.md`
- **変更**: When to Use / Strategy セクションに「初期は最低限のスモークテストから始め、段階的に重い verify を追加する」1 行追記
- **出典**: Boris Tip 2「検証コマンドが重すぎると時間食う、最初は最低限のスモークテストから始める」

### T2 (W6, Tip 10): hook timeout / 実行時間モニタリング
- **対象**: `references/harness-stability.md`
- **変更**: 「Hook 健全性」セクションに hook timeout 設定 (settings.json hooks.*.timeout) と重い hook 検出 (実行時間 > 5s で警告) セクションを追加
- **出典**: Boris Tip 10「hook が重いとセッション全体が遅くなる、実行時間の上限を設けておく」

### T3 (W8, Tip 19): checkpoint 外部副作用警告
- **対象**: `skills/checkpoint/SKILL.md`
- **変更**: Anti-Patterns セクションに「外部副作用 (DB 操作 / API 呼び出し / file system mutation outside repo) は checkpoint で戻せない、別途確認が必要」1 行追記
- **出典**: Boris Tip 19「外部副作用がある作業は checkpoints では戻せない」

### T4 (W12, Tip 12): statusline cost 表示
- **対象**: `.config/claude/statusline.sh`
- **現状**: context% + 📚REF + 🧠MEM + ⚡SKILL の 4 要素
- **変更**: cost 表示を context-monitor.py 経由または環境変数 (CLAUDE_CODE_COST 等) で追加。branch は Claude Code 組み込みプロンプトに表示済みのため除外
- **注意**: cost 直接取得不可の場合は note に留め、次回 hygiene セッションで再評価
- **出典**: Boris Tip 12「branch / context% / cost の 3 要素」

### T5 (W9, Tip 22): pilot-first / 大規模 fan-out 移行ルール
- **対象**: `skills/dispatch/SKILL.md`
- **変更**: Workflow / Anti-Patterns に「fan-out で大規模移行する場合、まず数ファイルでパイロット実行し、失敗パターンを洗い出してから全体展開」1-2 行追記
- **出典**: Boris Tip 22「いきなり全量で回さない、まず数ファイルで失敗パターンを洗い出してから全体に展開」

### T6 (W13, Tip 28): Routines 研究プレビュー注意
- **対象**: `references/managed-agents-scheduling.md`
- **変更**: 冒頭または「コスト設計指針」セクション直前に「Routines は研究プレビュー機能、仕様変更可能性あり、GitHub trigger / API token 管理は別途設計」note 追記
- **出典**: Boris Tip 28「研究プレビューで仕様が変わりうる、GitHub trigger や API token 管理の設計は別途必要」

## Rejections (24 件、Pruning-First)

| カテゴリ | 件数 | 理由 |
|---------|------|------|
| Already (強化不要) | 20 | 既存仕組みで具体的に同等カバー |
| N/A (scope 外) | 4 | monorepo (#17) / research preview (#27/#29/#30) |

主要棄却の根拠:
- W2 (Tip 4): AutoEvolve session-learner で実装済み
- W3 (Tip 5): skill-writing-principles の entry 50 行原則で同等
- W4 (Tip 7): settings.json L124-158 で Read/Write/Edit deny 完全列挙済 (Pass 2 直接確認で Already 判明)
- W5 (Tip 9): agents/*.md 個別でツール制限済み
- W10 (Tip 23): claude-code-threats.md で COVERED 確認済
- W11 (Tip 24): harness-stability.md で 30 日評価ポリシー COVERED 確認済
- #11 PR @claude / #26 GitHub Action: 既存 skill で代替済み

## Lessons

1. **Already = 存在確認 ≠ 品質保証**: 初回判定で「全 Already 強化不要」とした後、ユーザー指摘 (「もう一度、手抜き、漏れないか」) による deep-dive で 6 件の novel 強化候補が判明。`feedback_absorb_already_deepdive.md` + `feedback_absorb_thoroughness.md` の再現パターン

2. **Sonnet Explore の引用範囲限界**: W4 (.env deny) で L85-99 までしか引用せず L124-158 の完全列挙を見落とした。重要箇所は Opus による直接 Read で再確認が必要

3. **Codex 批評の限界**: 「記事の主張」批評が主体で「具体的 warning vs 既存ファイルの 1 行検証」が不足。Sonnet Explore 深掘り + Opus 直接 Read の組み合わせが補完として有効

4. **Gemini hallucination 警戒**: grounding 付きでも `claude -w` フラグ等の独立検証不可な詳細を生成。MEMORY.md 既知の「過度に楽観的バイアス」が再発。Gemini 出力の具体数値は untrusted-stat として扱う

5. **マーケティング文体 ≠ 即棄却**: 「神記事」「生産性10倍」等のマーケティング文体を持つ記事でも、具体的 warning を丁寧に検証すると実用的な 1 行追記候補が 6 件見つかった。過去 ClaudeCodeStudio 採用 1 件の実績から「採用率低い」と即棄却せず、deep-dive が有効

## Plan

M 規模 (6 ファイル変更) だが各タスクは S 規模・相互依存なし。同一セッションで実装可能、または新セッションで `/rpi` 実行。

Codex Plan Gate は省略 (各タスクが独立 1 行追記、相互依存なし)。

対象ファイル:
- `skills/verification-before-completion/SKILL.md` (T1)
- `references/harness-stability.md` (T2)
- `skills/checkpoint/SKILL.md` (T3)
- `.config/claude/statusline.sh` (T4 — cost 取得可否を先確認)
- `skills/dispatch/SKILL.md` (T5)
- `references/managed-agents-scheduling.md` (T6)

## 実装結果 (2026-04-30)

実装段階で **2 件追加 Already 判明、最終採用 4 件のみ**:

| Task | 結論 | 理由 |
|------|------|------|
| T1 (W1, smoke test 段階化) | **Already** | 対象 skill `verification-before-completion` は plugin (`superpowers:`) で個人 dotfiles に存在せず変更不可。skill 経由で Boris の意図は既にカバー |
| T2 (W6, hook timeout) | **採用** | `references/harness-stability.md` に「Hook 実行時間モニタリング」セクション追加 (~10 行) |
| T3 (W8, checkpoint 副作用) | **採用** | `skills/checkpoint/SKILL.md` の末尾に Anti-Patterns セクション追加 (DB/API/外部状態の警告) |
| T4 (W12, statusline cost) | **Already** | `scripts/context-monitor.py` L122-133 で cost (色分け 💰), L274-277 で branch (🌿) を既に表示。Sonnet Explore は L62-76 のみ引用していた漏れ |
| T5 (W9, fan-out pilot-first) | **採用** | `skills/dispatch/SKILL.md` の末尾に Anti-Patterns 追加 (3-5 ファイルで先行検証) |
| T6 (W13, Routines preview) | **採用** | `references/managed-agents-scheduling.md` の Routines Pilot セクション冒頭に Research Preview 注記追加 (CLI / GitHub trigger / 課金条件 / フォールバック) |

### Load-bearing claim 修正

T2 初稿で「`scripts/runtime/hook-stats.py` (or 同等の集計)」と記述したが、実存確認で **不存在** が判明。「実行時間集計の手段は ad-hoc (個別 hook の `time` ラッパー / observability ログ / `dead-weight-scan.py` 拡張) — 専用 stats スクリプトは未実装」に修正。Boris Tip 24 (「絶対に守るべき最小集合から始める」) に準じて、専用ツール導入はせず ad-hoc 手段を明記した。

### 教訓 (実装段階)

6. **実装過程で更に Already 判明する**: ユーザー指摘で deep-dive した後でも、実装に取りかかると更に 2 件 Already (T1/T4) が判明した。Sonnet Explore の引用範囲漏れ (L62-76 のみで判定) が複数箇所で発生。これは Pass 2 deep-dive 後に **「重要箇所は実装直前にも Opus が直接 Read」** で再確認する規律が必要

7. **Load-bearing claim の即時検証**: ドキュメント追記でも「`scripts/X.py` で集計」のような claim を書いたら即 `find` / `ls` で実存確認する。書きながら別セッション knowledge を引きずると虚偽参照を生む
