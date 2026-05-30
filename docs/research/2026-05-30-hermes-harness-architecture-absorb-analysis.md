---
source: "Hermes Harness Architecture (記事テキスト貼り付け)"
title: "Hermes Harness Architecture"
author: "(harness 分析記事、Hermes = NousResearch / 引用元 'What is an Agent Harness')"
date: 2026-05-30
fetched: 2026-05-30
status: light-phase2-only
source-trust: "Untrusted (ベンダー賛辞トーン強、'best open harness' 主張は単独採用根拠にしない)"
topic-family: harness-engineering
family-index: 6
accepted_count: 1
---

# Hermes Harness Architecture — Absorb Analysis (light-phase2)

## Phase 1.5: Saturation Gate

- **Family**: `harness-engineering` (keyword `harness`/`hook`/`scaffold` 3+ hit)
- **N = 5** (過去同分野 absorb): harness-everything (2026-04-19, 6件採用) / harness-pipeline BAN (2026-04-21, ref) / AlphaSignal harness-engineering (2026-04-24, integrated) / self-healing CREAO (2026-04-29, adopted) / cursor-harness (2026-04-30, 採用0)
- **採用率 ≈ 40%** (>= 20%) → **PASS (warning)**。直近 reject は cursor 1 件のみで連続でないため Step 4.5 trend guard 不発火
- **delta 高** (Hermes は他 harness の*実装内部*を 9 部構成で解剖、過去 5 本の原則/hook/skill 論とは角度が異なる) → ユーザー判断で **light-phase2** を選択
- **Stale-Plan Audit (Step 7)**: cursor-harness → `retired` (採用0で確定、実装すべきタスクなし) / self-healing → `implemented` (Tri-judge が /absorb Phase 2.5 として実装済)

## Source Summary (Phase 1)

Hermes (NousResearch) を 9 部構成の harness モデル + 3 追加サブシステムで解剖した記事。主張は「最良の OSS harness の 1 つ」。核心は **OSS harness のランタイム内部実装** であり、Claude Code 上で operate するユーザーには大半が再実装不能 (harness fork が前提)。

## Phase 2: Judgment (novel 5 項目、Sonnet imagination ガード適用済)

| # | novel 論点 | 判定 | 根拠 |
|---|-----------|------|------|
| 1 | cwd プロジェクトファイル (CLAUDE.md/AGENTS.md/.cursorrules) を読み込む*前*の prompt-injection scan | **Gap** | 記事に明示。既存 `prompt-injection-detector.py` は Bash/Edit/Write のツール入力 + WebFetch/MCP が対象。cwd のローカル context ファイルは trusted 前提で未スキャン。clone した untrusted repo に `cd` → Claude Code が `./CLAUDE.md`/`./AGENTS.md` を自動読込 → injection 経路が残る |
| 2 | compaction の parent-child session lineage chain | **N/A** | session ID rotation / child session 生成は Claude Code 内部。PreCompact checkpoint + HANDOFF で文脈復旧は既にカバー。literal 実装は harness fork なしでは不可 |
| 3 | session_search (FTS で過去セッション想起) | **Already** | `recall` skill (contextual commits ベース) + `session_observer` JSONL。意図的に transcript FTS ではなく commit 履歴ベースを採用済 (設計判断) |
| 4 | cron first-class (permission-gate + profile 隔離) | **Already** | `CronCreate`/`schedule`/`/loop`。profile 隔離は Claude Code に概念なし (N/A 成分) |
| 5 | 3-tier prompt (stable/context/volatile) + cache 紐付け | **Already** | CLAUDE.md progressive disclosure + Cache Invalidation Boundary (2026-05-22 absorb で model-routing.md に追加済) |

**結果: Gap 1 件**。記事の「best open harness」トーンに反し、転用余地は item 1 のみに集約。他 4 件は Hermes 内部実装をユーザーが別機構で既に保有 or 再実装不能。

**興味深い逆転**: 記事が「Hermes に欠けている」と挙げる *durable externally-steerable child-run control* を、ユーザーは既に `cmux Worker (launch-worker.sh)` で保有している。

## Phase 2.5: 省略 (light-phase2)

Gap 1 件は security 関連だが threat model が明確 + bounded のため、ユーザー判断で Codex+Gemini 並列検証を省略し light のまま採用。

## Adopted (1 件)

### T1 [Gap, S]: cwd context ファイルの injection スキャン (SessionStart hook)

