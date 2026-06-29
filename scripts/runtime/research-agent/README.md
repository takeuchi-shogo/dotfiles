# research-agent

自己進化型 arXiv 文献調査エージェント（v1）。教科書 `docs/agentic-ai-textbook/` の
§12.7（autonomous research agent）を、重み学習なしで実装したもの。研究質問を与えると
arXiv を検索・読解し、引用付きの統合レポートを返す。成功した調査軌跡を memory-vec に
貯め、次の調査で意味検索して few-shot 注入する（経験RAG）。失敗した試行は自己批評を
episodic memory に蓄えて同じ試行内で改善する（Reflexion）。

既存の `tech-researcher`（RSS を毎日集める収集型バッチ）とは別軸の「深掘り調査層」。

## アーキテクチャ

LangGraph の状態機械:

```
retrieve_experience → research ⇄ tools → synthesize → reflect → (research | finalize)
```

- **retrieve_experience**: memory-vec から類似成功軌跡を引いて few-shot に。
- **research / tools**: LLM が arXiv を search し、重要論文を fetch（arxiv.org のみ）。
- **synthesize**: 収集結果を引用付きレポートに統合。
- **reflect**: 多軸自己評価（quality / grounding / novelty / format）。基準未達なら
  reflection を生成して research へ戻す（最大 `MAX_ITERATIONS` 回）。
- **finalize**: レポートを保存。`--save` かつ score 合格時のみ経験として永続化（Tier 3）。

## セットアップ

```bash
cd scripts/runtime/research-agent
uv venv
uv pip install -e ".[dev]"
```

LLM 認証（ChatAnthropic）: `ANTHROPIC_API_KEY` を環境変数で渡す。リポジトリにコミット
しないこと（local スコープ）。例: `~/.config/research-agent/.env` に置き、起動前に
`export $(grep -v '^#' ~/.config/research-agent/.env | xargs)` で読む、または direnv。

モデルは既定 `claude-sonnet-4-6`（`RESEARCH_AGENT_MODEL` で上書き可）。

## 使い方

```bash
# 調査のみ（経験は保存しない）
.venv/bin/python -m research_agent "LLM エージェントの経験リプレイは tool 選択精度をどう変えるか"

# 成功軌跡を経験として永続化（Tier 3 = 人間が --save を明示）
.venv/bin/python -m research_agent "..." --save

# 反復上限の変更
.venv/bin/python -m research_agent "..." --max-iter 4
```

レポートは `~/.cache/research-agent/reports/<date>-<slug>.md` に保存される。

## 経験RAG と memory-vec への配線

成功軌跡は `~/.cache/research-agent/experience/*.md` に置かれ、memory-vec の
`research-experience` ソースとして索引される。**新規 PC では memory-vec 側に2箇所の
配線が必要**（このリポジトリには既にコミット済み）:

1. `.config/claude/skill-data/memory-vec/reindex.ts` の `SOURCES` に
   `{ root: join(HOME, ".cache/research-agent/experience"), source: "research-experience" }`。
2. `.config/claude/scripts/runtime/memory-vec-stop-hook.py` の `scan_dirs()` に
   `Path.home() / ".cache" / "research-agent" / "experience"`。

配線後、experience を1件保存して索引・検索できることを確認:

```bash
# experience を1件作って検索に乗るか（手動 E2E）
cd /Users/<you>/dotfiles/.config/claude/skill-data/memory-vec
node --experimental-strip-types --no-warnings reindex.ts          # 全 source 再構築（~86s）
node --experimental-strip-types --no-warnings query.ts "クエリ" --source research-experience
```

`persist` 時の reindex は fire-and-forget（完了を待たない）。新しい経験は次回 reindex
完了後（次セッションの Stop hook 等）に検索へ反映される。full rebuild は本番全 source で
~86s かかるため同期待ちしない。

## テスト

```bash
.venv/bin/python -m pytest tests/ -v
```

- `test_tools.py`: arXiv パース / fetch の SSRF ガード（allowlist + IP pin）/ save。
- `test_graph.py`: LLM・HTTP を mock した E2E（done への到達、iteration 上限の強制）。
- `test_experience.py`: persist のフォーマット / retrieve の JSON パース / degrade。

「経験が2回目に効く」フル統合は本番 index を汚すため、上記の手動 E2E で確認する。

## セキュリティ（fetch の SSRF）

`fetch` は arxiv.org allowlist（host 厳密一致）を主防御とし、fetch-time に解決 IP を
private/loopback/link-local denylist で再チェック（DNS rebinding 対策）、redirect 不追従・
Content-Type 限定・サイズ上限・timeout を課す。

## スコープ

v1 は **arXiv 文献調査エージェント**。以下は将来フェーズ（YAGNI で v1 から除外）:

- nightly 自律実行（`run-research-agent.sh` + launchd、tech-researcher 相乗りパターン）。
- Web 検索（Brave、別途 API キー要）。
- `execute_code` ツール（実験実行）。
- 経験RAG の MMR / 時間減衰 / UCB コールドスタート探索 + persist 自動化。
- tech-researcher `adoption-ledger.jsonl` を検索ソース候補として連携。
