---
source: "md→HTML 自動変換 PostToolUse hook 記事 (テキスト貼付) + mathbullet/skills plugins/html/skills/html"
author: "記事著者不明 (Zenn 形式) / mathbullet (GitHub)"
date: 2026-08-13
status: analyzed
classification: measured-no-adopt
adopted_tasks: 0
family: html-output
saturation: "PASS (N=1, 先行は 2026-05-09-html-effectiveness)"
phase_2_5: "degraded — Codex 単独 (Gemini は IneligibleTierError)"
---

## Source Summary

**ユーザー仮説**: 2 つは別ソースだが、合わせると良さそう。

**ソース1 (記事)**: md 保存を合図に PostToolUse hook から Python スクリプトを呼び、同じフォルダに同名 HTML を決定論的に生成する。LLM 不使用ゆえトークン費用ゼロ。変換条件は「先頭行が `#` or front matter に `title:`」かつ「本文 800 字以上 or `![` を含む」かつ「除外ディレクトリ配下でない」。CSS インライン + 画像 base64 で 1 ファイル完結。Python 標準ライブラリのみ。例外時も exit 0。本文最大幅 700px の読み物レイアウト、`prefers-color-scheme` 追従。

**ソース2 (mathbullet html skill)**: LLM が HTML 説明文書を**生成**するための skill。デザインシステム (背景 `#FAF9F6` / 白地・黒罫線・角丸 / Ubuntu Sans+Mono + Noto Sans JP / リンク青 `#2990DA`・アクセント赤 `#D63A2F`・赤強調は 1 ページ 1 回)、MathJax 3、highlight.js、inline SVG 図 (ASCII art 禁止)、文書構造規定 (用語集→背景→本論→具体例→補足と限界)、命名 `{yyyymmdd}-{kebab}.html`。`design-system/` に `document.css` / `component-samples.html` / `math-copy.js`。

**根拠**: どちらも著者個人の運用経験。定量データなし。

**前提条件の非対称**: 記事はゼロトークン・オフライン・1 ファイル完結を売りにする。skill は LLM 生成・CDN 依存 (MathJax/highlight.js/webfont) を前提にする。**両者の機構は正反対**。

---

## Phase 1.5 Saturation Gate

family = `html-output`、N=1 (`2026-05-09-html-effectiveness-absorb-analysis.md`) → **PASS**。

先行 absorb との関係が本件の核心。先行は HTML 出力を「token tax」と「生成時間 markdown 比 2-4x」を主理由に棄却し、成果物として `references/output-format-decision-table.md` (markdown default / HTML は 4 条件を全部満たす時のみ) を作った。**記事はこの棄却理由の片方を無効化する** — 決定論変換なら生成コストは 0。この delta が本件を rehash でなくしている。

---

## Gap Analysis (Pass 1 → Phase 2.5 Codex 修正 → 実測)

