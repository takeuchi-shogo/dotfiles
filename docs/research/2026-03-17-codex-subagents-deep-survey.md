# Codex Subagents 深掘り調査

**調査日**: 2026-03-17  
**対象**: OpenAI Codex subagents の公式仕様、ローカル CLI 実態、dotfiles への適用可能性  
**ローカル確認環境**: `codex-cli 0.115.0`

---

## Executive Summary

提示された「Codex subagents」説明は、2026-03-17 時点の OpenAI 公式 Codex docs と概ね整合している。
特に、以下は公式に確認できた。

- subagents は親 agent が明示的に要求したときに起動される
- 並列に別観点を調査させ、親 agent が要約統合する
- built-in agent と custom agent の両方がある
- custom agent は project または user スコープの `.codex/agents/*.toml` で定義できる
- agent ごとに `model`、`model_reasoning_effort`、`sandbox_mode` などを固定できる
- `[agents]` で `max_threads` と `max_depth` を設定できる

追補として、同日の再確認では手元の `codex-cli 0.115.0` で `codex features list` が `multi_agent stable true` を返した。
そのため「機能自体は利用可能」と見てよく、現時点の主な課題は feature rollout ではなく、custom agent 運用と prompt/playbook の整備である。

dotfiles 側では、親 agent 用の `gpt-5.4` / `high` 設定に加えて、`.codex/agents/` と `[agents]` も導入済み。
したがって、次の改善余地は「review / exploration / docs verification の read-heavy 分業をどう標準運用にするか」に移っている。

---

## 1. 公式 docs で確認できたこと

### 1.1 概念

OpenAI の公式 docs では、subagents は「親 agent の文脈を汚さずに、独立したタスクを並列委譲する仕組み」として説明されている。
各 subagent は独立したコンテキストで動き、完了後は結果だけを親に返す。

この設計の利点は主に 2 つある。

1. 親 thread に exploration log や stack trace、途中メモを積み上げずに済む
2. 独立した調査を並列化できる

公式 docs は、最初の導入用途として read-heavy な調査や観点分離を強く推している。
たとえば、コードレビュー、競合しないログ分析、テスト失敗の原因切り分け、ドキュメント確認などが典型例。

### 1.2 起動方法

subagents は自動で常時起動されるものではなく、親 agent に対して明示的に依頼したときに使われる。
また、CLI では `/agent` command で background subagent thread を追えると説明されている。

### 1.3 built-in agent

公式 docs で確認できた built-in agent は以下の 3 種。

| Agent | 役割 |
|---|---|
| `default` | 汎用 fallback |
| `worker` | 実装寄りの一般タスク |
| `explorer` | read-heavy な探索・スキャン |

まず built-in で試し、必要が出てから custom agent へ昇格するのが自然。

### 1.4 custom agent

custom agent は以下のいずれかに TOML を置くことで定義できる。

- `~/.codex/agents/`
- `.codex/agents/`

代表的な設定項目は以下。

| 項目 | 用途 |
|---|---|
| `description` | 選択条件の要約 |
| `model` | agent 専用モデル |
| `model_reasoning_effort` | 推論コストの固定 |
| `sandbox_mode` | `read-only` / `workspace-write` など |
| `approval_policy` | 実行承認ポリシー |
| `tools.*` | 利用ツールの個別制御 |
| `nickname_candidates` | UI 上の表示名候補 |

公式例では、`security-reviewer` を `gpt-5.4` か `gpt-5.3-codex-spark` で定義するパターンが示されている。
一方、ローカル `codex-cli 0.115.0` の parser では少なくとも `include_plan_tool` は未対応だったため、この repo では agent TOML を最小構成に寄せている。

### 1.5 runtime 制御

公式 docs では `[agents]` セクションで以下を制御できる。

- `max_threads`: 同時に許可する subagent 数
- `max_depth`: subagent がさらに subagent を生む深さ

公式の既定例は以下。

```toml
[agents]
max_threads = 6
max_depth = 1
```

加えて、`spawn_agents_on_csv = true` という experimental な fan-out 機能も docs 上は確認できた。

### 1.6 モデル選択

公式 docs が明確に勧めている初期値は次のとおり。

- 親 agent や深い判断が必要な reviewer: `gpt-5.4`
- 高速な探索・読み・要約: `gpt-5.3-codex-spark`

