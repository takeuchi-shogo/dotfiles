---
title: "One Post by Karpathy Made 41,000 Developers... Here's the Full Guide (@0xkkai) — absorb analysis"
date: 2026-07-31
status: analyzed
adopt_count: 4
family: obsidian-second-brain
family_entry: 22
subfamily: "karpathy-llm-wiki (5 件目)"
author: "@0xkkai (Medium/X, content-farm 系)"
prior_absorb_count: 21 (obsidian-second-brain family) / 4 (karpathy-llm-wiki 系)
saturation_verdict: "PASS (warning) — 採用率 40%、delta=4 (novel 1 + ambiguous 3)"
verdict: "記事 tactic 採用 0。記事の lens が露出させた実バグ/drift へ翻訳して 4 件採用"
phase_2_5: "Codex (gpt-5.6-terra, read-only) 単独。Gemini は IneligibleTierError で恒久使用不可"
related:
  - 2026-04-07-karpathy-llm-kb-full-guide-analysis.md (同ジャンルの先行 "full guide" 解説記事)
  - 2026-04-05-karpathy-llm-wiki-gist-analysis.md (一次ソースの gist)
  - 2026-07-05-leopardracer-second-brain-1500-convos-absorb-analysis.md (family 21 件目)
---

# /absorb 分析: Karpathy "LLM Wiki" Full Guide (@0xkkai, 2026-07-31)

## Source Summary

**主張**: 生ドキュメントは「ソースコード」、wiki は「コンパイル済み成果物」。raw を一度だけ処理して
wiki に構造化・相互リンクし、以後のクエリは wiki だけを読む。トークン 70-90% 削減 + 永続記憶。

**手法** (11 件、per-method 台帳は下記)。**根拠**: star 数 (gist 5,000 / repo 6,800)、"41,000
developers"、トークン算術モデル (実測ではなく推定)。**前提条件**: Claude Desktop + Obsidian。

記事は content-farm 系 (末尾に `Follow @0xkkai` 誘導、数値は全て検証不能)。一次ソースの Karpathy
gist は 2026-04-05 に、同ジャンルのコミュニティ解説 "full course" は 2026-04-07 に既に absorb 済み。

## Phase 1.5: Saturation Gate

family `obsidian-second-brain` の 22 件目、うち karpathy-llm-wiki 系は 5 件目。
採用率 40% (>= 20%) のため **PASS (warning)**。ただし 11 手法中 7 が named prior rehash なので
Phase 2 は delta 4 件のみに絞って実行した。

### per-method 照合台帳 (全 11 手法)

| # | current 手法 | verdict | matched_prior |
|---|---|---|---|
| 1 | raw/ + wiki/ + instructions/ 3フォルダ分離 (raw 不変) | rehash | `2026-04-05-karpathy-llm-wiki-gist-analysis.md` 手法1「3層アーキテクチャ: Raw Sources（不変のソースドキュメント）→ Wiki → Schema（CLAUDE.md 等の運用規約）」/ `instructions/PROCESSING.md` は schema 層の別名、raw 不変規約まで同一 |
| 2a | `wiki/index.md` (全ページ目録) | rehash | 同上 手法5「index.md（内容カタログ）+ log.md（時系列操作ログ）の2ファイル分離」/ 役割・読み順が同一 |
| 2b | `wiki/hot.md` (毎セッション更新・最初に読む直近キャッシュ) | **ambiguous** | log.md は append-only 操作ログで「最初に優先読み込みするホットキャッシュ」ではない。機能重複はあるが同等と名指せない |
| 3 | PROCESSING.md = コンパイラ設定 (1概念1ページ/必須セクション/wikilink 必須) | rehash | `2026-04-07-karpathy-llm-kb-full-guide-analysis.md` 手法8「CLAUDE.md as schema」+ 手法9「Page creation threshold」+ 手法11「YAML frontmatter conventions」 |
| 4 | 矛盾の**非破壊**処理 (`[!contradiction]` に両版+日付+出典、上書き禁止) | **ambiguous** | prior は gist 手法4「矛盾検出」/ full-guide 手法5「contradictions」/ Kevin 手法6「contradiction flagging」= いずれも検出・フラグ。「両版を残すマージ規約」は同等と言い切れない |
| 5 | Staleness 検出 (90日リンク追加なし → stale) | rehash | gist 手法4「陳腐化チェック」/ full-guide 手法5「stale content」/ 閾値の具体化のみ |
| 6 | ingest agent 5 ステップ | rehash | gist 手法2「Ingest: 要約ページ作成 + 既存ページ横断更新 + index/log 更新」/ 粒度差のみ |
| 7 | 日次 scan + **週次 audit で wiki health スコア化** | **ambiguous** | 定期実行は full-guide 手法15「Automation levels (scheduled)」で rehash だが、定量 health スコア + 監査レポート永続化の名指し先がない |
| 8 | `/autoresearch` 3ラウンド自律リサーチ → raw/ → wiki 化 | rehash | `2026-04-14-karpathy-second-brain-modified-analysis.md` 手法3「5 slash commands (`/research` 5-8 並列, /ingest, ...)」 |
| 9 | `lint the wiki` (orphan / dead link / contradiction) | rehash | gist 手法4 Lint「矛盾検出、陳腐化チェック、孤立ページ、欠損リンク」/ 完全一致 |
| 10 | vault へは **read-only 権限のみ**付与 (「削除するな」は助言) | **novel** | family prior 4 件に権限レベル強制の手法記載を名指せない |
| 11 | トークン経済モデル (250K → 5-15K/クエリ、70-90%削減) | rehash | gist 主張「RAG ではなく複利で蓄積」/ 手法ではなく同一主張の定量再表現 |

