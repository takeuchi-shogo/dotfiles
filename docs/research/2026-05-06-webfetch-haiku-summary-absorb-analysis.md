# WebFetch 内部 Haiku 要約問題の absorb 分析

## メタ
- **出典**: https://zenn.dev/zhizhiarv/articles/claude-code-webfetch-haiku-summary
- **著者**: sherry
- **公開**: 2026-05-04 (Zenn)
- **absorb 実施**: 2026-05-06
- **関連 plan**: [docs/plans/2026-05-06-webfetch-policy-plan.md](../plans/2026-05-06-webfetch-policy-plan.md)
- **規模**: L (14 ファイル変更、新規 2 + 修正 12)
- **採用**: 8/8 項目 (Group A+B+C 全採用、ユーザー判断: `a`)

## 記事の主張 (Phase 1 抽出)

Claude Code の WebFetch ツールは**内部で Haiku が要約してから** Opus/Sonnet に渡している。3 条件 (Content-Type: text/markdown 対応 + 80+ trusted domains リスト + markdown < 100k chars) を全部満たすドメイン (AWS docs, MDN, react.dev, kubernetes.io 等) のみフルコンテンツが通る。Wikipedia や Zenn 等はサイレントに truncate される。表示の "204.4KB" は受信バイト数で、実際 LLM が読むのは要約後コンテンツ。

### 主要手法
1. **3 条件 bypass**: text/markdown + trusted domain + <100k chars でフル通過
2. **多段 truncation pipeline**: HTTP 10MiB → HTML→markdown 1MiB → 100k chars → Haiku 要約
3. **Copyright protection**: Haiku 層で 125 文字引用制限・歌詞拒否・paraphrase 強制
4. **Silent failure mode**: 受信バイト数表示と実際 LLM が読む内容の乖離

### 証拠 (記事から)
- Wikipedia 'List of countries by population' サイレント truncation
- 18,000+ chars Zenn 記事 → ~500 chars 要約
- AWS docs はフル markdown 取得可能
- Verbose mode で内部プロンプト可視化

### 前提
- Claude Code v2.1.126 (リバースエンジニアリング由来、実装変更で変わる可能性)
- Built-in WebFetch のみ (API/claude.ai web UI には適用なし)

## Phase 2 ギャップ分析 (初版)

### Gap 判定 (初版、Phase 2.5 で多くが格下げ)
- **trusted_domains 認識**: Gap (references/CLAUDE.md/MEMORY.md に一切言及なし)
- **truncation_detection**: Gap (検知機構ゼロ)
- **defuddle 経路**: Gap (skill 登録のみ、fallback として未設計)
- **content_size_telemetry**: Gap (取得サイズ・truncation 記録なし)

### Already 強化分析
- **webfetch_alternatives** (Gemini/WebSearch/Codex/playwright/curl): partial、fallback 位置のみ
- **absorb Phase 1 robustness**: partial、失敗時のみ fallback、truncated 検知不可
- **7 skill が WebFetch 利用** (absorb/research/deep-read/digest/web-design-guidelines/alphaxiv/tech-article-reproducibility): 全部同じ盲点
- **gemini_grounding_for_fetch**: exists、リサーチ用途のみ
- **model-routing.md/subagent-delegation-guide.md**: partial、Haiku への WebFetch+要約委譲が二重圧縮を誘発

## Phase 2.5 修正 (Codex + Gemini 批評反映)

### 判定変更 (Gap → Already 拡張)
| 項目 | 変更理由 (Codex 指摘) |
|------|----------------------|
| trusted_domains 認識 | 外部 JSON + 1 行参照に格下げ (IFScale/Pruning-First 違反回避、本体を MEMORY 転記しない) |
| truncation_detection | friction-events.jsonl schema 1 種追加で吸収、新「機構」不要 |
| defuddle 経路 | skill 登録済み、web-fetch-policy.md に 3 行手順追加で Already 化 |
| content_size_telemetry | friction-events.jsonl が telemetry 基盤、上記と統合 |

### 新規 Gap (Codex 追加指摘 — 初版で見落とし)
- **引用 faithfulness vs Copyright filter (125 字制限)**: absorb/research/digest の「原文引用」運用と Haiku 層 copyright filter が直接コンフリクト。引用 faithfulness が壊れる
- **HTML→md 変換の lossy 性**: 100k 切詰めの**前段**の構造欠落 (table/figure/code-block)
- **Haiku 要約層の prompt injection 表面**: web 経由 prompt が Opus 到達前に Haiku に効く可能性、security-reviewer/mcp-audit と接続観点が抜けている

### 強化案の深化 (Codex 指摘)
- **web-fetch-policy.md** は policy ではなく **URL pattern → 経路 decision table** として書く (運用で参照されるため)
- **absorb Phase 1** は suggestion でなく **gate 化** (trusted 外で強制切替)
- **7 skill** は「3 行手順分散」ではなく **共通 policy + 1 行参照** (DRY/IFScale 配慮)
- **model-routing/subagent-delegation** の Haiku 委譲契約を **「生 markdown 取得まで」に限定**、要約は呼び出し側責務 (二重圧縮の根本遮断、Build to Delete 整合)

