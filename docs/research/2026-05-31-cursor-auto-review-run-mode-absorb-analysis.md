---
title: Cursor Auto Review 実行モード absorb 分析
date: 2026-05-31
source_url: https://cursor.com/ja/changelog/auto-review
source_type: changelog (Cursor 3.6, 2026-05-29)
status: analyzed (adopt=0, validation-only-followup-done)
topic_family: none (permission/autonomy/sandbox — 既存 taxonomy 4族に非該当、新分野扱いで PASS)
adopted: 0
tags: [absorb, permission, autonomy, sandbox, harness, reference-only]
---

# Cursor Auto Review 実行モード absorb 分析

## Source Summary（記事要約）

- **主張**: Auto Review = 承認を求める回数を減らしつつ、より安全に実行できるようにすることで、Cursor がより長時間自律実行できる新しい実行モード。
- **手法**:
  1. ツール呼び出し（Shell / MCP / Fetch）への自動レビュー適用
  2. allowlist 登録済みの呼び出しは即時実行
  3. サンドボックス化できる呼び出しはサンドボックス内で実行
  4. それ以外のエージェントアクションは「分類サブエージェント」に送り、**allow / 別アプローチを試す / 承認を求める (ask)** を判断
  5. カスタム指示で分類エージェントの動作を調整可能
  6. Settings > Cursor Settings > Agents > Run Mode の UI で設定
- **根拠**: changelog のため定性的のみ。詳細は docs/agent/tools/terminal#run-mode。
- **前提**: IDE 統合エージェント（Cursor）のツール実行ガバナンス。approval fatigue 削減が UX 訴求。
- **取得経路**: defuddle（cursor.com は trusted 外 + C1 オーバーライドで full markdown 取得）。

## Phase 1.5 Saturation Gate

**判定: PASS（新分野扱い）**

記事タイトルは "auto-review" だが、内容はコードレビューではなく **permission / autonomy / sandbox**（ツール実行ガバナンス）。手法を taxonomy 4 族（obsidian-second-brain / skill-graphs / harness-engineering / claude-code-tips）と照合した結果:

- `harness-engineering` の閾値（`harness` / `hook` / `scaffold` / `agent platform` のうち 3 つ以上）に **hit 0** で未達
- 他 3 族も hit なし

→ 「どの family にも分類しない」と明示判断（暗黙 family なし扱いを避ける）。Stale-Plan Audit も N=0 で skip。**code-review-best-practices family（直近 5 件 saturated）との誤分類を回避できた**点が収穫。

## Phase 2 + 2.5 修正済み判定テーブル

| # | 手法 | Phase 2 判定 | Phase 2.5 修正後 | 修正根拠 |
|---|------|------|------|------|
| 1 | run mode 段階的自動承認 + UI | Partial | **Partial（低優先）/ UI は N/A** | Codex: Run Mode UI はチーム/製品向け affordance。個人は hook/rules/profile で監査可能・安価 |
| 2 | allowlist 即時実行 | Already（完全一致） | **Already**（※「完全一致」を緩和） | Codex: ask tier=0 なので三値ではなく `allow/deny + default prompt`。実用上 Already 維持。settings.json allow 71 + `skipAutoPermissionPrompt` |
| 3 | execution sandbox | Partial | **Partial（低優先）** | Codex+Gemini 一致: 個人用途に E2B/microVM/air-gap は過剰。dotfiles は `.env denyRead` の minimal filesystem sandbox のみ |
| 4 | 分類サブエージェント三値判定（allow/alternative/ask） | Partial→Gap | **N/A（意図的 Reject）** | Codex+Gemini 一致: ①determinism boundary 違反（static-checkable は mechanism に寄せる）②prompt injection 経由の承認バイパスリスク ③レイテンシ500ms-2s。`agent-router.py` は委譲提案であって permission classifier ではなく「意図的に実装していない境界」 |
| 5 | 破壊的操作ガード | Already | **Already**（強化方向は棚卸し） | Codex: ルール追加より deny catalog / permission-audit の定期確認が先。deny rules 102 + `careful` skill |
| 6 | カスタム指示ガバナンス | Already | **Already** | CLAUDE.md + 40+ hooks + settings.local.json |

