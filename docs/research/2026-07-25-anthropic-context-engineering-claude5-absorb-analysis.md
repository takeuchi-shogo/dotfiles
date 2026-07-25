---
title: "The new rules of context engineering for Claude 5 generation models (Anthropic) — absorb analysis"
date: 2026-07-25
source:
  title: "The new rules of context engineering for Claude 5 generation models"
  author: Anthropic (公式ブログ)
  url: https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
  type: vendor-blog
  note: "本文はユーザー貼り付けの全文を一次ソースとして使用"
status: analyzed
family: なし (新分野 — context-engineering / 1st-party prompting policy)。隣接: 2026-07-06 fable-field-guide-unknowns, 2026-07-08 agentic-os-fable5-builders-guide
saturation: "PASS (family 該当なし — harness-engineering 1 hit / claude-code-tips 0 hit で閾値未満)"
adopted: 2
validation-only: 1
---

# Anthropic「Claude 5 世代の context engineering 新ルール」— absorb 分析 (採用 2, validation-only 1)

## 結論

**記事由来の構造変更は採用 0。** 実行したのは (a) 記事が触媒になって露出した実 drift の修正 1 件、(b) dotfiles 自身が既に持つ原則の執行 1 件 — どちらも記事の主張の移植ではない。

記事の中核主張「Claude Code の system prompt を 80% 以上削除しても coding eval に劣化なし」は **製品層 system prompt の話であり、個人 harness の CLAUDE.md / skill に移植してはならない**。Codex 批評が示した通り、Anthropic は特定モデル・特定 toolset・統制された eval 分布を持つ製品を最適化しているのに対し、個人の global CLAUDE.md は全 repo に upfront で入り、project 指示 / skill / memory はそれぞれ別の load path と寿命を持つ。同じ削減率が同じ非劣化を意味しない。

## Source Summary

- **主張**: Claude 5 世代 (Opus 5 / Fable 5) では過剰制約 (over-constraining) が有害。社内 transcript 読解で「leave documentation as appropriate」と「DO NOT add comments」のような system prompt / skill / user request の clash を実観測し、矛盾の解決自体が推論コストになっていた。旧世代では worst case 回避のため必要だった guardrail を削除し、judgement に委ねられるようになった。
- **手法 (current_methods, 11 件)**:
  1. Rules → Judgement (絶対ルールを削り「周囲のコードに合わせろ」型の委譲文へ)
  2. Examples → Interface design (使用例より enum 等の表現力ある引数設計)
  3. Upfront → Progressive disclosure (skill 分割 + ToolSearch による deferred tool loading)
  4. Repeat yourself → Simple tool descriptions (system prompt での再掲をやめ tool description に集約)
  5. CLAUDE.md memory → Auto-memory (`#` hotkey 運用の廃止)
  6. Simple specs → Rich references (HTML artifact / test suite / 移植元コード / rubric)
  7. CLAUDE.md は repo 説明を軽く、gotcha にトークンを割く。ファイルシステムから分かる自明を書かない
  8. Skill は lightweight guide。over-constrain しない (highly important area は例外)
  9. References は `@` mention。コード形式優先 (HTML mockup > 説明 > screenshot)
  10. `claude doctor` / `/doctor` で skill と CLAUDE.md を rightsize
  11. 矛盾指示の clash が推論コストになる
- **根拠**: 社内 transcript の実観測 + coding eval の実測 (80% 削減で非劣化)。1st-party。
- **前提**: Claude 5 世代限定。旧世代モデルでは guardrail が必要だった、と記事自身が明記。

## Phase 1.5: Saturation Gate

| family | キーワード hit | 閾値 | 判定 |
|---|---|---|---|
| `harness-engineering` | `harness` 1 hit (`agent harness`) | 3 以上 | 不成立 |
| `claude-code-tips` | 0 hit | 2 以上 | 不成立 |
| `skill-graphs` | 0-1 hit | 2 以上 | 不成立 |
| `obsidian-second-brain` | 0 hit | 3 以上 | 不成立 |

