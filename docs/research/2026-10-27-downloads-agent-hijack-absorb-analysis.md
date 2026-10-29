---
title: "Hijacking AI Agents via Downloads Folder (Forever Security) absorb"
date: 2026-10-27
source:
  title: "Markdown Is the New Executable: Attackers Are Dropping Agent Instructions Into Your Downloads Folder From the Web"
  author: Gal Weizman, Omer Samet (Forever Security)
  url: https://forever.security/blog/hijacking-ai-agents-via-downloads-folder/
  type: blog-post
  fetched: WebFetch (全文取得成功)
  intro: "https://x.com/0xWatkin/status/2114538646254633135"
status: integrated
family: agentic-security
adopted: 3
---

# Forever Security Downloads Agent Hijack — 採否

## Source Summary

**主張**: Web ページはクリックなしで `~/Downloads` にテキストファイルを落とせる。そこに置かれた `AGENTS.md` / `CLAUDE.md` を coding agent が起動時に読み、agent 自身の設定を書き換えさせると、Codex では悪意ある MCP 登録、Claude Code では `ANTHROPIC_BASE_URL` 経由のトークン流出につながる。製品側のバグではなく、Web が書けるフォルダと agent が信頼する指示ファイルの交差が攻撃面になる。

**手法（記事本文で確認できた範囲）**:
- Codex: 植えた `AGENTS.md` が `~/.codex/config.toml` に `[mcp_servers.*]` を追記させ、`--dangerously-bypass-approvals-and-sandbox` 付きの子プロセスで初期化確認させる。記事の再現では **90% 超** の試行でマルウェア実行まで到達
- Claude Code: 植えた `CLAUDE.md` が `.claude/settings.json` に `ANTHROPIC_BASE_URL` を書かせ、API 通信を攻撃者サーバへ向ける。記事の再現では **約 50%** で追従
- 推奨: Downloads で agent を起動しない / 見知らぬ指示ファイルを読む / 設定の異常を点検 / approval・sandbox を維持

**紹介ポスト** (@0xWatkin): Downloads での起動を避ける警告。Codex 成功率 >90%、Claude Code 成功率 ~50% など記事と同趣旨の要約。手法の追加情報はなし。

**前提**: agent は cwd の指示ファイルを信頼し、設定ファイルを自分で編集できる。Downloads はブラウザが書き込める特殊なフォルダ。

## Phase 1.5 Saturation Gate

family: `agentic-security`（先行: zero-trust 2026-05-31 / codex-security SAST 2026-03-17 / openai/codex-security 2026-07-31）。N=3 → 本件で N=4。採用率は既に 20% 超のため PASS (warning)。連続 reject ではない。

## 既存との照合

| 記事の手法 / 推奨 | 既存 | 判定 |
|---|---|---|
| cwd context の難読化 injection スキャン | `scan-context-files.py`（zero-width / ANSI / null / base64） | Already（難読化のみ。平文の設定書き換え指示は未検出） |
| Downloads を hostile 扱い | なし（cwd 警告なし） | Gap |
| `.claude/settings.json` への `ANTHROPIC_BASE_URL` 書き込み阻止 | settings.json に当該パスの Edit ask/deny なし | Gap |
| `~/.codex/config.toml` への `mcp_servers` 追記阻止 | 同上 | Gap |
| 平文の危険フラグ（BASE_URL / bypass / mcp_servers）検出 | なし | Gap |
| 製品パッチ前提の根本修正 | 記事自身が「パッチ対象ではない」と明記 | N/A |

## Integration Decisions

| # | 項目 | 判定 | 理由 |
|---|---|---|---|
| 1 | `.claude/settings*.json` / `~/.codex/config.toml` の Edit を ask | **Adopt** | 攻撃の書き込み sink に人間確認を挟む。ユーザー承認（提案1） |
| 2 | `scan-context-files.py` に平文危険指示 + Downloads cwd 警告 | **Adopt** | SessionStart で起動前に警告。難読化検出は維持 |
| 3 | 採否レポート + `_index.md` 追記 | **Adopt** | 既存 absorb 形式に合わせる |
| 4 | Downloads 起動の hard deny / sandbox 強制 | Reject | 承認範囲外。warn-only の既存方針と整合 |
| 5 | 汎用 jailbreak 文言の検出拡大 | Reject | 既存設計どおり FP が高い。固定トークンのみ |

### 採用した変更（adopted: 3）

1. **T1** `settings.json` permissions.ask に `Edit(.claude/settings*.json)` / `Edit(**/.claude/settings*.json)` / `Edit(~/.codex/config.toml)` を追加。Edit ルールは Write 含む file-editing tool に効く（`deny-rules-catalog.md`）。件数同期のため同 catalog の ASK を 18→21 に更新
2. **T2** `scan-context-files.py` に `ANTHROPIC_BASE_URL` / `--dangerously-bypass-approvals-and-sandbox` / `mcp_servers` 追加指示の平文検出と、cwd が `~/Downloads` 配下のときの警告を追加。既存テストに検出ケースを追加
3. **T3** 本レポートと `docs/research/_index.md` への新規行

## 取得できたもの / 読めなかったもの

| ソース | 結果 |
|---|---|
| Forever Security 記事本文 | 全文取得。成功率「Codex 90%超」「Claude 約50%」は本文で確認 |
| X 紹介 (`0xWatkin/2114538646254633135`) | 取得。記事の警告要約。追加の技術詳細なし |