| # | 手法 | 出典 | Phase 2 初期 | Codex 修正後 | 実測後の確定 |
|---|------|------|-------------|-------------|-------------|
| 1 | md 保存→同名 HTML を決定論生成 | 記事 | Gap | **N/A (現決定表下)** | **条件付き Gap** — 決定表は HTML に双方向性を必須とするが、実測で Artifact が「静的 local preview」需要を完全には満たさないと判明 |
| 2 | PostToolUse に hook 1 本追加 | 記事 | Partial (要設計変更) | **正しいが不十分** | 同左。`Edit\|Write` に既存 13 hook。加えて原子的書込み・無変更時 skip・出力の ignore/retention・raw HTML と `javascript:` URL のサニタイズが要る。`pulldown-cmark` は未導入なので「Rust がある」= 依存追加不要ではない |
| 3 | 変換対象の絞り込み条件 | 記事 | Gap (要整合) | 同左 | 800 字・`![` は可読性の粗い代理指標 (Codex 指摘)。採るなら決定表側の語彙に合わせる |
| 4 | CSS インライン + 画像 base64 | 記事 | Gap | Gap | 同左 |
| 5 | 例外時も exit 0 | 記事 | Already | Already | 既存 hook 群の標準作法 |
| 6 | Python 標準ライブラリ縛り | 記事 | N/A (棄却) | **棄却が正しい** | 手書き markdown パーサを意味し表・ネストリスト・コードフェンスで壊れる。ただし Rust 化も GFM 拡張・画像解決・サニタイズ・単体 HTML サイズを別途決めない限り解決にならない |
| 7 | Obsidian 風ダークテーマ | 記事 | Gap (低優先) | Gap (低優先) | **不要** — Artifact のトークン式 light/dark をそのまま使える (下記) |
| 8 | デザインシステム `document.css` | mathbullet | Gap | **条件付き** | **棄却** — Ubuntu Sans / Noto Sans JP は webfont。MathJax と同じ理由 (CSP・オフライン) で「1 ファイルで開ける」を壊す |
| 9 | MathJax 3 + highlight.js | mathbullet | N/A | **defer** | CDN 読込は不採用。ただしコード表示の設計は再利用候補 |
| 10 | inline SVG 図生成 | mathbullet | N/A | 概ね N/A | 生成は LLM authoring の責務。変換器が担えるのは既存画像・既存 SVG の安全な埋込みまで |
| 11 | 文書構造規定 | mathbullet | Partial | Partial | 変換でなく執筆規約。`templates/analysis-report.md` が同種の役割を持つ |
| 12 | `{yyyymmdd}-{kebab}` 命名 | mathbullet | Already | Already | docs/research/ の命名と同型 |

### Codex が指摘した見落とし (私が落としていた)

> PostToolUse は任意の「保存」を監視せず、Claude Code の `Edit` / `Write` だけを捉えます。Obsidian・エディタ・外部スクリプトの保存では更新されません。

記事は「保存した瞬間」と書くが、実際は「エージェントが書いた瞬間」。docs/research/ は Claude が書くので大半は動くが、Obsidian Vault のノートには一切効かない。

---

## Phase 2.5 セカンドオピニオン

**Codex (gpt-5.6-terra, xhigh)** — verbatim:

> 結論として、**新規 hook は作らない**判断が妥当です（現時点では 80% 程度）。

> **8 は最優先の検証対象ですが、代替確定ではありません。** Artifact はオンデマンドの managed/hosted 表示、ローカル HTML は offline・double-click・ファイル所有権を持つ配布物です。後者を必要とするなら代替になりません。逆に前者で足りるなら hook は不要です。**「未使用」は Gap の証拠ではなく、未検証の証拠です。**

> **9 は限定付きで正しいです。** 変換 HTML を gitignore し、agent が再 ingest しないなら token tax と LLM 生成時間は消えます。同階層で追跡するなら VCS ノイズ・二重管理は残ります。「読者不在」も外部読者ではなく、自分の判断が速くなるかで測るべきです。

Codex 推奨の段取り: (1) 実在 md で Artifact を試す → (2) 決定表に「静的 local preview」カテゴリが要るかだけ追記 → (3) 実証された場合だけ**明示実行**の Rust preview コマンド。PostToolUse 自動化はその後。

**Gemini**: `IneligibleTierError` (individuals sunset、2026-08-13 再確認) → **Phase 2.5 は Codex 単独 = degraded**。

---

## 実測: Artifact の markdown レンダリング

Codex 推奨の第 1 段を実行した。検証対象 2 件、WebFetch で生 HTML を取得 (Haiku 要約でなく raw)。

取得経路の注記: `claude-in-chrome` は extension 未接続で失敗。`agent-browser` で artifact URL を開くと `Page not found`、`--profile` で Chrome プロファイルを指定しても同じ (Chrome 起動中でロックされており判定材料にならない)。`claude.ai/code/artifacts` を開いて認証状態を確かめたところ **Cloudflare の bot 検出チャレンジ** に当たった。これは突破しない (bot 検出の回避は行わない) ため、agent-browser で artifact を直接見る経路は閉じている。**当初「未認証だから開けない」と書いたのは未検証の断定で、実際の理由は bot 検出だった。**

