# 第22章 Agent Skills（能力層 — 再利用可能な能力の獲得・合成）

> **一文サマリ:** Skill は、特定ドメイン/タスクの専門性を「プロンプト + ツール + 知識 + ワークフロー + ガードレール」として束ねた再利用可能な能力モジュール。再学習なしにロード・合成・差し替えできる。dotfiles の skills システムそのもの。
> **PDF参照:** §22, p.412-416

エージェントがモノリシックな prompt-and-tool から modular 構造に進むと、「能力をどう組織化・発見・合成するか」が核心になる。答えは **skill** に収束する。Voyager(Minecraft) が、LLMエージェントが検証済みの実行可能コードskillを蓄積していくライブラリで広めた。本番エージェントでも同じ — skill はドメイン専門性を合成可能・version管理可能な形に包む。**skill は MCP Server(Ch21) をツールアクセスに包む**ことが多く、skill抽象を標準ツール層に繋ぐ。

## 22.1 Skill とは何か

### Skill（自己完結した能力モジュール）
**これは何か** — 生のツール(単一関数を公開)と違い、skill は5要素を包む: ①**System prompt augmentation**(ドメイン固有の指示・制約・persona)②**Tool bindings**(必要なツール: API/MCP Server/ローカルコマンド)③**Knowledge**(参照資料・例・few-shot)④**Workflow logic**(多段手順・決定木・条件分岐)⑤**Guardrails**(skill固有の安全制約・出力形式・検証)。
**いつ使う / なぜ要る** — 同じ「やり方」を繰り返し使うとき(プロジェクトの "2回説明したら書き下ろせ" )。ツールが「ハンマー」なら、skill は「家の骨組みの組み方を知っていること」、agent は「どの skill を当てるか選ぶ大工」。
**最小実装（概念: skill vs tool vs agent）**

| 概念 | スコープ | 例 |
|---|---|---|
| **Tool** | 単一関数呼び出し | `web_search(query)` |
| **Skill** | 一貫した能力(prompt+tools+knowledge) | "Research Analyst" skill |
| **Agent** | 複数skillを持つ自律体 | リサーチエージェント本体 |

**リサーチエージェントでの使いどころ** — 「論文を構造化要約する」「情報源の信頼性を評価する」「重複トピックを判定する」を各 skill に。dotfiles の `.claude/skills/` 構造そのもの — project固有なら `<repo>/.claude/skills/`、汎用なら `~/.claude/skills/`。
**落とし穴** — ①skill を広げすぎると何もうまくできない(後述の "limit scope per skill")②全 skill を常時ロードすると context を食う(→ 動的発見、dotfiles の skillListingBudgetFraction と同じ問題)。
**PDF参照** — §22.1, p.412

## 22.2 Skill アーキテクチャパターン

### 動的 Skill 発見（context を食わせない)
**これは何か** — 3パターン: ①**Static loading**(初期化時に全skillロード、単純・低レイテンシだが未使用skillがcontext浪費、数百skillにスケールしない)②**Dynamic discovery**(skill router=軽量分類器/embeddingマッチャがタスクから関連skillを選んで活性化、context効率的だがrouting誤りで取りこぼし+レイテンシ)③**Hierarchical composition**(skill がDAGで他skillに依存、高レベルskillが sub-skill を呼ぶ)。
**いつ使う / なぜ要る** — skill が増えたとき。全部ロードは context を食い、肝心の skill を押し出す。
**最小実装**
```python
# 動的発見: router がタスクに関連する top-k skill だけ活性化
relevant = skill_router.match(user_request=msg, available_skills=registry, max_skills=3)
agent.activate(relevant)        # 選ばれた skill の prompt/tools/knowledge だけ注入
```
**リサーチエージェントでの使いどころ** — 調査タスクに応じて「論文要約」「ソース評価」skillだけ活性化。dotfiles の skill budget 管理(least-used を name-only に collapse、未使用61件を skillOverrides で抑制し dropped 94→25)と完全に同型 — **未使用skillの常時ロードが "使うskillを押し出す" のが本質的問題**(トークン量そのものより)。
**落とし穴** — ①routing 誤りで関連skillを逃す(分類器の精度)②階層合成は循環依存に注意(Ch18 の DAG 解決)③project/global の scope を間違えると、別リポで消える名前空間付きskillの罠(プラグイン提供skillは未installで消える)。
**PDF参照** — §22.2, p.413

## 22.3 ケーススタディ: Anthropic のエージェント設計

Anthropic のアプローチは skill ベース設計の最も明快な articulation で、**simplicity over complexity** と **composable building blocks over monolithic frameworks** を強調する。dotfiles の `<core_principles>` と一致。

**核原則:** ①**最も単純な解から始める**(単一LLM呼び出し・retrieval+生成 を試して不足が分かるまで agentic に手を出さない)②**Workflows vs Agents**(Ch19 と同じ、workflow=決定的・予測可能、agent=動的・柔軟だが制御困難)③**Augmented LLM が原子単位**: 生のモデルでなく、常に retrieval源・ツール・永続メモリを束ねた合成体 = 実質 **skill 装備モデル**。

