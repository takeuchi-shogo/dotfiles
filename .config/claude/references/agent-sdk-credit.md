---
status: active
last_reviewed: 2026-05-16
---

# Agent SDK Credit (2026-06-15〜)

Anthropic は **2026-06-15** から有料 Claude プランの billing を 2 プールに分割する。一次ソース: <https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan>

## 何が変わるか

| プール | 対象機能 | 消費先 |
|--------|---------|--------|
| **Subscription** (従来) | Interactive Claude Code (terminal/IDE) / Claude conversations (web/desktop/mobile) / Claude Cowork | プラン usage limit |
| **Agent SDK credit** (新規) | **`claude -p`** / Claude Agent SDK (Python/TS) / Claude Code GitHub Actions / Third-party Agent SDK apps | 月次 credit (per-user, no rollover) |

## Credit 額 (plan 別)

| Plan | 月次 credit |
|------|------------|
| Pro | $20 |
| Max 5x | $100 |
| Max 20x | $200 |
| Team Standard | $20 |
| Team Premium | $100 |
| Enterprise (usage-based) | $20 |
| Enterprise (seat-based Premium) | $200 |
| Enterprise (seat-based Standard) | 対象外 |

## 挙動

- **Drains first**: Agent SDK 利用は他より先に credit から消費
- **Refresh**: 月次 (billing cycle 起点)、未使用 credit は **rollover しない**
- **Opt-in claim 必要**: 初回 1 度 Claude account から claim、以後自動更新
- **超過時**: extra usage 有効なら API rate 課金、無効なら block
- **API key 利用 (Claude Developer Platform)**: 無関係 (pay-as-you-go 継続、credit 適用なし)
- **Per-user, not pooled**: Team/Enterprise でも個別 claim、共有/譲渡不可

## 当 dotfiles への影響

| 箇所 | 影響 |
|------|------|
| Main session の対話 (Opus 4.7 等) | ✅ Subscription pool (interactive) |
| `/research` の 8 並列 `claude -p` | ❌ Credit 消費 (最大の枯渇リスク) |
| `/autonomous` の長時間 `claude -p` | ❌ Credit 消費 |
| `/dispatch` の cmux Worker (claude headless 起動時) | ❌ Credit 消費 (起動形態次第) |
| `scripts/runtime/weekly-downloads-cleanup.sh` | ❌ Credit 消費 (低頻度) |
| Subagent (Sonnet/Haiku) 経由の `Agent` tool | ✅ Subscription pool (Claude Code 内部) |
| GitHub Actions integration | ❌ Credit 消費 (採用時) |

## Cost-aware fallback の判断

Credit 枯渇時の選択肢 (順序):
1. **Codex / Gemini に委譲** (`references/model-routing.md` の Cost-aware Fallback 節)
2. **extra usage 有効化** → API rate で続行 (予算管理を強化)
3. **Interactive (TUI) に切替** (parallel orchestration を諦める)

Pruning-First: ヘビーな claude -p バッチ (e.g. 8 並列 research) は credit 枯渇要因なので、Codex/Gemini で代替できないか起動前に検討する。

## 関連
- `references/model-routing.md` Cost-aware Fallback 節
- `references/managed-agents-scheduling.md` (Phase 0 billing 注記)
- `scripts/policy/cost-gate.py` (API cost cumulative tracking、credit pool 追跡は未実装)
- `docs/research/2026-05-16-anthropic-agent-sdk-credit-absorb-analysis.md` (本変更の analysis)
