# AI Harness Guide — 設計ドキュメント

- **日付**: 2026-05-29
- **ステータス**: 設計確定（実装プラン待ち）
- **対象読者**: チーム / 同僚（横展開）

## 1. 目的

この dotfiles が体現する「AI コーディングエージェントの活用方法（仕組みと思想）」を、
同僚が**明日から真似て使える**形でまとめ、横展開できる成果物にする。

既存 `README.md` は「リポジトリに何が入っているか・どうセットアップするか」のカタログ型で、
「**どういう思想で AI をこう使っているか**」という活用方法そのものを語るドキュメントが存在しない。
本ガイドがその空白を埋める。

### 非目標 (YAGNI)

- 既存 `README.md` の全面書き換えはしない（役割が違う）。README → 本ガイドへの 1 行リンク追加に留める。
- 118 skill の全網羅はしない（全体地図でカテゴリ参照に留める）。
- CI での HTML 自動ビルドはしない（手動 `task docs:html`）。

## 2. 成果物（ファイル構成）

```
docs/
├── ai-harness-guide.md        # 本体（3 レイヤー単一ドキュメント）
└── assets/
    └── ai-harness-guide.css   # HTML 出力用スタイル（1 ファイル）
Taskfile.yml                    # task docs:html タスクを 1 つ追加
README.md                       # 「AI エージェント基盤」節に本ガイドへの 1 行リンク追加
```

- **本体は単一 Markdown ファイル**。読む側が「思想 → 実践 → 深掘り」を一本道で辿れる。
- **HTML 出力**は `pandoc` で `ai-harness-guide.md` → 自己完結 HTML（CSS 埋め込み・1 枚で配布可能）。
  `task docs:html` で再生成。pandoc 不在環境向けに「VS Code / GitHub レンダリングでも読める」旨を本体冒頭に注記。

## 3. 本体ドキュメントの内容アウトライン（3 レイヤー）

### Layer 1 — 5 分で分かる思想 (Why)

- 一言サマリ: **「Humans steer, agents execute」**（人間は方向付け、エージェントは実行）
- 核となる設計原則 5 つに絞る:
  1. search-first（既存探索を先に）
  2. 契約層 strict / 実装層 regenerable
  3. 判断をゲート化する（review/gate は suggestion ではなく pass/block）
  4. Build to Delete（ハーネスは過渡的技術）
  5. Scaffolding > Model（協調プロトコルが品質差異の主因）
- before-after（素の Claude vs このハーネス）を 1 表で

### Layer 2 — 明日から使う Starter (How, コピペ可能)

- 最小 CLAUDE.md 雛形（数十行版・肥大化させない。IFScale の知見に従い指示数を抑える）
- 規模別ワークフロー表（S / M / L）
- 効く skill 厳選 10 個 + 1 行用途:
  `/spec` `/epd` `/rpi` `/review` `/commit` `/research` `/debate` `/absorb` `/checkpoint` `/recall`
- マルチモデル委譲の最小ルール（Claude → Codex Review Gate / Gemini 1M 分析）

### Layer 3 — 全体地図 (Deep dive への参照)

- 4 層ハーネス（hooks / skills / agents / references）の俯瞰図
- 「もっと知るには」リンク集（`CLAUDE.md`, `references/`, `docs/playbooks/` 等の**実在パス**へ）
- 規模感の数字（執筆時に `ls` で再カウントした実数を記載）

## 4. 正確性の担保

- 既存 README は件数が陳腐化していた（例: 31 agent と記載 → 実際 22）。
  本ガイドは**執筆時に実数を `ls` で再カウント**して記載する。
- リンクは**実在パスのみ**（壊れリンクを作らない）。執筆後にリンク到達性を検証する。

## 5. HTML 出力の仕組み

- `task docs:html`:
  ```
  pandoc docs/ai-harness-guide.md \
    --standalone --embed-resources \
    --css docs/assets/ai-harness-guide.css \
    -o docs/ai-harness-guide.html
  ```
  （`--embed-resources` で CSS をインライン化し、HTML 1 枚で配布可能にする）
- `docs/ai-harness-guide.html` は生成物のため `.gitignore` 追加を検討（プランで判断）。

## 6. 受入基準

- [ ] `docs/ai-harness-guide.md` が 3 レイヤー構成で存在する
- [ ] Layer 1 の設計原則 5 つ・before-after 表がある
- [ ] Layer 2 にコピペ可能な最小 CLAUDE.md 雛形・S/M/L 表・skill 10 個・委譲ルールがある
- [ ] Layer 3 に 4 層俯瞰図・実在パスへのリンク集・実数カウントがある
- [ ] 記載された件数が執筆時の実数と一致する
- [ ] 全リンクが実在パスを指す（壊れリンク 0）
- [ ] `task docs:html` で自己完結 HTML が生成できる
- [ ] README に本ガイドへのリンクが 1 行追加されている