つまり、提示された投稿の「main は gpt-5.4、worker は spark」は概ね妥当。
ただし「何でも好きなモデルでよい」と一般化しすぎるより、まずは公式推奨の組み合わせから始めるほうが現実的。

### 1.7 sandbox / approvals の継承

公式 docs では、subagent は親 agent の sandbox と approval を継承すると説明されている。
そのため、background subagent から approval request が飛んでくる可能性もある。
必要なら custom agent 側で `sandbox_mode` を明示的に上書きできる。

これは実務上かなり重要で、explorer や reviewer を `read-only` に固定することで、並列実行の安全性を大きく上げられる。

---

## 2. 投稿内容のファクトチェック

| 投稿の主張 | 判定 | コメント |
|---|---|---|
| 「subagents は thread のノイズを減らす」 | 妥当 | 公式 docs の中心メッセージと一致 |
| 「並列の専門 agent が結果を持ち帰る」 | 妥当 | 公式 docs で確認 |
| 「built-in agent が 3 つある」 | 妥当 | `default` / `worker` / `explorer` を確認 |
| 「custom agent を `.codex/agents/` に置ける」 | 妥当 | 公式 docs で確認 |
| 「model / reasoning effort を agent ごとに分けられる」 | 妥当 | 公式 docs で確認 |
| 「parallel writes は避けるべき」 | 妥当 | 公式 docs の方がさらに慎重で、まず read-heavy を推奨 |
| 「No complex setup」 | 部分的に正しい | built-in を試すだけなら正しいが、再現性のある運用には agent 定義と runtime 設定が必要 |
| 「今すぐ普通に使える」 | 概ね妥当 | ローカル `codex-cli 0.115.0` では `multi_agent stable true` を確認。残る論点は運用設計 |

---

## 3. ローカル CLI で確認したこと

### 3.1 バージョン

ローカル環境では以下を確認した。

- `codex --version` → `codex-cli 0.115.0`

### 3.2 CLI help

`codex --help` と `codex exec --help` では、subagent 専用の独立 subcommand は見当たらなかった。
少なくとも CLI surface からは、subagents は通常の agent runtime に統合された機能として見える。

### 3.3 feature flag

`codex features list` では以下を確認した。

- `multi_agent stable true`
- `child_agents_md under development false`

したがって、2026-03-17 時点のローカル配布版では subagent runtime 自体は利用可能と見てよい。
一方で、agent 固有の長い運用メモを child agent 側へ自動注入できる状態ではないため、playbook と親 prompt の framing は依然として重要。

---

## 4. dotfiles リポジトリとの照合

### 4.1 既に整っている土台

この repo の [`.codex/config.toml`](../../.codex/config.toml) では、親 agent の基本設定として以下が既にある。

- `model = "gpt-5.4"`
- `model_reasoning_effort = "high"`
- `profiles.review`, `profiles.research`, `profiles.security`
- `context7`, `playwright`, `deepwiki` の MCP

さらに `.codex/agents/` と `[agents]` も導入済みで、親 agent の基盤はすでに subagent 運用と相性が良い。

### 4.2 調査時点の gap と follow-up

調査時点では以下が未整備だった。

- subagent 用の prompt テンプレートまたは運用ガイド
- dotfiles 固有の validation selection を支援する専用 agent
- skill から subagent へつなぐ明示的な判断基準

その後の follow-up で、以下を追加した。

- `docs/playbooks/codex-subagent-usage.md`
- `.codex/agents/validation_explorer.toml`
- `codex-search-first`、`codex-verification-before-completion`、`dotfiles-config-validation` への subagent 導線

### 4.3 導入相性が良いユースケース

この repo で最初に効きそうなのは次の 3 つ。

| ユースケース | 推奨 agent | 理由 |
|---|---|---|
| branch review | `reviewer`, `pr_explorer` | 変更影響と品質観点を分離できる |
| docs / config research | `docs_researcher` | README / docs / config を並列探索できる |
| test gap / validation impact 調査 | `validation_explorer` | Taskfile, validator, AGENTS を分担して読める |

逆に、同じファイル群へ同時編集を入れる implementation-heavy な用途は、最初の導入先としては相性が悪い。

---

## 5. 活かせるもの

### 5.1 review を subagents 前提に再設計する

最も ROI が高いのは review 系。
親 agent は最終判断だけに集中し、subagent に以下を並列委譲する。