### 前提の追加修正 (Codex + Gemini)
- v2.1.126 リバースエンジニアリング由来 → **当プロジェクトで 1 度実測してから policy 化** (observation_pinned 扱い、harness-stability 整合)
- Anthropic 公式は Haiku 介在を直接記述していない (Gemini 確認、ただしコミュニティで 100KB 制限による truncation 自体は再現多数)
- Copyright filter (125 字) はモデル側挙動で Claude Code 固有とは限らない
- 「Built-in WebFetch のみ」前提は当環境で崩れている → 「WebFetch=要約経路、生取得=別経路」として**役割分担**で再定義

### Gemini からの追加発見
- **Jina Reader** (`r.jina.ai/<url>`): URL 先頭付与で Markdown 化された本文取得、軽量経路 (2026-05 ベストプラクティス)
- **15 分キャッシュ**: 同一 URL は 15 分キャッシュされる
- **JS 非対応**: SPA は中身が空、PDF も精度低下
- **Cline は MCP+Playwright** でフルブラウザ、要約介在なし設計
- **Cursor (@Web)** も要約介在あり

## Phase 3 採用判断 (ユーザー回答: 全部採用 `a`)

| 採用 | ID | 項目 | 規模 | 理由 |
|------|-----|------|------|------|
| ✅ | A1 | references/web-fetch-policy.md (decision table) 新規 + 7 skill から 1 行参照 | M | Pruning-First を満たし 7 skill の盲点を 1 箇所で解消 |
| ✅ | A2 | PostToolUse hook で `webfetch_truncation_suspect` event 記録 | S-M | 観測可能性原則 (P3) の直接実装、AutoEvolve Phase 1 seed |
| ✅ | A3 | model-routing/subagent-delegation の Haiku 委譲契約「生取得限定」 | S | 二重圧縮の根本遮断 |
| ✅ | B1 | 当プロジェクトで 1 度実測 (Wikipedia/Zenn 等で受信バイト vs Read 可視文字数 vs 元記事) | S | policy 化前の根拠確保、harness-stability 整合 |
| ✅ | B2 | absorb Phase 1 gate 化 + 引用 faithfulness 警告 | S | 自己適用、最も影響が大きい skill |
| ✅ | C1 | 引用 faithfulness vs Copyright filter — web-fetch-policy.md に明記 | (A1 統合) | 新規 Gap 対応 |
| ✅ | C2 | HTML→md 変換 lossy — code/table 重視記事は curl+defuddle 強制 | (A1 統合) | 新規 Gap 対応 |
| ✅ | C3 | Haiku 要約層の prompt injection 表面 — security-reviewer に観点追加 | S | security 接続 |

| 棄却 | 項目 | 理由 |
|------|------|------|
| ❌ | trusted_domains リスト本体を CLAUDE.md/MEMORY.md に転記 | IFScale 違反、harness-stability 違反 (version-pinned 情報の常駐 NG) |
| ❌ | 各 skill に 3 行手順を個別追記 | DRY 違反、IFScale 悪化、保守コスト増 |

## Phase 4 統合プラン概要

詳細は [docs/plans/2026-05-06-webfetch-policy-plan.md](../plans/2026-05-06-webfetch-policy-plan.md) 参照。

7 phases 構成:
1. **観測ベースライン** (B1) — 実測で根拠確保 (Wikipedia/Zenn/Qiita/AWS docs)
2. **Telemetry 基盤** (A2) — friction-events schema 拡張 + PostToolUse hook
3. **中核 routing** (A1 + C1 + C2) — web-fetch-policy.md decision table 新規 + 7 skill 統合
4. **委譲契約改訂** (A3) — Haiku 委譲を生取得限定に
5. **自己適用** (B2) — absorb Phase 1 gate 化 + 引用 faithfulness 警告
6. **Security 接続** (C3) — security-reviewer に Haiku injection 観点
7. **MEMORY 索引** — _index.md 追記 + ポインタ 1 行

## 撤退条件

- **撤退 1**: Phase 1 実測で記事主張 (Wikipedia/Zenn のサイレント truncation) と乖離 → policy を「観測に基づく注意喚起」に格下げ、強制 gate 緩める
- **撤退 2**: web-fetch-policy.md が運用で参照されない (PostToolUse 観測で違反検知できない) → 6 ヶ月後に削除候補
- **撤退 3**: PostToolUse hook が偽陽性多発で AutoEvolve シグナル品質を下げる → 閾値緩和 or 削除

## Pre-mortem (失敗モード)

- Haiku 要約挙動が Anthropic 側で変わると policy 全体が陳腐化 → version-pinned で記録、観測 hook で実態追跡
- 7 skill 各 SKILL.md の 1 行参照が無視される → PostToolUse hook で WebFetch 直接利用を検知し warning
- friction-events.jsonl の schema 拡張が既存解析を壊す → schema バージョニング、optional フィールドで追加

## 関連索引

- 関連既存: `references/model-routing.md`, `references/subagent-delegation-guide.md`, `references/claude-code-threats.md` (CVE-2026-24052 WebFetch SSRF)
- 関連 absorb: 2026-04-21 obsidian-claudecode (defuddle 経路の発見元)
- 影響 skill: absorb/research/deep-read/digest/web-design-guidelines/alphaxiv/tech-article-reproducibility (7 skill)