→ **PASS (新分野扱い)**。Step 7 Stale-Plan Audit は同 family N=0 のため skip。

なお MEMORY.md の「claude-code-tips family (N=15): generic listicle は低収率」は本記事に適用していない。generic listicle ではなく 1st-party の prompting policy 転換であり、family 定義のキーワード閾値も満たさない。

## Phase 2 + 2.5: 判定テーブル (Codex 批評反映後)

Phase 2.5 は **Codex-only の degraded 実行**。Gemini は `IneligibleTierError: This client is no longer supported for Gemini Code Assist for individuals` で到達不能 (2026-07-25 再確認、`memory/feedback_gemini_cli_sunset.md` の記録通り)。したがって model-family diversity は 2 系統 (Claude + OpenAI) に留まり、Google 視点は欠落している。

| # | 手法 | Phase 2 初期判定 | 最終判定 | 根拠 |
|---|---|---|---|---|
| 1 | Rules → Judgement | Partial (未執行) | **Partial (理由訂正)** | 初期判定の例が誤り。`ruff.toml:8 select=["E","F","W"]` + `lefthook.yml:27 ruff check --fix` で bare except (E722) は既に mechanism 強制済。残るのは「未執行」ではなく **prompt 側の冗長重複** |
| 2 | Examples → Interface design | N/A | **Partial** (Codex 指摘で格上げ) | hook/人間起動の script も agent が呼ぶ interface。ただし「例を全部 interface に置換」は誤りで、少数の代表例は有効・網羅的 edge case 羅列を避けるのが公式見解 |
| 3 | Upfront → Progressive disclosure | Already (強化可能) | **Partial** | CLAUDE.md 121行 → `<important if>` 7個 → references/ 165 → rules/ 19 は実装済。skill 内部は `review` / `absorb` 等が既に references/ へ分割済 (skill 内 references 485 ファイル)。**行数を過剰制約の指標にしたのが誤り** |
| 4 | Repeat → tool description に集約 | Already (強化可能) | **Partial** | instruction DRY は CLAUDE.md:115 に明文化。既存重複の検出経路は skill-audit の CONFLICT のみ |
| 5 | CLAUDE.md memory → Auto-memory | Already (強化不要) | **Already (強化不要)** | `references/cc-7-layer-memory-model.md` に Layer 5 として定義済、`#` hotkey 運用は不採用済、Vault 単方向同期 (`sync-memory-to-vault.sh`) 稼働中 |
| 6 | Simple specs → Rich references | Gap | **Partial (降格)** | markdown rubric は意味的評価に適切であり Gap ではない。rich 化すべきは決定的に検証できる部分だけ (fixture / test / CLI / schema)。全 spec の HTML artifact 化は筋が悪い |
| 7 | CLAUDE.md は gotcha 中心 | Partial | **Partial** | project CLAUDE.md (73行) は gotcha 中心で記事の推奨通り。user CLAUDE.md (121行) は原則・哲学が中心で性質が違い、単純比較できない |
| 8 | Skill は over-constrain しない | Gap | **Partial (降格・最大の過大評価)** | Anti-Patterns 43件 / SKILL.md 590行は過剰制約の**証拠ではない**。既知の失敗を防ぎ評価で効いているなら残す。削除候補にすべきは「失敗トレースも評価差もない規則」だけ |
| 9 | `@` mention で reference 参照 | N/A | **N/A** | 現状のバッククォートパス表記は「必要時のみ Read」= progressive disclosure に忠実。`@` は自動展開でトークンを食い後退になる。展開コストはクライアント実装依存で、明確な検索失敗が出るまで移行理由がない |
| 10 | `/doctor` で rightsize | Gap | **Gap 維持 (事実訂正あり)** | Codex は「`claude doctor` は install/settings の read-only 診断」と指摘 — CLI 形については正しい。だが実測で CLI 自身が `For a full setup checkup that can also fix issues, run /doctor in a Claude Code session` と案内しており、記事が指すのは**セッション内 `/doctor`** で別物 |
| 11 | 矛盾指示の clash が推論コスト | Already (強化可能) | **Partial** | skill-audit CONFLICT 検出 + `references/contradiction-mapping.md` + `references/skill-conflict-resolution.md` は存在。既知の弱点として「CONFLICT 件数を成否指標にするな」(PR#125 で改善 PR が 18→24 に増やした実例、`memory/feedback_skill_audit_conflict_metric.md`) |

### Codex が指摘した見落とし

記事も初期分析も **skill 本体の行数**を論点にしていたが、実際に常時ロードされるのは **全 skill の frontmatter description** である。105 skill 環境では本文長より description の総量・誤発火・同時発火の方が先に測るべき指標。

→ dotfiles は PR #70 で対応済 (`skillListingBudgetFraction` + `skillOverrides` により dropped 94→25、~18k→11k tokens/session)。**Already (強化不要)**。

### Codex の中核反論 (採用)

> 最大の前提差は、Anthropic の system prompt は特定モデル・特定 toolset・評価分布を統制した製品層の話である点です。個人の global `CLAUDE.md` は全 repo に upfront で入り、project 指示・skills・memory は別の load path と寿命を持ちます。したがって「80% 削って coding eval 非劣化」を移植してはいけません。不可逆操作、権限、検証要求の hard constraint まで judgement 委譲するのも誤りです。

Codex の推奨順序 (参考、本 absorb では未着手):
1. 繰り返し使う 10-20 実タスクで成功率・再指示回数・tokens・誤発火を基準化する
2. その実データで description の重複・曖昧語・同時発火を整理する
3. 高頻度かつ未分割の長大 skill を1件だけ分割し held-out task で比較する
4. mechanism 済みの prompt 重複だけを削る ← **本 absorb で T2 として実施**
5. rubric を test/fixture 化するのは機械判定できる箇所だけ

Codex の結論「何も構造変更しないは現時点で有力」を採用し、1-3 は着手しなかった。ただし 1 (実タスク eval の基準化) は記事由来ではなく Codex 独自提案であり、`skill-audit` の A/B benchmark と重なるため将来検討の余地がある。

## 採用した変更

### T1: `.mcp.json` の実 drift 修正 (validation-only follow-up)

記事の `/doctor` 推奨が触媒となり `claude doctor` を実行したところ、実際の設定エラーを検出した:

```
Invalid settings
- /Users/takeuchishougo/dotfiles/.mcp.json › mcpServers.x-docs: Skipped —
  MCP server "x-docs" has a "url" but no "type"; add "type": "http" (or "sse" / "ws")
```

x-docs MCP サーバが **skip されて起動していなかった**。`"type": "http"` を追加して修正。再実行で `Invalid settings` セクションが消え、`No installation issues found.` を確認済。

これは「article-backed novel instruction」ではなく「platform drift validation triggered by article」であり、採用件数とは別 ledger で扱う (MEMORY.md の "採用 0 ≠ 終了" 方針に準拠)。

### T2: mechanism 済みルールの prompt 重複削除

dotfiles 自身の原則「Static-checkable rules は mechanism に寄せる」(CLAUDE.md `<core_principles>`) の執行。Sonnet Explore で rules/ 19 ファイル × 機械強制側 (ruff.toml / lefthook.yml / settings.json deny / claude-hooks) を全件照合した結果:

| 候補 | 機械強制の実体 | 判断 |
|---|---|---|
| `common/core-invariants.md:14` `--no-verify` 禁止 | settings.json permissions.deny | **残す** — block された時の理由説明として prompt 側に価値がある |
| `common/core-invariants.md:17` lint config 変更禁止 | `pre_tool.rs check_protect_linter` (BLOCK) | **残す** — 同上 |
| `common/error-handling.md` 空 catch 禁止 | `pre_tool.rs` GP-004 (BLOCK) | **残す** — GP-004 は完全に空の catch のみ検出。ログのみで再スローしない catch や `\|\| true` は未カバーで、原則本体に価値が残る |
| `python.md:114` bare `except:` は絶対禁止 | ruff **E722** + `ruff check --fix` で自動修正 | **削除** |
| `python.md:128` `from module import *` は禁止 | ruff **F403** + 同経路 | **削除** |

実効は 2 行。**この小ささ自体が観測結果** — 記事の言う「mechanism で表現できるのに prompt に残っている」問題は、dotfiles では既にほぼ解消されている。

なお Sonnet 走査は `prompt-only` (機械強制なし) を go.md 6件 / react.md 5件 / rust.md 3件 / proto.md 3件 / python.md 3件など計 30 件以上検出した。これらは `.golangci.yml` / `clippy.toml` / buf 設定が存在しないことに起因する。**mechanism 化の余地はあるが本 absorb のスコープ外**として記録に留める。

## 非採用 (記事由来の構造変更 — すべて reject)

| 手法 | 非採用理由 |
|---|---|
| CLAUDE.md の大幅削減 | 製品層 system prompt の 80% 削減実測を個人 harness に移植できない (load path と寿命が異なる)。記事自身の eval 分布も coding eval に限定 |
| SKILL.md 300行超 23件の行数削減 | 行数は過剰制約の指標として無効。削除候補は「失敗トレースも評価差もない規則」であり、行数で選別すると既知の失敗防止を壊す |
| Anti-Patterns テーブル 43件の削除 | 同上。既知の失敗を防いでいる限り残す |
| rubric の HTML artifact / test suite 化 | markdown rubric は意味的評価に適切。rich 化は決定的検証できる部分に限る |
| `@` mention への移行 | 自動展開でトークン増。現状のバッククォートパス表記の方が遅延読み込みで優位 |
| 絶対ルール → judgement 委譲の一律適用 | 不可逆操作・権限・検証要求の hard constraint を judgement に委ねるのは誤り。記事自身も "highly important areas" を例外としている |

## 教訓 (family 横断で効くもの)

1. **1st-party 記事でも文脈差を検証する** — Anthropic 公式だから移植可能とは限らない。「製品層 system prompt」と「個人 harness の CLAUDE.md / skill」は load path・寿命・eval 分布がすべて異なる。ベンダーバイアスだけでなく **レイヤーバイアス** を疑う。
2. **行数・件数を過剰制約の指標にしない** — 初期分析で SKILL.md 590行 / Anti-Patterns 43件を Gap 根拠にしたのは誤り。Codex 指摘で降格。`memory/feedback_skill_audit_conflict_metric.md` の「CONFLICT 件数を指標にするな」と同型の失敗を繰り返した。
3. **裏取りしてから判定を書く** — 「bare except は linter で表現できるのに prompt に残る」という初期判定は `ruff.toml` を読まずに書いた推測だった。実際は E722 で強制済。Phase 2 Pass 1 の探索結果を Pass 2 で機械強制側と突き合わせる工程が抜けていた。
4. **採用 0 でも `/doctor` 系の診断コマンドは走らせる価値がある** — 記事の主張は 1 つも移植しなかったが、実行しただけで MCP サーバ 1 つが起動していない drift を検出した。

## 未実施 / 残タスク

- **セッション内 `/doctor` の実行** — ユーザー操作が必要 (CLI からは起動できない)。skill と CLAUDE.md の rightsize 提案を一度見る価値がある。実行した場合、提案内容は本レポートの非採用理由と突き合わせて判断すること
- **Gemini 視点の欠落** — Phase 2.5 は Codex-only。Google 系モデルの批評は取得できていない
- **`prompt-only` 30件超の mechanism 化** — `.golangci.yml` / `clippy.toml` / buf 設定の不在が原因。別タスクとして切り出し可能
