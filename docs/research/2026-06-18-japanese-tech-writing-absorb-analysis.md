---
date: 2026-06-18
source: "k16shikano japanese-tech-writing SKILL (gist)"
url: https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d
family: prose-writing-style
status: implemented
adopted: 6
rejected: 2
---

## Source Summary

**主張**: LLM に悩ましい日本語を生成させないための文章規範 skill。鹿野桂一郎 (k16shikano) が Claude Code 用に設計。10 領域 — 整形、段落と論証、論証の厳密さ、読み手の負荷管理、視点と語り、演出の抑制、LLM っぽい表現の禁止、冗長の排除、見出しの付け方、読者への誠実さ。補助 skill `argument-gap-edit`（段落単位の論証ギャップ検出・再配置編集）も含む。

**取得経路**: defuddle (gist HTML→markdown)。

**前提条件**: 技術書・長文ドキュメント制作者向け。

## Phase 1.5 Saturation Gate

- family = `prose-writing-style`。過去 absorb: stop-slop (2026-06-17) のみ ≒ N=1。brevity 系 (caveman/genshijin) は別軸
- 段落構造・論証設計ルールを多く含み、stop-slop とは軸が異なる
- 判定: **PASS** (N<3 で飽和未達、specialized domain)
- Stale-Plan Audit: stop-slop は 1 日前で skip

## Gap Analysis

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | AI 臭除去（前置き/空疎な強調/受動態→行為者） | Already | `japanese-ai-prose.md` 8 パターン |
| 2 | LLM 口調禁止（予告と総括/空虚な形容） | Already | `japanese-ai-prose.md` + `prose.md` |
| 3 | ヘッジ→断定の過剰適用ガード（推量を機械的に断定に変えない） | **Gap** | `japanese-ai-prose.md:16` は逆向き（ヘッジ→断定）のみ、例外条項が欠落 |
| 4 | パラグラフライティング（段落の役割=受ける/果たす/渡す） | **Gap** | 未記載 |
| 5 | 論証の厳密さ（異なるものを同一視しない/単一原因還元しない/因果の機構を一文/「必ず」回避） | **Gap** | 未記載 |
| 6 | 整形の細部（一文一行/中黒並列禁止/ダッシュ3種/脚注/全角コロン） | **Gap** | 未記載 |
| 7 | 演出の節度（溜め/修辞疑問/太字/予告/見出し内容特定） | **Gap** | 未記載 |
| 8 | 冗長の排除 | Already | `concise.md` + `japanese-ai-prose.md` |
| 9 | em-dash 回避 | Already | `prose.md:28` |
| 10 | 読者への誠実さ | Partial | `overconfidence-prevention.md` 等に既出だが prose 規範ファイルに未統合 |
| 11 | 見出しの付け方（消極的のみ） | Partial | `prose.md` は消極的禁止のみ、内容特定の設計指針なし |
| 12 | argument-gap-edit skill 独立化 | N/A | 段落役割分析に統合可 |

## Already Strengthening Analysis

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | `japanese-ai-prose.md` ヘッジ→断定 | 過剰適用すると推量を消し事実を歪める | 例外条項「不確実なら推量を残す」を明示 | 強化可能 |
| S2 | `prose.md` AI tell 節 | 適用の濃淡が未定義で短い PR にも過剰適用される懸念 | 長文ドキュメント限定の注記 | 強化可能（`japanese-ai-prose.md` 側に移管） |

## Phase 2.5 (Codex + Gemini 並列)

**Gemini**: パラグラフライティングを LLM 規範として明文化した日本語事例は k16shikano が唯一に近い。段落ライティングは構造設計であり、ルール化すると false positive を生む（「受ける」段落を欠いた場合を機械判定できない）。textlint（文法）→ japanese-ai-prose（AI 臭）→ 本記事（段落構造）という層別設計が適切。論証の厳密さルールは参照規範として有効。

**Codex (gpt-5.5)**: 最大リスクは二重管理。ヘッジ禁止がすでに `paper-analysis/SKILL.md`・`japanese-ai-prose.md`・`concise.md` 等 4 箇所に分散しており、skill 化すると 5 箇所目になる。「論証の厳密さ」は `japanese-ai-prose.md` 強化が最良経路。「読者への誠実さ」は Gap でなく Partial。ユーザーはコードベースで docs/research・docs/plans・PR/Issue という長め散文を日常生成するが、CLAUDE.md 常時ロードに段落設計を入れるのは過剰。推奨: japanese-ai-prose.md 拡張（A 方針）。