最大の修正: **#4 を Gap → N/A（意図的 Reject）**。

## Phase 2.5 セカンドオピニオン詳細

### Codex（gpt-5.5, high effort）
- **最終推奨採用 0 件**。「薄い changelog から個人 harness に輸入するには抽象度が高すぎて mechanism に落ちない」。
- #4 は **Reject**、#1/#3 は低優先 Partial。
- **見落とし指摘（dotfiles 優位確認）**: MCP/Fetch 応答検査（`mcp-audit.py` / `mcp-response-inspector.py` / WebFetch truncation check）は dotfiles 側がむしろ記事より厚い。
- **過小評価指摘**: #5 強化は新モード導入より deny catalog / permission-audit の**棚卸しが先**。
- 注: Codex 初回 xhigh で silent stall（`CODEX_FAILED`）、high effort リトライで成功。

### Gemini（Google Search grounding）
- **トレードオフ表**が #4 Reject を裏付け:

  | 項目 | 静的 allowlist | LLM 分類器 |
  | --- | --- | --- |
  | 決定性 | 100% | 非決定的 |
  | 運用負荷 | 高 | 低 |
  | 攻撃耐性 | 強 | **弱（prompt injection）** |
  | レイテンシ | 0ms | 500ms〜2s |

- execution sandbox の 2026 標準（E2B Firecracker microVM / Wasm / 二段階ネットワーク air-gap / stateful sandbox）は個人用途に過剰。
- 先行事例: Devin = 完全事後承認モデル、aider = Git 安全網の楽観的実行。
- **注意**: Gemini が「Claude Code に `sandbox-auto-allow` / 5 段階 permission-mode が存在」と主張したが、検証者の知識（default/acceptEdits/plan/bypassPermissions の 4 つ）と食い違い。**機能名 hallucination の可能性が高く採用根拠にしない（未検証）**。Gemini の過度に楽観的バイアスの既知事例。

## Triage 結果（Phase 3）

ユーザー選択: **「#5 permission-audit 棚卸しだけ実施」**（記事採用ではなく既存 mechanism の validation-only follow-up）。

## Validation-only Follow-up

| 対象 | 内容 | 結果 |
|------|------|------|
| `scripts/lifecycle/permission-audit.py` | Codex「新実行モード導入より deny catalog / permission-audit の定期確認が先」を受け棚卸し実行（2026-05-31、月末/月初境界） | **クリーン**: allow 71 / deny 102、Bash 65（wildcard 警告閾値 10 以下）、pruning candidate なし、scope-creep signal なし |
| §6.6 Permission Hygiene（`claude-code-threats.md:172`） | cadence は「月初手動 trigger」だが last-run 追跡なし | 今回 2026-05-31 実行を記録。last-run timestamp 機構の追加は **scope 拡張のため提案に留め未実装** |

### 提案（未実装・要ユーザー判断）
permission-audit は「月初手動 trigger」だが last-run 記録がないため、実行されたかどうかを追跡できない。`scripts/lifecycle/` に last-run timestamp を残す軽量機構（または SessionStart hint）を足せば cadence の活性化を観測可能にできる。ただし harness 追加は scope 拡張のため、本 absorb では提案に留める。

## 採用判断

- **新規採用: 0 件**（Codex + Gemini + Opus 三者一致）
- validation-only follow-up: permission-audit 棚卸し実施（結果クリーン）
- 記事は **Reference Only** 扱い

## メタ所感

- 記事タイトル "auto-review" だが内容はコードレビューではなく permission/autonomy/sandbox。**code-review-best-practices family との誤分類を回避**できた（saturation gate の family 判定が機能）。
- 個人 dotfiles harness と IDE 製品（Cursor）の文脈差: 「承認回数削減」（製品 UX）より「**誤実行時の被害半径固定**」（個人）が重要（Codex）。
- dotfiles の "static-checkable は mechanism に寄せる" / determinism boundary 哲学が、LLM 分類サブエージェント（#4）を**意図的に採らない積極的根拠**として機能した。「未実装 = Gap」ではなく「未実装 = 意図的境界」と判定できたのが Phase 2.5 の価値。
