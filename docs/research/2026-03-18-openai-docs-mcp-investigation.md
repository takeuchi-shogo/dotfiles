---
status: active
last_reviewed: 2026-04-23
---

# OpenAI Docs MCP 調査

**調査日**: 2026-03-18  
**対象**: OpenAI 公式 Docs MCP と、この dotfiles / Codex 構成への適用可否  
**確認ソース**:

- <https://developers.openai.com/learn/docs-mcp>
- `codex mcp --help`
- `codex mcp add --help`
- `.codex/config.toml`
- `.mcp.json`
- `~/.codex/skills/.system/openai-docs/SKILL.md`

---

## Executive Summary

OpenAI の `Docs MCP` は、**OpenAI 公式ドキュメントを Codex から引ける公式 MCP サーバ**で、公式ページは Codex CLI への登録方法として次のコマンドを案内している。

```bash
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
```

さらに同ページは、登録後に **AGENTS.md で使うよう指示するか、Docs Skill と組み合わせる**ことを勧めている。

この repo との照合結果は次の通り。

- **未導入**: `.codex/config.toml` に `openaiDeveloperDocs` はまだ無い
- **相性は高い**: `~/.codex/skills/.system/openai-docs/SKILL.md` はまさにこの MCP を優先利用する前提で書かれている
- **local CLI は対応済み**: `codex-cli 0.115.0` の `codex mcp add --help` に `--url` 指定が存在する

したがって、**この repo では「Docs MCP を追加し、OpenAI まわりの問い合わせでは global `openai-docs` skill を使う」構成が自然**である。

---

## 1. 公式 docs で確認できたこと

公式ページ `developers.openai.com/learn/docs-mcp` では、Docs MCP を OpenAI の公式ドキュメント用 MCP サーバとして紹介している。
Codex CLI での有効化方法として、次のコマンドが明示されている。

```bash
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
```

また、登録後の使い方としては次が案内されている。

- Codex に docs を読ませる
- citations を付けて回答させる
- AGENTS.md に MCP を使うよう書く
- Docs Skill と組み合わせる

要するに、これは単なる接続先追加ではなく、**prompt / skill / AGENTS と組み合わせて初めて活きる retrieval surface** として設計されている。

---

## 2. local CLI で確認したこと

### 2.1 `codex mcp add` は `--url` を正式サポート

`codex mcp add --help` では、次の syntax が確認できた。

- `codex mcp add <NAME> --url <URL>`

これは公式ページの例と一致している。

### 2.2 利用中バージョン

- `codex --version` → `codex-cli 0.115.0`

少なくとも手元の CLI では、Docs MCP を command surface として追加できる状態にある。

---

## 3. 現在の repo 状態との照合

### 3.1 `.codex/config.toml`

現在の `.codex/config.toml` には次の MCP がある。

- `context7`
- `playwright`
- `deepwiki`

`openaiDeveloperDocs` はまだ無い。

### 3.2 `.mcp.json`

repo root の `.mcp.json` には次がある。

- `context7`
- `playwright`

ここにも `openaiDeveloperDocs` はまだ無い。

### 3.3 global skill はすでに前提化している

`~/.codex/skills/.system/openai-docs/SKILL.md` は、OpenAI 関連の質問では **developers.openai.com MCP server を最優先で使う**と明記している。
さらに、MCP が無ければまず次を試せと書いている。

```bash
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
```

つまり、**skill 側の前提はすでに整っていて、足りないのは実際の MCP 登録だけ**である。

---

## 4. 導入した場合の価値

この repo での利点はかなり明確。

### 4.1 OpenAI 情報取得の一次ソース化

今は OpenAI 関連の質問で official docs を参照したい場合、fallback browse に頼る場面がある。
Docs MCP を入れると、OpenAI 製品に関する調査を **公式 docs の retrieval** に寄せやすい。

### 4.2 `openai-docs` skill と噛み合う

既存の global skill がすでにこの MCP を前提にしているので、導入後の運用はシンプル。

- OpenAI 関連質問
- `openai-docs` skill を使う
- 必要なら AGENTS で OpenAI docs は Docs MCP 優先と補強する

### 4.3 Context7 との役割分担が明確

- `context7`: 汎用ライブラリ docs
- `openaiDeveloperDocs`: OpenAI 公式 docs 専用

この分離はかなり健全で、OpenAI 製品については一次ソースをより確実に優先できる。

---

## 5. この repo での導入方針

現時点で一番自然なのは次の方針。

1. `openaiDeveloperDocs` を Codex 側 MCP に追加する
2. OpenAI 関連の問い合わせでは global `openai-docs` skill を使う
3. repo local で補強したいなら `.codex/AGENTS.md` に「OpenAI docs は Docs MCP 優先」の 1 行だけ足す

ここで重要なのは、**新しい repo-local skill を作る必要は薄い**という点である。
既存の global `openai-docs` skill が十分に具体的だから、まずは MCP 登録だけでよい。

---

## 6. 実装候補

### Option A: CLI で追加

最小手順はこれ。

```bash
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
```

その後、Codex の再起動が必要になる可能性が高い。

### Option B: config に明示追加

公式ページは主に `codex mcp add` を案内している。
もし repo 管理下の `.codex/config.toml` に寄せるなら、既存の `[mcp_servers.*]` パターンに合わせて管理するのが自然。

ただし、**公式ページ上で確認できたのは add コマンドであって、同ページの TOML 例は今回確認できていない**。
そのため、TOML 直書きで進めるなら local 実機で `codex mcp add` の出力結果を確認してから寄せるのが安全。

---

## 7. 結論

事実関係としては次の通り。

- `Docs MCP` は OpenAI 公式 docs 用の公式 MCP
- 公式の Codex CLI 導入コマンドは `codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp`
- local `codex-cli 0.115.0` はこの command surface を持つ
- この repo にはまだ未導入
- しかし global `openai-docs` skill はすでに前提として持っている

したがって、**導入価値は高く、しかも既存構成との衝突は少ない**。
次の最小アクションは、「まず MCP を追加し、その後 `.codex/AGENTS.md` に OpenAI docs は Docs MCP 優先の 1 行を加える」ことだと判断できる。
