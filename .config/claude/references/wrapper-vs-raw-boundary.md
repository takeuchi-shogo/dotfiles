---
status: active
last_reviewed: 2026-04-23
---

# Wrapper vs Raw Primitive — Harness Control Plane

> このドキュメントは harness の**思想**を明文化するためのもの。新規 skill/tool/wrapper を追加するときの判断基準。

## なぜこれが必要か

Agent harness を育てていくと、同じ下位 tool に対して複数の層の wrapper が積まれていく傾向がある:

```
Opus → /dispatch → codex-rescue → codex CLI → (本当にやりたかったこと)
Opus → /gemini    → gemini-explore → gemini CLI → (同上)
Opus → /codex     → codex skill → codex CLI → (同上)
```

各層には存在理由があるが、wrapper stack が厚くなると以下の問題が出る:

- **抽象度の衝突**: 上位 wrapper が想定しない使い方を下位 tool で試したいとき、wrapper を剥がす/再構築するコストが高い
- **好みの固定化**: wrapper は「過去の良かった使い方」を凍結する。新しい使い方の発見を抑制する
- **コンテキスト圧迫**: 複数 wrapper の説明を全部読ませると token が嵩む

一方、全てを raw のまま渡すと以下が失われる:

- **決定論性**: 毎回同じ手順を LLM が再生成するので再現性が落ちる
- **safety gate**: 危険な操作の事前チェックが効かない
- **taste encoding**: 良い使い方のノウハウが毎回ゼロから再発見される

したがって、**どちらかに寄せるのではなく、境界を意識的に引く**必要がある。

## 判断マトリクス: いつ wrapper を作るか

wrapper を作るのが正しいのは、**以下のいずれかに明確に該当するとき**だけ:

| 基準 | 質問 | 例 |
|------|------|-----|
| **Determinism** | 毎回同じ結果が欲しいか？ | JSON 整形、テンプレート展開、ファイル生成スクリプト |
| **Safety gate** | 危険な操作の事前検証が必要か？ | `git push --force`, `rm -rf`, prod DB 書き込みの確認 |
| **Taste encoding** | 「良い使い方」を毎回再発見するのは非効率か？ | `/commit` (conventional commit 規則)、`/review` (レビュー観点) |
| **Token economy** | raw CLI のヘルプ/マニュアルが大きすぎて毎回ロードが割に合わないか？ | `codex` の 20+ オプションから必要な 3 つだけ露出 |
| **Cross-tool orchestration** | 複数の下位 tool を協調実行する必要があるか？ | `/research` (複数 model への fan-out + 集約) |

**上記のどれにも該当しないなら、wrapper は作らない。raw tool を直接使うべき。**

### アンチパターン: 作ってはいけない wrapper

- 「念のため」「なんとなく抽象化したい」だけの wrapper
- 下位 tool の 1:1 ラッパー（説明を書き換えただけで機能差なし）
- 判断を LLM から奪って手続き化したもの（= micromanagement。skill の "bad manager" 問題）
- 「将来こう使うかもしれない」という speculative abstraction

## 判断マトリクス: いつ raw primitive を渡すか

以下のいずれかに該当すれば、wrapper を作らず raw のまま使わせる:

| 基準 | 質問 | 例 |
|------|------|-----|
| **Exploration** | 想定外の使い方を発見したいか？ | `Bash` そのもの、`codex exec` 直接呼び出し |
| **Single-use** | 一度しか使わない操作か？（DRY は3回から） | ad-hoc な grep/find、臨時スクリプト |
| **LLM's judgment** | 文脈依存の判断を LLM に任せたいか？ | `rg` パターン選択、SQL クエリ生成 |
| **Composability** | 他の tool と自由に組み合わせたいか？ | 標準 Unix tools、SQL、HTTP クライアント |

PostHog の例: 4 つの別 tool (`projects-get`, `insight-get`, `insight-query` ×2) を `executeSql` 一本に統合した。これは上記 **Composability** と **LLM's judgment** が両立したケース。

## 既存 Wrapper Stack の棚卸し

（新規 wrapper 追加時はこの表に追加し、判断基準との対応を明示すること。）

| Wrapper | 下位 tool | 主な理由 | 備考 |
|---------|-----------|---------|------|
| `/dispatch` | cmux Worker / Subagent | Cross-tool orchestration, Taste encoding | ルーティング判断を集約 |
| `/codex` skill | `codex` CLI | Token economy, Taste encoding | 20+ option のうち推奨 3 つだけ露出 |
| `/gemini` skill | `gemini` CLI | Taste encoding (1M context の使い所) | 適用条件の絞り込み |
| `/commit` skill | `git commit` | Taste encoding (conventional commit 規則) | regex+emoji を固定化 |
| `/review` skill | subagents 群 | Cross-tool orchestration | 変更規模に応じて parallel fan-out |
| `codex-rescue` agent | `codex` CLI | Taste encoding (投入タイミングの判断) | 「自力で詰まった時だけ呼ぶ」を制約化 |
| `cmux-helpers` scripts | cmux CLI | Determinism (pane フロー), Token economy | ハイフン区切りコマンドの手順固定化 |

## 新規追加時のチェックリスト

新しく wrapper (skill / agent / script) を作りたくなったら、**以下を self-check** してから作る:

- [ ] 判断マトリクスのどの基準に該当するか、**1 つ以上** 明示できる
- [ ] raw tool をそのまま使うケース（Exploration など）を**阻害しない**
- [ ] 下位 tool への **逃げ道** がある（wrapper を剥がして raw にアクセスできる）
- [ ] 既存 wrapper との**重複**がない（重複する場合は既存を拡張）
- [ ] 手続き化ではなく taste encoding になっている（判断を LLM から奪っていない）

**3 個以上チェックできないなら作らない。**

## Capability Parity との関係

PostHog の原則 1 ("Let agents do everything users can") は、プロダクト会社が外部 agent に機能を公開する文脈では正しい。しかし**個人 harness では逆向きの力学**が働く:

- confused deputy リスク（OWASP LLM08 Excessive Agency）
- subagent が Opus 相当の tool を持つとコストが膨らむ
- 「全部使える」より「意図的に絞る」方が認知負荷が低い

詳細は `subagent-delegation-guide.md` の **Capability Restriction Policy** セクション参照。

## Build to Delete

このドキュメント自体も暫定物。以下が整えば削除してよい:

- 新規 wrapper 作成時にチェックリストを自動提示する hook が入る
- wrapper 棚卸し表が自動生成される仕組みができる
- wrapper 追加の頻度が月 1 件未満になる（思想が内在化された状態）

---

**関連**:
- `subagent-delegation-guide.md` — Capability Restriction Policy
- `skills/skill-creator/instructions/skill-writing-guide.md` — "What NOT to write" セクション
- `docs/research/2026-04-11-posthog-agent-first-rules-analysis.md` — 出典と分析