**delta = 4** (novel 1 + ambiguous 3)。

## Phase 2 判定 (delta 4 件、Phase 2.5 修正後)

| # | 手法 | Pass 2 初判定 | 最終判定 | 根拠 |
|---|---|---|---|---|
| D1 | hot.md / 直近キャッシュ | Already (強化不要) | **Partial** | `memory-vec-recall-hook.py` が意味検索で path-only push、index.db に concepts 47/47 索引済 = 記事の hot.md より上位。だが ① `memory-vec-stop-hook.py` の `scan_dirs()` が memory+Vault のみで **wiki 変更では再索引が発火しない** ② `compile-wiki/SKILL.md` は INDEX 全読み仕様のままで二重系 |
| D2 | 矛盾の非破壊マージ | Already (強化不要) | **Partial** | `boundary_condition` は **JSON フィールド**で JSONL 層専用。Markdown の wiki/research 向け規約はなく `[!contradiction]` 実データ 0 件 |
| D3 | health スコア + `audits/` 永続化 | N/A (棄却) | **N/A 維持** | 消費者ゼロ metrics の失敗が実績 2 件 (observe ログ削除 / task trends 使用0で CLOSED)。`INDEX.md:5-6` の stats 行で足りる |
| D4 | 権限レベル強制 | Partial | **Partial** | destructive Bash は `settings.json:90-130` で hard deny、lint config は `pre_tool.rs:23-64` で exit 2。穴は `kubectl delete` (careful skill が自認、kubectl 実在) → **ユーザー判断で見送り** |

## Phase 2.5: Codex 批評による修正 (Gemini は sunset)

Codex が 4 点を指摘し、**すべて実ファイルで裏が取れた**:

1. **D1 は Already ではなく Partial** — `reindex.ts:63` は `dotfiles/docs/wiki/concepts` を source に持つが
   stop hook の `scan_dirs()` は memory + Vault のみ。索引する側と監視する側が非対称で恒久 stale になる。
   実害: `docs/wiki/concepts/terminal-tooling.md` が index.db より新しく未索引だった
2. **D2 は JSONL 層限定** — `boundary_condition` の実体は JSON コードフェンス。`[!contradiction]` は
   `docs/wiki/` `docs/research/` 全体で **0 件**
3. **Vault deny は Obsidian ではなく HashiCorp** — 両 settings.json の deny にある "vault" は
   `~/.vault-token` の 3 規則 (`Bash(* ~/.vault-token)` / `Read` / `Edit`) のみ
4. **D3 の相乗り先も死んでいる** — `daily-health-check.sh` の plist は launchd 未登録、
   ログ最終更新 2026-03-26

