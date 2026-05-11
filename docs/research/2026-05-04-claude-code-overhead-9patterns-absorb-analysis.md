---
source: "I tracked 430 hours of Claude Code usage. 73% was wasted on these 9 patterns (anonymous X post, Telegram funnel)"
date: 2026-05-04
status: integrated
author: anonymous (Telegram @+_ZWrQN7GuDA3ZDEy)
bias_warning: "Telegram集客あり。$1,340 / 90日 / 73% は単独proxy計測。Anthropic公式 verify は2026-04時点でほぼ全項目 unverified (Gemini grounding rate limit + 公式情報なし)"
---

# Claude Code Overhead 9 Patterns — Absorb Analysis

## Source Summary

**主張**: Claude Code セッションの 73% トークンは 9 つの不可視 overhead patterns に消える。proxy 計測 (90日 / 430時間 / 600万 token / $1,340) で「productive token 27% → 65% に改善した」と主張。モデル選択やプロンプト改善より overhead 削減が usage limit 対策の最大レバーと提唱。

**9 手法 (記事の主張と削減目標)**:

1. CLAUDE.md bloat (~14%) — 4,800 → 900 token
2. 会話履歴 re-read (~13%) — 60 message → 15 / /compact 使用
3. UserPromptSubmit hook injection (~11%) — 4 → 1 hook
4. Cache miss on session resume (~10%) — 5 min → 1-hour cache (paid plan)
5. Skill loading on irrelevant tasks (~7%) — 11 → 4 skill
6. MCP "just-in-case" tool defs (~6%) — 12 → 3 always-on
7. Extended thinking on simple Q (~5%) — global ON → OFF default
8. Wrong-direction generation (~4%) — Cmd+. early stop
9. Plugin auto-update / SessionStart noise (~3%) — 9 → 2

**根拠**: 自前 HTTP proxy で 90 日間ロギング。productive token 比率の measurement framework と claim する。**ただし数値合計 14+13+11+10+7+6+5+4+3=73% は engineered (suspiciously round)。Gemini grounding (rate limit 内) で確認した範囲では Anthropic 公式情報なし。March 2026 quota change のみ事実 (公式 acknowledged)、他は unverified。**

**前提条件**: Claude Max / Pro paid plan、heavy user (週 200+ ターン)、proxy 計測スキル保有者。普通の dotfiles user 全員には適用しない。

---

## Gap Analysis (Pass 1 + Pass 2: 既存の dotfiles 対策との突き合わせ)

| # | パターン | 当 setup 実測 | 既存対策 | 判定 |
|---|---------|------------|---------|------|
| 1 | CLAUDE.md bloat | user 458 + project 435 = 893 word ≈ 1,200 token (target <1,500) | `scripts/policy/claudemd-size-check.py` 4,096B 予算、Progressive Disclosure (`<important if>`) | **Already (棄却→ユーザー要請で再検討対象に変更)** |
| 2 | 会話履歴 re-read | /checkpoint, /recall, PostCompact verify | `pre-compact-save.js`, `post-compact-verify.js`, checkpoint skill | **Already (保留)** |
| 3 | UPS hook injection | 2 hook (claude-hooks Rust + user-input-guard.py) | `measure-instruction-budget.py` THRESHOLD_TOKENS=6000 監視、agent-router | **Already** |
| 4 | Cache miss (1-hour cache) | PreCompact/PostCompact のみ、`cache_control` 設定なし | (なし) | **保留 (要事実確認)** |
| 5 | Skill loading | **107 skill description 累計 49,133 bytes ≈ 12,283 token** (system-reminder で常時展開実測あり) | `/skill-audit` (5D Quality + Usage Tier)、`harness-stability.md` 30日評価ポリシー、自動 disable なし | **Gap (最優先)** |
| 6 | MCP tool schema | settings.json の MCP server 0 個、.mcp.json 別管理 | `mcp-audit.py` + VeriGrey Tool Filter + whitelist | **Already (棄却)** |
| 7 | Extended thinking | settings.json env で `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` 明示 | (設定) | **Already** |
| 8 | 早期停止 | /rewind (Esc-twice) + stagnation-detector.py。完全自動統合ではない、人間の習慣 | workflow-guide.md にトリガー条件記載 | **Partial (人間訓練扱い)** |
| 9 | SessionStart noise | 5 hook (session-load, checkpoint_recover, timestamp, env-bootstrap, memory-integrity-check) | (各 hook が個別目的、重複は今のところなし) | **Partial (監査要)** |

---

## Phase 2.5 修正 (Codex 批評由来)

Codex critique は Opus の Phase 2 分析を「Already 過大評価寄り」と指摘し、以下の修正を行った:

| 修正 | 元判定 | 修正後 | Codex 根拠 |
|------|------|--------|-----------|
| Pattern 5 格上げ | Partial | **Gap (最優先)** | 12,283 token tax は記事数値とは独立に当 setup の実害として確定 |
| Pattern 4 据え置き | Gap | **保留** | Anthropic API では 1h TTL あるが Claude Code 本体挙動は unverified |
| Pattern 1, 6 棄却 | 強化候補 | **棄却** | Pruning-First 違反、すでに最小、記事の helpful な提案を取り込まない |
| 数値の扱い | 採用 | **仮説生成限定** | 14+13+...=73% は engineered。判断は当 setup 実測ベースのみ |

Gemini critique は rate limit で完全 verify 不能。確認できた範囲では Anthropic 公式情報は限定的:

- Claim 1 (5min/1h cache TTL): API 公式に caching あり、ただし TTL 値は docs に明記なし → Unverified
- Claim 2 (March 2026 incident): 公式 acknowledgment 検出できず → Unverified
- Claim 3 (Skill token cost): 公式仕様明記なし → Unverified
- Claim 4 (Alt+T toggle): keybinding ドキュメントなし → Likely False
- Claim 5 (73% overhead): 第三者 benchmark なし → Unverified