**ユーザー判断**: 「既存強化で。最小ではなく徹底的に」→ skill 新設せず `japanese-ai-prose.md` を文章規範へ徹底拡張。

## Integration Decisions

### Gap / Partial → 採用

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | 「推量を機械的に断定に変えない」例外条項 | **採用** | `japanese-ai-prose.md:16` のヘッジ→断定ルールの過剰適用ガード。stop-slop 教訓（絶対ルール=二次 slop）と同型 |
| 2 | 論証の厳密さ積極設計 | **採用** | 異なるものを同一視しない/単一原因還元しない/因果の機構を一文/「必ず」回避/例が主張を支えるか。長文ドキュメント限定で収録 |
| 3 | 段落と論証（パラグラフライティング） | **採用** | 段落の役割=受ける/果たす/渡す。LLM 規範として明文化した日本語事例は本記事が唯一に近い。参照規範として有効 |
| 4 | 整形の細部 | **採用** | 一文一行/中黒並列禁止/ダッシュ3種回避/脚注の節度/全角コロン。技術文書向け整形規範として追加 |
| 5 | 演出の節度 | **採用** | 溜め・修辞疑問・太字・予告の節度、見出しは内容特定。`prose.md` の「溜め・もったいぶりを避ける」と同軸で強化 |
| 6 | 「適用の濃淡」注記の強化 | **採用** | 1-5 は長文ドキュメント限定（短い PR/Issue/会話には過剰）。Gemini/Codex 共通警告への対処。false positive 防止 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | `prose.md` 「溜め・もったいぶりを避ける」追記 | **採用** | ユーザー追加フィードバック由来。演出節度と同軸 |

### 棄却

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| R1 | skill 丸ごと vendoring（japanese-tech-writing skill 新設） | **棄却** | AI 臭除去・brevity・LLM 口調が既存 4 箇所と二重管理。stop-slop 棄却と同型 |
| R2 | argument-gap-edit 独立 skill 化 | **棄却** | 段落の役割分析はパラグラフライティング節に統合済。独立させる推敲頻度なし |

## Plan

### Task 1: japanese-ai-prose.md 拡張 (S-M)

- **File**: `.config/claude/references/japanese-ai-prose.md`
- **Changes**: ①「ヘッジ→断定」例外条項追加 ②論証の厳密さ節（6 ルール） ③段落と論証節（役割設計） ④整形節（一文一行/中黒/ダッシュ/脚注/全角コロン） ⑤演出の節度節 ⑥長文ドキュメント限定の冒頭注記強化
- **二重管理回避**: AI 臭除去・brevity・LLM 口調の既存パターンは再録せず参照、新規ルールのみ追記
- **Size**: M

### Task 2: prose.md 追記 (S)

- **File**: `.config/claude/output-styles/prose.md`
- **Changes**: 演出節度の「溜め・もったいぶりを避ける」を会話応答向けに 1 行追記
- **Size**: S

## 設計判断

**skill でなく reference 拡張を選んだ理由**: CLAUDE.md の `<important if="writing a Japanese prose artifact">` が `references/japanese-ai-prose.md` を既に参照しており、一元的な prose 規範ファイルとして機能している。skill 化は同一コンテンツの 5 箇所目を生み、stop-slop 分析で確定した「二重管理=stop 条件」を再踏む。

**「絶対ルール化しない」設計の根拠**: Gemini の実証（em-dash 全禁止→文章が短文羅列化、副詞全削除→解像度低下）と stop-slop absorb の教訓（2026-06-17）から、整形・演出ルールも「既定の傾向+例外条項」として設計する。段落設計は機械的チェックリストではなく設計指針として記述する。

## 出典との差分

k16shikano SKILL の段落役割設計（受ける/果たす/渡す）は LLM 規範として日本語で明文化した事例として希少。ただし本来は著者の推敲設計であり、LLM への機械的適用は false positive を生む。参照規範として `japanese-ai-prose.md` に収録し、「設計指針として読む」という注釈を添える形で翻訳する。論証の厳密さルール群は dotfiles の技術分析文書（docs/research・docs/plans）に直接効くため採用価値が高い。