### 自己修正 (Phase 2 で誤っていた点)

- **「query エントリ 6 件」は誤り** — `grep -c "query" log.md` の hit は log 本文中の言及で、
  query 実行記録は 0 件。なお `log.md:1630` に「READ は MANUAL のみ、PROACTIVE read=0 件」という
  過去の同一結論が既にある
- **「contradiction-mapping.md Rule 26」は存在しない** — Pass 1 の Sonnet が付けた番号。
  実体は 5 ステップ解決フロー

### Codex の提案を計測で退けた点

Codex は P1 で「query 規約を **vector-first に揃えろ**」と提案したが、実測すると 384 次元モデルは
**日本語の自然文クエリに弱い**:

| クエリ | top-1 | distance |
|---|---|---|
| `contradiction detection` (英語) | `contradiction-detection.md` ✅ | 1.171 |
| `sonnet imagination bias` (英語) | `sonnet-imagination-bias.md` ✅ | 1.272 |
| `compounding loop` (英語) | `compounding-loop.md` ✅ | 1.166 |
| 「矛盾検出の設計」(日本語) | `compounding-loop.md` ❌ (正解は top-5 圏外) | 1.325 |

vector 単独に寄せると日本語クエリで検索品質が落ちる。**Grep + recall hook の和集合**に修正して採用した (レビューで判明した理由は下記 Post-Review 節)。

## Integration Decisions

記事の tactic 直輸入は **採用 0**。3 フォルダ構成・PROCESSING.md・90 日 stale・トークン算術は
すべて既存実装または既 absorb 済み。採用した 4 件はいずれも **記事の lens が露出させた
dotfiles 側の実バグ / drift への翻訳**。

| Task | 内容 | 規模 | 変更ファイル | 状態 |
|---|---|---|---|---|
| T1 | 再索引トリガーに wiki を追加。`scan_dirs()` に `WIKI_CONCEPTS_DIR` を追加し、reindex.ts の source roots と同期させる意図を docstring に明記 | S | `.config/claude/scripts/runtime/memory-vec-stop-hook.py` | 実装・検証済 |
| T2 | 「Vault root は denied」を permission ルールから 2026-04-14 限定の観測に降格。実 deny (`~/.vault-token`) との混同を明記 | S | `memory/feedback_obsidian_vault_subfolder_write.md` + `memory/MEMORY.md` | 実装済 |
| T4 | query 経路を INDEX.md の Grep + recall hook の和集合に整合。INDEX 全読みはフォールバックに降格。depth テーブルも同期。ベクトル検索を明示コマンドで呼ばない理由を計測値つきで明記 | S | `.config/claude/skills/compile-wiki/SKILL.md` | 実装済 (レビュー後に方針変更、下記 Post-Review 参照) |
| T5 | Markdown ページの矛盾記録形式 (`[!contradiction]` callout + 3 規約) を追記 | S | `.config/claude/references/contradiction-mapping.md` | 実装済 (ユーザー判断で採用。私は実データ 0 件ゆえ YAGNI 寄りと判断していた) |

**見送り (T3)**: `kubectl delete` の deny 追加。kubectl は `/usr/local/bin` に実在し careful skill も
穴を自認するが、全局 deny は正当な運用も止める。当面 careful の PreToolUse prompt gate でカバーし、
k8s を触る頻度が上がってから deny に上げる。

### T1 の検証記録

```
BEFORE: index.db Jul 29 06:53 / wiki rows=47 / STALE: terminal-tooling.md
hook exit=0
AFTER : index.db Jul 31 06:58 / wiki rows=47 / stale 0 件
log   : {"stage":"complete","indexed":284,"skipped":0,"anomalies":0}
```

`task validate-configs` / `task validate-symlinks` ともに ok。

## Post-Review 修正 (Harness Review Gate, tier=deep)

harness ファイル変更のため `/review` が必須。tier preflight は `risk_class=High` で **deep** 判定、
5 レビューアーを並列起動した (Gemini は sunset のため 3-way は degraded、うち code-reviewer と
cross-file-reviewer の 2 体は最終 verdict を返さず途中終了)。