**artifact を読めるのは WebFetch** (claude.ai のログインを使うと tool contract に明記)。視覚確認は WebFetch が保存した生 HTML を `file://` で `agent-browser open` → `set media dark` / `set viewport 390 844` → `screenshot --full` で行った。

| 検証項目 | 結果 | 根拠 (生 HTML) |
|---------|------|---------------|
| 本文レイアウト | **記事の処方を既に実装** | `body{max-width:720px;margin:0 auto;padding:32px}` — 記事の「本文最大幅 700px 前後」と同等 |
| ライト/ダーク | **トークン式で実装済 (視覚確認済)** | `--md-bg` 等を bare `:root` / `@media (prefers-color-scheme:dark)` / `:root[data-theme="dark"]` の 3 系統で定義。`@media print` も別途。`agent-browser set media dark` で反転を確認、Mermaid の配色も追従 |
| フォント | **システムフォントのみ** | `-apple-system,BlinkMacSystemFont,'SF Pro','Segoe UI',sans-serif` / コードは `'SF Mono',ui-monospace,Menlo` — webfont 読込なし = オフライン安全 |
| コードブロック | 横スクロールする | `pre{overflow-x:auto}` |
| シンタックスハイライト | **なし** | `<code class="language-python">` のクラスは付くが着色機構なし |
| 9 列の広い表 (1440px 幅) | **潰れる。表単体では横スクロールしない** | `table{width:100%}` のみで overflow ラッパーなし。視覚確認すると右 3 列が 1 文字幅まで潰れ、`読者が 2 週間ゼロなら撤退` が縦一列の文字列になる。1 行のために表の高さが約 550px |
| 同じ表 (390px 幅) | **ページ本体が横スクロールする** | viewport 390px に対し full-page screenshot が 704px 幅 = `document.scrollWidth` が viewport 超過。Artifact のガイドライン自身が「ページ本体は横スクロールさせない、広いコンテンツは自前の `overflow-x:auto` 内でスクロールさせる」と定めており、markdown レンダラがそれを破っている |
| タスクリスト | 描画される | `<input checked disabled type="checkbox">` |
| Mermaid | **ネイティブ描画される** | `<pre class="mermaid">` + `claude-mermaid-runtime` バンドルが inline 注入。ただしページが 3.2MB になる |
| 日本語 | 文字化けなし | — |
| **YAML frontmatter** | **剥がされず巨大な H2 になる** | `---` が `<hr>`、続く 7 行が丸ごと `<h2>source: "..." author: "..." date: ...</h2>` |

検証物 (private、本人のみ):
- 合成ストレステスト: <https://claude.ai/code/artifact/f42e8f36-6aae-45f5-909d-314285f0f4b5>
- 実コーパス (`2026-05-09-html-effectiveness-absorb-analysis.md`): <https://claude.ai/code/artifact/c88f2767-ad0c-4613-ad53-84b790a0c1ed>

### 実測が変えた判断

1. **Artifact は記事の CSS 処方をすでに満たしている**。700px 読み物幅・light/dark 追従・システムフォント・`pre` の overflow — 記事が「Obsidian のテーマを写した」と書いている層は、既に手元にある。よって手法 7 (Obsidian 風テーマ) と手法 8 (`document.css`) は移植不要になる。**ユーザー仮説の「合わせると良さそう」の合流点は、記事 + mathbullet ではなく、記事の機構 + Artifact の CSS だった。**

2. **ただし Artifact は記事の中核の痛点を悪化させうる**。記事が名指しする「表が横に伸びて読みにくい」に対し、Artifact は overflow ラッパーを持たず 720px に押し込む。視覚確認すると 9 列表の右 3 列が 1 文字幅まで潰れ、日本語が縦一列に落ちる (日本語は単語区切りがないため、列が細るとこうなる)。コードは `overflow-x:auto` で scroll するのに表はしない、という非対称。**CSS だけ読んで「折り返す」と書いた初稿は severity を過小評価していた** — レイアウト主張はスクリーンショットで確かめる。

3. **frontmatter が壊れる**。docs/research/ の全 370 件が frontmatter で始まるので、**全件で先頭に巨大な H2 のゴミが出る**。これは corpus 全体に効く欠陥。

