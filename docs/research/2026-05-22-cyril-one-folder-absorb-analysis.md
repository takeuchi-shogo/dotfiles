---
source: "How to Build an Obsidian System That Runs Your Entire Life From One Folder (@cyrilXBT)"
date: 2026-05-22
status: light-phase2-only
classification: reference-only
adopted_tasks: 1
rejected_main_claims: 12
note: "Phase 1.5 SATURATED → light Phase 2 (2 novel points only), Phase 2.5 (Codex+Gemini) omitted by user direction"
related:
  - docs/research/2026-05-08-cyril-obsidian-vault-absorb-analysis.md
  - docs/research/2026-05-19-cyril-obsidian-dashboard-absorb-analysis.md
---

## Context

本記事は @cyrilXBT による Obsidian 系記事 4 本目 (cyrilXBT 著者連続)。

| 本数 | タイトル略称 | 日付 | 判定 |
|------|-------------|------|------|
| 1 | Claude-Only Stack | 2026-04-11 | analyzed |
| 2 | Knowledge Vault | 2026-05-08 | reference-only (3 採用) |
| 3 | Dashboard | 2026-05-19 | reference-only (2 採用) |
| **4** | **One Folder (本記事)** | **2026-05-22** | **light Phase 2 のみ** |

3 本目 (Personal OS 再パッケージ色が強い Dashboard 記事) の時点で短絡判定が始まり、4 本目では Phase 1.5 で SATURATED 判定が確定した。しかしユーザーの指摘により、既存 absorb で見落とした可能性のある 2 novel points だけを救済し light Phase 2 として分析する。Phase 2.5 (Codex+Gemini 並列批評) はユーザー指示により省略。

---

## Article Summary

記事の主張は「フォルダ階層を捨て、LIFE/ 単一フォルダにすべてを置く」。

| 要素 | 内容 |
|------|------|
| フォルダ構造 | `LIFE/` 1 フォルダ + ファイル名で分類 |
| ファイル命名 | `YYYY-MM-DD-[TYPE]-[TOPIC].md` (TYPE: NOTE/IDEA/TASK/REVIEW/PLAN) |
| Frontmatter | universal schema — `date`, `type`, `status`, `tags`, `project` |
| 5 コマンド | `/morning` `/capture` `/review` `/find` `/plan` |
| N8N 自動化 | 3 本: 毎日 8PM レビュープロンプト / 月曜 stale ノート / 月次レビュー |

著者の主張: フォルダ選択コスト (filing decision) をゼロにし、Obsidian 検索 + AI フィルタリングで分類を代替できる。

---

## Saturation Context

**obsidian-second-brain family 12 件目**、cyrilXBT 著者 4 本連続。記事本体の 90%+ は以下と重複:

- `/morning` → `auto-morning-briefing.sh` で既実装
- `/capture` → `00-Inbox` フォルダ + `/note` skill で既実装
- `/review` → `/timekeeper review` で既実装
- `/find` → Obsidian 検索 + `obsidian-knowledge` skill で代替済
- `/plan` → `01-Projects/` + `/spec` + `/rpi` で既実装
- N8N 自動化 → Hammerspoon + launchd で代替済
- Universal frontmatter → `templates/obsidian-vault/CLAUDE.md` の naming conventions で部分的にカバー済

**新規論点は 2 つだけ** light Phase 2 の対象とする:
- **論点 A**: 単一フォルダ (flat) 構造 vs IPARAG 多フォルダ — 設計思想の比較
- **論点 B**: type-specific コマンド (5 種) vs 既存 4 skill (`/note`, `/digest`, `/decision`, `/eureka`) の intent routing 設計

---

## Pass 1 Sonnet Findings

### 論点 A: Flat vs IPARAG 構造

`templates/obsidian-vault/CLAUDE.md` を確認した結果:

- IPARAG + Zettelkasten の 9 フォルダ構造が既採用 (`00-Inbox` 〜 `08-Agent-Memory`)
- `04-Galaxy` が Zettelkasten パーマネントノートの独立 namespace として設計済
- anti-vision ノートや "なぜ IPARAG を選んだか" の Design Rationale は **文書化されていない**

記事の flat 化主張は既存構造への対案として有効だが、既存設計を覆す根拠は薄い。ただし **なぜ flat にしないか** の理由が CLAUDE.md に記載されておらず、将来の cyril 記事 5 本目や別著者の同類記事で同じ論点が再浮上するリスクがある。

**A1 (flat 構造への全面移行)**: Reject — IPARAG は actionability-based で意味的優位性あり  
**A2 (Design Rationale 文書化)**: Adopt — CLAUDE.md に "なぜ IPARAG を選ぶか" セクションを追加し飽和ガードを強化

### 論点 B: Type-specific コマンド vs Intent Router

既存 skill を確認:

| コマンド | 既存カバー |
|---------|-----------|
| `/note` | Inbox 単純保存 — 存在確認済 |
| `/digest` | literature ノート — 存在確認済 |
| `/decision` | 意思決定記録 — 存在確認済 |
| `/eureka` | 発見・洞察記録 — 存在確認済 |

記事の 5 コマンド (`/morning` `/capture` `/review` `/find` `/plan`) は既存 4 skill とほぼ 1-1 対応する。**自動 intent router** (ユーザー入力から type を推測してルーティング) は存在しないが、これは YAGNI 判定が妥当 — skill 呼び出しは明示的な方が安全。

**B1 (5 コマンド体系の全採用)**: Reject — 既存 4 skill + `/timekeeper` で機能カバー済  
**B2 (自動 intent router)**: N/A — YAGNI、明示 skill 呼び出しが安全設計

