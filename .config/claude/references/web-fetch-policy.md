---
status: active
last_reviewed: 2026-05-06
observation_pinned: "Claude Code v2.1.126"
---

# Web Fetch Policy

URL 取得の経路選択。`WebFetch` の内部 Haiku 要約 + サイレント truncation 観測に対応するための decision table。

## 観測前提

Claude Code v2.1.126 のリバースエンジニアリング (sherry/Zenn 2026-05-06) 由来:

- `WebFetch` は内部で Haiku 要約を実行する (HTML→md 変換 + 要約)
- 100k chars 超の入力はサイレント truncation される (出力は短い markdown のみ)
- HTML→md 変換は code/table を lossy にすることがある
- Haiku 層は web 経由 prompt injection の **Opus 到達前** の表面となり得る
- 引用 faithfulness は Anthropic の copyright filter (~125 字) で更に制限される

バージョン更新時に再検証必要。陳腐化判定は `observation_pinned` フィールドで行う。

## URL pattern → 経路 (Decision Table)

| URL pattern | 推奨経路 | 理由 |
|---|---|---|
| **trusted ドメイン** (`data/trusted-domains.json`) | `WebFetch` 直接 | full markdown 通過を観測確認済み |
| **一般記事** (Zenn / Qiita / note / blog / Wikipedia) | `curl` + `defuddle` → `Read` | サイレント truncation 回避 |
| **SPA / JS 必須** | Jina Reader (`https://r.jina.ai/<url>`) または playwright | 静的取得不可 |
| **PDF** | `curl` + pdf-extract | `WebFetch` lossy |
| **認証 / Cookie 必要** | 手動取得 → ファイル経由 | `WebFetch` は credential 持ち込み不可 |
| **GitHub PR / Issue** | `gh` CLI | `WebFetch` よりレート制限・認証の扱いが安全 |

## 用途別オーバーライド

trusted ドメインでも、用途によって `curl + defuddle` を強制する:

- **C1: 原文引用が必要** (`/absorb`, `/research`, `/digest` 等) → 引用 faithfulness のため `curl/defuddle` 強制
- **C2: code/table 重視** (技術ドキュメント、API リファレンス、設定例) → HTML→md lossy 回避のため `curl/defuddle` 強制
- **C3: subagent に取得結果を転記** (External Content Contamination 対象) → `subagent-delegation-guide.md` の Raw Fetch Only Contract に従う

## フォールバック順序

`WebFetch` 失敗時 (404 / DNS / timeout 等):

```
WebFetch
  → WebSearch (キャッシュ・ミラー検索)
  → curl + defuddle
  → Jina Reader (r.jina.ai)
  → Gemini grounding (1M context, 外部リサーチ)
  → AskUserQuestion (テキスト貼り付け依頼)
```

## trusted_domains の管理

- **本体**: `.config/claude/data/trusted-domains.json` (configuration data file)
- **転記禁止**: `CLAUDE.md` / `MEMORY.md` には**書かない** (常時コンテキストの IFScale 違反)
- **観測経路**: PostToolUse hook (`scripts/runtime/webfetch-truncation-detector.py`) が trusted 外で短い出力を検出し `friction-events.jsonl` に `webfetch_truncation_suspect` event を記録する

trusted リストの追加・削除は `data/trusted-domains.json` を直接編集する。

## 観測 (telemetry)

- **手動**: `webfetch_truncation_observation` (Phase 1 実測など、手動 append)
- **自動**: `webfetch_truncation_suspect` (`runtime/webfetch-truncation-detector.py` PostToolUse hook)
- 集計: `~/.claude/agent-memory/learnings/friction-events.jsonl` を参照

撤退条件:
- 6 ヶ月運用で本ドキュメントが参照されない → 削除候補
- hook が偽陽性多発 → `SHORT_OUTPUT_THRESHOLD` 緩和 or 削除

## 関連

- `references/model-routing.md` — Haiku 委譲は「生取得まで、要約は呼び出し側責務」
- `references/subagent-delegation-guide.md` — Raw Fetch Only Contract / External Content Contamination
- `agents/security-reviewer.md` — Web fetch via Haiku 要約層 (injection 表面)
- `scripts/runtime/webfetch-truncation-detector.py` — 観測 hook
- `data/trusted-domains.json` — trusted ドメインリスト
- 由来 absorb: `docs/research/2026-05-06-webfetch-haiku-summary-absorb-analysis.md`
- plan: `docs/plans/2026-05-06-webfetch-policy-plan.md`