初回 verdict は **NEEDS_FIX**。T4 の当初実装は `query.ts` をシェルから直接叩く形だったが、
3 レビューアーが**同一の根本原因**を別angleから指摘した:

| 指摘元 | severity | 内容 |
|---|---|---|
| codex-reviewer | **MUST** | `compile-wiki/SKILL.md:10` の `allowed-tools` に `Bash(node:*)` がなく、新設した経路が実行時に拒否される (= 到達不能なメイン経路) |
| security-reviewer | MEDIUM (conf 8) | `cd X && node Y "<ユーザーの質問>"` は質問文をシェル文字列に補間する。同一リポジトリ内の `memory-vec-recall-hook.py:186-195` / `memory-vec-stop-hook.py:117-128` はいずれも subprocess の **argv リスト**で渡しており、その規律を破る |
| edge-case-hunter | HIGH (conf 75) | `query.ts:23` の `new DatabaseSync()` は index.db 不在時に**空 DB を新規作成**する。空 DB の新しい mtime により stop hook の `latest_md_mtime <= db_mtime` が真になり、**本来必要な初回 reindex が永久にスキップ**される。query.ts を既定経路にすると新規マシンで露出する |

**対処 (根本原因側)**: 3 件すべて「シェル起動のベクトル検索を既定経路として文書化した」ことに由来する。
`query` サブコマンドの実行記録は通算 0 件であり、使われていない経路のために広い Bash 権限と
インジェクション面と空 DB トラップを抱えるのは YAGNI。**ベクトル検索の明示コマンドを撤去し**、
INDEX.md の Grep + recall hook が既に注入するパスの和集合に置き換えた。T4 の目的
(60KB の全文 Read をやめる) は Grep で達成されるため失われていない。撤去理由は将来の再導入時に
再検討できるよう SKILL.md 本文に計測値つきで残した。

**副次修正**: codex-reviewer が既存 drift として検出した `INDEX.md` の `Topics: 13` を実測値 14 に訂正
(`grep -c '^### '` = 14)。この diff 起因ではないが統計行を触っていたため同時に直した。

**採用しなかった指摘**:

- codex `[PLAN]` 和集合の tie-break 未定義 → 優先順位 (完全一致 → 部分一致 → recall パス、
  5 件超は sources 数優先、3 件未満は全文 Read) を明記して解消済み
- codex `[PLAN]` 計測値を dated な retrieval-evaluation reference に切り出す → 現時点で
  計測は 1 回・4 クエリのみ。専用 reference を新設するのは Pruning-First に反するため
  SKILL.md 内に「モデル差し替え時は再計測」と条件を書いて据え置き
- codex `[CONSIDER]` `query.ts` の overfetch (top-50 全 source 取得後に source フィルタで
  `[]` になりうる) → ベクトル経路を撤去したため本 diff では無効化。`query.ts` 側の
  既存課題として残る (recall hook は同じ経路を使うため別途要確認)

### 索引側 / 監視側の root 全件照合 (レビューで最重要だった未回答項目)

`reindex.ts` の `SourceRoot` 5 件と修正後の `scan_dirs()` を全件照合した結果、**完全一致**:

| # | reindex.ts | scan_dirs() |
|---|---|---|
| 1 | `MEMORY_DIR` | `MEMORY_DIR` |
| 2 | `VAULT/05-Literature` | `vault/"05-Literature"` |
| 3 | `VAULT/09-TechTrends` | `vault/"09-TechTrends"` |
| 4 | `~/.cache/research-agent/experience` | 同一 |
| 5 | `~/dotfiles/docs/wiki/concepts` | `WIKI_CONCEPTS_DIR` (今回追加) |

残る非対称はゼロ。なお codex は「docstring のコメントでは同期を保証できない。`scan_dirs()` と
TypeScript 側 `SOURCES` の正規化済み root set を比較する軽量な CI テストが妥当、manifest 化は
over-engineering」と評価した。これは未実施 (下記 follow-up)。`_drafts/` サブディレクトリは
hook 側 `glob("*.md")` と `reindex.ts:257` の `readdirSync` がどちらも非再帰で**対称的に無視**する
(edge-case-hunter 確認済)。並行実行は `reindex.ts:346-359` の O_EXCL ロック + `renameSync` の
アトミック差し替えで無害化されている。