- 変更ファイルと依存関係のマッピング
- correctness / security / test gap の観点レビュー
- docs / README / config との整合確認

これにより、親 thread に exploration log を溜め込まずに済む。

### 5.2 read-only explorer を標準化する

subagents 導入で最初に作るべきは write-capable worker ではなく、read-only explorer / reviewer 系。
並列性の利益を得つつ、ファイル競合や accidental write を避けられる。

### 5.3 model の役割分担を固定する

以下のように agent 単位で責務を固定すると、毎回の prompt が短くなり、再現性も上がる。

- parent / reviewer: `gpt-5.4`
- explorer / docs_researcher: `gpt-5.3-codex-spark`

### 5.4 `max_depth = 1` を守る

depth を増やすと、コンテキスト節約どころか orchestration コストが増える。
この repo の用途では depth-1 で十分。

---

## 6. 改善すべき点

### 6.1 投稿は「導入の簡単さ」を強調しすぎている

built-in agent を一度試すだけなら簡単だが、継続運用には次が必要。

- agent 定義ファイル
- runtime 制御 (`max_threads`, `max_depth`)
- sandbox 戦略
- prompt テンプレート

### 6.2 safety の論点が薄い

parallel write conflict への言及はあるが、実務上は以下も重要。

- approval request が background subagent から来る
- 親 sandbox を継承する
- reviewer / explorer は `read-only` に固定すべき

### 6.3 docs とローカル runtime の差分は縮小したが、運用差分は残る

runtime の可用性自体は `multi_agent stable true` により確認できた。
一方で、実務上は次の差分を引き続き確認すべき。

- custom agent 名解決と UI 表示が安定しているか
- `/agent` command や child-agent UX が docs とどこまで一致しているか
- repo 内の skill / playbook から再利用しやすい framing が整っているか

---

## 7. dotfiles 向け導入案

### 7.1 最小構成

runtime の最小構成としては以下で十分。

```toml
[agents]
max_threads = 4
max_depth = 1
```

`max_threads` は公式例の 6 より少し保守的に 4 から始めるのがよい。
token 消費と approval handling を見ながら増やせば十分。

### 7.2 custom agent 候補

以下 3 つは既に導入済みで、今後は運用整備の対象になる。

#### `pr-explorer.toml`

- 目的: diff と周辺ファイルの構造把握
- model: `gpt-5.3-codex-spark`
- reasoning: `medium`
- sandbox: `read-only`

#### `reviewer.toml`

- 目的: correctness / security / test gap のレビュー
- model: `gpt-5.4`
- reasoning: `high`
- sandbox: `read-only`

#### `docs-researcher.toml`

- 目的: README / AGENTS / Taskfile / docs の整合確認
- model: `gpt-5.3-codex-spark`
- reasoning: `medium`
- sandbox: `read-only`

### 7.3 prompt テンプレート例

#### branch review

```text
Review this branch with parallel subagents.
Use pr_explorer for code path mapping, reviewer for correctness/security/test gaps, and docs_researcher for documentation/config consistency.
Wait for all three, then return a prioritized summary with file references.
```

#### repo exploration

```text
Explore this repo with parallel subagents.
Use explorer on .codex/, another explorer on .agents/skills/, and reviewer on Taskfile.yml and validation scripts.
Return only the consolidated findings and avoid proposing edits yet.
```

---

## 8. 判断

subagents は「何でも速くする魔法」ではなく、親 agent のコンテキストを保護しながら独立タスクを分業する仕組みとして理解するべき。
この repo では、まず review / exploration / docs verification の read-heavy 用途に限定して導入するのが最善。

implementation-heavy な subagent 運用は、その後に段階的に広げればよい。

現時点での推奨は以下。

1. runtime と custom agent の基盤はそのまま維持する
2. 次は playbook、skill、validation mapping を整備して再利用性を上げる
3. write-capable subagent は read-only 運用が安定してから検討する

---

## Sources

- OpenAI Codex docs: <https://developers.openai.com/codex>
- OpenAI Codex docs, Subagent concepts: <https://developers.openai.com/codex/concepts/subagents>
- OpenAI Codex docs, Subagents: <https://developers.openai.com/codex/subagents>
- Local verification:
  - `codex --version`
  - `codex --help`
  - `codex exec --help`
  - `codex features list`
  - [`.codex/config.toml`](../../.codex/config.toml)
