# コードグラフ 4 点セット 導入 Playbook

本業リポジトリなど「深い呼び出しグラフを持つコードベース」に、ナレッジグラフ +
意味検索を入れるときの判断材料と手順。

**検証状態**: 手順とバージョン番号は出典記事の記述であり、**未実行・未検証**。
「dotfiles 側の判断」節だけが 2026-09-04 にこのリポジトリで実測した内容。
出典: <https://zenn.dev/helloworld/articles/bcaea69f58eae5>

## まず導入判断

グラフが効くかどうかは、リポジトリの規模ではなく**依存の形**で決まる。

| 形 | グラフの効き | 例 |
|----|------------|-----|
| 呼び出しが多段に連なる (A→B→C→D) | 効く。blast radius が実際に広がる | Web アプリのサービス層・ドメイン層 |
| 共通 util への star 型 (全部が 1 モジュールを import) | 効かない。2 段先が全部その util に落ちる | hook スクリプト群、CLI サブコマンド集 |
| Markdown・設定ファイル中心 | 効かない。AST を持たずグラフに乗らない | ドキュメントリポジトリ |

star 型と Markdown 中心のリポジトリでは、構造グラフ (code-review-graph /
Serena / Graphify) を入れても得るものがない。意味検索だけは別枠で、
これはドキュメント量が多いリポジトリほど効く。

## 4 ツールの役割分担

| ツール | 担当 | 代替できるか |
|--------|------|------------|
| code-review-graph | git diff → 影響範囲。レビュー用コンテキスト生成 | Grep で代替可だがトークンを食う |
| better-code-review-graph | 意味検索 (日本語クエリ → 英語シンボル) | 埋め込みモデル次第。384 次元は日本語で外す |
| Serena | `find_symbol` で定義元・実装クラスを行番号付き | LSP があれば重複する |
| Graphify | `/graphify query` で全体構造の要約 | アーキテクチャ文書があれば不要 |

4 つ全部を入れる必要はない。「影響範囲」だけなら 1 つ目、「あの処理どこ」だけなら
2 つ目で足りる。記事は 4 つ揃えた構成を提示しているが、役割は重なっている。

## セットアップ (記事の手順、未検証)

前提は Claude Code + Python 3.13 + uv。

```bash
pip install code-review-graph==2.3.7
code-review-graph install --platform claude-code --no-instructions
code-review-graph build

pip install better-code-review-graph==3.21.0
better-code-review-graph graph build --full-rebuild
better-code-review-graph graph embed   # Qwen3-Embedding-0.6B 約 570MB を取得

uv tool install -p 3.13 serena-agent==1.6.0
serena project create --index
serena setup claude-code

uv tool install graphify==0.9.28
graphify install
```

そのあと Claude Code を再起動し、`.mcp.json` の承認ダイアログで有効化、
`/graphify .` でグラフ構築。`.gitignore` に `.code-review-graph/`、
`graphify-out/`、`.serena/memories/` を追加する。

CLAUDE.md には「質問種別 → どのツールを呼ぶか」の表を置く。記事はこれを本体と
位置づけていて、実際ツール名を指定しない 9 種類の質問すべてで正しく振り分けられたと
報告している。ツールを入れるより、この表を書く方が効果に効く可能性が高い。

なお `.mcp.json` はプロジェクトスコープ (リポジトリにコミットして共有する) で、
このリポジトリの MCP 登録先である `~/.claude.json` とは別物。混同しないこと。

## 最大のリスク: 更新経路が揃っていない

| ツール | 更新 |
|--------|------|
| code-review-graph | 自動 (pre-commit フック) |
| better-code-review-graph | 手動 `graph build` + `graph embed` |
| Graphify | 手動 `/graphify . --update` |
| Serena | 手動 `serena project index` |

4 つのうち自動は 1 つだけ。古いグラフは「推測しない」ではなく「**古い事実で断定する**」
に化けるので、Grep フォールバックより悪くなりうる。チームに配る前に更新を
1 サイクル回してコストを実測し、手動 3 つを 1 コマンド (`task graph:update` 等) に
束ねてから配ること。

pre-commit フックについては、このリポジトリの
`references/code-review-graph-guide.md` が「auto-update hooks は使わない
(既存 hook 体系との衝突回避)」と書いている。lefthook を持つリポジトリに入れる場合、
記事の自動更新はこの方針と衝突する。

## 記事の数値の読み方

「14 万トークン → 70 トークン」は同じものを比べていない。70 はグラフ照会の
**応答**であって、そこから答えを作るために読むコードは別途かかる。比較対象の
142,188 は「全部読ませた場合」なので、削減幅は誇張の方向に効いている。
グラフの価値は削減率ではなく「最初に開くファイルを外さない」ことの方にある。

## dotfiles 自身の判断 (2026-09-04 実測)

構造グラフは**入れない**。Python は 189 ファイル 44,345 行あるが、内部 import は
`hook_utils` への集中が 30 箇所で、あとは 1 ファイル 1 hook の独立スクリプト。
上の表の star 型に該当し、影響範囲分析が全部 `hook_utils` に落ちる。追跡ファイルの
過半 (1,901) が Markdown で AST に乗らないことも効いている。

意味検索側には穴がある。`.config/claude/scripts/runtime/memory-vec-stop-hook.py:38`
の `scan_dirs()` が見ているのは memory ディレクトリ、Vault の `05-Literature` と
`09-TechTrends`、wiki concepts、research-agent experience の 5 つで、
`.config/claude/references/`、`.config/claude/skills/`、`docs/research/` は入っていない。
自分の harness ドキュメントだけが意味検索から外れている状態。新ツールではなく
memory-vec の scan roots を伸ばすのが筋。記事から取れる実利は埋め込みモデルの方で、
Qwen3-Embedding-0.6B は 1024 次元なので「384 次元は日本語クエリで正解が top-5 圏外」
という既知の実測に対する答えになる。