---

## Pass 2 Opus Judgment Table

| ID | 内容 | Pass 2 判定 | 根拠 |
|----|------|------------|------|
| A1 | LIFE/ flat 構造への全面移行 | **Reject** | IPARAG は actionability-based (Projects/Areas/Resources 分類) で意味的分類に優位。Galaxy は dense linking 用独立 namespace 必要。flat 化は 5,000+ ファイルでファイルシステム検索性能劣化リスクも残る |
| A2 | CLAUDE.md に Design Rationale 追加 | **Adopt (S)** | 未文書化ギャップ確認。cyril 記事 5 本目以降の同論点再浮上を文書化で予防できる。1 ファイル 15 行の変更で飽和ガード強化 |
| B1 | 5 コマンド体系の採用 | **Reject** | `/note` `/digest` `/decision` `/eureka` + `/timekeeper review` で機能カバー済。命名体系の変更コストがリターンを上回る |
| B2 | 自動 intent router 実装 | **N/A** | YAGNI。明示的 skill 呼び出しは安全設計原則に沿う。intent 推測の誤分類リスクの方が大きい |

---

## Adopted Tasks

### Task A2 [S, 1 file]: `templates/obsidian-vault/CLAUDE.md` に Design Rationale セクション追加

**対象ファイル**: `/Users/takeuchishougo/dotfiles/templates/obsidian-vault/CLAUDE.md`

**変更箇所**: `## Vault Architecture` セクション冒頭の Zettelkasten 言及行の直後

**追加内容** (~15 行):

```markdown
## Design Rationale (IPARAG vs One-Folder)

なぜ flat 単一フォルダにしないか:

1. **Filing decision は 00-Inbox に集約済** — キャプチャ時の分類コストはゼロ。整理は非同期で行う
2. **PARA は actionability-based** — Projects (期限)/Areas (継続)/Resources (参考) の分類は意味的に有効。flat 化すると actionability の signal が失われる
3. **Galaxy は独立 namespace 必須** — Zettelkasten パーマネントノートは dense linking が前提。他 type と混在すると link graph が汚染される
4. **chronological + type filtering は frontmatter + Bases query で代替可能** — ファイル名での type 埋め込みより frontmatter の方が構造化クエリに適している
5. **flat-everything は 5,000+ ファイルで性能劣化リスク** — Obsidian の file explorer / Quick Switcher はフォルダ階層があった方がスケールする
```

**Verification**:

```bash
grep -A 5 "IPARAG vs One-Folder" /Users/takeuchishougo/dotfiles/templates/obsidian-vault/CLAUDE.md
```

---

## Rejected Claims

| # | 主張 | 判定 | 理由 |
|---|------|------|------|
| C1 | LIFE/ 単一フォルダ構造 | Reject | IPARAG 9 フォルダ既採用、actionability-based 分類に優位性 |
| C2 | TYPE prefix ファイル命名 (NOTE/IDEA/TASK等) | Reject | frontmatter type フィールドで代替済、ファイル名 encode は移行コスト大 |
| C3 | Universal frontmatter schema | Reject | `templates/obsidian-vault/CLAUDE.md` に naming convention 既定義。universal 強制は YAGNI |
| C4 | `/morning` コマンド | Reject | `auto-morning-briefing.sh` + launchd で既実装 |
| C5 | `/capture` コマンド | Reject | `/note` skill + `00-Inbox` で既実装 |
| C6 | `/review` コマンド | Reject | `/timekeeper review` で既実装 |
| C7 | `/find` コマンド | Reject | Obsidian 検索 + `obsidian-knowledge` skill で代替済 |
| C8 | `/plan` コマンド | Reject | `01-Projects/` + `/spec` + `/rpi` で既実装 |
| C9 | N8N 毎日 8PM レビュープロンプト | Reject | Hammerspoon daily_enforcer + launchd で代替済 |
| C10 | N8N 月曜 stale ノート検出 | Reject | `vault-maintenance.sh` で代替済 (weekly-review hook) |
| C11 | N8N 月次レビュー自動化 | Reject | `/timekeeper review` の月次モード + Hammerspoon で代替済 |
| C12 | Obsidian AI 全面依存 (フォルダ廃止) | Reject | search + AI は補完ツール。構造的分類との組み合わせが適切 |

---

## Phase 2.5 Skipped

Codex (gpt-5.5) + Gemini 並列批評はユーザー指示により省略。

省略の正当性:
- 新規論点が A2 の 1 件のみ、判定の不確実性が低い
- A1/B1/B2 はいずれも既存実装との照合で判定可能 (外部ツール不要)
- Pass 2 Opus 判定で self-reflection を強化することで代替

Phase 2.5 を実施するとすれば: A2 の Design Rationale 内容の妥当性 (PARA actionability の文献根拠、flat-everything の性能データ) に対する Gemini grounded 検証が有用だった可能性はある。ただし S 規模タスクには過剰。

---

## Future Saturation Guard

A2 採用後、`templates/obsidian-vault/CLAUDE.md` に "## Design Rationale (IPARAG vs One-Folder)" セクションが存在する。

次の cyrilXBT 記事 (5 本目) または他著者の同類 "flat PKM" 記事では:

1. Phase 1.5 で `grep "IPARAG vs One-Folder" templates/obsidian-vault/CLAUDE.md` を実行
2. セクション存在 → "設計根拠文書化済" を根拠に flat 構造論点を即 skip
3. Phase 2 は新規論点 (上記以外) のみを対象とする

これにより obsidian-second-brain 系の構造論点は今後 absorb 不要となる。