**~100ms contract**: codex が実測 20 回で全 285 件 (wiki 47 件込み) の scan+stat が中央値 1.395ms /
最大 28.975ms。監視対象追加は contract を破らない。

## Validation-only Follow-up

採用件数に数えないが、記事の lens で露出した既存 drift:

| # | 対象 | drift 内容 | 訂正方針 |
|---|---|---|---|
| V1 | `scripts/runtime/daily-health-check.sh` + `com.claude.daily-health-check.plist` | plist が launchd 未登録、ログ最終更新 2026-03-26 で **4 ヶ月停止**。`launchctl list \| grep health` が空 | 別タスク。`feedback_launchctl_bootstrap_iorerror.md` の legacy `launchctl load -w` 経路で復旧するか、需要なしと判断して退役させるかの二択 |
| V2 | `.config/claude/references/contradiction-mapping.md:54` | 「検出された矛盾は `[CONTRADICTION]` タグ付きで `/improve` ダッシュボードに表示」— Codex 指摘によれば `/improve` ダッシュボードは退役扱い | 未修正 (minimum change のため隣接行に手を入れず)。要確認 |
| V3 | `memory/feedback_obsidian_vault_subfolder_write.md:13` | `enabledMcpjsonServers` が `["context7", "alphaxiv", "code-review-graph"]` と記載だが alphaxiv は commit aced9cf で無効化済 | 未修正 (T2 の対象範囲外)。要確認 |
| V4 | `~/.claude/skill-data/memory-vec/query.ts:23` | `new DatabaseSync()` が index.db 不在時に**空 DB を作成**し、その新しい mtime で stop hook の初回 reindex が永久スキップされる (edge-case-hunter, conf 75)。ベクトル経路撤去で `/compile-wiki query` からの露出は消えたが、**recall hook は同じ `query.ts` を呼ぶため経路は残る** | 別タスク。`docs` テーブル不在を検出したら DB ファイルを消す、または readOnly で開いて即 fallback |
| V5 | `~/.claude/skill-data/memory-vec/query.ts:67` | `OVERFETCH_K=50` で全 source 横断の top-50 を取った後に `--source` で絞るため、対象 source が global top-50 に入らないと `[]` を返す (codex, CONSIDER)。既存テストは 2 件のみで未カバー | 別タスク。source 別に候補を確保する検索、または overfetch 拡大 |
| V6 | `.config/claude/scripts/runtime/memory-vec-stop-hook.py` ↔ `reindex.ts` | 現在は root 5 件が完全一致するが、同期は docstring のコメントのみで担保されている。codex は「正規化済み root set を比較する軽量 CI テストが妥当、manifest 化は over-engineering」と評価 | 別タスク (未実施)。今回のバグの再発防止に直結する |

## 教訓 (family lessons 候補)

- **karpathy-llm-wiki サブ系は 5 件目で tactic 採用 0 が確定的**。記事側に新規性はないが、
  「compiled layer を読む」「staleness を検出する」「advice ≠ safeguard」という lens は
  dotfiles 側の実装非対称・stale fact を炙り出す検査器として機能した。採用 0 で閉じず
  lens として使う運用が正しい
- **索引する側と監視する側の非対称は silent staleness を生む**。reindex.ts の source roots と
  stop hook の scan_dirs は同期が必須で、これは静的に検査できる (将来 mechanism 化候補)
- **セカンドオピニオンも計測で検証する**。Codex の「vector-first に揃えろ」は日本語クエリで
  検索品質を落とすため、そのままは採用しなかった
- **未使用の経路に権限とリスクを足すな**。T4 の当初実装は `query.ts` をシェルから叩く形で、
  MUST (allowed-tools 不足) / MEDIUM (シェル補間によるインジェクション) / HIGH (空 DB による
  reindex 永久スキップ) の 3 指摘を同時に生んだ。根本原因は「実行記録 0 件のサブコマンドのために
  広い Bash 権限と新しい失敗モードを導入した」こと。**レビューで 3 者が別 angle から同一の根本原因を
  指摘したときは、個別に patch せず経路ごと落とすか再設計する**
