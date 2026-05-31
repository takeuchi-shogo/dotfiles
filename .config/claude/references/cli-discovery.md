---
status: reference
last_reviewed: 2026-04-23
---

# CLI Discovery Policy

## 発見順序

1. **CLI `--help`**: 新しいツールを使う前に必ず `--help` を確認する
2. **Skills**: Claude Code スキルで対応できるか確認する (`/skill-name`)
3. **MCP**: 専用 MCP server が存在するか確認する

## 理由

Progressive Disclosure 設計: 詳細は必要になったときだけ露出する。
CLI は最も軽量で副作用のない探索手段。

## 2 つの直交ラダー: ツール表面 × 操作信頼ティア

発見順序（上記）が「未知 CLI をどう探すか」を決めるのに対し、実行時には
**直交する 2 軸**で「どの surface に手を伸ばし、どれだけ承認を要するか」を判断する。

### 軸 1: ツール表面の信頼性ラダー（どのツールに手を伸ばすか）

**同じ結果が得られるなら、常に最も信頼性の高い surface を選ぶ。** browser / screen は
API・CLI が存在しない messy system への最終手段であり、happy path ではない。

| 信頼性 | ツール表面 | 特性 |
|---|---|---|
| 最高 | local file / `git` / `rg` / `grep` | 決定論的・高速・テキスト出力で LLM が解釈しやすい |
| 高 | 公式 CLI / API（`gh` 等） | 決定論的、構造化（JSON 等）出力 |
| 中 | MCP ツール | 権限管理付きの標準 surface。サーバー稼働に依存 |
| 低 | browser accessibility snapshot（agent-browser / playwright） | DOM 変化・bot 検知に脆い。snapshot は render 完了を待てる分まだ安全 |
| 最低 | screenshot / screen automation（Computer Use 含む） | 確率的な視覚解析依存。最も不安定かつ高コスト。最終手段 |

### 軸 2: 操作の信頼ティア（どれだけ承認を要するか）

破壊的操作は `settings.json` deny rules で hard block、`/careful` モードで全操作 Confirm 昇格、
という両端は既存だが、**その間の段階**を明示する。**外部に副作用が出る操作（送信ティア）を
独立ティアとして扱う**のが要点。

| ティア | 操作例 | 既定の扱い |
|---|---|---|
| read | ファイル読取・`rg`・`gh pr view` | 自由 |
| propose / draft | diff 提示・コメント下書き | 自由（適用前） |
| local write | `Edit` / `Write`・ローカルファイル変更 | 自由（commit 前） |
| commit | `git commit`（ローカル） | ユーザー依頼時のみ（CLAUDE.md） |
| **external side-effect（送信）** | `git push` / `gh pr create` / deploy / 外部 API / Slack・Issue 投稿 | **明示承認。記事の "approval gates are the product" の核心ティア** |
| destructive | `rm -rf` / force-push / `git reset --hard` / 本番データ削除 | deny rules で hard block |

> **2 軸は独立**: 例 — browser での read は「信頼性=低 / 信頼ティア=read」、
> `gh pr create` は「信頼性=高 / 信頼ティア=external side-effect」。
> 軸 2 の安全機構の体系は `governance-levels.md`（AutoEvolve 自律性）と
> `agency-safety-framework.md`（Affordances/deny rules）を参照。
>
> 出典: 「My Agent Stack For Automating My Personal Life」(Nicolas Bustamante, 2026-05) absorb。
> 業界標準のフォールバックラダー（API/CLI > Browser > Screen）と approval-gate trust-tier を
> coding harness 文脈に翻訳（`docs/research/2026-05-31-personal-agent-stack-absorb-analysis.md`）。

## 例

```bash
# Good: まず help を見る
gh --help
gh pr --help

# Good: サブコマンド発見後に実行
gh pr list --state open
```