$$\text{Augmented LLM} = \text{Model} + \text{Retrieval} + \text{Tools} + \text{Memory}$$

これは skill 概念に直接対応 — 各 skill が、特定タスクで model が**見られる・できる**ものを構成する。skill 境界 = その呼び出しでの能力範囲。

**Building block パターン(5つ):** Prompt Chaining / Routing / Parallelization / Orchestrator-Workers / Evaluator-Optimizer(全て Ch19 で詳説)。これらが skill テンプレートとして機能。

> **Anthropic の核心洞察:** 最も効果的なエージェントは最も複雑なものではなく、**良いツールを持つ単純なループ**:
> ```python
> while not done:
>     action = llm.decide(context, tools)
>     context.append(execute(action))
>     done = llm.should_stop(context)
> ```
> 知性は ①モデルの能力 ②ツール description の質 ③タスク framing の明確さ から来る — 凝ったオーケストレーションロジックからではない。**skill は ②と③に構造を与える。**

**設計推奨:** agentループを単純に保つ / ツール品質に投資(複雑なrouting より丁寧なdescription)/ structured output(parse失敗を防ぐ)/ recovery を組み込む(retry・明確化要求・人間へescalate)/ **skill毎にスコープを絞る**(何でもやろうとするskillは何もうまくできない、狭く定義されたskillの方が合成しやすい)。

## 22.4 Skill ライフサイクル

①**Discovery**(registry/marketplace/ローカル定義から利用可能skillを特定)→ ②**Selection**(リクエストに関連するskillをマッチ・ロード)→ ③**Activation**(skillのprompt/tools/knowledgeをcontextに注入)→ ④**Execution**(skillの能力でタスク遂行)→ ⑤**Deactivation**(skill contextを除去して後続タスクのためにcontextを空ける)→ ⑥**Learning**(実行結果がskillのfew-shot例やrouting を更新)。

> ⑥ Learning がリサーチエージェントの自己進化に繋がる — 「どのソース評価skillが当たったか」で routing を更新(Ch17 の write policy / dotfiles の learned 昇格ループと同型)。

## 22.5 Skill Registry と Marketplace

本番には基盤が要る: **Skill manifest**(name/capabilities/required tools/I/O schema の構造化記述で自動発見・routing を可能に)/ **version control**(skillは進化、再現性のためversion pin)/ **dependency resolution**(特定MCP Server・APIキー・他skillを要求)/ **permission model**(全agentが全skillにアクセスすべきでない=セキュリティ・コスト・能力境界)/ **marketplace**(組織がskillを公開・共有・install、コードのパッケージマネージャ類似)。

```json
// skill manifest の例(業界標準スキーマは未確立、共通フィールドの図示)
{"name": "source-evaluation", "version": "2.1.0",
 "requires": {"tools": ["fetch_url", "search"], "mcp_servers": ["brave-search"]},
 "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}},
 "prompts": ["skills/source-evaluation/system.md"],
 "knowledge": ["skills/source-evaluation/criteria.md"]}
```
> dotfiles の skills 配布(`skills-lock.json` 統合、`task skills:verify` で hash検証、google/skills + mizchi/skills の vendoring)がまさにこの registry/dependency/version 基盤の実装。

## 22.6 Skills vs Fine-Tuning（補完的）

| 観点 | Skills（in-context） | Fine-Tuning |
|---|---|---|
| デプロイ速度 | 即時 | 数時間〜日 |
| 柔軟性 | 実行時に差し替え・合成 | 学習時固定 |
| context コスト | context窓を消費 | 実行時ゼロ |
| 深い挙動変更 | context長で制限 | 深いパラメトリック変更 |
| マルチテナント | ユーザ毎に別skill | 全員同一モデル |
| 保守 | テキストファイル更新 | 新データで再学習 |

**補完的:** FT が**基礎能力**(指示追従・ツール利用形式・推論)を与え、skill が実行時に**タスク固有の専門性**を上乗せ。リサーチエージェントは「ツール利用と推論」は基盤モデルに任せ、「論文要約・ソース評価」は skill で乗せる — FT は不要(プロジェクトの YAGNI)。

---

## この章のまとめ

- **Skill = prompt + tools + knowledge + workflow + guardrails** の再利用可能能力モジュール。ツール(ハンマー)と agent(大工)の中間。dotfiles の skills システムそのもの。
- アーキは static/dynamic/hierarchical。**動的発見**が context を食わせない鍵 — dotfiles の skill budget 管理(未使用skillが使うskillを押し出す問題)と同型。
- Anthropic の核: **良いツールを持つ単純なループ**。知性はモデル能力 + ツールdescription + タスクframing から来る。skill は後二者に構造を与える。**skill毎にスコープを絞る。**
- ライフサイクル(discovery→...→learning)の ⑥Learning が自己進化に繋がる。
- registry/manifest/version/permission の基盤が本番に要る(dotfiles の skills-lock.json が実装)。
- **Skills と FT は補完的**: FTは基礎能力、skillはタスク固有専門性。リサーチagentは skill で十分(FT不要)。

**次章 → Ch23 A2A（エージェント間通信）。** 単一エージェントの skill を超え、複数の専門エージェントが協働する層に進む。