**記事の数値 / 公式 acknowledgment 主張は信頼度低と扱う。当 setup の実測値 (107 skill 12,283 token tax) のみ採用根拠とする。**

---

## Integration Decisions (Phase 3 ユーザー選別結果)

### 採用 (5 タスク)

| ID | 項目 | 判定 | 理由 |
|----|------|------|------|
| T1 | Skill 常時 tax 半減 (107 skill Tier 分類) | **採用 (最優先)** | 12,283 token は確定値の実害。Codex 推奨第一順位 |
| T1.5 | CLAUDE.md project 435 word 再検討 | **採用 (ユーザー追加)** | Pruning-First 観点で剪定余地確認 |
| T2 | SessionStart hook 監査 | **採用** | 5 hook の volatile output / latency 実測。cache prefix 影響確認 |
| T3 | Cache TTL 実態確認 (調査) | **採用 (保留→調査)** | Anthropic 公式 docs / Claude Code release notes で 1h TTL 自動有無を verify |
| T4 | MEMORY.md references 流入経路確認 | **採用** | 200+ pointer が system prompt に流入しているか経路最小確認 |

### 棄却

| 項目 | 理由 |
|------|------|
| Pattern 6 (MCP) | settings.json に MCP server 0 個ですでに最小。Pruning-First で不変更 |
| Pattern 7 (Extended thinking) | DISABLE_ADAPTIVE_THINKING=1 で OFF default 設定済み |
| Pattern 8 (早期停止強化) | /rewind で対応可能、人間の習慣に依存する範囲は harness 化しない |

---

## Plan (5 タスク)

### Task T1: 107 skill の Tier 分類と常時 description tax 半減 (M 規模, 最優先)

- **Files**:
  - `docs/specs/2026-05-04-skill-tier-pruning.md` (新規 spec)
  - `.claude/skills/skill-audit/SKILL.md` (Tier 分類強化)
  - `scripts/policy/measure-instruction-budget.py` (skill description budget 追加)
- **Changes**:
  - 107 skill を Daily/Weekly/Monthly/Unused に Tier 分類 (実測ベース、自己申告補完)
  - Unused tier は disable 候補として spec 化 (削除は 30 日評価後ポリシー遵守)
  - description budget を `measure-instruction-budget.py` に追加し、12,283 → ~6,000 token を半減目標として継続監視
  - `/skill-audit` を Tier 出力に対応
- **Size**: M (3 ファイル、新規 spec 含む)
- **Verification**: 半減目標達成 (description 累計 < 7,000 token)、`/skill-audit` で Tier レポート出力

### Task T1.5: dotfiles/CLAUDE.md project 側 (435 word) 再検討 (S 規模)

- **Files**: `dotfiles/CLAUDE.md`
- **Changes**:
  - 各セクションが project-specific か汎用かを精査
  - 重複・冗長部分を削減
  - 既存 user CLAUDE.md (458 word) との role 分離を確認
- **Size**: S (1 ファイル)
- **Verification**: word count 削減 (target: -100 word)、振る舞いに退行なし

### Task T2: SessionStart hook 監査 (S 規模)

- **Files**:
  - `scripts/runtime/sessionstart-audit.py` (新規)
  - `.claude/settings.json` (剪定があれば)
- **Changes**:
  - 5 hook (session-load.js, checkpoint_recover.py, timestamp file write, env-bootstrap.py, memory-integrity-check.py) の stdout サイズ・latency を実測
  - volatile output (timestamp, ランダム値) が cache prefix を破壊しないか確認
  - 重複・冗長があれば剪定
- **Size**: S (新規スクリプト + 必要に応じ settings.json)
- **Verification**: 各 hook の stdout < 200 bytes 目標、合計 latency < 3 秒

### Task T3: Claude Code prompt cache 1h TTL 実態確認 (S 規模、調査)

- **Files**: `docs/research/2026-05-04-claude-code-cache-ttl-investigation.md` (新規)
- **Changes**:
  - Anthropic 公式 docs (https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) を読み、1h TTL 仕様を verify
  - Claude Code 2.x release notes / CHANGELOG で自動 1h cache 機能を確認
  - 設定が必要なら settings.json への追加方法を Decision として記録
  - Gemini rate limit 解除後に再 grounding
- **Size**: S (調査レポートのみ)
- **Verification**: 公式 docs URL + verify した結論を記載、必要時の設定方法を 1 段落

### Task T4: MEMORY.md references 流入経路確認 (XS 規模、調査)

- **Files**: 本レポートに追記、または `docs/research/2026-05-04-memory-references-load-path.md` (必要に応じ)
- **Changes**:
  - SessionStart hook (session-load.js, env-bootstrap.py 等) のソースで MEMORY.md または `references/` の読み込みコードを grep
  - "on-demand" claim が事実か確認 (lazy load か常時注入か)
- **Size**: XS (grep + 1 段落の結論)
- **Verification**: 結論が「lazy / always-loaded / hybrid」のいずれかで明示

---

## 実行順序

1. T1 (最優先) — Skill 常時 tax 削減
2. T1.5 — CLAUDE.md project 再検討
3. T2 — SessionStart 監査
4. T3 — Cache TTL 調査
5. T4 — MEMORY references 経路確認

T2-T4 は T1 と並行可能 (依存なし)。

---

## ハンドオフ

L 規模未満のため `docs/plans/` への保存は不要。本分析レポート + Phase 5 で MEMORY.md にポインタ追記。実行は別セッションまたは引き続き同セッションで `/rpi` 等を使用。