- **新規ファイル**: `.config/claude/scripts/policy/scan-context-files.py`
- **機構**: SessionStart 時に cwd の `CLAUDE.md` / `AGENTS.md` / `.cursorrules` / `.claude/CLAUDE.md` をスキャン。正規ファイルには現れない難読化シグナル (zero-width unicode / ANSI escape / null byte / base64 eval payload) を検出したら `additionalContext` で警告 + `prompt-injection.jsonl` に記録
- **設計判断**:
  - 自然言語 jailbreak は対象外 (false-positive 高、SessionStart で毎回ノイズになる)。難読化系のみ = 高シグナル、trust-skip allowlist なしでも誤警告ゼロ
  - **warn-only** (`fail_closed=False`、exit 2 でブロックしない)。起動を妨げず判断は人間に委ねる
  - 難読化パターンは `prompt-injection-detector.py` と同期 (DRY: 3 consumer 目で lib 化、現在 2 consumer 目なので duplication + sync コメント)
- **settings.json**: SessionStart 配列に登録 (timeout 10、matcher 無し = 毎起動 + resume で再スキャン、cwd 変化追従)
- **検証**: ruff clean / 検出経路全通過 / clean ファイルは additionalContext ゼロ (ノイズなし) / validate-configs pass / settings.json valid JSON

#### Review Gate による hardening (/review 3-way + codex 再レビュー)

初版に対し code-reviewer (PASS) + codex-reviewer (NEEDS_FIX) + security-reviewer (adversarial, HIGH) の 3-way レビューを実施。収束 HIGH 1 件 + cheap MEDIUM 2 件を修正:

- **HIGH (codex + security 収束)**: `ZERO_WIDTH_RE` が 4 codepoint のみで **U+202E RTL override (Trojan Source CVE-2021-42574)** を取りこぼし。docstring の「難読化系は正規ファイルに絶対現れない」主張と乖離 → bidi/format 制御文字 (U+200B-200F / U+202A-202E / U+2060-2064 / U+206A-206F / U+061C / U+180E / U+FEFF + Unicode tag block) に広域化。**同期宣言通り `prompt-injection-detector.py` も sync** (同一 CVE gap)
- **MEDIUM (base64 evasion)**: `SUSPICIOUS_DECODED` が Python 系のみ → shell 系 (`curl `/`wget `/`| sh`/`bash -c`/`chmod +x`/`os.system`/`/bin/`) 追加 (両ファイル sync)
- **MEDIUM (symlink follow)**: `CLAUDE.md -> /etc/passwd` を読む false assurance → symlink 拒否 + symlink 自体を injection signal として報告
- **却下した誤検出**: codex #1「settings.json 未登録」= False Positive (Haiku fallback が `.claude/` を誤参照、実際は登録済み・検証済み)
- **確認された設計妥当性**: log injection 不可 (`json.dumps` ensure_ascii)、path traversal 不可 (固定 allowlist)、DoS 非現実的 (256KB cap + linear regex 6.5ms)、**warn-only は正しい** (block にすると hostile CLAUDE.md で self-DoS)
- **再検証**: U+202E/U+2060 新規検出 / base64 shell payload 検出 / symlink 拒否 / clean ノイズゼロ / **detector 回帰なし** (legit `ls`/`git` pass、U+202E in bash block) / codex 再レビュー PASS (char range 正当 / ReDoS 安全 / base64 fp ≤1/100M)
- **deferred (NITS_REMAIN)**: BASE64 長さ上限 (perf-only、DoS 否定済で不要) / multi-pattern 列挙 (warn-only で 1 件十分) / DRY lib 化 (3 consumer 目で実施) / detector の RTL tool-input false-positive (既存 scope 問題、CVE 遮断優先、follow-up task 候補)

## Rejected / Not Adopted (4 件)

- item 2 (compaction lineage): N/A — Claude Code 内部、checkpoint で代替済
- item 3 (session_search FTS): Already — recall + session_observer で別機構採用済
- item 4 (cron first-class): Already — CronCreate/schedule
- item 5 (3-tier prompt + cache): Already — progressive disclosure + Cache Invalidation Boundary

## メタ所見

- harness-engineering family 6 本目。記事の角度 (OSS harness 内部解剖) は novel だが、転用可能性は「ユーザーが operate する側 (Claude Code) では再実装不能」の壁で大半が削れる。delta 高 ≠ 採用多
- ベンダー賛辞トーン ("pace is insane", "best open harness") は `/absorb` 哲学通り単独採用根拠にせず、threat model の実在性で item 1 のみ採用
- Stale-Plan Audit が機能: cursor (retired) / self-healing (implemented) の 2 件を frontmatter で確定し、過去採用判断の腐敗を防止