4. Codex の指摘どおり、**hosted と local file の差は残る**。Artifact はオフライン閲覧もダブルクリックもできない。

---

## Integration Decisions

### 採用: なし (0 件)

ユーザー Triage 選択は「Artifact 検証だけ先に (実装ゼロ)」。検証を実行し、結果を本レポートに記録した時点で完了。

### 実測で棄却が確定したもの

| 項目 | 判定 | 理由 |
|------|------|------|
| mathbullet `document.css` の移植 | **棄却** | webfont 依存でオフライン要件を壊す。Artifact のシステムフォント CSS が上位互換 |
| Obsidian 風テーマの自作 | **棄却** | Artifact のトークン式 light/dark が既に同等 |
| MathJax / highlight.js | **棄却** | CDN 依存。CSP・オフラインと衝突 |
| Python 標準ライブラリ縛り | **棄却** | 手書きパーサになる。記事の配布容易性のための制約で自環境には利かない |
| 記事どおりの PostToolUse 自動変換 | **棄却 (現時点)** | Codex 80% + 既存 13 hook + 読者未実証。作るなら明示実行が先 |

### 保留 (次に必要性が実証されたら再開する)

必要になった場合の要件は実測から確定している。新規に設計する余地は少ない。

1. **frontmatter をメタデータブロックとして描画する** (H2 に落とさない)
2. **広い表を `overflow-x:auto` でラップする** — 記事の中核の痛点はここにしかない
3. CSS は Artifact の markdown レンダラを基準にする (システムフォント / 720px / トークン式 light-dark / `pre` の overflow)
4. 出力は gitignore 済みキャッシュ、Markdown を正本にする
5. 起動は**明示実行**から。PostToolUse 自動化はその後

撤退条件: 明示実行のコマンドを作った場合、2 週間使用 0 なら撤去する (MEMORY.md の死蔵アーティファクト系譜 — observe ログ / negative-knowledge.md / daily-health-check / task trends に倣う)。

---

## 当 dotfiles 文脈での教訓

1. **「未使用」は Gap の証拠ではなく未検証の証拠** (Codex)。私は Artifact 未使用を「既に持っている経路を使っていない」と書いて決着したように見せたが、実測すると frontmatter 破壊と表圧縮という 2 つの実欠陥が出た。未使用資産を代替として提示する前に、実データで走らせる。

2. **先行 absorb の棄却理由は、層ごとに再検査する**。2026-05-09 は「token tax」と「生成時間 2-4x」で HTML を棄却した。記事は前者だけを壊す。棄却理由を一括で復活させず、どの層が生き残っているか (VCS ノイズ / 二重管理 / 読者不在) を分けて見る。

3. **「合わせると良さそう」の合流点は、提示された 2 つの外にあることがある**。記事 + mathbullet ではなく、記事の機構 + 手元の Artifact レンダラが正しい組み合わせだった。外部ソース同士を突き合わせる前に、自環境の既存実装を第 3 のソースとして並べる。

4. **PostToolUse は「保存」でなく「エージェントの書込み」を捉える**。hook で自動化を設計するとき、トリガの実際の意味を記事の言葉のまま受け取らない。

5. **レイアウトの主張は CSS 読解で止めず視覚確認する**。`table{width:100%}` + overflow ラッパー無しから「セルが折り返す」と書いたが、実物は 1 文字幅への潰れだった。日本語は単語区切りがないので列幅の減少に対する劣化が英語より急峻。ブラウザ経路が 1 つ塞がった時点で代替を試すこと (claude-in-chrome 未接続 → agent-browser に切替、それも認証で塞がるなら保存済み HTML を `file://` で開く)。`feedback_browser_verify_ui_changes.md` の適用漏れ。

---

## Notes

- Phase 2.5 は Gemini 不在で Codex 単独 = degraded。周辺知識補完 (他プロジェクトの採用事例・より新しい代替手法) は未取得
- mathbullet の `document.css` / `component-samples.html` / `math-copy.js` の中身は未取得。ファイル名と SKILL.md の記述からの判断
- 記事本文は取得経路 text-paste。URL 未取得のため原典照合は未実施
